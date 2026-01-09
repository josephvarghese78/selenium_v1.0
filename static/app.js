// --------------------- Utilities ---------------------
function qs(sel){return document.querySelector(sel)}
function qsa(sel){return Array.from(document.querySelectorAll(sel))}
function fmtTime(s){return s||''}

// --------------------- Chart drawing (Canvas-based, no libs) ---------------------
function drawPieCanvas(canvas, values, colors, labels){
  const c = canvas;
  c.width = 360; c.height = 260;
  const ctx = c.getContext('2d');
  ctx.clearRect(0,0,c.width,c.height);
  const total = values.reduce((a,b)=>a+b,0) || 1;
  let start = -0.5 * Math.PI;
  const cx = c.width/2, cy = c.height/2 - 10, r = Math.min(c.width,c.height)/3;
  values.forEach((v,i)=>{
    const angle = (v/total) * 2 * Math.PI;
    ctx.beginPath();
    ctx.moveTo(cx,cy);
    ctx.arc(cx,cy, r, start, start + angle);
    ctx.closePath();
    ctx.fillStyle = colors[i] || '#888';
    ctx.fill();
    start += angle;
  });
  // legend
  ctx.font = '12px Arial';
  let lx = 12, ly = c.height - 14;
  labels.forEach((lbl,i)=>{
    ctx.fillStyle = colors[i];
    ctx.fillRect(lx,ly-8,12,8);
    ctx.fillStyle = '#000000'; // legend text black
    ctx.fillText(` ${lbl} (${values[i]})`, lx+18, ly);
    ly -= 16;
  });
}





// --------------------- Render Functions ---------------------
function renderTestList(tests){
  const container = qs('#testList'); container.innerHTML='';
  const authors = new Set();
  Object.values(tests).forEach(test=>{
    authors.add(test.author || 'Unknown');
    const el = document.createElement('div');
    el.className = 'test-item';
    el.innerHTML = `<div>
        <div style="font-weight:700">${test.name}</div>
        <div class="small muted">${test.suite || ''} · ${test.start || ''}</div>
      </div>
      <div class="badges">
        <div class="badge ${test.status.toLowerCase()==='pass'?'pass':(test.status.toLowerCase()==='fail'?'fail':'skip')}">
          ${test.status}
        </div>
      </div>`;
    el.onclick = ()=> showTest(test.id);
    container.appendChild(el);
  });
  const authSel = qs('#authorFilter');
  authSel.innerHTML = '<option value="ALL">All authors</option>';
  Array.from(authors).sort().forEach(a=>{
    const o = document.createElement('option'); o.value=a; o.textContent=a; authSel.appendChild(o);
  });
}

function renderSummary(summary, tests){
  const right = qs('#rightContent');
  const passed = summary.passed, failed = summary.failed, skipped = summary.skipped;
  const total = summary.total;
  const passPct = total ? (passed/total*100).toFixed(1) : 0;
  right.innerHTML = `
    <div class="card-row">
      <div class="card"><h3>Total Tests</h3><div class="big">${total}</div></div>
      <div class="card"><h3>Passed</h3><div class="big" style="color:var(--pass)">${passed}</div></div>
      <div class="card"><h3>Failed</h3><div class="big" style="color:var(--fail)">${failed}</div></div>
      <div class="card"><h3>Pass %</h3><div class="big">${passPct}%</div></div>
      <div class="card"><h3>Duration</h3><div class="big">${summary.duration || '-'}</div></div>
    </div>

    <div class="grid">
      <div>
        <div class="card test-details">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div class="kv">Author</div>
              <div style="font-weight:700">${summary.author || '-'}</div>
            </div>
            <div>
              <div class="kv">Environment</div>
              <div style="font-weight:700">${summary.env || '-'}</div>
            </div>
            <div>
              <div class="kv">System</div>
              <div style="font-weight:700">${summary.system || '-'}</div>
            </div>
          </div>
          <hr style="margin:12px 0;border:0;border-top:1px solid rgba(255,255,255,0.03)">
          <div style="display:flex;gap:12px;flex-wrap:wrap">
            <canvas id="pieCanvas"></canvas>
            <canvas id="barCanvas"></canvas>
            <canvas id="lineCanvas"></canvas>
          </div>
        </div>
      </div>
      <div>
        <div class="card">
          <h3>Quick Stats</h3>
          <div class="kv">OS: ${summary.os || '-'}</div>
          <div class="kv">Python: ${summary.python || '-'}</div>
          <div class="kv">Generated: ${summary.generated_at || '-'}</div>
          <div style="height:12px"></div>
          <h3>Top failures</h3>
          <div id="topFailures"></div>
        </div>
      </div>
    </div>

    <div style="margin-top:14px" id="recentArea"></div>
  `;

  // draw charts
  const pieCanvas = qs('#pieCanvas');
  drawPieCanvas(pieCanvas,
    [passed, failed, skipped],
    [
      getComputedStyle(document.documentElement).getPropertyValue('--pass').trim() || '#2ed573',
      getComputedStyle(document.documentElement).getPropertyValue('--fail').trim() || '#ff6b6b',
      getComputedStyle(document.documentElement).getPropertyValue('--skip').trim() || '#ffa502'
    ],
    ['Passed','Failed','Skipped']
  );

  const failures = Object.values(TESTS).filter(t=>t.status==='FAIL').slice(0,5);
  qs('#topFailures').innerHTML = failures.length ? failures.map(f=>`<div class="kv">${f.name}</div>`).join('') : '<div class="empty">No failures</div>';

  //const recent = Object.values(TESTS).slice(0,6);
  //qs('#recentArea').innerHTML = `<h3>Recent tests</h3>` + recent.map(t=>`<div class="kv">${t.name} · ${t.status}</div>`).join('');
}

