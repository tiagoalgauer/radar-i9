# Radar i9+ (nome provisório)

Robô que vigia notícias do mundo sobre a i9+ e o setor dela (baterias de segunda vida, economia circular, energia) e entrega o resultado ao Parceiro sem ninguém precisar apertar botão.

## Language

**Parceiro**:
A i9+ / InoveMais, representada pelo Sandro. Quem recebe o Radar.
_Avoid_: cliente, empresa

**Termo**:
Uma palavra ou expressão que o robô pesquisa (ex.: "baterias de segunda vida"). A lista de Termos é do Parceiro.
_Avoid_: keyword, palavra-chave, query

**Menção**:
Uma notícia encontrada para um Termo. Nunca é descartada: toda Menção fica no histórico.
_Avoid_: notícia, artigo, item, resultado

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
