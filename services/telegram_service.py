# services/telegram_service.py
import logging
import re
import requests
import io
from typing import Optional

# Importações do projeto
from utils.data_models import Pedido
from utils.cantadas import CANTADAS_DATA

# Configuração do logger
logger = logging.getLogger(__name__)

def escape_markdown_v2(text: str) -> str:
    """
    Escapa caracteres reservados do MarkdownV2 para o Telegram.
    Caracteres escapados: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if not text:
        return ""
    # Regex para escapar todos os caracteres reservados do MarkdownV2
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', str(text))


class TelegramService:
    """
    Serviço que encapsula as chamadas à API do Telegram para enviar notificações.
    """
    SEND_MESSAGE_URL = "https://api.telegram.org/bot{token}/sendMessage"
    SEND_PHOTO_URL = "https://api.telegram.org/bot{token}/sendPhoto"

    def __init__(self, token: str, chat_id: str):
        """
        Inicializa o serviço com o token do bot e o ID do chat de destino.
        """
        if not token or not chat_id:
            logger.warning("Token do Telegram ou Chat ID não foram fornecidos.")
        self.token = token
        self.chat_id = chat_id

    def _format_message(self, pedido: Pedido) -> str:
        """
        Formata a mensagem de notificação de acordo com o tipo de pedido.
        Todos os dados variáveis são escapados para segurança com MarkdownV2.
        """
        valor_formatado = f'{pedido.valor_total:.2f}'.replace('.', ',')
        remetente = escape_markdown_v2(pedido.remetente_nome)
        contato = escape_markdown_v2(pedido.remetente_contato or '—')
        destinatario = escape_markdown_v2(pedido.destinatario)
        equipe = escape_markdown_v2(pedido.equipe_destinatario)

        if pedido.tipo == "Carta":
            itens = escape_markdown_v2(', '.join(pedido.itens) if pedido.itens else '—')
            mensagem = escape_markdown_v2(pedido.mensagem_texto or '—')
            
            return (
                f"📩 *NOVA CARTA*\n\n"
                f"*De:* {remetente} `({contato})`\n"
                f"*Para:* {destinatario}\n"
                f"*Equipe:* {equipe}\n\n"
                f"*Itens:* {itens}\n"
                f"*Mensagem:*\n`{mensagem}`\n\n"
                f"*Valor Total:* R$ {escape_markdown_v2(valor_formatado)}"
            )

        elif pedido.tipo == "Cantada":
            # Busca o texto da cantada no dicionário, usando o ID como fallback
            cantada_texto = CANTADAS_DATA.get(str(pedido.cantada_id), "Cantada não encontrada")

            combo = escape_markdown_v2(pedido.combo_selecionado or '—')
            cantada_fmt = escape_markdown_v2(cantada_texto)
            parodia = escape_markdown_v2(pedido.parodia_id or '—')
            cartinha = escape_markdown_v2(pedido.mensagem_texto or '—')
            
            mensagem_partes = [
                f"💘 *NOVA CANTADA*\n\n",
                f"*De:* {remetente} `({contato})`\n",
                f"*Para:* {destinatario}\n",
                f"*Equipe:* {equipe}\n\n",
                f"🎁 *Combo:* {combo}\n",
                f"🎶 *Paródia:* {parodia}\n",
                f"💬 *Cantada:* `{cantada_fmt}`\n"
            ]
            if pedido.mensagem_texto: # Só adiciona a linha da cartinha se ela existir
                mensagem_partes.append(f"📝 *Cartinha:* `{cartinha}`\n")

            mensagem_partes.extend([
                f"\n*Valor Total:* R$ {escape_markdown_v2(valor_formatado)}"
            ])
            return "".join(mensagem_partes)
            
        return "Tipo de pedido desconhecido."

    def enviar_notificacao_pedido(self, pedido: Pedido, comprovante_bytes: Optional[bytes] = None) -> dict:
        """
        Envia a notificação para o Telegram.
        - Se houver comprovante, envia como foto com o texto na legenda.
        - Se não houver, envia apenas a mensagem de texto.
        Retorna um dicionário com o status do envio.
        """
        if not self.token or not self.chat_id:
            logger.error("Tentativa de enviar notificação sem Token ou Chat ID configurado.")
            return {"success": False, "error": "Configuração do Telegram incompleta."}

        text_message = self._format_message(pedido)
        result = {"success": False, "file_id": None}

        try:
            if comprovante_bytes:
                # Envia a foto com o texto como legenda (caption)
                url = self.SEND_PHOTO_URL.format(token=self.token)
                files = {'photo': ('comprovante.jpg', io.BytesIO(comprovante_bytes))}
                payload = {
                    'chat_id': self.chat_id,
                    'caption': text_message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(url, data=payload, files=files, timeout=20)
                response.raise_for_status()
                # Extrai o file_id da foto de melhor qualidade
                file_id = response.json().get("result", {}).get("photo", [{}])[-1].get("file_id")
                result["file_id"] = file_id
            else:
                # Envia apenas a mensagem de texto
                url = self.SEND_MESSAGE_URL.format(token=self.token)
                payload = {
                    'chat_id': self.chat_id,
                    'text': text_message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()

            logger.info(f"Notificação de pedido {pedido.id} enviada com sucesso para o Telegram.")
            result["success"] = True

        except requests.exceptions.RequestException as e:
            logger.exception(f"Erro de rede ao enviar notificação para o Telegram: {e}")
            result["error"] = str(e)
        except Exception as e:
            logger.exception(f"Erro inesperado ao enviar notificação para o Telegram: {e}")
            result["error"] = str(e)
            
        return result