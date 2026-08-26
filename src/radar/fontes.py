"""Fontes de Notícias, biblioteca padrão: Google News RSS, Bing News RSS, e feeds RSS/Atom fixos (Google Alerts, sites)."""

import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from radar.coleta import Noticia

REGIAO = {  # idioma → parâmetros do Google News
    "pt": {"hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"},
    "en": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
}
BING = {"pt": {"setlang": "pt-BR", "cc": "BR"}, "en": {"setlang": "en-US", "cc": "US"}}


def url_de_busca(termo: str, idioma: str, janela: str = "when:2d") -> str:
    r = REGIAO.get(idioma, REGIAO["pt"])
    q = f"{termo} {janela}".strip()  # janela vazia = sem filtro de data (coleta de estreia)
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, **r})


def url_bing(termo: str, idioma: str) -> str:
    return "https://www.bing.com/news/search?" + urllib.parse.urlencode({"q": termo, "format": "rss", **BING.get(idioma, BING["pt"])})


def baixar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Radar i9+; projeto de extensão)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _texto(el, nome: str) -> str:
    for filho in el:
        if _local(filho.tag) == nome:
            return (filho.text or "").strip()
    return ""


def _sem_html(texto: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", texto or ""))).strip()


def link_real(link: str) -> str:
    """Bing e Google Alerts embrulham o link do veículo num redirecionador com parâmetro url=."""
    u = urllib.parse.urlparse(link)
    if u.netloc.endswith(("bing.com", "google.com")):
        alvo = urllib.parse.parse_qs(u.query).get("url")
        if alvo:
            return alvo[0]
    return link


def _data(texto: str) -> str:
    if not texto:
        return ""
    try:
        return parsedate_to_datetime(texto).date().isoformat()  # RFC 822 (RSS)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).date().isoformat()  # ISO (Atom)
    except ValueError:
        return ""


def noticias_do_feed(xml_bytes: bytes, fonte_padrao: str = "") -> list[Noticia]:
    """RSS 2.0 (Google News, Bing, WordPress) e Atom (Google Alerts) no mesmo parser."""
    raiz = ET.fromstring(xml_bytes)
    out = []
    for item in raiz.iter():
        if _local(item.tag) not in ("item", "entry"):
            continue
        titulo = _sem_html(_texto(item, "title"))
        link = _texto(item, "link")
        if not link:  # Atom: <link href="..."/>
            for filho in item:
                if _local(filho.tag) == "link" and filho.get("href"):
                    link = filho.get("href")
                    break
        if not titulo or not link:
            continue
        fonte = _texto(item, "source") or _texto(item, "Source") or fonte_padrao
        if not fonte and " - " in titulo:  # Google News põe "Título - Fonte" no title
            fonte = titulo.rsplit(" - ", 1)[1]
        if fonte and titulo.endswith(f" - {fonte}"):
            titulo = titulo[: -len(fonte) - 3]
        data = _data(_texto(item, "pubDate") or _texto(item, "published") or _texto(item, "updated"))
        trecho = _sem_html(_texto(item, "description") or _texto(item, "content") or _texto(item, "summary"))
        if trecho.startswith(titulo) or "news.google.com" in trecho:  # Google News: description é só o link
            trecho = "" if "news.google.com" in trecho else trecho
        out.append(Noticia(titulo, link_real(link), fonte, data, trecho[:2000]))
    return out


noticias_do_rss = noticias_do_feed  # nome antigo


class FonteGoogleNews:
    def __init__(self, baixar=baixar, janela: str = "when:2d"):
        self.baixar, self.janela = baixar, janela

    def buscar(self, termo: str, idioma: str) -> list[Noticia]:
        return noticias_do_feed(self.baixar(url_de_busca(termo, idioma, self.janela)))


class FonteBingNews:
    def __init__(self, baixar=baixar):
        self.baixar = baixar

    def buscar(self, termo: str, idioma: str) -> list[Noticia]:
        return noticias_do_feed(self.baixar(url_bing(termo, idioma)))


class FonteRSS:
    """Feeds fixos por URL ([[feeds]] no config): Google Alerts em modo RSS, feed de sites (Embrapii, Tecpar…)."""

    def __init__(self, baixar=baixar):
        self.baixar = baixar

    def ler(self, url: str, nome: str) -> list[Noticia]:
        return noticias_do_feed(self.baixar(url), fonte_padrao=nome)


class FonteMultipla:
    """Soma Fontes de busca; uma falhando não derruba as outras (o log fica em `erros`)."""

    def __init__(self, *fontes, log=print):
        self.fontes, self.log = fontes, log

    def buscar(self, termo: str, idioma: str) -> list[Noticia]:
        out = []
        for f in self.fontes:
            try:
                out.extend(f.buscar(termo, idioma))
            except Exception as e:
                self.log(f"fonte {type(f).__name__}: falhou '{termo}' ({idioma}): {e}")
        return out
