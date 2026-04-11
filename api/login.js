import { createHmac } from 'node:crypto';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  const { login, password } = req.body || {};

  if (login === 'admin' && password === 'admin') {
    const secret = process.env.ADMIN_SECRET || 'hoper-cms-fallback';
    const payload = JSON.stringify({ user: 'admin', exp: Date.now() + 86400000 }); // 24h
    const data = Buffer.from(payload).toString('base64url');
    const sig = createHmac('sha256', secret).update(data).digest('hex');
    return res.json({ ok: true, token: `${data}.${sig}` });
  }

  res.status(401).json({ ok: false, error: 'Credenciais inválidas' });
}
