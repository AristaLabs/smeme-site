/* Bootstraps the Plausible queue/init stub when a site-specific proxied
   script (pa-*.js) is configured. Mirrors layouts/_analytics.html's prior
   inline snippet — see PLAUSIBLE_SCRIPT_URL / plausible_uses_custom_script. */
window.plausible =
  window.plausible ||
  function () {
    (plausible.q = plausible.q || []).push(arguments);
  };
plausible.init = plausible.init || function (i) { plausible.o = i || {}; };
plausible.init();
