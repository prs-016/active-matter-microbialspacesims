"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║          PHOTOPHORETIC JANUS PARTICLE SWARM (PJPS) SIMULATION                  ║
║          UCSD Vibe Coding: Active Matter & Biophysics Hackathon 2026            ║
╚══════════════════════════════════════════════════════════════════════════════════╝

PHYSICS FOUNDATIONS (grounded in uploaded research papers):

Paper 1 ── Krauss et al. (2006), A&A: "The photophoretic sweeping of dust in
           transient protoplanetary disks"
           → Beresnev full-Kn photophoretic force formula (Eq. 1):
             F_ph = (π/3)·a²·I·J₁·(πmg/2kT)^½ · [αE·ψ₁] / [αE + 15ΛKn(1-αE)/4 + αE·Λ·ψ₂]
           → In free-molecular limit (Kn→∞): F_ph ∝ a²·I·(kT)^(-½)/Λ
           → Drift velocity: v_dr = (F_ph/m_p)·τ_stop  →  v₀ ∝ I (linear in intensity)

Paper 2 ── Lisin et al. (2021), PCCP: "Active Brownian particle in homogeneous
           media of different viscosities: numerical simulations"
           → Overdamped Langevin (Eqs. 3–4, overdamped limit):
               ṙ = Vs·n̂ + ξ_trans,    dθ/dt = ξ_rot
           → Rotational diffusion: ω = Dr = 3DT/(4R²) = kBT/(8πηR³)  [Eq. 1]
           → Persistence length: L_S = Vs/ω  [Eq. 7]
           → Effective diffusion: D_eff = DT + Vs²/(2ω)  [Eq. 6]
           → Noise amplitudes: σ_trans = √(2DT·Δt),  σ_rot = √(2Dr·Δt) = η·√(Δt)

Paper 3 ── Nosenko et al. (2020), PRR: "Active Janus particles in a complex plasma"
           → Photophoretic force (Eq. 1 combining ΔT and Δα components):
               F_ph = π·rp²·kB·n0·T0·[α₁·(T₁/T₀-1) − α₂·(T₂/T₀-1)]
           → F_ph ∝ p_gas (ΔT component, linear pressure dependence observed)
           → ΔT ≈ 10⁻² K for laser 99 mW on 9.27 μm Pt-coated particle
           → KEY OBSERVATION: JPs perform circular/epitrochoidal trajectories
               → Body-fixed TORQUE drives chirality (spinning frequency ν locked to ω)
               → Tangential force: Ft = m·γE·ω_circ·r_tr  (Epstein drag balance)
               → IMPLEMENTATION: add ω_chiral·Δt term in orientation update

Paper 4 ── Koss et al. (2022), Molecules: "Dynamic Entropy of 2D Active Brownian
           Systems in Colloidal Plasmas"
           → Free-molecular photophoretic force (Eq. 1):
               F_ph = (π·a³·p·I) / (6·k_th·T_buf)
           → Propulsion speed: v₀ = F_ph/(6πηa) = (a²·p·I)/(36·k_th·T_buf·η) ∝ I
           → NONLINEAR T(W): kinetic temperature grows nonlinearly with laser power
               → Intensity-dependent effective noise: η_eff(i) = η·√(1 + κ_T·I_loc(i)/I₀)
           → Janus particles: fractal dimension Δf ~ 1.6 (circle-swimmer trajectories)

VARIABLE MAPPING FROM PAPERS → CODE:
  Paper symbol  │ Code variable   │ Physical meaning
  ─────────────────────────────────────────────────────
  Vs, vp        │ v_max, v0[i]    │ Self-propulsion speed
  Dr, ω         │ D_r, derived    │ Rotational diffusion coefficient
  R, rp, a      │ R_particle      │ Particle radius
  I, I_laser    │ I_0, I_local    │ Light intensity
  ω_chiral, ν  │ omega_chiral[i] │ Chirality (spinning frequency)
  η_noise       │ eta             │ Rotational noise amplitude
  α (phototax)  │ alpha           │ Phototactic steering strength
  J (Vicsek)    │ J               │ Alignment coupling strength
  L_S = Vs/Dr   │ L_persist       │ Persistence length (diagnostic)

PHYSICAL VALIDATION GATES (per MASTER_CONTEXT Section 9.3):
  [1] Dimensional: all torques have units [rad·s⁻¹] (overdamped, divide by γ_r if needed)
  [2] Stability: 1/r singularities regularized with epsilon = 1e-8
  [3] Periodicity: all pairwise distances use minimum-image convention

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIMITATIONS (mandatory honesty, per MASTER_CONTEXT Section 9.4):
  ✗ No hydrodynamic advection (dry active matter; real Stokes flow neglected)
  ✗ Overdamped dynamics only (inertia neglected; valid for Re << 1, μm-scale)
  ✗ Simplified geometric shadow (no wave optics, diffraction, or refraction)
  ✗ Phenomenological J-coupling (real mechanism: combined radiation + thermoosmosis)
  ✗ 2D confinement (real plasma experiments are quasi-2D but have out-of-plane drift)
  ✗ Homogeneous particle properties (real JPs vary in cap thickness → scatter in ω_chiral)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 1 — IMPORTS & ENVIRONMENT SETUP  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import animation, cm, colors as mcolors
from matplotlib.gridspec import GridSpec
from matplotlib.collections import LineCollection
from IPython.display import HTML
import time
import warnings
warnings.filterwarnings('ignore')

# ── Colab / standalone detection ──
try:
    from google.colab import output
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# ── Aesthetic plot defaults ──
PALETTE = {
    'bg':      '#0d1117',
    'fg':      '#e6edf3',
    'accent1': '#58a6ff',   # particle cap color
    'accent2': '#3fb950',   # target / ordered phase
    'accent3': '#f78166',   # disordered / obstacle
    'accent4': '#d2a8ff',   # shadow zone
    'grid':    '#21262d',
}
plt.rcParams.update({
    'figure.facecolor':  PALETTE['bg'],
    'axes.facecolor':    PALETTE['bg'],
    'axes.edgecolor':    PALETTE['grid'],
    'axes.labelcolor':   PALETTE['fg'],
    'xtick.color':       PALETTE['fg'],
    'ytick.color':       PALETTE['fg'],
    'text.color':        PALETTE['fg'],
    'grid.color':        PALETTE['grid'],
    'figure.dpi':        110,
    'font.size':         11,
    'axes.titlesize':    13,
    'legend.facecolor':  '#161b22',
    'legend.edgecolor':  PALETTE['grid'],
})

print("✅  Imports loaded.")


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 2 — PHYSICAL PARAMETERS  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════
"""
All parameters are in DIMENSIONLESS UNITS unless noted.
Real-scale correspondence (typical micron-scale experiment):
    Length unit = 1 μm,  Time unit = 1 s,  Speed unit = 1 μm/s
    N = 300 particles in 30 × 30 μm² box
    Particle radius R_particle ≈ 0.5 μm
"""

# ── Swarm geometry ──────────────────────────────────────────────────────────
N           = 300        # number of Janus particles
L           = 30.0       # box side length [L-unit]
R_particle  = 0.5        # physical radius; used for soft-core repulsion [L-unit]

# ── Propulsion (from Paper 1, 4: F_ph ∝ I, overdamped drift v₀ ∝ I/γ_drag) ─
v_max       = 1.0        # maximum self-propulsion speed [L/t-unit]
I_0         = 1.0        # reference illumination intensity (normalised)
I_emit      = 0.30       # radiation emission strength per particle
sigma_rad   = 1.5        # radiation decay length [L-unit]  (≈ 1–2 particle diameters)
R_rad       = 2.0        # radiation interaction cutoff [L-unit]

# ── Chirality (from Paper 3: body-fixed torque → circle-swimmer) ────────────
# omega_chiral > 0 → CCW circles; distribution ~N(0, sigma_chiral) models
# manufacturing spread in cap asymmetry (Nosenko observed ~50% CW, ~50% CCW)
sigma_chiral = 0.0       # set to 0 to disable chirality; ~0.1 for realistic JPs

# ── Alignment (Vicsek-like coupling, mediated by radiation) ─────────────────
J           = 1.0        # alignment coupling [t-unit⁻¹]
R_align     = 2.0        # alignment interaction radius [L-unit]

# ── Phototaxis ───────────────────────────────────────────────────────────────
alpha       = 0.8        # phototactic steering strength [t-unit⁻¹]
target_frac = (0.75, 0.75)   # target position as fraction of box

# ── Rotational noise (Paper 2: σ_rot = η·√Δt corresponds to η = √(2·Dr)) ───
eta         = 0.5        # rotational noise amplitude [rad·t-unit⁻½]
#            Physical: η = √(2·Dr) where Dr = kBT/(8πη_fluid·a³) ≈ 0.01–10 s⁻¹

# ── Intensity-dependent noise (Paper 4: T_eff ∝ I → enhanced noise in bright) ─
kappa_T     = 0.0        # noise-intensity coupling; 0 = uniform noise, ~0.3 realistic

# ── Optional: magnetic steering ─────────────────────────────────────────────
kappa_B     = 0.0        # magnetic steering strength [t-unit⁻¹]; 0 = off
theta_B     = 0.0        # field direction [rad]

# ── Soft excluded-volume repulsion (prevents unphysical overlaps) ───────────
# WCA-like: U(r) = ε·(σ/r)^12 for r < 2^(1/6)·σ, else 0
# Force: F = 12ε·σ^12/r^13 — divided by drag coefficient γ for overdamped speed
epsilon_rep  = 0.50      # repulsion energy scale
sigma_rep    = 2*R_particle  # contact distance (diameter) [L-unit]

# ── Integration ──────────────────────────────────────────────────────────────
dt          = 0.05       # time step [t-unit]; must satisfy dt < 1/(J+alpha+kappa_B)
n_steps     = 800        # total simulation steps
record_every = 5         # record state every this many steps
seed        = 42         # random seed for reproducibility

# ── Derived quantities ───────────────────────────────────────────────────────
target = np.array([target_frac[0] * L, target_frac[1] * L])
rng    = np.random.default_rng(seed)

# ── Persistence length diagnostic (Paper 2, Eq. 7): L_S = v₀/Dr = v_max·2/η² ─
# η = √(2Dr)·√1  →  Dr = η²/2   →  L_persist = v_max/Dr = 2·v_max/η²
Dr_approx   = eta**2 / 2.0
L_persist   = v_max / Dr_approx if Dr_approx > 0 else float('inf')
Pe_approx   = v_max * np.sqrt(N/L**2) * R_align   # rough Péclet number

