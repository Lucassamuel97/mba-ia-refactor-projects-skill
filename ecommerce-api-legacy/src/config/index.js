// Único ponto que lê o ambiente. Nenhum segredo fica no código.
module.exports = {
    port: Number(process.env.PORT || 3000),
    databasePath: ':memory:',
    // Ausente = rotas administrativas recusam todos os pedidos (403).
    adminToken: process.env.ADMIN_TOKEN || null,
};
