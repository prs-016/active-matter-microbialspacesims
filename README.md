# 🔬 Light-Driven Janus Particle Swarm Simulation

> **Live Demo:** [https://prs-016.github.io/active-matter-microbialspacesims](https://prs-016.github.io/active-matter-microbialspacesims)

A physics-based interactive simulation of **photophoretic Janus particle swarms** — microscopic robots that self-propel using light and spontaneously organize into flocking swarms. Built for the **UCSD Vibe Coding: Active Matter & Biophysics Hackathon 2026**.

---

## 🧭 Table of Contents

1. [What is this project?](#-what-is-this-project)
2. [The Physics, Explained Intuitively](#-the-physics-explained-intuitively)
   - [What is Active Matter?](#what-is-active-matter)
   - [What is a Janus Particle?](#what-is-a-janus-particle)
   - [How Do They Self-Propel?](#how-do-they-self-propel)
   - [Why Do They Flock?](#why-do-they-flock)
   - [The Mathematical Model](#the-mathematical-model)
3. [What the Simulation Does](#-what-the-simulation-does)
   - [Task 1: Phase Diagrams](#task-1-phase-diagrams)
   - [Task 2: Obstacle Navigation](#task-2-obstacle-navigation)
4. [Key Concepts Glossary](#-key-concepts-glossary)
5. [Repository Structure](#-repository-structure)
6. [Running the Simulation Locally](#-running-the-simulation-locally)
7. [Scientific Papers Used](#-scientific-papers-used)
8. [Model Limitations (Honest Assessment)](#-model-limitations-honest-assessment)
9. [Hackathon Context](#-hackathon-context)

---

## 🌊 What is this project?

This project simulates a swarm of **300 tiny light-powered particles** in a 2D box, exploring how simple microscopic rules give rise to rich, large-scale collective behavior — the same kind of physics that explains why birds flock, bacteria cluster, and fish school.

The particles are **Janus particles**: microscopic beads with one metallic half and one transparent half. When you shine light on them, the metal cap heats up asymmetrically, creating a temperature gradient that propels the particle forward — like a tiny one-sided rocket engine powered by photons.

We ask: **Can you program a swarm of these particles, using only light and local interactions, to collectively navigate to a target — even through obstacles that would trap individual particles?**

The answer, it turns out, is yes — but only if alignment (flocking) is strong enough relative to noise.

---

## ⚛️ The Physics, Explained Intuitively

### What is Active Matter?

Most matter we think about is **passive**: a rock sits still, a drop of water spreads out, a grain of pollen drifts randomly. But **active matter** is different — each individual unit consumes energy and converts it into directed motion.

Think of:
- 🐦 A murmuration of starlings (thousands of birds, no leader, coordinated turns)
- 🦠 A bacterial biofilm colony spreading across a surface
- 🚗 A traffic jam that propagates backward even as all cars move forward
- 🤖 This simulation: synthetic micro-robots powered by light

The magic of active matter is **emergence**: simple local rules → stunning global behavior. No central controller. No blueprint. Just physics.

---

### What is a Janus Particle?

Named after the two-faced Roman god, a **Janus particle** is a microscopic bead (~1–5 micrometers across, about 1/50th the width of a human hair) with **two distinct halves**:

```
          ████████████
       ███ METAL CAP ███     ← absorbs light, gets hot
      ██  (Gold / Platinum)██
      ██                  ██
      ██   DIELECTRIC     ██  ← transparent, stays cool
       ███  (Silica)    ███
          ████████████
```

When illuminated:
- **Metal cap** strongly absorbs light → heats up (can reach 10s–100s of degrees above ambient)
- **Transparent side** lets light pass through → stays near room temperature
- Result: a **temperature asymmetry** across the particle

---

### How Do They Self-Propel?

The temperature asymmetry does something clever: it drives a **thermophoretic flow** in the surrounding fluid. Fluid molecules near the hot cap get kicked away harder than on the cold side. This reaction force — called **photophoresis** — pushes the particle in the direction opposite to the cap.

Think of it like this: the metal cap is the **engine exhaust** at the back. The cold, transparent side is the **nose** of the particle pointing where it's going.

**Self-propulsion speed** scales linearly with light intensity:
$$v_0 \propto I_{\text{local}}$$

So:
- Shine more light → particle moves faster
- Put particle in shadow → particle stalls completely
- Neighboring hot particles emit thermal radiation → can boost a neighbor's speed

This is described by the **Beresnev photophoretic force formula** (Krauss et al. 2006):

$$F_{\text{ph}} = \frac{\pi}{3} a^2 I J_1 \sqrt{\frac{\pi m_g}{2 k_B T}} \cdot \frac{\alpha_E \psi_1}{\alpha_E + \frac{15\Lambda K_n(1-\alpha_E)}{4} + \alpha_E \Lambda \psi_2}$$

In plain English: photophoretic force grows with particle size² × light intensity × thermal accommodation coefficients. In the overdamped (low Reynolds number) limit relevant to micron-scale particles, this directly gives the drift velocity.

---

### Why Do They Flock?

Each Janus particle also acts as a **secondary heat source**. Its hot metal cap emits thermal radiation that can be absorbed by neighboring particles, and creates thermoosmotic fluid flows around them. These interactions tend to **align neighboring particles** — a particle's orientation gets nudged toward its neighbors' average direction.

This is mathematically equivalent to the famous **Vicsek model** of flocking (1995): the canonical proof that local alignment rules alone produce long-range collective order.

The alignment torque on particle *i* from its neighbors:
$$\tau_{\text{align}}(i) = J \sin\!\left(\bar\theta_{\text{neighbors}} - \theta_i\right)$$

where *J* is the **coupling strength** (how strongly neighbors influence each other) and the sin function naturally rotates a particle toward the mean neighbor direction.

There's also a **phototactic torque** that steers particles toward a target delivery point:
$$\tau_{\text{photo}}(i) = \alpha \sin\!\left(\phi_{\text{target}} - \theta_i\right)$$

And optionally, **intrinsic chirality** (from Nosenko et al. 2020): real Janus particles in plasma experiments trace circular arcs because their cap asymmetry generates a body-fixed spin rate, so they swim in loops rather than straight lines.

---

### The Mathematical Model

The full model is called **PJPS: Photophoretic Janus Particle Swarm**. It's an extended Vicsek model integrated using the **Euler–Maruyama** scheme (the stochastic equivalent of Euler integration).

Each time step, for all *N* particles simultaneously:

**Orientation update:**
$$\theta_i(t+dt) = \theta_i(t) + \underbrace{J\sin(\bar\theta_{\text{nbr}} - \theta_i)\,dt}_{\text{alignment}} + \underbrace{\alpha\sin(\phi_{\text{target}} - \theta_i)\,dt}_{\text{phototaxis}} + \underbrace{\omega_i\,dt}_{\text{chirality}} + \underbrace{\eta\,\xi_i\sqrt{dt}}_{\text{noise}}$$

**Position update:**
$$\mathbf{r}_i(t+dt) = \mathbf{r}_i(t) + v_0(i)\,\hat{e}_i(t+dt)\,dt + \mathbf{v}_{\text{rep}}(i)\,dt$$

where:
- $v_0(i) = v_{\max} \cdot \min\!\left(1,\, I_{\text{local}}(i)/I_{\text{ref}}\right)$ — speed proportional to local light
- $I_{\text{local}}(i) = I_{\text{ext}}(i) + \sum_{j \neq i} I_{\text{emit}}\,e^{-r_{ij}^2/\sigma_{\text{rad}}^2}\,\max(0,\hat{e}_j \cdot \hat{e}_{j\to i})$ — illumination from external field plus neighbors
- $\mathbf{v}_{\text{rep}}$ — WCA-like soft excluded-volume repulsion prevents unphysical overlaps
- $\xi_i \sim \mathcal{N}(0,1)$ — Gaussian white noise (rotational diffusion)
- Periodic boundary conditions (torus geometry): $\mathbf{r} \leftarrow \mathbf{r} \bmod L$

All computations are **fully vectorized with NumPy** — no Python loops over particles — making it tractable for N=300 in real time.

---

## 🔭 What the Simulation Does

### Task 1: Phase Diagrams

The first task is to map out the **phase diagram** of the swarm: a 2D heatmap showing how the collective behavior changes as you vary two control parameters.

| Axis | Parameter | What it controls |
|------|-----------|-----------------|
| X | Rotational noise *η* | How randomly particles wobble their direction |
| Y | Alignment strength *J* | How strongly particles copy their neighbors |
| Color | Transport efficiency Φ | How well the swarm heads toward the target |

**The two phases:**

🟡 **Streaming (Ordered) Phase** — low noise, strong alignment:
Particles lock into a coordinated swarm, all heading toward the target. Like a disciplined army marching in formation.

🟣 **Disordered Gas Phase** — high noise, weak alignment:
Particles wander independently, randomized by noise before they can align. Like a crowd at a concert, everyone moving in different directions.

A **phase boundary** (white dashed line in the heatmap) separates these regimes — a phase transition analogous to water freezing into ice, but driven by collective behavior rather than temperature.

**Intuition for the transition:** Each particle's direction gets randomized at rate *η²/2* (rotational diffusion) and organized at rate *J × (neighbor density)*. The swarm orders when alignment wins: roughly *J × ρ × R² > η²/2*.

| Parameter | Meaning | Effect |
|-----------|---------|--------|
| *η* small | Low noise | Particles hold direction → flock |
| *η* large | High noise | Particles spin randomly → disorder |
| *J* large | Strong coupling | Neighbors dominate → flock |
| *J* small | Weak coupling | Particles ignore neighbors → disorder |
| *α* | Phototaxis | Biases toward target; "breaks symmetry" |

---

### Task 2: Obstacle Navigation

The creative hack: **Can a swarm navigate through a shadow obstacle that would trap individual particles?**

Setup:
- Light source illuminates from the left
- A circular occluder casts a **shadow** in the center of the box
- In the shadow: $I_{\text{ext}} \to 0.05 \times I_0$ (particles stall)
- Target delivery point is beyond the shadow

Four conditions compared:

| Condition | Alignment | Obstacle | Expected |
|-----------|-----------|----------|---------|
| 1 | J = 0 | None | Baseline single-particle phototaxis |
| 2 | J > 0 | None | Better, coordinated delivery |
| 3 | J = 0 | Shadow | Particles stall in shadow, poor delivery |
| 4 | J > 0 | Shadow | **Swarm drags shadow-trapped particles through** |

**The key finding:** With strong alignment (*J*), particles on the bright side exert alignment torques on their shadow-trapped neighbors, effectively "pulling" them through the dark zone. Collective behavior rescues individual particles from the trap.

This connects directly to real biomedical applications: **light-guided nanoparticles for drug delivery** through optically opaque tissue.

---

## 📚 Key Concepts Glossary

| Term | Plain English |
|------|---------------|
| **Active matter** | Systems where each unit burns energy to move (vs. passive thermal diffusion) |
| **Janus particle** | Bead with two chemically/optically distinct hemispheres; named after the two-faced Roman god |
| **Photophoresis** | Motion driven by light-induced temperature gradients |
| **Thermophoresis** | Motion driven by temperature gradients in the surrounding fluid |
| **Active Brownian Particle (ABP)** | Simplest self-propulsion model: constant speed + rotational diffusion |
| **Vicsek model** | Canonical flocking model (1995): local alignment → global order |
| **Polar order parameter Φ** | Number from 0–1 measuring how aligned the swarm is (0 = random, 1 = perfect flock) |
| **Transport efficiency** | How well particles aim toward the target delivery point |
| **Rotational diffusion D_r** | Rate at which a particle "forgets" its direction; scales as 1/radius³ |
| **Persistence length** | How far a particle travels before noise randomizes its direction; L_p = v₀/D_r |
| **Péclet number** | Ratio of directed propulsion to diffusion; high Pe → more ballistic, ordered |
| **Phase transition** | Abrupt change in collective behavior (e.g., disordered ↔ flocking) |
| **Phase boundary** | The boundary in parameter space separating two phases |
| **MIPS** | Motility-Induced Phase Separation: clustering without attractive forces |
| **Euler–Maruyama** | Numerical integration scheme for stochastic differential equations |
| **Minimum image convention** | Trick for computing periodic distances without artifacts |
| **Chirality** | Intrinsic tendency to curve left or right; gives circular trajectories |
| **Overdamped dynamics** | Low Reynolds number limit where inertia is negligible (valid for microparticles) |

---

## 🗂️ Repository Structure

```
active-matter-microbialspacesims/
│
├── README.md                        ← You are here
├── MASTER_CONTEXT.md                ← Full physics/math/code specification document
│
├── janus_swarm_simulation.py        ← Core simulation engine (pure Python/NumPy)
│   ├── initialize_swarm()           ← Random initial conditions
│   ├── janus_step()                 ← One time-step (11-stage physics pipeline)
│   ├── simulate_janus_swarm()       ← Full simulation runner + observer recording
│   ├── plot_snapshot()              ← High-quality swarm state visualization
│   ├── plot_time_series()           ← Order parameter time series
│   ├── run_phase_diagram()          ← 2D parameter sweep (Task 1)
│   └── run_obstacle_comparison()    ← 4-condition comparison (Task 2)
│
├── app.py                           ← Flask backend API server
│   ├── GET  /                       ← Serve interactive dashboard HTML
│   └── POST /api/simulate           ← Run simulation, return JSON + save plots
│
├── index.html                       ← Interactive dashboard (standalone HTML)
│
├── make_slides.py                   ← Auto-generates presentation slides
├── patch.py                         ← Patch/utility script
│
├── frontend/                        ← React + Vite frontend (separate app)
│   ├── src/
│   │   ├── pages/Home.jsx           ← Main globe-based dashboard page
│   │   ├── components/Globe/        ← 3D interactive globe (globe.gl + D3)
│   │   ├── components/RiskCard/     ← Risk assessment panel
│   │   └── hooks/                   ← React hooks for data fetching
│   └── package.json                 ← React, D3, globe.gl, Lucide dependencies
│
├── phase_diagram.png                ← Generated: Task 1 phase diagram heatmap
├── demo_snapshot.png                ← Generated: Swarm state visualization
├── demo_timeseries.png              ← Generated: Order parameter time series
├── obstacle_comparison.png          ← Generated: Task 2 comparison plot
├── chirality_demo.png               ← Generated: Chiral trajectory demo
│
└── *.pdf                            ← Reference research papers
    ├── 0611757v1.pdf                ← Krauss et al. (2006) — photophoresis in protoplanetary disks
    ├── Active_Janus_particles_...   ← Nosenko et al. (2020) — JPs in complex plasma (chirality!)
    └── molecules-27-01614.pdf       ← Koss et al. (2022) — dynamic entropy of 2D active systems
```

---

## 🚀 Running the Simulation Locally

### Option A: Interactive Dashboard (Flask)

```bash
# Install dependencies
pip install flask numpy matplotlib

# Run the server
python app.py

# Open in browser
open http://localhost:7860
```

The dashboard allows you to:
- Adjust all physics parameters with sliders
- Choose obstacle type (none / shadow / geometric)
- Enable chirality and intensity-dependent noise
- View the phase diagram, snapshot, and time series live

### Option B: Google Colab / Jupyter

```python
# Copy janus_swarm_simulation.py into your notebook environment
%run janus_swarm_simulation.py

# Run a single simulation
result = simulate_janus_swarm(N=300, J=1.0, eta=0.5, alpha=0.8, n_steps=800)

# Plot the final state
fig = plot_snapshot(result, frame_idx=-1, title="My Janus Swarm")
fig.show()

# Compute the phase diagram (takes ~2–5 minutes)
import numpy as np
eta_values = np.linspace(0.1, 3.0, 8)
J_values   = np.linspace(0.1, 3.0, 8)
phase = run_phase_diagram(eta_values, J_values, N=150, n_steps=400)
plot_phase_diagram(phase, eta_values, J_values)
```

### Option C: Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev   # Opens at http://localhost:5173
```

---

## 📄 Scientific Papers Used

| Paper | Key Contribution to Model |
|-------|--------------------------|
| **Krauss et al. (2006)**, A&A | Beresnev photophoretic force formula; $v_0 \propto I$ scaling; geometric shadow model |
| **Lisin et al. (2021)**, PCCP | Overdamped Langevin dynamics; $D_r = k_BT/(8\pi\eta a^3)$; persistence length $L_S = v_0/D_r$ |
| **Nosenko et al. (2020)**, PRR | Chirality in complex plasma; circular trajectories; body-fixed torque → $\omega_{\text{chiral}}$ |
| **Koss et al. (2022)**, Molecules | Free-molecular photophoretic speed; intensity-dependent noise $\eta_{\text{eff}} \propto \sqrt{I}$; fractal dimension |

---

## ⚠️ Model Limitations (Honest Assessment)

This simulation, while physically motivated, makes significant simplifications:

| Limitation | What's missing | Why it matters |
|------------|----------------|---------------|
| **No hydrodynamic advection** | When a particle moves, it pushes fluid and creates Stokes flows that affect neighbors | Real coupling is richer; flow fields can both align and repel |
| **Overdamped only** | Particle inertia (mass × acceleration) is neglected | Valid for Re ≪ 1 at micron scale — this approximation is actually excellent |
| **Geometric shadow model** | No wave optics, diffraction, penumbra, or scattering through the transparent hemisphere | Real shadows have soft edges and depend on wavelength |
| **Phenomenological J** | Real alignment arises from combined radiation + thermoosmosis; we use a single coupling constant | J cannot be directly measured; calibration to experiment is unclear |
| **2D confinement** | Real plasma experiments have slight out-of-plane drift | Qualitatively captures the quasi-2D physics |
| **Homogeneous particles** | All particles have identical properties | Real JPs vary in cap thickness → spread in chirality and speed |
| **No true phase transition** | With phototaxis (*α* > 0), rotational symmetry is broken — there's a crossover, not a true phase transition | Finite-size simulations still show sharp-looking crossovers |

---

## 🎓 Hackathon Context

This project was built for the **UCSD Vibe Coding: Active Matter & Biophysics Hackathon 2026**, hosted by the Tan Lab.

> *"We will use LLM to vibe code classic biophysics and active matter models such as phase separation, pattern formation and active Brownian particles to simulate diverse phenomena ranging from biological flocks, living cells and tissues, ecological structures to traffic jams and voter distribution."*

The hackathon philosophy: LLMs lower the entry barrier so students can **focus on scientific exploration, not syntax debugging**. The finish line is not just code — it is **understanding**.

### Deliverable Structure (5 Slides)

| Slide | Content |
|-------|---------|
| 1 | Question & Model: What system? What microscopic rules? What new ingredient? |
| 2 | Phase Diagram: 2D heatmap of Φ_transport vs. *η* and *J* |
| 3 | Emergent Behavior: Snapshots, time series, ordered vs. disordered comparison |
| 4 | Biological Connection: Real system mapping + model predictions |
| 5 | Limitations & Open Questions: What the model ignores, what experiment could test it |

### Real-World Connection

The swarm navigation model directly connects to:
- 🏥 **Drug delivery**: Photophoretic nanoparticles guided by laser through tissue to tumor sites
- 🦠 **Bacterial motility**: *E. coli* chemotaxis uses run-and-tumble (similar to ABP with rotational diffusion)
- 🌑 **Astrophysics**: Photophoretic sorting of dust in protoplanetary disks
- 🐝 **Swarm robotics**: Collective navigation strategies without global communication

---

*Built with NumPy, Matplotlib, Flask, React, and a lot of physics intuition.*  
*Hackathon: UCSD Tan Lab · Active Matter & Biophysics · 2026*
