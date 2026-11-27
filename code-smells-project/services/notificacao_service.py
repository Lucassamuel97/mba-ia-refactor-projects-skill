"""Notificações de pedido. Hoje registradas em log; o envio real entra aqui."""
import logging

from models.pedido_model import STATUS_APROVADO, STATUS_CANCELADO

logger = logging.getLogger(__name__)


class NotificacaoService:
    def pedido_criado(self, pedido_id, usuario_id):
        logger.info("ENVIANDO EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
        logger.info("ENVIANDO SMS: Seu pedido foi recebido!")
        logger.info("ENVIANDO PUSH: Novo pedido recebido pelo sistema")

    def status_alterado(self, pedido_id, novo_status):
        if novo_status == STATUS_APROVADO:
            logger.info("NOTIFICAÇÃO: Pedido %s foi aprovado! Preparar envio.", pedido_id)
        if novo_status == STATUS_CANCELADO:
            logger.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
