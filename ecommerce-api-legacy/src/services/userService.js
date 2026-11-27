const { ConflictError } = require('../utils/errors');

class UserService {
    constructor({ db, userModel, enrollmentModel }) {
        this.db = db;
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
    }

    // Matrículas e pagamentos são histórico financeiro: o usuário que os tem não é apagado.
    deleteUser(userId) {
        return this.db.transaction(async () => {
            if (await this.enrollmentModel.countByUser(userId) > 0) {
                throw new ConflictError('Usuário possui matrículas registradas');
            }
            await this.userModel.deleteById(userId);
        });
    }
}

module.exports = { UserService };
