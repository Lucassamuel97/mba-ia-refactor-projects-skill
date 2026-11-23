const { randomBytes, scrypt } = require('node:crypto');
const { promisify } = require('node:util');

const scryptAsync = promisify(scrypt);
const SALT_BYTES = 16;
const KEY_BYTES = 64;

// Formato gravado: scrypt$<salt hex>$<hash hex>
async function hashPassword(password) {
    const salt = randomBytes(SALT_BYTES).toString('hex');
    const key = await scryptAsync(password, salt, KEY_BYTES);
    return `scrypt$${salt}$${key.toString('hex')}`;
}

module.exports = { hashPassword };
