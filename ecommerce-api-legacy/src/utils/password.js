const { randomBytes, scrypt, timingSafeEqual } = require('node:crypto');
const { promisify } = require('node:util');

const scryptAsync = promisify(scrypt);
const KEY_LENGTH = 64;
const SCHEME = 'scrypt';

async function hashPassword(password) {
    const salt = randomBytes(16).toString('hex');
    const hash = await scryptAsync(password, salt, KEY_LENGTH);
    return `${SCHEME}$${salt}$${hash.toString('hex')}`;
}

async function verifyPassword(password, stored) {
    const [scheme, salt, hash] = String(stored).split('$');
    if (scheme !== SCHEME || !salt || !hash) return false;
    const expected = Buffer.from(hash, 'hex');
    const candidate = await scryptAsync(password, salt, expected.length);
    return timingSafeEqual(candidate, expected);
}

module.exports = { hashPassword, verifyPassword };
