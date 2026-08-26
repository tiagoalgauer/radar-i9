"""Uma Coleta inteira: config → fonte → dedupe → IA → histórico → Alerta/Digest."""

import hashlib
import tomllib
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from radar import correio, db


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


def _simples(texto: str) -> str:
    """Sem acento e sem caixa, para comparar Termos de marca."""
    return "".join(c for c in unicodedata.normalize("NFD", texto or "") if unicodedata.category(c) != "Mn").lower()


def e_de_marca(cfg: Config, titulo: str, resumo: str | None) -> bool:
    alvo = _simples(f"{titulo} {resumo or ''}")
    return any(_simples(t.texto) in alvo for t in cfg.termos if t.marca)


def chave_de(link: str) -> str:
    return hashlib.sha1(link.encode("utf-8")).hexdigest()


def _enviar(con, cfg, remetente, tipo, mencoes, montar, hoje_iso, log) -> bool:
    """Envia e registra. Se o e-mail falhar, não registra: a próxima Coleta tenta de novo."""
    assunto, texto, html_ = montar(mencoes)
    try:
        remetente.enviar(list(cfg.email.get(tipo, [])), assunto, texto, html_)
    except Exception as e:
        log(f"{tipo}: falhou o envio ({e}); fica para a proxima Coleta")
        return False
    if getattr(remetente, "simulado", False):
        log(f"{tipo}: simulado, nao registrado — sai de verdade quando houver credenciais")
        return False
    db.registrar_envio(con, tipo, hoje_iso, mencoes)
    con.commit()
    return True


def coletar(cfg: Config, fonte, ia, remetente, hoje: date, db_path: Path, log=print) -> dict:
    con = db.abrir(db_path)
    try:
        return _coletar(cfg, fonte, ia, remetente, hoje, con, log)
    finally:
        con.close()


def _coletar(cfg, fonte, ia, remetente, hoje, con, log):
    hoje_iso = hoje.isoformat()
    novas = ignoradas = 0
    for termo in cfg.termos:
        for idioma in termo.idiomas:
            try:
                noticias = fonte.buscar(termo.texto, idioma)
            except Exception as e:  # um feed quebrado não apaga o dia
                log(f"fonte: falhou '{termo.texto}' ({idioma}): {e}")
                continue
            for n in noticias:
                if db.inserir_mencao(con, chave_de(n.link), n, idioma, termo.texto, hoje_iso):
                    novas += 1
                else:
                    ignoradas += 1
    db.registrar_coleta(con, hoje_iso, novas, ignoradas)
    con.commit()  # o dia está salvo antes de qualquer chamada de IA
    log(f"coleta: {len(cfg.termos)} termos, {novas} mencoes novas, {ignoradas} ja vistas")

    ok = falhas = 0
    tocadas = []
    for m in db.pendentes_de_ia(con):
        tocadas.append(m.chave)
        try:
            a = ia.analisar(m.titulo, m.fonte)
            db.gravar_analise(con, m.chave, a["resumo"], a.get("relevancia"), a.get("tema"), a.get("sentimento"))
            ok += 1
        except Exception as e:  # o robô nunca para por causa do provedor
            db.gravar_falha_de_ia(con, m.chave, m.titulo)
            falhas += 1
            if falhas == 1:
                log(f"ia: falhou '{m.titulo}': {e}")
    log(f"ia: {ok} ok, {falhas} falhas (ficam para reprocessar)")

    # marca é recalculada para tudo que passou pela IA nesta Coleta (novas e reprocessadas)
    for m in db.por_chaves(con, tocadas):
        db.gravar_marca(con, m.chave, e_de_marca(cfg, m.titulo, m.resumo))
    con.commit()

    marcas = db.sem_envio(con, "alerta", db.mencoes_de_marca(con))
    enviado = marcas and _enviar(con, cfg, remetente, "alerta", marcas,
                                 lambda ms: correio.montar_alerta(ms, cfg.link_painel, cfg.nome), hoje_iso, log)
    log(f"alerta de marca: {'enviado com ' + str(len(marcas)) + ' mencoes' if enviado else ('NAO enviado, ' + str(len(marcas)) + ' pendentes' if marcas else 'nada novo')}")

    ultimo = db.ultimo_envio(con, "digest")
    passados = (hoje - date.fromisoformat(ultimo)).days if ultimo else None
    digest = None
    if ultimo is None or passados >= cfg.intervalo_dias:
        pendentes = db.sem_envio(con, "digest", db.todas_ordenadas_para_digest(con))
        enviado = _enviar(con, cfg, remetente, "digest", pendentes,
                          lambda ms: correio.montar_digest(ms, cfg.link_painel, cfg.intervalo_dias, cfg.nome, primeiro=ultimo is None), hoje_iso, log)
        digest = len(pendentes)
        quando = 'primeiro' if ultimo is None else str(passados) + ' dias desde o ultimo'
        log(f"digest: {'enviado' if enviado else 'NAO enviado'} com {digest} mencoes ({quando})")
    else:
        log(f"digest: nao e dia ({passados} de {cfg.intervalo_dias} dias)")
    return {"novas": novas, "ignoradas": ignoradas, "ia_ok": ok, "ia_falhas": falhas, "alerta": len(marcas), "digest": digest}
