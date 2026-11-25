// Fixed references chosen for the trial. Drawn wherever they show, so words and charts cannot drift.
const LIMIT_DD = -10;       // go-live rule: max drawdown no worse than this, percent
const TARGET_SEK_DAY = 50;  // the daily profit target, SEK

const loc = d3.formatLocale({decimal: '.', thousands: ',', grouping: [3], currency: ['', ''], minus: '-'});
const fSigned0 = loc.format('+,.0f'), fInt = loc.format(',.0f'), fSigned2 = loc.format('+.2f'), f2 = loc.format('.2f'), f1 = loc.format('.1f');
const parseDay = d3.utcParse('%Y-%m-%d'), fDay = d3.utcFormat('%-d %b'), fDayLong = d3.utcFormat('%a %-d %b %Y');
const PAPER = dash.colors[0], INDEX = 'var(--cds-chart-muted)', SURFACE = 'var(--color-panel)';

document.querySelectorAll('.qt-key-paper').forEach((e) => { e.style.background = PAPER; });
document.querySelectorAll('.qt-key-index').forEach((e) => { e.style.background = INDEX; });

// ---- single values from the summary row ----
function field(name, render) {
  dash.draw(name, (el) => {
    const s = dash.data('summary');
    el.classList.toggle('dash-skeleton', s.status === 'loading');
    el.classList.remove('qt-good', 'qt-bad');
    if (s.status !== 'ok' || !s.data.length) { el.textContent = '—'; return; }
    render(el, s.data[0]);
  });
}
const tone = (el, good) => el.classList.add(good ? 'qt-good' : 'qt-bad');
const day = (v) => { const d = parseDay(v); return d ? fDay(d) : String(v); };

field('days', (el, r) => { el.textContent = fInt(+r.trading_days); });
field('paper-pct', (el, r) => { el.textContent = fSigned2(+r.paper_pct) + '%'; });
field('paper-pct-toned', (el, r) => { el.textContent = fSigned2(+r.paper_pct) + '%'; tone(el, +r.paper_pct >= 0); });
field('index-pct', (el, r) => { el.textContent = fSigned2(+r.index_pct) + '%'; });
field('gap', (el, r) => { el.textContent = fSigned2(+r.gap_points); });
field('gap-toned', (el, r) => { el.textContent = fSigned2(+r.gap_points); tone(el, +r.gap_points >= 0); });
field('paper-sek', (el, r) => { el.textContent = fSigned0(+r.paper_sek); });
field('capital', (el, r) => { el.textContent = fInt(+r.capital_sek); });
field('start', (el, r) => { el.textContent = day(r.trial_start); });
field('asof', (el, r) => { const d = parseDay(r.as_of); el.textContent = d ? fDayLong(d) : String(r.as_of); });
field('maxdd', (el, r) => { el.textContent = f2(+r.max_drawdown_pct) + '%'; });
field('dd-now', (el, r) => { el.textContent = f2(+r.drawdown_now_pct) + '%'; });
field('avg', (el, r) => { el.textContent = fSigned0(+r.avg_sek_per_day); });
field('up-days', (el, r) => { el.textContent = fInt(+r.up_days); });
field('down-days', (el, r) => { el.textContent = fInt(+r.down_days); });
field('best', (el, r) => { el.textContent = fSigned0(+r.best_day_sek); });
field('best-date', (el, r) => { el.textContent = day(r.best_day_date); });
field('worst', (el, r) => { el.textContent = fSigned0(+r.worst_day_sek); });
field('worst-date', (el, r) => { el.textContent = day(r.worst_day_date); });
field('verdict', (el, r) => { el.textContent = String(r.verdict); if (r.verdict === 'PASS') tone(el, true); else if (r.verdict === 'FAIL') tone(el, false); });
field('last-reb', (el, r) => { el.textContent = day(r.last_rebalance); });
field('to-reb', (el, r) => { el.textContent = fInt(+r.days_to_rebalance); });
field('regime', (el, r) => { el.textContent = String(r.regime); });
field('positions', (el, r) => { el.textContent = fInt(+r.positions); });
field('sma-gap', (el, r) => { el.textContent = fSigned2(+r.index_vs_sma200_pct) + '%'; });
dash.draw('limit', (el) => { el.textContent = LIMIT_DD + '%'; });
dash.draw('target', (el) => { el.textContent = fInt(TARGET_SEK_DAY) + ' SEK'; });

