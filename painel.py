"""Painel do Radar i9+ — somente leitura, lê o radar.db do repositório. `uv run streamlit run painel.py`."""

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

st.set_page_config(page_title=cfg.nome, page_icon=str(RAIZ / "static" / "logo-i9.png"), layout="wide")
st.logo(str(RAIZ / "static" / "logo-i9.png"), size="large", link="https://inovemais.tec.br")
st.markdown(
    "<div style='height:6px;border-radius:3px;background:linear-gradient(90deg,#f5121c,#4592ff);margin-bottom:.6rem'></div>",
    unsafe_allow_html=True)  # a barra do logo da i9+
st.title(cfg.nome)
st.caption("Menções à i9+/InoveMais e ao setor, coletadas todo dia pelo robô. Nada é descartado; a Relevância só ordena.")

mencoes = listar_mencoes(DB) if DB.exists() else []
ultima = ultima_coleta(DB) if DB.exists() else None
ultimo_digest = ultimo_envio_por_tipo(DB, "digest") if DB.exists() else None
proximo = (date.fromisoformat(ultimo_digest) + timedelta(days=cfg.intervalo_dias)).isoformat() if ultimo_digest else "na próxima Coleta"

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Menções no histórico", len(mencoes))
c2.metric("Última Coleta", ultima or "—")
c3.metric("Último Digest", ultimo_digest or "—")
c4.metric("Próximo Digest", proximo)
c5.metric("Intervalo", f"{cfg.intervalo_dias} dias")

if not mencoes:
    st.info("Ainda não há Menções. O robô roda todo dia às 8h; o primeiro histórico aparece depois da primeira Coleta.")
    st.stop()

df = pd.DataFrame([m.__dict__ for m in mencoes])

with st.sidebar:
    st.header("Filtros")
    so_marca = st.checkbox("Só Menções de marca (i9+/InoveMais)", key="so_marca")
    termos = st.multiselect("Termo", sorted(df["termo"].dropna().unique()), key="termos")
    temas = st.multiselect("Tema", sorted(df["tema"].dropna().unique()), key="temas")
    idiomas = st.multiselect("Idioma", sorted(df["idioma"].dropna().unique()), key="idiomas")
    datas = df["data"].replace("", pd.NA).dropna()
    if len(datas):
        d_min, d_max = date.fromisoformat(datas.min()), date.fromisoformat(datas.max())
        periodo = st.date_input("Período", (d_min, d_max), min_value=d_min, max_value=d_max, key="periodo")
    else:
        periodo = None
    busca = st.text_input("Buscar no título/resumo", key="busca")

f = df
if so_marca:
    f = f[f["marca"]]
if termos:
    f = f[f["termo"].isin(termos)]
if temas:
    f = f[f["tema"].isin(temas)]
if idiomas:
    f = f[f["idioma"].isin(idiomas)]
if periodo and len(periodo) == 2:
    sem_data = f["data"].fillna("") == ""  # Menção sem data nunca some por causa do período
    f = f[sem_data | ((f["data"] >= periodo[0].isoformat()) & (f["data"] <= periodo[1].isoformat()))]
if busca:
    b = busca.lower()
    f = f[f["titulo"].str.lower().str.contains(b, regex=False, na=False) | f["resumo"].fillna("").str.lower().str.contains(b, regex=False)]

f = f.sort_values(["marca", "relevancia", "data"], ascending=[False, False, False], na_position="last")

st.subheader(f"{len(f)} de {len(df)} Menções")
st.download_button("⬇️ Baixar tudo (CSV)", df.to_csv(index=False).encode("utf-8-sig"), "radar-i9.csv", "text/csv",
                   help="O histórico completo, sem filtro — para guardar no computador da empresa.")

for _, m in f.head(200).iterrows():
    marca = "🔔 " if m["marca"] else ""
    borda = "#f5121c" if m["marca"] else "#4592ff"
    nota = f"**{int(m['relevancia'])}/10**" if pd.notna(m["relevancia"]) else "sem nota"
    with st.container(border=True):
        st.markdown(f"<div style='border-left:4px solid {borda};padding-left:.6rem'>{marca}<b><a href='{m['link']}' target='_blank'>{m['titulo']}</a></b></div>", unsafe_allow_html=True)
        partes = [m["fonte"], m["data"], m["idioma"], nota, m["tema"], m["sentimento"], f"termo: {m['termo']}"]
        st.caption(" · ".join(str(x) for x in partes if pd.notna(x) and x))  # sem "nan"/vazios
        if m["resumo"] and m["resumo"] != m["titulo"]:
            st.write(m["resumo"])
if len(f) > 200:
    st.caption(f"Mostrando 200 de {len(f)}. Use os filtros ou baixe o CSV.")  # ponytail: paginação quando alguém pedir
