---
status: accepted
---

# O robô mora na nuvem do GitHub e grava o histórico de volta no repositório

O Parceiro exige custo zero e quer "um agente que coleta e organiza sozinho". Decidimos que a Coleta roda no GitHub Actions (cron diário, repo público) e não num PC da empresa nem em servidor: ninguém precisa ligar nada, e o log do run é evidência datada para a etapa 6. Como a máquina do Actions é descartável, o arquivo SQLite com as Menções é commitado de volta no repositório ao fim de cada Coleta; o Painel (Streamlit Community Cloud, endereço grátis `*.streamlit.app`) lê esse arquivo do repo.

## Considered Options

- **Robô no PC da empresa** (Agendador do Windows): histórico local, mas exige PC ligado, Python instalado e manutenção pelo Parceiro. Rejeitado como padrão; mantido como comando local de brinde (mesmo código, só muda quem liga).
- **Banco online** (Supabase, Turso, Neon, Atlas, D1): resolve persistência sem commit, mas cada um é mais uma conta/senha para repassar ao Parceiro. Plano B se o commit do `.db` virar dor.
- **GitHub Pages estático** no lugar do Streamlit: nunca dorme, mas filtros mais pobres. Plano B se a hibernação de 12h do Streamlit incomodar.

## Consequences

- Histórico público (as Menções são notícias públicas; nada sensível entra no banco).
- Workflow com `contents: write`; commits do bot não devem redisparar o cron (evento `schedule` não dispara em push).
- Se o repositório ficar 60 dias sem atividade o cron é desativado — o commit diário do bot já conta como atividade.
