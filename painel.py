"""Painel do Radar i9+ — somente leitura, lê o radar.db do repositório. `uv run streamlit run painel.py`.

Layout inspirado nas plataformas de clipping (Brand24, Knewin, Zeeng, CoverageBook): números grandes no topo
com variação vs. período anterior, filtros na barra lateral, cartões de Menção em grade. Gráficos ficaram no commit ca1cc7f até a equipe decidir quais quer.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))  # Streamlit Cloud instala só o requirements.txt; o pacote radar vive em src/

from radar.coleta import carregar_config  # noqa: E402
from radar.db import listar_mencoes, ultimo_envio_por_tipo, ultima_coleta

DB = Path(os.environ.get("RADAR_DB", RAIZ / "radar.db"))
cfg = carregar_config(RAIZ / "config.toml")

# Paleta (validada p/ daltonismo sobre o fundo escuro): azul = setor, vermelho = marca (cores da i9+), verde = positivo.
AZUL, VERMELHO, VERDE, CINZA = "#4592ff", "#f5121c", "#22a35e", "#8a8f99"
COR_SENT = {"positivo": VERDE, "neutro": CINZA, "negativo": VERMELHO}
# Ícones (SVG inline, traço branco) — sem emoji.
_SVG = "<svg width='11' height='11' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='3' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:-1px;margin-right:.3rem'>{}</svg>"
ICONE = {
    "positivo": _SVG.format("<path d='M20 6 9 17l-5-5'/>"),                     # check
    "neutro": _SVG.format("<path d='M5 12h14'/>"),                              # traço
    "negativo": _SVG.format("<path d='M12 5v9'/><path d='M12 18h.01'/>"),      # exclamação
    "sem análise": _SVG.format("<circle cx='12' cy='12' r='8'/>"),
    "marca": _SVG.format("<path d='M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9'/><path d='M10 21h4'/>"),  # sino
}
PERIODOS = {"7 dias": 7, "30 dias": 30, "90 dias": 90, "Tudo": None}

st.set_page_config(page_title=cfg.nome, page_icon=str(RAIZ / "static" / "logo-i9.png"), layout="wide")
st.logo(str(RAIZ / "static" / "logo-i9.png"), size="large", link="https://inovemais.tec.br")
st.markdown(
    f"""<style>
    .block-container {{ padding-top: 1.2rem; }}
    [data-testid="stMetric"] {{ background: #1a1d24; border-radius: 12px; padding: .9rem 1rem; }}
    [data-testid="stMetricLabel"] {{ text-transform: uppercase; letter-spacing: .06em; font-size: .72rem; opacity: .75; }}
    .pill {{ display:inline-block; padding:.1rem .55rem; border-radius:999px; font-size:.72rem; font-weight:600;
             letter-spacing:.02em; margin-right:.35rem; color:#fff; }}
    .meta {{ color:#9aa0ab; font-size:.78rem; margin:.4rem 0 0; }}
    .resumo {{ color:#c9ccd3; font-size:.88rem; line-height:1.4; }}
    .titulo a {{ color:#f2f2f2; text-decoration:none; font-weight:600; font-size:1.02rem; }}
    .titulo a:hover {{ color:{AZUL}; }}
    .faixa {{ height:6px; border-radius:3px; background:linear-gradient(90deg,{VERMELHO},{AZUL}); margin-bottom:.6rem; }}
    </style><div class="faixa"></div>""",
    unsafe_allow_html=True)

mencoes = listar_mencoes(DB) if DB.exists() else []
ultima = ultima_coleta(DB) if DB.exists() else None
ultimo_digest = ultimo_envio_por_tipo(DB, "digest") if DB.exists() else None
proximo = (date.fromisoformat(ultimo_digest) + timedelta(days=cfg.intervalo_dias)).isoformat() if ultimo_digest else "na próxima Coleta"

cab, status = st.columns([3, 2], vertical_alignment="bottom")
cab.title(cfg.nome)
cab.caption("Tudo que saiu sobre a i9+/InoveMais e o setor, coletado todo dia pelo robô. Nada é descartado; a Relevância só ordena.")
status.markdown(
    f"<div class='meta' style='text-align:right'>Última Coleta: <b>{ultima or '—'}</b> &nbsp;·&nbsp; "
    f"Último Digest: <b>{ultimo_digest or '—'}</b> &nbsp;·&nbsp; Próximo: <b>{proximo}</b> (a cada {cfg.intervalo_dias} dias)</div>",
    unsafe_allow_html=True)

if not mencoes:
    st.info("Ainda não há Menções. O robô roda todo dia às 8h; o primeiro histórico aparece depois da primeira Coleta.")
    st.stop()

df = pd.DataFrame([m.__dict__ for m in mencoes])
df["data"] = df["data"].fillna("")
df["sentimento"] = df["sentimento"].fillna("sem análise")
hoje = date.today()

# ---------- Filtros (barra lateral: fica à vista enquanto a lista rola) ----------
with st.sidebar:
    st.header("Filtros")
    periodo = st.pills("Período", list(PERIODOS), default="30 dias", key="periodo") or "Tudo"
    so_marca = st.checkbox("Só Menções de marca", key="so_marca", help="Só o que cita a i9+/InoveMais diretamente.")
    busca = st.text_input("Buscar no título ou resumo", key="busca", placeholder="ex.: Tecpar, lítio, edital…")
    sents = st.multiselect("Sentimento", ["positivo", "neutro", "negativo", "sem análise"], key="sents")
    termos = st.multiselect("Termo", sorted(df["termo"].dropna().unique()), key="termos")
    idiomas = st.multiselect("Idioma", sorted(df["idioma"].dropna().unique()), key="idiomas")


def no_periodo(base, inicio, fim):
    """Menção sem data nunca some por causa do período."""
    return base[(base["data"] == "") | ((base["data"] >= inicio.isoformat()) & (base["data"] <= fim.isoformat()))]


dias = PERIODOS[periodo]
f = df
anterior = None  # mesmo recorte, período imediatamente anterior — pra dizer "subiu/caiu"
if dias:
    f = no_periodo(df, hoje - timedelta(days=dias), hoje)
    anterior = df[(df["data"] >= (hoje - timedelta(days=2 * dias)).isoformat()) & (df["data"] < (hoje - timedelta(days=dias)).isoformat())]
if so_marca:
    f = f[f["marca"]]
    anterior = anterior[anterior["marca"]] if anterior is not None else None
if termos:
    f = f[f["termo"].isin(termos)]
if idiomas:
    f = f[f["idioma"].isin(idiomas)]
if sents:
    f = f[f["sentimento"].isin(sents)]
if busca:
    b = busca.lower()
    f = f[f["titulo"].str.lower().str.contains(b, regex=False, na=False) | f["resumo"].fillna("").str.lower().str.contains(b, regex=False)]


def favorabilidade(base):
    """% de positivas entre as Menções que a IA já classificou (como as plataformas de clipping mostram)."""
    c = base[base["sentimento"].isin(COR_SENT)]
    return round(100 * (c["sentimento"] == "positivo").mean()) if len(c) else None


def delta(atual, ant, sufixo=""):
    return None if ant is None else f"{atual - ant:+d}{sufixo} vs. período anterior"


# ---------- Números grandes ----------
com_data = f[f["data"] != ""].copy()
por_dia = com_data.groupby("data").size().reindex(
    [(hoje - timedelta(days=i)).isoformat() for i in range(min(dias or 30, 30) - 1, -1, -1)], fill_value=0)
fav, fav_ant = favorabilidade(f), favorabilidade(anterior) if anterior is not None else None
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Menções", len(f), delta(len(f), len(anterior) if anterior is not None else None), chart_data=por_dia.tolist(), chart_type="area")
k2.metric("Menções de marca", int(f["marca"].sum()), delta(int(f["marca"].sum()), int(anterior["marca"].sum()) if anterior is not None else None),
          help="Citam a i9+/InoveMais diretamente (título ou trecho). Disparam Alerta no mesmo dia.")
k3.metric("Favorabilidade", f"{fav}%" if fav is not None else "—",
          None if fav is None or fav_ant is None else f"{fav - fav_ant:+d} p.p. vs. período anterior",
          help="Parcela de Menções positivas para a i9+ entre as já classificadas pela IA.")
k4.metric("Veículos", int(f["fonte"].nunique()), help="Sites/jornais diferentes que publicaram.")
k5.metric("Relevância média", f"{f['relevancia'].mean():.1f}/10" if f["relevancia"].notna().any() else "—",
          help="Nota 0–10 dada pela IA. Só ordena; nunca corta.")

# ---------- Lista ----------
f = f.sort_values(["marca", "relevancia", "data"], ascending=[False, False, False], na_position="last")
st.divider()
t1, t2 = st.columns([3, 1], vertical_alignment="center")
t1.subheader(f"{len(f)} de {len(df)} Menções")
t2.download_button("Baixar tudo (CSV)", df.to_csv(index=False).encode("utf-8-sig"), "radar-i9.csv", "text/csv", icon=":material/download:",
                   help="O histórico completo, sem filtro — para guardar no computador da empresa.", width="stretch")


def pill(texto, cor):
    return f"<span class='pill' style='background:{cor}'>{texto}</span>"


aba_cartoes, aba_tabela = st.tabs(["Cartões", "Tabela"])
with aba_tabela:
    st.dataframe(f[["data", "titulo", "fonte", "sentimento", "tema", "relevancia", "termo", "idioma", "link"]],
                 hide_index=True, width="stretch", column_config={"link": st.column_config.LinkColumn("link", display_text="abrir")})
with aba_cartoes:
    st.session_state.setdefault("limite", 40)
    lote = list(f.head(st.session_state["limite"]).iterrows())
    for i in range(0, len(lote), 3):
        for col, (_, m) in zip(st.columns(3), lote[i:i + 3]):
            etiquetas = pill(ICONE.get(m["sentimento"], "") + m["sentimento"], COR_SENT.get(m["sentimento"], "#3a3f4a"))
            if pd.notna(m["tema"]) and m["tema"]:
                etiquetas += pill(m["tema"], "#2b3140")
            if m["marca"]:
                etiquetas += pill(ICONE["marca"] + "i9+", VERMELHO)
            resumo = m["resumo"] if m["resumo"] and m["resumo"] != m["titulo"] else ""
            if len(resumo) > 220:
                resumo = resumo[:220].rsplit(" ", 1)[0] + "…"
            nota = f"{int(m['relevancia'])}/10" if pd.notna(m["relevancia"]) else "sem nota"
            meta = " · ".join(str(x) for x in [m["fonte"], m["data"], nota] if pd.notna(x) and x)
            with col.container(border=True):
                st.markdown(
                    f"<div>{etiquetas}</div>"
                    f"<div class='titulo' style='margin:.4rem 0 .3rem'><a href='{m['link']}' target='_blank'>{m['titulo']}</a></div>"
                    f"<div class='resumo'>{resumo}</div><div class='meta'>{meta}</div>",
                    unsafe_allow_html=True)
    if len(f) > st.session_state["limite"]:
        if st.button(f"Mostrar mais ({len(f) - st.session_state['limite']} restantes)"):
            st.session_state["limite"] += 40
            st.rerun()
