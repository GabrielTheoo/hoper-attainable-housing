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

  // ── Text helpers (preserve child elements like icons) ─────────
  // Get only the direct text node content of an element
  function getDirectText(el) {
    let t = '';
    el.childNodes.forEach(function (n) {
      if (n.nodeType === Node.TEXT_NODE) t += n.textContent;
    });
    t = t.trim();
    return t || el.textContent.trim();
  }

  // Set text without destroying child elements (icons, badges, etc.)
  function applyText(el, newText) {
    // Collect direct text nodes
    const tNodes = [];
    el.childNodes.forEach(function (n) {
      if (n.nodeType === Node.TEXT_NODE && n.textContent.trim()) tNodes.push(n);
    });
    if (tNodes.length > 0) {
      tNodes[0].textContent = newText;
      for (let i = 1; i < tNodes.length; i++) tNodes[i].textContent = '';
    } else {
      // No direct text nodes — safe to set textContent
      el.textContent = newText;
    }
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
        if (ov.text !== undefined) applyText(el, ov.text);
        if (ov.color) el.style.color = ov.color;
      }
    } catch { /* silent fail on non-Vercel environments */ }
  }

  // ── Edit mode (when inside admin iframe) ──────────────────────
  const editableMap = new Map();

  function isEditable(el) {
    if (el.closest('script,style,noscript,svg')) return false;
    if (el.querySelector('h1,h2,h3,h4,h5,h6,p,ul,ol,table,section,article,nav,header,footer')) return false;
    const tag = el.tagName.toLowerCase();
    if (tag === 'div') {
      // Divs must have direct text (not just via child elements)
      // This excludes layout containers that only have child divs
      const directText = getDirectText(el);
      if (directText.length < 2) return false;
      // Skip divs with too many children (clearly a layout container)
      if (el.children.length > 4) return false;
    } else {
      if (el.textContent.trim().length < 2) return false;
    }
    return true;
  }

  function enableEditMode() {
    const style = document.createElement('style');
    style.textContent =
      '[data-he]:hover{outline:2px dashed #EB7F1E!important;outline-offset:3px!important;' +
      'cursor:pointer!important;background:rgba(235,127,30,.06)!important;}' +
      'body{user-select:none!important;}';
    document.head.appendChild(style);

    // Include div to catch card titles/items; filter keeps only leaf-ish text elements
    const SEL = 'h1,h2,h3,h4,h5,h6,p,li,a,button,span,label,td,th,strong,em,small,div';
    document.querySelectorAll(SEL).forEach(function (el) {
      if (!isEditable(el)) return;

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
          text: getDirectText(el),
          color: el.style.color || '',
          rect: { top: r.top + window.scrollY, left: r.left, w: r.width, h: r.height }
        }, window.location.origin);
      }, false);
    });

    window.addEventListener('message', function (e) {
      if (e.origin !== window.location.origin) return;
      if (e.data.type !== 'HE_APPLY') return;
      const el = editableMap.get(e.data.xpath);
      if (!el) return;
      if (e.data.text !== undefined) applyText(el, e.data.text);
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
