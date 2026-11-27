// Express 4 não encaminha rejeições de handlers async: este wrapper as entrega ao errorHandler.
const asyncHandler = (handler) => (req, res, next) =>
    Promise.resolve(handler(req, res, next)).catch(next);

module.exports = { asyncHandler };
