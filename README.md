# Radar i9+ — agente de clipping (nome provisório)

Robô que acorda sozinho todo dia, busca no Google News as notícias sobre a i9+/InoveMais e o setor
(baterias de segunda vida, economia circular, energia), resume com IA gratuita, guarda tudo num
histórico que nunca descarta nada, avisa por e-mail no mesmo dia quando a marca é citada, manda um
Digest a cada N dias e mostra tudo num Painel na web. **Custo zero: sem cartão, sem servidor, sem domínio.**

Projeto de Extensão "TI e Sociedade" — Universidade Positivo, Equipe 6 (ADS), parceiro i9+ Baterias e Energia.

- Vocabulário do projeto: [`CONTEXT.md`](CONTEXT.md) · Decisões: [`docs/adr/`](docs/adr/) · Spec e tickets: [`.scratch/radar-i9/`](.scratch/radar-i9/)
- Cotas gratuitas verificadas em 2026: [`docs/research/free-tiers-2026.md`](docs/research/free-tiers-2026.md)

## Como funciona (uma Coleta)

1. Lê `config.toml` (Termos, Intervalo, destinatários).
2. Para cada Termo × idioma, busca no Google News RSS (`when:2d`).
3. Ignora o que já está no histórico (hash do link). **Nada é apagado, nunca.**
4. Cada Menção nova vai à IA: resumo em português, Relevância 0–10, tema, sentimento. Se a IA falhar,
   a Menção fica guardada com o título como resumo e é reprocessada na próxima Coleta.
5. Menção que cita `InoveMais`/`i9+` (Termos de marca) → **Alerta de marca** por e-mail no mesmo dia.
6. Se passaram N dias do último Digest → **Digest** (marca no topo, depois por Relevância, top 20 + link do Painel).
7. Grava `radar.db` de volta no repositório (no GitHub Actions).

## Rodar no seu PC

```bash
uv sync                      # instala (precisa do uv: https://docs.astral.sh/uv/)
cp .env.example .env         # preencha as chaves (opcional — sem elas roda em modo simulado)
uv run radar                 # uma Coleta completa
uv run pytest                # testes (sem internet, sem chave)
```

Sem `SMTP_USER`/`SMTP_PASS` o e-mail é **simulado** (impresso na tela, ninguém recebe). Sem
`GEMINI_API_KEY` as Menções são guardadas sem resumo e reprocessadas quando a chave existir.

### Comandos de fumaça (testam cada peça contra o mundo real)

```bash
uv run radar fumaca fonte    # busca no Google News e mostra o que achou por Termo
uv run radar fumaca ia       # manda uma notícia de exemplo ao Gemini (ou Groq) e mostra a resposta
uv run radar fumaca email    # envia um e-mail de teste para o próprio SMTP_USER
```

## Robô na nuvem (GitHub Actions) — ticket 06

O workflow `.github/workflows/radar.yml` roda todo dia às 08:00 (Curitiba) e por clique
(*Actions → radar → Run workflow*). Ele coleta, resume, envia e commita o `radar.db` de volta (ADR-0001).

1. No repositório: **Settings → Secrets and variables → Actions → Secrets** → `GEMINI_API_KEY`, `SMTP_USER`, `SMTP_PASS`.
2. Enquanto os segredos não existem, ligue o **modo demonstração**: **Variables** → `RADAR_SIMULAR_ENVIO` = `1`.
   Sem essa variável e sem segredos o run **falha de propósito** (nunca um run verde que não envia nada).
3. Para demonstrar ao vivo: *Actions → radar → Run workflow*. O log mostra as linhas `coleta:`, `ia:`, `alerta de marca:`, `digest:`.

O cron do GitHub desliga se o repositório ficar 60 dias sem atividade — o commit diário do robô já conta como atividade.

## Painel na web (Streamlit Community Cloud) — tickets 07 e 08

Local: `uv run streamlit run painel.py` (abre em http://localhost:8501).

Publicar, de graça e sem domínio:

1. Entrar em https://share.streamlit.io com a conta do **GitHub** (nenhuma conta nova).
2. *Create app → Deploy a public app from GitHub* → repositório `radar-i9`, branch `main`, arquivo `painel.py`.
3. Em *App URL* escolher `radar-i9` → o endereço fica `https://radar-i9.streamlit.app`. Se mudar, atualize `link_painel` no `config.toml`.
4. O app relê o repositório a cada commit do robô, então o Painel acompanha o `radar.db` sozinho.

Depois de 12h sem ninguém abrir, o app hiberna; quem abrir espera ~15 s ele acordar (fato verificado em `docs/research/`).

## Rodar no PC da empresa (brinde — ticket 09)

O mesmo robô, sem GitHub, num Windows. Uma vez só:

1. Instalar o `uv`: abrir o **PowerShell** e colar `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
2. Baixar o projeto: `git clone https://github.com/tiagoalgauer/radar-i9.git` (ou *Code → Download ZIP* e descompactar).
3. Entrar na pasta: `cd radar-i9`.
4. Copiar `.env.example` para `.env` e preencher `GEMINI_API_KEY` (e `SMTP_USER`/`SMTP_PASS` se quiser e-mail de verdade).
5. `uv run radar` → faz uma Coleta; o histórico fica em `radar.db` **nesse PC**.
6. Painel local: `uv run streamlit run painel.py` → abre http://localhost:8501.

Sem `SMTP_USER`/`SMTP_PASS` nenhum e-mail sai (modo simulado). Para agendar todo dia sem o GitHub: *Agendador de Tarefas do Windows* → ação `uv run radar` na pasta do projeto. Testado em: _(pendente — anotar aqui o Windows e a data do primeiro teste)_.

## Plano B de IA: Groq (ticket 10)

Se a cota gratuita do Gemini mudar: criar uma chave grátis em https://console.groq.com (sem cartão), guardar como
`GROQ_API_KEY` (Secret do GitHub ou `.env`) e trocar no `config.toml`:

```toml
[ia]
provedor = "groq"
modelo = "openai/gpt-oss-120b"
```

Nada mais muda. Teste: `uv run radar fumaca ia`.

## Configurar

`config.toml` — Termos (com `marca = true` para os que disparam Alerta; `idiomas = []` para só detectar
sem buscar), `intervalo_dias`, destinatários, link do Painel, provedor/modelo de IA. Termos **sem aspas**.

Variáveis de ambiente (`.env` local ou *Secrets* do GitHub):

| Variável | Para quê |
|---|---|
| `GEMINI_API_KEY` | chave do Gemini (Google AI Studio, free tier) |
| `GROQ_API_KEY` | só se `provedor = "groq"` no config (plano B) |
| `SMTP_USER` | Gmail do projeto (remetente) |
| `SMTP_PASS` | senha de app desse Gmail (exige verificação em 2 etapas) |
| `RADAR_SIMULAR_ENVIO` | qualquer valor = não envia e-mail mesmo com credenciais |

## Estrutura

```
config.toml        Termos, Intervalo, destinatários
src/radar/
  coleta.py        uma Coleta inteira (a costura testada)
  db.py            histórico SQLite (mencoes, envios)
  fontes.py        Google News RSS
  ia.py            Gemini (plano A) / Groq (plano B)
  correio.py       Alerta, Digest, SMTP do Gmail
  cli.py           `uv run radar` e os comandos de fumaça
painel.py          Painel Streamlit (lê radar.db)
.github/workflows/ o cron diário
tests/             pytest com dublês; fixtures = XML real do Google News
```
