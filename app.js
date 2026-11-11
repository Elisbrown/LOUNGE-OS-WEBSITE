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
  // Download cards carry data-os: windows, mac-apple-silicon, mac-intel, android
  // or web. The card for the visitor's system is marked recommended and selected.
  var detectedOS = detectOS();
  var selectedOS = null;

  function detectOS() {
    var ua = navigator.userAgent || '';
    var platform = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '';
    if (/android/i.test(ua)) return 'android';
    // iPhone, iPad and iPod (iPadOS reports itself as a Mac with a touch screen) use the web app
    if (/iphone|ipad|ipod/i.test(ua) || (/^mac/i.test(platform) && navigator.maxTouchPoints > 1)) return 'web';
    if (/^win/i.test(platform) || /windows nt/i.test(ua)) return 'windows';
    // Browsers report every Mac as Intel, so the chip is unknown here: 'mac'
    // recommends both Mac cards (refined below where the browser tells the chip).
    if (/^mac/i.test(platform) || /macintosh|mac os x/i.test(ua)) return 'mac';
    return 'web';
  }

  function updateDownloadCards() {
    var cards = Array.prototype.slice.call(document.querySelectorAll('.download-card[data-os]'));
    if (!cards.length) return;
    var active = selectedOS || detectedOS;
    // 'mac' (chip unknown) matches both Mac cards
    function matches(os, target) { return os === target || (target === 'mac' && os.indexOf('mac-') === 0); }
    var hasActive = cards.some(function (c) { return matches(c.dataset.os, active); });
    cards.forEach(function (card) {
      card.classList.toggle('recommended', matches(card.dataset.os, detectedOS));
      // Keep the page's default selection when no card matches
      if (hasActive) card.classList.toggle('selected', matches(card.dataset.os, active));
    });
  }

  updateDownloadCards();

  // Chromium browsers can tell an Intel Mac from an Apple Silicon one
  if (detectedOS === 'mac' && navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
    navigator.userAgentData.getHighEntropyValues(['architecture']).then(function (v) {
      if (!v) return;
      detectedOS = v.architecture === 'x86' ? 'mac-intel' : (v.architecture === 'arm' ? 'mac-apple-silicon' : 'mac');
      updateDownloadCards();
    }).catch(function () {});
  }

  // Interactive card selection
  document.querySelectorAll('.download-card[data-os]').forEach(function (card) {
    card.addEventListener('click', function (e) {
      // Don't trigger if clicking the download button
      if (e.target.closest('.btn')) return;
      selectedOS = this.dataset.os;
      updateDownloadCards();
    });
  });


  /* ---------- 3. PRICING & LOCALIZATION ---------- */

  // Plan prices, the same features in both currencies. Visitors in Cameroon see
  // FCFA, everyone else US$. Yearly = 10 months (2 months free). Keep in sync with
  // PRICES in scripts/site/build.py and the price cards in /index.html.
  var PLANS = {
    starter: { USD: { monthly: 10, yearly: 100 }, XAF: { monthly: 6000, yearly: 60000 } },
    business: { USD: { monthly: 25, yearly: 250 }, XAF: { monthly: 15000, yearly: 150000 } },
    pro: { USD: { monthly: 50, yearly: 500 }, XAF: { monthly: 30000, yearly: 300000 } }
  };

  var isBot = /bot|crawl|spider|slurp|bingpreview|mediapartners|facebookexternalhit|embedly|lighthouse|headless|gptbot|claude|perplexity|chatgpt/i.test(navigator.userAgent);
  var pagePath = window.location.pathname;
  var pageLang = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var isFr = pageLang.indexOf('fr') === 0;
  var PRICE_TEXT = isFr
    ? { monthly: '/ mois', yearly: '/ an', save: 'Vous économisez {amount}' }
    : { monthly: '/ month', yearly: '/ year', save: 'You save {amount}' };

  // Until the visitor's country is known, guess Cameroon from the device's time zone
  function inCameroonTimeZone() {
    try { return Intl.DateTimeFormat().resolvedOptions().timeZone === 'Africa/Douala'; } catch (e) { return false; }
  }
  var activeCurrency = !isBot && inCameroonTimeZone() ? 'XAF' : 'USD';
  var activeBilling = 'monthly';

  // US$10 / 6,000 FCFA in English, 10 $ US / 6 000 FCFA in French (same as build.py)
  function formatPrice(amount, currency) {
    var n = String(amount).replace(/\B(?=(\d{3})+(?!\d))/g, isFr ? '\u202f' : ',');
    if (currency === 'XAF') return n + '\u00a0FCFA';
    return isFr ? n + '\u00a0$\u00a0US' : 'US$' + n;
  }

  // Cards: .price-card[data-plan] with .price, .price-period and an optional
  // .price-savings (shown for yearly billing).
  function updatePricing() {
    document.querySelectorAll('.price-card[data-plan]').forEach(function (card) {
      var plan = PLANS[card.dataset.plan];
      if (!plan) return;
      var p = plan[activeCurrency];
      var price = card.querySelector('.price');
      var period = card.querySelector('.price-period');
      var savings = card.querySelector('.price-savings');
      if (price) price.textContent = formatPrice(p[activeBilling], activeCurrency);
      if (period) period.textContent = PRICE_TEXT[activeBilling];
      if (savings) {
        savings.textContent = PRICE_TEXT.save.replace('{amount}', formatPrice(p.monthly * 12 - p.yearly, activeCurrency));
        savings.hidden = activeBilling !== 'yearly';
      }
    });
    // Billing toggle: a .toggle-switch button between [data-billing] labels
    document.querySelectorAll('.billing-toggle').forEach(function (toggle) {
      var yearly = activeBilling === 'yearly';
      var sw = toggle.querySelector('.toggle-switch');
      if (sw) {
        sw.classList.toggle('active', yearly);
        sw.setAttribute('aria-checked', yearly ? 'true' : 'false');
      }
      toggle.querySelectorAll('[data-billing]').forEach(function (label) {
        label.classList.toggle('active', label.dataset.billing === activeBilling);
      });
    });
  }

  function setBilling(billing) {
    if (billing !== 'monthly' && billing !== 'yearly') return;
    activeBilling = billing;
    updatePricing();
  }

  document.querySelectorAll('.billing-toggle').forEach(function (toggle) {
    var sw = toggle.querySelector('.toggle-switch');
    if (sw) {
      sw.addEventListener('click', function () {
        setBilling(activeBilling === 'yearly' ? 'monthly' : 'yearly');
      });
    }
    toggle.querySelectorAll('[data-billing]').forEach(function (label) {
      label.addEventListener('click', function () { setBilling(label.dataset.billing); });
    });
  });

  function applyCountryPricing(geo) {
    if (!geo || !geo.country_code) return;
    var currency = geo.country_code === 'CM' ? 'XAF' : 'USD';
    if (currency === activeCurrency) return;
    activeCurrency = currency;
    updatePricing();
  }

  updatePricing();

  // Multilingual meta descriptions for the machine-translated homepage only
  const seoData = {
      'fr': { desc: "LoungeOS est un logiciel de caisse et de gestion pour restaurants, bars, hôtels, boutiques et supermarchés : ventes, stocks, dépenses, comptabilité et Mobile Money. Essai gratuit de 14 jours." },
      'es': { desc: "LoungeOS es un sistema de punto de venta y gestión para restaurantes, bares, hoteles, tiendas y supermercados: ventas, inventario, gastos y contabilidad. Prueba gratuita de 14 días." },
      'de': { desc: "LoungeOS ist ein Kassen- und Verwaltungssystem für Restaurants, Bars, Hotels, Geschäfte und Supermärkte: Verkauf, Lager, Ausgaben und Buchhaltung. 14 Tage kostenlos testen." },
      'zh-CN': { desc: "LoungeOS是适用于餐厅、酒吧、酒店、零售店和超市的收银与管理系统：销售、库存、支出和会计。14天免费试用。" },
      'ar': { desc: "LoungeOS نظام نقاط بيع وإدارة للمطاعم والحانات والفنادق والمتاجر والسوبرماركت: المبيعات والمخزون والمصروفات والمحاسبة. تجربة مجانية لمدة 14 يومًا." },
      'hi': { desc: "LoungeOS रेस्तरां, बार, होटल, दुकानों और सुपरमार्केट के लिए POS और प्रबंधन सिस्टम है: बिक्री, इन्वेंट्री, खर्च और अकाउंटिंग। 14 दिन का मुफ्त ट्रायल।" },
      'pt': { desc: "LoungeOS é um sistema de PDV e gestão para restaurantes, bares, hotéis, lojas e supermercados: vendas, estoque, despesas e contabilidade. Teste grátis de 14 dias." },
      'ru': { desc: "LoungeOS — кассовая система и система управления для ресторанов, баров, отелей, магазинов и супермаркетов: продажи, склад, расходы и учёт. 14 дней бесплатно." },
      'ja': { desc: "LoungeOSはレストラン、バー、ホテル、小売店、スーパー向けのPOS・管理システムです。販売、在庫、経費、会計。14日間無料トライアル。" }
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
    CM: { en: ['Running a business in Cameroon? FCFA prices, MTN MoMo and Orange Money', '/cameroon/'],
          fr: ['Vous êtes au Cameroun ? Tarifs en FCFA, MTN MoMo et Orange Money', '/fr/cameroun/'] },
    NG: { en: ['In Nigeria? See how LoungeOS works for Nigerian businesses', '/nigeria/'] },
    GH: { en: ['In Ghana? See how LoungeOS records MoMo payments', '/ghana/'] },
    ZA: { en: ['In South Africa? See how LoungeOS handles load-shedding', '/south-africa/'] },
    CI: { fr: ["Vous êtes en Côte d'Ivoire ? LoungeOS pour maquis, restaurants, boutiques et supermarchés", '/fr/cote-divoire/'] },
    SN: { fr: ['Vous êtes au Sénégal ? LoungeOS pour restaurants, boutiques et commerces', '/fr/senegal/'] }
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
    // Wait until the visitor scrolls past the hero, so the banner never covers its buttons
    whenScrolled(function () {
      if (!document.querySelector('.locale-banner')) document.body.appendChild(b);
    });
  }

  function whenScrolled(fn) {
    function past() { return window.scrollY > window.innerHeight * 0.4; }
    if (past()) return fn();
    function onScroll() {
      if (!past()) return;
      window.removeEventListener('scroll', onScroll);
      fn();
    }
    window.addEventListener('scroll', onScroll, { passive: true });
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
    // Not on the pricing pages: they already show the visitor's currency
    var landing = /^\/(index\.html)?$|^\/fr\/$|^\/features\/$|^\/fr\/fonctionnalites\/|^\/download\/|^\/fr\/telecharger\//.test(pagePath);
    if (!landing) return false;
    var cfg = COUNTRY_BANNERS[country];
    var pick = cfg && (pageLang === 'fr' ? (cfg.fr || cfg.en) : (cfg.en || cfg.fr));
    if (!pick && geo.continent_code === 'AF') {
      pick = pageLang === 'fr' ? ['En Afrique ? Mobile Money et vente hors ligne', '/fr/afrique/'] : ['In Africa? See mobile money and offline selling', '/africa/'];
    }
    if (pick && pick[1] !== pagePath) {
      showBanner(pick[0], pick[1], pageLang === 'fr' ? 'Voir →' : 'See →');
      return true;
    }
    return false;
  }

  function onGeo(data) {
    applyCountryPricing(data);

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

  // Detect the visitor's country for the currency (FCFA in Cameroon, US$ elsewhere),
  // the language and local pages.
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
              country_code: data.country_code, continent_code: data.continent_code,
              languages: data.languages
            }));
            onGeo(data);
          }
        })
        // Lookup blocked or unavailable: keep the default currency and language
        .catch(function () {});
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
    if (lang === 'fr') {
        var fr = document.querySelector('link[rel="alternate"][hreflang="fr"]');
        if (fr && fr.href && fr.href !== location.href) { location.href = fr.href; return; }
    }
    if (lang === 'en' && document.documentElement.lang === 'fr') {
        var en = document.querySelector('link[rel="alternate"][hreflang="en"]');
        if (en && en.href) { location.href = en.href; return; }
    }
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

