const { PAYMENT_STATUS } = require('../models/paymentModel');

const APPROVED_CARD_PREFIX = '4';
const VISIBLE_CARD_DIGITS = 4;

// Gateway simulado herdado do legado: aprova cartões iniciados em "4" e recusa os demais.
// Uma integração real substitui esta classe mantendo o método charge.
class PaymentGateway {
    constructor({ apiKey, logger }) {
        this.apiKey = apiKey;
        this.logger = logger;
    }

    async charge({ cardNumber, amount }) {
        const lastDigits = cardNumber.slice(-VISIBLE_CARD_DIGITS);
        const keyState = this.apiKey ? 'configurada' : 'ausente';
        this.logger.info(`Processando ${amount} no cartão final ${lastDigits} (chave do gateway ${keyState})`);

        return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    }
}

module.exports = PaymentGateway;
