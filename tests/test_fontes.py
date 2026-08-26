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


def test_janela_vazia_busca_sem_filtro_de_data():
    assert url_de_busca("InoveMais", "pt", janela="") == "https://news.google.com/rss/search?q=InoveMais&hl=pt-BR&gl=BR&ceid=BR%3Apt-419"


# ---------- ticket 11: trecho + Fontes extras ----------

from radar.fontes import FonteBingNews, FonteRSS, url_bing


def test_bing_news_real_traz_trecho_link_real_e_veiculo():
    fonte = FonteBingNews(baixar=lambda url: (FIX / "bing-pt.xml").read_bytes())

    noticias = fonte.buscar("baterias segunda vida", "pt")

    assert len(noticias) == 11
    n = noticias[0]
    assert n.titulo == 'Nissan dá "segunda vida" às baterias do Leaf fora dos automóveis'
    assert n.link == "https://www.noticiasaominuto.com/auto/2945724/nissan-da-segunda-vida-as-baterias-do-leaf-fora-dos-automoveis"
    assert n.fonte == "Notícias ao Minuto" and n.data == "2026-02-26"
    assert n.trecho.startswith("Quando já não servem para automóveis")
    assert "format=rss" in url_bing("x", "pt") and "setlang=pt-BR" in url_bing("x", "pt") and "setlang=en-US" in url_bing("x", "en")


def test_feed_rss_generico_embrapii():
    noticias = FonteRSS(baixar=lambda url: (FIX / "embrapii.xml").read_bytes()).ler("https://embrapii.org.br/feed/", "Embrapii")

    assert len(noticias) == 21
    assert all(n.titulo and n.link.startswith("https://embrapii.org.br/") and n.data for n in noticias)
    assert noticias[0].fonte == "Embrapii"


def test_feed_atom_do_google_alerts_traz_link_real_e_trecho_sem_html():
    noticias = FonteRSS(baixar=lambda url: (FIX / "google-alerts.atom").read_bytes()).ler("https://www.google.com/alerts/feeds/0/1", "Google Alerts")

    assert len(noticias) == 1
    n = noticias[0]
    assert n.link == "https://www.senaipr.org.br/tecnologiaeinovacao/blog/visita-ao-parque-tecnologico"
    assert n.data == "2025-11-12" and "i9+ Baterias" in n.trecho and "<b>" not in n.trecho
