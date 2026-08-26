# 09: Rodar no PC do Parceiro (brinde)

**What to build:** O mesmo código roda no PC de qualquer pessoa com um comando só: um arquivo `.env` de exemplo com as variáveis, e instruções de no máximo 10 linhas (instalar `uv`, clonar, preencher `.env`, `uv run radar`). O histórico fica local nesse caso. Testado uma vez num Windows.

**Blocked by:** 05 (Digest a cada N dias)

**Status:** ready-for-human (instruções no README; falta o teste num Windows)

- [x] `.env.example` com todas as variáveis e comentários em português
- [ ] Instruções no README ✅ — falta testar num Windows por alguém da equipe
- [x] Rodar local não envia e-mail por acidente: modo "simular envio" ligado por padrão fora do Actions
