# Free tiers para o bot de clipping — verificação em fontes primárias (2026-08-25)

Escopo: stack Python + Google News RSS + LLM grátis + SQLite + GitHub Actions cron + Streamlit Community Cloud + e-mail. Restrição: zero custo, sem cartão de crédito.
Método: só documentação oficial / páginas first-party, consultadas em 2026-08-25. Tudo que **não** foi confirmado em fonte primária está marcado com **[NÃO VERIFICADO]**.

## Resumo

| Serviço | Grátis? | Limite principal | Cartão? | Fonte |
|---|---|---|---|---|
| Gemini API (Free tier) | Sim — 2.5 Flash, 2.5 Flash-Lite, 3.5/3.6/3.7 Flash, 3.5/3.1 Flash-Lite etc. marcados "Free of charge" | RPM/RPD por modelo **não constam mais na doc**; só visíveis logado no AI Studio **[NÃO VERIFICADO]** | Não (conta nova começa no Free Tier) | https://ai.google.dev/gemini-api/docs/pricing · https://ai.google.dev/gemini-api/docs/rate-limits · https://ai.google.dev/gemini-api/docs/billing |
| GitHub Models | **NÃO — aposentado em 30/07/2026** | inference API, playground e BYOK desligados para todos | — | https://github.blog/changelog/2026-07-30-github-models-is-now-retired/ |
| Groq (Free plan) | Sim | ex.: `openai/gpt-oss-120b` 30 RPM / 1.000 RPD / 8K TPM / 200K TPD; Llama 3.x **não aparece** na tabela free | Não (cartão só no Developer plan) | https://console.groq.com/docs/rate-limits · https://console.groq.com/docs/billing-faqs |
| OpenRouter (`:free`) | Sim | 20 req/min; 50 req/dia (1.000/dia se já comprou ≥ US$10 de créditos) | Não | https://openrouter.ai/docs/api-reference/limits |
| Google News RSS (`/rss/search`) | Sim (sem doc oficial; uso "pessoal, não comercial" segundo o próprio feed) | `when:7d` e `after:AAAA-MM-DD` funcionam; máx. 100 itens por feed | Não | Teste empírico (ver §4) |
| GitHub Actions (repo público) | Sim, ilimitado em runners padrão | cron mín. 5 min; atrasos em picos; **desativa após 60 dias sem atividade**; job ≤ 6 h | Não | https://docs.github.com/en/billing/managing-billing-for-your-products/about-billing-for-github-actions · https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows |
| Streamlit Community Cloud | Sim ("all for free") | 690 MB–2,7 GB RAM; hiberna após **12 h** sem tráfego; 1 app privado por vez | Não | https://docs.streamlit.io/deploy/streamlit-community-cloud · https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app |
| Gmail SMTP + App Password | Sim (conta pessoal com verificação em 2 etapas) | ~500 e-mails/dia e ≤ 500 destinatários por mensagem | Não | https://support.google.com/accounts/answer/185833 · https://support.google.com/mail/answer/22839 |
| Brevo Free | Sim | 300 e-mails/dia; logo Brevo nos e-mails | Não | https://www.brevo.com/free-smtp-server/ · https://help.brevo.com/hc/en-us/articles/208580669 |
| Resend Free | Sim | 3.000/mês, 100/dia; **sem domínio verificado só envia para o próprio e-mail** | Não informado na página de preços **[NÃO VERIFICADO]** | https://resend.com/pricing · https://resend.com/docs/knowledge-base/403-error-resend-dev-domain |

## 1. Google Gemini API — free tier

