# 03: IA — resumo em português, Relevância, tema e sentimento

**What to build:** Cada Menção nova recebe, numa única chamada à IA, resumo em português (2–3 frases), Relevância 0–10 para a i9+, tema curto e sentimento. Se a IA falhar depois das retentativas (429 com espera crescente), a Menção é gravada mesmo assim com o título como resumo, sem nota, tema "sem classificação" e marcada para reprocessar; a próxima Coleta reprocessa as marcadas antes das novas. O provedor é uma interface de um método (texto → JSON) — os testes usam uma IA falsa; o adaptador real fala com o Gemini por HTTP direto, modelo vindo do config. Um comando de fumaça envia uma Menção real ao Gemini e imprime a resposta.

**Blocked by:** 01 (Esqueleto do projeto + primeira Coleta com dedupe)

**Status:** feita

- [ ] Teste: IA falsa devolve JSON → Menção gravada com resumo, Relevância, tema e sentimento
- [ ] Teste: IA falsa lança erro → Menção gravada com título como resumo, Relevância vazia, marcada para reprocessar; Coleta não para
- [ ] Teste: na Coleta seguinte, com IA funcionando, a Menção marcada é reprocessada e desmarcada
- [ ] Teste: a IA é chamada uma vez por Menção nova, nunca para Menção já vista
- [ ] Adaptador Gemini sem SDK, chave só por variável de ambiente, retentativa em 429
- [ ] Log mostra chamadas ok / falhas
- [x] IA real rodou no Actions (run 32920388790, 26/08): 184 Menções analisadas, 27 em 429 reprocessam amanhã
