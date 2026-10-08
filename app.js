/* ============================================================
   LoungeOS — Interactive Features
   OS Detection, Pricing Toggle, Scroll Animations,
   Mobile Menu, FAQ Accordion
   ============================================================ */

(function () {
  'use strict';

  /* ---------- 1. MOBILE MENU ---------- */
  const menuToggle = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');

  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', function () {
      this.classList.toggle('active');
      navLinks.classList.toggle('open');
      document.body.classList.toggle('menu-open');
    });

    // Close menu when a link is clicked
    navLinks.querySelectorAll('a:not(.nav-dropdown-menu a)').forEach(function (link) {
      link.addEventListener('click', function () {
        menuToggle.classList.remove('active');
        navLinks.classList.remove('open');
        document.body.classList.remove('menu-open');
      });
    });

    // Mobile Dropdown toggle
    const dropdownToggles = document.querySelectorAll('.nav-dropdown-toggle');
    dropdownToggles.forEach(function(dt) {
      dt.addEventListener('click', function(e) {
        if (window.innerWidth <= 1024) {
          e.preventDefault();
          this.parentElement.classList.toggle('active');
        }
      });
    });
  }

  /* ---------- 2. OS DETECTION ---------- */
  var detectedOS = null;
  var selectedOS = null;

  function detectOS() {
    var ua = navigator.userAgent.toLowerCase();
    if (ua.indexOf('mac') !== -1 && ua.indexOf('iphone') === -1 && ua.indexOf('ipad') === -1) {
      return 'mac';
    }
    if (ua.indexOf('win') !== -1) {
      return 'windows';
    }
    return null;
  }

  function updateDownloadCards() {
    var macCard = document.getElementById('downloadMac');
    var winCard = document.getElementById('downloadWin');
    if (!macCard || !winCard) return;

    // Clear states
    macCard.classList.remove('selected', 'recommended');
    winCard.classList.remove('selected', 'recommended');

    // Mark recommended
    if (detectedOS === 'mac') {
      macCard.classList.add('recommended');
    } else if (detectedOS === 'windows') {
      winCard.classList.add('recommended');
    }

    // Mark selected
    var active = selectedOS || detectedOS;
    if (active === 'mac') {
      macCard.classList.add('selected');
    } else if (active === 'windows') {
      winCard.classList.add('selected');
    }
  }

  // Detect OS and apply
  detectedOS = detectOS();
  updateDownloadCards();

  // Interactive card selection
  document.querySelectorAll('.download-card').forEach(function (card) {
    card.addEventListener('click', function (e) {
      // Don't trigger if clicking the download button
      if (e.target.closest('.btn')) return;
      selectedOS = this.dataset.os;
      updateDownloadCards();
    });
  });


  /* ---------- 3. PRICING & LOCALIZATION ---------- */

  // Regional pricing. Per-month prices for the monthly, 6-month and 12-month
  // plans, set by market rather than converted from FCFA. Keep in sync with the
  // price tables on /pricing/, /fr/tarifs/ and the country pages, and with the
  // amounts charged at account.loungeos.app/checkout.
  var REGIONAL_PRICING = {
    XAF: { monthly: 30000, six: 25000, yearly: 20000, region: 'fcfa' },
    XOF: { monthly: 30000, six: 25000, yearly: 20000, region: 'fcfa' },
    NGN: { monthly: 35000, six: 30000, yearly: 25000, region: 'ng' },
    GHS: { monthly: 299, six: 249, yearly: 199, region: 'gh' },
    ZAR: { monthly: 599, six: 499, yearly: 449, region: 'za' },
    EUR: { monthly: 45, six: 40, yearly: 35, region: 'eu' },
    GBP: { monthly: 39, six: 35, yearly: 31, region: 'uk' },
    USD: { monthly: 49, six: 44, yearly: 39, region: 'global' },
    CAD: { monthly: 65, six: 59, yearly: 52, region: 'global' },
    AUD: { monthly: 75, six: 67, yearly: 59, region: 'global' },
    AED: { monthly: 179, six: 159, yearly: 139, region: 'global' }
  };
  // Countries without a fixed local table: priced from a US$ tier, shown in the
  // visitor's currency at the day's exchange rate.
  var USD_TIERS = {
    global: { monthly: 49, six: 44, yearly: 39 },
    emerging: { monthly: 25, six: 21, yearly: 17 }
  };
  var GLOBAL_TIER_COUNTRIES = ['US', 'CA', 'GB', 'IE', 'FR', 'DE', 'NL', 'BE', 'LU', 'AT', 'CH', 'IT', 'ES', 'PT',
    'GR', 'CY', 'MT', 'SI', 'SK', 'CZ', 'PL', 'HR', 'EE', 'LV', 'LT', 'FI', 'SE', 'NO', 'DK', 'IS', 'AU', 'NZ',
    'JP', 'KR', 'SG', 'HK', 'TW', 'IL', 'AE', 'SA', 'QA', 'KW', 'BH', 'OM'];

  var isBot = /bot|crawl|spider|slurp|bingpreview|mediapartners|facebookexternalhit|embedly|lighthouse|headless|gptbot|claude|perplexity|chatgpt/i.test(navigator.userAgent);
  var pagePath = window.location.pathname;
  var pageLang = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var currencyFormatter = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF', maximumFractionDigits: 0 });
  var activePrices = { monthly: 30000, six: 25000, yearly: 20000 };
  var activeRegion = 'fcfa';
  var activeCurrency = 'XAF';

  function niceRound(v) {
    if (v < 100) return Math.round(v);
    var step = Math.pow(10, Math.floor(Math.log10(v)) - 1) / 2;
    return Math.round(v / step) * step;
  }

  function formatPrice(amount) {
    return currencyFormatter.format(amount);
  }

  function planOf(el, fallbackByBase) {
    return el.dataset.plan || fallbackByBase[el.dataset.basePrice || el.dataset.baseTotal || el.dataset.baseSavings];
  }

  function updatePricing() {
    var p = activePrices;
    var totals = { six: p.six * 6, yearly: p.yearly * 12 };
    var savings = { six: p.monthly * 6 - totals.six, yearly: p.monthly * 12 - totals.yearly };

    document.querySelectorAll('.price[data-base-price]').forEach(function (el) {
      var plan = planOf(el, { '30000': 'monthly', '25000': 'six', '20000': 'yearly' });
      if (p[plan] !== undefined) el.textContent = formatPrice(p[plan]);
    });
    document.querySelectorAll('.price-total[data-base-total]').forEach(function (el) {
      var plan = planOf(el, { '150000': 'six', '240000': 'yearly' });
      if (totals[plan] !== undefined) el.textContent = formatPrice(totals[plan]) + ' ' + (el.dataset.totalLabel || 'total');
    });
    document.querySelectorAll('.price-savings[data-base-savings]').forEach(function (el) {
      var plan = planOf(el, { '30000': 'six', '120000': 'yearly' });
      if (savings[plan] === undefined) return;
      var freeMonthsText = el.dataset.freeMonths || '';
      el.textContent = (el.dataset.saveLabel || 'You save') + ' ' + formatPrice(savings[plan]) + (freeMonthsText ? ' (' + freeMonthsText + ')' : '');
    });
    // Pass the visitor's region to checkout so it can charge the matching price.
    document.querySelectorAll('a[data-checkout]').forEach(function (a) {
      try {
        var u = new URL(a.href);
        u.searchParams.set('region', activeRegion);
        u.searchParams.set('currency', activeCurrency);
        a.href = u.toString();
      } catch (e) {}
    });
  }

  function applyRegionalPricing(geo) {
    var cur = geo.currency;
    var country = geo.country_code;
    if (!cur) return;
    var locale = navigator.language || 'en-US';
    var table = REGIONAL_PRICING[cur];
    function setFormatter(c) {
      var loc = c === 'XAF' || c === 'XOF' ? 'fr-FR' : locale;
      // narrowSymbol shows ₦, GH₵, R, € instead of NGN, GHS, ZAR when the browser
      // language doesn't match the currency's country; older browsers fall back.
      try {
        currencyFormatter = new Intl.NumberFormat(loc, { style: 'currency', currency: c, currencyDisplay: 'narrowSymbol', maximumFractionDigits: 0 });
      } catch (e) {
        try { currencyFormatter = new Intl.NumberFormat(loc, { style: 'currency', currency: c, maximumFractionDigits: 0 }); } catch (e2) {}
      }
    }
    if (table) {
      activePrices = table; activeRegion = table.region; activeCurrency = cur;
      setFormatter(cur);
      updatePricing();
      return;
    }
    var tierName = GLOBAL_TIER_COUNTRIES.indexOf(country) > -1 ? 'global' : 'emerging';
    var tier = USD_TIERS[tierName];
    fetch('https://open.er-api.com/v6/latest/USD')
      .then(function (res) { return res.json(); })
      .then(function (rates) {
        var r = rates && rates.rates && rates.rates[cur];
        if (!r) { cur = 'USD'; r = 1; }
        activePrices = { monthly: niceRound(tier.monthly * r), six: niceRound(tier.six * r), yearly: niceRound(tier.yearly * r) };
        activeRegion = tierName; activeCurrency = cur;
        setFormatter(cur);
        updatePricing();
      })
      .catch(function (e) { console.error('Exchange rate error:', e); });
  }

  // Initialize pricing formatting (FCFA until the visitor's region is known)
  updatePricing();

  // Multilingual meta descriptions for the machine-translated homepage only
  const seoData = {
      'fr': { desc: "LoungeOS est un logiciel de caisse hors ligne pour restaurants, bars et lounges : commandes, écrans cuisine, stocks, Mobile Money et comptabilité. Essai gratuit de 30 jours." },
      'es': { desc: "LoungeOS es un sistema POS sin conexión para restaurantes, bares y lounges: pedidos, pantallas de cocina, inventario y contabilidad. Prueba gratuita de 30 días." },
      'de': { desc: "LoungeOS ist ein Offline-Kassensystem für Restaurants, Bars und Lounges: Bestellungen, Küchendisplays, Lager und Buchhaltung. 30 Tage kostenlos testen." },
      'zh-CN': { desc: "LoungeOS是适用于餐厅、酒吧和休闲吧的离线POS系统：点餐、厨房显示屏、库存和会计。30天免费试用。" },
      'ar': { desc: "LoungeOS نظام نقاط بيع يعمل بدون إنترنت للمطاعم والحانات: الطلبات وشاشات المطبخ والمخزون والمحاسبة. تجربة مجانية لمدة 30 يومًا." },
      'hi': { desc: "LoungeOS रेस्तरां, बार और लाउंज के लिए ऑफ़लाइन POS है: ऑर्डर, किचन डिस्प्ले, इन्वेंट्री और अकाउंटिंग। 30 दिन का मुफ्त ट्रायल।" },
      'pt': { desc: "LoungeOS é um PDV offline para restaurantes, bares e lounges: pedidos, telas de cozinha, estoque e contabilidade. Teste grátis de 30 dias." },
      'ru': { desc: "LoungeOS — офлайн POS-система для ресторанов, баров и лаунжей: заказы, кухонные экраны, склад и учёт. 30 дней бесплатно." },
      'ja': { desc: "LoungeOSはレストラン、バー、ラウンジ向けのオフラインPOSです。注文、キッチンディスプレイ、在庫、会計。30日間無料トライアル。" }
  };

  function updateDynamicSEO(lang) {
      if (pagePath !== '/' && pagePath !== '/index.html') return;
      if (!seoData[lang]) return;
      document.documentElement.lang = lang;
      var metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc) metaDesc.content = seoData[lang].desc;
      var ogDesc = document.querySelector('meta[property="og:description"]');
      if (ogDesc) ogDesc.content = seoData[lang].desc;
  }

  /* ---------- 3b. LOCATION & LANGUAGE SUGGESTIONS ---------- */
  var COUNTRY_BANNERS = {
    CM: { en: ['Running a venue in Cameroon? FCFA prices, MTN MoMo & Orange Money setup', '/cameroon/'],
          fr: ['Vous êtes au Cameroun ? Tarifs en FCFA, MTN MoMo et Orange Money', '/fr/cameroun/'] },
    NG: { en: ['In Nigeria? See naira pricing and local setup', '/nigeria/'] },
    GH: { en: ['In Ghana? See cedi pricing and MoMo setup', '/ghana/'] },
    ZA: { en: ['In South Africa? See rand pricing and load-shedding setup', '/south-africa/'] },
    CI: { fr: ["Vous êtes en Côte d'Ivoire ? LoungeOS pour maquis, restaurants et lounges", '/fr/cote-divoire/'] },
    SN: { fr: ['Vous êtes au Sénégal ? LoungeOS pour restaurants et lounges', '/fr/senegal/'] }
  };
  var FRANCOPHONE = ['CM', 'CI', 'SN', 'GA', 'CG', 'CD', 'TD', 'CF', 'GQ', 'BJ', 'TG', 'BF', 'ML', 'NE', 'GN',
    'MG', 'DJ', 'KM', 'BI', 'RW', 'MR', 'FR', 'BE', 'CH', 'LU', 'MC', 'HT'];

  function storageGet(store, key) { try { return window[store].getItem(key); } catch (e) { return null; } }
  function storageSet(store, key, val) { try { window[store].setItem(key, val); } catch (e) {} }

  function showBanner(text, href, linkText) {
    if (document.querySelector('.locale-banner')) return;
    var b = document.createElement('div');
    b.className = 'locale-banner';
    b.setAttribute('role', 'region');
    b.setAttribute('aria-label', pageLang === 'fr' ? 'Suggestion' : 'Suggestion for your location');
    var span = document.createElement('span');
    span.textContent = text;
    var a = document.createElement('a');
    a.href = href;
    a.textContent = linkText;
    var close = document.createElement('button');
    close.type = 'button';
    close.setAttribute('aria-label', pageLang === 'fr' ? 'Fermer' : 'Close');
    close.textContent = '×';
    close.addEventListener('click', function () {
      b.remove();
      storageSet('localStorage', 'loBannerDismissed', String(Date.now()));
    });
    b.appendChild(span); b.appendChild(a); b.appendChild(close);
    document.body.appendChild(b);
  }

  function suggestLocale(geo) {
    var dismissed = parseInt(storageGet('localStorage', 'loBannerDismissed') || '0', 10);
    if (dismissed && Date.now() - dismissed < 7 * 864e5) return false;
    var country = geo.country_code;
    var browserLang = (navigator.language || '').slice(0, 2).toLowerCase();
    var wantsFr = browserLang === 'fr' || (FRANCOPHONE.indexOf(country) > -1 && browserLang !== 'en');
    var frAlt = document.querySelector('link[rel="alternate"][hreflang="fr"]');
    if (pageLang === 'en' && wantsFr && frAlt) {
      showBanner('Ce site existe en français.', frAlt.getAttribute('href'), 'Voir la version française');
      return true;
    }
    var landing = /^\/(index\.html)?$|^\/fr\/$|^\/pricing\/|^\/fr\/tarifs\/|^\/features\/$|^\/fr\/fonctionnalites\/|^\/download\/|^\/fr\/telecharger\//.test(pagePath);
    if (!landing) return false;
    var cfg = COUNTRY_BANNERS[country];
    var pick = cfg && (pageLang === 'fr' ? (cfg.fr || cfg.en) : (cfg.en || cfg.fr));
    if (!pick && geo.continent_code === 'AF') {
      pick = pageLang === 'fr' ? ["En Afrique ? Tarifs locaux et Mobile Money", '/fr/afrique/'] : ['In Africa? See local pricing and mobile money setup', '/africa/'];
    }
    if (pick && pick[1] !== pagePath) {
      showBanner(pick[0], pick[1], pageLang === 'fr' ? 'Voir →' : 'See →');
      return true;
    }
    return false;
  }

  function onGeo(data) {
    applyRegionalPricing(data);

    // Auto-language: real French pages first, machine translation otherwise
    // (always overridden by an explicit ?lang= parameter).
    var primaryLang = paramLang;
    if (!primaryLang && data.languages) {
      primaryLang = data.languages.split(',')[0].split('-')[0];
      if (primaryLang === 'zh') primaryLang = 'zh-CN';
    }
    var suggested = suggestLocale(data);
    var hasRealFrench = !!document.querySelector('link[rel="alternate"][hreflang="fr"]');
    var autoAllowed = paramLang || (!document.documentElement.hasAttribute('data-no-autolang') &&
      !(primaryLang === 'fr' && (hasRealFrench || suggested)));

    var supportedLangs = ['en', 'fr', 'es', 'de', 'zh-CN', 'ar', 'hi', 'pt', 'ru', 'ja'];
    if (autoAllowed && primaryLang && primaryLang !== pageLang && supportedLangs.includes(primaryLang)) {
      var selectField = document.getElementById("customLangSelect");
      if (selectField && selectField.value !== primaryLang && (!storageGet('sessionStorage', 'langAutoSet') || paramLang)) {
        selectField.value = primaryLang;
        storageSet('sessionStorage', 'langAutoSet', 'true');
        // Wait for Google Translate script to be ready
        setTimeout(function() {
          if (typeof changeLanguage === 'function') {
            changeLanguage(primaryLang);
            updateDynamicSEO(primaryLang);
          }
        }, 1000);
      }
    }
  }

  // Auto-detect location for currency, language and local pages.
  // Skipped for crawlers so search engines index each page as published.
  var urlParams = new URLSearchParams(window.location.search);
  var paramLang = urlParams.get('lang');

  if (!isBot) {
    var cachedGeo = storageGet('sessionStorage', 'loGeo');
    if (cachedGeo) {
      try { onGeo(JSON.parse(cachedGeo)); } catch (e) {}
    } else {
      fetch('https://ipapi.co/json/')
        .then(function(response) { return response.json(); })
        .then(function(data) {
          if (data && !data.error) {
            storageSet('sessionStorage', 'loGeo', JSON.stringify({
              currency: data.currency, country_code: data.country_code,
              continent_code: data.continent_code, languages: data.languages
            }));
            onGeo(data);
          }
        })
        .catch(function(e) { console.error("Location detection error:", e); });
    }
  }


  /* ---------- 4. FAQ ACCORDION ---------- */
  document.querySelectorAll('.faq-question').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = this.parentElement;
      var wasOpen = item.classList.contains('open');

      // Close all
      document.querySelectorAll('.faq-item').forEach(function (faq) {
        faq.classList.remove('open');
      });

      // Toggle current
      if (!wasOpen) {
        item.classList.add('open');
      }
    });
  });


  /* ---------- 5. SCROLL ANIMATIONS ---------- */
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
      }
    );

    document.querySelectorAll('.animate-on-scroll').forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback: show everything
    document.querySelectorAll('.animate-on-scroll').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }


  /* ---------- 6. SMOOTH SCROLL FOR ANCHOR LINKS ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#') return;
      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        var navHeight = document.querySelector('.navbar').offsetHeight || 56;
        var top = target.getBoundingClientRect().top + window.pageYOffset - navHeight;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });

  /* ---------- 7. LIGHTBOX FOR SCREENSHOTS ---------- */
  const modal = document.getElementById('lightboxModal');
  const lightboxImg = document.getElementById('lightboxImage');
  const btnClose = document.getElementById('lightboxClose');
  const btnNext = document.getElementById('lightboxNext');
  const btnPrev = document.getElementById('lightboxPrev');

  if (modal && lightboxImg) {
    // Collect all unique images
    const images = Array.from(document.querySelectorAll('.carousel-track .carousel-img'));
    
    // We only need the first half (since we duplicated them for the infinite loop)
    const uniqueImages = images.slice(0, images.length / 2).map(img => img.dataset.full || img.src);
    let currentIndex = 0;

    function openModal(index) {
      currentIndex = index;
      lightboxImg.src = uniqueImages[currentIndex];
      modal.showModal();
    }

    function closeModal() {
      modal.close();
      lightboxImg.src = '';
    }

    function showNext() {
      currentIndex = (currentIndex + 1) % uniqueImages.length;
      lightboxImg.src = uniqueImages[currentIndex];
    }

    function showPrev() {
      currentIndex = (currentIndex - 1 + uniqueImages.length) % uniqueImages.length;
      lightboxImg.src = uniqueImages[currentIndex];
    }

    // Attach click events to all images in the carousel
    images.forEach((img, idx) => {
      img.addEventListener('click', () => {
        // Map the clicked image index back to the unique array index
        const mappedIndex = idx % uniqueImages.length;
        openModal(mappedIndex);
      });
    });

    btnClose.addEventListener('click', closeModal);
    btnNext.addEventListener('click', showNext);
    btnPrev.addEventListener('click', showPrev);

    // Close when clicking outside the image
    modal.addEventListener('click', (e) => {
      if (e.target === modal || e.target.classList.contains('lightbox-content')) {
        closeModal();
      }
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (!modal.open) return;
      if (e.key === 'Escape') closeModal();
      if (e.key === 'ArrowRight') showNext();
      if (e.key === 'ArrowLeft') showPrev();
    });
  }

})();

