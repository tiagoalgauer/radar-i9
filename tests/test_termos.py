"""Editar Termos no texto do config.toml sem quebrar o arquivo (o Painel grava isso no GitHub)."""

import pytest

from radar.termos import adicionar_termo, remover_termo, termos_de

CONFIG = '''nome = "Radar"
intervalo_dias = 7

[[termos]]
texto = "InoveMais"
marca = true
idiomas = ["pt", "en"]

[[termos]]
texto = "baterias de segunda vida"
idiomas = ["pt"]

[[feeds]]
nome = "Embrapii"
url = "https://embrapii.org.br/feed/"
'''


def test_adicionar_entra_no_fim_e_arquivo_continua_valido():
    novo = adicionar_termo(CONFIG, "  Lactec ", ["pt"], marca=False)
    termos = termos_de(novo)
    assert [t["texto"] for t in termos] == ["InoveMais", "baterias de segunda vida", "Lactec"]
    assert termos[-1] == {"texto": "Lactec", "idiomas": ["pt"]}
    assert termos_de(novo) and "Embrapii" in novo  # o resto do arquivo fica intacto


def test_adicionar_de_marca_e_recusa_repetido_ou_vazio():
    novo = adicionar_termo(CONFIG, "i9+ Baterias", ["pt", "en"], marca=True)
    assert termos_de(novo)[-1]["marca"] is True
    with pytest.raises(ValueError):
        adicionar_termo(CONFIG, "inovemais", ["pt"])
    with pytest.raises(ValueError):
        adicionar_termo(CONFIG, "   ", ["pt"])
    with pytest.raises(ValueError):
        adicionar_termo(CONFIG, 'com "aspas"', ["pt"])


def test_remover_tira_so_aquele_bloco():
    novo = remover_termo(CONFIG, "InoveMais")
    assert [t["texto"] for t in termos_de(novo)] == ["baterias de segunda vida"]
    assert "Embrapii" in novo and "intervalo_dias = 7" in novo
    with pytest.raises(ValueError):
        remover_termo(CONFIG, "não existe")


def test_adicionar_e_remover_voltam_ao_mesmo_conjunto():
    ida = adicionar_termo(CONFIG, "Lactec", ["pt"])
    volta = remover_termo(ida, "Lactec")
    assert termos_de(volta) == termos_de(CONFIG)