// --------------------- Show single test ---------------------
function showTest(id){
  const t = TESTS[id];
  if(!t) return;
  const right = qs('#rightContent');
  right.innerHTML = `
    <div class="test-details card">
      <div class="test-header">
        <div>
          <div style="font-weight:800;font-size:18px">${t.name}</div>
          <div class="small muted">Suite: ${t.suite || ''} · Author: ${t.author || ''} · Start: ${t.start||''} · Duration: ${t.duration||''}</div>
        </div>
        <div class="badges">
          <div class="badge ${t.status.toLowerCase()==='pass'?'pass':(t.status.toLowerCase()==='fail'?'fail':'skip')}">${t.status}</div>
        </div>
      </div>
      <div class="steps" id="stepsArea"></div>
    </div>
  `;
  const stepsArea = qs('#stepsArea');
  t.steps.forEach((s, idx)=>{
    const div = document.createElement('div'); div.className = 'step';
    div.innerHTML = `
      <div class="step-header">
        <div>
          <div style="font-weight:700">${idx+1}. ${s.step_name}</div>
          <div class="meta small muted">Start: ${s.start || ''} . Duration: ${s.duration || ''}</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <div class="kv">${s.status}</div>
        </div>
      </div>
      <div class="kv">${s.message || ''}</div>
      ${s.screenshot ? `<img src="${s.screenshot}" class="screenshot" onclick="openModal('${s.screenshot}')">` : ''}
      ${s.trace ? `<details style="margin-top:8px"><summary class="kv">View stacktrace</summary><pre style="white-space:pre-wrap;color:#f2f2f2;background:rgba(0,0,0,0.2);padding:8px;border-radius:6px">${s.trace}</pre></details>` : ''}
    `;
    stepsArea.appendChild(div);
  });
}

// --------------------- Modal for screenshots ---------------------
function openModal(src){
  let modal = qs('.modal');
  if(!modal){
    modal = document.createElement('div'); modal.className='modal'; modal.id='imgModal';
    modal.innerHTML = `<div class="close-x" onclick="closeModal()">✕</div><img id="modalImg"><div style="width:18px;height:18px"></div>`;
    document.body.appendChild(modal);
  }
  qs('#modalImg').src = src;
  modal.style.display = 'flex';
}
function closeModal(){ const m=qs('.modal'); if(m) m.style.display='none' }

// --------------------- Search / Filter ---------------------
function onSearch(){ applyFilters() }
function onFilterChange(){ applyFilters() }
function applyFilters(){
  const q = qs('#searchBox').value.toLowerCase();
  const status = qs('#statusFilter').value;
  const author = qs('#authorFilter').value;
  const filtered = {};
  Object.values(TESTS).forEach(t=>{
    const matchQ = t.name.toLowerCase().includes(q) || (t.suite||'').toLowerCase().includes(q);
    const matchStatus = status==='ALL' || t.status===status;
    const matchAuthor = author==='ALL' || (t.author||'')===author;
    if(matchQ && matchStatus && matchAuthor) filtered[t.id]=t;
  });
  renderTestList(filtered);
}

// --------------------- Theme toggle ---------------------
function toggleTheme(){
  const body = document.body;
  body.dataset.theme = body.dataset.theme==='dark'?'light':'dark';
}
function showSummary(){
  renderSummary(SUMMARY, TESTS);
  renderTestList(TESTS);
}

// --------------------- Init ---------------------
(function init(){
  renderTestList(TESTS);
  showSummary();
  if(Array.isArray(TESTS)){
    const map = {};
    TESTS.forEach(t=> map[t.id] = t);
    window.TESTS = map;
  }
  document.addEventListener('keydown', (e)=> { if(e.key==='Escape') closeModal(); });
})();
