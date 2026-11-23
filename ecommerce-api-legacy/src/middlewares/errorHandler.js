const { STATUS_CODES } = require('node:http');
const { AppError } = require('../utils/errors');

const INTERNAL_ERROR_MESSAGE = 'Erro interno do servidor';

const isClientError = (statusCode) => statusCode >= 400 && statusCode < 500;

// As respostas de erro seguem em texto puro, como a API sempre respondeu.
function createErrorHandler({ logger }) {
    return function errorHandler(err, req, res, next) {
        if (res.headersSent) return next(err);

        if (err instanceof AppError) {
            return res.status(err.statusCode).send(err.message);
        }

        // Erros 4xx do próprio framework (ex.: JSON malformado): mesmo status, sem stack trace.
        if (err.expose && isClientError(err.statusCode)) {
            return res.status(err.statusCode).send(STATUS_CODES[err.statusCode]);
        }

        logger.error(err);
        res.status(500).send(INTERNAL_ERROR_MESSAGE);
    };
}

module.exports = { createErrorHandler };
