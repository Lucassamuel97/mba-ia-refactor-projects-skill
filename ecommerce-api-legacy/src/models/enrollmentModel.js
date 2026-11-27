class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    async create({ userId, courseId }) {
        const { lastID } = await this.db.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
        );
        return lastID;
    }

    async countByUser(userId) {
        const row = await this.db.get('SELECT COUNT(*) AS total FROM enrollments WHERE user_id = ?', [userId]);
        return row.total;
    }
}

module.exports = { EnrollmentModel };
