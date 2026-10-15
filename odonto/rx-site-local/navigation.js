class PanoramicaNavigation extends HTMLElement {
  connectedCallback() {
    if (this.dataset.ready === 'true') return;
    this.dataset.ready = 'true';
    const current = this.getAttribute('current') || '';
    const userId = this.getAttribute('user-id');
    const logoutId = this.getAttribute('logout-id');
    const links = [
      ['analysis', '/', 'Análise'],
      ['review', '/review', 'Revisão'],
      ['validation', '/validacao', 'Validação'],
      ['registration', '/cadastro', 'Cadastro'],
      ['api', '/docs', 'API / JSON'],
    ];
    const navigation = links.map(([key, href, label]) =>
      `<a href="${href}"${current === key ? ' aria-current="page"' : ''}>${label}</a>`
    ).join('');
    const user = userId ? `<span class="pa-nav-user" id="${userId}"></span>` : '';
    const logout = logoutId
      ? `<button class="pa-nav-logout" id="${logoutId}" type="button"${this.hasAttribute('logout-hidden') ? ' hidden' : ''}>Sair</button>`
      : '';
    this.innerHTML = `
      <header class="pa-topbar">
        <div class="pa-topbar-inner">
          <a class="pa-brand" href="/" aria-label="Panoramica AI - Análise">
            <span class="pa-brand-mark" aria-hidden="true">PA</span>
            <span>Panoramica AI</span>
          </a>
          <div class="pa-nav-scroll">
            <nav class="pa-nav" aria-label="Navegação principal">${navigation}${user}${logout}</nav>
          </div>
        </div>
      </header>`;
  }
}

if (!customElements.get('panoramica-nav')) {
  customElements.define('panoramica-nav', PanoramicaNavigation);
}
