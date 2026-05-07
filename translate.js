/* CDL Training of Tampa — Language Switcher (ES / EN / PT)
   Multi-strategy:
   - On native pages (main `/`): redirect to the native subdomain/sister site.
   - On non-native pages (e.g. blog subpages hosted only on ES):
     use Google Translate cookie + reload.
   - Reads <html lang> as source of truth for page's native language.
*/
(function(){
  'use strict';

  var STORAGE_KEY = 'cdl_lang';

  // Paths that have native versions at each subdomain/sister site.
  var NATIVE_PATHS_RE = /^\/?(index\.html)?$/;

  function getPageLang(){
    var l = (document.documentElement.lang || 'es').toLowerCase();
    if (l.indexOf('pt') === 0) return 'pt';
    if (l.indexOf('en') === 0) return 'en';
    return 'es';
  }

  function readGtCookieLang(){
    var m = document.cookie.match(/googtrans=\/[a-z-]+\/([a-z-]+)/i);
    return m && m[1] ? m[1].toLowerCase().split('-')[0] : null;
  }

  function getCurrentLang(){
    var c = readGtCookieLang();
    if (c && ['es','en','pt'].indexOf(c) !== -1) return c;
    return getPageLang();
  }

  function clearTransCookies(){
    var host = location.hostname;
    var root = host.replace(/^(www|es|en|pt)\./, '');
    var domains = ['', host, '.' + host, root, '.' + root];
    for (var i = 0; i < domains.length; i++){
      var str = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/;';
      if (domains[i]) str += ' domain=' + domains[i] + ';';
      document.cookie = str;
    }
  }

  function isProdHost(){
    return /getmycdltampa\.com$/.test(location.hostname);
  }

  function isPagesDev(){
    return /\.pages\.dev$/.test(location.hostname);
  }

  function rootDomain(){
    return location.hostname.replace(/^(www|es|en|pt)\./, '');
  }

  /* Return the absolute URL of the native sister site for a given lang,
     or null if we don't have one for the current hosting environment. */
  function nativeUrlFor(lang){
    if (isProdHost()){
      return 'https://' + lang + '.getmycdltampa.com/';
    }
    if (isPagesDev()){
      return 'https://cdl-landing-' + lang + '.pages.dev/';
    }
    // Local dev / unknown host: no native redirect.
    return null;
  }

  function switchLang(lang){
    try { localStorage.setItem(STORAGE_KEY, lang); } catch(e){}
    clearTransCookies();

    var path = location.pathname;
    var native = NATIVE_PATHS_RE.test(path);
    var pageLang = getPageLang();

    if (lang === pageLang && !readGtCookieLang()){
      return;
    }

    var nativeUrl = nativeUrlFor(lang);
    if (nativeUrl && native){
      window.location.href = nativeUrl;
      return;
    }

    if (lang !== pageLang){
      var val = '/' + pageLang + '/' + lang;
      document.cookie = 'googtrans=' + val + '; path=/';
      if (isProdHost()){
        document.cookie = 'googtrans=' + val + '; path=/; domain=.' + rootDomain();
      }
    }
    location.reload();
  }

  function markActive(lang){
    var btns = document.querySelectorAll('.lang-btn');
    for (var i = 0; i < btns.length; i++){
      var match = btns[i].getAttribute('data-lang') === lang;
      btns[i].classList.toggle('active', match);
      btns[i].setAttribute('aria-pressed', match ? 'true' : 'false');
    }
  }

  window.googleTranslateElementInit = function(){
    try {
      new google.translate.TranslateElement({
        pageLanguage: getPageLang(),
        includedLanguages: 'en,pt,es',
        autoDisplay: false
      }, 'google_translate_element');
    } catch(e){ /* no-op */ }
  };

  document.addEventListener('click', function(e){
    var btn = e.target.closest ? e.target.closest('.lang-btn') : null;
    if (!btn) return;
    e.preventDefault();
    switchLang(btn.getAttribute('data-lang'));
  });

  markActive(getCurrentLang());

  var pageLang = getPageLang();
  var currentLang = getCurrentLang();
  if (pageLang !== currentLang){
    var s = document.createElement('script');
    s.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    s.async = true;
    s.defer = true;
    document.head.appendChild(s);
  }
})();