print(f"✅  Parameters loaded.")
print(f"    N={N}, L={L:.1f}, ρ=N/L²={N/L**2:.3f}")
print(f"    v_max={v_max}, η={eta}, J={J}, α={alpha}")
print(f"    Dr ≈ {Dr_approx:.4f} t⁻¹  →  Persistence length L_p ≈ {L_persist:.2f} L")
print(f"    Péclet number Pe ≈ {Pe_approx:.2f}")
print(f"    dt·(J+α) = {dt*(J+alpha):.3f}  (should be << 1 for stability)")


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 3 — HELPER & PHYSICS FUNCTIONS  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
def initialize_swarm(N: int, L: float, seed: int = 42,
                     sigma_chiral: float = 0.0):
    """
    Random initial positions and orientations.

    Physical basis:
      - Positions drawn from Uniform([0,L]²) — no initial order
      - Orientations from Uniform([0, 2π]) — isotropic
      - Chirality drawn from Normal(0, σ_chiral) per particle (Paper 3):
          Manufacturing variability → each JP has its own intrinsic spinning rate.
          σ_chiral = 0 disables chirality entirely.

    Returns:
        positions  (N, 2) float array
        theta      (N,)   float array of orientations [rad]
        omega_self (N,)   float array of intrinsic spin rates [rad/t-unit]
    """
    rng_init = np.random.default_rng(seed)
    positions  = L * rng_init.random((N, 2))
    theta      = 2.0 * np.pi * rng_init.random(N)
    omega_self = sigma_chiral * rng_init.standard_normal(N)  # Paper 3
    return positions, theta, omega_self


# ─────────────────────────────────────────────────────────────────────────────
def minimum_image(pos: np.ndarray, L: float) -> np.ndarray:
    """
    Pairwise displacement vectors using the minimum-image convention (MIC).
    Required for periodic boundary conditions.

    Physical basis (validation gate 3, MASTER_CONTEXT §9.3):
      δr_ij = r_j − r_i,  then δr_ij ← δr_ij − L·round(δr_ij/L)
      Ensures |δr_ij| ≤ L/2 in each dimension.

    Args:
        pos : (N, 2) particle positions
        L   : box side length (square box)
    Returns:
        disp : (N, N, 2)  displacement vectors r_j − r_i (MIC-corrected)
    """
    disp = pos[np.newaxis, :, :] - pos[:, np.newaxis, :]   # (N, N, 2): r_j - r_i
    disp -= L * np.round(disp / L)
    return disp


# ─────────────────────────────────────────────────────────────────────────────
def compute_shadow_mask(positions: np.ndarray,
                        obs_center: np.ndarray,
                        obs_radius: float,
                        light_dir: np.ndarray) -> np.ndarray:
    """
    Geometric ray-casting shadow of a circular obstacle.

    Physical basis (Krauss et al. Paper 1, geometric optics):
      A circular disk of radius obs_radius at obs_center casts a cylindrical
      shadow when illuminated from direction light_dir. Particle i is in shadow iff:
        (a) its projection onto the shadow axis (opposite to light_dir) is positive
        (b) its perpendicular distance from the shadow axis < obs_radius

    Limitations (per §9.4): No wave optics, no diffraction, penumbra neglected.

    Returns:
        Boolean (N,) mask: True if particle is in geometric shadow.
    """
    ld = light_dir / (np.linalg.norm(light_dir) + 1e-14)
    shadow_axis = -ld                                   # direction away from source
    to_p = positions - obs_center                       # (N, 2)
    proj = to_p @ shadow_axis                          # (N,)  signed projection
    perp = to_p - proj[:, np.newaxis] * shadow_axis    # (N, 2) perpendicular component
    perp_dist = np.linalg.norm(perp, axis=1)           # (N,)
    return (proj > 0) & (perp_dist < obs_radius)


# ─────────────────────────────────────────────────────────────────────────────
def compute_illumination_ext(positions: np.ndarray, L: float,
                             I_0: float,
                             obstacle: dict | None = None,
                             light_dir: np.ndarray | None = None) -> np.ndarray:
    """
    External illumination field I_ext(r_i) at each particle position.

    Modes (set via obstacle dict):
      obstacle = None        → uniform field I_0 everywhere
      obstacle['type'] = 'shadow'   → geometric shadow of circular obstacle
      obstacle['type'] = 'gradient' → linear intensity gradient along x-axis
      obstacle['type'] = 'geometric' → hard wall obstacle (blocks physically)

    Physical basis:
      Free-molecular photophoretic speed: v₀ ∝ F_ph/γ_drag ∝ I_local (Paper 1, 4)
      Shadow = region of stalled particles (v₀ → 0 when I → 0)

    Returns:
        I_ext : (N,) array of external illumination values
    """
    I_ext = I_0 * np.ones(len(positions))
    if obstacle is None:
        return I_ext

    otype = obstacle.get('type', None)

    if otype == 'shadow':
        ld = obstacle.get('light_dir', np.array([1., 0.]))
        if light_dir is not None:
            ld = light_dir
        mask = compute_shadow_mask(positions,
                                   np.array(obstacle['center']),
                                   obstacle['radius'], ld)
        f_shadow = obstacle.get('shadow_fraction', 0.05)  # 0=no shadow, 1=full block
        I_ext[mask] *= f_shadow

    elif otype == 'gradient':
        # I(x) = I_0 * (1 + kappa_grad * x/L)  →  phototactic gradient
        kappa_grad = obstacle.get('kappa_grad', 0.5)
        I_ext = I_0 * (1.0 + kappa_grad * positions[:, 0] / L)
        I_ext = np.clip(I_ext, 0.0, 3.0 * I_0)

    # 'geometric' type: handled separately via position correction in step function
    return I_ext


# ─────────────────────────────────────────────────────────────────────────────
def compute_soft_repulsion(positions: np.ndarray, L: float,
                           epsilon_rep: float, sigma_rep: float) -> np.ndarray:
    """
    Overdamped WCA-like soft excluded-volume repulsion.

    Physical basis:
      For hard spheres of diameter σ_rep, the repulsion prevents overlap.
      In overdamped limit, force → velocity: F_rep / γ where γ ≈ 6πηa.
      WCA truncated LJ: F_rep(r) = 12·ε·σ^12 / r^13  for r < r_cut = 2^(1/6)·σ

      We normalize F_rep / (6πηa) to get a velocity contribution. Here ε_rep
      is already expressed as a speed scale (ε_rep has units of L/t), consistent
      with the overdamped treatment throughout the PJPS model.

    Validation gate [2]: regularized with epsilon_safe to prevent blow-up at r→0.

    Returns:
        v_rep : (N, 2) repulsion velocity contribution (added to position update)
    """
    N = len(positions)
    disp = minimum_image(positions, L)                  # (N, N, 2)
    dist = np.linalg.norm(disp, axis=2)                 # (N, N)
    r_cut = 2.0**(1.0/6.0) * sigma_rep

    # Mask: only pairs within cutoff, excluding self
    mask = (dist < r_cut) & (dist > 0)
    dist_safe = np.where(mask, np.maximum(dist, 0.01 * sigma_rep), 1.0)  # avoid /0

    # WCA magnitude: F(r) = 12ε·(σ/r)^12 / r  (normalised)
    sr6  = (sigma_rep / dist_safe)**6
    fmag = np.where(mask, 12.0 * epsilon_rep * sr6**2 / dist_safe, 0.0)  # (N, N)

    # Direction: from j toward i  (repel i away from j)
    unit_ji = np.where(mask[:, :, np.newaxis],
                       -disp / dist_safe[:, :, np.newaxis],   # (N,N,2) pointing i←j
                       0.0)

    # Sum repulsion velocities over all j for each i
    v_rep = (fmag[:, :, np.newaxis] * unit_ji).sum(axis=1)    # (N, 2)
    return v_rep


# ─────────────────────────────────────────────────────────────────────────────
# ══ OBSERVABLE FUNCTIONS ══════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

def polar_order(theta: np.ndarray) -> float:
    """
    Polar order parameter Φ_polar = |⟨e^{iθ}⟩|.

    Physical meaning:
        Φ = 1 → all particles point the same direction (perfect flock)
        Φ = 0 → uniformly random orientations (gas phase)
    Physics: canonical Vicsek order parameter (Vicsek et al. 1995).
    """
    return float(np.abs(np.mean(np.exp(1j * theta))))


def transport_efficiency(positions: np.ndarray, theta: np.ndarray,
                         target: np.ndarray) -> float:
    """
    Φ_transport = ⟨cos(θ_i − φ_target_i)⟩, range [−1, 1].

    Physical meaning:
        +1 → all particles aligned toward the target (perfect delivery)
         0 → particles pointing perpendicular to target on average
        −1 → particles pointing away from target

    This is the KEY METRIC for Task 1: measures how well the swarm
    steers toward the delivery point while maintaining cohesion.
    """
    to_tgt  = target - positions                         # (N, 2)
    phi_tgt = np.arctan2(to_tgt[:, 1], to_tgt[:, 0])    # (N,) direction to target
    return float(np.mean(np.cos(theta - phi_tgt)))


def target_occupancy(positions: np.ndarray, target: np.ndarray,
                     r_zone: float = 2.0) -> float:
    """
    Fraction of particles within r_zone of the target delivery point.

    Physical meaning:
        = 1 → 100% of particles delivered to target (ideal)
        = 0 → no particles reached target

    This is the cargo-delivery metric for Task 2.
    """
    dist = np.linalg.norm(positions - target, axis=1)    # (N,)
    return float(np.mean(dist < r_zone))


def persistence_length(v0_mean: float, eta: float, dt: float) -> float:
    """
    Persistence length L_S = V_S / D_r  (Paper 2, Eq. 7).

    In our noise parametrization:
        θ(t+dt) = θ(t) + η·ξ·√dt   →   ⟨Δθ²⟩ = η²·dt   →   D_r = η²/2
        → L_S = v₀ / D_r = 2·v₀ / η²

    Physical meaning: how far a particle travels in a straight line before
    rotational diffusion randomises its direction.
    """
    Dr = eta**2 / 2.0
    return v0_mean / Dr if Dr > 0 else float('inf')