// The basket section says one thing while invested and another while the regime rule holds cash.
dash.onData(() => {
  const s = dash.data('summary');
  const cash = s.status === 'ok' && s.data.length > 0 && +s.data[0].positions === 0;
  document.querySelectorAll('[data-when="invested"]').forEach((e) => { e.hidden = cash; });
  document.querySelectorAll('[data-when="cash"]').forEach((e) => { e.hidden = !cash; });
});

// ---- shared chart pieces ----
function dailyRows() {
  const s = dash.data('daily');
  if (s.status !== 'ok') return {status: s.status, rows: []};
  const rows = s.data.map((r) => ({date: parseDay(r.date), iso: String(r.date), paper: +r.paper_pct, index: +r.index_pct,
    pnl: +r.day_pnl_sek, dd: +r.drawdown_pct, reb: +r.rebalanced === 1})).filter((r) => r.date);
  return {status: rows.length > 1 ? 'ok' : 'empty', rows};
}
function placeholder(el, status) {
  el.replaceChildren();
  el.classList.toggle('dash-skeleton', status === 'loading');
  if (status === 'loading') return;
  const p = document.createElement('p');
  p.className = 'qt-fail';
  p.textContent = status === 'error' ? 'This chart could not load its data.' : '—';
  el.append(p);
}
function textWidth(svg, strings) {
  const g = svg.append('g');
  let w = 0;
  for (const s of strings) w = Math.max(w, g.append('text').text(s).node().getComputedTextLength());
  g.remove();
  return w;
}
function tipRow(tip, color, value, name) {
  const row = document.createElement('div');
  row.className = 'qt-tip-row';
  if (color) { const key = document.createElement('span'); key.className = 'qt-key'; key.style.background = color; key.style.marginRight = '0'; row.append(key); }
  const v = document.createElement('strong'); v.textContent = value; row.append(v);
  const n = document.createElement('span'); n.className = 'qt-tip-name'; n.textContent = name; row.append(n);
  tip.append(row);
}
function placeTip(tip, xPx, top, width) {
  tip.hidden = false;
  const tw = tip.offsetWidth;
  let left = xPx + 12;
  if (left + tw > width - 4) left = xPx - tw - 12;
  tip.style.left = Math.max(4, left) + 'px';
  tip.style.top = top + 'px';
}
function keys(svg, n, getAt, show, hide) {
  svg.on('keydown', (ev) => {
    if (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') {
      ev.preventDefault();
      const at = getAt();
      show(at < 0 ? n - 1 : Math.max(0, Math.min(n - 1, at + (ev.key === 'ArrowRight' ? 1 : -1))));
    } else if (ev.key === 'Escape') hide();
  }).on('focus', () => show(n - 1)).on('blur', hide);
}

