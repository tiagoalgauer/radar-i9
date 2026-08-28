# Radar i9+ (nome provisório)

Robô que vigia notícias do mundo sobre a i9+ e o setor dela (baterias de segunda vida, economia circular, energia) e entrega o resultado ao Parceiro sem ninguém precisar apertar botão.

## Language

**Parceiro**:
A i9+ / InoveMais, representada pelo Sandro. Quem recebe o Radar.
_Avoid_: cliente, empresa

**Termo**:
Uma palavra ou expressão que o robô pesquisa (ex.: "baterias de segunda vida"). A lista de Termos é do Parceiro.
_Avoid_: keyword, palavra-chave, query

**Notícia**:
O item bruto que uma Fonte devolve (título, link, veículo, data), antes de entrar no histórico.
_Avoid_: item, entrada, resultado

**Fonte**:
De onde as Notícias vêm: Google News RSS e Bing News RSS (busca por Termo × idioma) e feeds fixos (RSS/Atom, inclusive Google Alerts).
_Avoid_: feed, provedor de notícias

**Menção**:
Uma Notícia que entrou no histórico para um Termo. Nunca é descartada.
_Avoid_: artigo, item, resultado

**Tema**:
Categoria curta em português que a IA dá a uma Menção (ex.: "baterias", "regulação").
_Avoid_: categoria, tag

**Sentimento**:
Positivo, neutro ou negativo para a i9+, dado pela IA a uma Menção.
_Avoid_: tom, polaridade

**Envio**:
Registro de um e-mail que saiu (Alerta ou Digest) com as Menções que ele levou. É o que impede reenvio.
_Avoid_: log de e-mail, histórico de envio

**Menção de marca**:
Menção que cita a i9+/InoveMais diretamente. Dispara um Alerta de marca e vai no topo do Digest.
_Avoid_: citação

**Alerta de marca**:
E-mail enviado no mesmo dia em que uma Menção de marca é encontrada, sem esperar o Digest.
_Avoid_: notificação, aviso

**Relevância**:
Nota de 0 a 10 dada pela IA a uma Menção, usada só para ordenar. Nunca corta.
_Avoid_: score, filtro

**Coleta**:
Uma rodada do robô buscando Menções novas para todos os Termos.
_Avoid_: scraping, crawl, run

**Digest**:
O e-mail periódico com as Menções novas desde o último Digest, ordenadas por Relevância.
_Avoid_: clipping, relatório, newsletter

**Intervalo**:
Quantos dias entre um Digest e o próximo. Quem escolhe é o Parceiro.
_Avoid_: cadência, cron, frequência

**Painel**:
A página web onde o Parceiro vê todas as Menções, com filtros.
_Avoid_: dashboard, site, app
