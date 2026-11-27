const express = require('express');
const config = require('./config');
const logger = require('./utils/logger');
const { createConnection } = require('./database/connection');
const { initSchema } = require('./database/schema');
const { UserModel } = require('./models/userModel');
const { CourseModel } = require('./models/courseModel');
const { EnrollmentModel } = require('./models/enrollmentModel');
const { PaymentModel } = require('./models/paymentModel');
const { AuditLogModel } = require('./models/auditLogModel');
const { ReportModel } = require('./models/reportModel');
const { PaymentGateway } = require('./services/paymentGateway');
const { CheckoutService } = require('./services/checkoutService');
const { ReportService } = require('./services/reportService');
const { UserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { checkoutRoutes } = require('./routes/checkoutRoutes');
const { adminRoutes } = require('./routes/adminRoutes');
const { userRoutes } = require('./routes/userRoutes');
const { createRequireAdminToken } = require('./middlewares/requireAdminToken');
const { errorHandler } = require('./middlewares/errorHandler');

async function main() {
    const db = createConnection(config.databasePath);
    await initSchema(db);

    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const paymentModel = new PaymentModel(db);
    const auditLogModel = new AuditLogModel(db);
    const reportModel = new ReportModel(db);

    const checkoutService = new CheckoutService({
        db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel,
        paymentGateway: new PaymentGateway(),
    });
    const reportService = new ReportService({ reportModel });
    const userService = new UserService({ db, userModel, enrollmentModel });

    const requireAdminToken = createRequireAdminToken({ adminToken: config.adminToken });

    const app = express();
    app.use(express.json());
    app.use('/api', checkoutRoutes({ checkoutController: createCheckoutController({ checkoutService }) }));
    app.use('/api', adminRoutes({ reportController: createReportController({ reportService }), requireAdminToken }));
    app.use('/api', userRoutes({ userController: createUserController({ userService }), requireAdminToken }));
    app.use(errorHandler);

    app.listen(config.port, () => {
        logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

main().catch((err) => {
    logger.error('Falha ao iniciar a aplicação', err);
    process.exit(1);
});
