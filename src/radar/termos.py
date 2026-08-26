"""Gerenciar Termos pelo Painel: edita o config.toml direto no GitHub (a fonte da verdade), sem a pessoa abrir o repositório.

O robô lê o config na próxima Coleta; o Streamlit Cloud republica o Painel sozinho depois do commit.
"""

import base64
import json
import re
import tomllib
import urllib.request

API = "https://api.github.com/repos/{repo}/contents/{caminho}"


def _bloco(t) -> str:
    linhas = ["[[termos]]", f'texto = "{t["texto"]}"']
    if t.get("marca"):
        linhas.append("marca = true")
    linhas.append("idiomas = [" + ", ".join(f'"{i}"' for i in t.get("idiomas", [])) + "]")
    return "\n".join(linhas) + "\n"


def _validar(texto: str) -> str:
    texto = " ".join(texto.split())
    if not texto:
        raise ValueError("O Termo não pode ficar vazio.")
    if '"' in texto or "\n" in texto:
        raise ValueError("O Termo não pode ter aspas.")
    return texto


def adicionar_termo(toml_txt: str, texto: str, idiomas: list[str], marca: bool = False) -> str:
    texto = _validar(texto)
    raw = tomllib.loads(toml_txt)
    if any(t["texto"].lower() == texto.lower() for t in raw.get("termos", [])):
        raise ValueError(f'"{texto}" já está na lista.')
    novo = toml_txt.rstrip("\n") + "\n\n" + _bloco({"texto": texto, "idiomas": idiomas, "marca": marca})
    tomllib.loads(novo)  # garante que o arquivo continua válido antes de gravar
    return novo


def remover_termo(toml_txt: str, texto: str) -> str:
    padrao = re.compile(r"\n*\[\[termos\]\]\n(?:(?!\[\[).)*?texto = \"" + re.escape(texto) + r"\"\n(?:(?!\[\[)[^\n]*\n?)*", re.S)
    novo, n = padrao.subn("\n", toml_txt, count=1)
    if n == 0:
        raise ValueError(f'"{texto}" não está na lista.')
    novo = novo.rstrip("\n") + "\n"
    tomllib.loads(novo)
    return novo


def termos_de(toml_txt: str) -> list[dict]:
    return tomllib.loads(toml_txt).get("termos", [])


def _chamar(url, token, dados=None, metodo="GET"):
    req = urllib.request.Request(url, data=json.dumps(dados).encode() if dados else None, method=metodo,
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                          "User-Agent": "Radar i9+"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def ler_no_github(repo: str, token: str, caminho="config.toml") -> tuple[str, str]:
    """(conteúdo, sha) — o sha é exigido pelo GitHub para gravar por cima."""
    r = _chamar(API.format(repo=repo, caminho=caminho), token)
    return base64.b64decode(r["content"]).decode("utf-8"), r["sha"]


def gravar_no_github(repo: str, token: str, conteudo: str, sha: str, mensagem: str, caminho="config.toml") -> None:
    _chamar(API.format(repo=repo, caminho=caminho), token, metodo="PUT",
            dados={"message": mensagem, "content": base64.b64encode(conteudo.encode("utf-8")).decode(), "sha": sha})
