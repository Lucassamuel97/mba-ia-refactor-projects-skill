const { createHash, timingSafeEqual } = require('node:crypto');

const ADMIN_TOKEN_HEADER = 'x-admin-token';
const ACCESS_DENIED_MESSAGE = 'Acesso negado';

const digest = (value) => createHash('sha256').update(value).digest();

// Sem token configurado, as rotas protegidas respondem 403 sempre (seguro por padrão).
function createRequireAdminToken({ adminToken }) {
    return function requireAdminToken(req, res, next) {
        const providedToken = req.get(ADMIN_TOKEN_HEADER) || '';
        const isAuthorized = Boolean(adminToken) && timingSafeEqual(digest(providedToken), digest(adminToken));

        if (!isAuthorized) return res.status(403).send(ACCESS_DENIED_MESSAGE);
        next();
    };
}

module.exports = { createRequireAdminToken };
