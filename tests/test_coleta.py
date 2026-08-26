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
texto = "i9+"
marca = true
idiomas = []   # só detecção de marca, não busca

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


# ---------- ticket 03: IA ----------


class IAQueFalha:
    def __init__(self):
        self.chamadas = 0

    def analisar(self, titulo, fonte):
        self.chamadas += 1
        raise RuntimeError("cota estourada")


class IAContadora(IAFalsa):
    def __init__(self):
        self.chamadas = []

    def analisar(self, titulo, fonte):
        self.chamadas.append(titulo)
        return super().analisar(titulo, fonte)


def test_ia_preenche_resumo_relevancia_tema_e_sentimento(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [N1]})
    db = tmp_path / "radar.db"

    coletar(config(tmp_path), fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    m = listar_mencoes(db)[0]
    assert (m.resumo, m.relevancia, m.tema, m.sentimento, m.reprocessar) == (
        "Resumo de i9+ inaugura fábrica de baterias", 7, "setor", "neutro", False)


def test_ia_falhando_guarda_a_mencao_e_marca_para_reprocessar(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [N1]})
    db = tmp_path / "radar.db"
    linhas = []

    coletar(config(tmp_path), fonte, IAQueFalha(), RemetenteFalso(), HOJE, db, log=linhas.append)

    m = listar_mencoes(db)[0]
    assert (m.resumo, m.relevancia, m.tema, m.reprocessar) == ("i9+ inaugura fábrica de baterias", None, "sem classificação", True)
    assert any("ia" in l and "1 falha" in l for l in linhas)


def test_coleta_seguinte_reprocessa_mencao_pendente(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [N1]})
    db = tmp_path / "radar.db"
    cfg = config(tmp_path)
    coletar(cfg, fonte, IAQueFalha(), RemetenteFalso(), HOJE, db)

    coletar(cfg, fonte, IAFalsa(), RemetenteFalso(), date(2026, 8, 26), db)

    m = listar_mencoes(db)[0]
    assert (m.relevancia, m.reprocessar) == (7, False)


def test_ia_e_chamada_uma_vez_por_mencao_nova_nunca_para_ja_vista(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [N1, N3]})
    db = tmp_path / "radar.db"
    cfg = config(tmp_path)
    ia = IAContadora()

    coletar(cfg, fonte, ia, RemetenteFalso(), HOJE, db)
    coletar(cfg, fonte, ia, RemetenteFalso(), date(2026, 8, 26), db)

    assert sorted(ia.chamadas) == sorted([N1.titulo, N3.titulo])


# ---------- ticket 04: Menção de marca + Alerta ----------

MARCA1 = Noticia("InoveMais fecha parceria com Lactec", "https://ex.com/m1", "Gazeta", "2026-08-25")
MARCA2 = Noticia("Startup de Curitiba, a i9+ recicla baterias", "https://ex.com/m2", "Folha", "2026-08-25")
MARCA_SEM_ACENTO = Noticia("Inovemais amplia fabrica", "https://ex.com/m3", "Bem Paraná", "2026-08-25")


def marcas(db):
    return sorted(m.link for m in listar_mencoes(db) if m.marca)


def alertas(rem):
    return [e for e in rem.enviados if "Alerta" in e[1]]