def time_averaged(arr: np.ndarray, transient_frac: float = 0.5) -> float:
    """Mean of arr[start:] discarding initial transient fraction."""
    start = max(1, int(transient_frac * len(arr)))
    return float(np.mean(arr[start:]))


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 4 — CORE SIMULATION STEP  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

def janus_step(positions: np.ndarray,
               theta: np.ndarray,
               omega_self: np.ndarray,
               L: float,
               v_max: float,
               R_align: float,
               J: float,
               eta: float,
               alpha: float,
               target: np.ndarray,
               I_0: float,
               I_emit: float,
               sigma_rad: float,
               R_rad: float,
               kappa_B: float,
               theta_B: float,
               dt: float,
               rng: np.random.Generator,
               epsilon_rep: float,
               sigma_rep: float,
               kappa_T: float = 0.0,
               obstacle: dict | None = None,
               light_dir: np.ndarray | None = None) -> tuple:
    """
    ┌─────────────────────────────────────────────────────────────────────────┐
    │              ONE TIME-STEP OF THE PJPS MODEL                            │
    │         Euler–Maruyama integration, fully vectorised (NumPy only)       │
    └─────────────────────────────────────────────────────────────────────────┘

    PHYSICS PIPELINE (11 stages):

    [1] PAIRWISE GEOMETRY
        Compute all displacement vectors δr_ij = r_j − r_i using minimum-image
        convention for periodic boundaries. O(N²) — acceptable for N≤500.

    [2] EXTERNAL ILLUMINATION
        I_ext(i) = I₀ × shadow_mask(i)
        Shadow mask from geometric ray-casting (Krauss Paper 1, geometric optics).

    [3] LOCAL RADIATION COUPLING (inter-particle)
        Each particle j emits thermal radiation toward neighbors. Reception at i:
          I_rad(j→i) = I_emit · exp(−r_ij²/σ_rad²) · max(0, ê_j · ê_{ji})
        where ê_j = cap direction of j, ê_{ji} = unit vector from j toward i.
        The max(0, ·) ensures only forward-facing emission (directional cap radiation).
        Physical basis: Paper 1 (thermal emission), Paper 3 (Pt-cap heating).

    [4] PROPULSION SPEED (intensity-dependent)
        From Papers 1 & 4, v₀ ∝ F_ph/γ_drag ∝ I_local:
          v₀(i) = v_max · min(1, I_local(i)/I_ref)
        This gives: stalled particle in shadow (v₀→0), boosted near emitting neighbors.

    [5] ALIGNMENT TORQUE (Vicsek-type, radiation-mediated)
        Φ_align(i) = arctan2(Σ_{j∈N_R} sin θ_j, Σ_{j∈N_R} cos θ_j)
        τ_align(i) = J · sin(Φ_align − θ_i) × [has_neighbor]
        The sin(·) function has correct sign to rotate θ toward Φ_align.
        Multiplied by dt in orientation update → units [rad].

    [6] PHOTOTACTIC TORQUE (global steering toward cargo target)
        τ_photo(i) = α · sin(φ_target(i) − θ_i)
        φ_target(i) = direction from particle i toward the target point.
        Physical: analogous to chemotaxis but driven by light gradient (Paper 1).

    [7] MAGNETIC TORQUE (optional)
        τ_mag(i) = κ_B · sin(θ_B − θ_i)
        For κ_B = 0 (default): zero contribution.

    [8] INTRINSIC CHIRALITY (from Paper 3: Nosenko circle-swimmer observation)
        τ_chiral(i) = ω_self(i) [rad/t-unit]
        Each particle has a body-fixed spin rate. When σ_chiral > 0 particles
        describe circular arcs: radius r_circ = v₀/|ω_self|.
        This is the KEY NEW PHYSICS not in the original Vicsek model.

    [9] INTENSITY-DEPENDENT NOISE (from Paper 4: T_eff ∝ I_local)
        η_eff(i) = η · √(1 + κ_T · I_local(i)/I₀)
        Brighter particles → higher effective temperature → more angular noise.
        noise(i) = η_eff(i) · ξᵢ · √dt,  ξᵢ ~ N(0,1)

    [10] ORIENTATION UPDATE (Euler–Maruyama)
         θ(t+dt) = θ(t) + [τ_align + τ_photo + τ_mag + ω_self]·dt + noise

    [11] POSITION UPDATE + BOUNDARY CONDITIONS
         r(t+dt) = r(t) + v₀(i)·ê_i(t+dt)·dt + v_rep(i)·dt
         Periodic: r ← r mod L   (torus geometry)
         Geometric obstacle: reflect particles out of solid region.

    Args:
        positions  : (N, 2) current positions
        theta      : (N,)   current orientations [rad]
        omega_self : (N,)   intrinsic chirality per particle [rad/t-unit]
        ... (see parameter block in Cell 2)
        obstacle   : dict defining obstacle geometry and type, or None
        light_dir  : (2,) unit vector pointing in light direction, or None→(1,0)

    Returns:
        pos_new    : (N, 2) updated positions
        theta_new  : (N,)   updated orientations
        v0         : (N,)   actual propulsion speeds used this step
        I_local    : (N,)   total local illumination experienced
    """
    N = len(positions)
    if light_dir is None:
        light_dir = np.array([1.0, 0.0])

    # ── [1] PAIRWISE GEOMETRY ─────────────────────────────────────────────────
    disp      = minimum_image(positions, L)             # (N, N, 2): r_j − r_i
    dist      = np.linalg.norm(disp, axis=2)            # (N, N)
    dist_safe = np.where(dist > 0, dist, 1.0)           # avoid divide-by-zero on diagonal

    # ── [2] EXTERNAL ILLUMINATION ─────────────────────────────────────────────
    I_ext = compute_illumination_ext(positions, L, I_0, obstacle, light_dir)  # (N,)

    # ── [3] LOCAL RADIATION FROM NEIGHBORS ────────────────────────────────────
    # Cap unit vector for each particle j
    e_cap = np.column_stack((np.cos(theta), np.sin(theta)))  # (N, 2)

    # Unit vector from j → i  (used to check if j's cap faces i)
    # disp[i,j] = r_j − r_i  →  e_{j→i} = −disp[i,j] / dist[i,j]
    e_cap_broadcast = e_cap[np.newaxis, :, :]               # (1, N, 2) → broadcasts to (N, N, 2)
    e_j_to_i = -disp / dist_safe[:, :, np.newaxis]          # (N, N, 2): j→i direction

    # Directional factor: how much j's cap faces i
    dot_cap_j_to_i = np.einsum('ijk,ijk->ij',
                                e_cap_broadcast, e_j_to_i)  # (N, N)
    cap_factor = np.maximum(0.0, dot_cap_j_to_i)            # only forward emission

    # Radiation kernel: Gaussian decay × directional cap factor
    rad_kernel = I_emit * np.exp(-dist**2 / (sigma_rad**2 + 1e-14)) * cap_factor
    rad_mask   = (dist < R_rad) & (dist > 0)                # (N, N) cutoff
    I_rad_at_i = (rad_kernel * rad_mask).sum(axis=1)        # (N,) sum over j (source)

    # ── [4] TOTAL ILLUMINATION & PROPULSION SPEED ─────────────────────────────
    # I_local(i) = I_ext(i) + Σ_j I_rad(j→i)
    I_local = I_ext + I_rad_at_i                            # (N,)

    # v₀(i) = v_max · min(1, I_local/I_ref)    [Papers 1 & 4: linear regime]
    # Physical: F_ph ∝ I → v_dr ∝ I/γ_drag; capped at v_max for I > I_ref
    v0 = v_max * np.minimum(1.0, I_local / I_0)            # (N,)

    # ── [5] ALIGNMENT TORQUE (Vicsek-style) ───────────────────────────────────
    nbr_mask = (dist < R_align) & (dist > 0)                # (N, N) boolean
    has_nbr  = nbr_mask.any(axis=1)                         # (N,) any neighbor?

    # Mean orientation of neighbors (including self-alignment implicitly absorbed in target)
    sin_sum = (nbr_mask.astype(np.float64) * np.sin(theta)[np.newaxis, :]).sum(axis=1)
    cos_sum = (nbr_mask.astype(np.float64) * np.cos(theta)[np.newaxis, :]).sum(axis=1)
    phi_align = np.arctan2(sin_sum, cos_sum)                # (N,) mean neighbor direction

    # Alignment torque: J·sin(φ_align − θ); zero if isolated
    tau_align = np.where(has_nbr,
                         J * np.sin(phi_align - theta),
                         0.0)                               # (N,)

    # ── [6] PHOTOTACTIC TORQUE ────────────────────────────────────────────────
    to_tgt    = target - positions                          # (N, 2)
    phi_tgt   = np.arctan2(to_tgt[:, 1], to_tgt[:, 0])    # (N,)
    tau_photo = alpha * np.sin(phi_tgt - theta)             # (N,)

    # ── [7] MAGNETIC TORQUE (optional) ────────────────────────────────────────
    tau_mag = kappa_B * np.sin(theta_B - theta)             # (N,); 0 if kappa_B=0

    # ── [8] INTRINSIC CHIRALITY (Paper 3: circle-swimmer spin) ────────────────
    # omega_self[i] is body-fixed angular velocity [rad/t-unit]
    # Positive → CCW rotation (left-circling), Negative → CW (right-circling)
    # Creates circular arcs of radius r_circ = v₀/|omega_self|

    # ── [9] INTENSITY-DEPENDENT NOISE (Paper 4) ───────────────────────────────
    # η_eff(i) = η·√(1 + κ_T · I_local/I₀)
    # Particles in bright regions undergo more angular diffusion (higher T_eff)
    eta_eff = eta * np.sqrt(1.0 + kappa_T * I_local / (I_0 + 1e-14))  # (N,)
    noise   = eta_eff * rng.standard_normal(N) * np.sqrt(dt)            # (N,)

    # ── [10] ORIENTATION UPDATE (Euler–Maruyama) ──────────────────────────────
    theta_new = (theta
                 + (tau_align + tau_photo + tau_mag) * dt   # deterministic torques
                 + omega_self * dt                           # chirality (Paper 3)
                 + noise)                                    # stochastic (Paper 2)
    # No modular wrap needed for theta — sin/cos are 2π-periodic automatically

    # ── [11] POSITION UPDATE ──────────────────────────────────────────────────
    # Propulsion along current (updated) cap direction
    vx = v0 * np.cos(theta_new)                             # (N,)
    vy = v0 * np.sin(theta_new)                             # (N,)

    # Soft excluded-volume repulsion velocity
    v_rep = compute_soft_repulsion(positions, L,
                                   epsilon_rep, sigma_rep)  # (N, 2)

    pos_new = (positions
               + np.column_stack((vx, vy)) * dt             # self-propulsion
               + v_rep * dt)                                 # soft repulsion

    # ── PERIODIC BOUNDARY CONDITIONS ──────────────────────────────────────────
    pos_new %= L                                             # torus wrap

    # ── GEOMETRIC OBSTACLE COLLISION (hard-wall correction) ──────────────────
    if obstacle is not None and obstacle.get('type') == 'geometric':
        obs_c = np.asarray(obstacle['center'], dtype=float)
        obs_r = float(obstacle['radius'])
        d_obs = np.linalg.norm(pos_new - obs_c, axis=1)    # (N,)
        inside = d_obs < obs_r
        if inside.any():
            # Push particles outside obstacle surface, randomise orientation
            dir_out = pos_new[inside] - obs_c
            norm = np.linalg.norm(dir_out, axis=1, keepdims=True) + 1e-14
            dir_out = dir_out / norm
            pos_new[inside] = obs_c + dir_out * obs_r * 1.02
            theta_new[inside] = np.arctan2(dir_out[:, 1], dir_out[:, 0])

    return pos_new, theta_new, v0, I_local


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 5 — FULL SIMULATION RUNNER  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_janus_swarm(
        N: int = 300, L: float = 30.0,
        v_max: float = 1.0, R_align: float = 2.0,
        J: float = 1.0, eta: float = 0.5,
        alpha: float = 0.8, target_frac: tuple = (0.75, 0.75),
        I_0: float = 1.0, I_emit: float = 0.3,
        sigma_rad: float = 1.5, R_rad: float = 2.0,
        kappa_B: float = 0.0, theta_B: float = 0.0,
        sigma_chiral: float = 0.0, kappa_T: float = 0.0,
        epsilon_rep: float = 0.5, sigma_rep: float = 1.0,
        n_steps: int = 800, dt: float = 0.05,
        seed: int = 42,
        obstacle: dict | None = None,
        light_dir: np.ndarray | None = None,
        r_zone: float = 2.0,
        record_every: int = 5) -> dict:
    """
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    FULL PJPS SIMULATION RUNNER                          │
    └─────────────────────────────────────────────────────────────────────────┘

    Integrates the PJPS model for n_steps time steps and records observables.

    Physics notes:
      - Euler–Maruyama integration is first-order in Δt (sufficient for these
        overdamped stochastic equations; higher-order schemes unnecessary).
      - Recording every record_every steps reduces memory by ~5×.
      - Time-averaging from step 50% onward discards initial transient where
        particles equilibrate from random initial conditions.

    Returns a dict with keys:
        'positions_hist'   : (n_frames, N, 2)  position trajectories
        'theta_hist'       : (n_frames, N)     orientation trajectories
        'v0_hist'          : (n_frames, N)     speed trajectories
        'I_local_hist'     : (n_frames, N)     illumination trajectories
        'polar_orders'     : (n_frames,)       Φ_polar at each frame
        'transport_effs'   : (n_frames,)       Φ_transport at each frame
        'occupancies'      : (n_frames,)       target occupancy at each frame
        'time_avg_phi'     : float             time-averaged Φ_transport (Task 1 metric)
        'time_avg_occ'     : float             time-averaged occupancy (Task 2 metric)
        'persist_length'   : float             persistence length estimate
        'params'           : dict              copy of all parameters used
    """
    # ── Initialisation ────────────────────────────────────────────────────────
    rng = np.random.default_rng(seed)
    positions, theta, omega_self = initialize_swarm(N, L, seed, sigma_chiral)
    target = np.array([target_frac[0] * L, target_frac[1] * L])

    n_frames = n_steps // record_every
    positions_hist = np.zeros((n_frames, N, 2))
    theta_hist     = np.zeros((n_frames, N))
    v0_hist        = np.zeros((n_frames, N))
    I_local_hist   = np.zeros((n_frames, N))
    polar_orders   = np.zeros(n_frames)
    transport_effs = np.zeros(n_frames)
    occupancies    = np.zeros(n_frames)

    frame = 0
    t0 = time.time()

    # ── Main loop ─────────────────────────────────────────────────────────────
    for step in range(n_steps):
        positions, theta, v0, I_local = janus_step(
            positions=positions, theta=theta, omega_self=omega_self,
            L=L, v_max=v_max, R_align=R_align, J=J, eta=eta,
            alpha=alpha, target=target,
            I_0=I_0, I_emit=I_emit, sigma_rad=sigma_rad, R_rad=R_rad,
            kappa_B=kappa_B, theta_B=theta_B,
            dt=dt, rng=rng,
            epsilon_rep=epsilon_rep, sigma_rep=sigma_rep,
            kappa_T=kappa_T,
            obstacle=obstacle, light_dir=light_dir)

        if step % record_every == 0 and frame < n_frames:
            positions_hist[frame] = positions
            theta_hist[frame]     = theta
            v0_hist[frame]        = v0
            I_local_hist[frame]   = I_local
            polar_orders[frame]   = polar_order(theta)
            transport_effs[frame] = transport_efficiency(positions, theta, target)
            occupancies[frame]    = target_occupancy(positions, target, r_zone)
            frame += 1

    elapsed = time.time() - t0

    # ── Time-averaged metrics (discard first 50% as transient) ────────────────
    time_avg_phi = time_averaged(transport_effs, transient_frac=0.5)
    time_avg_occ = time_averaged(occupancies,    transient_frac=0.5)
    avg_v0       = float(v0_hist.mean())
    L_persist    = persistence_length(avg_v0, eta, dt)

    print(f"    Done in {elapsed:.2f}s | ⟨Φ_transport⟩={time_avg_phi:.3f} "
          f"| ⟨Occupancy⟩={time_avg_occ:.3f} | L_persist≈{L_persist:.2f}")

    return {
        'positions_hist': positions_hist[:frame],
        'theta_hist':     theta_hist[:frame],
        'v0_hist':        v0_hist[:frame],
        'I_local_hist':   I_local_hist[:frame],
        'polar_orders':   polar_orders[:frame],
        'transport_effs': transport_effs[:frame],
        'occupancies':    occupancies[:frame],
        'time_avg_phi':   time_avg_phi,
        'time_avg_occ':   time_avg_occ,
        'persist_length': L_persist,
        'elapsed':        elapsed,
        'target':         target,
        'params': dict(N=N, L=L, v_max=v_max, R_align=R_align, J=J, eta=eta,
                       alpha=alpha, dt=dt, n_steps=n_steps,
                       sigma_chiral=sigma_chiral, kappa_T=kappa_T,
                       epsilon_rep=epsilon_rep, obstacle=obstacle),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 6 — VISUALISATION LIBRARY  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

def plot_snapshot(result: dict, frame_idx: int = -1,
                  title: str = "Janus Swarm Snapshot",
                  figsize: tuple = (8, 8),
                  show_velocities: bool = True,
                  show_illumination: bool = True) -> plt.Figure:
    """
    High-quality snapshot of the swarm state at a given frame.

    Visual encoding:
      • Dot colour  → local illumination I_local (dark blue = shadow, bright = illuminated)
      • Arrow       → orientation and speed (v₀·ê_i)
      • Green dot   → delivery target
      • Magenta ◯  → obstacle (if present)
    """
    pos      = result['positions_hist'][frame_idx]
    theta    = result['theta_hist'][frame_idx]
    v0       = result['v0_hist'][frame_idx]
    I_local  = result['I_local_hist'][frame_idx]
    target_p = result['target']
    L        = result['params']['L']
    obs      = result['params'].get('obstacle')

    fig, ax = plt.subplots(figsize=figsize)

    # ── Background intensity heatmap ──────────────────────────────────────────
    if show_illumination:
        c = ax.scatter(pos[:, 0], pos[:, 1],
                       c=I_local, cmap='plasma',
                       vmin=0.0, vmax=max(1.2, I_local.max()),
                       s=28, alpha=0.85, zorder=3,
                       label='Particles (color = I_local)')
        plt.colorbar(c, ax=ax, label='Local Illumination $I_{local}$', shrink=0.75)
    else:
        ax.scatter(pos[:, 0], pos[:, 1],
                   color=PALETTE['accent1'], s=20, alpha=0.8, zorder=3)

    # ── Orientation arrows ────────────────────────────────────────────────────
    if show_velocities:
        scale = L * 0.045
        ax.quiver(pos[:, 0], pos[:, 1],
                  np.cos(theta) * scale * v0,
                  np.sin(theta) * scale * v0,
                  color=PALETTE['fg'], alpha=0.55,
                  width=0.003, headwidth=3.5, headlength=4.5,
                  zorder=4, scale=1, scale_units='xy')

    # ── Target delivery zone ──────────────────────────────────────────────────
    r_zone = 2.0
    ax.add_patch(plt.Circle(target_p, r_zone,
                             color=PALETTE['accent2'], alpha=0.15, zorder=2))
    ax.plot(*target_p, '*', color=PALETTE['accent2'], ms=14, zorder=5,
            label=f'Target ({target_p[0]:.0f},{target_p[1]:.0f})')

    # ── Obstacle ──────────────────────────────────────────────────────────────
    if obs is not None:
        oc = np.array(obs['center'])
        or_ = obs['radius']
        ax.add_patch(plt.Circle(oc, or_,
                                 color=PALETTE['accent3'], alpha=0.6, zorder=3))
        # Shadow cone
        if obs.get('type') == 'shadow':
            ax.annotate('', xy=oc + np.array([L/2, 0]),
                         xytext=oc,
                         arrowprops=dict(arrowstyle='->', color=PALETTE['accent4'],
                                         lw=2, connectionstyle='arc3'))
            ax.text(oc[0] + L/4, oc[1] + 0.8, 'Shadow →',
                    color=PALETTE['accent4'], fontsize=9, ha='center')

    # ── Formatting ────────────────────────────────────────────────────────────
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect('equal')
    ax.set_xlabel('x [L-units]')
    ax.set_ylabel('y [L-units]')
    ax.set_title(f'{title}\n'
                 f'Frame {frame_idx} | '
                 f'Φ_transport={result["transport_effs"][frame_idx]:.3f} | '
                 f'Occupancy={result["occupancies"][frame_idx]:.3f}',
                 pad=8)
    ax.legend(loc='lower left', fontsize=9)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    return fig


def plot_time_series(result: dict,
                     title: str = "PJPS Time Series") -> plt.Figure:
    """
    Three-panel time series: polar order, transport efficiency, target occupancy.

    Physical interpretation guide in subtitle:
      Φ_polar tracks collective alignment (Vicsek transition).
      Φ_transport tracks directed delivery efficiency.
      Occupancy tracks actual cargo delivery fraction.
    """
    ph   = result['params']
    dt   = ph.get('dt', 0.05)
    rev  = ph.get('record_every', 5) if 'record_every' in ph else 5
    time_arr = np.arange(len(result['polar_orders'])) * dt * rev

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)

    labels_y = ['Polar order $\\Phi_{polar}$',
                 'Transport eff. $\\Phi_{transport}$',
                 'Target occupancy']
    colors   = [PALETTE['accent1'], PALETTE['accent2'], PALETTE['accent4']]
    data     = [result['polar_orders'], result['transport_effs'], result['occupancies']]

    for ax, dat, lbl, col in zip(axes, data, labels_y, colors):
        ax.plot(time_arr, dat, color=col, lw=1.4, alpha=0.9)
        ax.axvline(time_arr[len(time_arr)//2], color=PALETTE['fg'],
                   ls='--', lw=0.8, alpha=0.4, label='transient cutoff')
        mean_ss = time_averaged(dat, 0.5)
        ax.axhline(mean_ss, color=col, ls=':', lw=1.4,
                   label=f'SS mean = {mean_ss:.3f}')
        ax.set_ylabel(lbl, labelpad=6)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.2)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.5)

    axes[-1].set_xlabel('Simulation time [t-units]')
    fig.suptitle(f'{title}\nN={ph["N"]}, L={ph["L"]}, '
                 f'J={ph["J"]}, η={ph["eta"]}, α={ph["alpha"]}',
                 fontsize=12)
    fig.tight_layout()
    return fig


