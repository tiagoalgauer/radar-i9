"""Costura 1: uma Coleta inteira, com dublês para o mundo externo."""

from datetime import date

from radar.coleta import Noticia, carregar_config, coletar
from radar.db import listar_mencoes

HOJE = date(2026, 8, 25)

CONFIG_TOML = """
nome = "Radar i9+"
intervalo_dias = 7
link_painel = "https://radar-i9.streamlit.app"

[ia]
provedor = "gemini"
modelo = "gemini-2.5-flash-lite"

[email]
alerta = ["sandro@exemplo.com"]
digest = ["sandro@exemplo.com", "equipe@exemplo.com"]

[[termos]]
texto = "InoveMais"
marca = true
idiomas = ["pt", "en"]

[[termos]]
texto = "baterias de segunda vida"
idiomas = ["pt"]
"""


class FonteFalsa:
    def __init__(self, por_termo):
        self.por_termo = por_termo  # {(termo, idioma): [Noticia] | Exception}

    def buscar(self, termo, idioma):
        r = self.por_termo.get((termo, idioma), [])
        if isinstance(r, Exception):
            raise r
        return r


class IAFalsa:
    def analisar(self, titulo, fonte):
        return {"resumo": f"Resumo de {titulo}", "relevancia": 7, "tema": "setor", "sentimento": "neutro"}


class RemetenteFalso:
    def __init__(self):
        self.enviados = []

    def enviar(self, destinatarios, assunto, texto, html):
        self.enviados.append((destinatarios, assunto, texto, html))


def config(tmp_path, toml=CONFIG_TOML):
    p = tmp_path / "config.toml"
    p.write_text(toml)
    return carregar_config(p)


N1 = Noticia("i9+ inaugura fábrica de baterias", "https://ex.com/a", "Gazeta", "2026-08-24")
N2 = Noticia("Second-life batteries boom", "https://ex.com/b", "Reuters", "2026-08-23")
N3 = Noticia("Mercado de baterias usadas cresce", "https://ex.com/c", "Valor", "2026-08-22")


def test_coleta_grava_mencoes_da_fonte_com_os_campos(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [N1], ("InoveMais", "en"): [N2], ("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"

    coletar(config(tmp_path), fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    got = [(m.titulo, m.link, m.fonte, m.data, m.idioma, m.termo, m.coletada_em) for m in listar_mencoes(db)]
    assert sorted(got) == sorted([
        ("i9+ inaugura fábrica de baterias", "https://ex.com/a", "Gazeta", "2026-08-24", "pt", "InoveMais", "2026-08-25"),
        ("Second-life batteries boom", "https://ex.com/b", "Reuters", "2026-08-23", "en", "InoveMais", "2026-08-25"),
        ("Mercado de baterias usadas cresce", "https://ex.com/c", "Valor", "2026-08-22", "pt", "baterias de segunda vida", "2026-08-25"),
    ])


def test_rodar_duas_vezes_nao_duplica(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [N1, N3]})
    db = tmp_path / "radar.db"
    cfg = config(tmp_path)

    r1 = coletar(cfg, fonte, IAFalsa(), RemetenteFalso(), HOJE, db)
    r2 = coletar(cfg, fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    assert (r1["novas"], r2["novas"]) == (2, 0)
    assert len(listar_mencoes(db)) == 2


def test_mesma_noticia_em_dois_termos_entra_uma_vez_no_primeiro_termo(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [N1], ("baterias de segunda vida", "pt"): [N1]})
    db = tmp_path / "radar.db"

    coletar(config(tmp_path), fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    assert [(m.link, m.termo) for m in listar_mencoes(db)] == [("https://ex.com/a", "InoveMais")]


def test_fonte_falhando_em_um_termo_nao_derruba_a_coleta(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): ConnectionError("feed fora do ar"), ("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"
    linhas = []

    coletar(config(tmp_path), fonte, IAFalsa(), RemetenteFalso(), HOJE, db, log=linhas.append)

    assert [m.link for m in listar_mencoes(db)] == ["https://ex.com/c"]
    assert any("InoveMais" in l and "feed fora do ar" in l for l in linhas)
