# 07: Painel v1 — Streamlit lendo o histórico

**What to build:** Um app Streamlit, no mesmo repositório, lê o `radar.db` e mostra: cabeçalho de status (última Coleta, último Digest, próximo Digest = último + Intervalo, Intervalo, total de Menções); filtros por Termo, tema, idioma, período e "só marca"; lista com título linkado, fonte, data, resumo, Relevância, tema e sentimento; Menções de marca destacadas; botão "Baixar CSV" com todo o histórico. Somente leitura. Um teste de fumaça (costura 2) carrega o app com um banco de fixture e verifica que o status e a lista renderizam e que "só marca" reduz a lista.

**Blocked by:** 01 (Esqueleto do projeto + primeira Coleta com dedupe)

**Status:** feita

- [ ] `uv run streamlit run ...` abre o Painel local com um banco de exemplo
- [ ] Status, filtros, destaque de marca e CSV funcionando
- [ ] Teste de fumaça com o utilitário de teste do Streamlit, sem rede
- [ ] Tudo em português; nada de edição de config pelo Painel (fora de escopo)