- **Existe.** A página de preços diz: "Start building free of charge with generous limits, then scale up with prepaid then pay-as-you-go pricing". Modelos com coluna *Free tier* = "Free of charge" incluem: Gemini 3.7 Flash, 3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 3.1 Pro Preview, 2.5 Pro, 2.5 Flash, 2.5 Flash-Lite, 2.0 Flash/Flash-Lite e os modelos de embedding. Fonte: https://ai.google.dev/gemini-api/docs/pricing
- Preço pago de referência (por 1M tokens): 2.5 Flash-Lite US$0,10 in / US$0,40 out; 2.5 Flash US$0,30 / US$2,50; 3.6/3.7 Flash US$0,75 / US$3,75 até 31/12/2026. Fonte: mesma página.
- IDs atuais (https://ai.google.dev/gemini-api/docs/models): `gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-2.5-flash`, `gemini-2.5-flash-lite` (todos estáveis).
- **Limites RPM/RPD: a tabela por modelo saiu da documentação.** A página de rate limits (atualizada 2026-08-18) só mostra a tabela de tiers — Free: "Active project or free trial"; Tier 1: conta de billing ativa — e manda ver os limites em https://aistudio.google.com/rate-limit (exige login). Fonte: https://ai.google.dev/gemini-api/docs/rate-limits
  - **[NÃO VERIFICADO]** Últimos valores públicos que constavam na doc antes da remoção (memória, final de 2025): 2.5 Flash ≈ 10 RPM / 250 RPD; 2.5 Flash-Lite ≈ 15 RPM / 1.000 RPD. Confirmar no AI Studio com a conta do projeto antes de dimensionar. Para um clipping diário (algumas dezenas de resumos/dia) qualquer um desses valores sobra.
- **Cartão:** não. "New accounts begin on the Free Tier, which allows access to certain models... up to the models' free tier rate limits"; billing só para subir de tier. Fonte: https://ai.google.dev/gemini-api/docs/billing
- **Brasil:** listado em https://ai.google.dev/gemini-api/docs/available-regions. Os Termos só obrigam *Paid Services* para usuários finais no EEE/Suíça/Reino Unido — não afeta o Brasil. Fonte: https://ai.google.dev/gemini-api/terms
- **Privacidade (importante para a empresa):** nos *Unpaid Services* "Google uses the content you submit to the Services and any generated responses to provide, improve, and develop Google products" (https://ai.google.dev/gemini-api/terms). Como o bot só manda manchetes/trechos públicos de notícias, o risco é baixo, mas deve constar no relatório.

## 2. GitHub Models (models.github.ai)

- **Não existe mais.** Changelog oficial: "As of July 30, 2026, GitHub Models is now retired. The playground, model catalog, inference API, and bring your own key (BYOK) are no longer available to any customer". Alternativas indicadas: Microsoft Foundry (pago/Azure) e GitHub Copilot. Fontes: https://github.blog/changelog/2026-07-30-github-models-is-now-retired/ · https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/ · https://github.blog/changelog/2026-06-16-github-models-is-no-longer-available-to-new-customers/
- A página de docs https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models hoje só exibe o aviso de aposentadoria; não há mais tabela de rate limits nem permissão `models: read` na lista de escopos de `permissions` do workflow (https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).
- **Conclusão:** descartar do plano. Qualquer tutorial/artigo de 2025 sobre "LLM grátis via GITHUB_TOKEN" está obsoleto.

## 3. Plano B de LLM — Groq e OpenRouter

**Groq (Free plan)** — https://console.groq.com/docs/rate-limits
- Tabela Free plan (RPM / RPD / TPM / TPD): `openai/gpt-oss-120b` 30 / 1.000 / 8K / 200K; `openai/gpt-oss-20b` idem; `qwen/qwen3.6-27b` idem; `groq/compound` 30 / 250 / 70K / –; `whisper-large-v3` 20 / 2.000.
- `llama-3.3-70b-versatile` e `llama-3.1-8b-instant` seguem em https://console.groq.com/docs/models como modelos de produção, mas **não aparecem na tabela Free** — só usar o que está na tabela.
- Cartão: Developer plan exige "a valid payment method (credit card, US bank account, or SEPA debit account)"; o Free não. Fonte: https://console.groq.com/docs/billing-faqs
- TPM de 8K é apertado: resumir 1 notícia por chamada, com texto curto.

**OpenRouter (modelos `:free`)** — https://openrouter.ai/docs/api-reference/limits
- 20 requisições/min; 50 req/dia sem créditos; 1.000 req/dia se já comprou ≥ US$10 (uma vez, vitalício). FAQ: ":free — The model is always provided for free and has low rate limits" (https://openrouter.ai/docs/faq).
- 50 req/dia cobre um clipping diário pequeno; a lista de modelos `:free` muda sem aviso.

## 4. Google News RSS

- **Não há documentação oficial** do endpoint `/rss/search`. A busca em support.google.com / developers.google.com só retorna threads de comunidade e a doc do Feedfetcher (crawler), nada sobre parâmetros ou operadores. O próprio feed traz no `<copyright>`: "This XML feed is made available solely for the purpose of rendering Google News results within a personal feed reader for personal, non-commercial use, and any other use of the feed is expressly prohibited" — risco jurídico/ToS para uso por empresa, mesmo pequena (ver Riscos).
- **Teste empírico em 2026-08-26 00:19 UTC** (`curl`, User-Agent de navegador, `hl=pt-BR&gl=BR&ceid=BR:pt-419`), todos HTTP 200:

| query | itens | pubDate mais antigo → mais novo |
|---|---|---|
| `"baterias de segunda vida" when:7d` | 0 | — (frase exata é rara demais) |
| `"baterias de segunda vida"` (sem when) | 27 | 22/04/2024 → 18/05/2026 |
| `baterias segunda vida when:7d` | 1 | 21/08/2026 |
| `baterias when:7d` | 100 | 19/08/2026 → 25/08/2026 |
| `baterias when:30d` | 100 | 03/08/2026 → 25/08/2026 |
| `economia circular when:7d` | 67 | 19/08/2026 → 25/08/2026 |
| `"economia circular" when:7d` | 58 | 19/08/2026 → 25/08/2026 |
| `baterias after:2026-08-18` | 100 | 18/08/2026 → 25/08/2026 |

- Conclusões: `when:7d`, `when:30d` e `after:AAAA-MM-DD` **funcionam** e filtram por data corretamente; o feed é RSS 2.0 com `<title>`, `<link>` (redirect news.google.com), `<pubDate>`, `<source>`; teto de **100 itens** por consulta; queries com frase exata + `when:` ficam vazias facilmente — preferir termos soltos + `when:7d` e deduplicar por link/título no SQLite.

## 5. GitHub Actions em repositório público

- **Minutos:** "GitHub Actions usage is free for self-hosted runners and for public repositories that use standard GitHub-hosted runners". (Privado no plano Free: 2.000 min/mês.) Fonte: https://docs.github.com/en/billing/managing-billing-for-your-products/about-billing-for-github-actions
- **`schedule`:** intervalo mínimo 5 min; "can be delayed during periods of high loads... High load times include the start of every hour" (evite `0 * * * *`, use p.ex. `17 9 * * 1-5`); "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days"; roda só na branch default; UTC por padrão, mas hoje aceita `timezone: "America/Sao_Paulo"` ao lado do `cron`. Fonte: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- **Commit de volta com `GITHUB_TOKEN`:** basta `permissions: contents: write` no workflow ("write includes read"; escopos não citados viram `none`). Fonte: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
  - O push feito com `GITHUB_TOKEN` **não dispara outro workflow** ("events triggered by the GITHUB_TOKEN will not create a new workflow run", exceto `workflow_dispatch`/`repository_dispatch`). Bom: sem loop; e o commit diário do `clipping.db` conta como "atividade" e evita a desativação de 60 dias. Fonte: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
- Outros limites: job ≤ 6 h; 20 jobs simultâneos no Free; `GITHUB_TOKEN` 1.000 req/h por repo. Fonte: https://docs.github.com/en/actions/reference/limits

## 6. Streamlit Community Cloud

- **Grátis:** "you can create, deploy, and manage your Streamlit apps — all for free". Conecta a repositórios GitHub "public or private". Fonte: https://docs.streamlit.io/deploy/streamlit-community-cloud
- **Repo público não é obrigatório**, mas "You are only allowed one private app at a time". Fonte: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- **Recursos** (limites de fev/2024, "may change at any time without notice"): CPU 0,078–2 cores; RAM 690 MB–2,7 GB; storage até 50 GB. Estourar dá "This app has gone over its resource limits". Fonte: https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- **Hibernação:** "All apps without traffic for 12 hours go to sleep"; qualquer pessoa com acesso acorda clicando "Yes, get this app back up!". Mesma fonte. (Era 7 dias em versões antigas da doc — hoje é 12 h.)
- Apps hospedados nos EUA; updates via GitHub limitados a 5/min. Fonte: https://docs.streamlit.io/deploy/streamlit-community-cloud/status
- Implicação: o app dorme quase todo dia; o SQLite deve vir do repositório (commitado pelo Action), pois o disco do app não é persistente/confiável.

## 7. Gmail SMTP com App Password

- **Disponível** para conta pessoal com verificação em 2 etapas: "App passwords can only be used with accounts that have 2-Step Verification turned on". Indisponível se a 2-etapas for só por chave física, em contas de trabalho/escola (Workspace, depende do admin) ou com Proteção Avançada. Google avisa que "aren't recommended and are unnecessary in most cases" (recomenda Sign in with Google/OAuth) — mas continua funcionando. Fonte: https://support.google.com/accounts/answer/185833
- **Limite de envio (conta pessoal):** bloqueio temporário ao passar de "more than 500 emails sent in a day" ou "more than 500 recipients in a single email"; volta em 1–24 h. Fonte: https://support.google.com/mail/answer/22839
- **[NÃO VERIFICADO]** host/porta (`smtp.gmail.com`, 465 SSL / 587 STARTTLS): a página https://support.google.com/mail/answer/7126229 não expõe mais esses valores no texto obtido; são os valores padrão de longa data.
- Para um digest diário a 5–20 destinatários, o limite é irrelevante. Risco: usar a conta pessoal de um aluno — criar um Gmail dedicado ao projeto.

## 8. Plano B de e-mail — Brevo e Resend

**Brevo (ex-Sendinblue)**
- Página first-party do SMTP grátis: sem cartão, limite diário, exige verificação de remetente/autenticação de domínio, e **logo da Brevo nos e-mails** do plano grátis. Fonte: https://www.brevo.com/free-smtp-server/
- Número: **300 e-mails/dia**, sem rollover, sem cartão — consta em https://help.brevo.com/hc/en-us/articles/208580669-FAQs-What-are-the-limits-of-the-Free-plan e https://help.brevo.com/hc/en-us/articles/208589409 (páginas retornaram 403 ao fetch direto; valores lidos nos trechos indexados dessas mesmas URLs — **verificar na mão**).
- Destinatários arbitrários: sim, desde que o remetente (endereço ou domínio) seja verificado.

**Resend**
- Free: **3.000 e-mails/mês, 100/dia**, até 3 domínios. Fonte: https://resend.com/pricing. Cartão: página não diz **[NÃO VERIFICADO]**.
- **Sem domínio verificado não serve:** "You can only send testing emails to your own email address"; `resend.dev` "can only send emails to the email address associated with your Resend account". Fonte: https://resend.com/docs/knowledge-base/403-error-resend-dev-domain · https://resend.com/docs/dashboard/domains/introduction
- Só vale se a i9+ ceder um subdomínio (ex. `clipping.inovemais.com.br`) com DNS configurável.

## Riscos

1. **GitHub Models morreu (30/07/2026).** Tudo que planejava LLM "grátis" via `GITHUB_TOKEN` cai. Plano principal passa a ser Gemini; plano B Groq/OpenRouter.
2. **Gemini escondeu os limites do free tier** (tabela retirada da doc; só no AI Studio logado). Os números podem cair sem changelog — implementar retry/backoff e fallback de provedor desde o início. Dados enviados no free tier podem ser usados pelo Google para treinar.
3. **Google News RSS é não documentado e, pelo texto do próprio feed, restrito a uso pessoal não comercial.** Pode quebrar ou bloquear IP de runner do GitHub a qualquer momento. Alternativas gratuitas: RSS direto dos veículos do setor (documentado e legítimo). Registrar isso na parte de ética/impacto do trabalho.
4. **Cron do Actions desativa após 60 dias sem atividade** em repo público — mitigado pelo commit diário do banco. Atrasos de minutos/horas em horários cheios são normais.
5. **Streamlit hiberna em 12 h** sem visitas e limites "podem mudar sem aviso"; dashboard do cliente vai abrir "acordando". Não usar o disco do app como storage.
6. **Gmail App Passwords** é recurso que o Google desencoraja; pode ser removido de contas pessoais no futuro. Manter Brevo como contingência (300/dia, sem cartão, com logo).
7. **Groq free não inclui Llama 3.x** e tem TPM de 8K; OpenRouter `:free` dá só 50 req/dia sem crédito e a lista de modelos muda. Servem para contingência, não para carga principal.
