# Spec: Radar i9+ (nome provisório)

Status: ready-for-agent

## Problem Statement

A i9+/InoveMais (o Parceiro, representada pelo Sandro) precisa acompanhar o que sai na imprensa sobre a própria empresa e sobre o setor dela — baterias de segunda vida, economia circular, eletromobilidade, energia renovável — no Brasil e no mundo. Hoje isso é feito na mão, quando alguém lembra, e não fica registrado. Notícias sobre concorrentes, editais e parceiros passam batido; menções diretas à marca são descobertas tarde. A empresa não pode pagar ferramenta de clipping nem manter servidor: tudo tem que ser gratuito e funcionar sem alguém ligar.

## Solution

Um robô (o Radar) que acorda sozinho todo dia na nuvem do GitHub, busca no Google News as Menções novas para uma lista de Termos (em português e inglês), pede a uma IA gratuita um resumo em português, uma Relevância de 0 a 10, um tema e um sentimento para cada Menção, e guarda tudo num histórico que nunca descarta nada. Sempre que a i9+ for citada diretamente, o Sandro recebe um Alerta de marca por e-mail no mesmo dia. A cada Intervalo (N dias, escolhido por ele) recebe um Digest com o melhor do período. Tudo fica visível num Painel na web, com endereço gratuito, filtros e botão de baixar o histórico completo. O mesmo código roda no PC de qualquer pessoa com um comando só.

## User Stories

### Parceiro (Sandro)

1. Como Parceiro, quero receber um e-mail a cada N dias com as Menções mais relevantes do período, para acompanhar o setor sem precisar procurar.
2. Como Parceiro, quero escolher quantos dias há entre um Digest e o próximo, para o ritmo se adaptar à minha rotina.
3. Como Parceiro, quero ser avisado por e-mail no mesmo dia em que a i9+/InoveMais for citada, para reagir rápido a uma menção de marca.
4. Como Parceiro, quero que as Menções de marca apareçam no topo do Digest mesmo que já tenham gerado Alerta, para nada se perder.
5. Como Parceiro, quero que o Digest venha ordenado por Relevância, para ler o mais importante primeiro.
6. Como Parceiro, quero que o Digest mostre as 20 Menções mais relevantes e um link para ver o restante no Painel, para o e-mail não virar um livro.
7. Como Parceiro, quero ver no e-mail, para cada Menção, título, fonte, data, resumo em português e link, para decidir em segundos se abro.
8. Como Parceiro, quero que nenhuma Menção seja descartada por nota baixa, porque uma nota 3 pode ser relevante para mim.
9. Como Parceiro, quero abrir um endereço na web (sem instalar nada, sem senha) e ver todas as Menções, para consultar o histórico quando quiser.
10. Como Parceiro, quero filtrar o Painel por Termo, tema, idioma e período, para achar o que procuro.
11. Como Parceiro, quero as Menções de marca destacadas no Painel, para identificá-las de relance.
12. Como Parceiro, quero ver no Painel quando foi a última Coleta, o último Digest, o próximo Digest previsto e o Intervalo atual, para confiar que o robô está vivo.
13. Como Parceiro, quero baixar o histórico completo em CSV pelo Painel, para ter uma cópia no computador da empresa.
14. Como Parceiro, quero definir a lista de Termos (e quais são Termos de marca), para o Radar cobrir o que importa para a i9+.
15. Como Parceiro, quero Menções do mundo inteiro, em português e inglês, com resumo sempre em português, para não perder notícia internacional nem precisar traduzir.
16. Como Parceiro, quero que tudo funcione sem custo, sem cartão de crédito e sem servidor meu, porque essa é a condição do projeto.
17. Como Parceiro, quero ter a opção de rodar o robô no meu próprio PC com um comando, para ter o histórico local se um dia quiser.

### Equipe (os 8 alunos)

18. Como integrante da equipe, quero que o robô rode sozinho todo dia sem ninguém apertar nada, para a demonstração e a entrega serem de um agente autônomo.
19. Como integrante, quero editar Termos, Termos de marca, Intervalo, idiomas e destinatários num único arquivo de configuração, para ajustar o Radar após cada reunião com o Sandro sem mexer em código.
20. Como integrante, quero que o robô seja idempotente — rodar duas vezes no mesmo dia não duplica Menções nem reenvia e-mail —, para poder disparar na mão sem medo.
21. Como integrante, quero poder disparar o robô manualmente pelo GitHub, para demonstrar ao vivo na reunião e no vídeo.
22. Como integrante, quero que o histórico fique dentro do repositório, versionado, para que cada execução seja evidência datada para a etapa 6.
23. Como integrante, quero que uma falha da IA (cota estourada, erro) não perca a Menção: ela fica guardada com o título como resumo e sem nota, para o robô nunca parar por causa do provedor.
24. Como integrante, quero que uma falha de uma fonte ou de um Termo não derrube a Coleta inteira, para um feed quebrado não apagar o dia.
25. Como integrante, quero um log legível de cada execução (quantas Menções novas, quantas de marca, se enviou Digest/Alerta), para diagnosticar e tirar print como evidência.
26. Como integrante, quero que as credenciais (chave da IA, senha de app do e-mail) fiquem fora do código, em segredos do GitHub ou variáveis de ambiente, para o repositório poder ser público.
27. Como integrante, quero testes automatizados que rodem sem internet e sem chave, para validar o robô a cada mudança.
28. Como integrante, quero trocar o provedor de IA (Gemini → Groq) sem reescrever o robô, para ter plano B se a cota gratuita mudar.
29. Como integrante, quero que o Painel seja publicado de graça a partir do mesmo repositório, para o endereço existir sem domínio nem hospedagem paga.

