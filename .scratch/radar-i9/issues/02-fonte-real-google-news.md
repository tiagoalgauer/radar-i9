# 02: Fonte real — Google News RSS em pt e en

**What to build:** O adaptador real monta, para cada Termo × idioma configurado, a busca do Google News RSS (pt-BR/Brasil e en-US/EUA) com janela `when:2d` e Termo sem aspas, e devolve as Menções no mesmo formato que a fonte falsa. Um Termo ou feed que falhar (rede, XML inválido) é registrado no log e pulado, sem derrubar a Coleta. Um comando de fumaça roda o adaptador contra a internet e imprime o que achou, para a configuração inicial e a demonstração.

**Blocked by:** 01 (Esqueleto do projeto + primeira Coleta com dedupe)

**Status:** feita

- [ ] Teste (com fonte falsa que lança erro em um Termo): a Coleta termina, os outros Termos entram, o log registra a falha
- [ ] Teste: os campos título, link, fonte, data e idioma vêm preenchidos a partir de um XML real gravado do Google News
- [ ] Parse com a biblioteca padrão de XML (sem feedparser)
- [ ] Comando de fumaça documentado no README; rodado uma vez de verdade, com o resultado colado como evidência
- [ ] Termos iniciais da sticky do quadro já no `config.toml`
