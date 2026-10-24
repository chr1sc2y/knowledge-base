/* Optional enhancement: the initial per-100-g chart remains readable offline. */
(() => {
  const chart = document.querySelector('.fibre-chart');
  if (!chart) return;
  const zh = document.documentElement.lang.startsWith('zh');
  const controls = chart.querySelector('.chart-controls');
  const rows = [...chart.querySelectorAll('.fibre-row')];
  controls.hidden = false;
  controls.addEventListener('click', event => {
    const button = event.target.closest('button[data-mode]');
    if (!button) return;
    const portionMode = button.dataset.mode === 'portion';
    controls.querySelectorAll('button').forEach(el => el.setAttribute('aria-pressed', String(el === button)));
    rows.forEach(row => {
      const weight = portionMode ? Number(row.dataset.portion) : 100;
      const fibre = Number(row.dataset.value) * weight / 100;
      row.querySelector('.fibre-fill').style.width = `${fibre / 6 * 100}%`;
      row.querySelector('.fibre-value').innerHTML = `${(Math.round((fibre + Number.EPSILON) * 10) / 10).toFixed(1)}<small>g</small>`;
      row.querySelector('.portion-label').textContent = `${weight} g`;
    });
    const message = portionMode
      ? (zh ? '示例份量：西兰花 200 g，菠菜、罗马生菜、番茄与小白菜各 150 g，其余各 100 g；仅演示换算，不代表摄入标准。' : 'Example portions: broccoli 200 g; spinach, romaine, tomato and bok choy 150 g each; other foods 100 g each. An arithmetic illustration, not an intake standard.')
      : (zh ? '每 100 g 比较；比例尺从 0 开始。' : 'Comparison per 100 g; scale begins at zero.');
    chart.querySelector('[data-chart-note]').textContent = message;
    chart.querySelector('[aria-live]').textContent = message;
  });
})();
