const { parseCheckoutBody } = require('./validation');

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const enrollmentId = await checkoutService.checkout(parseCheckoutBody(req.body));
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
