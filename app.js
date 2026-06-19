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
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        menuToggle.classList.remove('active');
        navLinks.classList.remove('open');
        document.body.classList.remove('menu-open');
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
  var billingToggle = document.getElementById('billingToggle');
  var monthlyLabel = document.getElementById('monthlyLabel');
  var yearlyLabel = document.getElementById('yearlyLabel');
  var yearlyBadge = document.getElementById('yearlyBadge');
  var isYearly = false;

  var userCurrency = 'XAF';
  var exchangeRate = 1;
  var currencyFormatter = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF', maximumFractionDigits: 0 });

  function formatPrice(amount) {
      return currencyFormatter.format(amount * exchangeRate);
  }

  function updatePricing() {
    if (billingToggle) {
        billingToggle.classList.toggle('active', isYearly);
        monthlyLabel.classList.toggle('active', !isYearly);
        yearlyLabel.classList.toggle('active', isYearly);
        yearlyBadge.style.opacity = isYearly ? '1' : '0';
    }

    // Update price displays
    document.querySelectorAll('.price[data-base-monthly]').forEach(function (el) {
      var basePrice = isYearly ? parseInt(el.dataset.baseYearly) : parseInt(el.dataset.baseMonthly);
      el.textContent = formatPrice(basePrice);
    });

    // Update total displays
    document.querySelectorAll('.price-total[data-base-yearly-total]').forEach(function (el) {
      if (isYearly) {
          var baseTotal = parseInt(el.dataset.baseYearlyTotal);
          el.textContent = formatPrice(baseTotal) + ' / year';
      } else {
          el.textContent = '';
      }
    });
  }

  if (billingToggle) {
    billingToggle.addEventListener('click', function () {
      isYearly = !isYearly;
      updatePricing();
    });
  }

  // Initialize Pricing formatting
  updatePricing();

  // Multilingual Dynamic SEO Dictionary
  const seoData = {
      'en': {
          desc: "LoungeOS is the best offline-first Restaurant POS system. Streamline operations, protect revenue, and boost profits. Free 90-day trial — no credit card required.",
          keys: "Restaurant POS, Point of Sale, Restaurant Management Software, Offline POS, KDS, Kitchen Display System, Bar POS, Cafe Management, LoungeOS"
      },
      'fr': {
          desc: "LoungeOS est le meilleur système de caisse (POS) pour restaurant fonctionnant hors ligne. Optimisez vos opérations et augmentez vos profits. Essai gratuit de 90 jours.",
          keys: "Caisse Restaurant, Logiciel de Caisse, POS Hors Ligne, Gestion de Restaurant, Logiciel Bar, TPV Restaurant, Système d'affichage cuisine, LoungeOS"
      },
      'es': {
          desc: "LoungeOS es el mejor sistema POS para restaurantes con funcionamiento sin conexión. Optimice operaciones y proteja sus ingresos. Prueba gratuita de 90 días.",
          keys: "Punto de Venta Restaurante, Sistema POS, Software de Gestión de Restaurantes, POS Offline, Sistema de Pantalla de Cocina, KDS, LoungeOS"
      },
      'de': {
          desc: "LoungeOS ist das beste Offline-First-Kassensystem für Restaurants. Optimieren Sie Abläufe und steigern Sie Gewinne. 90 Tage kostenlos testen.",
          keys: "Kassensystem Gastronomie, Restaurant POS, Offline Kasse, Bar Management Software, Küchenanzeigesystem, LoungeOS"
      },
      'zh-CN': {
          desc: "LoungeOS是最佳的离线优先餐厅POS系统。简化运营，保护收入并提高利润。提供90天免费试用。",
          keys: "餐厅POS, 销售点系统, 离线POS, 餐厅管理软件, 酒吧管理, 厨房显示系统, LoungeOS"
      },
      'ar': {
          desc: "LoungeOS هو أفضل نظام نقاط بيع (POS) للمطاعم يعمل بدون إنترنت. قم بتبسيط العمليات وزيادة الأرباح. تجربة مجانية لمدة 90 يومًا.",
          keys: "نظام نقاط البيع, POS مطعم, برنامج إدارة المطاعم, نقاط البيع بدون إنترنت, نظام عرض المطبخ, LoungeOS"
      },
      'hi': {
          desc: "LoungeOS रेस्तरां के लिए सबसे अच्छा ऑफलाइन-फर्स्ट POS सिस्टम है। संचालन को सुव्यवस्थित करें और मुनाफा बढ़ाएं। 90 दिन का मुफ्त ट्रायल।",
          keys: "रेस्तरां पीओएस, पॉइंट ऑफ़ सेल, रेस्तरां प्रबंधन सॉफ्टवेयर, ऑफलाइन पीओएस, बार प्रबंधन, किचन डिस्प्ले सिस्टम, LoungeOS"
      },
      'pt': {
          desc: "LoungeOS é o melhor sistema PDV para restaurantes offline-first. Simplifique operações e aumente lucros. Teste grátis de 90 dias.",
          keys: "PDV Restaurante, Ponto de Venda, Sistema de Gestão de Restaurante, PDV Offline, Sistema de Exibição de Cozinha, LoungeOS"
      },
      'ru': {
          desc: "LoungeOS — лучшая POS-система для ресторанов, работающая в офлайн-режиме. Оптимизируйте работу и увеличьте прибыль. Бесплатная 90-дневная версия.",
          keys: "POS-система для ресторана, Автоматизация ресторана, Офлайн POS, Программа для бара, Система кухонных экранов, LoungeOS"
      },
      'ja': {
          desc: "LoungeOSは、最高のオフラインファースト・レストランPOSシステムです。業務を効率化し、利益を向上させます。90日間の無料トライアル。",
          keys: "レストランPOS, 販売時点情報管理, オフラインPOS, 飲食店管理システム, バー管理, キッチンディスプレイシステム, LoungeOS"
      }
  };

  function updateDynamicSEO(lang) {
      if (seoData[lang]) {
          document.documentElement.lang = lang;
          
          let metaDesc = document.querySelector('meta[name="description"]');
          if(metaDesc) metaDesc.content = seoData[lang].desc;
          
          let metaKeys = document.querySelector('meta[name="keywords"]');
          if(metaKeys) metaKeys.content = seoData[lang].keys;
          
          let ogDesc = document.querySelector('meta[property="og:description"]');
          if(ogDesc) ogDesc.content = seoData[lang].desc;
      }
  }

  // Auto-detect location for Currency and Language
  // Also check URL params for targeted language indexing
  var urlParams = new URLSearchParams(window.location.search);
  var paramLang = urlParams.get('lang');

  fetch('https://ipapi.co/json/')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.currency) {
            userCurrency = data.currency;
            
            // Set up formatter for user's locale and currency
            currencyFormatter = new Intl.NumberFormat(navigator.language || 'en-US', { 
                style: 'currency', 
                currency: userCurrency, 
                maximumFractionDigits: userCurrency === 'XAF' || userCurrency === 'JPY' ? 0 : 2 
            });

            // Fetch exchange rate from XAF to user's currency
            if (userCurrency !== 'XAF') {
                fetch('https://open.er-api.com/v6/latest/XAF')
                    .then(function(res) { return res.json(); })
                    .then(function(ratesData) {
                        if (ratesData && ratesData.rates && ratesData.rates[userCurrency]) {
                            exchangeRate = ratesData.rates[userCurrency];
                            updatePricing(); // Re-render with new currency
                        }
                    })
                    .catch(function(e) { console.error("Exchange rate error:", e); });
            } else {
                updatePricing();
            }
        }
        
        // Auto-Language selection based on location languages (overridden by URL param)
        var primaryLang = paramLang;
        if (!primaryLang && data.languages) {
            primaryLang = data.languages.split(',')[0].split('-')[0];
            if (primaryLang === 'zh') primaryLang = 'zh-CN';
        }
        
        var supportedLangs = ['en', 'fr', 'es', 'de', 'zh-CN', 'ar', 'hi', 'pt', 'ru', 'ja'];
        if (primaryLang && supportedLangs.includes(primaryLang)) {
            // Check if user has already manually selected a language
            var selectField = document.getElementById("customLangSelect");
            if (selectField && selectField.value !== primaryLang && (!sessionStorage.getItem('langAutoSet') || paramLang)) {
                selectField.value = primaryLang;
                sessionStorage.setItem('langAutoSet', 'true');
                // Wait for Google Translate script to be ready
                setTimeout(function() {
                    if(typeof changeLanguage === 'function') {
                        changeLanguage(primaryLang);
                        updateDynamicSEO(primaryLang);
                    }
                }, 1000);
            } else {
                updateDynamicSEO(primaryLang); // Just update SEO even if not changing visual lang automatically
            }
        }
    })
    .catch(function(e) { console.error("Location detection error:", e); });


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
    const uniqueImages = images.slice(0, images.length / 2).map(img => img.src);
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
var gtBannerObserver = new MutationObserver(function() {
    hideGoogleTranslateBanner();
});
gtBannerObserver.observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style'] });
