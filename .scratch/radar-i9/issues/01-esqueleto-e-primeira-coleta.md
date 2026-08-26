# 01: Esqueleto do projeto + primeira Coleta com dedupe

**What to build:** Rodar `uv run radar` com uma fonte de notícias falsa (XML de RSS gravado) grava as Menções no histórico SQLite com todos os campos (chave = hash do link, título, link, fonte, data, idioma, Termo, coletada_em; campos da IA vazios por enquanto). Rodar de novo não duplica nada. A mesma Menção achada por dois Termos entra uma vez. O log imprime uma linha por etapa (Termos lidos, Menções novas, ignoradas). A função de topo recebe fonte, IA, remetente, data e caminho do banco como parâmetros — é a costura 1 dos testes.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Projeto Python 3.13 gerenciado com `uv`, `pytest` rodando, `config.toml` com Termos (com idiomas e flag de marca), Intervalo, destinatários, link do Painel, modelo de IA
- [ ] Segredos só por variável de ambiente; nenhum segredo no repo
- [ ] Histórico SQLite com tabela de Menções (unicidade pela chave) e tabela de envios (vazia por enquanto)
- [ ] Teste: RSS gravado com N itens → N Menções no banco com os campos certos
- [ ] Teste: rodar duas vezes → mesmo número de Menções
- [ ] Teste: mesma notícia em dois Termos → uma Menção, associada ao primeiro Termo
- [ ] Log legível de uma linha por etapa
- [ ] Nenhum teste toca rede, chave ou relógio
