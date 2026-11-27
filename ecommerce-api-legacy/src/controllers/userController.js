const { parsePositiveInteger } = require('./validation');

function createUserController({ userService }) {
    return {
        async remove(req, res) {
            await userService.deleteUser(parsePositiveInteger(req.params.id));
            res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
        },
    };
}

module.exports = { createUserController };
