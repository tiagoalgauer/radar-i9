"""Fonte real: Google News RSS de busca, um pedido por Termo × idioma, biblioteca padrão."""

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from radar.coleta import Noticia

REGIAO = {  # idioma → parâmetros do Google News
    "pt": {"hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"},
    "en": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
}


def url_de_busca(termo: str, idioma: str, janela: str = "when:2d") -> str:
    r = REGIAO.get(idioma, REGIAO["pt"])
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": f"{termo} {janela}", **r})


def baixar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Radar i9+; projeto de extensão)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def noticias_do_rss(xml_bytes: bytes) -> list[Noticia]:
    raiz = ET.fromstring(xml_bytes)
    out = []
    for item in raiz.iter("item"):
        titulo = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not titulo or not link:
            continue
        fonte = (item.findtext("source") or "").strip()
        if not fonte and " - " in titulo:  # Google News põe "Título - Fonte" no title
            fonte = titulo.rsplit(" - ", 1)[1]
        if fonte and titulo.endswith(f" - {fonte}"):
            titulo = titulo[: -len(fonte) - 3]
        try:
            data = parsedate_to_datetime(item.findtext("pubDate") or "").date().isoformat()
        except (TypeError, ValueError):
            data = ""
        out.append(Noticia(titulo, link, fonte, data))
    return out


class FonteGoogleNews:
    def __init__(self, baixar=baixar, janela: str = "when:2d"):
        self.baixar, self.janela = baixar, janela

    def buscar(self, termo: str, idioma: str) -> list[Noticia]:
        return noticias_do_rss(self.baixar(url_de_busca(termo, idioma, self.janela)))
