"""Costura 2: o Painel renderiza com um banco de fixture (fumaça, sem rede)."""

from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

from radar.coleta import carregar_config, coletar
from test_coleta import CONFIG_TOML, MARCA1, N2, N3, FonteFalsa, IAFalsa, RemetenteFalso

PAINEL = Path(__file__).parent.parent / "painel.py"


def banco_de_fixture(tmp_path):
    (tmp_path / "config.toml").write_text(CONFIG_TOML)
    cfg = carregar_config(tmp_path / "config.toml")
    db = tmp_path / "radar.db"
    fonte = FonteFalsa({("InoveMais", "pt"): [MARCA1], ("InoveMais", "en"): [N2], ("baterias de segunda vida", "pt"): [N3]})
    coletar(cfg, fonte, IAFalsa(), RemetenteFalso(), date(2026, 8, 25), db)
    return db


def test_painel_mostra_status_e_lista_e_filtro_de_marca_reduz(tmp_path, monkeypatch):
    monkeypatch.setenv("RADAR_DB", str(banco_de_fixture(tmp_path)))
    app = AppTest.from_file(str(PAINEL), default_timeout=30).run()

    assert not app.exception
    valores = [m.value for m in app.metric]
    assert "3" in valores and "2026-08-25" in valores and "7 dias" in valores
    assert app.subheader[0].value == "3 de 3 Menções"
    assert any(MARCA1.titulo in md.value for md in app.markdown)

    app.checkbox(key="so_marca").check().run()

    assert app.subheader[0].value == "1 de 3 Menções"
    assert not any(N3.titulo in md.value for md in app.markdown)


def test_painel_sem_banco_nao_quebra(tmp_path, monkeypatch):
    monkeypatch.setenv("RADAR_DB", str(tmp_path / "nao-existe.db"))
    app = AppTest.from_file(str(PAINEL), default_timeout=30).run()

    assert not app.exception
    assert any("Ainda não há Menções" in i.value for i in app.info)
