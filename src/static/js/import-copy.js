/* Dashboard Import copy: the button opens the hidden file input.
   Choosing a file submits the form. Cancel leaves the page unchanged. */
if (!window.__smemeImportCopyBound) {
  window.__smemeImportCopyBound = true;

  document.body.addEventListener("click", function (event) {
    var button = event.target.closest("[data-import-copy-open]");
    if (!button) return;
    var form = button.closest("form");
    if (!form) return;
    var input = form.querySelector("[data-import-copy-file]");
    if (!input) return;
    input.click();
  });

  document.body.addEventListener("change", function (event) {
    var input = event.target.closest("[data-import-copy-file]");
    if (!input || !input.files || input.files.length === 0) return;
    var form = input.closest("form");
    if (!form) return;
    var button = form.querySelector("[data-import-copy-open]");
    if (button) button.disabled = true;
    if (typeof form.requestSubmit === "function") {
      form.requestSubmit();
    } else {
      form.submit();
    }
  });
}
