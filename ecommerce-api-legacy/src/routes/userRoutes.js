const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');

function userRoutes({ userController, requireAdminToken }) {
    const router = express.Router();
    router.delete('/users/:id', requireAdminToken, asyncHandler(userController.remove));
    return router;
}

module.exports = userRoutes;
