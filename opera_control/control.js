(() => {
  'use strict';

  const result = document.getElementById('result');
  const q = new URLSearchParams(location.search);
  const op = q.get('op') || 'status';

  const allowedHosts = [
    /(^|\.)signin\.aws\.amazon\.com$/,
    /(^|\.)console\.aws\.amazon\.com$/,
    /(^|\.)trycloudflare\.com$/,
    /^railway\.com$/,
    /(^|\.)railway\.app$/,
    /^github\.com$/,
    /^example\.com$/
  ];

  const safeText = (v, max = 300) => String(v ?? '').slice(0, max);
  const emit = (payload) => {
    const safe = JSON.stringify(payload, null, 2);
    result.textContent = safe;
    document.title = payload.ok ? 'RIPPLE_CONTROL_OK' : 'RIPPLE_CONTROL_ERROR';
  };

  const assertAllowedUrl = (url) => {
    const u = new URL(url);
    if (u.protocol !== 'https:') throw new Error('Only HTTPS target tabs are allowed');
    if (!allowedHosts.some((rx) => rx.test(u.hostname))) throw new Error('Target host not allowlisted');
    return u;
  };

  async function resolveTarget() {
    const explicit = Number(q.get('tab') || q.get('tabId') || 0);
    if (explicit) {
      const tab = await chrome.tabs.get(explicit);
      assertAllowedUrl(tab.url || '');
      return tab;
    }
    const urlContains = q.get('urlContains');
    if (!urlContains) throw new Error('tab/tabId or urlContains is required');
    const tabs = await chrome.tabs.query({});
    const matches = tabs.filter((t) => (t.url || '').includes(urlContains));
    if (!matches.length) throw new Error('No matching tab');
    const tab = matches.find((t) => t.active) || matches[0];
    assertAllowedUrl(tab.url || '');
    return tab;
  }

  async function runInTab(tabId, func, args = []) {
    const out = await chrome.scripting.executeScript({ target: { tabId }, func, args });
    return out?.[0]?.result;
  }

  const ops = {
    async status() {
      return { ok: true, op: 'status', capabilities: ['resolve_tab','click_css','click_text','set_value','press_key','get_url'] };
    },

    async resolve_tab() {
      const tab = await resolveTarget();
      const u = assertAllowedUrl(tab.url || '');
      return { ok: true, op, tabId: tab.id, host: u.hostname, path: u.pathname };
    },

    async get_url() {
      const tab = await resolveTarget();
      const u = assertAllowedUrl(tab.url || '');
      return { ok: true, op, tabId: tab.id, host: u.hostname, path: u.pathname, url: u.href };
    },

    async click_css() {
      const tab = await resolveTarget();
      const selector = q.get('selector');
      if (!selector || selector.length > 500) throw new Error('Valid selector required');
      const r = await runInTab(tab.id, (sel) => {
        const el = document.querySelector(sel);
        if (!el) return { found: false };
        el.scrollIntoView({ block: 'center', inline: 'center' });
        el.click();
        return { found: true, tag: el.tagName, text: (el.innerText || el.textContent || '').trim().slice(0, 160) };
      }, [selector]);
      return { ok: !!r?.found, op, tabId: tab.id, result: r };
    },

    async click_text() {
      const tab = await resolveTarget();
      const text = q.get('text');
      if (!text || text.length > 300) throw new Error('Valid text required');
      const r = await runInTab(tab.id, (needle) => {
        const norm = (s) => String(s || '').replace(/\s+/g, ' ').trim().toLowerCase();
        const n = norm(needle);
        const nodes = [...document.querySelectorAll('button,a,[role="button"],[tabindex],div')];
        const exact = nodes.find((el) => norm(el.innerText || el.textContent) === n);
        const contains = nodes.find((el) => norm(el.innerText || el.textContent).includes(n));
        const el = exact || contains;
        if (!el) return { found: false };
        el.scrollIntoView({ block: 'center', inline: 'center' });
        el.click();
        return { found: true, tag: el.tagName, text: (el.innerText || el.textContent || '').trim().slice(0, 160) };
      }, [text]);
      return { ok: !!r?.found, op, tabId: tab.id, result: r };
    },

    async set_value() {
      const tab = await resolveTarget();
      const selector = q.get('selector');
      const value = q.get('value') ?? '';
      if (!selector || selector.length > 500) throw new Error('Valid selector required');
      if (value.length > 20000) throw new Error('Value too long');
      const r = await runInTab(tab.id, (sel, val) => {
        const el = document.querySelector(sel);
        if (!el) return { found: false };
        el.focus();
        const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
        if (setter) setter.call(el, val); else el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return { found: true, tag: el.tagName, valueLength: val.length };
      }, [selector, value]);
      return { ok: !!r?.found, op, tabId: tab.id, result: r };
    },

    async press_key() {
      const tab = await resolveTarget();
      const selector = q.get('selector') || 'body';
      const key = q.get('key') || 'Enter';
      if (selector.length > 500 || key.length > 40) throw new Error('Invalid selector/key');
      const r = await runInTab(tab.id, (sel, k) => {
        const el = document.querySelector(sel);
        if (!el) return { found: false };
        el.focus?.();
        const init = { key: k, code: k === 'Enter' ? 'Enter' : k, bubbles: true, cancelable: true };
        el.dispatchEvent(new KeyboardEvent('keydown', init));
        el.dispatchEvent(new KeyboardEvent('keypress', init));
        el.dispatchEvent(new KeyboardEvent('keyup', init));
        return { found: true, tag: el.tagName, key: k };
      }, [selector, key]);
      return { ok: !!r?.found, op, tabId: tab.id, result: r };
    }
  };

  (async () => {
    try {
      if (!Object.prototype.hasOwnProperty.call(ops, op)) throw new Error('Unsupported operation');
      emit(await ops[op]());
    } catch (e) {
      emit({ ok: false, op: safeText(op, 80), error: safeText(e?.message || e, 300) });
    }
  })();
})();
