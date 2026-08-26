"""Adaptador do Google News, com XML real gravado (sem rede)."""

from pathlib import Path

from radar.fontes import FonteGoogleNews, url_de_busca

FIX = Path(__file__).parent / "fixtures"


def fonte_gravada(arquivo):
    return FonteGoogleNews(baixar=lambda url: (FIX / arquivo).read_bytes())


def test_url_de_busca_usa_regiao_do_idioma_e_janela_sem_aspas():
    assert url_de_busca("baterias de segunda vida", "pt") == (
        "https://news.google.com/rss/search?q=baterias+de+segunda+vida+when%3A2d&hl=pt-BR&gl=BR&ceid=BR%3Apt-419")
    assert "hl=en-US&gl=US&ceid=US%3Aen" in url_de_busca("second-life batteries", "en")


def test_xml_real_em_portugues_vira_noticias_com_campos_preenchidos():
    noticias = fonte_gravada("gnews-pt.xml").buscar("economia circular baterias", "pt")

    assert len(noticias) == 8
    n = noticias[0]
    assert n.titulo == "Governo do Estado institui Regulamento Geral de Logística Reversa no Rio de Janeiro"
    assert n.fonte == "Governo do Estado do Rio de Janeiro"
    assert n.data == "2026-08-25"
    assert n.link.startswith("https://news.google.com/rss/articles/")


def test_xml_real_em_ingles_tem_31_noticias_todas_com_titulo_link_e_data():
    noticias = fonte_gravada("gnews-en.xml").buscar("second life batteries", "en")

    assert len(noticias) == 31
    assert all(n.titulo and n.link and n.data for n in noticias)
