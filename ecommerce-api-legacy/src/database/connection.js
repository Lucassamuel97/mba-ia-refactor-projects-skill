const { AsyncLocalStorage } = require('node:async_hooks');
const sqlite3 = require('sqlite3').verbose();

// Promises sobre o driver de callbacks. O banco em memória exige uma conexão única,
// então os comandos passam por uma fila: nada de fora entra no meio de uma transação aberta.
function createConnection(filename) {
    const raw = new sqlite3.Database(filename);
    const insideTransaction = new AsyncLocalStorage();
    let queue = Promise.resolve();

    function enqueue(task) {
        const result = queue.then(task);
        queue = result.catch(() => {});
        return result;
    }

    function execute(method, sql, params) {
        return new Promise((resolve, reject) => {
            raw[method](sql, params, function onDone(err, rows) {
                if (err) return reject(err);
                resolve(method === 'run' ? { lastID: this.lastID, changes: this.changes } : rows);
            });
        });
    }

    function statement(method) {
        return (sql, params = []) => (insideTransaction.getStore()
            ? execute(method, sql, params)
            : enqueue(() => execute(method, sql, params)));
    }

    function transaction(work) {
        if (insideTransaction.getStore()) return work();

        return enqueue(() => insideTransaction.run(true, async () => {
            await execute('run', 'BEGIN', []);
            try {
                const result = await work();
                await execute('run', 'COMMIT', []);
                return result;
            } catch (err) {
                await execute('run', 'ROLLBACK', []);
                throw err;
            }
        }));
    }

    return { run: statement('run'), get: statement('get'), all: statement('all'), transaction };
}

module.exports = { createConnection };
