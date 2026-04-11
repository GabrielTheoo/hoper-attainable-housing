import { put, list } from '@vercel/blob';
import { createHmac } from 'node:crypto';

const BLOB_FILE = 'hoper-cms-content.json';

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
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');

  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'authorization, content-type');
    return res.status(200).end();
  }

  if (req.method === 'GET') {
    try {
      const { blobs } = await list({ prefix: BLOB_FILE });
      if (!blobs.length) return res.json({});
      const r = await fetch((blobs[0].downloadUrl || blobs[0].url) + '?bust=' + Date.now());
      return res.json(await r.json());
    } catch (e) {
      console.error('GET /api/content error:', e);
      return res.json({});
    }
  }

  if (req.method === 'PUT') {
    const token = (req.headers.authorization || '').replace('Bearer ', '');
    if (!verifyToken(token)) {
      return res.status(401).json({ error: 'Não autorizado' });
    }

    // Vercel auto-parses JSON body, but handle raw string as fallback
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch {
        return res.status(400).json({ error: 'JSON inválido' });
      }
    }
    if (!body || typeof body !== 'object') body = {};

    try {
      await put(BLOB_FILE, JSON.stringify(body), {
        access: 'public',
        addRandomSuffix: false,
        allowOverwrite: true,
        contentType: 'application/json',
      });
      return res.json({ ok: true });
    } catch (e) {
      console.error('PUT /api/content blob error:', e);
      return res.status(500).json({ error: String(e?.message || e) });
    }
  }

  res.status(405).end();
}
