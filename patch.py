import re
with open("index.html", "r") as f:
    text = f.read()

# 1. Add CSS
css_to_add = """
/* ── Fullscreen Image Modal ─────────────────────── */
.img-modal {
  display: none; position: fixed; z-index: 9999;
  left: 0; top: 0; width: 100%; height: 100%;
  background-color: rgba(0,0,0,0.85);
  backdrop-filter: blur(4px);
  justify-content: center; align-items: center;
}
.img-modal-content {
  max-width: 90vw; max-height: 90vh;
  border-radius: var(--radius); box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}
.img-modal-close {
  position: absolute; top: 20px; right: 30px;
  color: #fff; font-size: 35px; font-weight: bold; cursor: pointer;
}
.img-modal-close:hover { color: var(--acc1); }
</style>"""
text = text.replace("</style>", css_to_add, 1)

# 2. Add HTML
html_to_add = """
<!-- ══ IMAGE MODAL ═══════════════════════════════════════════════════════════ -->
<div id="imgModal" class="img-modal" onclick="closeModal()">
  <span class="img-modal-close" onclick="closeModal()">&times;</span>
  <img class="img-modal-content" id="imgModalEl">
</div>

<!-- ══ FOOTER ════════════════════════════════════════════════════════════════ -->
"""
text = text.replace("<!-- \u2550\u2550 FOOTER \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550 -->", html_to_add)

# 3. JS Functions
js_to_add = """
function openModal(imgId) {
  const img = document.getElementById(imgId);
  if (!img) return;
  const modal = document.getElementById('imgModal');
  const modalImg = document.getElementById('imgModalEl');
  modal.style.display = 'flex';
  modalImg.src = img.src;
}
function closeModal() { document.getElementById('imgModal').style.display = 'none'; }

async function runPyAndRefreshCard() {
  const btn = document.getElementById('btnTsRun');
  const spinner = document.getElementById('tsSpinner');
  const imgTimeseries = document.getElementById('imgTimeseries');
  const imgSnapshot = document.getElementById('imgSnapshot');
  if (btn) btn.disabled = true;
  if (spinner) spinner.style.display = 'block';
  try {
    const body = {
      N: SIM.N, L: SIM.L, eta: SIM.eta, J: SIM.J, alpha: SIM.alpha,
      v_max: SIM.v_max, r_align: SIM.r_align, shadow_type: SIM.shadow_type,
      chiral_spin: SIM.chiral_spin, n_steps: SIM.n_steps, dt: SIM.dt
    };
    const res = await fetch('/api/simulate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!res.ok) throw new Error("Simulation failed");
    const data = await res.json();
    const t = new Date().getTime();
    if (imgTimeseries) imgTimeseries.src = '/plots/demo_timeseries.png?t=' + t;
    if (imgSnapshot) imgSnapshot.src = '/plots/demo_snapshot.png?t=' + t;
    rtChart.polar = data.polar_orders; rtChart.transport = data.transport_effs; rtChart.occ = data.occupancies;
    rtChart.time = Array.from({length: data.n_frames}, (_, i) => i * SIM.dt * Math.max(1, Math.floor(SIM.n_steps/data.n_frames)));
    updatePlotly();
  } catch (e) { alert("Failed: " + e.message); } finally {
    if (btn) btn.disabled = false;
    if (spinner) spinner.style.display = 'none';
  }
}

async function runTask(endpoint, imgId, spinnerId, buttonId) {
  const btn = document.getElementById(buttonId);
  const spinner = document.getElementById(spinnerId);
  const img = document.getElementById(imgId);
  if (btn) btn.disabled = true;
  if (spinner) spinner.style.display = 'block';
  try {
    const res = await fetch(endpoint, { method: 'POST' });
    if (!res.ok) throw new Error("Task failed");
    const t = new Date().getTime();
    if (img) img.src = img.src.split('?')[0] + '?t=' + t;
  } catch (e) { alert("Failed: " + e.message); } finally {
    if (btn) btn.disabled = false;
    if (spinner) spinner.style.display = 'none';
  }
}
// ─────────────────────────────────────────────────────────────────────────────
"""
text = text.replace("// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500", js_to_add, 1)

# 4. Buttons 
# Demo Snapshot
text = re.sub(
    r'<img class="plot-img" src="/plots/demo_snapshot.png".*?</div>\s*</div>',
    """<img class="plot-img" id="imgSnapshot" src="/plots/demo_snapshot.png" alt="Demo Snapshot" onerror="this.style.display='none'">
      <div class="plot-card-footer" style="display:flex;justify-content:space-between;align-items:flex-end">
        <span style="max-width:200px">Color = I_local &middot; Arrows = orientation &amp; speed</span>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="loadPreset('demo');scrollToSim()">▶ Live Sim</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="openModal('imgSnapshot')">🔍 Enlarge</button>
        </div>
      </div>
    </div>""",
    text, flags=re.DOTALL
)

