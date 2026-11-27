const { createHash, timingSafeEqual } = require('node:crypto');
const { ForbiddenError, UnauthorizedError } = require('../utils/errors');

const digest = (value) => createHash('sha256').update(value).digest();

// Guard das rotas administrativas: sempre ligado. Sem ADMIN_TOKEN no ambiente, nega tudo.
function createRequireAdminToken({ adminToken }) {
    return function requireAdminToken(req, res, next) {
        const provided = req.get('X-Admin-Token');
        if (!provided) return next(new UnauthorizedError('Autenticação necessária'));
        if (!adminToken || !timingSafeEqual(digest(provided), digest(adminToken))) {
            return next(new ForbiddenError('Acesso negado'));
        }
        return next();
    };
}

module.exports = { createRequireAdminToken };
