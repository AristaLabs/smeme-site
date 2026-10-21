/* SMEme Business waitlist form: "Other" workspace toggle + at-least-one
   workspace validation for a normal cross-origin form submission. */
(function () {
  function initWaitlistOtherToggle(root) {
    var scope = root || document;
    var otherCb = scope.querySelector("[data-waitlist-other-toggle]");
    var wrap = scope.querySelector("#waitlist-other-wrap");
    if (!otherCb || !wrap) return;
    function sync() {
      wrap.classList.toggle("hidden", !otherCb.checked);
    }
    otherCb.addEventListener("change", sync);
    sync();
  }
  initWaitlistOtherToggle(document.getElementById("waitlist"));
  document.body.addEventListener("submit", function (event) {
    var form = event.target;
    if (!form || !form.getAttribute || !form.getAttribute("data-waitlist-form")) return;
    var checked = form.querySelectorAll('input[name="workspaces"]:checked');
    var err = form.querySelector("[data-waitlist-workspaces-error]");
    if (checked.length) {
      if (err) err.remove();
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    if (!err) {
      err = document.createElement("p");
      err.setAttribute("data-waitlist-workspaces-error", "");
      err.setAttribute("role", "alert");
      err.className = "text-sm text-danger-700 dark:text-danger-300";
      err.textContent = "Select at least one workspace option.";
      var fieldset = form.querySelector("fieldset");
      if (fieldset) fieldset.appendChild(err);
    }
  });
})();
