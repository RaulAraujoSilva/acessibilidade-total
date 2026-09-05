(() => {
  const root = document.documentElement;
  const contrast = document.getElementById('interface-contrast');
  const size = document.getElementById('interface-size');
  const apply = (settings) => {
    root.dataset.contrast = settings.contrast ? 'high' : 'normal';
    root.dataset.textSize = ['large', 'larger'].includes(settings.size) ? settings.size : 'normal';
    if (contrast) contrast.checked = !!settings.contrast;
    if (size) size.value = root.dataset.textSize;
  };
  try { apply(JSON.parse(localStorage.getItem('accessibility-preferences') || '{}') || {}); } catch (_) { apply({}); }
  const save = () => {
    const settings = { contrast: contrast.checked, size: size.value };
    apply(settings);
    try { localStorage.setItem('accessibility-preferences', JSON.stringify(settings)); } catch (_) {}
  };
  contrast?.addEventListener('change', save);
  size?.addEventListener('change', save);
  document.getElementById('reset-appearance')?.addEventListener('click', () => { apply({}); save(); });
  const texts = {
    original: 'O atendimento está disponível de segunda a sexta-feira, das 9h às 17h. Solicite apoio à equipe quando precisar.',
    simple: 'Atendemos de segunda a sexta-feira. O horário é das 9h às 17h. Se precisar de ajuda, fale com a equipe.'
  };
  document.querySelectorAll('[data-demo]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-demo]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    document.getElementById('demo-paper').classList.toggle('demo-high-contrast', button.dataset.demo === 'contrast');
    document.getElementById('demo-text').textContent = texts[button.dataset.demo] || texts.original;
    document.getElementById('demo-status').textContent = button.textContent + ' selecionado. Demonstração ilustrativa, sem chamada de IA.';
  }));
  document.querySelectorAll('input[type="file"]').forEach(input => input.addEventListener('change', () => {
    const status = document.getElementById('selected-file');
    if (status) status.textContent = input.files?.[0] ? 'Arquivo selecionado: ' + input.files[0].name : 'Nenhum arquivo selecionado.';
  }));
})();
