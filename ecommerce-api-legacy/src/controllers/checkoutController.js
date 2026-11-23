const { ValidationError } = require('../utils/errors');

const INVALID_INPUT_MESSAGE = 'Bad Request';
const EMAIL_FORMAT = /^[^\s@]+@[^\s@]+$/;

const isText = (value) => typeof value === 'string';

// Os nomes dos campos (usr, eml, pwd, c_id, card) são o contrato da API e ficam como estão.
function parseCheckoutInput(body) {
    const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = body;

    const hasRequiredFields = name && email && courseId && cardNumber;
    const hasValidTypes = isText(name) && isText(email) && isText(cardNumber) && (!password || isText(password));

    if (!hasRequiredFields || !hasValidTypes || !EMAIL_FORMAT.test(email)) {
        throw new ValidationError(INVALID_INPUT_MESSAGE);
    }

    return { name, email, password, courseId, cardNumber };
}

function createCheckoutController({ checkoutService }) {
    return {
        async create(req, res) {
            const enrollmentId = await checkoutService.checkout(parseCheckoutInput(req.body));
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
