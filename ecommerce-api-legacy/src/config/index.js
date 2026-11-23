// Único ponto de leitura do ambiente. Segredos não têm valor padrão: ausentes, o recurso fica desligado.
module.exports = {
    port: Number(process.env.PORT || 3000),
    databaseFile: ':memory:',
    // Ausente = rotas administrativas respondem 403.
    adminToken: process.env.ADMIN_TOKEN || null,
    // Ausente = o gateway de pagamento segue apenas em modo simulado.
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || null,
    logLevel: process.env.LOG_LEVEL || 'info',
};
