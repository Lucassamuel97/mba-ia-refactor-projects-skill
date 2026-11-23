const { PAYMENT_STATUS } = require('../models/paymentModel');
const { BusinessRuleError, NotFoundError } = require('../utils/errors');

class CheckoutService {
    constructor({
        courseModel, userModel, enrollmentModel, paymentModel, auditLogModel,
        paymentGateway, hashPassword, runInTransaction, logger,
    }) {
        this.courseModel = courseModel;
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
        this.paymentGateway = paymentGateway;
        this.hashPassword = hashPassword;
        this.runInTransaction = runInTransaction;
        this.logger = logger;
    }

    async checkout({ name, email, password, courseId, cardNumber }) {
        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        // Como no legado, a conta é criada antes da cobrança e permanece se o pagamento for recusado.
        const userId = await this.findOrCreateUser({ name, email, password });

        // A cobrança é externa ao banco: acontece antes, e só o resultado entra na transação.
        const status = await this.paymentGateway.charge({ cardNumber, amount: course.price });
        if (status === PAYMENT_STATUS.DENIED) throw new BusinessRuleError('Pagamento recusado');

        const enrollmentId = await this.runInTransaction(async () => {
            const newEnrollmentId = await this.enrollmentModel.create({ userId, courseId });
            await this.paymentModel.create({ enrollmentId: newEnrollmentId, amount: course.price, status });
            await this.auditLogModel.record(`Checkout curso ${courseId} por ${userId}`);
            return newEnrollmentId;
        });

        this.logger.info(`Checkout concluído: matrícula ${enrollmentId} em "${course.title}"`);
        return enrollmentId;
    }

    // Busca e criação na mesma transação: dois checkouts simultâneos não duplicam o email.
    findOrCreateUser({ name, email, password }) {
        return this.runInTransaction(async () => {
            const existingUser = await this.userModel.findByEmail(email);
            if (existingUser) return existingUser.id;

            // Sem pwd a conta fica sem senha utilizável (o legado gravava uma senha padrão conhecida).
            const passwordHash = password ? await this.hashPassword(password) : null;
            return this.userModel.create({ name, email, passwordHash });
        });
    }
}

module.exports = CheckoutService;
