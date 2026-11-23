const express = require('express');

const config = require('./config');
const { createConnection } = require('./database/connection');
const { initSchema } = require('./database/schema');
const { createLogger } = require('./utils/logger');
const { hashPassword } = require('./utils/password');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');

const PaymentGateway = require('./services/paymentGateway');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');

const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');

const checkoutRoutes = require('./routes/checkoutRoutes');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');

const { createRequireAdminToken } = require('./middlewares/requireAdminToken');
const { createErrorHandler } = require('./middlewares/errorHandler');

const logger = createLogger(config.logLevel);

async function start() {
    const db = createConnection(config.databaseFile);
    await initSchema(db);

    const userModel = new UserModel(db);
    const reportModel = new ReportModel(db);

    const checkoutService = new CheckoutService({
        courseModel: new CourseModel(db),
        userModel,
        enrollmentModel: new EnrollmentModel(db),
        paymentModel: new PaymentModel(db),
        auditLogModel: new AuditLogModel(db),
        paymentGateway: new PaymentGateway({ apiKey: config.paymentGatewayKey, logger }),
        hashPassword,
        runInTransaction: db.transaction,
        logger,
    });
    const reportService = new ReportService({ reportModel });

    const checkoutController = createCheckoutController({ checkoutService });
    const reportController = createReportController({ reportService });
    const userController = createUserController({ userModel });
    const requireAdminToken = createRequireAdminToken({ adminToken: config.adminToken });

    const app = express();
    app.use(express.json());
    app.use('/api', checkoutRoutes({ checkoutController }));
    app.use('/api', adminRoutes({ reportController, requireAdminToken }));
    app.use('/api', userRoutes({ userController, requireAdminToken }));
    app.use(createErrorHandler({ logger }));

    app.listen(config.port, () => {
        logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

start().catch((err) => {
    logger.error('Falha ao iniciar a aplicação', err);
    process.exit(1);
});
