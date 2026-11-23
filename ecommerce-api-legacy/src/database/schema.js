const { PAYMENT_STATUS } = require('../models/paymentModel');
const { hashPassword } = require('../utils/password');

const TABLES = [
    'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)',
    'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)',
    'CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)',
    'CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)',
    'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
];

const SEED_USER = { name: 'Leonan', email: 'leonan@fullcycle.com.br', password: '123' };

async function initSchema(db) {
    const seedPasswordHash = await hashPassword(SEED_USER.password);

    await db.transaction(async () => {
        for (const createTable of TABLES) {
            await db.run(createTable);
        }

        await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [SEED_USER.name, SEED_USER.email, seedPasswordHash]);
        await db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
        await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
        await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, ?)', [PAYMENT_STATUS.PAID]);
    });
}

module.exports = { initSchema };
