"""E-mails do Radar: montagem do Alerta de marca e do Digest, e envio por SMTP do Gmail."""

# ponytail: texto e HTML montados à mão; um template engine só quando o Parceiro pedir layout

import html
import smtplib
from email.message import EmailMessage

TOP_DIGEST = 20  # ponytail: Q13 aberta com o Parceiro; nada some do histórico, só do e-mail


def _item_texto(m):
    nota = f" · relevância {m.relevancia}/10" if m.relevancia is not None else ""
    tema = f" · {m.tema}" if m.tema else ""
    return f"• {m.titulo}\n  {m.fonte} · {m.data}{nota}{tema}\n  {m.resumo or ''}\n  {m.link}\n"


def _item_html(m):
    nota = f" · relevância {m.relevancia}/10" if m.relevancia is not None else ""
    tema = f" · {html.escape(m.tema)}" if m.tema else ""
    marca = " 🔔" if m.marca else ""
    return (
        f'<p><b><a href="{html.escape(m.link)}">{html.escape(m.titulo)}</a>{marca}</b><br>'
        f"<small>{html.escape(m.fonte or '')} · {m.data}{nota}{tema}</small><br>"
        f"{html.escape(m.resumo or '')}</p>"
    )


def montar_alerta(mencoes, nome="Radar i9+"):
    n = len(mencoes)
    assunto = f"🔔 {nome} — Alerta de marca: {n} {'menções' if n != 1 else 'menção'} à i9+/InoveMais hoje"
    texto = f"A i9+/InoveMais foi citada em {n} notícia(s) encontrada(s) hoje:\n\n" + "\n".join(_item_texto(m) for m in mencoes)
    corpo = "".join(_item_html(m) for m in mencoes)
    html_ = f"<h2>{html.escape(nome)} — Alerta de marca</h2><p>A i9+/InoveMais foi citada em {n} notícia(s) encontrada(s) hoje:</p>{corpo}"
    return assunto, texto, html_


def montar_digest(mencoes, link_painel, intervalo_dias, nome="Radar i9+", primeiro=False):
    total = len(mencoes)
    top = mencoes[:TOP_DIGEST]
    restantes = total - len(top)
    n_marca = sum(1 for m in mencoes if m.marca)
    periodo = "desde o início" if primeiro else "desde o último Digest"
    assunto = f"📰 {nome} — Digest: {total} menções {periodo}" + (f" ({n_marca} da marca)" if n_marca else "")
    if total == 0:
        texto = f"Nenhuma menção nova {periodo}. O robô continua vigiando (próximo Digest em {intervalo_dias} dias).\nPainel: {link_painel}\n"
        html_ = f"<h2>{html.escape(nome)} — Digest</h2><p>Nenhuma menção nova {periodo}. O robô continua vigiando (próximo Digest em {intervalo_dias} dias).</p><p><a href=\"{html.escape(link_painel)}\">Abrir o Painel</a></p>"
        return assunto, texto, html_
    rodape = f"\n… e mais {restantes} no Painel: {link_painel}\n" if restantes else f"\nPainel completo: {link_painel}\n"
    texto = f"{total} menções {periodo} (menções à marca primeiro, depois por relevância):\n\n" + "\n".join(_item_texto(m) for m in top) + rodape
    rodape_html = (f'<p>… e mais <b>{restantes}</b> no <a href="{html.escape(link_painel)}">Painel</a>.</p>' if restantes
                   else f'<p><a href="{html.escape(link_painel)}">Abrir o Painel completo</a></p>')
    html_ = f"<h2>{html.escape(nome)} — Digest</h2><p>{total} menções {periodo} (marca primeiro, depois por relevância):</p>" + "".join(_item_html(m) for m in top) + rodape_html
    return assunto, texto, html_


class RemetenteGmail:
    def __init__(self, usuario: str, senha_de_app: str, nome="Radar i9+"):
        self.usuario, self.senha, self.nome = usuario, senha_de_app, nome

    def enviar(self, destinatarios, assunto, texto, html_):
        msg = EmailMessage()
        msg["From"] = f"{self.nome} <{self.usuario}>"
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = assunto
        msg.set_content(texto)
        msg.add_alternative(html_, subtype="html")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as s:
            s.login(self.usuario, self.senha)
            s.send_message(msg)


class RemetenteSimulado:
    """Fora do GitHub Actions (ou sem credenciais) só imprime — ninguém recebe e-mail por acidente."""

    simulado = True  # a Coleta não registra o envio: o Digest/Alerta sai de verdade quando houver credenciais

    def __init__(self, log=print):
        self.log = log

    def enviar(self, destinatarios, assunto, texto, html_):
        self.log(f"[simulado] e-mail para {', '.join(destinatarios)}: {assunto}")
        self.log(texto)