/* ---------- 8. CUSTOM GOOGLE TRANSLATE ---------- */
window.changeLanguage = function(lang) {
    var selectField = document.querySelector(".goog-te-combo");
    if (selectField) {
        selectField.value = lang;
        selectField.dispatchEvent(new Event('change'));
        // Aggressively remove the Google Translate banner after translation
        setTimeout(function() { hideGoogleTranslateBanner(); }, 100);
        setTimeout(function() { hideGoogleTranslateBanner(); }, 500);
        setTimeout(function() { hideGoogleTranslateBanner(); }, 1500);
    } else {
        // If google translate script is still loading, try again
        setTimeout(function() {
            window.changeLanguage(lang);
        }, 500);
    }
};

function hideGoogleTranslateBanner() {
    // Remove the banner frame
    var banners = document.querySelectorAll('.skiptranslate');
    banners.forEach(function(el) {
        if (el.tagName === 'DIV' || el.tagName === 'IFRAME') {
            el.style.display = 'none';
            el.style.height = '0';
            el.style.visibility = 'hidden';
        }
    });
    // Also target iframes injected by Google
    var iframes = document.querySelectorAll('iframe.goog-te-banner-frame, iframe.goog-te-menu-frame');
    iframes.forEach(function(iframe) {
        iframe.style.display = 'none';
        iframe.style.height = '0';
        iframe.style.visibility = 'hidden';
    });
    // Fix body position that Google Translate shifts
    document.body.style.top = '0px';
    document.body.style.position = 'static';
}

