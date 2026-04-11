import { put } from '@vercel/blob';
import { createHmac } from 'node:crypto';

function verifyToken(token) {
  try {
    const [data, sig] = (token || '').split('.');
    if (!data || !sig) return false;
    const secret = process.env.ADMIN_SECRET || 'hoper-cms-fallback';
    const expected = createHmac('sha256', secret).update(data).digest('hex');
    if (expected !== sig) return false;
    const { exp } = JSON.parse(Buffer.from(data, 'base64url').toString());
    return exp > Date.now();
  } catch {
    return false;
  }
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') return res.status(405).end();

  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!verifyToken(token)) return res.status(401).json({ error: 'Não autorizado' });

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch {
      return res.status(400).json({ error: 'JSON inválido' });
    }
  }

  const { filename, base64, mimeType } = body || {};
  if (!filename || !base64 || !mimeType) {
    return res.status(400).json({ error: 'Campos obrigatórios: filename, base64, mimeType' });
  }

  const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'];
  if (!allowed.includes(mimeType)) {
    return res.status(400).json({ error: 'Tipo não permitido. Use PNG, JPG, WebP ou SVG.' });
  }

  try {
    const buffer = Buffer.from(base64, 'base64');
    const blob = await put('hoper-uploads/' + filename, buffer, {
      access: 'public',
      contentType: mimeType,
      addRandomSuffix: true,
    });
    return res.json({ ok: true, url: blob.url });
  } catch (e) {
    console.error('POST /api/upload error:', e);
    return res.status(500).json({ error: String(e?.message || e) });
  }
}