## Implementation Decisions

**Forma geral.** Um único pacote Python (3.13, gerenciado com `uv`), com uma função de topo que executa **uma Coleta** completa: ler configuração → buscar Menções novas para cada Termo × idioma → deduplicar contra o histórico → enriquecer cada Menção nova com a IA → gravar → decidir e enviar Alerta de marca e/ou Digest → registrar envios. Essa função recebe suas dependências externas (fonte de notícias, IA, remetente de e-mail, data de hoje, caminho do banco) como parâmetros, para o mesmo código rodar no GitHub Actions, no PC de alguém e nos testes com dublês.

**Configuração.** Um arquivo TOML (lido com a biblioteca padrão) versionado no repositório contém: lista de Termos (cada um com idiomas em que é buscado e se é Termo de marca), Intervalo em dias, destinatários do Digest e do Alerta, nome do remetente, link do Painel, modelo de IA. Segredos (chave da IA, usuário e senha de app do SMTP) vêm só de variáveis de ambiente. Lista inicial de Termos vem da sticky do quadro (marca: `i9+`, `InoveMais`; setor: baterias de segunda vida / second-life batteries, economia circular / circular economy, baterias de lítio, eletromobilidade, painéis solares requalificados, energia renovável, armazenamento de energia; parceiros: Lactec, EMBRAPII, SENAI, TSEA Energia). Termos sem aspas na busca (frase exata + `when:` retorna zero no Google News).

**Fonte de notícias.** Google News RSS de busca (`/rss/search`), uma requisição por Termo × idioma, com `hl`/`gl`/`ceid` de pt-BR/Brasil e en-US/EUA, e janela `when:2d` (a Coleta é diária; a sobreposição de um dia cobre atrasos do índice). Parse com a biblioteca padrão de XML. Campos extraídos: título, link, fonte, data de publicação. Uma fonte que falhar (rede, XML inválido) é registrada no log e pulada.

**Dedupe.** A chave de uma Menção é o hash do link. O banco tem restrição de unicidade nessa chave; a mesma Menção encontrada por dois Termos é gravada uma vez e associada ao primeiro Termo que a achou. Nada é apagado, nunca.

**IA.** Chamada HTTP direta à API do Gemini (modelo configurável, padrão `gemini-2.5-flash-lite`, free tier, sem SDK), uma chamada por Menção nova, pedindo resposta em JSON com: resumo em português (2–3 frases), Relevância 0–10 para a i9+, tema (uma categoria curta), sentimento (positivo/neutro/negativo). Retentativa com espera em 429; ao esgotar, a Menção é gravada com resumo = título, Relevância vazia, tema "sem classificação" e marcada para reprocessamento na próxima Coleta. O provedor é uma interface de um método (texto → JSON), para Groq (API compatível com OpenAI) entrar como alternativa por configuração.

**Menção de marca.** Decidida por código, não pela IA: uma Menção é de marca se o título ou o resumo contém algum Termo de marca (comparação sem acento e sem caixa). Determinístico e testável sem IA.

**Histórico.** SQLite num arquivo no repositório. Tabela de Menções (chave, título, link, fonte, data de publicação, idioma, Termo, resumo, Relevância, tema, sentimento, é-marca, data da Coleta, precisa-reprocessar) e tabela de envios (tipo Digest/Alerta, data, quantas Menções, quais chaves). O workflow do Actions faz commit do arquivo ao fim da Coleta (ADR-0001).

**Alerta de marca.** Ao fim de uma Coleta, se houver Menções de marca novas que ainda não constam em nenhum envio do tipo Alerta, envia um e-mail listando todas elas e registra o envio. Rodar de novo no mesmo dia não reenvia.

**Digest.** Enviado quando não há Digest anterior ou quando a data de hoje menos a data do último Digest é maior ou igual ao Intervalo. Conteúdo: Menções gravadas desde o último Digest; Menções de marca primeiro; depois por Relevância decrescente (sem nota vai por último); as 20 primeiras no e-mail, com contagem das restantes e link do Painel. Cada item: título (link), fonte, data, resumo, Relevância, tema. Se não houver Menção nova no período, envia mesmo assim um Digest curto dizendo isso (o Parceiro sabe que o robô está vivo). Registra o envio com a data, que passa a ser a referência do próximo.

**E-mail.** SMTP do Gmail com senha de app, biblioteca padrão, mensagem multipart (texto simples + HTML simples, sem imagens). Remetente é a conta Gmail do projeto.

