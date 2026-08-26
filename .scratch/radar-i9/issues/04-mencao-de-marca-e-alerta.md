# 04: Menção de marca + Alerta de marca por e-mail

**What to build:** Uma Menção é de marca quando o título ou o resumo contém um Termo de marca (comparação sem acento e sem caixa) — decidido por código, não pela IA. Ao fim da Coleta, se houver Menções de marca novas que ainda não constam em nenhum envio do tipo Alerta, o robô manda um e-mail (texto + HTML simples) listando todas, com título linkado, fonte, data e resumo, e registra o envio. Rodar de novo no mesmo dia não reenvia. Os testes usam um remetente falso que só guarda o que seria enviado; o adaptador real usa SMTP do Gmail com senha de app. Um comando de fumaça manda um e-mail de teste.

**Blocked by:** 01 (Esqueleto do projeto + primeira Coleta com dedupe)

**Status:** ready-for-agent

- [ ] Teste: "InoveMais" no título → Menção marcada; "inovemais" e "i9+" também; Termo de setor não marca
- [ ] Teste: Coleta com 2 Menções de marca novas → 1 e-mail com as 2; envio registrado
- [ ] Teste: segunda Coleta no mesmo dia sem marca nova → nenhum e-mail
- [ ] Teste: Coleta sem Menção de marca → nenhum e-mail
- [ ] Destinatários do Alerta vêm do config; remetente e senha só por variável de ambiente
- [ ] Fumaça enviou um e-mail real para a conta do projeto; print como evidência
