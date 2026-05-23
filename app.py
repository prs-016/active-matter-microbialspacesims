"""
PJPS Simulation Dashboard — Flask Backend
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
import numpy as np
import sys, os, json, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# ── Import simulation code (lazy) ─────────────────────────────────────────────
_sim_globals = {}

def _load_sim():
    if _sim_globals:
        return
    try:
        import types
        # Patch IPython
        for mn in ['IPython', 'IPython.display', 'google', 'google.colab']:
            if mn not in sys.modules:
                sys.modules[mn] = types.ModuleType(mn)
        sys.modules['IPython.display'].HTML = lambda x: x
        sys.modules['IPython'].get_ipython = lambda: None
        sys.modules['IPython'].version_info = (8, 25)

        sim_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'janus_swarm_simulation.py')
        with open(sim_path) as f:
            src = f.read()
        exec_src = src.split("def main():")[0]
        exec(exec_src, _sim_globals)
        print("✅ Simulation module loaded")
    except Exception as e:
        print(f"❌ Failed to load sim: {e}")
        traceback.print_exc()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plots/<path:filename>')
def serve_plot(filename):
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), filename)


@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    _load_sim()
    if 'simulate_janus_swarm' not in _sim_globals:
        return jsonify({'error': 'Simulation not loaded'}), 500

    try:
        p = request.json or {}
        sim_fn = _sim_globals['simulate_janus_swarm']

        # Build obstacle dict
        obs = None
        obs_type = p.get('obstacle_type', 'none')
        if obs_type != 'none':
            L = float(p.get('L', 30.0))
            obs = {
                'type': obs_type,
                'center': [L * 0.5, L * 0.5],
                'radius': float(p.get('obs_radius', 3.0)),
                'shadow_fraction': float(p.get('shadow_fraction', 0.05)),
                'light_dir': [1.0, 0.0],
            }

        result = sim_fn(
            N=int(p.get('N', 200)),
            L=float(p.get('L', 30.0)),
            v_max=float(p.get('v_max', 1.0)),
            R_align=float(p.get('R_align', 2.0)),
            J=float(p.get('J', 1.0)),
            eta=float(p.get('eta', 0.5)),
            alpha=float(p.get('alpha', 0.8)),
            target_frac=(0.75, 0.75),
            I_0=float(p.get('I_0', 1.0)),
            I_emit=float(p.get('I_emit', 0.3)),
            sigma_rad=float(p.get('sigma_rad', 1.5)),
            R_rad=float(p.get('R_rad', 2.0)),
            kappa_B=float(p.get('kappa_B', 0.0)),
            theta_B=float(p.get('theta_B', 0.0)),
            sigma_chiral=float(p.get('sigma_chiral', 0.0)),
            kappa_T=float(p.get('kappa_T', 0.0)),
            epsilon_rep=float(p.get('epsilon_rep', 0.5)),
            sigma_rep=float(p.get('sigma_rep', 1.0)),
            n_steps=int(p.get('n_steps', 400)),
            dt=float(p.get('dt', 0.05)),
            seed=int(p.get('seed', 42)),
            obstacle=obs,
            r_zone=2.0,
            record_every=int(p.get('record_every', 4)),
        )

        # Generate and save the final state and timeseries plots using Matplotlib
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            dir_path = os.path.dirname(os.path.abspath(__file__))

            # Plot and save final state
            fig1 = _sim_globals['plot_snapshot'](
                result,
                frame_idx=-1,
                title=f"PJPS — Final State (J={float(p.get('J', 1.0)):.1f}, \u03b7={float(p.get('eta', 0.5)):.1f}, \u03b1={float(p.get('alpha', 0.8)):.1f})"
            )
            fig1.savefig(os.path.join(dir_path, 'demo_snapshot.png'), dpi=150, bbox_inches='tight')
            plt.close(fig1)

            # Plot and save timeseries
            fig2 = _sim_globals['plot_time_series'](
                result,
                title="PJPS Demo — Time Series"
            )
            fig2.savefig(os.path.join(dir_path, 'demo_timeseries.png'), dpi=150, bbox_inches='tight')
            plt.close(fig2)
        except Exception as plot_err:
            print(f"⚠️ Failed to generate plots in API: {plot_err}")

        # Serialize key results (not the full arrays to keep response small)
        n_fr = len(result['polar_orders'])
        step_size = max(1, n_fr // 80)  # max 80 frames for response
        frames_idx = list(range(0, n_fr, step_size))

        return jsonify({
            'polar_orders':   [round(float(result['polar_orders'][i]), 4)   for i in frames_idx],
            'transport_effs': [round(float(result['transport_effs'][i]), 4) for i in frames_idx],
            'occupancies':    [round(float(result['occupancies'][i]), 4)    for i in frames_idx],
            'time_avg_phi':   round(result['time_avg_phi'], 4),
            'time_avg_occ':   round(result['time_avg_occ'], 4),
            'persist_length': round(float(result['persist_length']), 3) if result['persist_length'] < 1e5 else 9999,
            'elapsed':        round(result['elapsed'], 2),
            # Final frame positions & orientations for display
            'final_pos':   result['positions_hist'][-1].tolist(),
            'final_theta': result['theta_hist'][-1].tolist(),
            'final_I':     result['I_local_hist'][-1].tolist(),
            'n_frames':    len(frames_idx),
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    _load_sim()
    print("🚀  PJPS Dashboard running at http://localhost:7860")
    app.run(host='0.0.0.0', port=7860, debug=False, threaded=True)
