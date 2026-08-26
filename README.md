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
tests/             pytest com dublês; fixtures = XML real do Google News
```