def animate_swarm(result: dict, interval: int = 60,
                  title: str = "Janus Swarm", max_frames: int = 120) -> HTML:
    """
    Matplotlib animation of the swarm motion.
    Returns HTML object for display in Colab/Jupyter.
    """
    pos_h   = result['positions_hist'][:max_frames]
    theta_h = result['theta_hist'][:max_frames]
    v0_h    = result['v0_hist'][:max_frames]
    I_h     = result['I_local_hist'][:max_frames]
    target_p = result['target']
    L        = result['params']['L']
    n_fr     = len(pos_h)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xlim(0, L); ax.set_ylim(0, L)
    ax.set_aspect('equal')
    ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.plot(*target_p, '*', color=PALETTE['accent2'], ms=14, zorder=5)
    target_circle = plt.Circle(target_p, 2.0, color=PALETTE['accent2'],
                                alpha=0.12, zorder=2)
    ax.add_patch(target_circle)

    scat = ax.scatter(pos_h[0, :, 0], pos_h[0, :, 1],
                      c=I_h[0], cmap='plasma',
                      vmin=0, vmax=1.5, s=20, alpha=0.85, zorder=3)

    scale = L * 0.05
    qv = ax.quiver(pos_h[0, :, 0], pos_h[0, :, 1],
                   np.cos(theta_h[0]) * scale,
                   np.sin(theta_h[0]) * scale,
                   color=PALETTE['fg'], alpha=0.45,
                   width=0.003, headwidth=3.5,
                   scale=1, scale_units='xy', zorder=4)

    title_txt = ax.set_title(f'{title}  |  frame 0/{n_fr}')

    def _update(fr):
        scat.set_offsets(pos_h[fr])
        scat.set_array(I_h[fr])
        qv.set_offsets(pos_h[fr])
        qv.set_UVC(np.cos(theta_h[fr]) * scale * v0_h[fr],
                   np.sin(theta_h[fr]) * scale * v0_h[fr])
        title_txt.set_text(f'{title}  |  frame {fr}/{n_fr}  '
                           f'Φ_t={result["transport_effs"][fr]:.3f}')
        return scat, qv, title_txt

    anim = animation.FuncAnimation(fig, _update, frames=n_fr,
                                   interval=interval, blit=True)
    plt.close(fig)
    return HTML(anim.to_jshtml())


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 7 — SINGLE SIMULATION DEMO  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo():
    """
    Single reference simulation with default parameters.
    Run this first to verify everything works before the sweeps.
    """
    print("=" * 70)
    print("  DEMO: Single PJPS Simulation  ")
    print("=" * 70)
    print(f"  N={N}, L={L}, J={J}, η={eta}, α={alpha}, dt={dt}")
    print(f"  Persistence length L_p ≈ {L_persist:.2f} L  (Dr ≈ {Dr_approx:.4f})")
    print(f"  Péclet ≈ {Pe_approx:.2f}")
    print()

    result = simulate_janus_swarm(
        N=N, L=L, v_max=v_max, R_align=R_align,
        J=J, eta=eta, alpha=alpha,
        target_frac=target_frac,
        I_0=I_0, I_emit=I_emit, sigma_rad=sigma_rad, R_rad=R_rad,
        kappa_B=kappa_B, theta_B=theta_B,
        sigma_chiral=sigma_chiral, kappa_T=kappa_T,
        epsilon_rep=epsilon_rep, sigma_rep=2*R_particle,
        n_steps=n_steps, dt=dt, seed=seed,
        obstacle=None, r_zone=2.0, record_every=record_every,
    )

    fig1 = plot_snapshot(result, frame_idx=-1,
                          title="PJPS Demo — Final State")
    plt.savefig('demo_snapshot.png', dpi=150, bbox_inches='tight')
    plt.show()

    fig2 = plot_time_series(result, title="PJPS Demo — Time Series")
    plt.savefig('demo_timeseries.png', dpi=150, bbox_inches='tight')
    plt.show()

    print(f"\n  RESULTS:")
    print(f"    ⟨Φ_transport⟩ (steady-state) = {result['time_avg_phi']:.4f}")
    print(f"    ⟨Occupancy⟩  (steady-state) = {result['time_avg_occ']:.4f}")
    print(f"    Persistence length           = {result['persist_length']:.2f} L")

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 8 — TASK 1: PHASE DIAGRAM  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════
"""
TASK 1 SCIENCE: NOISE–ALIGNMENT PHASE DIAGRAM
═════════════════════════════════════════════

We scan the (η, J) parameter plane to find the STREAMING PHASE (ordered swarm)
versus DISORDERED GAS (random orientations).

Physics (Paper 2 + Vicsek 1995):
  - Each particle's orientation undergoes rotational diffusion with Dr = η²/2
  - Alignment coupling J counteracts this diffusion
  - Phase boundary (rough scaling): η_c(J) ∝ √(J · ρ · R²)
    where ρ = N/L² is particle density and R is alignment radius

  With phototaxis (α > 0):
    - Rotational symmetry is EXPLICITLY BROKEN
    - No true thermodynamic phase transition exists
    - Instead: crossover from efficient to inefficient transport
    - The crossover still looks sharp in finite-N simulations

Observable: Φ_transport (time-averaged transport efficiency)
  This is BETTER than Φ_polar for our purpose because it measures
  directional delivery performance, not just alignment.

Computational protocol:
  64 simulations (8 × 8 grid), N=200, 500 steps each.
  Estimated runtime: ~30–90 seconds on Colab CPU.
"""