// A line chart over trading days: one y axis in percent, a crosshair that reads every series.
function timeChart(el, rows, cfg) {
  el.replaceChildren();
  el.classList.remove('dash-skeleton');
  const width = Math.max(el.clientWidth, 240), height = cfg.height;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${width} ${height}`)
    .attr('role', 'img').attr('aria-label', cfg.aria).attr('tabindex', 0);
  const vals = rows.flatMap((r) => cfg.series.map((s) => r[s.key]));
  let lo = Math.min(0, d3.min(vals)), hi = Math.max(0, d3.max(vals));
  for (const ref of cfg.refs || []) { lo = Math.min(lo, ref.y); hi = Math.max(hi, ref.y); }
  const y = d3.scaleLinear().domain([lo, hi]).nice(5);
  const ticks = y.ticks(5);
  const step = ticks.length > 1 ? Math.abs(ticks[1] - ticks[0]) : 1;
  const tf = loc.format(step < 1 ? '+.1f' : '+.0f');
  const tickText = (v) => (v === 0 ? '0' : tf(v)) + '%';
  const last = rows[rows.length - 1];
  const narrow = width < 460;
  const endText = cfg.series.map((s) => (narrow || cfg.series.length === 1 ? '' : s.label + ' ') + cfg.value(last[s.key]));
  const m = {top: 16, bottom: 26, left: Math.ceil(textWidth(svg, ticks.map(tickText))) + 10, right: Math.ceil(textWidth(svg, endText)) + 18};
  const x = d3.scaleUtc().domain(d3.extent(rows, (r) => r.date)).range([m.left, width - m.right]);
  y.range([height - m.bottom, m.top]);
  const g = svg.append('g');
  g.selectAll('line.qt-grid').data(ticks).join('line').attr('class', 'qt-grid').attr('x1', m.left).attr('x2', width - m.right)
    .attr('y1', (v) => y(v)).attr('y2', (v) => y(v)).style('stroke', (v) => (v === 0 ? 'var(--cds-chart-axis)' : 'var(--cds-chart-grid)')).style('stroke-width', 1);
  g.selectAll('text.qt-yt').data(ticks).join('text').attr('class', 'qt-yt').attr('x', m.left - 8).attr('y', (v) => y(v)).attr('dy', '0.32em').attr('text-anchor', 'end').text(tickText);
  // Date labels sit on real trading days, evenly spread and always including the latest one.
  const nTicks = Math.max(2, Math.min(rows.length, Math.floor((width - m.left - m.right) / 84)));
  const xt = [...new Set(d3.range(nTicks).map((i) => Math.round((i * (rows.length - 1)) / (nTicks - 1))))].map((i) => rows[i].date);
  g.selectAll('text.qt-xt').data(xt).join('text').attr('class', 'qt-xt').attr('x', (d) => x(d)).attr('y', height - 6).attr('text-anchor', 'middle').text((d) => fDay(d));
  for (const ref of cfg.refs || []) {
    g.append('line').attr('x1', m.left).attr('x2', width - m.right).attr('y1', y(ref.y)).attr('y2', y(ref.y)).style('stroke', 'var(--cds-chart-reference)').style('stroke-width', 1);
    g.append('text').attr('x', m.left + 4).attr('y', y(ref.y) - 6).text(ref.label);
  }
  if (cfg.marks) {
    // Every change gets its line. A label is drawn only where it clears the labels already placed,
    // so changes a day or two apart share one label instead of printing over each other.
    const placed = [];
    const labelW = textWidth(svg, [cfg.marks.label]);
    for (const r of rows.filter(cfg.marks.test)) {
      const px = x(r.date);
      g.append('line').attr('x1', px).attr('x2', px).attr('y1', m.top).attr('y2', height - m.bottom).style('stroke', 'var(--cds-chart-reference)').style('stroke-width', 1);
      const anchorEnd = px > (m.left + width - m.right) / 2;
      const x0 = anchorEnd ? px - 5 - labelW : px + 5, x1 = x0 + labelW;
      if (placed.some((b) => x0 < b[1] + 8 && x1 > b[0] - 8)) continue;
      placed.push([x0, x1]);
      g.append('text').attr('x', anchorEnd ? px - 5 : px + 5).attr('y', m.top + 8).attr('text-anchor', anchorEnd ? 'end' : 'start').text(cfg.marks.label);
    }
  }
  for (const s of cfg.series) {
    const col = s.color(last[s.key]);
    if (cfg.area) g.append('path').attr('d', d3.area().x((r) => x(r.date)).y0(y(0)).y1((r) => y(r[s.key]))(rows)).style('fill', col).style('opacity', 0.1);
    g.append('path').attr('d', d3.line().x((r) => x(r.date)).y((r) => y(r[s.key]))(rows)).style('fill', 'none').style('stroke', col)
      .style('stroke-width', 2).style('stroke-linejoin', 'round').style('stroke-linecap', 'round');
    g.append('circle').attr('cx', x(last.date)).attr('cy', y(last[s.key])).attr('r', 4).style('fill', col).style('stroke', SURFACE).style('stroke-width', 2);
  }
  const ends = cfg.series.map((s, i) => ({text: endText[i], y: y(last[s.key])})).sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 15) { const mid = (ends[i].y + ends[i - 1].y) / 2; ends[i - 1].y = mid - 7.5; ends[i].y = mid + 7.5; }
  g.selectAll('text.qt-end').data(ends).join('text').attr('class', 'qt-end').attr('x', x(last.date) + 9).attr('y', (d) => d.y).attr('dy', '0.32em').style('fill', 'var(--color-fg)').text((d) => d.text);

  const cross = g.append('line').attr('y1', m.top).attr('y2', height - m.bottom).style('stroke', 'var(--cds-chart-axis)').style('stroke-width', 1).attr('visibility', 'hidden');
  const dots = cfg.series.map((s) => g.append('circle').attr('r', 4).style('stroke', SURFACE).style('stroke-width', 2).attr('visibility', 'hidden'));
  const tip = document.createElement('div');
  tip.className = 'qt-tip';
  tip.hidden = true;
  el.append(tip);
  const nearest = d3.bisector((r) => r.date).center;
  let at = -1;
  const show = (i) => {
    at = i;
    const r = rows[i];
    cross.attr('x1', x(r.date)).attr('x2', x(r.date)).attr('visibility', 'visible');
    dots.forEach((d, k) => d.attr('cx', x(r.date)).attr('cy', y(r[cfg.series[k].key])).style('fill', cfg.series[k].color(r[cfg.series[k].key])).attr('visibility', 'visible'));
    tip.replaceChildren();
    const head = document.createElement('div'); head.className = 'qt-tip-head'; head.textContent = fDayLong(r.date); tip.append(head);
    cfg.series.forEach((s) => tipRow(tip, s.color(r[s.key]), cfg.value(r[s.key]), s.label));
    placeTip(tip, x(r.date), m.top, width);
  };
  const hide = () => { at = -1; cross.attr('visibility', 'hidden'); dots.forEach((d) => d.attr('visibility', 'hidden')); tip.hidden = true; };
  const point = (ev) => show(nearest(rows, x.invert(d3.pointer(ev, svg.node())[0])));
  svg.append('rect').attr('x', m.left - 6).attr('y', 0).attr('width', Math.max(0, width - m.left - m.right) + 12).attr('height', height).style('fill', 'transparent')
    .on('pointermove', point).on('pointerdown', point).on('pointerleave', hide);
  keys(svg, rows.length, () => at, show, hide);
}

dash.draw('equity-chart', (el) => {
  const d = dailyRows();
  if (d.status !== 'ok') return placeholder(el, d.status);
  timeChart(el, d.rows, {
    height: 300,
    aria: 'Line chart of cumulative return in percent for the paper portfolio and the OMXS30 index, by trading day',
    series: [{key: 'paper', label: 'Paper', color: () => PAPER}, {key: 'index', label: 'OMXS30', color: () => INDEX}],
    value: (v) => fSigned2(v) + '%',
    marks: {test: (r) => r.reb && r !== d.rows[0], label: 'portfolio changed'},
  });
});

dash.draw('dd-chart', (el) => {
  const d = dailyRows();
  if (d.status !== 'ok') return placeholder(el, d.status);
  timeChart(el, d.rows, {
    height: 240,
    aria: 'Line chart of drawdown in percent below the peak, by trading day, with the go-live limit line',
    series: [{key: 'dd', label: 'Drawdown', color: (v) => (v < LIMIT_DD ? 'var(--cds-chart-status-critical)' : PAPER)}],
    value: (v) => f2(v) + '%',
    area: true,
    refs: [{y: LIMIT_DD, label: 'go-live limit ' + LIMIT_DD + '%'}],
  });
});

// Bars for each day's profit or loss. Direction from the zero line carries the sign, so one color.
dash.draw('pnl-chart', (el) => {
  const d = dailyRows();
  if (d.status !== 'ok') return placeholder(el, d.status);
  const rows = d.rows.slice(1);   // the first row is the starting point and has no day of its own
  el.replaceChildren();
  el.classList.remove('dash-skeleton');
  const width = Math.max(el.clientWidth, 240), height = 240;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${width} ${height}`)
    .attr('role', 'img').attr('aria-label', 'Bar chart of paper profit or loss in SEK for each trading day').attr('tabindex', 0);
  const y = d3.scaleLinear().domain([Math.min(0, d3.min(rows, (r) => r.pnl)), Math.max(0, d3.max(rows, (r) => r.pnl))]).nice(5);
  const ticks = y.ticks(5);
  const tickText = (v) => (v === 0 ? '0' : fSigned0(v));
  const m = {top: 20, bottom: 34, left: Math.ceil(textWidth(svg, ticks.map(tickText))) + 10, right: 8};
  const x = d3.scaleBand().domain(rows.map((r) => r.iso)).range([m.left, width - m.right]).paddingInner(0.25).paddingOuter(0.15);
  y.range([height - m.bottom, m.top]);
  const g = svg.append('g');
  g.selectAll('line.qt-grid').data(ticks).join('line').attr('class', 'qt-grid').attr('x1', m.left).attr('x2', width - m.right)
    .attr('y1', (v) => y(v)).attr('y2', (v) => y(v)).style('stroke', (v) => (v === 0 ? 'var(--cds-chart-axis)' : 'var(--cds-chart-grid)')).style('stroke-width', 1);
  g.selectAll('text.qt-yt').data(ticks).join('text').attr('class', 'qt-yt').attr('x', m.left - 8).attr('y', (v) => y(v)).attr('dy', '0.32em').attr('text-anchor', 'end').text(tickText);
  const every = Math.max(1, Math.ceil(rows.length / Math.max(2, Math.floor((width - m.left - m.right) / 64))));
  g.selectAll('text.qt-xt').data(rows.filter((r, i) => (rows.length - 1 - i) % every === 0)).join('text').attr('class', 'qt-xt')
    .attr('x', (r) => x(r.iso) + x.bandwidth() / 2).attr('y', height - 6).attr('text-anchor', 'middle').text((r) => fDay(r.date));
  const bw = Math.min(24, x.bandwidth());
  const cx = (r) => x(r.iso) + x.bandwidth() / 2;
  const bar = (r) => {
    const x0 = cx(r) - bw / 2, y0 = y(0), y1 = y(r.pnl), s = r.pnl >= 0 ? 1 : -1, rad = Math.min(4, bw / 2, Math.abs(y1 - y0));
    return `M${x0},${y0}V${y1 + s * rad}Q${x0},${y1} ${x0 + rad},${y1}H${x0 + bw - rad}Q${x0 + bw},${y1} ${x0 + bw},${y1 + s * rad}V${y0}Z`;
  };
  const bars = g.selectAll('path.qt-bar').data(rows).join('path').attr('class', 'qt-bar').attr('d', bar).style('fill', PAPER);
  // Label only the two extremes; the axis, the tooltip and the table carry the rest.
  const best = rows.reduce((a, b) => (b.pnl > a.pnl ? b : a)), worst = rows.reduce((a, b) => (b.pnl < a.pnl ? b : a));
  const clampX = (v, text) => { const half = textWidth(svg, [text]) / 2; return Math.max(m.left + half, Math.min(width - m.right - half, v)); };
  for (const [r, dy] of [[best, -6], [worst, 13]]) {
    if ((r === best && r.pnl <= 0) || (r === worst && r.pnl >= 0)) continue;
    const text = fSigned0(r.pnl);
    g.append('text').attr('x', clampX(cx(r), text)).attr('y', y(r.pnl) + dy).attr('text-anchor', 'middle').style('fill', 'var(--color-fg)').text(text);
  }
  const tip = document.createElement('div');
  tip.className = 'qt-tip';
  tip.hidden = true;
  el.append(tip);
  let at = -1;
  const show = (i) => {
    at = i;
    const r = rows[i];
    bars.style('opacity', (b) => (b === r ? 1 : 0.45));
    tip.replaceChildren();
    const head = document.createElement('div'); head.className = 'qt-tip-head'; head.textContent = fDayLong(r.date); tip.append(head);
    tipRow(tip, null, fSigned0(r.pnl) + ' SEK', r.pnl >= 0 ? 'profit' : 'loss');
    placeTip(tip, cx(r), m.top, width);
  };
  const hide = () => { at = -1; bars.style('opacity', 1); tip.hidden = true; };
  g.selectAll('rect.qt-hit').data(rows).join('rect').attr('class', 'qt-hit').attr('x', (r) => x(r.iso) - (x.step() - x.bandwidth()) / 2).attr('y', m.top)
    .attr('width', x.step()).attr('height', height - m.top - m.bottom).style('fill', 'transparent')
    .on('pointermove', (ev, r) => show(rows.indexOf(r))).on('pointerdown', (ev, r) => show(rows.indexOf(r))).on('pointerleave', hide);
  keys(svg, rows.length, () => at, show, hide);
});

