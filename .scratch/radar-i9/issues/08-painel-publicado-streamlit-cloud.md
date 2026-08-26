# 08: Painel publicado no Streamlit Community Cloud + link no Digest

**What to build:** O Painel vai ao ar em um endereço gratuito `*.streamlit.app` a partir do repositório público, lendo o `radar.db` commitado pelo robô (redeploy a cada commit). O link do Painel entra no `config.toml` e aparece no Digest e no Alerta. O README explica como foi publicado (login com GitHub, sem domínio, sem cartão) e que o app hiberna após 12h sem acesso.

**Blocked by:** 06 (Robô na nuvem — GitHub Actions diário + commit do histórico), 07 (Painel v1 — Streamlit lendo o histórico)

**Status:** ready-for-agent

- [ ] Painel acessível por URL pública, sem senha, mostrando Menções reais
- [ ] Depois de um run do robô, o Painel reflete as Menções novas sem intervenção
- [ ] Link do Painel presente no Digest e no Alerta
- [ ] README com o passo a passo da publicação; print como evidência
