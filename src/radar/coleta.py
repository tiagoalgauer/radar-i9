"""Uma Coleta inteira: config → fonte → dedupe → IA → histórico → Alerta/Digest."""

import hashlib
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from radar import db


@dataclass(frozen=True)
class Noticia:
    titulo: str
    link: str
    fonte: str
    data: str  # ISO (AAAA-MM-DD)


@dataclass(frozen=True)
class Termo:
    texto: str
    idiomas: tuple[str, ...]
    marca: bool = False


@dataclass(frozen=True)
class Config:
    nome: str
    intervalo_dias: int
    link_painel: str
    termos: tuple[Termo, ...]
    ia: dict = field(default_factory=dict)
    email: dict = field(default_factory=dict)


def carregar_config(caminho: Path) -> Config:
    raw = tomllib.loads(Path(caminho).read_text(encoding="utf-8"))
    termos = tuple(
        Termo(t["texto"], tuple(t.get("idiomas", ["pt"])), bool(t.get("marca", False)))
        for t in raw.get("termos", [])
    )
    return Config(
        nome=raw.get("nome", "Radar"),
        intervalo_dias=int(raw.get("intervalo_dias", 7)),
        link_painel=raw.get("link_painel", ""),
        termos=termos,
        ia=raw.get("ia", {}),
        email=raw.get("email", {}),
    )


def chave_de(link: str) -> str:
    return hashlib.sha1(link.encode("utf-8")).hexdigest()


def coletar(cfg: Config, fonte, ia, remetente, hoje: date, db_path: Path, log=print) -> dict:
    con = db.abrir(db_path)
    novas = 0
    for termo in cfg.termos:
        for idioma in termo.idiomas:
            try:
                noticias = fonte.buscar(termo.texto, idioma)
            except Exception as e:  # um feed quebrado não apaga o dia
                log(f"fonte: falhou '{termo.texto}' ({idioma}): {e}")
                continue
            for n in noticias:
                if db.inserir_mencao(con, chave_de(n.link), n, idioma, termo.texto, hoje.isoformat()):
                    novas += 1
    con.commit()
    log(f"coleta: {len(cfg.termos)} termos, {novas} mencoes novas")
    return {"novas": novas}
