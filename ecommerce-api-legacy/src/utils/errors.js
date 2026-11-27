class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.statusCode = statusCode;
    }
}

class ValidationError extends AppError {
    constructor(message = 'Bad Request') { super(message, 400); }
}

class BusinessRuleError extends AppError {
    constructor(message) { super(message, 400); }
}

class UnauthorizedError extends AppError {
    constructor(message = 'Autenticação necessária') { super(message, 401); }
}

class ForbiddenError extends AppError {
    constructor(message = 'Acesso negado') { super(message, 403); }
}

class NotFoundError extends AppError {
    constructor(message) { super(message, 404); }
}

class ConflictError extends AppError {
    constructor(message) { super(message, 409); }
}

module.exports = {
    AppError, ValidationError, BusinessRuleError, UnauthorizedError,
    ForbiddenError, NotFoundError, ConflictError,
};
