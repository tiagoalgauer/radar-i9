# 05: Digest a cada N dias (Intervalo do Parceiro)

**What to build:** Ao fim da Coleta o robô decide se manda o Digest: manda quando nunca houve Digest, ou quando hoje − data do último Digest ≥ Intervalo do config. O Digest traz as Menções gravadas desde o último Digest: Menções de marca primeiro, depois por Relevância decrescente (sem nota por último); as 20 primeiras no e-mail, com a contagem das restantes e o link do Painel; cada item com título linkado, fonte, data, resumo, Relevância e tema. Sem novidade no período, sai um Digest curto dizendo isso. O envio é registrado e passa a ser a referência do próximo.

**Blocked by:** 03 (IA — resumo, Relevância, tema e sentimento), 04 (Menção de marca + Alerta de marca por e-mail)

**Status:** feita

- [ ] Teste: nunca houve Digest → envia
- [ ] Teste: último Digest há Intervalo−1 dias → não envia; há Intervalo dias → envia
- [ ] Teste: ordem = marca primeiro, depois Relevância decrescente, sem nota por último
- [ ] Teste: 25 Menções → e-mail com 20 + "mais 5 no Painel" + link
- [ ] Teste: nenhuma Menção nova no período → Digest "vazio" enviado
- [ ] Teste: rodar duas vezes no dia do Digest → um envio só
- [ ] Menção de marca que já gerou Alerta continua no topo do Digest
