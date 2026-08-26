"""`uv run radar` — uma Coleta real. `uv run radar fumaca fonte|ia|email` — testa cada adaptador contra o mundo."""

import os
import sys
from datetime import date
from pathlib import Path

from radar import correio, fontes, ia
from radar.coleta import carregar_config, coletar

RAIZ = Path(__file__).resolve().parents[2]


def _env(nome):
    v = os.environ.get(nome, "").strip()
    return v or None


def _carregar_dotenv():
    p = RAIZ / ".env"
    if p.exists():
        for linha in p.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.lstrip().startswith("#"):
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def _remetente(cfg):
    usuario, senha = _env("SMTP_USER"), _env("SMTP_PASS")
    if usuario and senha and _env("RADAR_SIMULAR_ENVIO") is None:
        return correio.RemetenteGmail(usuario, senha, cfg.nome)
    print("e-mail: modo simulado (defina SMTP_USER e SMTP_PASS para enviar de verdade)")
    return correio.RemetenteSimulado()


def _ia(cfg):
    chave = _env("GROQ_API_KEY") if cfg.ia.get("provedor") == "groq" else _env("GEMINI_API_KEY")
    if not chave:
        print("ia: sem chave (GEMINI_API_KEY / GROQ_API_KEY) — Menções ficam para reprocessar")
        return _IASemChave()
    return ia.criar(cfg.ia, chave)


class _IASemChave:
    def analisar(self, titulo, fonte):
        raise RuntimeError("sem chave de IA")


def fumaca(alvo, cfg):
    if alvo == "fonte":
        fonte = fontes.FonteGoogleNews()
        for t in cfg.termos:
            for idioma in t.idiomas:
                noticias = fonte.buscar(t.texto, idioma)
                print(f"'{t.texto}' ({idioma}, when:2d): {len(noticias)} noticias")
                for n in noticias[:3]:
                    print(f"  - {n.data} | {n.fonte} | {n.titulo}")
    elif alvo == "ia":
        print(_ia(cfg).analisar("InoveMais e Lactec firmam parceria para baterias de segunda vida", "Gazeta do Povo"))
    elif alvo == "email":
        _remetente(cfg).enviar([_env("SMTP_USER") or "ninguem@exemplo.com"], f"{cfg.nome} — teste de envio",
                               "Se você recebeu isto, o envio funciona.", "<p>Se você recebeu isto, o envio funciona.</p>")
        print("e-mail de teste enviado")
    else:
        sys.exit("uso: radar fumaca fonte|ia|email")


def main():
    _carregar_dotenv()
    cfg = carregar_config(RAIZ / "config.toml")
    if len(sys.argv) > 1 and sys.argv[1] == "fumaca":
        return fumaca(sys.argv[2] if len(sys.argv) > 2 else "", cfg)
    r = coletar(cfg, fontes.FonteGoogleNews(), _ia(cfg), _remetente(cfg), date.today(), RAIZ / "radar.db")
    print(f"resumo: {r}")


if __name__ == "__main__":
    main()
