# Radar i9+ — agente de clipping (nome provisório)

Robô que acorda sozinho todo dia, busca no Google News as notícias sobre a i9+/InoveMais e o setor
(baterias de segunda vida, economia circular, energia), resume com IA gratuita, guarda tudo num
histórico que nunca descarta nada, avisa por e-mail no mesmo dia quando a marca é citada, manda um
Digest a cada N dias e mostra tudo num Painel na web. **Custo zero: sem cartão, sem servidor, sem domínio.**

Projeto de Extensão "TI e Sociedade" — Universidade Positivo, Equipe 6 (ADS), parceiro i9+ Baterias e Energia.

- Vocabulário do projeto: [`CONTEXT.md`](CONTEXT.md) · Decisões: [`docs/adr/`](docs/adr/) · Spec e tickets: [`.scratch/radar-i9/`](.scratch/radar-i9/)
- Cotas gratuitas verificadas em 2026: [`docs/research/free-tiers-2026.md`](docs/research/free-tiers-2026.md)

## Equipe: como trabalhar sem o Tiago (viagem de 28/08 a ~14/09)

O que está no ar roda sozinho: o robô acorda todo dia às 8h (aba **Actions**) e o Painel https://radar-i9.streamlit.app
republica a cada commit na `main`. Nenhuma dessas duas coisas precisa de gente.

**O que falta** está nas [Issues](https://github.com/tiagoalgauer/radar-i9/issues) deste repositório (público: qualquer um lê e comenta).
Pegue uma, comente "peguei", comente "feito" quando terminar. Etiquetas: `sem-codigo` (conta, reunião, config), `codigo`
(mexe em `.py`), `so-o-tiago` (Secrets deste repo/do Streamlit — só o dono consegue; no fork, quem consegue é o dono do fork).

### Opção 1 (recomendada, não depende do Tiago): a equipe faz um Fork

1. **Um** colega clica em **Fork** (canto superior direito) → vira `usuario/radar-i9`, uma cópia inteira que é da equipe.
2. Nesse fork: *Settings → Collaborators* → adicionar os outros 7. Pronto, todo mundo tem escrita no repo da equipe.
3. Refazer o que não vem no fork (10 min, tudo descrito neste README):
   - *Settings → Secrets and variables → Actions*: `GEMINI_API_KEY` (chave grátis, seção "Configurar"); `SMTP_USER`/`SMTP_PASS` quando existir o Gmail do projeto.
     Enquanto não tem SMTP: **Variables** → `RADAR_SIMULAR_ENVIO` = `1`.
   - Aba **Actions** → *I understand… enable them* (fork vem com o cron desligado) → *radar → Run workflow* pra testar.
   - Publicar o Painel do fork no Streamlit (seção "Painel na web") com a conta de quem forkou; nos Secrets do Streamlit,
     `RADAR_REPO = "usuario/radar-i9"` pro botão de Termos gravar no fork. Trocar `link_painel` no `config.toml`.
4. Trabalhar no fork como num repo normal (regras abaixo). O repositório original fica como estava, em modo simulado.

### Opção 2: colaborador no repositório original

Precisa que o Tiago adicione o usuário do GitHub de cada um (*Settings → Collaborators*). Se acontecer antes da viagem, ótimo:
um repo só, Painel e Secrets já configurados. Se não, Opção 1.

### Regras pra ninguém derrubar o que está no ar (valem nos dois casos)

1. Nunca trabalhe direto na `main`: `git switch -c minha-mudanca` → commit → `git push -u origin minha-mudanca` → **Pull Request**.
2. **Outro colega** revisa e faz o merge (leu, o check `testes` está verde). Ninguém espera o Tiago.
3. **Nunca commite `radar.db`.** O robô commita ele todo dia; se aparecer no seu `git status` depois de um `uv run radar`, rode `git restore radar.db`.
4. Antes de abrir o PR: `git pull --rebase origin main` e `uv run pytest`.
5. Quebrou a `main` (Painel com erro)? `git revert <commit>` + push — o Painel volta em 1–2 min.

Mudanças que **não precisam de git**: Termos → botão *Gerenciar Termos* no Painel (quando o token estiver configurado) ou
editar `config.toml` direto no GitHub (seções abaixo). Feeds e e-mails → `config.toml` no GitHub (lápis → *Commit changes*).

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

## Fontes (ticket 11)

| Fonte | O que traz | Como configurar |
|---|---|---|
| **Google News RSS** | notícias por Termo, pt e en, últimos 2 dias | automático, por Termo |
| **Bing News RSS** | segundo índice + **trecho do corpo** (ajuda a achar a marca e a IA) | automático, por Termo |
| **Feeds fixos** (`[[feeds]]` no config) | RSS de sites (ex.: Embrapii) e **Google Alerts em modo RSS** (blogs, páginas, PDFs) | `nome` + `url` no `config.toml` |

Google Alerts: em https://www.google.com/alerts crie o alerta (ex.: `InoveMais`, `"i9+" baterias`, `site:linkedin.com InoveMais`),
em *Mostrar opções* escolha **Entregar para: Feed RSS**, copie a URL do feed e cole num `[[feeds]]`. Grátis, sem chave.
A mesma matéria vinda de duas Fontes entra uma vez (link real + título).

Fora do alcance (sem API gratuita): LinkedIn e Instagram — ver `docs/research/fontes-alem-do-google-news.md`.

## Adicionar ou remover um Termo pelo Painel (botão)

Na barra lateral do Painel, **Gerenciar Termos** -> senha da equipe -> formulário. O Painel grava o `config.toml` no GitHub
por trás dos panos; o robô usa na próxima Coleta e o Painel republica sozinho em 1–2 min. Pra funcionar, dois Secrets no
Streamlit Cloud (app -> Settings -> Secrets):

```toml
GITHUB_TOKEN = "github_pat_..."   # token fine-grained: só o repositório radar-i9, permissão Contents: Read and write
SENHA_TERMOS = "uma senha combinada com o Sandro"
```

Token: GitHub -> Settings -> Developer settings -> Fine-grained tokens -> Generate; validade de 1 ano; ao vencer, gerar outro.

## Adicionar ou trocar um Termo sem instalar nada

1. Abra https://github.com/tiagoalgauer/radar-i9/blob/main/config.toml e clique no lápis (**Edit**).
2. Copie um bloco `[[termos]]` existente e mude o `texto` (sem aspas dentro do texto) e os `idiomas` (`["pt"]`, `["en"]` ou os dois).
   Se for nome da empresa, coloque `marca = true` — aí dispara Alerta no mesmo dia.
3. **Commit changes** (botão verde). Pronto: o robô usa a lista nova na próxima Coleta (todo dia às 8h).
   Pra rodar na hora: aba **Actions** → *Radar* → **Run workflow**.

Quem tem permissão de editar: quem for colaborador do repositório (Settings → Collaborators). Dá pra convidar o Sandro.

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
  fontes.py        Google News RSS, Bing News RSS e feeds fixos ([[feeds]])
  ia.py            Gemini (plano A) / Groq (plano B)
  correio.py       Alerta, Digest, SMTP do Gmail
  termos.py        adicionar/remover Termo gravando o config.toml no GitHub (botão do Painel)
  cli.py           `uv run radar` e os comandos de fumaça
painel.py          Painel Streamlit (lê radar.db; botão Gerenciar Termos)
.github/workflows/ radar.yml = o cron diário · testes.yml = pytest em todo PR
tests/             pytest com dublês; fixtures = XML real das Fontes
radar.db           o histórico (commitado pelo robô — nunca por pessoas)
```
