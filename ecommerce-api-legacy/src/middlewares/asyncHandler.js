// No Express 4, a rejeição de um handler async precisa ser encaminhada ao next.
const asyncHandler = (handler) => (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);

module.exports = asyncHandler;