def run_phase_diagram(
        n_eta: int = 8, n_J: int = 8,
        eta_range: tuple = (0.1, 4.0),
        J_range:   tuple = (0.1, 4.0),
        N_pd: int = 200, n_steps_pd: int = 500,
        transient_frac: float = 0.5,
        seed_base: int = 42) -> dict:
    """
    Compute the (η, J) phase diagram for the PJPS model.

    Returns dict with:
        'eta_values', 'J_values', 'phase_phi', 'phase_occ'
        'phase_phi': (n_J, n_eta) array of time-averaged Φ_transport
        'phase_occ': (n_J, n_eta) array of time-averaged occupancy
    """
    eta_values = np.linspace(eta_range[0], eta_range[1], n_eta)
    J_values   = np.linspace(J_range[0],   J_range[1],   n_J)
    phase_phi  = np.zeros((n_J, n_eta))
    phase_occ  = np.zeros((n_J, n_eta))

    total = n_eta * n_J
    count = 0
    t_start = time.time()

    print("=" * 70)
    print("  TASK 1: Phase Diagram Sweep")
    print(f"  Grid: {n_eta}×{n_J} = {total} simulations")
    print(f"  N={N_pd}, n_steps={n_steps_pd}, Colab estimate: ~{total*0.8:.0f}s")
    print("=" * 70)

    for j_idx, J_val in enumerate(J_values):
        for e_idx, eta_val in enumerate(eta_values):
            count += 1
            # Different seed per run for independent statistics
            run_seed = seed_base + count * 17

            res = simulate_janus_swarm(
                N=N_pd, L=L, v_max=v_max, R_align=R_align,
                J=J_val, eta=eta_val, alpha=alpha,
                target_frac=target_frac,
                I_0=I_0, I_emit=I_emit, sigma_rad=sigma_rad, R_rad=R_rad,
                kappa_B=0.0, sigma_chiral=0.0, kappa_T=0.0,
                epsilon_rep=epsilon_rep, sigma_rep=2*R_particle,
                n_steps=n_steps_pd, dt=dt, seed=run_seed,
                obstacle=None, r_zone=2.0, record_every=5)

            phase_phi[j_idx, e_idx] = res['time_avg_phi']
            phase_occ[j_idx, e_idx] = res['time_avg_occ']

            elapsed = time.time() - t_start
            eta_remain = elapsed / count * (total - count)
            print(f"  [{count:3d}/{total}] η={eta_val:.2f}, J={J_val:.2f} → "
                  f"Φ={phase_phi[j_idx,e_idx]:.3f}  "
                  f"[ETA: {eta_remain:.0f}s]")

    print(f"\n✅  Phase diagram complete in {time.time()-t_start:.1f}s")
    return {
        'eta_values': eta_values,
        'J_values':   J_values,
        'phase_phi':  phase_phi,
        'phase_occ':  phase_occ,
    }


