# MASTER CONTEXT DOCUMENT
# Light-Driven Janus Particle Swarm Simulation
# UCSD Vibe Coding: Active Matter & Biophysics Hackathon 2026
#
# ============================================================
# PURPOSE OF THIS DOCUMENT
# ============================================================
#
# This document is a complete, self-contained context brief intended to be
# pasted into a large language model (Claude, Gemini, GPT-4, etc.) to give
# it full understanding of:
#   1. The hackathon context, rules, and deliverables
#   2. The physical system being simulated (photophoretic Janus particles)
#   3. The full mathematical model with all equations
#   4. The simulation architecture and code design requirements
#   5. Research paper equations that will be uploaded separately
#   6. How to honestly assess the model and generate working code
#
# The LLM reading this document should:
#   - Treat all physics descriptions as starting points for its own research
#   - Be brutally honest about what is physically justified vs. simplified
#   - Identify any equations that are approximations or phenomenological
#   - Generate complete, runnable Python code (Google Colab compatible)
#   - Flag any areas where it needs more information from research papers
#
# ============================================================


# ============================================================
# SECTION 1: HACKATHON CONTEXT
# ============================================================

## 1.1 Event Overview

- **Event name:** Vibe Coding: Active Matter & Biophysics Hackathon 2026
- **Host:** UCSD Tan Lab (https://ucsd-tan-lab.github.io/vibecoding-activematter-2026/)
- **Format:** Single-day marathon hackathon
- **Team size:** 2-4 students (mixed Bio/Physics/Data Science/Engineering encouraged)
- **Platform:** Google Colab notebooks (no local install required)
- **Tools:** Python, NumPy, Matplotlib, LLMs (Gemini, Claude, etc.)

## 1.2 The Core Philosophy

> "We will use LLM to vibe code classic biophysics and active matter models such as
> phase separation, pattern formation and active Brownian particles to simulate diverse
> phenomena ranging from biological flocks, living cells and tissues, ecological
> structures to traffic jams and voter distribution."

The role of the LLM is to LOWER the entry barrier. Students with little programming
background should be able to run sophisticated simulations and focus on SCIENTIFIC
EXPLORATION, not syntax debugging.

The finish line is NOT just code — it is UNDERSTANDING.

## 1.3 Task Definitions

### TASK 1: Reproduce & Intuition
- Generate and reproduce PHASE DIAGRAMS (how behavior changes across parameter sweeps)
- Explain results intuitively via LLM-assisted exploration
- Specifically: map how an ORDER PARAMETER changes as you vary 2 control parameters
- Produce a 2D heatmap where color = order parameter value
- Draw and label the PHASE BOUNDARY between ordered and disordered phases
- Provide a physical interpretation of each phase

### TASK 2: Creative Hacking
- Introduce disorder, boundary conditions, defects, or external fields
- Connect your model to a REAL physical, biological, ecological, or societal system
- The hack must change the EMERGENT BEHAVIOR in a measurable, scientifically
  interesting way — not just make a prettier animation
- Strong format: "I changed X → I measured Y → I found Z → This suggests W
  about real system S → but the model ignores Q"

## 1.4 Final Deliverable: 5-Slide Presentation

Slide 1: Question and Model
  - What physical system are you modeling?
  - What microscopic rules did you start from?
  - What new ingredient did you add (the creative hack)?

Slide 2: Phase Diagram (Task 1 result)
  - 2D heatmap of order parameter vs. two control parameters
  - Label axes and parameter values
  - Identify the phase transition boundary

Slide 3: Emergent Behavior Analysis
  - Simulation snapshots, animations, or trajectory plots
  - Quantitative measurements of order parameters over time
  - Comparison of two regimes (ordered vs. disordered)

Slide 4: Biological / Physical Connection
  - Map model elements to a real system
  - What does the phase transition mean physically?
  - What prediction does the model make about the real system?

Slide 5: Limitations and Open Questions
  - What does the model ignore?
  - What would need to change for a more realistic model?
  - What experiment could test the prediction?

## 1.5 Tutorial Notebooks Provided

Two tutorial notebooks are provided on Google Drive. They define the baseline
models and techniques the hackathon expects participants to use.

### Tutorial 1: Intro to Active Matter (particle-based simulations)
File: tutorial1_active_matter.ipynb

Content overview:
  Part 1: Python basics - arrays, scatter plots, random walks, periodic boundaries
  Part 2: Active Brownian Particles (ABP) - single and many particles
  Part 3: Vicsek Model - alignment interactions, polar order parameter
  Part 4: Measurements - polar order, MSD, clustering, phase diagrams
  Part 5: LLM workflow - prompting, testing, debugging, sanity checking
  Part 6: Mini-challenge - add chirality, obstacles, leaders, heterogeneous speeds
  Part 7: Optional extensions

### Tutorial 2: Intro to Pattern Formation (field-based simulations)
File: tutorial2_pattern_formation.ipynb

Content overview:
  Parts 1-5: Python basics - 2D grids, Laplacian, diffusion, reaction-diffusion
  Parts 6-8: Gray-Scott model - two-field reaction diffusion
  Parts 9-10: Measurements - pattern strength, cluster counting
  Parts 11-12: Phase diagrams in (F, k) parameter space
  Parts 13-14: Creative hacks - feed-rate gradients, obstacles
  Parts 15-16: LLM workflow and sanity checks
  Parts 17-19: Mini-challenge, deliverable template, reflection

# ============================================================
# SECTION 2: ACTIVE MATTER PHYSICS PRIMER
# ============================================================

## 2.1 What is Active Matter?

Active matter consists of systems whose individual units CONSUME ENERGY to
generate motion or mechanical forces. Unlike passive matter (e.g. colloids
that diffuse due to thermal fluctuations), active matter particles are
self-propelled — they convert internal energy or ambient energy into directed
mechanical work.

Key distinction:
  - Passive particle: moves only due to thermal fluctuations (Brownian motion)
  - Active particle: moves due to internal propulsion mechanism + thermal fluctuations

Examples of active matter:
  - Biological: bird flocks, fish schools, bacterial colonies, cytoskeletal filaments,
    cellular monolayers, sperm cells, molecular motors
  - Synthetic: self-propelled colloids, Janus particles, nanomotors, active emulsions,
    vibrated granular matter, robotic swarms
  - Social: human crowds, traffic flow, voter populations, opinion dynamics

The key emergent phenomena in active matter:
  1. Collective motion / flocking (polar ordered phase)
  2. Motility-induced phase separation (MIPS) - clustering without attractive forces
  3. Giant number fluctuations (anomalously large density variations)
  4. Active turbulence (chaotic flows even at low Reynolds number)
  5. Topological defects and active nematics
  6. Pattern formation and Turing-like instabilities

## 2.2 Model 1: Active Brownian Particles (ABP)

The ABP model is the SIMPLEST model of self-propulsion. Each particle has:
  - Position: r_i = (x_i, y_i) in 2D
  - Orientation angle: theta_i (direction of self-propulsion)
  - Speed: v_0 (constant, fixed for each particle)
  - Rotational diffusion coefficient: D_r

Update equations (Euler-Maruyama, overdamped Langevin):

  x_i(t + dt) = x_i(t) + v_0 * cos(theta_i) * dt
  y_i(t + dt) = y_i(t) + v_0 * sin(theta_i) * dt
  theta_i(t + dt) = theta_i(t) + sqrt(2 * D_r * dt) * xi_i(t)

where xi_i(t) ~ N(0,1) is independent Gaussian white noise per particle per step.

Physical interpretation:
  - v_0: self-propulsion speed (e.g., from light absorption, chemical gradient)
  - D_r: rotational diffusion rate = how quickly particle "forgets" its direction
  - Persistence length: l_p = v_0 / D_r (how far particle goes before turning)
  - At short times (t << 1/D_r): ballistic motion, MSD ~ (v_0*t)^2
  - At long times (t >> 1/D_r): diffusive motion, effective D_eff = v_0^2 / (2*D_r)

Key parameters and their effects:
  - Increasing v_0: faster motion, longer persistence, more clustering (MIPS)
  - Increasing D_r: more random, faster direction loss, less clustering
  - Decreasing D_r: more persistent, straighter trajectories, more like ballistic

Real system correspondences:
  - D_r ~ 0.01-0.1 s^-1: swimming bacteria like E. coli
  - D_r ~ 1-10 s^-1: active colloids in solution
  - D_r controlled by particle size (D_r = k_B*T / (8*pi*eta*a^3) for sphere of radius a)

## 2.3 Chiral ABP (extension)

Add a constant turning rate omega (chirality):
  theta_i(t + dt) = theta_i(t) + omega * dt + sqrt(2 * D_r * dt) * xi_i(t)

  - omega > 0: particles tend to turn left (counterclockwise)
  - omega < 0: particles tend to turn right (clockwise)
  - omega = 0: standard ABP (no chirality)

Real systems: some bacteria near surfaces swim in circles due to hydrodynamic coupling
with the wall; asymmetric L-shaped particles; sperm cells.

## 2.4 Model 2: Vicsek Model (Collective Flocking)

The Vicsek model (Vicsek et al., 1995) is the canonical minimal model of
collective motion. It demonstrates that local alignment interactions alone
(no long-range communication) are sufficient to produce large-scale,
coordinated collective motion.

Rules:
  1. Each particle moves at constant speed v_0
  2. At each time step, particle i aligns its direction with the AVERAGE
     direction of all particles j within interaction radius R (including itself)
  3. Add angular noise eta to break perfect alignment

Update equations:

  phi_i(t) = arctan2( sum_j[in R] sin(theta_j), sum_j[in R] cos(theta_j) )
  theta_i(t + dt) = phi_i(t) + eta * (rand - 0.5)   [original Vicsek: uniform noise]
  or equivalently:
  theta_i(t + dt) = phi_i(t) + eta * N(0,1)          [Gaussian noise variant]

  x_i(t + dt) = x_i(t) + v_0 * cos(theta_i(t+dt)) * dt
  y_i(t + dt) = y_i(t) + v_0 * sin(theta_i(t+dt)) * dt
  Apply periodic boundary conditions: r_i <- r_i mod L

Key observable: POLAR ORDER PARAMETER

  Phi = (1/N) * |sum_i exp(i * theta_i)|
      = |mean(exp(i * theta_i))|
      = sqrt( mean(cos(theta_i))^2 + mean(sin(theta_i))^2 )

  Phi = 1: perfect alignment (all particles move in same direction)
  Phi = 0: completely disordered (random orientations)

Phase transition:
  - At low eta and high density (rho = N/L^2): Phi ~ 1 (FLOCKING phase)
  - At high eta or low density: Phi ~ 0 (DISORDERED GAS phase)
  - The transition eta_c(rho) is a continuous (or weakly first-order) phase transition
  - eta_c increases with density (more neighbors = stronger alignment = noise needed to break it)

Phase diagram axes:
  X: noise eta (from 0 to ~4.0)
  Y: density rho = N/L^2 (or equivalently box size L at fixed N)
  Color: time-averaged polar order Phi (after discarding initial transient)

The phase boundary separates:
  - STREAMING / FLOCKING phase (low eta, high rho): Phi near 1
  - DISORDERED GAS phase (high eta, low rho): Phi near 0

Critical noise at fixed density approximately:
  eta_c ~ 2 * rho^(1/2) [rough scaling, exact form depends on system details]

## 2.5 Model 3: Gray-Scott Reaction-Diffusion (Pattern Formation)

The Gray-Scott model is a two-field PDE model that produces TURING PATTERNS -
spontaneous spatial structures emerging from reaction and diffusion.

Fields:
  u(x,y,t): resource / substrate (e.g., nutrients, activator precursor)
  v(x,y,t): active species / product (e.g., signal molecule, activator)

PDEs (continuous form):
  du/dt = Du * nabla^2(u) - u*v^2 + F*(1 - u)
  dv/dt = Dv * nabla^2(v) + u*v^2 - (F + k)*v

Parameters:
  Du: diffusion coefficient of u (typically 0.16)
  Dv: diffusion coefficient of v (typically 0.08)
  F: feed rate (how fast u is replenished from outside) [range: 0.01 - 0.1]
  k: kill rate (how fast v is removed / degraded) [range: 0.04 - 0.08]

Discretization (explicit Euler, 2D grid):
  du = Du * laplacian(u) - u*v^2 + F*(1 - u)
  dv = Dv * laplacian(v) + u*v^2 - (F+k)*v
  u_new = clip(u + dt*du, 0, 1)
  v_new = clip(v + dt*dv, 0, 1)

Discrete Laplacian (5-point stencil with periodic BC):
  laplacian(u)[i,j] = u[i+1,j] + u[i-1,j] + u[i,j+1] + u[i,j-1] - 4*u[i,j]

Pattern types by (F, k) parameter values:
  F=0.035, k=0.065: spots (isolated dots, like animal skin)
  F=0.060, k=0.062: labyrinths (maze-like structures)
  F=0.025, k=0.055: waves / mixed structures
  F=0.018, k=0.051: sparse dots
  F=0.010, k=0.047: unstable / no pattern (uniform state)
  F=0.090, k=0.057: spatiotemporal chaos

Biological interpretations:
  u, v = activator-inhibitor pair (Gierer-Meinhardt mechanism)
  u, v = prey, predator (Lotka-Volterra with diffusion)
  u, v = actin, myosin (cell cytoskeletal patterns)
  Pattern = animal skin pigmentation (cheetah spots, zebrafish stripes, giraffe patches)
  Pattern = hair follicle spacing during embryogenesis
  Pattern = lung branching morphogenesis

Key observables:
  Pattern strength: std(v) [low = uniform, high = strong spatial pattern]
  Cluster count: number of connected regions where v > threshold
  Dominant wavelength: peak of Fourier power spectrum of v field

Turing instability condition (why two fields are needed):
  For pattern formation, you need:
  1. A SHORT-RANGE ACTIVATOR (v self-amplifies locally)
  2. A LONG-RANGE INHIBITOR (u diffuses fast and suppresses v at distance)
  Mathematically: Du > Dv required (fast u, slow v)
  One field alone cannot produce stationary Turing patterns.


# ============================================================
# SECTION 3: THE PHYSICAL SYSTEM — PHOTOPHORETIC JANUS PARTICLES
# ============================================================

## 3.1 What is a Janus Particle?

A Janus particle is a microscopic or nanoscopic particle with TWO DISTINCT FACES
or hemispheres, each having different physical or chemical properties. Named after
the two-faced Roman god Janus.

In the context of this simulation:
  - One hemisphere: coated with a light-absorbing metal (e.g., gold, platinum,
    carbon black, or iron oxide)
  - Other hemisphere: transparent dielectric (e.g., silica SiO2, polystyrene PS)

Typical sizes: 0.5 - 5 micrometers in diameter
Typical metal cap: 5 - 50 nm thick coating deposited by evaporation or sputtering
Metal cap coverage: ~50% of surface area (one hemisphere)

## 3.2 The Photophoresis Mechanism (How Janus Particles Self-Propel)

Photophoresis is the motion of particles driven by light-induced temperature
gradients. For Janus particles, the mechanism is:

Step 1 — Asymmetric absorption:
  When illuminated by a laser or uniform light field, the metal-coated hemisphere
  ABSORBS light strongly (high absorptivity alpha_metal ~ 0.3-0.9 depending on metal).
  The dielectric hemisphere TRANSMITS most light (low absorptivity alpha_dielectric << 0.1).

Step 2 — Asymmetric heating:
  The metal cap heats up significantly (can reach tens to hundreds of degrees above
  ambient). The dielectric hemisphere stays near ambient temperature.
  Result: a temperature gradient ACROSS the particle: T_hot on cap side, T_cold on other side.

Step 3 — Thermophoretic force:
  The temperature gradient in the FLUID surrounding the particle drives a
  thermophoretic flow. In a temperature gradient dT/dz, a spherical particle
  experiences a thermophoretic velocity:
    v_thermo = -D_T * (grad T) / T
  where D_T is the thermophoretic diffusion coefficient.

  For a Janus particle, the asymmetric heating creates an asymmetric temperature
  field in the surrounding fluid, generating a NET force on the particle.

Step 4 — Self-propulsion direction:
  The force direction depends on the particle-fluid thermophoretic coupling:
  - If the particle is THERMOPHOBIC (moves away from heat sources):
    propulsion toward the COLD hemisphere (cap pushes particle forward)
  - If the particle is THERMOPHILIC:
    propulsion toward the HOT hemisphere

  For most experimental Janus particles in water or organic solvents:
    Propulsion direction ~ away from the metal cap (cap is the "engine" at the back)
    Speed: v_0 = C * I_0 * alpha_metal * R / (kappa_fluid)
    where:
      C: coupling constant (thermophoretic mobility, units m^2 s^-1 K^-1)
      I_0: incident light intensity (W/m^2)
      alpha_metal: metal cap absorptivity (dimensionless, 0 to 1)
      R: particle radius (m)
      kappa_fluid: fluid thermal conductivity (W m^-1 K^-1)

Typical experimental values:
  Particle radius: R ~ 1-5 um
  Illumination: I_0 ~ 10^4 - 10^6 W/m^2 (focused laser or LED array)
  Self-propulsion speed: v_0 ~ 1 - 100 um/s depending on I_0
  Rotational diffusion: D_r ~ 0.01 - 10 s^-1 (scales as 1/R^3)

## 3.3 Local Radiation Coupling Between Neighboring Particles

This is the KEY INNOVATION of our model beyond standard ABP.

When particle i is illuminated and its metal cap heats up, it becomes a
secondary HEAT SOURCE that can affect neighboring particles.

### Physical mechanism of inter-particle radiation coupling:

#### Mechanism A: Near-field thermal radiation (electromagnetic)
  Particle i's hot metal cap emits thermal radiation (blackbody-like, peaked in
  infrared for T ~ 300-400 K). A neighboring particle j receives this radiation.
  The absorption depends on:
    - Distance r_ij = |r_j - r_i|: intensity falls as 1/r_ij^2 (far field)
    - Orientation: if j's cap faces toward i, it absorbs more (cap has higher absorptivity)
    - If j's transparent side faces i, absorption is much lower

  Effective radiation received by j from i:
    I_ij = (P_rad_i / (4*pi*r_ij^2)) * g(theta_ij, phi_ij)
  where:
    P_rad_i = emissivity * sigma * T_cap_i^4 * A_cap (Stefan-Boltzmann radiated power)
    g(theta_ij, phi_ij): geometric coupling factor depending on relative orientation
    theta_ij = angle between r_j - r_i and particle i's cap direction
    phi_ij = angle between r_j - r_i and particle j's cap direction

  Simplified coupling factor (phenomenological):
    g(theta_ij, phi_ij) = (1 + beta * cos(theta_ij)) * (1 + gamma * cos(phi_ij))
  where:
    cos(theta_ij) = dot(e_cap_i, (r_j - r_i)/r_ij)  [how much i's cap faces j]
    cos(phi_ij) = -dot(e_cap_j, (r_j - r_i)/r_ij)  [how much j's cap faces i]
    beta, gamma: coupling asymmetry parameters (0 = isotropic, 1 = fully directed)

#### Mechanism B: Hydrodynamic interactions via thermal fluid flows
  The temperature gradient around particle i drives a fluid flow (thermoosmotic flow).
  Particle j, immersed in this flow, experiences a drift velocity:
    v_drift_j = mu_TO * grad(T_field_i(r_j))
  where mu_TO is the thermoosmotic mobility of j's surface.

  Since j's two hemispheres have different mu_TO values, this creates a NET TORQUE
  on j, aligning or misaligning it relative to the temperature gradient from i.

#### Mechanism C: Optical shadowing (reduced primary illumination)
  If particle i sits BETWEEN the light source and particle j, it casts an optical
  shadow. Particle j receives reduced primary illumination:
    I_primary_j = I_0 * (1 - shadow_fraction_ij)
  where shadow_fraction depends on the projected area of i as seen from the light
  direction and the distance between i and j.

### Net effect of inter-particle coupling:

The combined effect of Mechanisms A, B, and C creates:

1. EFFECTIVE ALIGNMENT: nearby particles tend to develop correlated orientations
   (this is our Vicsek-like coupling J)

2. SPEED MODULATION: local illumination at each particle depends on its neighbors'
   positions and orientations (variable v_0)

3. EFFECTIVE REPULSION/ATTRACTION: thermophoretic interactions between hot particles
   can create effective pair potentials (cap-cap repulsion, cap-body attraction)

For the hackathon simulation, we model these complex effects with TWO simplified terms:
  (a) Vicsek-type alignment: J * sin(phi_mean_neighbors - theta_i) [captures alignment]
  (b) Local intensity field: I_local(r_i) = I_ext(r_i) + sum_j I_rad(j->i) [captures speed mod]

## 3.4 Global External Fields

### Global Field 1: Spatially Varying Illumination I(x,y)

The primary light field driving propulsion is not necessarily uniform.

Examples of spatial profiles:
  Gaussian beam: I(x,y) = I_0 * exp(-((x-x_c)^2 + (y-y_c)^2) / (2*sigma_beam^2))
  Standing wave: I(x,y) = I_0 * (1 + cos(2*pi*x/lambda))^2 / 4
  Gradient: I(x,y) = I_0 * (1 + kappa_grad * x / L) [linear gradient along x]
  Stripe: I(x,y) = I_0 * (x > L/2) [bright right half, dark left half]
  Shadow obstacle: I(x,y) = I_0 * (1 - shadow_mask(x,y,obstacle)) [see below]

Effect on particle behavior:
  v_0(r_i) = v_max * I(r_i) / I_ref
  Particles in bright regions move fast → tend to leave (they don't slow down to stay)
  Particles in dark regions move slow → tend to accumulate (trapping effect)
  This is called PHOTOPHOBIC trapping or light-induced clustering

Phototactic vs photophobic:
  Phototactic (moves toward light): effective alpha in update biases theta toward
    angle pointing to bright region
  Photophobic (moves away from light): effective alpha biases theta toward dark region
  Mechanism of phototaxis in Janus particles: orientation-dependent absorption
    means particles naturally orient to be propelled toward high-I regions

### Global Field 2: Magnetic Field B(x,y)

For Janus particles with magnetic caps (e.g., FePt, Fe3O4, cobalt), an external
magnetic field exerts a TORQUE on the particle:
  tau_mag = m x B = |m| * |B| * sin(theta_B - theta_i)
where:
  m: magnetic moment of particle (direction = cap direction for FePt Janus particles)
  B: external magnetic field (direction = field angle theta_B)
  theta_i: current particle orientation

This adds a magnetic steering term to the orientation update:
  theta_i += (|m|*|B| / xi_r) * sin(theta_B - theta_i) * dt
where xi_r is the rotational drag coefficient.

For a rotating magnetic field: theta_B(t) = Omega_B * t
This can make all particles spin synchronously and swim in helical paths.

For a gradient field: grad(B) creates a force proportional to grad(|m|*|B|)
This creates effective long-range attraction/repulsion between particles.

### Global Field 3: External Flow Field u_ext(x,y)

A background fluid flow (e.g., microfluidic channel flow, convection) advects particles:
  dr_i/dt = v_0 * e_cap_i + u_ext(r_i) + sqrt(2*D_T)*xi_T

Poiseuille (parabolic) flow: u_ext = U_max * (1 - (y/W)^2) * e_x
Uniform flow: u_ext = U_0 * (cos(theta_flow), sin(theta_flow))
Vortex: u_ext = Gamma/(2*pi*r) in azimuthal direction

Effect: Flow can stretch, shear, and organize the swarm into elongated streams or
trapped regions (depending on whether v_0 > or < |u_ext|).

### Global Field 4: Chemical Gradient / Chemotaxis

For particles with chemically active surfaces:
  grad(c)(x,y): concentration gradient of signaling molecule
  theta_bias = arctan2(grad(c)_y, grad(c)_x) [direction of increasing c]
  Chemotactic torque: kappa_c * sin(theta_bias - theta_i)

This is mathematically identical to the phototactic steering term alpha in our model.

# ============================================================
# SECTION 4: THE COMPLETE MATHEMATICAL MODEL
# ============================================================

## 4.1 Model Name

Photophoretic Janus Particle Swarm (PJPS) Model

This is an EXTENDED VICSEK MODEL with:
  (1) Orientation-dependent propulsion speed (v_0 depends on local radiation)
  (2) Radiation-mediated alignment (Vicsek coupling J from thermal interactions)
  (3) Global field steering (phototaxis alpha, magnetic steering kappa_B)
  (4) Spatially varying noise (eta can depend on local I if desired)

## 4.2 State Variables

  N particles in a 2D box of size L x L
  Positions: r_i = (x_i, y_i),  i = 1, ..., N
  Orientations: theta_i (angle of cap direction / self-propulsion direction)
  
  Note: theta_i = 0 means particle moves in +x direction
        theta_i = pi/2 means particle moves in +y direction

## 4.3 External Illumination Field

  I_ext(x, y): external light intensity field [W/m^2]
  
  Default (uniform): I_ext(x,y) = I_0 (constant everywhere)
  
  With obstacle (shadow):
    shadow_mask(x,y) = 1 if (x,y) is in geometric shadow of obstacle, 0 otherwise
    I_ext(x,y) = I_0 * (1 - f_shadow * shadow_mask(x,y))
    where f_shadow in [0,1]: 0 = no shadow, 1 = complete shadow
  
  With gradient:
    I_ext(x,y) = I_0 * (1 + kappa_grad * x/L)  [phototactic gradient along x]

## 4.4 Local Radiation from Neighboring Particles

  I_rad(j -> i) = I_emit * exp(-r_ij^2 / sigma_rad^2) * max(0, dot(e_j, e_ij))

  where:
    r_ij = |r_i - r_j|: distance from j to i
    e_j = (cos(theta_j), sin(theta_j)): unit vector in j's cap direction
    e_ij = (r_i - r_j) / r_ij: unit vector from j toward i
    dot(e_j, e_ij): how much j's cap "faces" i (1 = perfectly facing, 0 = perpendicular, -1 = facing away)
    I_emit: radiation emission strength of a particle [W/m^2 at contact]
    sigma_rad: radiation decay length [same units as box size L]

  Total local illumination at particle i:
    I_local(i) = I_ext(r_i) + sum_{j != i, r_ij < R_rad} I_rad(j -> i)

## 4.5 Propulsion Speed

  v_0(i) = v_max * min(1, I_local(i) / I_ref)

  where:
    v_max: maximum self-propulsion speed (at full illumination)
    I_ref: reference illumination level (= I_0 for normalization)
  
  Special cases:
    I_local(i) = I_0 (uniform, no neighbors): v_0(i) = v_max (baseline)
    I_local(i) = 0 (complete shadow): v_0(i) = 0 (stalled particle)
    I_local(i) > I_0 (enhanced by neighbors): v_0(i) > v_max [cap at v_max or allow]

## 4.6 Alignment Torque (Local Radiation Coupling -> Vicsek-like)

  phi_align(i) = arctan2(sum_{j in N_R(i)} sin(theta_j), sum_{j in N_R(i)} cos(theta_j))
  
  where N_R(i) = {j != i : r_ij < R} = set of neighbors within radius R
  
  If |N_R(i)| = 0: phi_align(i) = theta_i (no change from alignment if isolated)
  
  Alignment torque: tau_align(i) = J * sin(phi_align(i) - theta_i)
  
  Note: sin(phi - theta) has the correct sign to rotate theta toward phi

## 4.7 Phototactic Steering Torque (Global Field)

  phi_target(i) = arctan2(y_target - y_i, x_target - x_i)
  tau_phototax(i) = alpha * sin(phi_target(i) - theta_i)
  
  OR for a smooth illumination gradient (more realistic):
  I_grad = nabla(I_ext) evaluated at r_i
  phi_gradient(i) = arctan2(I_grad_y, I_grad_x)  [direction of increasing I]
  tau_phototax(i) = alpha * sin(phi_gradient(i) - theta_i)

## 4.8 Magnetic Steering Torque (Optional Global Field)

  tau_mag(i) = kappa_B * sin(theta_B(t) - theta_i)
  
  where theta_B(t) = field direction (constant or rotating: theta_B = Omega_B * t)

## 4.9 Noise

  xi_i(t) ~ N(0,1): independent standard Gaussian, new draw every timestep
  
  Orientation noise: eta * xi_i * sqrt(dt)
  
  Optional: spatially varying noise
    eta_eff(i) = eta_base + eta_fluct * (1 - I_local(i)/I_0)
    [noisier in darker regions, mimicking Brownian vs driven behavior]

## 4.10 Full Orientation Update Equation

  theta_i(t + dt) = theta_i(t)
    + J * sin(phi_align(i) - theta_i) * dt        [alignment]
    + alpha * sin(phi_target(i) - theta_i) * dt   [phototaxis / global steering]
    + kappa_B * sin(theta_B - theta_i) * dt       [magnetic steering, optional]
    + eta * xi_i * sqrt(dt)                        [rotational noise]

## 4.11 Full Position Update Equation

  x_i(t + dt) = x_i(t) + v_0(i) * cos(theta_i(t+dt)) * dt
  y_i(t + dt) = y_i(t) + v_0(i) * sin(theta_i(t+dt)) * dt
  
  Apply boundary conditions (see Section 5.2 for options)

## 4.12 Initial Conditions

  Positions: r_i ~ Uniform([0, L] x [0, L])
  Orientations: theta_i ~ Uniform([0, 2*pi])
  
  Both initialized randomly with a fixed random seed for reproducibility.

# ============================================================
# SECTION 5: SIMULATION ARCHITECTURE
# ============================================================

## 5.1 Parameter Table (All Parameters with Defaults)

  # ---- Swarm parameters ----
  N = 300           # Number of Janus particles
  L = 30.0          # Box size (dimensionless units, real scale: ~300 um for 1 um/unit)
  v_max = 1.0       # Maximum self-propulsion speed [L/time_unit]
  R = 2.0           # Alignment interaction radius [L]
  J = 1.0           # Alignment coupling strength [1/time_unit]
  eta = 0.3         # Rotational noise amplitude [rad/sqrt(time_unit)]
  dt = 0.05         # Time step [time_unit]
  
  # ---- Phototaxis parameters ----
  alpha = 0.5       # Phototactic steering strength [1/time_unit]
  target = (0.75*L, 0.75*L)  # Target position (cargo delivery point)
  
  # ---- Illumination field parameters ----
  I_0 = 1.0         # Background illumination intensity [normalized]
  I_ref = 1.0       # Reference intensity for v_0 normalization
  
  # ---- Local radiation coupling parameters ----
  I_emit = 0.3      # Radiation emission strength per particle [normalized]
  sigma_rad = 2.0   # Radiation spatial decay length [L] (same as R or smaller)
  R_rad = R         # Cutoff radius for radiation interactions
  
  # ---- Magnetic field parameters (optional) ----
  kappa_B = 0.0     # Magnetic steering strength (0 = disabled)
  theta_B = 0.0     # Magnetic field direction [rad]
  Omega_B = 0.0     # Rotation rate of magnetic field [rad/time_unit]
  
  # ---- Simulation parameters ----
  n_steps = 1000    # Total simulation steps
  record_every = 5  # Record trajectory every N steps
  transient = 0.5   # Fraction of simulation to discard as transient for averaging
  seed = 42         # Random seed for reproducibility

## 5.2 Boundary Conditions

  Option A (PERIODIC - default, standard for active matter):
    r_i = r_i mod L (component-wise)
    Minimum image convention for distances:
      d_ij = r_j - r_i - L * round((r_j - r_i) / L)  [component-wise]
  
  Option B (REFLECTIVE - models a confined container):
    If x_i < 0: x_i = -x_i, theta_i = pi - theta_i  [reflect x-velocity]
    If x_i > L: x_i = 2*L - x_i, theta_i = pi - theta_i
    Same for y
  
  Option C (ABSORBING at target - models cargo delivery):
    If r_i is within r_zone of target: remove particle i from simulation
    Track: N_delivered(t) = number removed by time t
  
  For the phase diagram (Task 1): Use Option A (periodic)
  For the obstacle demo (Task 2): Use Option A or B depending on setup

## 5.3 Order Parameters (Full Definitions)

  ### OP1: Polar Order (global alignment, range [0,1])
  Phi_polar = |mean(exp(i * theta))| = sqrt(mean(cos(theta))^2 + mean(sin(theta))^2)
  
  Physical meaning: 1 = perfect flocking, 0 = isotropic disorder

  ### OP2: Transport Efficiency (target-directed alignment, range [-1,1])
  phi_target_i = arctan2(y_target - y_i, x_target - x_i)
  Phi_transport = mean(cos(theta_i - phi_target_i))
  
  Physical meaning: 1 = all particles aimed at target, 0 = random w.r.t. target

  ### OP3: Target Occupancy (delivery fraction, range [0,1])
  Phi_occupancy = (count of particles within r_zone of target) / N
  
  Physical meaning: fraction of swarm that has reached the delivery zone

  ### OP4: Speed Order (normalized mean speed, range [0,1])
  Phi_speed = mean(v_0(i)) / v_max
  
  Physical meaning: 1 = all particles fully illuminated, 0 = all stalled

  ### OP5: Cluster Order (largest cluster size / N, range [0,1])
  Use DBSCAN or simple neighbor-graph connected components with threshold R_cluster
  Phi_cluster = (size of largest connected component) / N
  
  Physical meaning: 1 = single giant cluster, 0 = fully dispersed

  For the phase diagram: USE Phi_transport (most relevant to the hackathon narrative)

## 5.4 Vectorized Computation Strategy

  All per-particle computations must be VECTORIZED over N particles.
  No Python-level loops over particles (use NumPy broadcasting).
  
  Key patterns:
  
  # Pairwise displacements (N x N x 2 array):
  disp = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]  # (N, N, 2)
  disp -= L * np.round(disp / L)  # minimum image
  dist = np.linalg.norm(disp, axis=2)  # (N, N)
  
  # Neighbor mask:
  neighbors = (dist < R) & (dist > 0)  # (N, N) bool, exclude self
  
  # Alignment (vectorized):
  sin_sum = neighbors.astype(float) @ np.sin(theta)  # (N,)
  cos_sum = neighbors.astype(float) @ np.cos(theta)  # (N,)
  phi_align = np.arctan2(sin_sum, cos_sum)            # (N,)
  tau_align = J * np.sin(phi_align - theta)           # (N,)
  
  # Phototactic torque (vectorized):
  to_target = target - positions          # (N, 2)
  phi_tgt = np.arctan2(to_target[:,1], to_target[:,0])  # (N,)
  tau_phototax = alpha * np.sin(phi_tgt - theta)         # (N,)
  
  # Local radiation field (vectorized):
  e_cap = np.column_stack((np.cos(theta), np.sin(theta)))  # (N, 2) cap directions
  e_ij = disp / (dist[:,:,np.newaxis] + 1e-10)  # (N, N, 2) unit vectors i->j
  dot_cap_ij = np.einsum('ij,ikj->ik', e_cap, e_ij)  # (N, N) dot(e_cap_i, e_ij)
  rad_from_j = I_emit * np.exp(-dist**2/sigma_rad**2) * np.maximum(0, dot_cap_ij)
  rad_mask = (dist < R_rad) & (dist > 0)
  I_rad = (rad_from_j * rad_mask).sum(axis=0)  # (N,) radiation at each particle
  I_local = np.clip(I_ext_at_particles + I_rad, 0, None)  # (N,)
  v0_array = v_max * np.minimum(1.0, I_local / I_ref)  # (N,)

## 5.5 Obstacle Implementation

  ### Geometric Obstacle (hard circle):
  obstacle_center = np.array([x_obs, y_obs])
  obstacle_radius = r_obs
  
  def apply_obstacle(positions, theta, obstacle_center, obstacle_radius):
      d_obs = np.linalg.norm(positions - obstacle_center, axis=1)  # (N,)
      inside = d_obs < obstacle_radius
      if inside.any():
          # Push particles to surface
          dir_out = (positions[inside] - obstacle_center)
          dir_out /= np.linalg.norm(dir_out, axis=1, keepdims=True)
          positions[inside] = obstacle_center + dir_out * obstacle_radius * 1.01
          # Reflect orientation (optional: deflect outward or randomize)
          theta[inside] = np.arctan2(dir_out[:,1], dir_out[:,0]) + eta*rng.normal(size=inside.sum())
      return positions, theta
  
  ### Optical Shadow (illumination mask):
  light_direction = np.array([1.0, 0.0])  # light comes from -x direction
  
  def compute_shadow_mask(positions, obstacle_center, obstacle_radius, light_direction):
      # Vector from obstacle to each particle
      to_particles = positions - obstacle_center  # (N, 2)
      # Project onto shadow axis (opposite light direction)
      shadow_axis = -light_direction / np.linalg.norm(light_direction)
      proj = to_particles @ shadow_axis  # (N,) scalar projection
      # Perpendicular distance from shadow axis
      perp_vec = to_particles - proj[:, np.newaxis] * shadow_axis[np.newaxis, :]
      perp_dist = np.linalg.norm(perp_vec, axis=1)  # (N,)
      # In shadow if: behind obstacle (proj > 0) AND within shadow cone width
      in_shadow = (proj > 0) & (perp_dist < obstacle_radius)
      return in_shadow


# ============================================================
# SECTION 6: PHASE DIAGRAM DESIGN (TASK 1)
# ============================================================

## 6.1 Phase Diagram Specification

The phase diagram maps the EMERGENT BEHAVIOR of the swarm as two control
parameters are varied. It is the central scientific result of Task 1.

### Primary Phase Diagram: Transport Efficiency vs. Noise and Alignment

  X-axis: Rotational noise eta (range: 0.0 to 4.0, 8-10 evenly spaced points)
  Y-axis: Alignment strength J (range: 0.0 to 3.0, 8-10 evenly spaced points)
  Color (Z): Time-averaged transport efficiency Phi_transport

  Expected topology:
    Upper-left region (low eta, high J): HIGH Phi_transport = STREAMING PHASE
      -> Particles are well-aligned and consistently directed toward target
      -> Color: bright yellow/white
    Lower-right region (high eta, low J): LOW Phi_transport = DISORDERED PHASE
      -> Particles wander randomly, poor target delivery
      -> Color: dark blue/black
    Phase boundary: a diagonal band from (eta_c_low, J_low) to (eta_c_high, J_high)
      -> Separates streaming from disordered phases
      -> Is NOT sharp in finite systems (finite-size effects blur the transition)

### Secondary Phase Diagram: Polar Order vs. Noise and Density

  X-axis: Rotational noise eta (range: 0.0 to 4.0)
  Y-axis: Density rho = N/L^2 (vary L from 15 to 40 at fixed N=150)
  Color: Time-averaged polar order Phi_polar

  This is the CLASSIC Vicsek phase diagram. It is easier to interpret and
  compare with published literature. Recommended as a sanity check.

### Optional: Order Parameter vs. Phototaxis Strength

  X-axis: Noise eta
  Y-axis: Phototactic bias alpha
  Color: Target occupancy Phi_occupancy

  This diagram specifically shows when phototaxis is strong enough to overcome
  noise and drive the swarm to the target.

## 6.2 Computational Protocol for Phase Diagram

  For each parameter combination (eta_i, J_j):
    1. Initialize N particles randomly (fixed seed for reproducibility)
    2. Run simulation for n_steps = 500 total steps
    3. Discard first 50% as transient (equilibration period)
    4. Compute time-average of Phi_transport over remaining 250 steps
    5. Store in phase[i,j] array
  
  Total simulation runs: n_eta * n_J = 8 * 8 = 64 runs
  Total steps: 64 * 500 = 32,000 steps
  
  For N=200, this should run in ~30-60 seconds in Google Colab (CPU)
  For N=500, budget 3-5 minutes.

## 6.3 Expected Physics of the Phase Transition

The NOISE-ALIGNMENT TRADEOFF is the core physics:

  - Each particle's orientation diffuses due to noise eta
  - Neighboring particles' alignment interactions (J) counteract this diffusion
  - There is a critical noise eta_c(J) above which alignment cannot maintain order

  Rough scaling:
    At eta = 0: all particles align perfectly regardless of J (as long as J > 0)
    At J = 0: alignment plays no role, Phi decreases monotonically with eta
    Phase boundary approximately: eta_c ~ sqrt(J * rho * R^2)  [rough estimate]

  IMPORTANT PHYSICAL NOTE FOR LLM:
  The exact scaling of eta_c with model parameters depends on:
    (1) Whether noise is additive (Gaussian) or multiplicative
    (2) Whether the phase transition is continuous (second order) or discontinuous (first order)
    (3) Finite-size effects (true phase transition only in N -> infinity limit)
    (4) The presence of the phototactic bias alpha (breaks rotational symmetry)
  
  With alpha > 0 (phototaxis):
    - Rotational symmetry is EXPLICITLY BROKEN by the target direction
    - There is no true phase transition in the thermodynamic sense
    - Instead: a crossover from high to low transport efficiency
    - But it still looks like a phase transition in finite simulations

## 6.4 How to Plot the Phase Diagram

  import matplotlib.pyplot as plt
  import numpy as np
  
  plt.figure(figsize=(8, 6))
  im = plt.imshow(
      phase_data,          # shape: (n_J, n_eta)
      origin='lower',
      aspect='auto',
      extent=[eta_min, eta_max, J_min, J_max],
      vmin=0, vmax=1,
      cmap='plasma'        # 'viridis', 'plasma', 'inferno' work well
  )
  plt.colorbar(im, label='Transport Efficiency Phi_transport')
  plt.xlabel('Rotational Noise η', fontsize=14)
  plt.ylabel('Alignment Strength J', fontsize=14)
  plt.title('Janus Swarm Phase Diagram\nStreaming Phase vs. Disordered Gas', fontsize=14)
  
  # Add phase boundary contour (where Phi_transport = 0.5)
  eta_grid, J_grid = np.meshgrid(eta_values, J_values)
  plt.contour(eta_grid, J_grid, phase_data, levels=[0.5], colors='white', linewidths=2)
  
  # Annotate phases
  plt.text(0.5, 2.5, 'STREAMING\nPHASE', color='white', fontsize=12, ha='center')
  plt.text(3.0, 0.5, 'DISORDERED\nGAS', color='white', fontsize=12, ha='center')
  
  plt.tight_layout()
  plt.savefig('janus_phase_diagram.pdf', dpi=300)
  plt.show()

# ============================================================
# SECTION 7: CREATIVE HACK — OBSTACLE & SHADOW (TASK 2)
# ============================================================

## 7.1 The Scientific Question

"Can a self-organized Janus particle swarm collectively navigate around an
optical obstacle that would stall individual isolated particles?"

HYPOTHESIS:
  - Single particle in shadow of obstacle: stalls (v_0 -> 0), gets trapped
  - Swarm with alignment interactions: particles on the bright side drag
    shadow-trapped particles out via alignment torques, enabling collective
    navigation around the obstacle

MEASURABLE PREDICTION:
  - Phi_occupancy(t) with obstacle < Phi_occupancy(t) without obstacle (expected)
  - BUT: for HIGH J, Phi_occupancy difference is SMALLER (swarm helps)
  - For LOW J, obstacle effectively blocks the swarm (particles decouple)

## 7.2 Obstacle Options

### Option A: Circular Geometric Obstacle

  Properties:
    - Center: (x_obs, y_obs)  [choose between start and target positions]
    - Radius: r_obs ~ 3-5 units (comparable to R, the interaction radius)
    - Particles CANNOT enter (reflective boundary)
    - Light passes AROUND obstacle (no shadow, just physical barrier)

  Implementation: see Section 5.5 apply_obstacle() function above

  Scientific connection: physical barrier in microfluidic channel, tumor mass,
  cellular aggregate that blocks drug delivery nanoparticles

### Option B: Optical Shadow Obstacle (RECOMMENDED - more physically motivated)

  Properties:
    - Occluder position: (x_obs, y_obs) between light source and target
    - Occluder radius: r_obs ~ 3-5 units
    - Light source direction: fixed (e.g., from left, light_dir = (1,0))
    - In shadow: I_ext(r_i) reduced to f_shadow * I_0 (default f_shadow = 0.05)
    - In shadow: v_0(i) reduced proportionally -> particles stall
    - Geometric motion still allowed (particles CAN move through shadow region)

  Implementation: see compute_shadow_mask() in Section 5.5

  Physical interpretation:
    - Occluder = opaque tissue, tumor, or cell aggregate blocking laser
    - Shadow = "dark zone" where photophoresis stops
    - Collective alignment helps particles transit the dark zone faster
    - With NO alignment (J=0): particles stall in shadow for exponentially long
    - With alignment (J>0): bright neighbors drag shadow particles through

### Option C: Magnetic Field Trap (combines both global fields)

  Properties:
    - Add a localized magnetic field gradient that acts as a "trap"
    - grad(B) concentrated at obstacle position
    - Particles with magnetic caps feel a force TOWARD the trap center
    - Must overcome this with swarm propulsion/alignment

  Physical interpretation: magnetic trap created by permanent magnets or
  electromagnets used to steer particle swarms in biomedical applications

## 7.3 Comparison Protocol for Task 2

  Run 4 conditions:
    (1) No obstacle, J=0: baseline single-particle phototaxis
    (2) No obstacle, J=J_opt: baseline swarm phototaxis
    (3) With obstacle, J=0: single particles vs. obstacle
    (4) With obstacle, J=J_opt: swarm vs. obstacle

  For each: plot Phi_occupancy(t) over time
  
  Key result to show: the GAP between conditions (3) and (4) quantifies
  the BENEFIT of collective behavior for obstacle navigation.

# ============================================================
# SECTION 8: COMPLETE PYTHON CODE SPECIFICATION
# ============================================================

## 8.1 File Structure for Google Colab

  Single notebook: janus_swarm_simulation.ipynb
  
  Cell 1: Imports and setup
  Cell 2: All parameters (clearly labeled, easy to change)
  Cell 3: Helper functions (laplacian, periodic BC, etc.)
  Cell 4: Core simulation step function
  Cell 5: Full simulation runner
  Cell 6: Order parameter functions
  Cell 7: Animation helper
  Cell 8: Single simulation demo + visualization
  Cell 9: Phase diagram sweep (Task 1)
  Cell 10: Phase diagram plotting
  Cell 11: Obstacle implementation
  Cell 12: Obstacle comparison experiment (Task 2)
  Cell 13: Sanity checks
  Cell 14: Summary and biological interpretation

## 8.2 Complete Code — Cell 1: Imports

  import numpy as np
  import matplotlib.pyplot as plt
  import matplotlib.patches as patches
  from matplotlib import animation, cm
  from IPython.display import HTML
  from scipy import ndimage
  import time
  
  plt.rcParams['figure.figsize'] = (8, 6)
  plt.rcParams['font.size'] = 12
  plt.rcParams['figure.dpi'] = 100

## 8.3 Complete Code — Cell 2: Parameters

  # ================================================================
  # ALL SIMULATION PARAMETERS — CHANGE THESE TO EXPLORE
  # ================================================================
  
  # Swarm parameters
  N = 300                  # Number of Janus particles
  L = 30.0                 # Box size
  v_max = 1.0              # Max self-propulsion speed
  R = 2.0                  # Alignment interaction radius
  J = 1.0                  # Alignment coupling strength
  eta = 0.5                # Rotational noise amplitude
  dt = 0.05                # Timestep
  
  # Phototaxis
  alpha = 0.8              # Phototactic steering strength
  target_frac = (0.75, 0.75)  # Target as fraction of box
  
  # Local radiation coupling
  I_emit = 0.3             # Radiation emission per particle
  sigma_rad = 1.5          # Radiation decay length
  R_rad = R                # Radiation interaction cutoff
  
  # Magnetic field (set kappa_B > 0 to enable)
  kappa_B = 0.0            # Magnetic steering strength
  theta_B = 0.0            # Magnetic field direction [rad]
  
  # Illumination field
  I_0 = 1.0                # Background illumination
  
  # Simulation control
  n_steps = 800            # Total steps
  record_every = 5         # Animation frame interval
  seed = 42                # Random seed
  
  # Derived quantities
  target = np.array([target_frac[0] * L, target_frac[1] * L])
  rng = np.random.default_rng(seed)

## 8.4 Complete Code — Cell 3: Helper Functions

  def minimum_image(pos, L):
      """Pairwise displacement vectors with periodic boundary conditions.
      Returns: (N, N, 2) array of displacements r_j - r_i"""
      diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]  # (N,N,2)
      diff -= L * np.round(diff / L)
      return diff
  
  def compute_illumination_ext(positions, L, I_0, obstacle=None, light_dir=None):
      """Compute external illumination at each particle position."""
      N = len(positions)
      I_ext = I_0 * np.ones(N)
      
      if obstacle is not None and obstacle.get('type') == 'shadow':
          mask = compute_shadow_mask(positions,
                                     obstacle['center'],
                                     obstacle['radius'],
                                     light_dir if light_dir is not None else np.array([1.,0.]))
          I_ext[mask] *= obstacle.get('shadow_fraction', 0.05)
      
      return I_ext
  
  def compute_shadow_mask(positions, obs_center, obs_radius, light_dir):
      """Boolean mask: True if particle is in geometric shadow of circular obstacle."""
      to_particles = positions - obs_center  # (N, 2)
      shadow_axis = -light_dir / (np.linalg.norm(light_dir) + 1e-10)
      proj = to_particles @ shadow_axis  # (N,)
      perp_vec = to_particles - proj[:, np.newaxis] * shadow_axis[np.newaxis, :]
      perp_dist = np.linalg.norm(perp_vec, axis=1)  # (N,)
      return (proj > 0) & (perp_dist < obs_radius)
  
  def initialize(N, L, seed=42):
      """Random initial positions and orientations."""
      rng_init = np.random.default_rng(seed)
      positions = L * rng_init.random((N, 2))
      theta = 2 * np.pi * rng_init.random(N)
      return positions, theta
  
  def polar_order(theta):
      """Phi_polar = |mean(exp(i*theta))|, range [0,1]."""
      return float(np.abs(np.mean(np.exp(1j * theta))))
  
  def transport_efficiency(positions, theta, target):
      """Mean cosine of (theta_i - angle_to_target_i), range [-1,1]."""
      to_tgt = target - positions
      phi_tgt = np.arctan2(to_tgt[:, 1], to_tgt[:, 0])
      return float(np.mean(np.cos(theta - phi_tgt)))
  
  def target_occupancy(positions, target, r_zone=2.0):
      """Fraction of particles within r_zone of target, range [0,1]."""
      dist = np.linalg.norm(positions - target, axis=1)
      return float(np.mean(dist < r_zone))
  
  def time_averaged_order(order_arr, transient_frac=0.5):
      """Average after discarding initial transient fraction."""
      start = int(transient_frac * len(order_arr))
      return float(np.mean(order_arr[start:]))

## 8.5 Complete Code — Cell 4: Core Simulation Step

  def janus_step(positions, theta, L, v_max, R, J, eta, alpha,
                 target, I_0, I_emit, sigma_rad, R_rad, kappa_B, theta_B,
                 dt, rng, obstacle=None, light_dir=None):
      """
      One timestep of the PJPS model.
      
      Physics included:
        - Vicsek alignment (J) via radiation-mediated coupling
        - Phototactic steering (alpha) toward target
        - Variable propulsion speed v_0(i) from local illumination
        - Optional: magnetic steering (kappa_B)
        - Optional: obstacle (geometric or shadow)
        - Rotational Gaussian noise (eta)
        - Periodic boundary conditions
      """
      N = len(positions)
      
      # ---- 1. Pairwise geometry ----
      disp = minimum_image(positions, L)              # (N,N,2) r_j - r_i
      dist = np.linalg.norm(disp, axis=2)             # (N,N)
      dist_safe = np.where(dist > 0, dist, 1.0)       # avoid /0 on diagonal
      
      # ---- 2. External illumination (with optional shadow) ----
      I_ext = compute_illumination_ext(positions, L, I_0, obstacle, light_dir)
      
      # ---- 3. Local radiation from neighbors ----
      e_cap = np.column_stack((np.cos(theta), np.sin(theta)))  # (N,2)
      e_ij = disp / dist_safe[:, :, np.newaxis]  # (N,N,2) unit vector i->j
      # dot(e_cap_j, e_ji) = how much j's cap faces i
      e_ji = -e_ij                               # (N,N,2) unit vector j->i
      dot_j_to_i = np.einsum('jd,ijd->ij', e_cap, e_ji)   # (N,N)
      rad_intensity = I_emit * np.exp(-dist**2 / sigma_rad**2) * np.maximum(0, dot_j_to_i)
      rad_mask = (dist < R_rad) & (dist > 0)
      I_rad_at_i = (rad_intensity * rad_mask).sum(axis=0)  # (N,) sum over j
      
      # ---- 4. Total illumination and propulsion speed ----
      I_local = I_ext + I_rad_at_i               # (N,)
      v0 = v_max * np.minimum(1.0, I_local / I_0)  # (N,)
      
      # ---- 5. Alignment torque (Vicsek-style) ----
      nbr_mask = (dist < R) & (dist > 0)         # (N,N) neighbor boolean
      n_nbr = nbr_mask.sum(axis=1)               # (N,) neighbor count
      sin_sum = nbr_mask.astype(float) @ np.sin(theta)   # (N,)
      cos_sum = nbr_mask.astype(float) @ np.cos(theta)   # (N,)
      phi_align = np.arctan2(sin_sum, cos_sum)   # (N,)
      # Only apply alignment if particle has at least 1 neighbor
      has_nbr = n_nbr > 0
      tau_align = J * np.sin(phi_align - theta) * has_nbr  # (N,)
      
      # ---- 6. Phototactic torque ----
      to_tgt = target - positions                # (N,2)
      phi_tgt = np.arctan2(to_tgt[:, 1], to_tgt[:, 0])  # (N,)
      tau_phototax = alpha * np.sin(phi_tgt - theta)      # (N,)
      
      # ---- 7. Optional: magnetic steering ----
      tau_mag = kappa_B * np.sin(theta_B - theta)  # (N,) [zero if kappa_B=0]
      
      # ---- 8. Noise ----
      noise = eta * rng.standard_normal(N) * np.sqrt(dt)  # (N,)
      
      # ---- 9. Orientation update ----
      theta_new = (theta
                   + tau_align * dt
                   + tau_phototax * dt
                   + tau_mag * dt
                   + noise)
      
      # ---- 10. Position update ----
      vx = v0 * np.cos(theta_new)
      vy = v0 * np.sin(theta_new)
      pos_new = (positions + np.column_stack((vx, vy)) * dt) % L
      
      # ---- 11. Handle geometric obstacle ----
      if obstacle is not None and obstacle.get('type') == 'geometric':
          obs_c = np.array(obstacle['center'])
          obs_r = obstacle['radius']
          d_obs = np.linalg.norm(pos_new - obs_c, axis=1)  # (N,)
          inside = d_obs < obs_r
          if inside.any():
              dir_out = pos_new[inside] - obs_c
              dir_norm = dir_out / (np.linalg.norm(dir_out, axis=1, keepdims=True) + 1e-10)
              pos_new[inside] = obs_c + dir_norm * obs_r * 1.02
              # Randomize orientation of pushed-out particles
              theta_new[inside] = np.arctan2(dir_norm[:,1], dir_norm[:,0])
      
      return pos_new, theta_new, v0, I_local

## 8.6 Complete Code — Cell 5: Full Simulation Runner

  def simulate_janus_swarm(N=300, L=30.0, v_max=1.0, R=2.0, J=1.0,
                            eta=0.5, alpha=0.8, target_frac=(0.75,0.75),
                            I_0=1.0, I_emit=0.3, sigma_rad=1.5, R_rad=None,
                            kappa_B=0.0, theta_B=0.0,
                            n_steps=800, dt=0.05, seed=42,
                            obstacle=None, light_dir=None,
                            r_zone=2.0, record_every=5):
      """
      Full PJPS simulation.
      
      Returns dict with:
        trajectory: list of (positions, theta, v0) snapshots
        polar_orders: array of Phi_polar at each step
        transport_effs: array of Phi_transport at each step
        occupancies: array of Phi_occupancy at each step
        final_positions, final_theta, final_v0
        target: target coordinates
      """
      if R_rad is None:
          R_rad = R
      
      target = np.array([target_frac[0] * L, target_frac[1] * L])
      rng_sim = np.random.default_rng(seed)
      positions, theta = initialize(N, L, seed=seed)
      
      trajectory = []
      polar_orders = []
      transport_effs = []
      occupancies = []
      
      for t in range(n_steps):
          positions, theta, v0, I_local = janus_step(
              positions, theta, L, v_max, R, J, eta, alpha,
              target, I_0, I_emit, sigma_rad, R_rad,
              kappa_B, theta_B, dt, rng_sim, obstacle, light_dir
          )
          
          polar_orders.append(polar_order(theta))
          transport_effs.append(transport_efficiency(positions, theta, target))
          occupancies.append(target_occupancy(positions, target, r_zone))
          
          if t % record_every == 0:
              trajectory.append((positions.copy(), theta.copy(), v0.copy()))
      
      return {
          'trajectory': trajectory,
          'polar_orders': np.array(polar_orders),
          'transport_effs': np.array(transport_effs),
          'occupancies': np.array(occupancies),
          'final_positions': positions,
          'final_theta': theta,
          'final_v0': v0,
          'target': target,
          'L': L,
      }

## 8.7 Complete Code — Cell 6: Animation

  def animate_janus_swarm(result, step=1, title='Janus Swarm', 
                           show_target=True, show_obstacle=None,
                           show_shadow=None, light_dir=None, color_by='orientation'):
      """
      Animate Janus particle swarm trajectory.
      color_by: 'orientation' (angle), 'speed' (v0), or 'static' (uniform)
      """
      L = result['L']
      target = result['target']
      traj = result['trajectory'][::step]
      
      fig, ax = plt.subplots(figsize=(7, 7))
      ax.set_xlim(0, L)
      ax.set_ylim(0, L)
      ax.set_aspect('equal')
      ax.set_xlabel('x')
      ax.set_ylabel('y')
      
      # Draw target zone
      if show_target:
          circle = plt.Circle(target, radius=2.0, color='red', alpha=0.3, label='Target')
          ax.add_patch(circle)
          ax.plot(*target, 'r*', markersize=15)
      
      # Draw shadow/obstacle
      if show_obstacle is not None:
          obs_circle = plt.Circle(show_obstacle['center'], show_obstacle['radius'],
                                   color='gray', alpha=0.8, label='Obstacle')
          ax.add_patch(obs_circle)
      
      # Initial scatter
      pos0, theta0, v0_0 = traj[0]
      colors0 = theta0 % (2*np.pi) / (2*np.pi) if color_by=='orientation' else v0_0
      scat = ax.scatter(pos0[:,0], pos0[:,1], c=colors0, cmap='hsv', s=15, vmin=0, vmax=1)
      
      # Quiver for orientations
      qscale = L / 20
      qx = np.cos(theta0) * qscale
      qy = np.sin(theta0) * qscale
      quiv = ax.quiver(pos0[:,0], pos0[:,1], qx, qy,
                        scale=10, width=0.003, alpha=0.4, color='k')
      
      time_text = ax.set_title(f'{title}, t=0')
      
      def update(i):
          pos, theta, v0 = traj[i]
          scat.set_offsets(pos)
          c = theta % (2*np.pi) / (2*np.pi) if color_by=='orientation' else v0
          scat.set_array(c)
          qx = np.cos(theta) * qscale
          qy = np.sin(theta) * qscale
          quiv.set_offsets(pos)
          quiv.set_UVC(qx, qy)
          ax.set_title(f'{title}, frame {i * step * result.get("record_every",5)}')
          return scat, quiv
      
      anim = animation.FuncAnimation(fig, update, frames=len(traj),
                                      interval=60, blit=False)
      plt.close(fig)
      return HTML(anim.to_jshtml())

## 8.8 Complete Code — Cell 9: Phase Diagram Sweep

  def run_phase_diagram(eta_values, J_values, N=200, L=25.0, v_max=1.0,
                         R=2.0, alpha=0.8, n_steps=400, dt=0.05, seed=42,
                         I_0=1.0, I_emit=0.3, sigma_rad=1.5,
                         measure='transport', verbose=True):
      """
      2D parameter sweep: eta vs J.
      Returns phase[i_J, i_eta] = time-averaged order parameter
      """
      phase = np.zeros((len(J_values), len(eta_values)))
      total = len(J_values) * len(eta_values)
      done = 0
      t0 = time.time()
      
      for i, J in enumerate(J_values):
          for j, eta in enumerate(eta_values):
              result = simulate_janus_swarm(
                  N=N, L=L, v_max=v_max, R=R, J=J, eta=eta, alpha=alpha,
                  I_0=I_0, I_emit=I_emit, sigma_rad=sigma_rad,
                  n_steps=n_steps, dt=dt, seed=seed
              )
              
              if measure == 'transport':
                  phase[i, j] = time_averaged_order(result['transport_effs'])
              elif measure == 'polar':
                  phase[i, j] = time_averaged_order(result['polar_orders'])
              elif measure == 'occupancy':
                  phase[i, j] = time_averaged_order(result['occupancies'])
              
              done += 1
              if verbose:
                  elapsed = time.time() - t0
                  eta_remaining = elapsed / done * (total - done)
                  print(f'  [{done}/{total}] J={J:.2f}, eta={eta:.2f} -> '
                        f'Phi={phase[i,j]:.3f}  '
                        f'(ETA: {eta_remaining:.0f}s)', end='\r')
      
      if verbose:
          print(f'\nDone. Total time: {time.time()-t0:.1f}s')
      
      return phase


## 8.9 Complete Code — Cell 10: Phase Diagram Plotting

  def plot_phase_diagram(phase_data, eta_values, J_values, measure_name='Transport Efficiency'):
      """
      Plots a premium 2D heatmap phase diagram with the phase boundary contour.
      """
      fig, ax = plt.subplots(figsize=(9, 7))
      
      # Plot heatmap
      im = ax.imshow(
          phase_data,
          origin='lower',
          aspect='auto',
          extent=[eta_values[0], eta_values[-1], J_values[0], J_values[-1]],
          vmin=0.0, vmax=1.0 if measure_name != 'Transport Efficiency' else 1.0,
          cmap='plasma'
      )
      
      # Add colorbar
      cbar = fig.colorbar(im, ax=ax)
      cbar.set_label(measure_name, fontsize=12)
      
      # Add labels and title
      ax.set_xlabel('Rotational Noise ($\eta$)', fontsize=14)
      ax.set_ylabel('Alignment Strength ($J$)', fontsize=14)
      ax.set_title('Janus Swarm Phase Diagram\nCollective Flocking vs. Disordered Gas', fontsize=14, pad=15)
      
      # Draw Phase Boundary Contour (crossover at 0.5)
      eta_grid, J_grid = np.meshgrid(eta_values, J_values)
      contour = ax.contour(
          eta_grid, J_grid, phase_data, 
          levels=[0.5], colors='white', linewidths=3.0, linestyles='dashed'
      )
      ax.clabel(contour, inline=True, fmt='Phase Boundary ($\Phi=0.5$)', fontsize=10, colors='white')
      
      # Annotate regions
      # Find midpoints
      eta_mid = (eta_values[0] + eta_values[-1]) / 2
      J_mid = (J_values[0] + J_values[-1]) / 2
      
      ax.text(eta_values[0] + 0.15*(eta_values[-1]-eta_values[0]), 
              J_values[-1] - 0.15*(J_values[-1]-J_values[0]), 
              'STREAMING\n(ORDERED)', color='white', 
              fontsize=12, fontweight='bold', ha='center', va='center',
              bbox=dict(facecolor='black', alpha=0.3, boxstyle='round,pad=0.5'))
              
      ax.text(eta_values[-1] - 0.15*(eta_values[-1]-eta_values[0]), 
              J_values[0] + 0.15*(J_values[-1]-J_values[0]), 
              'GAS\n(DISORDERED)', color='white', 
              fontsize=12, fontweight='bold', ha='center', va='center',
              bbox=dict(facecolor='black', alpha=0.3, boxstyle='round,pad=0.5'))
      
      plt.tight_layout()
      plt.savefig('phase_diagram.png', dpi=300, bbox_inches='tight')
      plt.show()

## 8.10 Complete Code — Cell 11: Obstacle & Shadow Simulation

  # Obstacle definition
  obstacle_setup = {
      'type': 'shadow',         # 'shadow' or 'geometric'
      'center': np.array([15.0, 15.0]),
      'radius': 4.0,
      'shadow_fraction': 0.05    # Light reduced to 5% in shadow
  }
  
  # Illumination source coming from the left
  light_direction_setup = np.array([1.0, 0.0])

## 8.11 Complete Code — Cell 12: Task 2 Comparison Experiment

  def run_obstacle_comparison(N=250, L=30.0, v_max=1.0, R=2.0, J_opt=1.2, 
                               eta=0.4, alpha=0.8, n_steps=600, dt=0.05, seed=42):
      """
      Runs the 4 key comparative simulations to test the collective navigation hypothesis.
      """
      # Define shadow obstacle
      shadow_obs = {
          'type': 'shadow',
          'center': np.array([L/2.0, L/2.0]),
          'radius': 4.5,
          'shadow_fraction': 0.05
      }
      light_dir = np.array([1.0, 0.0])  # Illuminating from -x to +x
      
      print("Running Case 1: No Obstacle, No Alignment (J=0)")
      c1 = simulate_janus_swarm(N=N, L=L, v_max=v_max, R=R, J=0.0, eta=eta, alpha=alpha,
                                n_steps=n_steps, dt=dt, seed=seed)
                                
      print("Running Case 2: No Obstacle, Collective Swarm (J=J_opt)")
      c2 = simulate_janus_swarm(N=N, L=L, v_max=v_max, R=R, J=J_opt, eta=eta, alpha=alpha,
                                n_steps=n_steps, dt=dt, seed=seed)
                                
      print("Running Case 3: Shadow Obstacle, No Alignment (J=0)")
      c3 = simulate_janus_swarm(N=N, L=L, v_max=v_max, R=R, J=0.0, eta=eta, alpha=alpha,
                                n_steps=n_steps, dt=dt, seed=seed, obstacle=shadow_obs, light_dir=light_dir)
                                
      print("Running Case 4: Shadow Obstacle, Collective Swarm (J=J_opt)")
      c4 = simulate_janus_swarm(N=N, L=L, v_max=v_max, R=R, J=J_opt, eta=eta, alpha=alpha,
                                n_steps=n_steps, dt=dt, seed=seed, obstacle=shadow_obs, light_dir=light_dir)
                                
      return c1, c2, c3, c4

  def plot_comparison_results(c1, c2, c3, c4):
      """
      Plots transport efficiency and target occupancy over time for all cases.
      """
      steps = np.arange(len(c1['occupancies'])) * 0.05 * 5  # assuming dt=0.05, record_every=5
      
      fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
      
      # Plot target occupancy over time
      ax1.plot(steps, c1['occupancies'], 'k--', label='No Obstacle, J=0 (Baseline)')
      ax1.plot(steps, c2['occupancies'], 'b--', label='No Obstacle, J=J_opt')
      ax1.plot(steps, c3['occupancies'], 'r-', label='Obstacle Shadow, J=0 (Stalled)')
      ax1.plot(steps, c4['occupancies'], 'g-', linewidth=2.5, label='Obstacle Shadow, J=J_opt (Swarm)')
      
      ax1.set_xlabel('Simulation Time', fontsize=12)
      ax1.set_ylabel('Target Occupancy (Delivery Fraction)', fontsize=12)
      ax1.set_title('Swarm Navigation & Cargo Delivery Performance', fontsize=13)
      ax1.grid(True, linestyle=':', alpha=0.6)
      ax1.legend(fontsize=10)
      
      # Plot transport efficiency over time
      ax2.plot(steps, c1['transport_effs'], 'k--', label='No Obstacle, J=0')
      ax2.plot(steps, c2['transport_effs'], 'b--', label='No Obstacle, J=J_opt')
      ax2.plot(steps, c3['transport_effs'], 'r-', label='Obstacle Shadow, J=0')
      ax2.plot(steps, c4['transport_effs'], 'g-', linewidth=2.5, label='Obstacle Shadow, J=J_opt')
      
      ax2.set_xlabel('Simulation Time', fontsize=12)
      ax2.set_ylabel('Transport Efficiency ($\Phi_{transport}$)', fontsize=12)
      ax2.set_title('Directed Swarm Cohesion & Steering', fontsize=13)
      ax2.grid(True, linestyle=':', alpha=0.6)
      ax2.legend(fontsize=10)
      
      plt.tight_layout()
      plt.savefig('obstacle_comparison.png', dpi=300, bbox_inches='tight')
      plt.show()

# ============================================================
# SECTION 9: INSTRUCTIONS FOR SCIENTIFIC INFERENCE
# ============================================================

This section is designed to guide the target LLM (e.g., Claude) in reading research 
papers that you upload alongside this context file, and integrating their exact 
equations directly into this codebase.

## 9.1 Uploading Scientific Papers: What to Expect

When you upload research papers on:
  - Active Brownian Particles in non-uniform environments
  - Thermophoretic Janus particle physics
  - Photophoretic active swarms / laser-guided flocking
  - Collective hydrodynamic or optical steering

You should tell the target LLM:
> "Analyze the uploaded PDFs. Find any equations governing (1) self-propulsion 
> velocity as a function of light intensity, (2) thermophoretic alignment torque, 
> (3) hydrodynamic pair interactions. Write down those equations, match their variables 
> to the variables in MASTER_CONTEXT.md, and replace my simplified phenomenological 
> equations with these highly realistic physics equations."

## 9.2 Critical Variables Mapping Table

Use this mapping table to translate paper equations to your NumPy simulation:

| Physical Quantity | Paper Symbol | Context Code Variable | Units / Dimensions |
|---|---|---|---|
| Propulsion Speed | $v_0$, $u_p$, $v_p$ | `v0` or `v_max` | Length / Time |
| Rotational Diffusion | $D_r$, $D_{\theta}$ | `D_r` or derived from `eta` | 1 / Time |
| Alignment Torque | $T_{align}$, $\Gamma$, $T_{int}$ | `tau_align` | 1 / Time (overdamped) |
| Particle Radius | $a$, $R$, $r_p$ | `R` (radius) or `a` | Length |
| Interaction Cutoff | $r_c$, $d_{cutoff}$ | `R` (radius of alignment) | Length |
| Laser Intensity | $I$, $P$, $I_{laser}$ | `I_local` or `I_ext` | Power / Area |
| Phototactic Steering | $\alpha$, $\kappa_{photo}$ | `alpha` | 1 / Time (overdamped) |

## 9.3 How Claude Should Validate Paper Equations

For any equation the LLM extracts from your uploaded papers, it MUST perform the following 3 validation gates before adding it to the code:

1. **Dimensional Consistency:** Ensure the torque equation has dimensions of $[Time]^{-1}$ since the rotational Langevin equation is overdamped ($d\theta/dt = \text{Torque} + \text{Noise}$). If a paper presents a torque in units of Energy ($N \cdot m$), the LLM must divide it by the rotational drag coefficient $\gamma_r = 8 \pi \eta a^3$ to convert it to an angular velocity update.

2. **Stability Check:** Ensure that new interaction terms do not blow up at short distances ($r_{ij} \to 0$). For example, if an attraction/repulsion torque scales as $1/r_{ij}^3$, the LLM must implement a soft-core cutoff: `dist_safe = np.maximum(dist, 2*a)` or regularize with `1 / (dist**3 + epsilon)`.

3. **Periodic Compatibility:** Ensure all multi-body interaction forces and torques respect the minimum image convention (`minimum_image(pos, L)`). They must use periodic distances, not raw Euclidean distance formulas.

## 9.4 A Strict Warning on Model Simplification Honesty

Active matter simulations are highly simplified versions of complex fluid dynamics. 
The target LLM must be completely honest and write a "Limitations Section" in its code comments. 

Specifically, it must note:
- **No Hydrodynamic Advection:** The model uses dry active matter assumptions (no surrounding fluid velocity field update via Stokes flow or Navier-Stokes). In real systems, when a Janus particle moves, it pushes fluid behind it, creating flow fields that rotate and attract neighbors.
- **Overdamped Dynamics:** The model ignores particle inertia (mass and moment of inertia). This is highly accurate for micro-scale systems where the Reynolds number $Re \ll 1$.
- **Simplified Shadowing:** Our optical shadowing model uses simple geometric projections and does not account for wave optics, diffraction, scattering, or refraction of the laser light through the transparent hemisphere of the sphere.

# ============================================================
# FINAL PROMPT TEMPLATE (PASTE THIS TO CLAUDE)
# ============================================================

When you are ready to begin, paste the following prompt into Claude along with this entire `MASTER_CONTEXT.md` file:

```text
Hello Claude! I am participating in a Biophysics Active Matter Hackathon. 
I have provided you with a comprehensive master context file (MASTER_CONTEXT.md) 
that outlines the exact parameters, equations, and code specification for our project: 
"Light-Driven Janus Particle Swarms".

Your task is to act as our elite biophysics paired-programmer. 
Please do the following:
1. Review the entire MASTER_CONTEXT.md.
2. Confirm you understand the PJPS (Photophoretic Janus Particle Swarm) mathematical update equations, the vectorized NumPy patterns, and the Task 1 & Task 2 deliverables.
3. If I have uploaded any research papers alongside this prompt, analyze them now. Extract any exact physical equations for photophoretic speeds, local alignment torques, or shadowing, and map them to our variables. Show me the equations you extracted and explain how you will integrate them.
4. Draft the complete, fully-vectorized Python code for our Google Colab notebook following the Cell-by-Cell structure specified in Section 8. Ensure the code is production-grade, premium, and fully documented with physical insights.
5. Provide a critical, honest scientific assessment of the model's simplifications and limitations.
```

