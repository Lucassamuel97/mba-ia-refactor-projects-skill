const { AppError, BusinessRuleError, NotFoundError, UnauthorizedError } = require('../utils/errors');
const { PAYMENT_STATUS } = require('../models/paymentModel');
const { hashPassword, verifyPassword } = require('../utils/password');
const logger = require('../utils/logger');

// Falha de banco em uma etapa vira 500 com a mensagem que a API já usava para ela.
async function step(promise, message) {
    try {
        return await promise;
    } catch (err) {
        if (err instanceof AppError) throw err;
        logger.error(message, err);
        throw new AppError(message, 500);
    }
}

class CheckoutService {
    constructor({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway }) {
        this.db = db;
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
        this.paymentGateway = paymentGateway;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        const existingUser = await step(this.userModel.findByEmail(email), 'Erro DB');
        if (existingUser) await this.#ensurePassword(password, existingUser);

        const status = await this.paymentGateway.charge({ card, amount: course.price });
        if (status === PAYMENT_STATUS.DENIED) throw new BusinessRuleError('Pagamento recusado');

        return this.db.transaction(async () => {
            const userId = await this.#resolveBuyer({ name, email, password, existingUser });
            const enrollmentId = await step(this.enrollmentModel.create({ userId, courseId }), 'Erro Matrícula');
            await step(this.paymentModel.create({ enrollmentId, amount: course.price, status }), 'Erro Pagamento');
            await this.auditLogModel.create(`Checkout curso ${courseId} por ${userId}`);
            return enrollmentId;
        });
    }

    async #ensurePassword(password, user) {
        if (!(await verifyPassword(password, user.pass))) throw new UnauthorizedError('Credenciais inválidas');
    }

    // Dentro da transação: reconsulta o email para não duplicar a conta em checkouts concorrentes.
    async #resolveBuyer({ name, email, password, existingUser }) {
        if (existingUser) return existingUser.id;
        const user = await step(this.userModel.findByEmail(email), 'Erro DB');
        if (user) {
            await this.#ensurePassword(password, user);
            return user.id;
        }
        const passwordHash = await hashPassword(password);
        return step(this.userModel.create({ name, email, passwordHash }), 'Erro ao criar usuário');
    }
}

module.exports = { CheckoutService };
