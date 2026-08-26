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
