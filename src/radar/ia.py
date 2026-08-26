"""Provedores de IA: um método, texto → JSON. Gemini (plano A) e Groq (plano B), sem SDK."""

import json
import time
import urllib.error
import urllib.request

PROMPT = """Você analisa notícias para o Radar de uma empresa brasileira de baterias de segunda vida, economia circular
e energia renovável (a i9+ / InoveMais). Analise a notícia abaixo e responda SOMENTE um JSON com os campos:
"resumo" (2 a 3 frases em português do Brasil, mesmo que a notícia esteja em outro idioma; descreva SÓ o que a
notícia diz — NÃO cite a i9+ nem a InoveMais no resumo a menos que a própria notícia as mencione),
"relevancia" (inteiro de 0 a 10: quanto essa notícia importa para essa empresa acompanhar),
"tema" (uma categoria curta em português, ex.: "baterias", "economia circular", "energia solar", "regulação", "concorrência", "parceiros"),
"sentimento" ("positivo", "neutro" ou "negativo" para a i9+).

Título: {titulo}
Fonte: {fonte}
"""


def _post_json(url, corpo, cabecalhos, tentativas=4, esperar=time.sleep):
    dados = json.dumps(corpo).encode("utf-8")
    for i in range(tentativas):
        req = urllib.request.Request(url, data=dados, headers={"Content-Type": "application/json", **cabecalhos})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < tentativas - 1:
                esperar(2 ** (i + 1))  # 2, 4, 8 s
                continue
            corpo_erro = e.read().decode("utf-8", "replace")[:300].replace("\n", " ")
            raise RuntimeError(f"HTTP {e.code} em {url.split('?')[0]}: {corpo_erro}") from e
        except (urllib.error.URLError, TimeoutError):
            if i < tentativas - 1:
                esperar(2 ** (i + 1))
                continue
            raise


def _json_da_resposta(texto: str) -> dict:
    texto = texto.strip()
    if texto.startswith("```"):
        texto = texto.strip("`").removeprefix("json").strip()
    d = json.loads(texto)
    return {
        "resumo": str(d.get("resumo", "")).strip(),
        "relevancia": max(0, min(10, int(d.get("relevancia", 0)))),
        "tema": str(d.get("tema", "sem classificação")).strip().lower(),
        "sentimento": str(d.get("sentimento", "neutro")).strip().lower(),
    }


class GeminiIA:
    def __init__(self, chave: str, modelo: str = "gemini-3.5-flash-lite", esperar=time.sleep):
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        self.chave, self.esperar = chave, esperar

    def analisar(self, titulo: str, fonte: str) -> dict:
        corpo = {
            "contents": [{"parts": [{"text": PROMPT.format(titulo=titulo, fonte=fonte)}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
        }
        r = _post_json(self.url, corpo, {"x-goog-api-key": self.chave}, esperar=self.esperar)
        return _json_da_resposta(r["candidates"][0]["content"]["parts"][0]["text"])


class GroqIA:
    """Plano B: API compatível com OpenAI."""

    def __init__(self, chave: str, modelo: str = "openai/gpt-oss-120b", esperar=time.sleep):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.chave, self.modelo, self.esperar = chave, modelo, esperar

    def analisar(self, titulo: str, fonte: str) -> dict:
        corpo = {
            "model": self.modelo,
            "messages": [{"role": "user", "content": PROMPT.format(titulo=titulo, fonte=fonte)}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        r = _post_json(self.url, corpo, {"Authorization": f"Bearer {self.chave}"}, esperar=self.esperar)
        return _json_da_resposta(r["choices"][0]["message"]["content"])


PROVEDORES = {  # provedor → (classe, variável de ambiente da chave, modelo padrão)
    "gemini": (GeminiIA, "GEMINI_API_KEY", "gemini-3.5-flash-lite"),
    "groq": (GroqIA, "GROQ_API_KEY", "openai/gpt-oss-120b"),
}


def variavel_da_chave(cfg_ia: dict) -> str:
    return PROVEDORES[cfg_ia.get("provedor", "gemini")][1]


def criar(cfg_ia: dict, chave: str):
    classe, _, modelo_padrao = PROVEDORES[cfg_ia.get("provedor", "gemini")]
    return classe(chave, cfg_ia.get("modelo") or modelo_padrao)
