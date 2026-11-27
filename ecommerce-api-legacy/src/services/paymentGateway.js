const { PAYMENT_STATUS } = require('../models/paymentModel');
const logger = require('../utils/logger');

const APPROVED_CARD_PREFIX = '4';

// Gateway simulado: cartões que começam com 4 são aprovados.
class PaymentGateway {
    async charge({ card }) {
        logger.info(`Processando cartão final ${card.slice(-4)}`);
        return card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    }
}

module.exports = { PaymentGateway, APPROVED_CARD_PREFIX };