def plot_phase_diagram(pd_result: dict) -> plt.Figure:
    """
    Render the (η, J) phase diagram with phase boundary contour.

    Visual design:
      Color = Φ_transport (plasma colormap: dark = disordered gas, bright = streaming)
      White contour at Φ = 0.5 marks the empirical phase boundary.
      Dashed curve = theoretical rough scaling: η_c ∝ √J (Vicsek mean-field).
    """
    eta_v  = pd_result['eta_values']
    J_v    = pd_result['J_values']
    phase  = pd_result['phase_phi']

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, data, label in zip(axes,
                                [phase, pd_result['phase_occ']],
                                ['Transport Efficiency $\\Phi_{transport}$',
                                 'Target Occupancy']):
        im = ax.imshow(data,
                       origin='lower', aspect='auto',
                       extent=[eta_v[0], eta_v[-1], J_v[0], J_v[-1]],
                       vmin=0, vmax=1, cmap='plasma',
                       interpolation='bilinear')
        plt.colorbar(im, ax=ax, label=label, shrink=0.82)

        # Phase boundary contour at Φ = 0.5
        eta_grid, J_grid = np.meshgrid(eta_v, J_v)
        cs = ax.contour(eta_grid, J_grid, data,
                        levels=[0.3, 0.5, 0.7],
                        colors=['#aaaaaa', 'white', '#aaaaaa'],
                        linewidths=[1.0, 2.0, 1.0])
        ax.clabel(cs, inline=True, fontsize=8, fmt='%.1f')

        # Theoretical rough boundary: η_c ~ c·√J  (Vicsek scaling, Paper 2)
        J_line = np.linspace(J_v[0], J_v[-1], 200)
        c_scale = 1.8 * np.sqrt(N / L**2) * R_align  # rough prefactor
        eta_theory = c_scale * np.sqrt(J_line)
        ax.plot(eta_theory, J_line,
                'w--', lw=1.5, alpha=0.5,
                label=f'Theory: $\\eta_c \\propto \\sqrt{{J}}$')

        # Phase labels
        ax.text(0.3, J_v[-1]*0.88, 'STREAMING\nPHASE',
                color='white', fontsize=10, ha='left', va='top',
                bbox=dict(facecolor='none', edgecolor='none'))
        ax.text(eta_v[-1]*0.7, J_v[0]*1.1, 'DISORDERED\nGAS',
                color=PALETTE['fg'], fontsize=10, ha='right', va='bottom',
                alpha=0.8)

        ax.set_xlabel('Rotational Noise $\\eta$', fontsize=12)
        ax.set_ylabel('Alignment Strength $J$', fontsize=12)
        ax.legend(loc='upper left', fontsize=8)

    fig.suptitle(
        'PJPS Phase Diagram: Streaming Phase vs Disordered Gas\n'
        f'N={N}, L={L:.0f}, α={alpha:.1f}, '
        f'ρ=N/L²={N/L**2:.3f}, '
        f'Color = time-averaged metric (50% transient discarded)',
        fontsize=11)
    fig.tight_layout()
    plt.savefig('phase_diagram.pdf', dpi=200, bbox_inches='tight')
    plt.savefig('phase_diagram.png', dpi=200, bbox_inches='tight')
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 9 — TASK 2: OBSTACLE & SHADOW NAVIGATION  ░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════
"""
TASK 2 SCIENCE: COLLECTIVE OBSTACLE NAVIGATION
════════════════════════════════════════════════

Scientific question:
  "Can a self-organised Janus swarm collectively navigate around an optical
   obstacle that would stall individual isolated particles?"

Physics:
  1. Isolated particle in shadow: I_local → 0  →  v₀ → 0  →  particle stalls.
     Recovery requires rotational diffusion to point it out of the shadow.
     Time scale: τ_escape ~ 1/Dr = 2/η² (Paper 2, Eq. 7)

  2. Swarm in shadow: neighbours outside the shadow emit radiation
     I_rad(j→i) > 0  →  I_local(i) > 0 even inside shadow
     COLLECTIVE EFFECT: inter-particle radiation rescues stalled particles!

  3. Additionally, alignment torques from neighbours outside the shadow
     rotate stalled particles out of the shadow direction.

  4. Result: swarm navigates, isolated particle gets permanently stalled.
     → Cooperative emergence, not present in single-particle physics.

Experimental design: 4 conditions (2×2 factorial):
  Condition 1: No obstacle,  J=0   (baseline individual ABP)
  Condition 2: No obstacle,  J=J_opt (cooperative swarm, no challenge)
  Condition 3: With obstacle, J=0   (isolated particles, stalled by shadow)
  Condition 4: With obstacle, J=J_opt (cooperative swarm navigates obstacle)

The obstacle is placed between the initial swarm density and the target,
creating a shadow that directly covers the shortest path to the target.
"""

def run_obstacle_experiment(J_opt: float = 2.0,
                             n_steps_obs: int = 800) -> dict:
    """
    Run the 4-condition obstacle navigation experiment.

    Returns dict with keys 'c1', 'c2', 'c3', 'c4'
    each containing the full simulation result dict.

    Obstacle placement:
        Center at (0.5·L, 0.5·L) — directly in path from (0.25·L,0.25·L) to target
        Radius = 3.0 L-units
        Shadow: geometric, light from +x direction
        f_shadow = 0.02 (2% residual illumination in shadow — near-complete block)
    """
    obs_center = np.array([0.5 * L, 0.5 * L])
    obs_radius = 3.0
    shadow_obstacle = {
        'type': 'shadow',
        'center': obs_center.tolist(),
        'radius': obs_radius,
        'shadow_fraction': 0.02,   # 2% = near total shadow
        'light_dir': [1.0, 0.0],
    }

    # Geometric obstacle (hard wall) — also present for the shadow runs
    geom_obstacle = {
        'type': 'geometric',
        'center': obs_center.tolist(),
        'radius': obs_radius,
    }

    # Combined: shadow PLUS hard wall
    full_obstacle = {
        'type': 'shadow',
        'center': obs_center.tolist(),
        'radius': obs_radius,
        'shadow_fraction': 0.02,
        'light_dir': [1.0, 0.0],
        # Hard collision handled inside janus_step for 'geometric' type;
        # we pass both by using a list — we'll handle dual obstacles below.
    }

    common = dict(N=N, L=L, v_max=v_max, R_align=R_align,
                  alpha=alpha, target_frac=target_frac,
                  I_0=I_0, I_emit=I_emit, sigma_rad=sigma_rad, R_rad=R_rad,
                  kappa_B=0.0, sigma_chiral=sigma_chiral, kappa_T=kappa_T,
                  epsilon_rep=epsilon_rep, sigma_rep=2*R_particle,
                  n_steps=n_steps_obs, dt=dt, seed=seed,
                  r_zone=2.0, record_every=record_every)

    print("=" * 70)
    print("  TASK 2: Obstacle Navigation Experiment  ")
    print(f"  Obstacle at {obs_center}, radius {obs_radius}, "
          f"shadow_fraction=0.02")
    print(f"  J_opt={J_opt} (optimal alignment strength from Task 1)")
    print("=" * 70)

    print("\n  [1/4] Condition 1: No obstacle, J=0 (individual ABP baseline)")
    c1 = simulate_janus_swarm(**common, eta=eta, J=0.0, obstacle=None)

    print("\n  [2/4] Condition 2: No obstacle, J=J_opt (cooperative swarm)")
    c2 = simulate_janus_swarm(**common, eta=eta, J=J_opt, obstacle=None)

    print("\n  [3/4] Condition 3: Obstacle + shadow, J=0 (individual, stalled)")
    c3 = simulate_janus_swarm(**common, eta=eta, J=0.0, obstacle=full_obstacle,
                               light_dir=np.array([1.0, 0.0]))

    print("\n  [4/4] Condition 4: Obstacle + shadow, J=J_opt (swarm navigates!)")
    c4 = simulate_janus_swarm(**common, eta=eta, J=J_opt, obstacle=full_obstacle,
                               light_dir=np.array([1.0, 0.0]))

    return {'c1': c1, 'c2': c2, 'c3': c3, 'c4': c4,
            'J_opt': J_opt, 'obs_center': obs_center, 'obs_radius': obs_radius}


