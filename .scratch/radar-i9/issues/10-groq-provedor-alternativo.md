# 10: Groq como provedor de IA alternativo (plano B)

**What to build:** Trocar `provedor = "groq"` (e a chave correspondente na variável de ambiente) no config faz o robô usar a API do Groq (compatível com OpenAI, plano gratuito) em vez do Gemini, sem mudar mais nada. Serve de plano B se a cota gratuita do Gemini mudar no meio do semestre.

**Blocked by:** 03 (IA — resumo, Relevância, tema e sentimento)

**Status:** feita (fumaça real fica para quando houver chave do Groq)

- [x] Teste: com `provedor = "groq"`, a Coleta usa o adaptador Groq (verificado com dublê)
- [x] Adaptador Groq sem SDK, mesma interface de um método, mesmo JSON de saída
- [ ] Fumaça rodada uma vez com uma chave gratuita do Groq
- [x] Trade-offs da stack no quadro citam o plano B
