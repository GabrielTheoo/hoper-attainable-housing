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

  // ── Block helpers ─────────────────────────────────────────────
  function getBlockId(section) {
    if (section.id) return section.id;
    const cls = Array.from(section.classList).find(c => c && c !== 'section');
    return cls || null;
  }

  function findBlockById(bid) {
    if (!bid) return null;
    const byId = document.getElementById(bid);
    if (byId) return byId;
    try { return document.querySelector('main > section.' + CSS.escape(bid)); } catch { return null; }
  }

  // ── Text helpers ──────────────────────────────────────────────
  function getDirectText(el) {
    const parts = [];
    el.childNodes.forEach(function (n) {
      if (n.nodeType === Node.TEXT_NODE) {
        const t = n.textContent.trim();
        if (t) parts.push(t);
      }
    });
    return parts.join(' ') || el.textContent.trim();
  }

  function applyText(el, newText) {
    const tNodes = [];
    el.childNodes.forEach(function (n) {
      if (n.nodeType === Node.TEXT_NODE && n.textContent.trim()) tNodes.push(n);
    });
    if (tNodes.length > 0) {
      tNodes[0].textContent = newText;
      for (let i = 1; i < tNodes.length; i++) tNodes[i].textContent = '';
      Array.from(el.childNodes).forEach(function (n) {
        if (n.nodeType === 1 && n.tagName === 'BR') n.remove();
      });
    } else {
      el.textContent = newText;
    }
  }

  // ── Apply stored overrides ────────────────────────────────────
  function applyOverrideMap(overrides) {
    const blocks = overrides.__blocks__;
    if (blocks) {
      if (blocks.__order__ && Array.isArray(blocks.__order__)) {
        const main = document.querySelector('main');
        if (main) {
          const existing = Array.from(main.querySelectorAll(':scope > section'));
          const ordered = [];
          blocks.__order__.forEach(function (bid) {
            const el = findBlockById(bid);
            if (el && el.parentElement === main) ordered.push(el);
          });
          existing.forEach(function (s) { if (!ordered.includes(s)) ordered.push(s); });
          ordered.forEach(function (s) { main.appendChild(s); });
        }
      }
      for (const [bid, bdata] of Object.entries(blocks)) {
        if (bid === '__order__') continue;
        const el = findBlockById(bid);
        if (el && bdata.style) el.setAttribute('style', bdata.style);
      }
    }

    for (const [xpath, ov] of Object.entries(overrides)) {
      if (xpath === '__blocks__') continue;
      const el = byXPath(xpath);
      if (!el) continue;
      if (ov.text !== undefined) applyText(el, ov.text);
      if (ov.color) el.style.color = ov.color;
      if (ov.elStyle) el.setAttribute('style', ov.elStyle);
      if (ov.src !== undefined && el.tagName.toLowerCase() === 'img') el.src = ov.src;
      if (ov.svgContent !== undefined && el.tagName.toLowerCase() === 'svg') {
        const tmp = document.createElement('div');
        tmp.innerHTML = ov.svgContent;
        const newEl = tmp.firstElementChild;
        if (newEl) el.replaceWith(newEl);
      }
    }
  }

  async function applyOverrides() {
    const path = window.location.pathname;
    try {
      const res = await fetch('/api/content', { cache: 'no-store' });
      if (res.ok) {
        const all = await res.json();
        const overrides = all[path] || all[path.replace(/\/$/, '')] || all[path + '/'] || {};
        applyOverrideMap(overrides);
      }
    } catch {}
    try {
      const raw = localStorage.getItem('hcms_preview_session');
      if (raw) {
        const all = JSON.parse(raw);
        const overrides = all[path] || all[path.replace(/\/$/, '')] || all[path + '/'] || {};
        applyOverrideMap(overrides);
      }
    } catch {}
  }

  // ── Edit mode ──────────────────────────────────────────────────
  const editableMap = new Map();
  let swapMode = false;

  // Swap mode: visual style injected dynamically
  let swapStyle = null;

  function enterSwapMode() {
    swapMode = true;
    if (!swapStyle) {
      swapStyle = document.createElement('style');
      swapStyle.id = 'he-swap-style';
      document.head.appendChild(swapStyle);
    }
    swapStyle.textContent =
      '[data-he]:hover{outline:2px dashed #00c8ff!important;outline-offset:3px!important;' +
      'cursor:crosshair!important;background:rgba(0,200,255,.08)!important;}' +
      '[data-hm]:hover{outline:2px dashed #00c8ff!important;outline-offset:3px!important;cursor:crosshair!important;}';
  }

  function exitSwapMode() {
    swapMode = false;
    if (swapStyle) swapStyle.textContent = '';
  }

  function elSnapshot(el) {
    const tag = el.tagName.toLowerCase();
    const isMedia = el.hasAttribute('data-hm');
    if (isMedia) {
      return {
        mediaType: tag === 'img' ? 'image' : 'svg',
        src: tag === 'img' ? el.src : undefined,
        svgContent: tag === 'svg' ? el.outerHTML : undefined,
      };
    }
    return {
      text: getDirectText(el),
      color: el.style.color || '',
      elStyle: el.getAttribute('style') || '',
    };
  }

  function inZone(el, selector) { return !!el.closest(selector); }

  function isEditable(el, restrict) {
    if (el.closest('script,style,noscript,svg')) return false;
    if (restrict) {
      if (!el.closest(restrict)) return false;
    } else {
      if (inZone(el, 'nav,header,footer')) return false;
    }
    if (el.querySelector('h1,h2,h3,h4,h5,h6,p,ul,ol,table,section,article,nav,header,footer')) return false;
    const tag = el.tagName.toLowerCase();
    if (tag === 'div') {
      const dt = getDirectText(el);
      if (dt.length < 2) return false;
      if (el.children.length > 4) return false;
    } else {
      if (el.textContent.trim().length < 2) return false;
    }
    return true;
  }

  function isEditableMedia(el, restrict) {
    if (el.closest('script,style,noscript')) return false;
    if (restrict) {
      if (!el.closest(restrict)) return false;
    } else {
      if (inZone(el, 'nav,header,footer')) return false;
    }
    const tag = el.tagName.toLowerCase();
    if (tag === 'svg') {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.width <= 18) return false;
      return true;
    }
    if (tag === 'img') {
      if (!el.src || el.src === window.location.href) return false;
      return true;
    }
    return false;
  }

  function enableEditMode(restrict) {
    const style = document.createElement('style');
    style.textContent =
      '[data-he]:hover{outline:2px dashed #EB7F1E!important;outline-offset:3px!important;' +
      'cursor:pointer!important;background:rgba(235,127,30,.08)!important;}' +
      '[data-hm]:hover{outline:2px dashed #EB7F1E!important;outline-offset:3px!important;cursor:pointer!important;}' +
      '[data-hb]{transition:outline .1s;}' +
      '[data-hb]:hover{outline:2px solid rgba(235,127,30,.5)!important;outline-offset:-2px!important;cursor:pointer!important;}' +
      '[data-hb].hb-sel{outline:2px solid #EB7F1E!important;outline-offset:-2px!important;}' +
      'body{user-select:none!important;}';
    document.head.appendChild(style);

    // ── Blocks ─────────────────────────────────────────────────
    if (!restrict) {
      const main = document.querySelector('main');
      if (main) {
        const blockList = [];
        Array.from(main.querySelectorAll(':scope > section')).forEach(function (sec) {
          const bid = getBlockId(sec);
          if (!bid) return;
          sec.setAttribute('data-hb', bid);
          const heading = sec.querySelector('h1,h2,h3,h4,h5,h6');
          const label = heading ? heading.textContent.trim().slice(0, 50) : bid;
          blockList.push({ blockId: bid, label: label });

          sec.addEventListener('click', function (e) {
            if (e.target.closest('[data-he],[data-hm]')) return;
            e.stopPropagation();
            document.querySelectorAll('[data-hb]').forEach(function (s) { s.classList.remove('hb-sel'); });
            sec.classList.add('hb-sel');
            const r = sec.getBoundingClientRect();
            window.parent.postMessage({
              type: 'HE_BLOCK_CLICK',
              blockId: bid,
              blockStyle: sec.getAttribute('style') || '',
              rect: { top: r.top + window.scrollY, left: r.left, w: r.width, h: r.height }
            }, window.location.origin);
          }, false);
        });
        window.parent.postMessage({ type: 'HE_BLOCKS', blocks: blockList }, window.location.origin);
      }
    }

    // ── Text elements ──────────────────────────────────────────
    const SEL = 'h1,h2,h3,h4,h5,h6,p,li,a,button,span,label,td,th,strong,em,small,div';
    document.querySelectorAll(SEL).forEach(function (el) {
      if (!isEditable(el, restrict)) return;
      const xpath = getXPath(el);
      el.setAttribute('data-he', '1');
      editableMap.set(xpath, el);

      el.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const snap = elSnapshot(el);
        if (swapMode) {
          exitSwapMode();
          window.parent.postMessage(Object.assign({ type: 'HE_SWAP_PICK', xpath: xpath }, snap), window.location.origin);
          return;
        }
        const r = el.getBoundingClientRect();
        window.parent.postMessage(Object.assign({
          type: 'HE_CLICK', xpath: xpath,
          rect: { top: r.top + window.scrollY, left: r.left, w: r.width, h: r.height }
        }, snap), window.location.origin);
      }, false);
    });

    // ── Media elements ─────────────────────────────────────────
    document.querySelectorAll('img,svg').forEach(function (el) {
      if (!isEditableMedia(el, restrict)) return;
      const tag = el.tagName.toLowerCase();
      const xpath = getXPath(el);
      el.setAttribute('data-hm', '1');
      editableMap.set(xpath, el);

      el.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const snap = elSnapshot(el);
        if (swapMode) {
          exitSwapMode();
          window.parent.postMessage(Object.assign({ type: 'HE_SWAP_PICK', xpath: xpath }, snap), window.location.origin);
          return;
        }
        const r = el.getBoundingClientRect();
        window.parent.postMessage(Object.assign({
          type: 'HE_CLICK', xpath: xpath,
          rect: { top: r.top + window.scrollY, left: r.left, w: r.width, h: r.height }
        }, snap), window.location.origin);
      }, false);
    });

    // ── Messages from admin ────────────────────────────────────
    window.addEventListener('message', function (e) {
      if (e.origin !== window.location.origin) return;

      if (e.data.type === 'HE_APPLY') {
        const el = editableMap.get(e.data.xpath);
        if (!el) return;
        if (e.data.text !== undefined) applyText(el, e.data.text);
        if (e.data.color !== undefined) el.style.color = e.data.color || '';
        if (e.data.elStyle !== undefined) el.setAttribute('style', e.data.elStyle);
        if (e.data.src !== undefined && el.tagName.toLowerCase() === 'img') el.src = e.data.src;
        if (e.data.svgContent !== undefined && el.tagName.toLowerCase() === 'svg') {
          const tmp = document.createElement('div');
          tmp.innerHTML = e.data.svgContent;
          const newEl = tmp.firstElementChild;
          if (newEl) { newEl.setAttribute('data-hm', '1'); el.replaceWith(newEl); editableMap.set(e.data.xpath, newEl); }
        }
        return;
      }

      if (e.data.type === 'HE_SWAP_ENTER') { enterSwapMode(); return; }
      if (e.data.type === 'HE_SWAP_EXIT')  { exitSwapMode();  return; }

      if (e.data.type === 'HE_CLICK_XPATH') {
        const el = editableMap.get(e.data.xpath);
        if (el) el.click();
        return;
      }

      if (e.data.type === 'HE_GET_BLOCK_ELEMENTS') {
        const blockEl = findBlockById(e.data.blockId);
        if (!blockEl) return;
        const elements = [];
        const seen = new Set();
        blockEl.querySelectorAll('[data-he],[data-hm]').forEach(function (el) {
          const xpath = getXPath(el);
          if (seen.has(xpath)) return;
          seen.add(xpath);
          const isMedia = el.hasAttribute('data-hm');
          const tag = el.tagName.toLowerCase();
          elements.push({
            xpath: xpath,
            tag: tag,
            type: isMedia ? (tag === 'img' ? 'image' : 'svg') : 'text',
            preview: isMedia ? '' : (getDirectText(el) || el.textContent.trim()).slice(0, 45),
          });
        });
        window.parent.postMessage({
          type: 'HE_BLOCK_ELEMENTS', blockId: e.data.blockId, elements: elements
        }, window.location.origin);
        return;
      }

      if (e.data.type === 'HE_SELECT_BLOCK') {
        document.querySelectorAll('[data-hb]').forEach(function (s) { s.classList.remove('hb-sel'); });
        const el = findBlockById(e.data.blockId);
        if (el) { el.classList.add('hb-sel'); el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
        return;
      }

      if (e.data.type === 'HE_DESELECT_BLOCK') {
        document.querySelectorAll('[data-hb]').forEach(function (s) { s.classList.remove('hb-sel'); });
        return;
      }

      if (e.data.type === 'HE_REORDER') {
        const main = document.querySelector('main');
        if (!main || !Array.isArray(e.data.order)) return;
        e.data.order.forEach(function (bid) {
          const el = findBlockById(bid);
          if (el && el.parentElement === main) main.appendChild(el);
        });
        return;
      }

      if (e.data.type === 'HE_APPLY_BLOCK') {
        const el = findBlockById(e.data.blockId);
        if (!el) return;
        if (e.data.style !== undefined) el.setAttribute('style', e.data.style);
        return;
      }
    });
  }

  // ── Detect admin iframe ───────────────────────────────────────
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
        applyOverrides().then(function () { enableEditMode(e.data.restrict || null); });
      });
    } else {
      applyOverrides();
    }
  });
})();
