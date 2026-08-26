"""`uv run radar` — uma Coleta real. `uv run radar fumaca fonte|ia|email` — testa cada adaptador contra o mundo.

Coleta de estreia (uma vez, na mão): `uv run radar --janela 1y --termos "InoveMais,i9+ baterias"` olha 1 ano
para trás só nesses Termos. Também aceita RADAR_JANELA / RADAR_TERMOS no ambiente (é como o Actions passa)."""

import os
import sys
from datetime import date
from pathlib import Path

from radar import correio, fontes, ia
from radar.coleta import carregar_config, coletar, restringir_busca

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


NO_ACTIONS = bool(os.environ.get("GITHUB_ACTIONS"))


def _exigir_no_actions(o_que):
    """No GitHub Actions um segredo faltando é erro — nunca um run verde que não envia nada.
    Exceção explícita: a variável RADAR_SIMULAR_ENVIO ligada no repositório (modo demonstração)."""
    if NO_ACTIONS and _env("RADAR_SIMULAR_ENVIO") is None:
        sys.exit(f"erro: {o_que} não configurado nos Secrets do repositório (ou ligue a variável RADAR_SIMULAR_ENVIO)")


def _remetente(cfg):
    usuario, senha = _env("SMTP_USER"), _env("SMTP_PASS")
    if usuario and senha and _env("RADAR_SIMULAR_ENVIO") is None:
        return correio.RemetenteGmail(usuario, senha, cfg.nome)
    _exigir_no_actions("SMTP_USER/SMTP_PASS")
    print("e-mail: modo simulado (defina SMTP_USER e SMTP_PASS para enviar de verdade)")
    return correio.RemetenteSimulado()


def _ia(cfg):
    variavel = ia.variavel_da_chave(cfg.ia)
    chave = _env(variavel)
    if not chave:
        _exigir_no_actions(variavel)
        print(f"ia: sem {variavel} — Menções ficam para reprocessar")
        return _IASemChave()
    return ia.criar(cfg.ia, chave)


class _IASemChave:
    def analisar(self, titulo, fonte):
        raise RuntimeError("sem chave de IA")


def fumaca(alvo, cfg):
    if alvo == "fonte":
        fonte = fontes.FonteMultipla(fontes.FonteGoogleNews(), fontes.FonteBingNews())
        for f in cfg.feeds:
            print(f"feed '{f['nome']}': {len(fontes.FonteRSS().ler(f['url'], f['nome']))} noticias")
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


def _opcao(nome, env):
    """--nome valor na linha de comando, senão a variável de ambiente, senão None."""
    if f"--{nome}" in sys.argv:
        return sys.argv[sys.argv.index(f"--{nome}") + 1]
    return _env(env)


def main():
    _carregar_dotenv()
    cfg = carregar_config(RAIZ / "config.toml")
    if len(sys.argv) > 1 and sys.argv[1] == "fumaca":
        return fumaca(sys.argv[2] if len(sys.argv) > 2 else "", cfg)
    janela = _opcao("janela", "RADAR_JANELA")
    termos = _opcao("termos", "RADAR_TERMOS")
    if termos:
        cfg = restringir_busca(cfg, {t.strip().lower() for t in termos.split(",")})
        print(f"coleta restrita a: {', '.join(t.texto for t in cfg.termos if t.idiomas)}")
    # "tudo" = sem filtro de data (o when: do Google News não alcança mais que alguns meses)
    google = fontes.FonteGoogleNews(janela="" if janela == "tudo" else f"when:{janela}") if janela else fontes.FonteGoogleNews()
    fonte = fontes.FonteMultipla(google, fontes.FonteBingNews())  # dois índices; o Bing traz trecho do corpo
    if janela:
        print(f"janela de busca: {janela}")
    r = coletar(cfg, fonte, _ia(cfg), _remetente(cfg), date.today(), RAIZ / "radar.db", feeds=fontes.FonteRSS())
    print(f"resumo: {r}")


if __name__ == "__main__":
    main()
