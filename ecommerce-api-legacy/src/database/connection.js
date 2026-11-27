const sqlite3 = require('sqlite3');

// Promises sobre o driver de callbacks. Banco em memória exige conexão única:
// ela é criada pelo composition root e injetada nos models.
function createConnection(path) {
    const raw = new sqlite3.Database(path);

    const run = (sql, params = []) => new Promise((resolve, reject) => {
        raw.run(sql, params, function onRun(err) {
            if (err) reject(err);
            else resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
    const get = (sql, params = []) => new Promise((resolve, reject) => {
        raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
    const all = (sql, params = []) => new Promise((resolve, reject) => {
        raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });

    // Transações serializadas: a conexão é compartilhada, então duas não podem se sobrepor.
    let queue = Promise.resolve();
    function transaction(work) {
        const result = queue.then(async () => {
            await run('BEGIN');
            try {
                const value = await work();
                await run('COMMIT');
                return value;
            } catch (err) {
                await run('ROLLBACK');
                throw err;
            }
        });
        queue = result.catch(() => {});
        return result;
    }

    return { run, get, all, transaction };
}

module.exports = { createConnection };