def test_termo_de_marca_no_titulo_marca_a_mencao_sem_acento_e_sem_caixa(tmp_path):
    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [MARCA1, MARCA_SEM_ACENTO, N3]})
    db = tmp_path / "radar.db"

    coletar(config(tmp_path), fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    assert marcas(db) == ["https://ex.com/m1", "https://ex.com/m3"]


def test_termo_de_setor_nao_marca(tmp_path):
    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"

    coletar(config(tmp_path), fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    assert marcas(db) == []


def test_alerta_de_marca_envia_um_email_com_todas_as_mencoes_novas(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [MARCA1, MARCA2], ("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()

    coletar(config(tmp_path), fonte, IAFalsa(), rem, HOJE, db)

    assert len(alertas(rem)) == 1
    dest, assunto, texto, html = alertas(rem)[0]
    assert dest == ["sandro@exemplo.com"]
    assert "Alerta de marca: 2 menções" in assunto
    for n in (MARCA1, MARCA2):
        assert n.titulo in texto and n.link in html and n.fonte in texto
    assert N3.titulo not in texto


def test_alerta_nao_e_reenviado_na_segunda_coleta_do_dia(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [MARCA1]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()
    cfg = config(tmp_path)

    coletar(cfg, fonte, IAFalsa(), rem, HOJE, db)
    coletar(cfg, fonte, IAFalsa(), rem, HOJE, db)

    assert len(alertas(rem)) == 1


def test_sem_mencao_de_marca_nao_ha_alerta(tmp_path):
    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()

    coletar(config(tmp_path), fonte, IAFalsa(), rem, HOJE, db)

    assert alertas(rem) == []


# ---------- ticket 05: Digest a cada N dias ----------


def digests(rem):
    return [e for e in rem.enviados if "Digest" in e[1]]


def test_primeiro_digest_sai_quando_nunca_houve_digest(tmp_path):
    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()

    coletar(config(tmp_path), fonte, IAFalsa(), rem, HOJE, db)

    (dest, assunto, texto, html) = digests(rem)[0]
    assert dest == ["sandro@exemplo.com", "equipe@exemplo.com"]
    assert N3.titulo in texto and "https://radar-i9.streamlit.app" in texto


def test_digest_respeita_o_intervalo(tmp_path):
    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()
    cfg = config(tmp_path)  # intervalo_dias = 7

    coletar(cfg, fonte, IAFalsa(), rem, date(2026, 8, 1), db)   # primeiro Digest
    coletar(cfg, fonte, IAFalsa(), rem, date(2026, 8, 7), db)   # 6 dias: não
    coletar(cfg, fonte, IAFalsa(), rem, date(2026, 8, 8), db)   # 7 dias: sim
    coletar(cfg, fonte, IAFalsa(), rem, date(2026, 8, 8), db)   # de novo no mesmo dia: não

    assert len(digests(rem)) == 2


def test_digest_ordena_marca_primeiro_depois_relevancia_e_sem_nota_por_ultimo(tmp_path):
    NOTA3 = Noticia("Preço do lítio cai no mercado global", "https://ex.com/n3", "Valor", "2026-08-25")

    class IAPorTitulo:
        notas = {NOTA3.titulo: 3, N3.titulo: 9, MARCA1.titulo: 2}

        def analisar(self, titulo, fonte):
            if titulo == N2.titulo:
                raise RuntimeError("falhou")
            return {"resumo": "r", "relevancia": self.notas[titulo], "tema": "t", "sentimento": "neutro"}

    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [NOTA3, N2, N3, MARCA1]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()

    coletar(config(tmp_path), fonte, IAPorTitulo(), rem, HOJE, db)

    texto = digests(rem)[0][2]
    pos = [texto.index(n.titulo) for n in (MARCA1, N3, NOTA3, N2)]
    assert pos == sorted(pos)


def test_digest_mostra_top_20_e_conta_o_resto(tmp_path):
    muitas = [Noticia(f"Notícia {i:02d}", f"https://ex.com/{i}", "F", "2026-08-25") for i in range(25)]
    fonte = FonteFalsa({("baterias de segunda vida", "pt"): muitas})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()

    coletar(config(tmp_path), fonte, IAFalsa(), rem, HOJE, db)

    texto = digests(rem)[0][2]
    assert sum(1 for n in muitas if n.titulo in texto) == 20
    assert "mais 5" in texto and "https://radar-i9.streamlit.app" in texto


def test_digest_vazio_e_enviado_quando_nao_ha_mencao_nova(tmp_path):
    fonte = FonteFalsa({})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()

    coletar(config(tmp_path), fonte, IAFalsa(), rem, HOJE, db)

    assert len(digests(rem)) == 1 and "Nenhuma menção nova" in digests(rem)[0][2]


def test_mencao_de_marca_que_ja_gerou_alerta_continua_no_topo_do_digest(tmp_path):
    fonte = FonteFalsa({("InoveMais", "pt"): [MARCA1], ("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()

    coletar(config(tmp_path), fonte, IAFalsa(), rem, HOJE, db)

    alertas = [e for e in rem.enviados if "Alerta" in e[1]]
    texto = digests(rem)[0][2]
    assert len(alertas) == 1 and texto.index(MARCA1.titulo) < texto.index(N3.titulo)


# ---------- regressões da revisão de código ----------

from pathlib import Path

from radar.fontes import FonteGoogleNews

FIX = Path(__file__).parent / "fixtures"


def test_xml_real_gravado_atravessa_a_coleta_inteira(tmp_path):
    toml = CONFIG_TOML.replace('texto = "baterias de segunda vida"\nidiomas = ["pt"]', 'texto = "economia circular baterias"\nidiomas = ["pt"]')
    fonte = FonteGoogleNews(baixar=lambda url: (FIX / ("gnews-pt.xml" if "pt-BR" in url else "gnews-en.xml")).read_bytes())
    db = tmp_path / "radar.db"

    r = coletar(config(tmp_path, toml), fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    # InoveMais pt/en e 'economia circular baterias' pt leem os mesmos 2 arquivos: 8 (pt) + 31 (en), o resto é repetido
    assert (r["novas"], r["ignoradas"]) == (39, 8)
    assert len(listar_mencoes(db)) == 39


def test_mencao_de_ontem_reprocessada_hoje_com_marca_no_resumo_gera_alerta(tmp_path):
    class IAQueCitaAMarca(IAFalsa):
        def analisar(self, titulo, fonte):
            return {**super().analisar(titulo, fonte), "resumo": "A InoveMais foi citada como parceira."}

    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [N3]})
    db = tmp_path / "radar.db"
    rem = RemetenteFalso()
    cfg = config(tmp_path)
    coletar(cfg, fonte, IAQueFalha(), rem, date(2026, 8, 24), db)
    assert alertas(rem) == []

    coletar(cfg, fonte, IAQueCitaAMarca(), rem, HOJE, db)

    assert len(alertas(rem)) == 1 and N3.titulo in alertas(rem)[0][2]


def test_alerta_que_falhou_no_envio_sai_na_coleta_seguinte(tmp_path):
    class RemetenteQueFalha(RemetenteFalso):
        def enviar(self, *a):
            raise ConnectionError("smtp fora do ar")

    fonte = FonteFalsa({("InoveMais", "pt"): [MARCA1]})
    db = tmp_path / "radar.db"
    cfg = config(tmp_path)
    linhas = []
    coletar(cfg, fonte, IAFalsa(), RemetenteQueFalha(), HOJE, db, log=linhas.append)  # não explode
    assert any("smtp fora do ar" in l for l in linhas)

    rem = RemetenteFalso()
    coletar(cfg, fonte, IAFalsa(), rem, date(2026, 8, 26), db)

    assert len(alertas(rem)) == 1 and MARCA1.titulo in alertas(rem)[0][2]


def test_marca_ignora_acento_e_caixa(tmp_path):
    fonte = FonteFalsa({("baterias de segunda vida", "pt"): [Noticia("INOVEMAÍS anuncia nova planta", "https://ex.com/ac", "F", "2026-08-25")]})
    db = tmp_path / "radar.db"

    coletar(config(tmp_path), fonte, IAFalsa(), RemetenteFalso(), HOJE, db)

    assert marcas(db) == ["https://ex.com/ac"]