// Run banner cleanup on page load and continuously watch for it
var gtCleanupScheduled = false;
var gtBannerObserver = new MutationObserver(function() {
    if (gtCleanupScheduled) return;
    gtCleanupScheduled = true;
    requestAnimationFrame(function() {
        gtCleanupScheduled = false;
        hideGoogleTranslateBanner();
    });
});
gtBannerObserver.observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style'] });

// --- Clerk Authentication Session Management ---
(function() {
  const clerkPubKey = 'pk_test_cmlnaHQtbWFybW9zZXQtMjYuY2xlcmsuYWNjb3VudHMuZGV2JA';
  
  const script = document.createElement('script');
  script.setAttribute('data-clerk-publishable-key', clerkPubKey);
  script.async = true;
  script.src = 'https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js';
  script.crossOrigin = 'anonymous';
  
  script.onload = async () => {
    try {
      await window.Clerk.load();
      if (window.Clerk.user) {
        // User is signed in, update all CTA buttons to "Go to Dashboard"
        const ctas = document.querySelectorAll('a.btn, button.btn, a#navCtaBtn, a#heroCtaBtn, a#footerCtaBtn');
        ctas.forEach(btn => {
          const text = btn.innerText.toLowerCase();
          if (text.includes('start free trial') || text.includes('get started') || text.includes('sign up')) {
            // Keep the icon if it exists
            const icon = btn.querySelector('svg');
            btn.innerText = 'Go to Dashboard';
            if (icon) btn.appendChild(icon);
            
            // Only update href if it's an anchor
            if (btn.tagName === 'A') {
              btn.href = 'https://account.loungeos.app/dashboard';
            }
          }
        });
      }
    } catch (err) {
      console.error('Error loading Clerk:', err);
    }
  };
  
  function loadClerk() { document.head.appendChild(script); }
  if (document.readyState === 'complete') {
    setTimeout(loadClerk, 1500);
  } else {
    window.addEventListener('load', function () { setTimeout(loadClerk, 1500); });
  }
})();
