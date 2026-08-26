# Fontes além do Google News — o que dá pra cobrir (grátis ou pago)

Pesquisa feita em **26/08/2026** contra páginas oficiais (preços/docs). Preços são os exibidos na página na data; moeda conforme a página (BRL quando há página brasileira, senão USD). Itens marcados **[NÃO VERIFICADO]** não foram confirmados em fonte primária (página bloqueou ou não carregou).

Contexto: o robô de clipping da i9+/InoveMais hoje usa só Google News RSS. Abaixo, o que seria preciso para cobrir também redes sociais (LinkedIn/Instagram), blogs institucionais e editais/diários oficiais.

## Tabela-resumo

| Fonte/serviço | Cobre o quê | Grátis? | Preço mais barato (visto em 26/08/2026) | Cartão? | Esforço p/ integrar no robô | URL |
|---|---|---|---|---|---|---|
| Instagram Graph API — Mentions | Posts/comentários onde a conta @InoveMais é **marcada** (não busca por palavra) | Sim | US$ 0 | Não | API (conta profissional + app Meta + permissões) | https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/mentions/ |
| Instagram Graph API — Hashtag Search | Posts públicos com uma **#hashtag** exata (máx. 30 hashtags/7 dias) | Sim | US$ 0 | Não | API + App Review ("Instagram Public Content Access") | https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag-search |
| Instagram Graph API — Business Discovery | Posts públicos de **outras** contas profissionais por username (ex.: @senaipr, @tecpar) | Sim | US$ 0 | Não | API | https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/business-discovery |
| Meta Business Suite (Mentions & Tags / notificações) | Menções e marcações da conta própria (IG + FB) | Sim | R$ 0 | Não | Manual (painel/e-mail/push) | https://business.facebook.com |
| LinkedIn API (Posts / Community Management) | Só posts da **própria** página (r_organization_social); **não há busca por palavra-chave/menções** para terceiros | Sim (acesso restrito) | US$ 0 | Não | API — mas não resolve o caso de uso | https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api |
| Google Alerts (`site:linkedin.com "InoveMais"`, `"i9+"`, `filetype:pdf`) | Páginas indexadas pelo Google (inclui posts públicos do LinkedIn indexados, PDFs, blogs) | Sim | R$ 0 | Não | **RSS** (opção "Entregar para → Feed RSS") | https://www.google.com/alerts |
| Talkwalker Alerts | Notícias, blogs, fóruns, sites, X/Twitter | Sim | US$ 0 | Não | **RSS** ou e-mail | https://www.talkwalker.com/alerts |
| Bing News RSS | Notícias indexadas pelo Bing (`bing.com/news/search?q=...&format=rss`) | Sim | US$ 0 | Não | **RSS** (não documentado oficialmente; ~14 itens/feed) | https://www.bing.com/news/search?q=%22InoveMais%22&format=rss |
| Inoreader | Agregador RSS + "monitoring feeds" por palavra-chave + monitor de página web | Sim (plano Free) | US$ 0 / Pro US$ 7,50/mês anual (US$ 9,99 mensal) | Não no Free | RSS (o robô já consome RSS; Inoreader é opcional) | https://www.inoreader.com/pricing |
| Feedly | Agregador RSS; Pro+ tem "RSS Builder" p/ sites sem feed | Sim (Free) | Pro ~US$ 6–7/mês anual **[NÃO VERIFICADO — página oficial não carregou]** | Não no Free | RSS | https://feedly.com/pricing |
| Brand24 | Web, notícias, blogs, fóruns, **Instagram e LinkedIn** | Trial 14 dias | US$ 199/mês (anual) ou US$ 249/mês (mensal) — plano Individual, 3 keywords | Trial sem cartão | API/e-mail/exportação (manual→API) | https://brand24.com/prices/ |
| Mention | Web, notícias, blogs, fóruns, X, Reddit (IG/LinkedIn **não listados**) | Não (sem trial visível) | US$ 599/mês, contrato anual (único plano) | — | API | https://en.support.mention.com/en/articles/7988097-mention-plans-explained |
| Hootsuite (Listening by Talkwalker) | Instagram/LinkedIn no listening **só no Enterprise** (sob consulta); planos básicos escutam FB, X, Bluesky, YouTube, Quora | Trial 14 dias | US$ 99/usuário/mês (Standard, anual) — mas sem IG/LinkedIn listening | Trial sem cartão | Manual/API (Enterprise) | https://www.hootsuite.com/plans |
| Sprout Social | Publicação/inbox IG+LinkedIn; **Listening é add-on** (preço sob consulta) | Trial 30 dias | US$ 79/seat/mês anual (Essentials) + add-on Listening | Trial sem cartão | Manual/API | https://sproutsocial.com/pricing/ |
| Talkwalker (Hootsuite) — plataforma | Listening completo (IG, LinkedIn, notícias, blogs…) | Não | Sob consulta | — | API | https://www.talkwalker.com/pricing |
| Meltwater | Mídia + social listening | Não (demo) | Sob consulta | — | API | https://www.meltwater.com/en/pricing |
| Buzzmonitor (BR) | Social listening (IG, LinkedIn etc.), SAC, publicação | "Teste grátis" no site | **R$ 1.790,00/mês** ("planos a partir de") | Não informado | API/exportação | https://buzzmonitor.com/precos/ |
| Stilingue by Blip (BR) | Instagram, LinkedIn, FB, X, YouTube, blogs, portais | Não | Sob consulta | — | API/exportação | https://www.stilingue.com.br/ |
| Knewin (BR) | Clipping de imprensa + redes + podcasts | Não (demo) | Sob consulta | — | Plataforma/exportação | https://knewin.com/ |
| Querido Diário (OKBR) | Diários oficiais **municipais** (Curitiba coberta, id 4106902) | Sim (open source, CC-BY) | R$ 0 | Não | **API** REST sem auth (`/gazettes?querystring=&territory_ids=`) | https://api.queridodiario.ok.org.br/docs |
| Ro-DOU (Ministério da Gestão) | Clipping por palavra-chave do **DOU**, INLABS e Querido Diário, com alerta e-mail/Slack/Discord | Sim (GPL-3.0) | R$ 0 (custo = hospedar Airflow) | Não | Auto-hospedado (Docker) — pesado | https://github.com/gestaogovbr/Ro-dou |
| DOU — in.gov.br | Busca avançada (termos, datas, seções); sem RSS/alerta oficial | Sim | R$ 0 | Não | Scraping da busca / INLABS (manual) | https://www.in.gov.br/consulta/ |
| DIOE — Diário Oficial do Paraná | Busca por nome/empresa/protocolo; sem RSS/alerta | Sim | R$ 0 | Não | Manual | https://dioe.pr.gov.br/ |
| PNCP — Portal Nacional de Contratações Públicas | Editais/licitações de todo o país (API de consulta pública) | Sim | R$ 0 | Não | **API** (consulta sem autenticação, conforme manual — página do manual não carregou) | https://pncp.gov.br/api/consulta/swagger-ui/index.html |
| Portal da Transparência — API de Dados | Convênios, contratos, transferências federais | Sim | R$ 0 | Não | API (chave via cadastro gov.br) | https://portaldatransparencia.gov.br/api-de-dados |
| Alerta Licitação | Alertas de licitações por e-mail/WhatsApp (6.441 portais) | Navegação grátis; alertas pagos | **R$ 44,90/mês** (Individual; anual R$ 369,90) | Cartão, boleto ou PIX | E-mail (manual) | https://alertalicitacao.com.br/ |
| Effecti | Licitações (1.400+ portais), alertas, robô de lances | "Versão gratuita" | Sob consulta (WhatsApp) | — | Plataforma | https://effecti.com.br/plataforma/ |
| ConLicitação | Boletim diário de licitações | "Faça o teste" | Sob consulta (planos Super/Premium/Advanced/Black; 6/12/24 meses) | PIX, boleto ou cartão | E-mail | https://conlicitacao.com.br/planos/ |
| JusBrasil — Diários | Busca em diários oficiais (grátis p/ consultas pontuais); "Jusbrasil Acompanha" monitora Tribunais e Diários | Busca sim; monitoramento pago | Preço **[NÃO VERIFICADO — página /pro retornou 403]** | Cartão | Manual/e-mail | https://www.jusbrasil.com.br/diarios/ |
| Prosas — Central de Editais | Editais de fomento/impacto social | Sim (busca p/ proponentes) | R$ 0 | Não | Manual (sem RSS/newsletter visível) | https://prosas.com.br/ |
| Embrapii | Notícias e chamadas públicas | Sim | R$ 0 | Não | **RSS** válido (`/feed/`, 12 itens) | https://embrapii.org.br/feed/ |
| FINEP — Chamadas públicas | Chamadas abertas | Sim | R$ 0 | Não | Manual (sem RSS/newsletter na página) | http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta |
| Fundação Araucária — Programas Abertos | Chamadas do PR | Sim | R$ 0 | Não | Manual (sem RSS/newsletter na página) | https://www.fappr.pr.gov.br/Programas-Abertos |
| Tecpar / SENAI PR / Sebrae PR | Editais e notícias | Sim | R$ 0 | Não | Manual / Google Alerts `site:` (sem RSS encontrado; SENAI bloqueou fetch) | https://www.tecpar.br/ · https://sebraepr.com.br/licitacoes/ |

