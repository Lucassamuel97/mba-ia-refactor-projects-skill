const LEVELS = { error: 0, warn: 1, info: 2, debug: 3 };

// Ponto único de saída de log da aplicação.
function createLogger(level) {
    const threshold = LEVELS[level] ?? LEVELS.info;
    const writer = (name, output) => (...args) => {
        if (LEVELS[name] <= threshold) output(`[${name.toUpperCase()}]`, ...args);
    };

    return {
        error: writer('error', console.error),
        warn: writer('warn', console.warn),
        info: writer('info', console.log),
        debug: writer('debug', console.log),
    };
}

module.exports = { createLogger };
