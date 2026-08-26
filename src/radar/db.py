"""Histórico: SQLite num arquivo. Nada é apagado, nunca."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS mencoes (
  chave TEXT PRIMARY KEY,
  titulo TEXT NOT NULL,
  link TEXT NOT NULL,
  fonte TEXT,
  data TEXT,
  idioma TEXT,
  termo TEXT,
  resumo TEXT,
  relevancia INTEGER,
  tema TEXT,
  sentimento TEXT,
  marca INTEGER NOT NULL DEFAULT 0,
  coletada_em TEXT NOT NULL,
  reprocessar INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS envios (
  id INTEGER PRIMARY KEY,
  tipo TEXT NOT NULL,
  data TEXT NOT NULL,
  quantidade INTEGER NOT NULL,
  chaves TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class Mencao:
    chave: str
    titulo: str
    link: str
    fonte: str
    data: str
    idioma: str
    termo: str
    resumo: str | None
    relevancia: int | None
    tema: str | None
    sentimento: str | None
    marca: bool
    coletada_em: str
    reprocessar: bool


def abrir(caminho: Path) -> sqlite3.Connection:
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def inserir_mencao(con, chave, noticia, idioma, termo, coletada_em) -> bool:
    """True se entrou; False se já existia (dedupe pela chave)."""
    cur = con.execute(
        "INSERT OR IGNORE INTO mencoes (chave, titulo, link, fonte, data, idioma, termo, coletada_em)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (chave, noticia.titulo, noticia.link, noticia.fonte, noticia.data, idioma, termo, coletada_em),
    )
    return cur.rowcount == 1


def _mencao(row) -> Mencao:
    d = dict(row)
    d["marca"] = bool(d["marca"])
    d["reprocessar"] = bool(d["reprocessar"])
    return Mencao(**d)


def listar_mencoes(caminho: Path) -> list[Mencao]:
    con = abrir(caminho)
    try:
        return [_mencao(r) for r in con.execute("SELECT * FROM mencoes ORDER BY coletada_em DESC, data DESC")]
    finally:
        con.close()


def pendentes_de_ia(con) -> list[Mencao]:
    return [_mencao(r) for r in con.execute("SELECT * FROM mencoes WHERE reprocessar = 1 ORDER BY coletada_em, data")]


def gravar_analise(con, chave, resumo, relevancia, tema, sentimento):
    con.execute(
        "UPDATE mencoes SET resumo=?, relevancia=?, tema=?, sentimento=?, reprocessar=0 WHERE chave=?",
        (resumo, relevancia, tema, sentimento, chave),
    )


def gravar_falha_de_ia(con, chave, titulo):
    """Guarda mesmo assim: título vira resumo, sem nota, continua marcada para reprocessar."""
    con.execute(
        "UPDATE mencoes SET resumo=COALESCE(resumo, ?), tema='sem classificação', reprocessar=1 WHERE chave=?",
        (titulo, chave),
    )


def gravar_marca(con, chave, marca: bool):
    con.execute("UPDATE mencoes SET marca=? WHERE chave=?", (int(marca), chave))


def por_chaves(con, chaves) -> list[Mencao]:
    if not chaves:
        return []
    q = ",".join("?" * len(chaves))
    return [_mencao(r) for r in con.execute(f"SELECT * FROM mencoes WHERE chave IN ({q})", list(chaves))]


def mencoes_de_marca(con) -> list[Mencao]:
    return [_mencao(r) for r in con.execute("SELECT * FROM mencoes WHERE marca = 1 ORDER BY data DESC")]


def sem_envio(con, tipo, mencoes) -> list[Mencao]:
    """Menções que ainda não constam em nenhum envio desse tipo."""
    ja = set()
    for (chaves,) in con.execute("SELECT chaves FROM envios WHERE tipo = ?", (tipo,)):
        ja.update(chaves.split(","))
    return [m for m in mencoes if m.chave not in ja]


def registrar_envio(con, tipo, data, mencoes):
    con.execute(
        "INSERT INTO envios (tipo, data, quantidade, chaves) VALUES (?, ?, ?, ?)",
        (tipo, data, len(mencoes), ",".join(m.chave for m in mencoes)),
    )


def ultimo_envio(con, tipo) -> str | None:
    r = con.execute("SELECT MAX(data) FROM envios WHERE tipo = ?", (tipo,)).fetchone()
    return r[0] if r else None


def todas_ordenadas_para_digest(con) -> list[Mencao]:
    """Marca primeiro, depois Relevância decrescente (sem nota por último), depois data."""
    return [_mencao(r) for r in con.execute(
        "SELECT * FROM mencoes ORDER BY marca DESC, relevancia IS NULL, relevancia DESC, data DESC")]


def ultima_coleta(caminho: Path) -> str | None:
    con = abrir(caminho)
    try:
        return con.execute("SELECT MAX(coletada_em) FROM mencoes").fetchone()[0]
    finally:
        con.close()


def ultimo_envio_por_tipo(caminho: Path, tipo) -> str | None:
    con = abrir(caminho)
    try:
        return ultimo_envio(con, tipo)
    finally:
        con.close()