---

## A) Redes sociais — LinkedIn e Instagram

### Instagram (Meta) — API oficial

- **Só contas profissionais** (Business ou Creator): "Your app users must have an Instagram professional account." — https://developers.facebook.com/docs/instagram-platform/overview
- **Custo:** a API é gratuita; exige criar um app em developers.facebook.com. **App Review** só é obrigatório para *Advanced Access* (contas que você não administra) — https://developers.facebook.com/docs/instagram-platform/overview
- **Menções (@InoveMais):** endpoint de Mentions retorna captions, comentários e mídias em que a conta foi @mencionada; há webhook. Limitações: "Mentions on Stories are not supported"; sem webhook se o post de origem for de conta privada. Permissões: `instagram_business_basic` + `instagram_business_manage_comments` — https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/mentions/ e https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/mentioned_media
- **Busca por palavra-chave: NÃO existe.** Só busca por hashtag: "Instagram Public Content Access feature allows your app to access Instagram Graph API's Hashtag Search endpoints" — https://developers.facebook.com/docs/instagram-platform/overview. A Hashtag Search exige App Review e tem limite "30 unique hashtags within a 7 day period" — https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag-search
- **Business Discovery:** lê posts públicos de outras contas profissionais por username (útil para acompanhar @senaipr, @tecpar, @sebraepr e parceiros que possam citar a i9+) — https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/business-discovery
- **Grátis sem código:** Meta Business Suite mostra "Mentions & Tags" e envia notificações para a conta dona; é gratuito. Fonte primária da Meta não carregou (só título) — descrição do recurso conforme fontes secundárias **[NÃO VERIFICADO na página da Meta]**: https://www.facebook.com/business/help/547440452866017