// --- WhatsApp chat button ---
// One button on every page that opens a WhatsApp chat with the LoungeOS team,
// with a first message in the page's language.
(function () {
  if (document.querySelector('.wa-float')) return;
  var fr = (document.documentElement.lang || '').slice(0, 2) === 'fr';
  var text = fr
    ? 'Bonjour, je souhaite en savoir plus sur LoungeOS. (Page : ' + location.pathname + ')'
    : 'Hello, I would like to know more about LoungeOS. (Page: ' + location.pathname + ')';
  var a = document.createElement('a');
  a.className = 'wa-float';
  a.href = 'https://wa.me/237679690703?text=' + encodeURIComponent(text);
  a.target = '_blank';
  a.rel = 'noopener';
  a.setAttribute('aria-label', fr ? 'Discuter avec nous sur WhatsApp' : 'Chat with us on WhatsApp');
  a.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.07-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.08 1.76-.72 2.01-1.42.25-.7.25-1.29.17-1.42-.07-.12-.27-.2-.57-.35zM12.05 21.5h-.01a9.4 9.4 0 0 1-4.8-1.31l-.34-.2-3.57.94.95-3.48-.22-.36a9.43 9.43 0 0 1-1.44-5.02c0-5.21 4.24-9.45 9.46-9.45a9.4 9.4 0 0 1 6.68 2.77 9.39 9.39 0 0 1 2.77 6.69c0 5.21-4.24 9.45-9.46 9.45zm8.04-17.49A11.3 11.3 0 0 0 12.05.67C5.78.67.68 5.77.68 12.04c0 2 .52 3.96 1.52 5.68L.58 23.33l5.74-1.5a11.33 11.33 0 0 0 5.72 1.46h.01c6.27 0 11.37-5.1 11.37-11.37 0-3.04-1.18-5.89-3.33-8.04z"/></svg><span>WhatsApp</span>';
  document.body.appendChild(a);
})();

