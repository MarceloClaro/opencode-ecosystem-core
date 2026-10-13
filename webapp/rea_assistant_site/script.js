"use strict";

// Somente cópia local de texto. Nenhum comando é executado pelo navegador.
document.querySelectorAll("[data-copy-target]").forEach((button) => {
  button.addEventListener("click", async () => {
    const feedback = document.getElementById("copy-status");
    const command = document.getElementById(button.dataset.copyTarget);
    const originalLabel = button.textContent;
    try {
      const text = command.textContent.trim();
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const field = document.createElement("textarea");
        field.value = text;
        field.className = "copy-fallback";
        field.setAttribute("readonly", "");
        field.setAttribute("aria-hidden", "true");
        document.body.appendChild(field);
        try {
          field.select();
          if (!document.execCommand("copy")) throw new Error("Cópia indisponível");
        } finally {
          field.remove();
        }
      }
      feedback.textContent = "Comando copiado. Cole no terminal para executá-lo.";
      button.textContent = "Copiado";
      setTimeout(() => { button.textContent = originalLabel; }, 1800);
      setTimeout(() => { feedback.textContent = ""; }, 6000);
    } catch (_) {
      feedback.textContent = "Não foi possível copiar automaticamente. Selecione o comando e copie.";
    }
  });
});