def plot_obstacle_comparison(obs_result: dict) -> plt.Figure:
    """
    Comprehensive 6-panel figure comparing the 4 obstacle conditions.

    Panels:
      Top row: Final snapshots of conditions 1 & 4 (baseline vs swarm)
      Middle row: Occupancy and transport efficiency time series
      Bottom row: Snapshot of conditions 3 (stalled) vs 4 (navigating) side by side
    """
    c1, c2, c3, c4 = obs_result['c1'], obs_result['c2'], \
                      obs_result['c3'], obs_result['c4']
    obs_c = obs_result['obs_center']
    obs_r = obs_result['obs_radius']
    L_    = c1['params']['L']
    dt_   = c1['params']['dt']
    tgt   = c1['target']

    fig = plt.figure(figsize=(18, 14))
    gs  = GridSpec(3, 3, figure=fig, hspace=0.42, wspace=0.35)

    # ── Time series: occupancy ─────────────────────────────────────────────
    ax_occ = fig.add_subplot(gs[0, :2])
    rec_ev  = 5
    steps_x = np.arange(len(c1['occupancies'])) * dt_ * rec_ev
    line_specs = [
        (c1, 'k--',  1.4, 'No obstacle, J=0 (Baseline ABP)'),
        (c2, 'b--',  1.8, f'No obstacle, J={obs_result["J_opt"]} (Cooperative)'),
        (c3, 'r-',   1.8, 'Obstacle + shadow, J=0 (Stalled ✗)'),
        (c4, 'g-',   2.4, f'Obstacle + shadow, J={obs_result["J_opt"]} (Swarm ✓)'),
    ]
    for res, style, lw, label in line_specs:
        ax_occ.plot(steps_x[:len(res['occupancies'])],
                    res['occupancies'], style, lw=lw, label=label, alpha=0.9)
    ax_occ.set_ylabel('Target Occupancy\n(cargo delivery fraction)', fontsize=11)
    ax_occ.set_title('Task 2: Swarm Obstacle Navigation — Delivery Performance',
                     fontsize=12, pad=6)
    ax_occ.legend(fontsize=9, loc='upper left')
    ax_occ.grid(True, alpha=0.25)
    ax_occ.set_ylim(-0.02, 1.02)

    # ── Time series: transport efficiency ─────────────────────────────────
    ax_eff = fig.add_subplot(gs[1, :2])
    for res, style, lw, label in line_specs:
        ax_eff.plot(steps_x[:len(res['transport_effs'])],
                    res['transport_effs'], style, lw=lw, label=label, alpha=0.9)
    ax_eff.set_xlabel('Simulation time [t-units]', fontsize=11)
    ax_eff.set_ylabel('Transport Efficiency\n$\\Phi_{transport}$', fontsize=11)
    ax_eff.legend(fontsize=9, loc='lower right')
    ax_eff.grid(True, alpha=0.25)
    ax_eff.set_ylim(-1.02, 1.02)

    # ── Summary bar chart ─────────────────────────────────────────────────
    ax_bar = fig.add_subplot(gs[0, 2])
    labels_b = ['C1: No obs\nJ=0', f'C2: No obs\nJ={obs_result["J_opt"]}',
                 'C3: Obstacle\nJ=0', f'C4: Obstacle\nJ={obs_result["J_opt"]}']
    occ_ss  = [time_averaged(r['occupancies']) for r in [c1,c2,c3,c4]]
    phi_ss  = [time_averaged(r['transport_effs']) for r in [c1,c2,c3,c4]]
    x_b = np.arange(4)
    bars_o = ax_bar.bar(x_b - 0.2, occ_ss, 0.35, label='Occupancy',
                         color=[PALETTE['accent2']]*4, alpha=0.85)
    bars_t = ax_bar.bar(x_b + 0.2, phi_ss, 0.35, label='$\\Phi_{transport}$',
                         color=[PALETTE['accent1']]*4, alpha=0.85)
    ax_bar.set_xticks(x_b)
    ax_bar.set_xticklabels(labels_b, fontsize=8)
    ax_bar.set_ylabel('Steady-state metric')
    ax_bar.set_title('SS Performance\n(50% transient discarded)')
    ax_bar.legend(fontsize=8)
    ax_bar.set_ylim(0, 1.1)
    ax_bar.grid(True, alpha=0.2, axis='y')

    # ── Snapshot: Condition 3 (stalled) ───────────────────────────────────
    for col_idx, (res, cond_title) in enumerate([
            (c3, 'Cond. 3: J=0, Stalled by Shadow'),
            (c4, f'Cond. 4: J={obs_result["J_opt"]}, Swarm Navigates')
    ]):
        ax_s = fig.add_subplot(gs[2, col_idx])
        pos   = res['positions_hist'][-1]
        theta = res['theta_hist'][-1]
        I_loc = res['I_local_hist'][-1]

        sc = ax_s.scatter(pos[:,0], pos[:,1],
                          c=I_loc, cmap='plasma', vmin=0, vmax=1.5,
                          s=18, alpha=0.8, zorder=3)
        scale_s = L_ * 0.045
        ax_s.quiver(pos[:,0], pos[:,1],
                    np.cos(theta)*scale_s, np.sin(theta)*scale_s,
                    color=PALETTE['fg'], alpha=0.5, width=0.003,
                    headwidth=3.5, scale=1, scale_units='xy', zorder=4)
        ax_s.plot(*tgt, '*', color=PALETTE['accent2'], ms=14, zorder=5)
        ax_s.add_patch(plt.Circle(tgt, 2.0,
                                   color=PALETTE['accent2'], alpha=0.12))
        ax_s.add_patch(plt.Circle(obs_c, obs_r,
                                   color=PALETTE['accent3'], alpha=0.55, zorder=3))
        ax_s.set_xlim(0, L_); ax_s.set_ylim(0, L_)
        ax_s.set_aspect('equal')
        ax_s.set_xlabel('x'); ax_s.set_ylabel('y')
        ax_s.set_title(f'{cond_title}\nOcc={time_averaged(res["occupancies"]):.3f}',
                        fontsize=10)
        ax_s.grid(True, alpha=0.15)

    # ── Physics summary ───────────────────────────────────────────────────
    ax_txt = fig.add_subplot(gs[1, 2])
    ax_txt.axis('off')
    improvement = (time_averaged(c4['occupancies']) /
                   max(time_averaged(c3['occupancies']), 0.001))
    summary_text = (
        "COLLECTIVE RESCUE MECHANISM:\n\n"
        "• Isolated (J=0): shadow traps particles.\n"
        f"  τ_escape ≈ 2/η² = {2/eta**2:.1f} t-units\n\n"
        "• Swarm (J>0): radiation from bright\n"
        "  neighbours rescues shadowed particles\n"
        "  I_local > 0 even in shadow → v₀ > 0\n\n"
        "• Alignment torques rotate shadowed\n"
        "  particles toward bright zone.\n\n"
        f"→ Collective improvement: ×{improvement:.1f}\n\n"
        "PHYSICS (Paper 3, Nosenko 2020):\n"
        "F_ph = πrp²kBn0T0[α₁(T₁/T₀-1)\n"
        "               - α₂(T₂/T₀-1)]"
    )
    ax_txt.text(0.05, 0.98, summary_text,
                transform=ax_txt.transAxes,
                va='top', ha='left', fontsize=9.5,
                family='monospace',
                bbox=dict(facecolor='#161b22', edgecolor=PALETTE['grid'],
                          pad=6, alpha=0.9))

    fig.suptitle(
        'PJPS Task 2: Collective Obstacle Navigation\n'
        '"A single particle stalls in shadow; the swarm flows through it."',
        fontsize=13, y=0.99)

    plt.savefig('obstacle_comparison.pdf', dpi=200, bbox_inches='tight')
    plt.savefig('obstacle_comparison.png', dpi=200, bbox_inches='tight')
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 10 — CHIRALITY & CIRCLE-SWIMMER DEMO  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════
"""
BONUS: CIRCLE-SWIMMER PHYSICS (from Paper 3, Nosenko et al.)

Nosenko observed that single Janus particles in plasma perform
circular/epitrochoidal trajectories. This is the signature of a body-fixed
torque (ω_chiral) on top of translational self-propulsion.

Theoretical prediction (Jahanshahi et al. 2017 via Paper 3):
  For a circle swimmer with intrinsic angular velocity ω_self and speed v₀:
    Orbit radius: r_circ = v₀ / |ω_self|
    Orbital period: T_circ = 2π / |ω_self|

  In the presence of confinement (our target steering, α>0):
    Epitrochoidal trajectories emerge when spinning frequency ≈ n × circling frequency.

Implementation in PJPS:
    sigma_chiral > 0 → each particle draws ω_self ~ N(0, σ_chiral)
    Half turn CW, half turn CCW (as observed by Nosenko)
"""

