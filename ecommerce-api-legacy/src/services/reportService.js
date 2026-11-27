const { AppError } = require('../utils/errors');
const { PAYMENT_STATUS } = require('../models/paymentModel');
const logger = require('../utils/logger');

class ReportService {
    constructor({ reportModel }) {
        this.reportModel = reportModel;
    }

    async financialReport() {
        let rows;
        try {
            rows = await this.reportModel.financialRows();
        } catch (err) {
            logger.error('Erro DB', err);
            throw new AppError('Erro DB', 500);
        }

        const courses = new Map();
        for (const row of rows) {
            if (!courses.has(row.course_id)) {
                courses.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const courseData = courses.get(row.course_id);
            const hasPayment = row.payment_id !== null;
            if (hasPayment && row.payment_status === PAYMENT_STATUS.PAID) {
                courseData.revenue += row.payment_amount;
            }
            courseData.students.push({
                student: row.user_id !== null ? row.student_name : 'Unknown',
                paid: hasPayment ? row.payment_amount : 0,
            });
        }
        return [...courses.values()];
    }
}

module.exports = { ReportService };
