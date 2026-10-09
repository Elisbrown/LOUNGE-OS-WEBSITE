#!/usr/bin/env node
/* Generates a branded 1200x630 share image (link preview) for every page:
 * the page's screenshot, darkened, with the LoungeOS logo, a category label,
 * the page title and the domain. Output: images/og/<slug>.png (converted to
 * WebP by to_webp.py). scripts/seo_update.py points og:image/twitter:image at them.
 *
 *   npm i -g playwright   (or use an installed one)
 *   node scripts/og/make-og.js && python3 scripts/og/to_webp.py
 *
 * Options: node scripts/og/make-og.js /blog/some-post/  (only those pages)
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = path.join(ROOT, 'images', 'og');
const SKIP_DIRS = new Set(['.git', '.github', 'scripts', 'node_modules', 'images', 'Screenshots']);

// Pages without a hero screenshot get one of these (by slug, else by default)
const FALLBACK_IMAGE = {
  home: 'loungeos-pos-order-screen', fr: 'loungeos-tableau-de-bord-francais', blog: 'loungeos-kitchen-display-system',
  privacy: 'loungeos-activity-log-audit-trail', terms: 'loungeos-staff-management', legal: 'loungeos-receipt-configuration',
  accessibility: 'loungeos-currency-settings', documentation: 'loungeos-kitchen-display-system',
  knowledgebase: 'loungeos-inventory-dashboard', '404': 'loungeos-table-management', default: 'loungeos-pos-order-screen',
};
const LABEL = {
  home: 'Restaurant POS', fr: 'Logiciel de caisse', privacy: 'Legal', terms: 'Legal', legal: 'Legal',
  accessibility: 'Accessibility', documentation: 'Documentation', knowledgebase: 'Knowledge base', '404': 'LoungeOS',
};

function slugFor(url) {
  const p = url.replace(/^https?:\/\/[^/]+/, '').replace(/^\/|\/$/g, '').replace(/\.html$/, '').replace(/\/index$/, '');
  return p ? p.replace(/\//g, '-') : 'home';
}

function decode(s) {
  return s.replace(/&amp;/g, '&').replace(/&#39;|&rsquo;/g, '’').replace(/&quot;/g, '"').replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\s+/g, ' ').trim();
}

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name) && !e.name.startsWith('.')) walk(path.join(dir, e.name), out); }
    else if (e.name.endsWith('.html')) out.push(path.join(dir, e.name));
  }
  return out;
}

function pageData(file) {
  const src = fs.readFileSync(file, 'utf8');
  const m = (re) => { const r = src.match(re); return r ? decode(r[1].replace(/<[^>]+>/g, '')) : ''; };
  const rel = path.relative(ROOT, file).replace(/\\/g, '/');
  const canonical = m(/<link\s+rel="canonical"\s+href="([^"]+)"/) || '/' + rel.replace(/index\.html$/, '');
  const slug = slugFor(canonical);
  const lang = m(/<html\s+lang="([^"]+)"/) || 'en';
  const hero = (src.match(/<header class="page-hero">([\s\S]*?)<\/header>/) || [])[1] || '';
  const article = (src.match(/<article[\s\S]*?<figure>([\s\S]*?)<\/figure>/) || [])[1] || '';
  const img = ((hero + article).match(/\/images\/screens\/(loungeos-[a-z-]+?)(?:-800)?\.webp/) || [])[1]
    || FALLBACK_IMAGE[slug] || FALLBACK_IMAGE.default;
  let title = m(/<h1[^>]*>([\s\S]*?)<\/h1>/) || m(/<meta\s+property="og:title"\s+content="([^"]*)"/) || m(/<title>([^<]*)/);
  const label = LABEL[slug] || m(/<header class="page-hero">[\s\S]*?<p class="section-label">([\s\S]*?)<\/p>/) || 'LoungeOS';
  const isBlog = /^(fr-)?blog-/.test(slug);
  return { file: rel, slug, lang, img, title, label: isBlog && !/blog/i.test(label) ? (lang === 'fr' ? 'Blog · ' : 'Blog · ') + label : label };
}

function b64(file, type) { return `data:${type};base64,` + fs.readFileSync(file).toString('base64'); }

function template(d) {
  const bg = b64(path.join(ROOT, 'images', 'screens', d.img + '.webp'), 'image/webp');
  const logo = b64(path.join(ROOT, 'images', 'logo', 'loungeos-logo-white.svg'), 'image/svg+xml');
  const fr = d.lang.startsWith('fr');
  const tagline = fr ? 'Caisse hors ligne · restaurants, bars, lounges' : 'Offline POS · restaurants, bars, lounges';
  const footer = fr ? 'Essai gratuit 30 jours · Fonctionne sans internet · Conçu au Cameroun'
                    : '30-day free trial · Works without internet · Made in Cameroon';
  const len = d.title.length;
  const size = len > 95 ? 46 : len > 70 ? 52 : len > 48 ? 60 : 68;
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&display=block" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1200px;height:630px;overflow:hidden;font-family:Poppins,Arial,sans-serif}
.card{position:relative;width:1200px;height:630px;background:#0b0b0c url(${bg}) right center/cover no-repeat}
.shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(8,8,10,.94) 0%,rgba(8,8,10,.86) 48%,rgba(8,8,10,.55) 100%)}
.inner{position:absolute;inset:0;padding:54px 64px 0;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:22px}
.brand img{height:46px}
.brand span{color:rgba(255,255,255,.72);font-size:17px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;border-left:1px solid rgba(255,255,255,.28);padding-left:22px}
.label{margin-top:58px;align-self:flex-start;background:#ff0013;color:#fff;font-weight:700;font-size:19px;letter-spacing:.12em;text-transform:uppercase;padding:7px 16px;border-radius:4px}
h1{margin-top:26px;color:#fff;font-weight:800;font-size:${size}px;line-height:1.12;letter-spacing:-.015em;max-width:1000px;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.foot{position:absolute;left:64px;right:64px;bottom:40px;color:rgba(255,255,255,.85);font-size:20px;font-weight:500}
.foot b{color:#fff;font-weight:700}
.bar{position:absolute;left:0;right:0;bottom:0;height:10px;background:#ff0013}
</style></head><body><div class="card"><div class="shade"></div><div class="inner">
<div class="brand"><img src="${logo}" alt=""><span>${esc(tagline)}</span></div>
<div class="label">${esc(d.label)}</div>
<h1>${esc(d.title)}</h1>
</div><div class="foot"><b>loungeos.app</b> &nbsp;·&nbsp; ${esc(footer)}</div><div class="bar"></div></div></body></html>`;
}

(async () => {
  const only = process.argv.slice(2);
  fs.mkdirSync(OUT, { recursive: true });
  let pages = walk(ROOT).map(pageData);
  if (only.length) pages = pages.filter((p) => only.some((u) => slugFor(u) === p.slug));
  const exe = process.env.CHROMIUM_PATH || (fs.existsSync('/opt/pw-browsers/chromium-1194/chrome-linux/chrome') ? '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' : undefined);
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  for (const d of pages) {
    await page.setContent(template(d), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(OUT, d.slug + '.png') });
    process.stdout.write('.');
  }
  fs.writeFileSync(path.join(OUT, 'pages.json'), JSON.stringify(pages, null, 1));
  await browser.close();
  console.log(`\n${pages.length} share images`);
})();
