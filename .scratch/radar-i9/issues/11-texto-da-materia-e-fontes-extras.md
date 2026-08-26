# 11: Texto da matéria + Fontes extras (Bing News, Google Alerts, RSS de sites)

**What to build:** Hoje o robô só enxerga **título + veículo** de cada Notícia (o Google News RSS não entrega o corpo). Consequência vista em 26/08: as duas matérias reais sobre a i9+ (Feira de Inovação na Rua XV, ABSOLAR Meeting) citam a empresa só no corpo do texto → nenhuma virou Menção de marca, e a IA resume sem saber do que a matéria fala de verdade. Este ticket dá ao robô um **trecho do texto** de cada Notícia e soma índices além do Google News: (a) Bing News RSS (traz snippet do corpo, sem chave); (b) Google Alerts em modo RSS (índice diferente, pega blogs/páginas — precisa da conta Gmail do projeto); (c) RSS direto dos sites que o Parceiro indicar (Tecpar, AEN Paraná, Agência Curitiba, Canal Solar, ANEEL…). O trecho entra na detecção de marca (título + trecho + resumo) e no prompt da IA. Cada Fonte é um adaptador com a mesma interface `buscar(termo, idioma)`; a Coleta percorre todas.

**Blocked by:** 02 (Fonte real — Google News RSS). Lista de sites depende da reunião com o Sandro ("quais fontes importam?").

**Status:** feita (falta só o Sandro indicar sites/alertas para os [[feeds]])

- [x] Notícia ganha campo `trecho` (opcional); Google News deixa vazio, Bing preenche com o snippet
- [x] Menção de marca considera título + trecho + resumo
- [x] Prompt da IA recebe o trecho quando existir
- [x] Fonte Bing News RSS (`bing.com/news/search?format=rss`) com teste em XML gravado
- [x] Fonte Google Alerts RSS (URL do alerta no config) com teste em XML gravado
- [x] Fonte RSS genérica por URL (lista `[[fontes_rss]]` no config) com teste em XML gravado
- [x] Mesma Notícia vinda de duas Fontes entra uma vez (dedupe pelo link final, não pelo redirecionador)
- [ ] Coleta de estreia refeita nos Termos de marca: as matérias de 2025 sobre a i9+ aparecem com 🔔 no Painel
- [x] Limite documentado: LinkedIn/Instagram não têm API gratuita — ficam fora (dizer isso ao Parceiro)