// --- Lead tracking ---
// Sends a Google Analytics event for each step towards a customer: trial and
// sign-in clicks, app downloads, and contact clicks (email, phone, WhatsApp).
// Mark them as key events in GA4 (Admin > Events) to see them as conversions.
(function () {
  function send(name, params) {
    try { if (typeof window.gtag === 'function') window.gtag('event', name, params); } catch (e) {}
  }
  function where(a) {
    var box = a.closest('section[id], nav, footer, header');
    if (!box) return 'page';
    return box.id || box.tagName.toLowerCase();
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var base = { link_text: (a.textContent || '').trim().slice(0, 60), page_path: location.pathname, placement: where(a) };
    if (/^https:\/\/app\.loungeos\.app/.test(href)) {
      send('start_trial_click', base);
      send('generate_lead', Object.assign({ method: 'trial' }, base));
    } else if (/releases\/(latest\/)?download\//.test(href)) {
      var file = href.split('/').pop();
      send('file_download', Object.assign({ file_name: file, platform: /\.exe$/.test(file) ? 'windows' : /\.dmg$/.test(file) ? 'mac' : /\.apk$/.test(file) ? 'android' : 'other' }, base));
    } else if (/^mailto:/.test(href)) {
      send('contact_click', Object.assign({ method: 'email', contact: href.slice(7).split('?')[0] }, base));
    } else if (/^tel:/.test(href)) {
      send('contact_click', Object.assign({ method: 'phone' }, base));
    } else if (/^https:\/\/(wa\.me|api\.whatsapp\.com)/.test(href)) {
      send('contact_click', Object.assign({ method: 'whatsapp' }, base));
    } else if (/^https:\/\/account\.loungeos\.app/.test(href)) {
      send('account_click', base);
    }
  }, true);
})();
