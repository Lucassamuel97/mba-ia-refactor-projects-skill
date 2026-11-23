// A exclusão continua removendo só o usuário: apagar matrículas e pagamentos junto
// tiraria receita do relatório financeiro, o que depende de decisão de negócio.
const USER_DELETED_MESSAGE = 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';

function createUserController({ userModel }) {
    return {
        async remove(req, res) {
            await userModel.deleteById(req.params.id);
            res.send(USER_DELETED_MESSAGE);
        },
    };
}

module.exports = { createUserController };