# Demo Timeseries
text = re.sub(
    r'<img class="plot-img" src="/plots/demo_timeseries.png".*?</div>\s*</div>',
    """<div id="tsSpinner" style="display:none;text-align:center;padding:20px 0;color:var(--fg2);font-size:0.85rem">⏳ Running Python simulation… (~5–15s)</div>
      <img class="plot-img" id="imgTimeseries" src="/plots/demo_timeseries.png" alt="Demo Timeseries" onerror="this.style.display='none'">
      <div class="plot-card-footer" style="display:flex;justify-content:space-between;align-items:flex-end">
        <span style="max-width:200px">Φ_polar, Φ_transport, Occupancy · Dashed = transient</span>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
          <button class="btn btn-ghost" id="btnTsRun" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="runPyAndRefreshCard()">▶ Generate Plot</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="openModal('imgTimeseries')">🔍 Enlarge</button>
        </div>
      </div>
    </div>""",
    text, flags=re.DOTALL
)

# Phase Diagram
text = re.sub(
    r'<img class="plot-img" src="/plots/phase_diagram.png".*?</div>\s*</div>',
    """<div id="phaseSpinner" style="display:none;text-align:center;padding:20px 0;color:var(--fg2);font-size:0.85rem">⏳ Running Python simulation… (~15s)</div>
      <img class="plot-img" id="imgPhase" src="/plots/phase_diagram.png" alt="Phase Diagram" onerror="this.style.display='none'">
      <div class="plot-card-footer" style="display:flex;justify-content:space-between;align-items:flex-end">
        <span style="max-width:200px">Streaming phase vs disordered gas</span>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
          <button class="btn btn-ghost" id="btnPhaseRun" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="runTask('/api/run-phase', 'imgPhase', 'phaseSpinner', 'btnPhaseRun')">▶ Generate Plot</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="loadPreset('ordered');scrollToSim()">▶ Live Sim</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="openModal('imgPhase')">📊 View Diagram</button>
        </div>
      </div>
    </div>""",
    text, flags=re.DOTALL
)

# Obstacle
text = re.sub(
    r'<img class="plot-img" src="/plots/obstacle_comparison.png".*?</div>\s*</div>',
    """<div id="obsSpinner" style="display:none;text-align:center;padding:20px 0;color:var(--fg2);font-size:0.85rem">⏳ Running Python simulation… (~15s)</div>
      <img class="plot-img" id="imgShadow" src="/plots/obstacle_comparison.png" alt="Obstacle Comparison" onerror="this.style.display='none'">
      <div class="plot-card-footer" style="display:flex;justify-content:space-between;align-items:flex-end">
        <span style="max-width:200px">Collective rescue vs J=0</span>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
          <button class="btn btn-ghost" id="btnObsRun" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="runTask('/api/run-shadow', 'imgShadow', 'obsSpinner', 'btnObsRun')">▶ Generate Plot</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="loadPreset('shadow');scrollToSim()">▶ Live Sim</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="openModal('imgShadow')">📊 View Plot</button>
        </div>
      </div>
    </div>""",
    text, flags=re.DOTALL
)

# Chirality
text = re.sub(
    r'<img class="plot-img" src="/plots/chirality_demo.png".*?</div>\s*</div>',
    """<div id="chiralSpinner" style="display:none;text-align:center;padding:20px 0;color:var(--fg2);font-size:0.85rem">⏳ Running Python simulation… (~15s)</div>
      <img class="plot-img" id="imgChirality" src="/plots/chirality_demo.png" alt="Chirality Demo" onerror="this.style.display='none'">
      <div class="plot-card-footer" style="display:flex;justify-content:space-between;align-items:flex-end">
        <span style="max-width:200px">Circular/epitrochoidal paths</span>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
          <button class="btn btn-ghost" id="btnChiralRun" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="runTask('/api/run-chiral', 'imgChirality', 'chiralSpinner', 'btnChiralRun')">▶ Generate Plot</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="loadPreset('chiral');scrollToSim()">▶ Live Sim</button>
          <button class="btn btn-ghost" style="font-size:0.68rem;padding:3px 8px;width:100%" onclick="openModal('imgChirality')">📊 View Plot</button>
        </div>
      </div>
    </div>""",
    text, flags=re.DOTALL
)

with open("index.html", "w") as f:
    f.write(text)

