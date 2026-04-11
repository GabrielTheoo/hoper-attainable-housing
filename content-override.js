(function () {
  'use strict';

  // ── XPath helpers ─────────────────────────────────────────────
  function getXPath(el) {
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && node !== document.documentElement) {
      const tag = node.tagName.toLowerCase();
      let idx = 1, count = 0;
      let sib = node.parentElement ? node.parentElement.firstElementChild : null;
      while (sib) {
        if (sib.tagName.toLowerCase() === tag) {
          count++;
          if (sib === node) idx = count;
        }
        sib = sib.nextElementSibling;
      }
      parts.unshift(count > 1 ? tag + '[' + idx + ']' : tag);
      node = node.parentElement;
    }
    return '//' + parts.join('/');
  }

  function byXPath(xpath) {
    try {
      return document.evaluate(
        xpath, document, null,
        XPathResult.FIRST_ORDERED_NODE_TYPE, null
      ).singleNodeValue;
    } catch { return null; }
  }

  // ── Apply stored overrides (regular visitors) ─────────────────
  async function applyOverrides() {
    try {
      const res = await fetch('/api/content', { cache: 'no-store' });
      if (!res.ok) return;
      const all = await res.json();
      const path = window.location.pathname;
      const overrides = all[path] || all[path.replace(/\/$/, '')] || all[path + '/'] || {};
      for (const [xpath, ov] of Object.entries(overrides)) {
        const el = byXPath(xpath);
        if (!el) continue;
        if (ov.text !== undefined) el.textContent = ov.text;
        if (ov.color) el.style.color = ov.color;
      }
    } catch { /* silent fail on non-Vercel environments */ }
  }

  // ── Edit mode (when inside admin iframe) ──────────────────────
  const editableMap = new Map();

  function enableEditMode() {
    const style = document.createElement('style');
    style.textContent =
      '[data-he]:hover{outline:2px dashed #EB7F1E!important;outline-offset:3px!important;' +
      'cursor:pointer!important;background:rgba(235,127,30,.06)!important;}' +
      'body{user-select:none!important;}';
    document.head.appendChild(style);

    const SEL = 'h1,h2,h3,h4,h5,h6,p,li,a,button,span,label,td,th,strong,em,small';
    document.querySelectorAll(SEL).forEach(function (el) {
      if (el.closest('script,style,noscript')) return;
      if (el.querySelector('h1,h2,h3,h4,p,div,ul,ol,table')) return;
      const text = el.textContent.trim();
      if (!text || text.length < 2) return;

      const xpath = getXPath(el);
      el.setAttribute('data-he', '1');
      editableMap.set(xpath, el);

      el.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const r = el.getBoundingClientRect();
        window.parent.postMessage({
          type: 'HE_CLICK',
          xpath: xpath,
          text: el.textContent,
          color: el.style.color || '',
          rect: { top: r.top + window.scrollY, left: r.left, w: r.width, h: r.height }
        }, window.location.origin);
      }, true);
    });

    window.addEventListener('message', function (e) {
      if (e.origin !== window.location.origin) return;
      if (e.data.type !== 'HE_APPLY') return;
      const el = editableMap.get(e.data.xpath);
      if (!el) return;
      if (e.data.text !== undefined) el.textContent = e.data.text;
      if (e.data.color !== undefined) el.style.color = e.data.color || '';
    });
  }

  // ── Detect if inside admin iframe (same-origin check) ─────────
  function inAdminFrame() {
    try { return window !== window.top && !!window.top.document; }
    catch { return false; }
  }

  // ── Boot ──────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    if (inAdminFrame()) {
      window.parent.postMessage(
        { type: 'HE_READY', path: window.location.pathname },
        window.location.origin
      );
      window.addEventListener('message', function init(e) {
        if (e.origin !== window.location.origin) return;
        if (e.data.type !== 'HE_ENABLE') return;
        window.removeEventListener('message', init);
        applyOverrides().then(enableEditMode);
      });
    } else {
      applyOverrides();
    }
  });
})();
