# 06: Robô na nuvem — GitHub Actions diário + commit do histórico

**What to build:** Um workflow do GitHub Actions acorda o robô todo dia às 8h (Curitiba) e também por disparo manual, instala `uv`, roda a Coleta com os segredos do repositório e, se o `radar.db` mudou, faz commit e push dele (ADR-0001). O log do run mostra as linhas de resumo da Coleta. O README explica em passos curtos como criar os segredos (chave do Gemini, usuário e senha de app do Gmail) e como disparar na mão. O primeiro run real é a primeira evidência datada do projeto.

**Blocked by:** 02 (Fonte real — Google News RSS em pt e en)

**Status:** feita

- [ ] Repositório público no GitHub com o código
- [ ] Workflow com `schedule` diário e `workflow_dispatch`, permissão `contents: write`
- [ ] Commit do `radar.db` só quando houver mudança; commit do bot não redispara o cron
- [ ] Segredos configurados; nenhum segredo no código
- [ ] Um run manual verde com Menções reais commitadas; print do log como evidência
- [ ] README: como configurar segredos, como disparar, como ler o log
