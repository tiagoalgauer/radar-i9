"""Painel do Radar i9+ — somente leitura, lê o radar.db do repositório. `uv run streamlit run painel.py`.

Layout inspirado nas plataformas de clipping (Brand24, Knewin, Zeeng, CoverageBook): números grandes no topo
com variação vs. período anterior, volume no tempo, favorabilidade, top Temas/veículos clicáveis, cartões de Menção.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import altair as alt
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
    .meta {{ color:#9aa0ab; font-size:.8rem; margin:.25rem 0 .1rem; }}
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
    f"<div class='meta' style='text-align:right'>🤖 Última Coleta: <b>{ultima or '—'}</b> &nbsp;·&nbsp; "
    f"📨 Último Digest: <b>{ultimo_digest or '—'}</b> &nbsp;·&nbsp; Próximo: <b>{proximo}</b> (a cada {cfg.intervalo_dias} dias)</div>",
    unsafe_allow_html=True)

if not mencoes:
    st.info("Ainda não há Menções. O robô roda todo dia às 8h; o primeiro histórico aparece depois da primeira Coleta.")
    st.stop()

df = pd.DataFrame([m.__dict__ for m in mencoes])
df["data"] = df["data"].fillna("")
df["sentimento"] = df["sentimento"].fillna("sem análise")
hoje = date.today()

# ---------- Filtros (uma linha; os gráficos também filtram) ----------
fc1, fc2, fc3 = st.columns([2, 1, 2], vertical_alignment="bottom")
periodo = fc1.pills("Período", list(PERIODOS), default="30 dias", key="periodo") or "Tudo"
so_marca = fc2.checkbox("Só Menções de marca", key="so_marca", help="Só o que cita a i9+/InoveMais diretamente.")
busca = fc3.text_input("Buscar no título ou resumo", key="busca", placeholder="ex.: Tecpar, lítio, edital…")
with st.expander("Mais filtros"):
    m1, m2, m3 = st.columns(3)
    termos = m1.multiselect("Termo", sorted(df["termo"].dropna().unique()), key="termos")
    idiomas = m2.multiselect("Idioma", sorted(df["idioma"].dropna().unique()), key="idiomas")
    sents = m3.multiselect("Sentimento", ["positivo", "neutro", "negativo", "sem análise"], key="sents")


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

# ---------- Gráficos ----------


def barras_h(campo, titulo, chave):
    """Top 8 em barras horizontais; clicar numa barra filtra a lista abaixo (limpe clicando fora)."""
    top = f[campo].dropna().value_counts().head(8).reset_index()
    top.columns = [campo, "n"]
    sel = alt.selection_point(fields=[campo], name="sel")
    ch = (alt.Chart(top).mark_bar(cornerRadiusEnd=4, height=18, color=AZUL)
          .encode(x=alt.X("n:Q", axis=None), y=alt.Y(f"{campo}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180)),
                  opacity=alt.condition(sel, alt.value(1), alt.value(0.35)),
                  tooltip=[alt.Tooltip(f"{campo}:N", title=titulo), alt.Tooltip("n:Q", title="Menções")])
          .add_params(sel).properties(height=8 * 26, title=alt.Title(titulo, anchor="start", fontSize=13, color="#c9ccd3")))
    texto = ch.mark_text(align="left", dx=4, color="#f2f2f2", fontSize=11).encode(text="n:Q", opacity=alt.value(1))
    ev = st.altair_chart((ch + texto).configure_view(stroke=None), on_select="rerun", key=chave)
    return ev.selection.get("sel", {}).get(campo, []) if hasattr(ev, "selection") else []


g1, g2 = st.columns([3, 2])
with g1:
    if len(com_data):
        semanal = not dias or dias > 60
        com_data["semana"] = pd.to_datetime(com_data["data"]).dt.to_period("W").dt.start_time if semanal else pd.to_datetime(com_data["data"])
        com_data["tipo"] = com_data["marca"].map({True: "Marca (i9+)", False: "Setor"})
        modo = st.pills("Colorir por", ["Marca × setor", "Sentimento"], default="Marca × setor", key="cor_volume", label_visibility="collapsed")
        if modo == "Sentimento":  # padrão Buzzmonitor: volume e mix de sentimento numa figura só
            cor, dom, cores = "sentimento", [*COR_SENT, "sem análise"], [*COR_SENT.values(), "#3a3f4a"]
        else:
            cor, dom, cores = "tipo", ["Setor", "Marca (i9+)"], [AZUL, VERMELHO]
        vol = (alt.Chart(com_data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
               .encode(x=alt.X("semana:T", title=None, axis=alt.Axis(format="%d/%m", grid=False, labelColor="#9aa0ab")),
                       y=alt.Y("count():Q", title=None, axis=alt.Axis(gridColor="#262a33", labelColor="#9aa0ab", tickCount=4)),
                       color=alt.Color(f"{cor}:N", scale=alt.Scale(domain=dom, range=cores),
                                       legend=alt.Legend(title=None, orient="top-right", labelColor="#c9ccd3")),
                       tooltip=[alt.Tooltip("semana:T", title="Data", format="%d/%m/%Y"), alt.Tooltip(f"{cor}:N", title=""), alt.Tooltip("count():Q", title="Menções")])
               .properties(height=8 * 26, title=alt.Title("Volume de Menções por " + ("semana" if semanal else "dia"),
                                                         anchor="start", fontSize=13, color="#c9ccd3")))
        st.altair_chart(vol.configure_view(stroke=None).configure(background="transparent"), width="stretch")
with g2:
    cont = f["sentimento"].value_counts().reindex(["positivo", "neutro", "negativo"], fill_value=0).reset_index()
    cont.columns = ["sentimento", "n"]
    sent = (alt.Chart(cont).mark_bar(cornerRadiusEnd=4, height=22)
            .encode(x=alt.X("n:Q", axis=None), y=alt.Y("sentimento:N", sort=["positivo", "neutro", "negativo"], title=None, axis=alt.Axis(labelColor="#c9ccd3")),
                    color=alt.Color("sentimento:N", scale=alt.Scale(domain=list(COR_SENT), range=list(COR_SENT.values())), legend=None),
                    tooltip=[alt.Tooltip("sentimento:N", title="Sentimento"), alt.Tooltip("n:Q", title="Menções")])
            .properties(height=8 * 26, title=alt.Title("Sentimento para a i9+", anchor="start", fontSize=13, color="#c9ccd3")))
    rot = sent.mark_text(align="left", dx=4, color="#f2f2f2", fontSize=11).encode(text="n:Q")
    st.altair_chart((sent + rot).configure_view(stroke=None).configure(background="transparent"), width="stretch")

g3, g4 = st.columns(2)
with g3:
    temas_sel = barras_h("tema", "Temas mais frequentes", "g_temas")
with g4:
    fontes_sel = barras_h("fonte", "Veículos que mais publicaram", "g_fontes")
if temas_sel:
    f = f[f["tema"].isin(temas_sel)]
if fontes_sel:
    f = f[f["fonte"].isin(fontes_sel)]

# ---------- Lista ----------
f = f.sort_values(["marca", "relevancia", "data"], ascending=[False, False, False], na_position="last")
st.divider()
t1, t2 = st.columns([3, 1], vertical_alignment="center")
t1.subheader(f"{len(f)} de {len(df)} Menções")
t2.download_button("⬇️ Baixar tudo (CSV)", df.to_csv(index=False).encode("utf-8-sig"), "radar-i9.csv", "text/csv",
                   help="O histórico completo, sem filtro — para guardar no computador da empresa.", width="stretch")


def pill(texto, cor):
    return f"<span class='pill' style='background:{cor}'>{texto}</span>"


aba_cartoes, aba_tabela = st.tabs(["Cartões", "Tabela"])
with aba_tabela:
    st.dataframe(f[["data", "titulo", "fonte", "sentimento", "tema", "relevancia", "termo", "idioma", "link"]],
                 hide_index=True, width="stretch", column_config={"link": st.column_config.LinkColumn("link", display_text="abrir")})
with aba_cartoes:
    st.session_state.setdefault("limite", 40)
    for _, m in f.head(st.session_state["limite"]).iterrows():
        borda = VERMELHO if m["marca"] else AZUL
        etiquetas = pill("🔔 MARCA", VERMELHO) if m["marca"] else ""
        etiquetas += pill(m["sentimento"], COR_SENT.get(m["sentimento"], "#3a3f4a"))
        if pd.notna(m["tema"]) and m["tema"]:
            etiquetas += pill(m["tema"], "#2b3140")
        nota = f"Relevância {int(m['relevancia'])}/10" if pd.notna(m["relevancia"]) else "sem nota"
        meta = " · ".join(str(x) for x in [m["fonte"], m["data"], m["idioma"], nota, f"termo: {m['termo']}"] if pd.notna(x) and x)
        with st.container(border=True):
            st.markdown(
                f"<div style='border-left:4px solid {borda};padding-left:.7rem'>"
                f"<div class='titulo'><a href='{m['link']}' target='_blank'>{m['titulo']}</a></div>"
                f"<div class='meta'>{meta}</div>{etiquetas}</div>",
                unsafe_allow_html=True)
            if m["resumo"] and m["resumo"] != m["titulo"]:
                st.write(m["resumo"])
    if len(f) > st.session_state["limite"]:
        if st.button(f"Mostrar mais ({len(f) - st.session_state['limite']} restantes)"):
            st.session_state["limite"] += 40
            st.rerun()