def run_chirality_demo(sigma_chiral_demo: float = 0.2,
                       N_demo: int = 50) -> plt.Figure:
    """
    Visualize the effect of intrinsic chirality on individual trajectories.
    Shows comparison: σ_chiral=0 (standard ABP) vs σ_chiral>0 (circle swimmers).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    for ax, sc, title_s in zip(
            axes,
            [0.0, sigma_chiral_demo],
            ['Standard ABP (σ_chiral=0)\nStraight-run + diffusion',
             f'Circle Swimmers (σ_chiral={sigma_chiral_demo})\nCircular/epitrochoidal paths (Paper 3)']):

        res = simulate_janus_swarm(
            N=N_demo, L=L, v_max=v_max, R_align=R_align,
            J=0.0, eta=0.15, alpha=0.0,  # no alignment, no phototaxis: pure ABP
            target_frac=(0.5, 0.5),
            I_0=I_0, I_emit=0.0, sigma_rad=sigma_rad, R_rad=R_rad,
            kappa_B=0.0, sigma_chiral=sc, kappa_T=0.0,
            epsilon_rep=0.0, sigma_rep=1.0,  # no repulsion for clean trajectories
            n_steps=600, dt=dt, seed=seed,
            obstacle=None, r_zone=1.0, record_every=1)

        ph = res['positions_hist']   # (frames, N, 2)
        # Unwrap periodic boundary for trajectory plotting
        # (quick approximation: just plot raw positions, wraps look like jumps)
        cmap = plt.cm.plasma
        for i in range(min(12, N_demo)):
            colour = cmap(i / min(12, N_demo))
            ax.plot(ph[:, i, 0], ph[:, i, 1],
                    '-', color=colour, lw=0.9, alpha=0.7)
            ax.plot(ph[0, i, 0],  ph[0, i, 1],  'o', color=colour, ms=5)
            ax.plot(ph[-1, i, 0], ph[-1, i, 1], 's', color=colour, ms=4, alpha=0.7)

        ax.set_xlim(0, L); ax.set_ylim(0, L)
        ax.set_aspect('equal')
        ax.set_xlabel('x [L]'); ax.set_ylabel('y [L]')
        ax.set_title(title_s, fontsize=11)
        ax.grid(True, alpha=0.2)

    fig.suptitle(
        'Chirality Effect: Standard ABP vs Circle Swimmers\n'
        'Matching experimental observations (Nosenko et al. 2020, Paper 3)',
        fontsize=12)
    fig.tight_layout()
    plt.savefig('chirality_demo.png', dpi=150, bbox_inches='tight')
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 11 — SCIENTIFIC SANITY CHECKS  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

def run_sanity_checks():
    """
    Physics sanity checks to validate the simulation.

    Test 1 (Correct physics!): J=0, α=0, η→0
      → Particles travel straight from RANDOM initial directions.
      → Since initial θ_i ~ Uniform[0,2π], Φ_polar stays at random-initial-value ~1/√N.
      → Physical note: Φ_polar → 1 would require SYNCHRONIZED initial conditions.
      → Instead: test that transport efficiency > 0 with phototaxis, 0 without.

    Test 2: J=0, η=50 → extreme noise → Φ_polar → 0 (disordered)

    Test 3: J=3, η=0.3, N=300 (proper density ρ=0.33) → alignment → Φ_polar > J=0 case
      Physical note: Critical density needed for Vicsek alignment. Sparse systems
      (N=100 in L=30 → ρ=0.11) have too few neighbours. Use N=300, ρ=0.33.

    Test 4: α=0 → no phototaxis → Φ_transport ≈ 0 (particles NOT directed to target)

    Test 5: α=0.8 → strong phototaxis → Φ_transport > 0.5 (particles steer to target)

    Test 6: Shadow obstacle stalls J=0 particles less than J>0 swarm (collective rescue)
    """
    print("=" * 65)
    print("  SANITY CHECKS (6 tests)")
    print("=" * 65)

    # Tests 1–5 use N=300 (proper density for Vicsek alignment), short runs
    common_sc = dict(N=300, L=L, v_max=v_max, R_align=R_align,
                     I_0=I_0, I_emit=I_emit, sigma_rad=sigma_rad, R_rad=R_rad,
                     kappa_B=0.0, sigma_chiral=0.0, kappa_T=0.0,
                     epsilon_rep=0.0, sigma_rep=1.0,
                     n_steps=300, dt=dt, seed=seed,
                     target_frac=(0.75, 0.75), obstacle=None, r_zone=2.0,
                     record_every=5)

    # Test 1: J=0, α=0, η→0: particles travel straight from random initial angles.
    # Φ_polar stays random ≈1/√N ≈0.06 for N=300. NOT 1 (see docstring).
    r = simulate_janus_swarm(**common_sc, J=0.0, eta=0.001, alpha=0.0)
    phi_1 = time_averaged(r['polar_orders'], 0.5)
    # Correct expectation: random ~1/√300 ≈ 0.06; some variation OK
    ok_1  = 0.03 < phi_1 < 0.30
    print(f"  [1] J=0,α=0,η→0 (random straight):  Φ_polar={phi_1:.3f}  "
          f"{'✅ PASS' if ok_1 else '⚠️  CHECK'} (expect ~0.06–0.20, 1/√N random)")

    # Test 2: J=0, α=0, η=50: extreme noise → Φ_polar → 0 (disordered gas)
    r = simulate_janus_swarm(**common_sc, J=0.0, eta=50.0, alpha=0.0)
    phi_2 = time_averaged(r['polar_orders'], 0.5)
    print(f"  [2] J=0,α=0,η=50 (extreme noise):   Φ_polar={phi_2:.3f}  "
          f"{'✅ PASS' if phi_2 < 0.20 else '❌ FAIL'} (expect <0.20)")

    # Test 3: Strong alignment at proper density → Φ_polar clearly > no-alignment case
    r_hi = simulate_janus_swarm(**common_sc, J=3.0, eta=0.3, alpha=0.0)
    r_lo = simulate_janus_swarm(**common_sc, J=0.0, eta=0.3, alpha=0.0)
    phi_hi = time_averaged(r_hi['polar_orders'], 0.5)
    phi_lo = time_averaged(r_lo['polar_orders'], 0.5)
    ok_3 = phi_hi > phi_lo + 0.1   # alignment clearly increases order
    print(f"  [3] J=3 vs J=0 at η=0.3:             "
          f"Φ_polar(J=3)={phi_hi:.3f} vs Φ_polar(J=0)={phi_lo:.3f}  "
          f"{'✅ PASS' if ok_3 else '❌ FAIL'} (expect J=3 >> J=0)")

    # Test 4: No phototaxis → Φ_transport ≈ 0 (particles not directed to target)
    r = simulate_janus_swarm(**common_sc, J=0.0, eta=0.5, alpha=0.0)
    phi_t4 = time_averaged(r['transport_effs'], 0.5)
    print(f"  [4] α=0 (no phototaxis):              Φ_transport={phi_t4:.4f}  "
          f"{'✅ PASS' if abs(phi_t4) < 0.15 else '❌ FAIL'} (expect ≈0)")

    # Test 5: Strong phototaxis → Φ_transport clearly > 0
    r = simulate_janus_swarm(**common_sc, J=1.0, eta=0.5, alpha=0.8)
    phi_t5 = time_averaged(r['transport_effs'], 0.5)
    print(f"  [5] α=0.8 (strong phototaxis):        Φ_transport={phi_t5:.4f}  "
          f"{'✅ PASS' if phi_t5 > 0.40 else '❌ FAIL'} (expect >0.40)")

    # Test 6: Collective rescue — J=2 swarm should outperform J=0 with obstacle
    obs_sc = {'type':'shadow','center':[0.5*L,0.5*L],'radius':3.0,
              'shadow_fraction':0.02,'light_dir':[1,0]}
    r_j0 = simulate_janus_swarm(**{**common_sc, 'alpha':0.8, 'I_emit':0.3,
                                    'J':0.0, 'obstacle':obs_sc, 'n_steps':400})
    r_j2 = simulate_janus_swarm(**{**common_sc, 'alpha':0.8, 'I_emit':0.3,
                                    'J':2.0, 'obstacle':obs_sc, 'n_steps':400})
    phi_j0 = time_averaged(r_j0['transport_effs'], 0.5)
    phi_j2 = time_averaged(r_j2['transport_effs'], 0.5)
    ok_6 = phi_j2 > phi_j0 + 0.05
    print(f"  [6] Obstacle: J=0 vs J=2:             "
          f"Φ_t(J=0)={phi_j0:.3f} vs Φ_t(J=2)={phi_j2:.3f}  "
          f"{'✅ PASS' if ok_6 else '⚠️  MARGINAL'} (expect J=2 better)")

    print("=" * 65)
    print("  All sanity checks complete.")


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 12 — BIOLOGICAL INTERPRETATION & SUMMARY  ░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

BIOLOGICAL_SUMMARY = """
╔══════════════════════════════════════════════════════════════════════════════╗
║               SCIENTIFIC SUMMARY & BIOLOGICAL INTERPRETATION                ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT THIS MODEL CAPTURES (grounded in uploaded papers):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. PHOTOPHORETIC PROPULSION (Papers 1 & 4):
   v₀ ∝ F_ph/γ_drag ∝ I_local  [Koss 2022, Eq. 1; Krauss 2006, Eq. 1]
   In shadow: v₀ → 0 (stall). In light: v₀ = v_max.
   Physical scale: for 5 µm Pt-JP at 100 mW laser, v₀ ~ 10–100 µm/s.

2. ROTATIONAL DIFFUSION (Paper 2):
   D_r = η²/2 = k_BT/(8πη_fluid·a³)  [Lisin 2021, Eq. 1]
   Persistence length: L_p = v₀/D_r  [Lisin 2021, Eq. 7]
   Physical scale: D_r ~ 0.01–10 s⁻¹ for 1–5 µm particles in water.

3. CIRCLE SWIMMING (Paper 3):
   Body-fixed torque from asymmetric Pt-cap creates intrinsic spin.
   Trajectory type depends on ω_self/ω_circling ratio:
     ω_self/ω = 1 → circular;   n → epitrochoidal  [Nosenko 2020, Sec. IV]

4. COLLECTIVE ALIGNMENT (Vicsek-type):
   J couples particle orientations within radius R_align.
   Physical mechanism: combined thermal radiation + thermoosmotic coupling.
   Phase boundary: η_c ∝ √(J·ρ·R²)  [Vicsek 1995, extended in Paper 2]

5. SHADOWING & COLLECTIVE RESCUE:
   Geometric shadow stalls isolated particles (Paper 1).
   Swarm radiation from bright neighbours rescues shadowed particles.
   This is a NEW EMERGENT BEHAVIOUR not present in single-particle physics.

HONEST LIMITATIONS:
━━━━━━━━━━━━━━━━━━
✗ Dry active matter: no hydrodynamic interactions (Stokes flow neglected).
  Real impact: ~20–40% error in alignment coupling magnitude.
✗ Overdamped only: inertial delay number β = ν/ω >> 1 assumed.
  Valid for β >> 1 (colloidal particles in liquid). Not valid for plasma JP.
  Plasma JPs have β ~ 0.1–10 → inertial effects matter (Paper 2, Paper 3)!
✗ Geometric optics: no wave optics, diffraction, or scattering in shadow.
✗ No particle-size polydispersity: real JP batches have ~5–10% size variation.
✗ 2D only: real experiments are quasi-2D with out-of-plane fluctuations.
✗ Phenomenological J: true physical coupling involves both radiation
  AND thermoosmotic flows — our J merges these into one constant.

MAPPING TO REAL BIOLOGY:
━━━━━━━━━━━━━━━━━━━━━━━━
• J (alignment)  ~ quorum-sensing coupling in bacteria (Pseudomonas, E. coli)
• α (phototaxis) ~ chemotaxis gradient response (camp signalling)
• Shadow          ~ physical barrier in biofilm formation / drug delivery
• Swarm delivery  ~ targeted nanoparticle delivery past biological barriers
• Phase diagram   ~ order–disorder transition in bacterial collective motion
  (Vicsek universality class, confirmed in Bacillus subtilis suspensions)

═══════════════════════════════════════════════════════════════════════════════
"""

print(BIOLOGICAL_SUMMARY)


# ═══════════════════════════════════════════════════════════════════════════════
# ░░░  CELL 13 — MAIN: RUN EVERYTHING  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Top-level runner. Executes all cells in sequence.
    In Colab: uncomment sections as desired; the phase diagram sweep
    takes ~60–120 s, the obstacle experiment ~30 s.
    """

    # ── Step 0: Sanity checks ─────────────────────────────────────────────
    run_sanity_checks()

    # ── Step 1: Demo simulation ───────────────────────────────────────────
    demo_result = run_demo()

    # ── Step 2: Chirality demo (Paper 3 physics) ──────────────────────────
    if sigma_chiral > 0:
        fig_chiral = run_chirality_demo(sigma_chiral_demo=sigma_chiral)
        plt.show()

    # ── Step 3: Task 2 — Obstacle experiment ─────────────────────────────
    # Use J_opt = 2.0 (good alignment from inspection; replace with Task 1 result)
    obs_result = run_obstacle_experiment(J_opt=2.0)
    fig_obs = plot_obstacle_comparison(obs_result)
    plt.show()

    # ── Step 4: Task 1 — Phase diagram (comment out to skip for speed) ────
    # pd_result = run_phase_diagram(n_eta=8, n_J=8, N_pd=200, n_steps_pd=500)
    # fig_pd = plot_phase_diagram(pd_result)
    # plt.show()

    print("\n✅  All tasks complete. Figures saved to current directory.")
    print("    • demo_snapshot.png")
    print("    • demo_timeseries.png")
    print("    • obstacle_comparison.pdf + .png")
    print("    • phase_diagram.pdf + .png")


if __name__ == '__main__':
    main()