**Agendamento.** Workflow do GitHub Actions com `schedule` diário às 11:00 UTC (8h em Curitiba) e `workflow_dispatch` para disparo manual; permissão `contents: write`; passos: instalar `uv`, rodar a Coleta, commitar o banco se mudou. Segredos no repositório. O mesmo comando (`uv run radar`) roda no PC de qualquer pessoa com um `.env`.

**Painel.** App Streamlit no mesmo repositório, lendo o arquivo SQLite do próprio repositório (Streamlit Community Cloud faz redeploy a cada commit). Somente leitura. Mostra: cabeçalho de status (última Coleta, último Digest, próximo Digest = último + Intervalo, Intervalo, total de Menções), filtros (Termo, tema, idioma, período, só-marca), tabela/cards com título linkado, fonte, data, resumo, Relevância, tema, sentimento, Menções de marca destacadas, botão "Baixar CSV" com todo o histórico. Endereço `*.streamlit.app`, sem domínio.

**Logs.** Cada Coleta imprime um resumo de uma linha por etapa (Termos buscados, Menções novas, de marca, chamadas de IA ok/falhas, Alerta/Digest enviado ou não e por quê). É o que aparece no log do Actions.

**Idioma.** Busca em pt e en; toda saída para o Parceiro (resumo, tema, e-mails, Painel) em português.

## Testing Decisions

**O que é um bom teste aqui.** Testa o comportamento observável de uma Coleta inteira através da função de topo, com dublês para o mundo externo: uma fonte de notícias falsa que devolve XML de RSS gravado de respostas reais do Google News, uma IA falsa que devolve JSON determinístico (ou erro, quando o teste quer), um remetente de e-mail falso que apenas guarda o que seria enviado, uma data fixa e um banco SQLite temporário. Nenhum teste toca rede, chave ou relógio. Valores esperados vêm dos fixtures (títulos e links reais gravados), nunca recalculados pelo mesmo código.

**Costura 1 — uma Coleta (principal, quase única).** Todos os comportamentos do robô são testados por aqui:
- Menções novas do RSS aparecem no banco com os campos certos; a mesma Menção em dois Termos entra uma vez; rodar duas vezes não duplica.
- Menção de marca é detectada por Termo de marca no título/resumo, sem acento/caixa.
- Alerta de marca é enviado no dia em que há Menção de marca nova, com todas elas, e não é reenviado na segunda execução do mesmo dia.
- Digest é enviado quando nunca houve Digest; não é enviado antes de passar o Intervalo; é enviado no dia em que o Intervalo fecha; ordem = marca primeiro, depois Relevância; corte em 20 com contagem das restantes; Digest "vazio" quando não há Menção nova.
- IA falhando: Menção gravada com título como resumo, sem nota, marcada para reprocessar; próxima Coleta reprocessa.
- Fonte falhando: a Coleta termina, as outras fontes entram, o log registra.
- Config: Termos, idiomas, Intervalo e destinatários lidos do TOML são respeitados.

**Costura 2 — Painel (fumaça).** Um teste com o utilitário de teste do Streamlit que carrega o app apontando para um banco de fixture e verifica que o cabeçalho de status e a tabela renderizam e que o filtro "só-marca" reduz a lista. Não se testa layout.

**Sem teste automatizado (verificação manual, uma vez):** o adaptador real do Google News, o adaptador real do Gemini e o envio real por SMTP — um comando de "fumaça" que roda cada um contra o mundo real e imprime o resultado, usado na configuração inicial e na demonstração.

**Prior art.** Repositório novo; não há testes anteriores. Ferramenta: `pytest`, fixtures como arquivos XML/JSON gravados.

## Out of Scope

- Editar Termos ou Intervalo pelo Painel (v1 é só leitura; a equipe edita o arquivo).
- Espanhol e outros idiomas além de pt/en.
- Scraper de portais sem RSS, API própria (FastAPI), espelho em Google Sheets — cortados.
- Banco online (Supabase, Turso etc.) — plano B só se o commit do banco virar dor (ADR-0001).
- Alertas por WhatsApp/Telegram.
- Login/senha no Painel.
- Nome definitivo do projeto (provisório: Radar i9+).
- Tamanho final do e-mail (Q13 aberta; padrão 20 até o Parceiro opinar).

## Further Notes

- Fatos verificados sobre as cotas gratuitas em `docs/research/free-tiers-2026.md`: Gemini free tier existe sem cartão, mas os limites só aparecem logado no AI Studio (pendência do grupo: criar a conta Gmail do projeto e anotar RPM/RPD); GitHub Models foi aposentado (07/2026) — plano B de IA é Groq; Google News RSS é "uso pessoal, não comercial" (risco de ToS registrado); Streamlit Cloud hiberna após 12h sem acesso (plano B: GitHub Pages estático).
- O cron do Actions desativa após 60 dias sem atividade no repositório; o commit diário do banco já conta como atividade.
- Divisão do trabalho entre os 8 integrantes é assunto dos tickets, não desta spec.