### LinkedIn — API oficial

- **Não há API de busca de posts/menções para terceiros.** A Posts API (Community Management) só permite ler posts **do autor** (`q=author`) com `r_organization_social` (própria página, precisa ser ADMIN) ou `r_member_social` ("restricted and is available to approved users only") — https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- Acesso ao Community Management API exige aplicar ao Development Tier e depois Standard Tier com gravação de tela — https://learn.microsoft.com/en-us/linkedin/shared/linkedin-api-partner-support-guide
- Scraping é proibido pelo User Agreement, seção 8.2: "Develop, support or use software, devices, scripts, robots or any other means or processes (such as crawlers, browser plugins and add-ons or any other technology) to scrape or copy the Services" — https://www.linkedin.com/legal/user-agreement
- **Conclusão:** para LinkedIn, ou (a) Google Alerts `site:linkedin.com` (pega só posts públicos que o Google indexa — cobertura parcial), ou (b) ferramenta paga que tem acordo com o LinkedIn (Brand24, Talkwalker, Stilingue, Buzzmonitor declaram cobrir).

### Ferramentas pagas (preços oficiais)

| Ferramenta | Mais barato | IG | LinkedIn | Trial | Fonte |
|---|---|---|---|---|---|
| Brand24 | US$ 199/mês anual (US$ 249 mensal), 3 keywords | Sim | Sim | 14 dias, "No credit card required" | https://brand24.com/prices/ |
| Mention | US$ 599/mês, anual (Solo/Pro/Pro Plus descontinuados jul/2025) | não listado | não listado | não informado | https://en.support.mention.com/en/articles/7988097-mention-plans-explained |
| Hootsuite | US$ 99/usuário/mês anual (Standard); IG/LinkedIn no Listening **só Enterprise** | Enterprise | Enterprise | 14 dias sem cartão | https://www.hootsuite.com/plans · https://www.hootsuite.com/platform/listening |
| Sprout Social | US$ 79/seat/mês anual (Essentials); Listening = add-on sob consulta | Sim (add-on) | Sim (add-on) | 30 dias sem cartão | https://sproutsocial.com/pricing/ |
| Talkwalker | Sob consulta (Core/Analyze/Business) | Sim | Sim | Demo | https://www.talkwalker.com/pricing |
| Meltwater | Sob consulta ("tailored pricing") | Sim | Sim | Demo | https://www.meltwater.com/en/pricing |
| Buzzmonitor (BR) | **R$ 1.790,00/mês** | Sim | Sim | "Teste Grátis" | https://buzzmonitor.com/precos/ |
| Stilingue by Blip (BR) | Sob consulta | Sim | Sim | não | https://www.stilingue.com.br/ |
| Knewin (BR) | Sob consulta | Sim | (redes, não detalha) | Demo | https://knewin.com/ |

