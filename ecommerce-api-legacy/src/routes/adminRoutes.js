const express = require('express');
const { asyncHandler } = require('../middlewares/asyncHandler');

function adminRoutes({ reportController, requireAdminToken }) {
    const router = express.Router();
    router.get('/admin/financial-report', requireAdminToken, asyncHandler(reportController.financialReport));
    return router;
}

module.exports = { adminRoutes };
