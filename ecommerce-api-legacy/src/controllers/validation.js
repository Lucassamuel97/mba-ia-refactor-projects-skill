const { ValidationError } = require('../utils/errors');

const POSITIVE_INTEGER = /^[1-9]\d*$/;

function isNonEmptyString(value) {
    return typeof value === 'string' && value.length > 0;
}

function parsePositiveInteger(value) {
    if (typeof value === 'number' && Number.isInteger(value) && value > 0) return value;
    if (typeof value === 'string' && POSITIVE_INTEGER.test(value)) return Number(value);
    throw new ValidationError();
}

function parseCheckoutBody(body) {
    const data = body && typeof body === 'object' ? body : {};
    const { usr, eml, pwd, card } = data;
    if (![usr, eml, pwd, card].every(isNonEmptyString)) throw new ValidationError();
    return { name: usr, email: eml, password: pwd, courseId: parsePositiveInteger(data.c_id), card };
}

module.exports = { parseCheckoutBody, parsePositiveInteger };
