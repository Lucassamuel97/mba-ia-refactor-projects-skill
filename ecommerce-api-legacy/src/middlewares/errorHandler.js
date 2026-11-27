const { STATUS_CODES } = require('node:http');
const { AppError } = require('../utils/errors');
const logger = require('../utils/logger');

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    if (err instanceof AppError) {
        return res.status(err.statusCode).send(err.message);
    }
    // Erros HTTP do próprio Express (JSON malformado, corpo grande): mesmo status, sem stack trace.
    if (err.status && err.status < 500) {
        return res.status(err.status).send(err.status === 400 ? 'Bad Request' : STATUS_CODES[err.status]);
    }
    logger.error('Erro não tratado', err);
    return res.status(500).send('Erro interno do servidor');
}

module.exports = { errorHandler };
