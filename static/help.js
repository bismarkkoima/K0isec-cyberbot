// Save the user's important phone numbers on this computer only.
(function () {
    "use strict";
    var form = document.getElementById("contacts-form");
    var saved = {};
    try { saved = JSON.parse(Guardian.store("guardian-contacts") || "{}"); } catch (e) { saved = {}; }
    Array.prototype.forEach.call(form.elements, function (field) {
        if (field.name && saved[field.name]) field.value = saved[field.name];
    });
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        var data = {};
        Array.prototype.forEach.call(form.elements, function (field) {
            if (field.name) data[field.name] = field.value.trim();
        });
        Guardian.store("guardian-contacts", JSON.stringify(data));
        document.getElementById("contacts-saved").textContent = "✅ Saved on this computer.";
    });
})();