// ---- tables: the type marks the cells from the table's own data-source and row key ----
function cell(tr, text, cls) {
  const td = document.createElement('td');
  td.textContent = text;
  if (cls) td.className = cls;
  tr.append(td);
  return td;
}
function tableRows(name, source, columns, build) {
  dash.draw(name, (tbody) => {
    const s = dash.data(source);
    tbody.replaceChildren();
    if (s.status === 'error') {
      const tr = document.createElement('tr');
      cell(tr, 'This table could not load its data.', 'qt-fail').colSpan = columns;
      tbody.append(tr);
    }
    if (s.status !== 'ok') return;
    for (const tr of build(s.data)) tbody.append(tr);
  });
}
tableRows('checklist-rows', 'checklist', 4, (rows) => rows.map((r) => {
  const tr = document.createElement('tr');
  cell(tr, String(r.criterion)); cell(tr, String(r.threshold)); cell(tr, String(r.value));
  cell(tr, String(r.result), r.result === 'pass' ? 'qt-res-pass' : 'qt-res-wait');
  return tr;
}));
tableRows('holdings-rows', 'holdings', 6, (rows) => rows.map((r) => {
  const tr = document.createElement('tr');
  cell(tr, String(r.ticker)); cell(tr, String(r.company));
  cell(tr, f1(+r.weight_pct) + '%', 'qt-num'); cell(tr, fInt(+r.sek), 'qt-num');
  cell(tr, fSigned2(+r.return_since_rebalance_pct) + '%', 'qt-num'); cell(tr, fSigned2(+r.predicted_excess_pct) + '%', 'qt-num');
  return tr;
}));
tableRows('daily-rows', 'daily', 5, (rows) => rows.slice().reverse().map((r) => {
  const tr = document.createElement('tr');
  tr.dataset.key = String(r.date);
  const d = parseDay(r.date);
  cell(tr, d ? fDayLong(d) : String(r.date));
  cell(tr, fSigned2(+r.paper_pct) + '%', 'qt-num'); cell(tr, fSigned2(+r.index_pct) + '%', 'qt-num');
  cell(tr, fSigned0(+r.day_pnl_sek), 'qt-num'); cell(tr, f2(+r.drawdown_pct) + '%', 'qt-num');
  return tr;
}));