### Contornos gratuitos

1. **Google Alerts** com `"InoveMais" site:linkedin.com`, `"i9+" site:linkedin.com`, `"InoveMais" site:instagram.com`. Fontes: "Automatic/News/Blogs/Web…", frequência "As-it-happens / once a day / once a week", resultados "All results" — https://www.google.com/alerts. Entrega em **RSS** ("Deliver to → RSS feed"): documentada por terceiros, não na ajuda oficial (https://support.google.com/websearch/answer/4815696) — https://www.howtogeek.com/444549/how-to-create-an-rss-feed-from-a-google-alert/
2. **Meta Business Suite** — menções e marcações da própria conta, grátis (ver acima).
3. **Instagram Graph API — Mentions + Business Discovery** — grátis, precisa de conta Business e app Meta (padrão de acesso *Standard* para conta própria, sem App Review).
4. Hashtag Search (`#economiacircular`, `#segundavida`, `#InoveMais`) — grátis, mas exige App Review.

---

## B) Blogs institucionais / páginas web

- **Google Alerts** (grátis, RSS): um alerta por termo. Termos sugeridos: `"InoveMais"`, `"i9+" Curitiba`, `"segunda vida" baterias`, `"economia circular" Paraná`, `site:senaipr.org.br`, `site:tecpar.br`, `site:sebraepr.com.br`. — https://www.google.com/alerts
- **Talkwalker Alerts** (grátis): "You can receive Alerts via email, RSS, or through a Slack integration"; cobre "news platforms, blogs, forums, websites, and even Twitter (X)" — https://www.talkwalker.com/alerts
- **Bing News RSS** (grátis): `https://www.bing.com/news/search?q=%22InoveMais%22&format=rss` retorna RSS válido (testado; 0 itens hoje). Limite ~14 itens; recurso não documentado oficialmente — https://learn.microsoft.com/en-us/answers/questions/2343925/bing-news-search-exploratory-rss-view
- **RSS dos próprios sites:** Embrapii tem feed válido (https://embrapii.org.br/feed/). Tecpar (`/rss.xml` devolve HTML), FINEP e Fundação Araucária não expõem RSS/newsletter nas páginas de chamadas; SENAI PR bloqueou o fetch (403). Para esses, usar Google Alerts `site:` ou o "monitor de página" do Inoreader.
- **Inoreader** — Free: 150 feeds RSS, 20 web feeds, 30 monitoring feeds (busca por palavra), "No credit card required"; Pro US$ 7,50/mês anual ou US$ 9,99 mensal — https://www.inoreader.com/pricing
- **Feedly** — Free/Pro/Pro+/Enterprise; Pro+ inclui "RSS Builder" para sites sem feed (https://docs.feedly.com/article/140-what-is-the-difference-between-feedly-basic-pro-and-teams). Preços: página oficial não carregou; terceiros citam Pro US$ 6–7/mês anual e Pro+ US$ 8,25/mês anual **[NÃO VERIFICADO]** — https://feedly.com/pricing

---

## C) Editais, PDFs, Diário Oficial

- **Querido Diário (Open Knowledge Brasil)** — só diários **municipais** do Executivo ("diários oficiais do poder executivo municipal brasileiro"; não cobre DOU nem DIOE-PR). Código MIT, dados CC-BY. **Curitiba coberta** (territory_id 4106902, fonte legisladocexterno.curitiba.pr.gov.br, desde 09/05/2022). API REST **sem autenticação**: `GET https://api.queridodiario.ok.org.br/gazettes?territory_ids=4106902&querystring="economia circular"` → 43 diários, com `excerpts`, `url`, `txt_url`. — https://docs.queridodiario.ok.org.br/ · https://api.queridodiario.ok.org.br/docs
- **Ro-DOU** (Secretaria de Gestão e Inovação / Ministério da Gestão) — clipping por palavra-chave do **DOU + INLABS + Querido Diário**, notificações por e-mail/Slack/Discord, GPL-3.0, roda em Apache Airflow (Docker). Grátis, mas exige hospedar Airflow — pesado para o robô atual. — https://github.com/gestaogovbr/Ro-dou · https://gestaogovbr.github.io/Ro-dou/
- **DOU (in.gov.br)** — serviço gratuito ("Este serviço é gratuito para o cidadão"), busca avançada por termos/datas/seções; **sem RSS ou alerta oficial** — https://www.gov.br/pt-br/servicos/acessar-o-diario-oficial-da-uniao · https://www.in.gov.br/consulta/
- **DIOE — Diário Oficial do Paraná** — busca por nome de pessoa/empresa/protocolo; nova plataforma (IONews) desde 13/07/2026; sem RSS/alerta — https://www.parana.pr.gov.br/servicos/Documentos/Documentos-oficiais/Consultar-o-Diario-Oficial-do-Estado-DIOE-Epol8QoB
- **PNCP** — API de consulta pública de contratações/editais (Swagger em https://pncp.gov.br/api/consulta/swagger-ui/index.html). Manual diz que consulta é pública e só manutenção exige auth (https://pncp.gov.br/manual/pt-br/latest/singlehtml/ — página não carregou no teste; afirmação via snippet do manual).
- **Portal da Transparência — API de Dados** — grátis, exige chave obtida com conta gov.br (nível Prata/Ouro); datasets de convênios, contratos etc. — https://portaldatransparencia.gov.br/api-de-dados
- **Google Alerts `filetype:pdf`** — ex.: `"InoveMais" filetype:pdf`, `"segunda vida" baterias edital filetype:pdf` — grátis, RSS.
- **Newsletters/páginas de fomento** (grátis): FINEP chamadas abertas (http://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta), Embrapii (RSS https://embrapii.org.br/feed/), Fundação Araucária (https://www.fappr.pr.gov.br/Programas-Abertos), Sebrae PR licitações (https://sebraepr.com.br/licitacoes/), Prosas Central de Editais (https://prosas.com.br/). Nenhuma dessas páginas expõe newsletter/RSS além da Embrapii.
- **Serviços pagos de licitação/editais:**
  - Alerta Licitação — **R$ 44,90/mês** (Individual: 2 e-mails/dia, filtros por estado/modalidade/itens, Excel); Corporativo R$ 54,90/mês; cartão, boleto ou PIX — https://alertalicitacao.com.br/
  - Effecti — planos Iniciante/Profissional/Grandes Contas/Consultores, preço via WhatsApp; "experimente a versão gratuita" — https://effecti.com.br/plataforma/
  - ConLicitação — Super/Premium/Advanced/Black, 6/12/24 meses, PIX/boleto/cartão, preço não exibido — https://conlicitacao.com.br/planos/
  - JusBrasil — busca em diários grátis; "Jusbrasil Acompanha" inclui "Monitoramento diário em sites de Tribunais e Diários Oficiais" (https://suporte.jusbrasil.com.br/hc/pt-br/articles/19759490506516); preço **[NÃO VERIFICADO — /pro retornou 403]**. É voltado a processos judiciais, não a editais.

---

## Recomendação de custo zero

Tudo abaixo entra no robô como **mais um feed RSS ou uma chamada HTTP**, sem mudar a arquitetura:

1. **Google Alerts → RSS** (um alerta por termo; "All results", "As-it-happens"): `"InoveMais"`, `"i9+" Curitiba`, `"InoveMais" site:linkedin.com`, `"InoveMais" site:instagram.com`, `"InoveMais" filetype:pdf`, `site:senaipr.org.br "InoveMais"`, `site:tecpar.br`, `"segunda vida" baterias`, `"economia circular" Curitiba`.
2. **Talkwalker Alerts → RSS** com os mesmos termos (cobre fóruns e X).
3. **Bing News RSS** com os mesmos termos.
4. **Querido Diário API** (`territory_ids=4106902`, querystring por termo, `published_since` = última execução) — cobre o Diário Oficial de Curitiba.
5. **PNCP API** filtrando por UF=PR / município Curitiba e palavra-chave (baterias, resíduos, energia).
6. **Embrapii RSS** + páginas FINEP/Fundação Araucária/Sebrae via Google Alerts `site:`.
7. **Instagram (dono da conta):** ativar notificações de Mentions & Tags no Meta Business Suite (zero código). Se quiser no robô: app Meta + Mentions API (grátis) para menções à conta; Business Discovery para acompanhar @senaipr/@tecpar/@sebraepr.
8. **LinkedIn:** só o item 1 (`site:linkedin.com`) — cobertura parcial, sem alternativa oficial gratuita.

## Se houver orçamento

Caminho mais barato que cobre **LinkedIn + Instagram** de forma legítima (via acordos com as plataformas):

- **Brand24 Individual — US$ 199/mês (anual) ou US$ 249/mês (mensal)**, 3 keywords, IG e LinkedIn inclusos, trial 14 dias sem cartão, "30-day money-back guarantee" — https://brand24.com/prices/. Integração: e-mail/relatórios ou API. 3 keywords bastam ("InoveMais", "i9+", "i9 Mais").
- Alternativa nacional em BRL: **Buzzmonitor a partir de R$ 1.790/mês** (https://buzzmonitor.com/precos/) — muito acima do necessário para uma empresa pequena.
- Sprout (US$ 79 + add-on Listening sob consulta) e Hootsuite (IG/LinkedIn listening só Enterprise) saem mais caros ou não têm preço público. Mention (US$ 599/mês anual) não lista IG/LinkedIn.
- Para editais públicos: **Alerta Licitação R$ 44,90/mês** só se PNCP/Querido Diário (grátis) não bastarem.

## Riscos/limites

- **LinkedIn não tem API de busca/menções para terceiros**; scraping viola o User Agreement (seção 8.2 "Don'ts") — https://www.linkedin.com/legal/user-agreement. Cobertura via Google Alerts depende do que o Google indexa (posts públicos, não todos).
- **Instagram:** API só para contas profissionais; sem busca por palavra-chave (só hashtag, com App Review e 30 hashtags/7 dias); Stories não entram nas menções. Scraping de páginas públicas viola os Termos de Uso do Instagram **[NÃO VERIFICADO — página dos termos não carregou; cláusula "collect information in unauthorized or automated ways" citada de memória]**.
- **Google Alerts / Bing RSS / Talkwalker Alerts** não têm SLA nem documentação oficial de RSS (Google Alerts RSS existe mas não está na ajuda oficial; Bing `format=rss` é "exploratory", ~14 itens). Podem sumir sem aviso.
- **Querido Diário** cobre só diários **municipais**; DOU e DIOE-PR ficam fora (Ro-DOU cobre DOU, mas exige Airflow).
- **Preços em USD** (Brand24, Inoreader etc.) variam com câmbio e IOF; planos "anual" exigem pagamento adiantado.
- **Ferramentas "sob consulta"** (Stilingue, Knewin, Meltwater, Talkwalker, Effecti, ConLicitação) tendem a contratos anuais com valores enterprise; não há preço público para comparar.
