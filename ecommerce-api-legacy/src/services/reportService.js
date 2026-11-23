const { PAYMENT_STATUS } = require('../models/paymentModel');

const UNKNOWN_STUDENT = 'Unknown';
const NO_PAYMENT_AMOUNT = 0;

class ReportService {
    constructor({ reportModel }) {
        this.reportModel = reportModel;
    }

    async financialReport() {
        const rows = await this.reportModel.listCourseEnrollments();
        const reportByCourse = new Map();

        for (const row of rows) {
            if (!reportByCourse.has(row.course_id)) {
                reportByCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const courseReport = reportByCourse.get(row.course_id);
            const hasPayment = row.payment_id !== null;

            if (hasPayment && row.payment_status === PAYMENT_STATUS.PAID) {
                courseReport.revenue += row.payment_amount;
            }
            courseReport.students.push({
                student: row.user_id === null ? UNKNOWN_STUDENT : row.student_name,
                paid: hasPayment ? row.payment_amount : NO_PAYMENT_AMOUNT,
            });
        }

        return [...reportByCourse.values()];
    }
}

module.exports = ReportService;
