# Prompt 02: Validated constant-thrust rocket flight

- Date: 2026-08-27 (America/Vancouver)
- Scope: physics
- Starting commit: `4fe35c6b58fb5581d6671e56b09ad327e4fc32ee`
- Implementation commit: `6ea447baa425216957a0b2bc552e8655cc663f8b`
- Implementation commit message: `Implement validated constant-thrust rocket flight`
- Target remote: `https://github.com/eugenelin89/rocketsim.git`
- Target branch: `main`
- Push status at record creation: implementation commit exists locally; implementation and prompt-record commits are pending the final non-force push

## Starting repository state

Prompt 02 began on clean `main` tracking `origin/main` at Prompt 01 record commit `4fe35c6`. The repository contained the installable package and one package-import test but no flight physics, simulation lifecycle, renderer, or Pygame application loop. The primary development interpreter was Python 3.12.14 at `/Users/eugenelin/.conda/envs/rocketsim/bin/python`, with pip from the same environment.

The next unused archive IDs were Prompt 02 and Decision 02. No unrelated user changes were present.

## Requirements and constraints

The implementation was restricted to a 2D constant-mass point rocket under constant gravity and finite-duration constant thrust at a fixed world angle. It required a fixed physics timestep, powered/coast phases, exact burnout semantics, ground-return termination, a minimal Pygame visualization and telemetry, analytical and convergence evidence, FPS independence, and deterministic reset.

Explicit non-goals included drag, atmosphere, wind, variable mass, real motor curves, recovery, rotation, stability, guidance, control, experiment infrastructure, optimization, machine learning, networking, and cloud features. The parent agent was the sole implementer. Specialist reviewers were read-only.

## Persistent specialist infrastructure

Created exactly:

- `.codex/agents/physics_reviewer.toml`
- `.codex/agents/numerical_reviewer.toml`
- `.codex/agents/test_reviewer.toml`

Each file was parsed with Python 3.12 `tomllib`, contained the required `name`, `description`, and `developer_instructions` keys, set `sandbox_mode = "read-only"` and `model_reasoning_effort = "high"`, and omitted `model` so the parent model is inherited.

The active collaboration runtime did not expose a custom-agent-type selector and therefore could not honestly demonstrate hot-loading the newly checked-in project agent names. Prompt 02's documented fallback was used: three persistent delegated agents named `physics_reviewer`, `numerical_reviewer`, and `test_reviewer` were explicitly instructed to read and follow their corresponding TOML definitions and remain read-only. All three were invoked successfully for pre-review, post-review, and final resolution review. No specialist modified repository files.

`AGENTS.md` now records when each specialist is required, their read-only authority, central parent ownership, and the pre-review/implementation/post-review/validation/commit workflow.

## Pre-implementation review and reconciliation

| Specialist | Principal findings | Reconciled contract |
| --- | --- | --- |
| Physics | Use SI units, +y upward, `F_g=(0,-mg)`, fixed-world `F_T=T(cos(theta),sin(theta))`, and exact half-open burn time `0 <= t < burn_time`. A crossing step must split at burnout. Ground return must not trigger at initial `y=0`. Analytical references must be independent. | Adopt the exact force model and half-open boundary; track liftoff; use a default configuration with thrust exceeding weight; keep gravity/zero-thrust references above ground when needed. |
| Numerical | Semi-implicit Euler must update velocity before position. A force-discontinuity crossing must be segmented. The wall-time accumulator must not drop elapsed time. Landing treatment must be deterministic and documented. Velocity is exact for aligned constant acceleration while position has first-order error. | Use fixed `dt=0.01 s`; split exactly at burnout; retain fractional wall time; linearly interpolate the first descending discrete ground crossing; derive tolerances from `0.5*a*t*dt`; require convergence and 30/60/144 FPS partition evidence. |
| Tests | The baseline import test was insufficient. Required independent configuration, force, boundary, integrator, analytical, limiting-case, convergence, lifecycle, reset, FPS, rendering-isolation, and app-smoke evidence. Expected values must not reuse production helpers. | Build literal closed-form oracles and boundary examples, deliberately use a non-aligned burnout case, exercise the public accumulator for FPS evidence, and provide a bounded SDL dummy application path. |

There was no unresolved disagreement among the specialists. The parent independently reconciled their reports against the governing project context and documented the durable state, numerical/event, and review-workflow choices in Decisions 02–04.

## Scientific model and equations

Internal coordinates and units are:

- world +x: horizontal/right
- world +y: upward
- ground: `y=0`
- position: metres
- velocity: metres per second
- acceleration: metres per second squared
- force: newtons
- mass: kilograms
- time: seconds
- angle: radians

For constant mass `m`, gravity magnitude `g`, thrust magnitude `T`, fixed angle `theta`, and burnout time `t_b`:

```text
F_g = (0, -m g)

F_T(t) = T(cos(theta), sin(theta))  for 0 <= t < t_b
F_T(t) = (0, 0)                    otherwise

a(t) = (F_g + F_T(t)) / m
```

No drag, variable mass, attitude dynamics, empirical damping, velocity clamp, or game-feel force is present.

## Numerical method and events

Each constant-acceleration segment uses semi-implicit Euler:

```text
v_next = v_current + a_current dt
p_next = p_current + v_next dt
```

A fixed step that spans burnout is split into a powered segment ending exactly at `t_b` and a coast segment for the remainder. At exact burnout the resulting phase and instantaneous acceleration are coast values.

For constant acceleration over `t=N*dt`, velocity is exact to floating-point error and:

```text
p_numerical - p_analytical = 0.5 a t dt
```

The display clock feeds a compensated floating-point accumulator. Only complete fixed steps advance physics; zero and representably subthreshold elapsed time never fabricate a step. Pre-launch and paused wall time do not accumulate, and reset clears state, history, counter, accumulator, and compensation.

Ground return is eligible only after a resolved positive-altitude state. The first later descending segment crossing `y=0` is linearly interpolated in time, horizontal position, and velocity, then altitude is set to zero and the state becomes terminal. This is interpolation of the discrete numerical path, not an exact impact root. A ground start with downward velocity, or whose first constant-force numerical segment does not end above ground, terminates at its initial ground state rather than recording negative altitude. Terminal thrust and acceleration describe the instant of impact and therefore remain time-consistent if impact precedes burnout.

## Implementation summary

Implemented:

- immutable neutral `Vector2`, validated `SimulationConfig`, and immutable `RocketState`
- Pygame-independent force equations and semi-implicit Euler segment integration
- deterministic launch/pause/reset/step lifecycle and trajectory history
- exact powered/coast transition and burnout segmentation
- compensated fixed-step wall-time accumulation
- deterministic liftoff and interpolated landing semantics
- Pygame application, renderer, world-to-screen mapping, trajectory, rocket marker, and SI telemetry
- `python -m rocket_sim` entry point
- SPACE launch/pause/resume, R reset, and ESC exit controls
- independent analytical, convergence, lifecycle, FPS, rendering, and smoke tests
- persistent specialist definitions and repository review policy
- current implementation, physics, architecture, validation, milestone, and decision documentation

## Files created

- `.codex/agents/numerical_reviewer.toml`
- `.codex/agents/physics_reviewer.toml`
- `.codex/agents/test_reviewer.toml`
- `docs/decisions/decision_02_constant_thrust_state_model.md`
- `docs/decisions/decision_03_fixed_step_and_event_semantics.md`
- `docs/decisions/decision_04_specialist_review_workflow.md`
- `src/rocket_sim/__main__.py`
- `src/rocket_sim/app.py`
- `src/rocket_sim/config.py`
- `src/rocket_sim/physics.py`
- `src/rocket_sim/rendering.py`
- `src/rocket_sim/simulation.py`
- `tests/test_analytical_validation.py`
- `tests/test_config.py`
- `tests/test_convergence.py`
- `tests/test_forces.py`
- `tests/test_integrator.py`
- `tests/test_rendering.py`
- `tests/test_simulation.py`
- `tests/test_time_accumulator.py`

## Files modified

- `AGENTS.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/PHYSICS_MODEL.md`
- `docs/VALIDATION.md`
- `docs/product/PROJECT_UNDERSTANDING.md`
- `src/rocket_sim/__init__.py`

No repository file was deleted. Existing documentation files were rewritten in place to distinguish implemented Prompt 02 behavior from future scope.

## Post-implementation findings and resolution

The first post-implementation review found:

| Severity | Finding | Resolution |
| --- | --- | --- |
| BLOCKING | A coarse ground-start case could produce a non-positive first endpoint without ever setting liftoff, then continue below ground indefinitely. | Ground admission now requires non-negative initial vertical velocity and a positive first constant-force numerical endpoint. A defensive stepping guard also prevents negative-altitude history. Downward and under-resolved regression cases were added. |
| BLOCKING | The original absolute accumulator tolerance could promote subthreshold elapsed time to a full step and could loop pathologically for very small valid `dt`. | Removed the absolute comparison epsilon. Added compensated summation with strict `>= dt`, explicit compensation reset, and zero/small-`dt`/nextafter regressions. |
| IMPORTANT | A pre-burn landed state could report zero thrust while its instantaneous acceleration still contained thrust. | Terminal thrust now follows the same half-open time predicate as acceleration. A pre-burn impact consistency regression and documentation were added. |
| IMPORTANT | Landing interpolation velocity evidence used zero acceleration and could not distinguish interpolation from endpoint selection. | Added a nonzero-gravity crossing with independently derived impact time, position, and velocity. |
| IMPORTANT | Burnout evidence did not prove a unique boundary state and transition. | The crossing test now requires exactly one burnout sample and one POWERED-to-COAST transition, plus zero coast telemetry thrust. |
| IMPORTANT | Pre-launch time isolation and pause/resume were incompletely evidenced. | Added pre-launch clock, retained fractional accumulator, resume, and third-SPACE control assertions. |
| IMPORTANT | Interpolated landing had no timestep-convergence evidence. | Added an independent piecewise analytical ground-root calculation and first-order landing-time convergence at `dt=0.02, 0.01, 0.005 s`. |

After these fixes, all three specialists performed final resolution reviews and explicitly reported commit-ready status with no remaining BLOCKING or IMPORTANT finding.

## Deferred or rejected findings

No required finding was rejected or deferred.

Optional suggestions not included because they were unnecessary for Prompt 02's validated scope:

- an additional coast-energy regression;
- a dedicated non-binary-decimal burnout test beyond the existing analytical decimal-time path and deliberately non-grid-aligned crossing;
- lifecycle-wide FPS partition tests beyond the required 30/60/144 pre-burn comparison;
- broader full-flight regression metrics.

These may strengthen future regression coverage but are not substitutes for the independent analytical and convergence evidence already present, and adding them was not necessary to complete Prompt 02.

## Validation performed

Environment and infrastructure:

```text
conda run -n rocketsim python --version
Python 3.12.14

conda run -n rocketsim python -c "import sys; print(sys.executable)"
/Users/eugenelin/.conda/envs/rocketsim/bin/python

conda run -n rocketsim python -m pip --version
pip 26.2.1 from /Users/eugenelin/.conda/envs/rocketsim/lib/python3.12/site-packages/pip (python 3.12)

Python 3.12 tomllib validation
specialists: numerical_reviewer, physics_reviewer, test_reviewer
```

Build, import, and complete suite:

```text
conda run -n rocketsim python -m compileall -q src tests
passed

conda run -n rocketsim python -m pytest
70 passed in 0.24s

conda run -n rocketsim python -c "import pygame, pytest, rocket_sim; ..."
pygame 2.6.1
pytest 8.4.2
rocket_sim 0.1.0
```

Focused scientific evidence:

```text
conda run -n rocketsim python -m pytest -q   tests/test_analytical_validation.py   tests/test_convergence.py   tests/test_integrator.py
11 passed in 0.02s

conda run -n rocketsim python -m pytest -q   tests/test_simulation.py   tests/test_time_accumulator.py
16 passed in 0.01s
```

Application and rendering:

```text
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1   conda run -n rocketsim python -c   "from rocket_sim.app import run; raise SystemExit(run(max_frames=3))"
passed with normal exit

conda run -n rocketsim python -m rocket_sim
real application process launched and remained live until intentionally interrupted after the smoke observation
```

A representative Pygame coast frame at `t=1.5 s` was rendered and visually inspected. It showed the ground, vertical trajectory, rocket marker, COAST phase, `8.990 m` altitude, `5.285 m/s` vertical velocity, `-9.810 m/s²` vertical acceleration, `1.000 kg` mass, and `0.000 N` thrust, matching the corresponding numerical state.

Repository audit:

```text
git diff --check
passed

git diff --cached --check
passed
```

The staged audit confirmed exactly three read-only specialist definitions, no named model override, no future specialist roles, no generated environments/caches, no credentials, no out-of-scope physics implementation, independent analytical expected values, and documentation consistent with the code.

## Validation not performed

Computer Use could not attach to the live unbundled SDL/Python window and explicitly disallowed controlling Terminal, so live keyboard interaction was not automated through the macOS GUI. This limitation is not presented as a successful manual keyboard test. The real module process launch succeeded, the renderer output was visually inspected, the bounded dummy-display loop exited normally, and SPACE launch/pause/resume, R reset, ESC exit, and rendering non-mutation are directly covered by automated tests.

No formatter, linter, or type checker was run because none is configured and Prompt 02 prohibited adding dependencies solely for generic tooling.

No real-flight comparison was performed because the model is intentionally uncalibrated and Prompt 02 requires analytical validation, not engineering-grade validation.

## Exact execution authorization — verbatim

~~~~~~text
Please execute the revised Prompt 02 you just produced, exactly as written.
Follow it end-to-end, including the persistent specialist-agent setup and validation, pre-implementation reviews, parent-agent implementation, post-implementation reviews, resolution of blocking findings, full validation, documentation and decision updates, the implementation commit, separate Prompt 02 record commit, push to `origin/main`, and final verification.
Do not expand scope beyond Prompt 02 and do not begin Prompt 03.
~~~~~~

## Exact resume instruction — verbatim

~~~~~~text
Please resume and complete Prompt 02 from the exact current repository state.

The previous execution was interrupted only because the Codex/Work usage limit was reached after substantial work had already been completed. Do not restart Prompt 02, discard existing changes, or redo completed work unnecessarily.

First inspect the current repository and determine exactly which Prompt 02 phases were completed and which remain outstanding. Then continue from the first incomplete required step.

In particular, verify the status of:

- persistent specialist-agent creation and successful invocation
- pre-implementation specialist reviews
- implementation
- automated analytical and numerical validation
- Pygame/manual validation
- post-implementation reviews by all three specialists
- resolution of all BLOCKING findings
- documentation and decision records
- final diff audit
- implementation commit
- Prompt 02 record containing the implementation SHA and implementation diff
- separate prompt-record commit
- push of both commits to `origin/main`
- final clean Git/upstream verification

Preserve all valid work already completed. Do not expand scope beyond Prompt 02 and do not begin Prompt 03.

When complete, provide the full Prompt 02 completion report required by the revised Prompt 02.
~~~~~~

## Revised Prompt 02 — verbatim

~~~~~~text
# Prompt 02 — Implement and Independently Validate Initial 2D Rocket Flight

Work in:

```text
/Users/eugenelin/dev/cwsf2027/rocketsim
```

Canonical repository:

```text
https://github.com/eugenelin89/rocketsim.git
```

This is Prompt 02, the first scientific simulation implementation milestone for RocketSim.

Prompt 01 established the repository, Python 3.12 environment policy, Miniconda `rocketsim` environment, packaging and test baseline, project documentation, and Git/prompt-history workflow.

Prompt 02 has two related goals:

1. implement the first scientifically validated 2D rocket-flight model;
2. establish and use RocketSim’s initial persistent Codex specialist-review infrastructure.

The scientific scope remains strictly:

> Implement the first scientifically validated 2D constant-mass rocket model with gravity and finite-duration constant thrust.

The specialist infrastructure improves review and validation. It must not broaden the product or physics scope.

The parent Codex agent is the sole primary implementer and integrator. Specialist agents are independent read-only reviewers, not parallel code writers.

```text
requirements + authoritative docs
                ↓
     independent pre-review
      ┌────────┼────────┐
      ↓        ↓        ↓
   physics  numerical  tests
      └────────┼────────┘
               ↓
       reconciled contract
               ↓
      parent implementation
               ↓
     independent post-review
               ↓
       findings resolved
               ↓
   analytical + numerical validation
               ↓
       final audit / commit / push
```

## 1. Required reading and inspection

Before editing:

1. Read `AGENTS.md` completely.
2. Read `Pygame_Rocket_Simulator_Project_Context.md` completely.
3. Read `docs/product/PROJECT_UNDERSTANDING.md`.
4. Read:
   - `docs/PHYSICS_MODEL.md`
   - `docs/ARCHITECTURE.md`
   - `docs/MILESTONES.md`
   - `docs/VALIDATION.md`
   - `docs/PROJECT_BRIEF.md`
   - `docs/RESEARCH_LOG.md`
5. Read all relevant records under:
   - `docs/decisions/`
   - `docs/prompts/`
6. Inspect the actual repository tree.
7. Inspect:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 10
```

8. Confirm the worktree is clean.
9. Confirm `main` tracks `origin/main`.
10. Determine the next unused prompt and decision IDs.
11. Preserve unrelated user work.

If the working tree is unexpectedly dirty or repository state conflicts materially with this prompt, stop and report the precise conflict instead of absorbing or discarding it.

## 2. Python environment

Use the established primary-machine environment:

```text
Conda environment: rocketsim
Python: 3.12
```

Do not create another environment or a nested `venv`.

Do not use:

- Conda `base`
- Homebrew Python
- system Python
- user-global Python

Make interpreter provenance explicit:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -m pytest
```

Use dependencies already declared in `pyproject.toml`.

Do not add NumPy, SciPy, pandas, matplotlib, another GUI framework, or another dependency manager. Python’s standard library, Pygame, and pytest are sufficient.

## 3. Scientific and application scope

Implement only what is required for:

- 2D position and velocity
- constant rocket mass
- constant gravitational acceleration
- constant thrust magnitude during a finite burn
- fixed thrust direction
- powered-flight and coast phases
- burnout
- fixed-timestep numerical integration
- ground-return termination
- minimum runnable Pygame visualization
- trajectory display
- basic telemetry
- reset and rerun
- headless physics tests
- analytical validation
- timestep-convergence validation
- rendering-FPS independence

The result should be the first runnable RocketSim application while keeping the physics core independently testable without opening a Pygame window.

## 4. Explicitly out of scope

Do not implement or pre-create placeholders for:

- aerodynamic drag
- air density or atmosphere
- wind
- variable mass
- dry/propellant mass separation
- propellant consumption or mass flow
- realistic motor curves or motor-data files
- dynamic pressure or Mach number
- parachutes or recovery physics
- launch-rail dynamics
- rocket rotation or attitude
- angular velocity or torque
- moment of inertia
- angle of attack
- center of mass or center of pressure calculations
- aerodynamic stability
- active guidance or control
- thrust-vector or fin control
- sensor simulation or telemetry hardware
- CSV experiment export
- plotting libraries
- parameter sweeps
- Monte Carlo analysis
- optimization or machine learning
- multiple rockets or swarm behavior
- backend or cloud functionality

Do not create speculative subsystem directories for future milestones.

## 5. Establish persistent specialist agents

Before implementing the physics model, create:

```text
.codex/
└── agents/
    ├── physics_reviewer.toml
    ├── numerical_reviewer.toml
    └── test_reviewer.toml
```

Do not create:

- `architecture_reviewer`
- `aerodynamics_reviewer`
- `propulsion_reviewer`
- `flight_dynamics_reviewer`
- `experiment_reviewer`

Those roles should be introduced only when an active milestone needs them.

Use the current custom-agent schema documented by OpenAI. Each file must define:

- `name`
- `description`
- `developer_instructions`

Set:

```toml
sandbox_mode = "read-only"
model_reasoning_effort = "high"
```

Omit `model` so the specialist inherits the parent model.

### `physics_reviewer.toml`

Create a definition equivalent to:

```toml
name = "physics_reviewer"
description = "Independently reviews RocketSim equations, assumptions, units, coordinate conventions, forces, physical events, and analytical correctness."

sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
You are RocketSim's independent physics reviewer.

You are a reviewer, not an implementation agent. Do not modify repository
files.

Your primary question is:

Does the implementation actually represent the intended physical system?

Review:
- governing equations
- physical assumptions
- SI units and dimensional consistency
- coordinate and sign conventions
- vector directions
- gravity
- thrust magnitude and direction
- initial conditions
- powered-flight behavior
- finite-duration thrust semantics
- burnout
- coast behavior
- ground and event behavior
- analytical expectations
- limiting cases
- physically impossible states
- hidden assumptions

For the current milestone, independently verify the constant-mass,
constant-gravity, finite-duration constant-thrust 2D point-mass model.

Derive or independently verify analytical expectations rather than copying
expected values from implementation code.

Classify meaningful findings as:

BLOCKING
IMPORTANT
OPTIONAL

For each finding:
- explain the physical issue
- reference exact files, functions, equations, or tests
- state the expected behavior
- recommend the smallest scientifically defensible correction

Do not focus on Python style unless it obscures physical correctness.
"""
```

### `numerical_reviewer.toml`

Create a definition equivalent to:

```toml
name = "numerical_reviewer"
description = "Independently reviews RocketSim integration, timestep semantics, event timing, convergence, numerical error, and analytical agreement."

sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
You are RocketSim's independent numerical-methods reviewer.

You are a reviewer, not an implementation agent. Do not modify repository
files.

Assume physically correct equations may still be implemented numerically
incorrectly.

Your primary question is:

Does the numerical implementation faithfully approximate the equations it
claims to solve?

Review:
- integration algorithm
- position and velocity update ordering
- fixed-timestep semantics
- burnout and other event boundaries
- steps that cross a force discontinuity
- truncation error
- numerical drift
- convergence as dt decreases
- numerical stability
- accumulated error
- floating-point tolerances
- analytical-reference comparisons
- determinism and reproducibility

Where analytical solutions exist, independently compare numerical behavior
against them.

Report:
1. BLOCKING numerical errors
2. IMPORTANT validation weaknesses
3. recommended analytical or convergence tests
4. OPTIONAL improvements

Reference exact files, functions, equations, and tests.
"""
```

### `test_reviewer.toml`

Create a definition equivalent to:

```toml
name = "test_reviewer"
description = "Independently reviews RocketSim analytical validation, test coverage, limiting cases, edge cases, tolerances, and regression evidence."

sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
You are RocketSim's independent scientific validation and test reviewer.

You are a reviewer, not an implementation agent. Do not modify repository
files.

Do not judge success merely by whether pytest passes.

Your primary question is:

If this implementation were physically or numerically wrong, could the
current tests still pass?

Review:
- independent analytical references
- unit tests
- physical invariants
- limiting cases
- powered/coast transitions
- event boundaries
- invalid inputs and edge cases
- error tolerances
- timestep convergence
- rendering-FPS independence
- deterministic reset and rerun behavior
- regression evidence
- tests that reproduce implementation logic instead of validating it

For each important requirement report:

REQUIREMENT
CURRENT EVIDENCE
MISSING EVIDENCE
RECOMMENDED VALIDATION

Identify BLOCKING gaps separately and reference exact tests and source files.
"""
```

If the installed Codex release requires a slightly different valid syntax, consult the current official Codex subagent documentation and make only the smallest syntax correction. Do not omit any role silently.

## 6. Validate specialist infrastructure

Before relying on the specialists:

1. Parse all three TOML files with Python 3.12 `tomllib`.
2. Confirm the required keys are present.
3. Confirm each agent is read-only.
4. Ask Codex to invoke each custom agent by name.
5. Verify the agents return review output without modifying files.
6. Re-check `git status` after the invocation test.

Do not merely create the files and assume Codex loaded them.

If newly created project agents require a supported configuration or workspace reload, use the smallest safe reload mechanism and resume without changing repository state.

If the current task cannot hot-load valid new agent files:

- do not falsely claim persistent agents were invoked;
- retain the valid persistent files for future tasks;
- use three explicitly delegated read-only subagents with the same role instructions as the temporary Prompt 02 fallback;
- record the fallback accurately in the Prompt 02 history and completion report.

Persistent named agents are preferred when supported.

## 7. Update `AGENTS.md`

Add a concise section titled approximately:

```text
## RocketSim Specialist Review Policy
```

It should establish:

### `physics_reviewer`

Invoke for changes involving:

- forces or acceleration
- motion equations
- gravity or thrust
- mass
- trajectories
- physical constants
- physical events and phase transitions
- drag, atmosphere, wind, or propulsion when those later become active

### `numerical_reviewer`

Invoke for changes involving:

- numerical integration
- timestep handling
- interpolation
- event timing
- numerical solvers
- convergence
- floating-point tolerances

### `test_reviewer`

Invoke before completing any milestone that changes simulation behavior.

### Write authority

- Specialist reviewers are read-only unless a future approved prompt explicitly changes that rule.
- The parent Codex agent owns implementation, integration, and final decisions.
- Do not allow multiple agents to modify overlapping implementation files concurrently.

### Review workflow

The parent agent must:

1. collect relevant specialist findings;
2. reconcile disagreements;
3. decide which findings require action;
4. implement or correct the code itself;
5. obtain post-implementation review;
6. resolve blocking findings;
7. run required validation;
8. audit the final diff;
9. commit only after review and validation gates pass.

Keep detailed role knowledge in `.codex/agents/*.toml`.

Keep scientific truth in `docs/PHYSICS_MODEL.md` and validation methodology in `docs/VALIDATION.md`.

Do not duplicate large blocks of specialist instructions in `AGENTS.md`.

## 8. Independent pre-implementation review

Before writing simulation code, invoke all three specialists. They may run in parallel because they are read-only.

Give each reviewer this Prompt 02 scope and direct it to inspect:

- `docs/PHYSICS_MODEL.md`
- `docs/VALIDATION.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/product/PROJECT_UNDERSTANDING.md`
- existing tests
- existing package structure
- relevant decision records

Wait for all three before central implementation begins.

### Physics pre-review

Ask `physics_reviewer` to determine independently:

- governing equations
- force definitions
- units and dimensions
- coordinate and sign conventions
- gravity direction
- thrust-vector semantics
- fixed-angle semantics
- initial-state assumptions
- powered-flight and coast behavior
- exact burnout boundary
- ground-return semantics
- analytical gravity-only solution
- analytical powered-flight solution
- limiting cases
- assumptions that must be documented

### Numerical pre-review

Ask `numerical_reviewer` to determine independently:

- semi-implicit Euler update semantics
- expected accuracy and limitations
- appropriate fixed timestep
- position and velocity error behavior
- handling of a step that crosses burnout
- convergence expectations
- FPS-independence testing
- appropriate tolerances
- likely event-timing errors

### Test pre-review

Ask `test_reviewer` to propose independent evidence for:

- gravity-only analytical motion
- powered-flight analytical motion
- exact burnout semantics
- vertical and angled launches
- zero thrust
- zero gravity
- invalid configurations
- timestep convergence
- rendering-FPS independence
- deterministic reset and rerun
- ground-return termination

It must identify tests that would be circular because their expected values duplicate implementation logic.

## 9. Reconcile pre-review findings

The parent agent must summarize and reconcile the three reports before implementation.

For every disagreement:

1. identify the disagreement;
2. consult the authoritative project documentation;
3. independently derive or verify the relevant equation;
4. choose the scientifically justified interpretation;
5. document the decision when it materially constrains future work.

Do not silently choose one reviewer’s opinion.

If the authoritative documents are ambiguous, update them before or alongside implementation.

## 10. Minimum architecture

Use the smallest coherent architecture required by this milestone.

The dependency direction should remain:

```text
physics/model
      ↓
simulation state
      ↓
application/rendering
```

The physics core must:

- run without Pygame initialization;
- use SI units and world coordinates;
- contain no pixels, fonts, window dimensions, or screen coordinates;
- be deterministic for the same inputs;
- expose enough state for tests and rendering.

The Pygame layer owns:

- window creation
- input
- drawing
- world-to-screen conversion
- display timing
- trajectory visualization
- telemetry presentation

A compact structure such as:

```text
src/rocket_sim/
├── __init__.py
├── models.py
├── physics.py
├── simulation.py
├── rendering.py
├── app.py
└── __main__.py
```

may be appropriate, but inspect first and choose the smallest justified structure.

Do not mechanically create this exact layout if fewer modules are clearer. Do not create future subsystem directories.

The application should be runnable with:

```bash
conda run -n rocketsim python -m rocket_sim
```

## 11. Coordinate system and units

Use:

```text
world +x = right
world +y = up
ground = y = 0
gravity acts in -y
```

Use SI units internally:

```text
position       metres
time           seconds
velocity       metres per second
acceleration   metres per second squared
mass           kilograms
force          newtons
angle           radians internally
```

Degrees may be accepted at a configuration or display boundary only when explicitly converted.

Rendering performs the y-axis inversion:

```text
screen_y = ground_screen_y - world_y * pixels_per_metre
```

Never store pixels as physical position.

## 12. Physical model

Represent at least:

```text
time_s
position_m = (x, y)
velocity_m_s = (vx, vy)
constant mass_kg
```

Configuration should include explicit SI-valued fields for:

- initial position
- initial velocity
- mass
- thrust magnitude
- burn duration
- fixed thrust angle
- gravitational acceleration
- physics timestep

Validate invalid configurations rather than silently accepting physically or numerically nonsensical values. At minimum:

- mass must be positive;
- timestep must be positive;
- gravity magnitude must not be negative;
- thrust magnitude must not be negative;
- burn duration must not be negative;
- configured values must be finite.

### Gravity

```text
F_g = (0, -m g)
```

or equivalently:

```text
a_g = (0, -g)
```

### Thrust

For fixed angle `theta`:

```text
F_t = T (cos(theta), sin(theta))
```

Thrust is active exactly while:

```text
0 <= t < burn_time
```

At and after burnout:

```text
F_t = (0, 0)
```

The thrust direction remains fixed in world coordinates. Do not add orientation dynamics.

### Net acceleration

During powered flight:

```text
a_x = T cos(theta) / m
a_y = T sin(theta) / m - g
```

During coast:

```text
a_x = 0
a_y = -g
```

Do not add empirical tuning, velocity clamps, fake damping, or “game feel” adjustments.

## 13. Numerical integration and time semantics

Use a documented fixed physics timestep independent of rendering FPS.

Use semi-implicit Euler unless the reconciled pre-review establishes a compelling documented reason not to:

```text
v_(n+1) = v_n + a_n dt
x_(n+1) = x_n + v_(n+1) dt
```

Document:

- the selected default timestep;
- update ordering;
- expected first-order position error;
- why rendering FPS cannot affect the physics;
- the handling of force discontinuities and ground events.

A requested step that crosses burnout must not apply powered thrust to the entire step. Split the internal step at `burn_time` or use an equivalently exact and independently validated event-boundary treatment.

Simulation time must advance deterministically from physics steps, not directly from Pygame frame time.

The Pygame loop may use an accumulator:

```text
real elapsed time
      ↓
accumulator
      ↓
zero or more fixed physics steps
      ↓
render current state
```

Changing rendering FPS must not change the physical result for the same simulation configuration.

## 14. Flight phases and events

At minimum, expose unambiguous powered and coast behavior.

Burnout must occur once at the documented boundary.

Ground-return semantics must:

- avoid terminating immediately from the initial `y = 0` launch state;
- end the flight after the rocket has left the ground and later returns while descending;
- use `y = 0` as the ground;
- produce no bounce or impact dynamics;
- avoid arbitrary velocity clamps except any explicitly documented terminal-state handling.

No launch-rail or pad-support-force model should be introduced. Choose a default launch configuration with sufficient upward thrust for liftoff and document this simplification.

If ground crossing occurs between fixed steps, use a deterministic documented treatment and test it. Do not claim more event-time precision than the implementation provides.

## 15. Minimal Pygame application

Implement only enough visualization to inspect the model:

- window creation
- ground reference
- rocket marker or simple shape
- trajectory trace
- world-to-screen transform
- elapsed simulation time
- altitude
- horizontal and vertical velocity
- speed
- powered/coast/finished state
- reset and rerun
- quit control

Keep controls small and documented. Suggested controls:

```text
SPACE   launch or pause/resume
R       reset
ESC     quit
```

Do not build a settings GUI, asset pipeline, elaborate art, or speculative HUD system.

Rendering must not mutate physical state.

## 16. Analytical validation

Analytical expectations must be derived independently of the numerical implementation.

### Constant acceleration over an interval

For constant acceleration:

```text
x(t) = x0 + vx0 t + 0.5 ax t²
y(t) = y0 + vy0 t + 0.5 ay t²
vx(t) = vx0 + ax t
vy(t) = vy0 + ay t
```

During powered flight:

```text
ax = T cos(theta) / m
ay = T sin(theta) / m - g
```

During gravity-only coast:

```text
ax = 0
ay = -g
```

Use piecewise analytical expectations when validating a trajectory that spans burnout.

Compare numerical results against analytical results at known times. Do not generate expected values using the implementation under test.

Document expected semi-implicit Euler behavior: velocity is exact to floating-point precision for constant acceleration over aligned steps, while position has first-order global error.

## 17. Required automated tests

Create scientifically meaningful tests for at least:

1. package/import baseline;
2. configuration validation;
3. gravity direction and magnitude;
4. thrust-vector components at representative angles;
5. thrust active before burnout;
6. thrust zero exactly at and after burnout;
7. constant mass throughout the run;
8. semi-implicit Euler update ordering;
9. gravity-only analytical velocity and position;
10. powered-flight analytical velocity and position;
11. piecewise powered-to-coast analytical comparison;
12. a step crossing burnout;
13. vertical launch preserving near-zero horizontal motion;
14. zero-thrust limiting behavior;
15. zero-gravity powered behavior;
16. timestep convergence;
17. deterministic repeat/reset behavior;
18. ground-return termination;
19. physics independence from rendering configuration or FPS.

Choose tolerances based on analytical error expectations, timestep, and floating-point behavior. Do not use broad unexplained tolerances merely to make tests pass.

For convergence, show that reducing `dt` reduces position error at the expected order for semi-implicit Euler.

Tests must run headlessly without opening a Pygame window.

## 18. Documentation updates

Update documentation to describe what actually exists after Prompt 02.

At minimum review and update:

- `README.md`
- `docs/product/PROJECT_UNDERSTANDING.md`
- `docs/PHYSICS_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/VALIDATION.md`
- `docs/MILESTONES.md` where status clarification is useful
- `AGENTS.md`

Document:

- equations
- assumptions and exclusions
- SI units and coordinate convention
- fixed timestep
- integrator and update order
- burnout boundary
- ground-event semantics
- application entry point and controls
- implemented package structure
- headless testing
- analytical validation
- convergence evidence
- specialist-review workflow

Do not make `.codex/agents/*.toml` the sole source of scientific truth.

## 19. Decision records

Inspect existing decision IDs.

Create only meaningful durable decision records. Prompt 02 is expected to require documentation for choices such as:

- state representation and architecture boundary;
- fixed-timestep semi-implicit Euler integration;
- burnout and ground-event semantics;
- persistent read-only specialist-review workflow.

Prefer coherent records over one record per minor coding detail. Do not overwrite prior decisions; link or supersede them properly if needed.

Include decision records in the implementation commit.

## 20. Main-agent implementation

After reconciling the pre-review:

- the parent agent implements the model, tests, application, and documentation;
- do not delegate central implementation to multiple writers;
- do not let specialists edit files;
- keep changes strictly within Prompt 02;
- run focused tests throughout implementation.

## 21. Independent post-implementation review

After initial implementation and tests, invoke all three specialists again against the actual code and documentation.

### Physics post-review

Require a direct answer to:

> Does the implementation actually solve the intended constant-mass gravity-plus-finite-duration-thrust model?

It must inspect equations, signs, units, initial conditions, burnout, coast, ground behavior, analytical expectations, and limiting cases.

### Numerical post-review

Require a direct answer to:

> Does the numerical implementation faithfully approximate the documented equations?

It must inspect integration ordering, timestep treatment, burnout crossing, event timing, convergence, error accumulation, and tolerances.

### Test post-review

Require a direct answer to:

> Could a physically or numerically incorrect implementation still pass these tests?

It must inspect independence of expected values, limiting cases, transition coverage, convergence, FPS independence, determinism, and tolerances.

Wait for all three reports.

## 22. Resolve specialist findings

Collect findings in a concise reconciliation table or equivalent record.

For every `BLOCKING` finding:

1. investigate independently;
2. correct code, tests, or documentation;
3. rerun relevant validation;
4. obtain another review from the relevant specialist if the fix materially changes reviewed behavior.

Do not dismiss a blocking finding merely because pytest passes.

For rejected findings, record a concrete technical reason grounded in equations, documented requirements, or independent evidence.

Address `IMPORTANT` findings unless there is a clear documented reason to defer them.

Optional suggestions must not broaden Prompt 02.

## 23. Full validation

After review findings are resolved, run at minimum:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -m compileall -q src tests
conda run -n rocketsim python -m pytest
conda run -n rocketsim python -c "import rocket_sim"
git diff --check
```

Also run:

- analytical-reference tests;
- timestep-convergence tests;
- deterministic repeat tests;
- FPS-independence tests;
- an application launch smoke test using the `rocketsim` environment.

Run formatting, linting, or type checking only if those tools are already configured. Do not add dependencies solely to satisfy a generic tooling checklist.

Report exact commands and results.

## 24. Final diff and repository audit

Before committing:

1. inspect `git status`;
2. inspect the complete diff;
3. inspect staged files;
4. confirm no generated environments or caches are staged;
5. confirm no credentials or secrets are staged;
6. confirm `.codex/agents/` contains exactly the intended three reviewers;
7. confirm specialist agents are read-only;
8. confirm no future specialist roles were added;
9. confirm no out-of-scope physics exists;
10. confirm tests use independent analytical references;
11. confirm documentation matches implementation;
12. run `git diff --check`.

The worktree should contain only Prompt 02 implementation, validation, documentation, decisions, and intentional specialist infrastructure.

## 25. Implementation commit

Commit the complete Prompt 02 implementation—including the three persistent agent definitions, `AGENTS.md` policy, simulation code, tests, documentation, and relevant decision records—in one coherent implementation commit unless a concrete repository constraint requires otherwise.

Suggested message:

```text
Implement validated constant-thrust rocket flight
```

Do not include the final prompt record in this commit.

Record the implementation SHA and generate its parent diff.

## 26. Prompt archive

Create the next prompt record, expected to be approximately:

```text
docs/prompts/prompt_02_physics.md
```

Use the actual next unused ID.

The record must preserve this complete Prompt 02 verbatim and include:

- date and scope;
- starting repository state;
- requirements and constraints;
- persistent agents created;
- whether named persistent agents or temporary fallback agents were invoked;
- pre-review findings;
- reconciliation decisions;
- implementation summary;
- files created, modified, or deleted;
- equations and assumptions;
- numerical method;
- validation commands and results;
- post-review findings;
- fixes made because of review;
- unresolved or rejected findings with rationale;
- implementation commit SHA;
- implementation commit diff against its parent;
- target remote and push status at record creation.

Commit the prompt record separately.

Suggested message:

```text
Record prompt 02 physics implementation
```

Do not amend the implementation commit to insert the prompt record.

## 27. Push and final verification

Confirm:

```bash
git branch --show-current
git remote -v
git status
```

Then push without force:

```bash
git push origin main
```

Afterward verify:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 10
git ls-remote origin refs/heads/main
```

Confirm:

- branch is `main`;
- `main` tracks `origin/main`;
- local and remote SHAs agree;
- implementation commit exists;
- prompt-record commit follows it;
- both commits are pushed;
- the working tree is clean.

Do not claim push success unless Git confirms it.

## 28. Completion report

Provide a concise but complete report with separate sections for:

1. scientific model implemented;
2. governing equations and assumptions;
3. coordinate system and SI units;
4. numerical method and timestep;
5. burnout and ground-event semantics;
6. application entry point and controls;
7. analytical validation;
8. convergence and FPS-independence evidence;
9. complete test result;
10. persistent agent files created;
11. whether each named agent was successfully invoked;
12. pre-review findings from each specialist;
13. post-review findings from each specialist;
14. fixes made because of specialist review;
15. rejected or deferred findings and rationale;
16. documentation updated;
17. decision records created or updated;
18. validation not performed and why;
19. implementation commit SHA and message;
20. prompt-record path;
21. prompt-record commit SHA and message;
22. remote URL and branch;
23. push status;
24. final Git status;
25. limitations and explicit non-goals;
26. recommended exact scope for the next milestone.

Do not start the next milestone.

Do not claim scientific correctness solely because the animation looks plausible or pytest passes.

The required evidence chain is:

```text
governing equations
        ↓
independent analytical expectation
        ↓
numerical implementation
        ↓
specialist adversarial review
        ↓
timestep convergence
        ↓
regression evidence
        ↓
milestone completion
```
~~~~~~

## Implementation commit patch (exact zero-context diff against parent)

~~~~~~diff
commit 6ea447baa425216957a0b2bc552e8655cc663f8b
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Aug 27 21:48:11 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Aug 27 21:48:11 2026 -0700

    Implement validated constant-thrust rocket flight

diff --git a/.codex/agents/numerical_reviewer.toml b/.codex/agents/numerical_reviewer.toml
new file mode 100644
index 0000000..f6b3b3d
--- /dev/null
+++ b/.codex/agents/numerical_reviewer.toml
@@ -0,0 +1,46 @@
+name = "numerical_reviewer"
+description = "Independently reviews RocketSim integration, timestep semantics, event timing, convergence, numerical error, and analytical agreement."
+
+sandbox_mode = "read-only"
+model_reasoning_effort = "high"
+
+developer_instructions = """
+You are RocketSim's independent numerical-methods reviewer.
+
+You are a reviewer, not an implementation agent. Do not modify repository
+files.
+
+Assume physically correct equations may still be implemented numerically
+incorrectly.
+
+Your primary question is:
+
+Does the numerical implementation faithfully approximate the equations it
+claims to solve?
+
+Review:
+- integration algorithm
+- position and velocity update ordering
+- fixed-timestep semantics
+- burnout and other event boundaries
+- steps that cross a force discontinuity
+- truncation error
+- numerical drift
+- convergence as dt decreases
+- numerical stability
+- accumulated error
+- floating-point tolerances
+- analytical-reference comparisons
+- determinism and reproducibility
+
+Where analytical solutions exist, independently compare numerical behavior
+against them.
+
+Report:
+1. BLOCKING numerical errors
+2. IMPORTANT validation weaknesses
+3. recommended analytical or convergence tests
+4. OPTIONAL improvements
+
+Reference exact files, functions, equations, and tests.
+"""
diff --git a/.codex/agents/physics_reviewer.toml b/.codex/agents/physics_reviewer.toml
new file mode 100644
index 0000000..54f2a9d
--- /dev/null
+++ b/.codex/agents/physics_reviewer.toml
@@ -0,0 +1,55 @@
+name = "physics_reviewer"
+description = "Independently reviews RocketSim equations, assumptions, units, coordinate conventions, forces, physical events, and analytical correctness."
+
+sandbox_mode = "read-only"
+model_reasoning_effort = "high"
+
+developer_instructions = """
+You are RocketSim's independent physics reviewer.
+
+You are a reviewer, not an implementation agent. Do not modify repository
+files.
+
+Your primary question is:
+
+Does the implementation actually represent the intended physical system?
+
+Review:
+- governing equations
+- physical assumptions
+- SI units and dimensional consistency
+- coordinate and sign conventions
+- vector directions
+- gravity
+- thrust magnitude and direction
+- initial conditions
+- powered-flight behavior
+- finite-duration thrust semantics
+- burnout
+- coast behavior
+- ground and event behavior
+- analytical expectations
+- limiting cases
+- physically impossible states
+- hidden assumptions
+
+For the current milestone, independently verify the constant-mass,
+constant-gravity, finite-duration constant-thrust 2D point-mass model.
+
+Derive or independently verify analytical expectations rather than copying
+expected values from implementation code.
+
+Classify meaningful findings as:
+
+BLOCKING
+IMPORTANT
+OPTIONAL
+
+For each finding:
+- explain the physical issue
+- reference exact files, functions, equations, or tests
+- state the expected behavior
+- recommend the smallest scientifically defensible correction
+
+Do not focus on Python style unless it obscures physical correctness.
+"""
diff --git a/.codex/agents/test_reviewer.toml b/.codex/agents/test_reviewer.toml
new file mode 100644
index 0000000..35ba333
--- /dev/null
+++ b/.codex/agents/test_reviewer.toml
@@ -0,0 +1,43 @@
+name = "test_reviewer"
+description = "Independently reviews RocketSim analytical validation, test coverage, limiting cases, edge cases, tolerances, and regression evidence."
+
+sandbox_mode = "read-only"
+model_reasoning_effort = "high"
+
+developer_instructions = """
+You are RocketSim's independent scientific validation and test reviewer.
+
+You are a reviewer, not an implementation agent. Do not modify repository
+files.
+
+Do not judge success merely by whether pytest passes.
+
+Your primary question is:
+
+If this implementation were physically or numerically wrong, could the
+current tests still pass?
+
+Review:
+- independent analytical references
+- unit tests
+- physical invariants
+- limiting cases
+- powered/coast transitions
+- event boundaries
+- invalid inputs and edge cases
+- error tolerances
+- timestep convergence
+- rendering-FPS independence
+- deterministic reset and rerun behavior
+- regression evidence
+- tests that reproduce implementation logic instead of validating it
+
+For each important requirement report:
+
+REQUIREMENT
+CURRENT EVIDENCE
+MISSING EVIDENCE
+RECOMMENDED VALIDATION
+
+Identify BLOCKING gaps separately and reference exact tests and source files.
+"""
diff --git a/AGENTS.md b/AGENTS.md
index 36be41b..e4f1349 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -23,0 +24,36 @@ These instructions apply to the entire repository.
+## RocketSim Specialist Review Policy
+
+RocketSim uses project-scoped Codex specialist agents for independent scientific review.
+
+### `physics_reviewer`
+
+Invoke for changes involving forces, acceleration, motion equations, gravity, thrust, mass, trajectories, physical constants, or physical events and phase transitions. Invoke it for drag, atmosphere, wind, or propulsion when those domains become active in later milestones.
+
+### `numerical_reviewer`
+
+Invoke for changes involving numerical integration, timestep handling, interpolation, event timing, numerical solvers, convergence, or floating-point tolerances.
+
+### `test_reviewer`
+
+Invoke before completing any milestone that changes simulation behavior.
+
+### Write Authority
+
+Specialist reviewers are read-only unless a future approved prompt explicitly changes that rule. The parent Codex agent owns implementation, integration, and final decisions. Do not allow multiple agents to modify overlapping implementation files concurrently.
+
+### Review Workflow
+
+Relevant specialists may investigate independently and in parallel. The parent agent must:
+
+1. collect relevant specialist findings
+2. reconcile disagreements
+3. decide which findings require action
+4. implement or correct the code itself
+5. obtain post-implementation review
+6. resolve blocking findings
+7. run required validation
+8. audit the final diff
+9. commit only after review and validation gates pass
+
+Keep detailed reviewer behavior in `.codex/agents/*.toml`. Keep scientific truth in `docs/PHYSICS_MODEL.md` and validation methodology in `docs/VALIDATION.md`.
+
diff --git a/README.md b/README.md
index 017d417..a4135a0 100644
--- a/README.md
+++ b/README.md
@@ -3 +3 @@
-A staged 2D model-rocket flight simulator built with Python and Pygame. The project emphasizes explicit assumptions, reproducible runs, analytical validation, and a clean boundary between physics and visualization.
+RocketSim is a scientifically inspectable 2D model-rocket flight simulator built with Python and Pygame. Its first flight milestone implements a constant-mass point rocket under constant gravity and finite-duration constant thrust, with a fixed physics timestep that is independent of display FPS.
@@ -7 +7 @@ A staged 2D model-rocket flight simulator built with Python and Pygame. The proj
-Prompt 01 establishes the Milestone 0 repository and tooling baseline. The `rocket_sim` package is installable and tested, but no Pygame application loop or rocket-flight physics is implemented yet.
+Milestone 1 is implemented. The runnable application displays the flight trajectory and live telemetry while a Pygame-independent physics core owns forces, integration, event transitions, and history.
@@ -9 +9 @@ Prompt 01 establishes the Milestone 0 repository and tooling baseline. The `rock
-The next milestone will add 2D constant-mass flight with gravity and finite-duration constant thrust. Drag, variable mass, wind, atmosphere, recovery, rotation, stability, guidance, and control remain out of scope until later milestones.
+Implemented physics:
@@ -11 +11,6 @@ The next milestone will add 2D constant-mass flight with gravity and finite-dura
-## Development setup
+- SI units and world coordinates with +x right and +y up
+- constant mass and constant gravity
+- constant thrust at a fixed world angle for `0 <= t < burn_time`
+- fixed `0.01 s` physics timestep and semi-implicit Euler integration
+- exact substep split when a fixed step crosses burnout
+- deterministic ground-return termination after liftoff
@@ -13 +18,5 @@ The next milestone will add 2D constant-mass flight with gravity and finite-dura
-Python 3.12 and an isolated environment are required. On the primary Miniconda-based development machine, create and use the dedicated `rocketsim` environment:
+Drag, variable mass, sampled thrust curves, wind, atmosphere, recovery, rotation, stability, guidance, and control are not implemented.
+
+## Setup and validation
+
+Python 3.12 and an isolated environment are required. On the primary development machine:
@@ -17,6 +26,2 @@ conda create -n rocketsim python=3.12 pip
-conda activate rocketsim
-python --version
-python -m pip --version
-python -m pip install --upgrade pip
-python -m pip install -e ".[dev]"
-python -m pytest
+conda run -n rocketsim python -m pip install -e ".[dev]"
+conda run -n rocketsim python -m pytest
@@ -25 +30,3 @@ python -m pytest
-For automated work on that machine, make the interpreter explicit without relying on shell activation:
+`pyproject.toml` is the canonical package and dependency declaration. Do not install the project into Conda `base`, a system interpreter, or a nested virtual environment.
+
+## Run the simulator
@@ -28 +35 @@ For automated work on that machine, make the interpreter explicit without relyin
-conda run -n rocketsim python -m pytest
+conda run -n rocketsim python -m rocket_sim
@@ -31 +38 @@ conda run -n rocketsim python -m pytest
-Conda supplies isolation, Python, and pip; `pyproject.toml` remains the canonical project and dependency declaration. Use `python -m pip` so pip belongs to the selected interpreter. Do not use Conda `base` for project dependencies, and do not create a nested `venv` inside the `rocketsim` environment.
+Controls:
@@ -33 +40,5 @@ Conda supplies isolation, Python, and pip; `pyproject.toml` remains the canonica
-On other machines, a conventional isolated Python 3.12 environment, including standard-library `venv`, is acceptable when it works normally. Install the same project and development dependencies from `pyproject.toml` with `python -m pip install -e ".[dev]"`.
+- `SPACE`: launch, pause, or resume
+- `R`: reset the complete deterministic run
+- `ESC`: exit
+
+Telemetry shows phase, simulation time, position, velocity, speed, acceleration, mass, and current thrust. The default vertical configuration uses a `1 kg` rocket, `20 N` thrust, a `1 s` burn, and `9.81 m/s²` gravity, so thrust exceeds weight during launch.
@@ -38,5 +49,6 @@ On other machines, a conventional isolated Python 3.12 environment, including st
-src/rocket_sim/     importable application package
-tests/              pytest test suite
-docs/product/       current implementation understanding
-docs/prompts/       prompt and implementation history
-docs/decisions/     durable project decisions
+.codex/agents/         persistent read-only specialist reviewer definitions
+src/rocket_sim/        configuration, physics, lifecycle, rendering, and app code
+tests/                 headless physics, numerical, lifecycle, and rendering tests
+docs/product/          current implementation understanding
+docs/prompts/          prompt and implementation history
+docs/decisions/        durable scientific and workflow decisions
@@ -45,15 +57 @@ docs/decisions/     durable project decisions
-Subsystem directories will be introduced only when a concrete implementation milestone needs them.
-
-## Documentation
-
-- [`Pygame_Rocket_Simulator_Project_Context.md`](Pygame_Rocket_Simulator_Project_Context.md) — canonical product, scientific, and milestone context
-- [`docs/product/PROJECT_UNDERSTANDING.md`](docs/product/PROJECT_UNDERSTANDING.md) — current implementation-oriented status
-- [`docs/PHYSICS_MODEL.md`](docs/PHYSICS_MODEL.md) — planned model assumptions and equations
-- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture direction
-- [`docs/VALIDATION.md`](docs/VALIDATION.md) — validation strategy
-- [`docs/MILESTONES.md`](docs/MILESTONES.md) — staged development plan
-- [`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md) — research questions and experiment log
-
-## Definition of success
-
-The simulator should become a trustworthy experimental sandbox rather than merely a plausible animation. Results must remain understandable, testable, and traceable to their equations, units, numerical method, and configuration.
+See [docs/PHYSICS_MODEL.md](docs/PHYSICS_MODEL.md) for the exact equations and limits, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for ownership boundaries, and [docs/VALIDATION.md](docs/VALIDATION.md) for the evidence strategy.
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 451cf9a..93b4be8 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -3 +3 @@
-## Objective
+## Implemented boundary
@@ -5,54 +5 @@
-The simulator should be designed so that the physics can run independently of Pygame. Pygame should be a visualization and input layer, not the physics engine itself.
-
-This separation will make it easier to:
-
-- test the physics,
-- run simulations faster than real time,
-- run parameter sweeps,
-- compare models,
-- add alternative visualizations later,
-- and potentially reuse the simulator for autonomous-control experiments.
-
----
-
-## Proposed Components
-
-### `main.py`
-
-Responsibilities:
-
-- Initialize Pygame.
-- Create the simulation.
-- Run the application loop.
-- Handle top-level user input.
-- Coordinate physics updates and rendering.
-
-It should contain as little physics logic as possible.
-
-### `simulation.py`
-
-Responsibilities:
-
-- Own simulation time.
-- Advance the simulation by a timestep.
-- Coordinate forces and environment.
-- Determine when a flight starts and ends.
-- Record trajectory/history data.
-
-Possible interface:
-
-```python
-simulation.step(dt)
-simulation.reset()
-simulation.is_finished
-```
-
-### `rocket.py`
-
-Responsibilities:
-
-- Store rocket physical properties.
-- Store current rocket state.
-- Update state from calculated forces.
-
-Possible properties:
+The simulator separates scientific state evolution from Pygame presentation:
@@ -61,6 +8,16 @@ Possible properties:
-position
-velocity
-mass
-dry_mass
-reference_area
-drag_coefficient
+Pygame events + frame time
+            |
+            v
+app.py -> Simulation.advance_elapsed()
+            |
+            v
+fixed-step accumulator -> simulation.py lifecycle/events
+            |
+            v
+physics.py forces + semi-implicit Euler
+            |
+            v
+immutable RocketState history
+            |
+            v
+rendering.py world transform + drawing + telemetry
@@ -69,43 +26 @@ drag_coefficient
-Later:
-
-```text
-angle
-angular_velocity
-moment_of_inertia
-center_of_mass
-center_of_pressure
-```
-
-### `motor.py`
-
-Responsibilities:
-
-- Motor burn duration.
-- Thrust as a function of time.
-- Propellant mass.
-- Mass flow.
-
-Possible interface:
-
-```python
-motor.thrust_at(t)
-motor.propellant_mass_at(t)
-motor.is_burning(t)
-```
-
-### `environment.py`
-
-Responsibilities:
-
-- Gravity.
-- Air density.
-- Wind.
-- Atmospheric properties.
-
-Possible interface:
-
-```python
-environment.gravity_at(position)
-environment.air_density_at(altitude)
-environment.wind_at(altitude, time)
-```
+`config.py`, `physics.py`, and `simulation.py` do not import Pygame. `app.py` owns window creation, input, the display clock, and the outer loop. `rendering.py` owns pixels, fonts, drawing, and the +y-up to +y-down transform.
@@ -113,12 +28 @@ environment.wind_at(altitude, time)
-### `renderer.py`
-
-Responsibilities:
-
-- Convert world coordinates to screen coordinates.
-- Draw rocket.
-- Draw trajectory.
-- Draw ground.
-- Draw telemetry.
-- Draw force vectors when enabled.
-
-The renderer must not modify physical state.
+## Module responsibilities
@@ -128,18 +32,3 @@ The renderer must not modify physical state.
-Responsibilities:
-
-- Store initial simulation parameters.
-- Keep tuning values out of physics code.
-
-Example configuration:
-
-```python
-ROCKET_MASS_KG = 1.5
-THRUST_N = 35.0
-BURN_TIME_S = 1.0
-LAUNCH_ANGLE_DEG = 85.0
-PHYSICS_DT = 0.01
-```
-
-Eventually, replace or supplement this with JSON/TOML experiment configuration files.
-
----
+- immutable, validated `SimulationConfig`
+- neutral immutable `Vector2`
+- SI-valued defaults and initial conditions
@@ -147,19 +36 @@ Eventually, replace or supplement this with JSON/TOML experiment configuration f
-## Main Loop
-
-Conceptually:
-
-```text
-initialize
-
-while running:
-    process user input
-
-    accumulate real elapsed time
-
-    while accumulated_time >= physics_dt:
-        simulation.step(physics_dt)
-        accumulated_time -= physics_dt
-
-    renderer.draw(simulation)
-    display frame
-```
+### `physics.py`
@@ -167 +38,4 @@ while running:
-This fixed-timestep structure prevents simulation results from changing significantly when graphical frame rate changes.
+- gravitational and thrust force equations
+- half-open burn predicate
+- net acceleration
+- one constant-acceleration semi-implicit Euler segment
@@ -169 +43 @@ This fixed-timestep structure prevents simulation results from changing signific
----
+It does not own wall time, phases, events, or drawing.
@@ -171,41 +45 @@ This fixed-timestep structure prevents simulation results from changing signific
-## Data Flow
-
-```text
-User Input
-    ↓
-Configuration
-    ↓
-Simulation
-    ↓
-Rocket + Motor + Environment
-    ↓
-Force Calculation
-    ↓
-Numerical Integration
-    ↓
-Updated Rocket State
-    ↓
-Renderer
-    ↓
-Pygame Display
-```
-
-Trajectory data should also be stored separately for later plotting and analysis.
-
----
-
-## Design Rules
-
-### Rule 1: SI units internally
-
-Never mix screen pixels with metres.
-
-### Rule 2: Renderer does not own physics
-
-Changing zoom or window size must not change simulation results.
-
-### Rule 3: Fixed physics timestep
-
-Physics should not depend directly on FPS.
-
-### Rule 4: One source of truth for state
+### `simulation.py`
@@ -213 +47,5 @@ Physics should not depend directly on FPS.
-Rocket position and velocity should be stored in one location only.
+- immutable `RocketState` samples and flight phases
+- launch, pause/resume, reset, and terminal lifecycle
+- fixed-timestep wall-time accumulator
+- exact burnout split and deterministic ground-crossing handling
+- physics step count and trajectory history
@@ -215 +53 @@ Rocket position and velocity should be stored in one location only.
-### Rule 5: Keep models replaceable
+Configuration is the source of constant mass. Every recorded state repeats that value so the invariant is observable.
@@ -217 +55 @@ Rocket position and velocity should be stored in one location only.
-For example, `ConstantThrustMotor` should later be replaceable by `ThrustCurveMotor` without rewriting the simulation.
+### `rendering.py`
@@ -219 +57,3 @@ For example, `ConstantThrustMotor` should later be replaceable by `ThrustCurveMo
-### Rule 6: Record experiment parameters
+- world metres to screen pixels
+- ground, trajectory, rocket, and telemetry drawing
+- no mutation of simulation state
@@ -221 +61 @@ For example, `ConstantThrustMotor` should later be replaceable by `ThrustCurveMo
-A result is not scientifically useful if the simulator cannot reproduce the run.
+### `app.py` and `__main__.py`
@@ -223 +63,4 @@ A result is not scientifically useful if the simulator cannot reproduce the run.
----
+- `python -m rocket_sim` entry point
+- Pygame initialization and shutdown
+- `SPACE`, `R`, and `ESC` controls
+- bounded `run(max_frames=...)` path for dummy-display smoke validation
@@ -225 +68 @@ A result is not scientifically useful if the simulator cannot reproduce the run.
-## Suggested First Classes
+## Clock contract
@@ -227,8 +70 @@ A result is not scientifically useful if the simulator cannot reproduce the run.
-```text
-Vector2 / pygame.math.Vector2
-Rocket
-Motor
-Environment
-Simulation
-Renderer
-```
+Elapsed unpaused display time is accumulated with compensated floating-point summation. The simulation consumes complete fixed `physics_dt_s` intervals and retains only a fractional remainder. It never advances a representably subthreshold interval and has no substep cap that drops elapsed time. Pre-launch, paused, and post-landing calls do not add elapsed time; reset clears the remainder, compensation, and step counter.
@@ -236 +72 @@ Renderer
-Using `pygame.math.Vector2` is acceptable for vector arithmetic in the first version.
+No absolute comparison tolerance creates simulation time. Burnout is handled by explicit segment endpoints, not an epsilon-expanded burn interval.
@@ -238 +74 @@ Using `pygame.math.Vector2` is acceptable for vector arithmetic in the first ver
----
+## State and event contract
@@ -240 +76 @@ Using `pygame.math.Vector2` is acceptable for vector arithmetic in the first ver
-## Future Architecture Possibilities
+The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. State acceleration describes the instantaneous force model at the state's resulting time, so a state exactly at burnout is coast even if the preceding interval was powered.
@@ -242 +78 @@ Using `pygame.math.Vector2` is acceptable for vector arithmetic in the first ver
-Later, the simulator may benefit from:
+Burnout and landing are handled inside the simulation boundary. A terminal state is the instant of impact, so pre-burn impact retains time-consistent thrust and acceleration telemetry. Rendering infers no transitions and performs no force calculations.
@@ -244,10 +80 @@ Later, the simulator may benefit from:
-- an `Experiment` class,
-- batch simulation mode,
-- CSV export,
-- plotting with Matplotlib,
-- Monte Carlo runs,
-- sensor simulation,
-- autopilot/controller modules,
-- multiple vehicles,
-- reinforcement learning environments,
-- and a headless mode without Pygame.
+## Extension limits
@@ -255 +82 @@ Later, the simulator may benefit from:
-These should remain future extensions rather than requirements for the first implementation.
+Prompt 02 deliberately does not introduce motor interfaces, atmosphere interfaces, data loaders, experiment frameworks, plugins, databases, ECS, networking, or abstractions for unimplemented milestones. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
diff --git a/docs/MILESTONES.md b/docs/MILESTONES.md
index 7615ec8..edc8c79 100644
--- a/docs/MILESTONES.md
+++ b/docs/MILESTONES.md
@@ -5 +5 @@
-Build the simulator in small, testable stages. Each milestone should introduce one major source of physical complexity while keeping previous behavior working.
+Add one major physical effect at a time, preserve validated earlier behavior, and keep display concerns outside the physics core.
@@ -7 +7 @@ Build the simulator in small, testable stages. Each milestone should introduce o
----
+## Milestone 0 — Repository and application foundation
@@ -9 +9 @@ Build the simulator in small, testable stages. Each milestone should introduce o
-## Milestone 0 — Project Skeleton
+Status: complete.
@@ -11 +11,5 @@ Build the simulator in small, testable stages. Each milestone should introduce o
-### Goal
+- installable Python 3.12 package
+- isolated Conda development workflow
+- Pygame runtime and pytest development dependencies
+- documentation, prompt archive, decisions, and repository policy
+- runnable module entry point and separated simulation/rendering modules
@@ -13 +17 @@ Build the simulator in small, testable stages. Each milestone should introduce o
-Create a runnable Pygame application with a clean project structure.
+The application portion was completed alongside Milestone 1 so it could display real, tested state rather than placeholder physics.
@@ -15 +19 @@ Create a runnable Pygame application with a clean project structure.
-### Deliverables
+## Milestone 1 — Powered point-mass flight
@@ -17,5 +21 @@ Create a runnable Pygame application with a clean project structure.
-- Pygame window opens.
-- Main loop runs.
-- Simulation and renderer are separate modules.
-- Basic configuration file exists.
-- Test directory exists.
+Status: complete in Prompt 02.
@@ -23 +23 @@ Create a runnable Pygame application with a clean project structure.
-### Completion Check
+Physics:
@@ -25 +25,5 @@ Create a runnable Pygame application with a clean project structure.
-The project launches without errors and can display a static rocket on a ground line.
+- constant gravity
+- constant mass
+- constant thrust on a finite half-open burn interval
+- fixed launch angle in world coordinates
+- no drag
@@ -27 +31 @@ The project launches without errors and can display a static rocket on a ground
----
+Features:
@@ -29 +33,5 @@ The project launches without errors and can display a static rocket on a ground
-## Milestone 1 — Powered Point-Mass Flight
+- launch, pause/resume, reset, and exit controls
+- trajectory and SI telemetry
+- powered-to-coast transition
+- post-liftoff ground return and terminal landing
+- fixed timestep independent of rendering FPS
@@ -31 +39 @@ The project launches without errors and can display a static rocket on a ground
-### Physics
+Validation:
@@ -33,5 +41,6 @@ The project launches without errors and can display a static rocket on a ground
-- Constant gravity.
-- Constant mass.
-- Constant thrust during a fixed burn interval.
-- No drag.
-- Fixed launch angle.
+- independent gravity, powered, and piecewise analytical cases
+- Euler ordering and known position-error checks
+- non-aligned burnout split
+- first-order timestep convergence
+- reset determinism and 30/60/144 FPS partition independence
+- bounded headless application smoke
@@ -39 +48 @@ The project launches without errors and can display a static rocket on a ground
-### Features
+## Milestone 2 — Aerodynamic drag
@@ -41,6 +50 @@ The project launches without errors and can display a static rocket on a ground
-- Launch/reset controls.
-- Rocket trajectory.
-- Elapsed time.
-- Position and velocity display.
-- Automatic transition from powered flight to coast.
-- Flight ends when rocket returns to ground.
+Status: not started. It is outside Prompt 02.
@@ -48 +52 @@ The project launches without errors and can display a static rocket on a ground
-### Validation
+When separately approved, this milestone may add quadratic drag with explicit density, drag coefficient, reference area, and air-relative velocity. It will require direction, zero-speed, `v²` scaling, analytical/limiting-case, and timestep-sensitivity evidence. No drag placeholder exists in the current implementation.
@@ -50 +54 @@ The project launches without errors and can display a static rocket on a ground
-Compare no-thrust ballistic motion with analytical projectile equations.
+## Later candidate milestones
@@ -52 +56 @@ Compare no-thrust ballistic motion with analytical projectile equations.
-### Completion Check
+The following remain unimplemented and require separate approval and validation:
@@ -54 +58,7 @@ Compare no-thrust ballistic motion with analytical projectile equations.
-Simulation results are stable and approximately independent of graphical FPS.
+1. variable mass and propellant depletion
+2. sampled real-motor thrust curves and total impulse
+3. atmospheric density and speed of sound
+4. wind and recovery
+5. rotational dynamics and aerodynamic stability
+6. headless experiment export and reproducibility tooling
+7. calibrated real-flight comparison and uncertainty analysis
@@ -56,190 +66 @@ Simulation results are stable and approximately independent of graphical FPS.
----
-
-## Milestone 2 — Aerodynamic Drag
-
-### Physics
-
-Add:
-
-```text
-F_drag = 0.5 rho C_d A v²
-```
-
-### Features
-
-- Configurable drag coefficient.
-- Configurable reference area.
-- Optional drag force vector display.
-
-### Validation
-
-Confirm that:
-
-- drag always opposes velocity,
-- drag is zero when velocity is zero,
-- drag scales approximately with `v²`,
-- altitude is lower with drag enabled than without drag.
-
----
-
-## Milestone 3 — Variable Mass and Motor Model
-
-### Physics
-
-- Dry mass.
-- Propellant mass.
-- Propellant depletion.
-- Changing total mass.
-
-### Features
-
-- Remaining propellant display.
-- Motor state: idle / burning / burned out.
-
-### Validation
-
-Confirm total rocket mass never drops below dry mass.
-
----
-
-## Milestone 4 — Real Thrust Curves
-
-### Goal
-
-Load sampled motor thrust data from a file.
-
-### Features
-
-- CSV motor data.
-- Linear interpolation.
-- Total impulse calculation.
-- Motor curve visualization or debug plot.
-
-### Validation
-
-Numerically integrate thrust curve and compare with expected total impulse.
-
----
-
-## Milestone 5 — Atmosphere and Mach Number
-
-### Physics
-
-- Density decreases with altitude.
-- Speed of sound estimate.
-- Mach number calculation.
-
-### Features
-
-- Display Mach number.
-- Display maximum Mach reached.
-
-### Validation
-
-Compare atmospheric values with a trusted reference at several altitudes.
-
----
-
-## Milestone 6 — Wind and Recovery
-
-### Physics
-
-- Horizontal wind.
-- Relative air velocity.
-- Parachute drag.
-
-### Features
-
-- Parachute deployment altitude/time condition.
-- Landing location.
-- Drift distance.
-
-### Validation
-
-Confirm stronger wind produces larger horizontal drift during descent.
-
----
-
-## Milestone 7 — Rotational Dynamics
-
-### Physics
-
-Introduce:
-
-- rocket orientation,
-- angular velocity,
-- torque,
-- moment of inertia,
-- angle of attack.
-
-### Features
-
-- Rocket sprite rotates physically.
-- Attitude data display.
-
-### Validation
-
-Start with simple torque-only test cases before aerodynamic stability.
-
----
-
-## Milestone 8 — Aerodynamic Stability
-
-### Physics
-
-- Center of gravity.
-- Center of pressure.
-- Restoring aerodynamic moment.
-- Approximate stability margin.
-
-### Features
-
-- Display CG and CP.
-- Show whether configuration is nominally stable.
-
-### Validation
-
-A statically stable rocket should tend to align with its relative airflow after small disturbances.
-
----
-
-## Milestone 9 — Experiment Mode
-
-### Features
-
-- Run without real-time graphics.
-- Sweep launch parameters.
-- Export CSV results.
-- Compare apogee, maximum velocity, range, and flight time.
-- Reproduce runs from saved configuration.
-
-### Example Experiment
-
-Vary launch angle from 70° to 90° and measure:
-
-```text
-apogee
-horizontal drift
-maximum speed
-flight duration
-```
-
----
-
-## Milestone 10 — Advanced Research Extensions
-
-Possible directions:
-
-- Active thrust-vector control.
-- Fin control.
-- Sensor simulation.
-- State estimation.
-- Kalman filtering.
-- Autonomous apogee detection.
-- Optimal control.
-- Monte Carlo uncertainty analysis.
-- Multi-rocket simulations.
-- Swarm behavior.
-- Reinforcement learning controllers.
-
-These are deliberately outside the initial scope.
+Advanced guidance, control, optimization, machine learning, and multi-vehicle work are research directions only. They must not be inferred from the current 2D point-mass model.
diff --git a/docs/PHYSICS_MODEL.md b/docs/PHYSICS_MODEL.md
index ae4ec56..9f0a207 100644
--- a/docs/PHYSICS_MODEL.md
+++ b/docs/PHYSICS_MODEL.md
@@ -3 +3 @@
-## Purpose
+## Implemented Milestone 1 model
@@ -5 +5 @@
-This document defines the physical assumptions, equations, variables, and staged fidelity of the rocket simulator.
+RocketSim currently models one constant-mass point rocket in a two-dimensional flat world. It uses SI units internally:
@@ -7 +7,7 @@ This document defines the physical assumptions, equations, variables, and staged
-The simulator should use SI units internally:
+- position: metres (m)
+- time: seconds (s)
+- velocity: metres per second (m/s)
+- acceleration: metres per second squared (m/s²)
+- mass: kilograms (kg)
+- force: newtons (N)
+- angle: radians
@@ -9,7 +15 @@ The simulator should use SI units internally:
-- Position: metres (m)
-- Time: seconds (s)
-- Velocity: metres per second (m/s)
-- Acceleration: metres per second squared (m/s²)
-- Mass: kilograms (kg)
-- Force: newtons (N)
-- Angle: radians internally
+World +x is horizontal/right, world +y is upward, and the ground is `y = 0`. Screen-coordinate inversion exists only in the renderer.
@@ -17 +17 @@ The simulator should use SI units internally:
-Screen pixels should never be used as physics units.
+## State and configuration
@@ -19 +19 @@ Screen pixels should never be used as physics units.
----
+Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, thrust magnitude, burn duration, fixed world launch angle, gravity magnitude, fixed physics timestep, and initial position and velocity.
@@ -21 +21 @@ Screen pixels should never be used as physics units.
-## Coordinate System
+All scalar and vector inputs must be finite. Mass and timestep must be positive. Thrust, burn duration, and gravity magnitude may be zero but not negative. Initial altitude may not be below ground.
@@ -23 +23 @@ Screen pixels should never be used as physics units.
-Use a two-dimensional Cartesian coordinate system:
+## Forces and acceleration
@@ -25,53 +25 @@ Use a two-dimensional Cartesian coordinate system:
-- +x = horizontal right
-- +y = upward
-- Ground = y = 0
-
-Pygame screen coordinates increase downward, so the renderer must convert simulation coordinates to screen coordinates.
-
----
-
-## Core State Variables
-
-At minimum, the rocket state should contain:
-
-```text
-time
-position_x
-position_y
-velocity_x
-velocity_y
-mass
-```
-
-Later versions may add:
-
-```text
-angle
-angular_velocity
-propellant_mass
-acceleration_x
-acceleration_y
-mach_number
-```
-
----
-
-## Milestone 1 Physics
-
-### Gravity
-
-Assume constant gravitational acceleration:
-
-```text
-g = 9.81 m/s²
-```
-
-The gravitational force is:
-
-```text
-F_gravity = m g
-```
-
-acting downward.
-
-In vector form:
+For constant mass `m > 0`, gravity magnitude `g >= 0`, thrust magnitude `T >= 0`, fixed launch angle `theta`, and burn duration `t_b >= 0`:
@@ -83,81 +31 @@ F_g = (0, -m g)
-### Thrust
-
-For the first implementation, assume constant thrust during the motor burn.
-
-For thrust magnitude `T` and launch angle `theta`:
-
-```text
-F_thrust_x = T cos(theta)
-F_thrust_y = T sin(theta)
-```
-
-After burnout:
-
-```text
-T = 0
-```
-
-### Net Force
-
-```text
-F_net = F_thrust + F_gravity
-```
-
-### Acceleration
-
-Newton's second law:
-
-```text
-a = F_net / m
-```
-
-Therefore:
-
-```text
-a_x = F_net_x / m
-a_y = F_net_y / m
-```
-
----
-
-## Numerical Integration
-
-Use a fixed simulation timestep `dt` initially.
-
-Recommended starting value:
-
-```text
-dt = 0.01 s
-```
-
-Use semi-implicit Euler integration:
-
-```text
-v_new = v_old + a * dt
-x_new = x_old + v_new * dt
-```
-
-This is preferable to updating position using the old velocity because it is generally more stable for simple real-time simulations.
-
-The physics timestep should be independent from the graphical frame rate if possible.
-
----
-
-## Milestone 2: Aerodynamic Drag
-
-Drag magnitude:
-
-```text
-F_drag = 0.5 * rho * C_d * A * v²
-```
-
-where:
-
-- `rho` = air density
-- `C_d` = drag coefficient
-- `A` = reference/frontal area
-- `v` = speed
-
-Drag must point opposite the velocity vector.
-
-For speed:
+Thrust uses an exact half-open time interval:
@@ -166 +34,2 @@ For speed:
-v = sqrt(v_x² + v_y²)
+F_T(t) = T(cos(theta), sin(theta))  when 0 <= t < t_b
+F_T(t) = (0, 0)                    otherwise
@@ -169,22 +38 @@ v = sqrt(v_x² + v_y²)
-If `v > 0`:
-
-```text
-F_drag_x = -F_drag * v_x / v
-F_drag_y = -F_drag * v_y / v
-```
-
-Initial simplification:
-
-```text
-rho = 1.225 kg/m³
-```
-
-at sea level.
-
----
-
-## Milestone 3: Variable Mass
-
-Model propellant consumption during motor burn.
-
-A simple first model:
+Negative time never produces thrust. Net acceleration is:
@@ -193 +41 @@ A simple first model:
-mass(t) = dry_mass + remaining_propellant_mass
+a(t) = (F_T(t) + F_g) / m
@@ -196 +44 @@ mass(t) = dry_mass + remaining_propellant_mass
-For constant mass flow:
+Therefore the powered and coast accelerations are:
@@ -199 +47,2 @@ For constant mass flow:
-propellant_mass_remaining = initial_propellant_mass - mass_flow_rate * t
+a_power = (T cos(theta) / m, T sin(theta) / m - g)
+a_coast = (0, -g)
@@ -202,3 +51 @@ propellant_mass_remaining = initial_propellant_mass - mass_flow_rate * t
-Clamp remaining propellant mass to zero.
-
-The reduced mass should automatically increase acceleration for the same thrust.
+Mass does not change at ignition, burnout, coast, or landing.
@@ -206 +53 @@ The reduced mass should automatically increase acceleration for the same thrust.
----
+## Numerical integration
@@ -208,5 +55 @@ The reduced mass should automatically increase acceleration for the same thrust.
-## Milestone 4: Real Motor Thrust Curve
-
-Replace constant thrust with a time-dependent motor curve.
-
-Example data:
+The default fixed physics timestep is `dt = 0.01 s`. Every interval over which acceleration is constant uses semi-implicit Euler in this exact order:
@@ -215,7 +58,2 @@ Example data:
-time_s,thrust_N
-0.00,0
-0.05,25
-0.10,40
-0.30,35
-0.60,20
-0.80,0
+v_next = v_current + a_current dt
+p_next = p_current + v_next dt
@@ -224,20 +62 @@ time_s,thrust_N
-Interpolate between samples to obtain thrust at simulation time.
-
-Possible future source: published model rocket motor test data.
-
----
-
-## Milestone 5: Atmospheric Model
-
-Allow air density to decrease with altitude.
-
-A simple approximation can be introduced first. A more realistic standard-atmosphere model can be added later.
-
-Potential variables:
-
-```text
-temperature
-pressure
-air_density
-speed_of_sound
-```
+If a configured step begins before burnout and ends after it, the simulator performs a powered substep ending exactly at `t_b`, followed by a coast substep for the remaining duration. A step ending exactly at burnout is powered for its entire interval; the resulting state at `t_b` reports coast phase and coast acceleration. A step starting at burnout is entirely coast.
@@ -245 +64 @@ speed_of_sound
-Mach number:
+For constant acceleration over `t = N dt`, velocity is exact apart from floating-point roundoff. Semi-implicit position differs from the continuous solution by:
@@ -248 +67 @@ Mach number:
-Mach = speed / speed_of_sound
+p_numerical - p_analytical = 0.5 a t dt
@@ -251 +70 @@ Mach = speed / speed_of_sound
----
+Position is therefore first-order accurate: its error should approximately halve when `dt` halves.
@@ -253 +72 @@ Mach = speed / speed_of_sound
-## Milestone 6: Attitude and Stability
+## Continuous analytical references
@@ -255,3 +74 @@ Mach = speed / speed_of_sound
-Once translational motion is reliable, introduce rocket orientation.
-
-State variables:
+For a constant acceleration `a` over duration `t`:
@@ -260,3 +77,2 @@ State variables:
-angle theta
-angular_velocity omega
-angular_acceleration alpha
+v(t) = v0 + a t
+p(t) = p0 + v0 t + 0.5 a t²
@@ -265 +81 @@ angular_acceleration alpha
-Rotational dynamics:
+For a powered/coast case, evaluate those equations with `a_power` through `t_b` to obtain `p_b` and `v_b`, then with `a_coast` for `tau = t - t_b`:
@@ -268 +84,2 @@ Rotational dynamics:
-torque = I * alpha
+v(t) = v_b + a_coast tau
+p(t) = p_b + v_b tau + 0.5 a_coast tau²
@@ -271 +88 @@ torque = I * alpha
-or:
+These continuous equations are the independent test oracle, with tolerances derived from the known Euler position error.
@@ -273,3 +90 @@ or:
-```text
-alpha = torque / I
-```
+## Ground boundary
@@ -277 +92 @@ alpha = torque / I
-Eventually, aerodynamic force should depend on angle of attack, center of pressure, and center of mass.
+Landing cannot trigger merely because the initial position is on the ground. The state first has to attain positive altitude. On the first later descending numerical segment whose endpoints cross from `y > 0` to `y <= 0`, the simulator linearly interpolates time, horizontal position, and velocity between the discrete endpoints, sets altitude to exactly zero, and enters a terminal landed phase. Any remainder of that physics step is discarded.
@@ -279 +94 @@ Eventually, aerodynamic force should depend on angle of attack, center of pressu
-This milestone is a major increase in complexity and should not be started until earlier models are validated.
+This is deterministic event interpolation, not an exact root solve. Landing time, range, and impact velocity remain timestep-sensitive and must not be reported as exact.
@@ -281 +96 @@ This milestone is a major increase in complexity and should not be started until
----
+A configuration starting on the ground is accepted only when its initial vertical velocity is non-negative and the endpoint of its first constant-force numerical segment is above ground. A downward initial velocity or a short flight that is too under-resolved to produce a positive first endpoint terminates at the initial ground state without recording negative altitude. Holding or resolving such a rocket on a pad would require an unimplemented contact/normal-force model. Gravity-only and zero-thrust analytical cases therefore start above ground or use a timestep that resolves their upward motion.
@@ -283 +98 @@ This milestone is a major increase in complexity and should not be started until
-## Ground Interaction
+The terminal state represents the instant of impact. If impact occurs before burnout, its instantaneous acceleration and reported thrust still follow the half-open burn model at that impact time; no later motion is integrated.
@@ -285 +100 @@ This milestone is a major increase in complexity and should not be started until
-The simulation begins with:
+## Implemented default scenario
@@ -288 +103,6 @@ The simulation begins with:
-y = 0
+mass              1.0 kg
+thrust            20.0 N
+burn duration     1.0 s
+launch angle      pi/2 rad (vertical)
+gravity           9.81 m/s²
+physics timestep  0.01 s
@@ -291,15 +111 @@ y = 0
-After launch, if the rocket returns to:
-
-```text
-y <= 0
-```
-
-and is descending, the flight should end.
-
-For the first version, no bounce or impact dynamics are needed.
-
----
-
-## Important Assumptions to Track
-
-Every simulation run should make clear which assumptions are active.
+The continuous powered acceleration is `10.19 m/s²` upward, so this scenario leaves the ground.
@@ -307 +113 @@ Every simulation run should make clear which assumptions are active.
-Examples:
+## Explicit omissions
@@ -309,7 +115 @@ Examples:
-- Flat Earth over short range.
-- Constant `g`.
-- No Coriolis force.
-- No wind unless enabled.
-- Rocket treated as a point mass until attitude dynamics are added.
-- Constant drag coefficient unless otherwise specified.
-- No transonic aerodynamic correction unless explicitly implemented.
+The model has no aerodynamic drag, wind, atmospheric variation, propellant depletion, variable mass, sampled thrust curve, attitude change, rotation, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. No empirical game-feel constants or clamps are applied.
@@ -317 +117 @@ Examples:
-These assumptions should eventually appear in exported experiment metadata.
+These omissions bound the meaning of results. The 2D point-mass trajectory is a validated learning model, not a calibrated real-flight or engineering-grade prediction.
diff --git a/docs/VALIDATION.md b/docs/VALIDATION.md
index 8c415ac..3816b3c 100644
--- a/docs/VALIDATION.md
+++ b/docs/VALIDATION.md
@@ -1 +1 @@
-# Validation and Testing Plan
+# Validation and Testing
@@ -3 +3 @@
-## Purpose
+## Current evidence standard
@@ -5 +5 @@
-A physics simulator is only useful if its output can be trusted. This document defines how the simulation should be checked as features are added.
+RocketSim validates simple cases against independently calculated known answers before relying on integrated flight behavior. Expected analytical values in tests are computed directly from literal parameters and closed-form equations, not by calling production force, phase, or integration helpers.
@@ -7 +7 @@ A physics simulator is only useful if its output can be trusted. This document d
-The guiding principle is:
+The suite runs headlessly with:
@@ -9,7 +9,3 @@ The guiding principle is:
-> Validate simple cases against known answers before trusting complex cases.
-
----
-
-## 1. Unit Tests
-
-Create automated tests for small physics functions.
+```bash
+conda run -n rocketsim python -m pytest
+```
@@ -17 +13 @@ Create automated tests for small physics functions.
-Examples:
+## Implemented checks
@@ -19 +15 @@ Examples:
-### Gravity
+### Configuration and force algebra
@@ -21 +17,10 @@ Examples:
-For a 2 kg rocket:
+- finite input enforcement
+- positive mass and timestep
+- non-negative thrust, burn duration, and gravity
+- valid zero-valued limiting cases
+- gravitational sign and magnitude
+- thrust components at 0, 90, and 180 degrees
+- net acceleration from force divided by mass
+- thrust immediately before, exactly at, and immediately after burnout
+- negative time producing no thrust
+- constant mass throughout a complete run
@@ -23,3 +28 @@ For a 2 kg rocket:
-```text
-F_g = 2 × 9.81 = 19.62 N downward
-```
+Direct identities use approximately `1e-12` absolute tolerance where floating-point trigonometry is involved.
@@ -27 +30 @@ F_g = 2 × 9.81 = 19.62 N downward
-### Thrust Components
+### Integration and event boundaries
@@ -29 +32,9 @@ F_g = 2 × 9.81 = 19.62 N downward
-At 90° launch angle:
+- one-step ordering that distinguishes semi-implicit from explicit Euler
+- a deliberately non-grid-aligned fixed step that crosses burnout
+- exact powered impulse and coast remainder in the crossing step
+- coast phase and instantaneous coast acceleration at the resulting boundary
+- no false landing at launch
+- deterministic interpolated ground crossing and terminal immutability
+- deterministic no-liftoff behavior for an unsupported ground configuration
+- no negative-altitude history for a downward or under-resolved ground start
+- consistent thrust and acceleration telemetry for an impact before burnout
@@ -31,4 +42 @@ At 90° launch angle:
-```text
-F_thrust_x ≈ 0
-F_thrust_y ≈ T
-```
+### Independent analytical motion
@@ -36 +44 @@ F_thrust_y ≈ T
-At 0° launch angle:
+The continuous references are:
@@ -39,2 +47,2 @@ At 0° launch angle:
-F_thrust_x ≈ T
-F_thrust_y ≈ 0
+v(t) = v0 + a t
+p(t) = p0 + v0 t + 0.5 a t²
@@ -43,15 +51 @@ F_thrust_y ≈ 0
-### Drag
-
-Verify that drag:
-
-- is zero at zero speed,
-- points opposite velocity,
-- increases by approximately 4× when speed doubles.
-
----
-
-## 2. Analytical Projectile Test
-
-Disable thrust after assigning an initial velocity and disable drag.
-
-For constant gravity:
+They are applied independently to gravity-only, powered constant-acceleration, and piecewise powered/coast cases. Velocity is expected to agree to roundoff during constant-acceleration intervals. Position expectations include the known semi-implicit Euler error:
@@ -60,3 +54 @@ For constant gravity:
-x(t) = x0 + vx0 t
-
-y(t) = y0 + vy0 t - 0.5 g t²
+p_numerical - p_analytical = 0.5 a t dt
@@ -65,3 +57 @@ y(t) = y0 + vy0 t - 0.5 g t²
-Compare simulation position against this analytical result.
-
-This is one of the most important early tests.
+The suite also checks vertical horizontal displacement, zero thrust, zero gravity, and uniform zero-force motion.
@@ -69 +59 @@ This is one of the most important early tests.
----
+### Convergence
@@ -71,16 +61 @@ This is one of the most important early tests.
-## 3. Vertical Launch Test
-
-Launch at exactly 90° with no drag.
-
-Expected behavior:
-
-- Horizontal displacement should remain approximately zero.
-- Vertical velocity should increase during sufficient powered thrust.
-- After burnout, vertical velocity should decrease linearly under gravity.
-- At apogee, vertical velocity should pass through zero.
-
----
-
-## 4. Timestep Convergence Test
-
-Run the same simulation using:
+An analytically referenced powered case runs with:
@@ -94,57 +69 @@ dt = 0.005 s
-Compare:
-
-- apogee,
-- flight time,
-- maximum speed,
-- landing position.
-
-Results should converge as timestep decreases.
-
-If halving `dt` dramatically changes the result, the timestep is too large or the numerical method is inadequate.
-
----
-
-## 5. FPS Independence Test
-
-Run rendering at different frame rates while keeping physics timestep fixed.
-
-For example:
-
-```text
-30 FPS
-60 FPS
-144 FPS
-```
-
-Final trajectory results should remain nearly identical.
-
----
-
-## 6. Energy Sanity Check
-
-For a drag-free coast phase, mechanical energy should remain approximately constant:
-
-```text
-E = 0.5 m v² + m g h
-```
-
-Small numerical error is expected.
-
-Large systematic gain or loss indicates an integration problem.
-
----
-
-## 7. Drag Sanity Checks
-
-With drag enabled:
-
-- Maximum altitude should normally decrease.
-- Mechanical energy should decrease during unpowered flight.
-- Higher drag coefficient should reduce apogee and speed.
-- Larger frontal area should increase drag.
-
----
-
-## 8. Motor Validation
-
-For thrust-curve motors, compute total impulse:
+Position error must decrease monotonically and the error ratio must remain close to two, which is evidence of first-order convergence. A finer run from the same production integrator is not used as the sole correctness oracle.
@@ -152,3 +71 @@ For thrust-curve motors, compute total impulse:
-```text
-I = integral(T dt)
-```
+The default vertical flight also compares interpolated landing time at those three timesteps with the independently solved positive root of the piecewise powered/coast trajectory. Landing-time error must decrease and approximately halve with timestep.
@@ -156 +73 @@ I = integral(T dt)
-Numerically integrate the loaded thrust curve and compare against published or expected motor impulse.
+### Lifecycle and time separation
@@ -158 +75,8 @@ Numerically integrate the loaded thrust curve and compare against published or e
----
+- full flight leaves the ground and later terminates while descending
+- reset restores state, history, flags, counter, and fractional accumulator
+- replaying the same elapsed-time sequence after reset gives exactly the same history
+- paused wall time does not accumulate
+- pre-launch wall time does not accumulate and pause can resume with retained fractional time
+- zero elapsed time at a very small valid timestep cannot fabricate a physics step
+- a representably subthreshold elapsed interval cannot fabricate a physics step
+- equal `0.5 s` elapsed durations partitioned at 30, 60, and 144 FPS produce the same 50 fixed physics steps and identical trajectory
@@ -160 +84 @@ Numerically integrate the loaded thrust curve and compare against published or e
-## 9. Regression Tests
+FPS validation feeds frame durations through the public accumulator rather than bypassing it with direct physics calls.
@@ -162 +86 @@ Numerically integrate the loaded thrust curve and compare against published or e
-When a milestone is completed, save several reference scenarios.
+### Rendering and application
@@ -164 +88,5 @@ When a milestone is completed, save several reference scenarios.
-Example:
+- physics modules have no Pygame import
+- world-to-screen conversion reverses only the vertical axis
+- drawing does not mutate physics state or trajectory
+- keyboard controls exercise launch/pause, reset, and exit
+- a dummy SDL display runs the application for a bounded number of frames and exits normally
@@ -166,8 +94 @@ Example:
-```text
-Scenario: basic_vertical_v1
-Mass: 1.0 kg
-Thrust: 20 N
-Burn: 1.0 s
-Angle: 90 deg
-Drag: disabled
-```
+## Full validation procedure
@@ -175 +96 @@ Drag: disabled
-Record expected approximate:
+Before a completed implementation is committed and pushed:
@@ -177,4 +98,9 @@ Record expected approximate:
-```text
-apogee
-flight time
-max velocity
+```bash
+conda run -n rocketsim python --version
+conda run -n rocketsim python -c "import sys; print(sys.executable)"
+conda run -n rocketsim python -m pip --version
+conda run -n rocketsim python -m compileall -q src tests
+conda run -n rocketsim python -m pytest
+conda run -n rocketsim python -c "import rocket_sim"
+SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy conda run -n rocketsim python -c "from rocket_sim.app import run; raise SystemExit(run(max_frames=2))"
+git diff --check
@@ -183,7 +109 @@ max velocity
-Future code changes should not unexpectedly change these values.
-
----
-
-## 10. Real-World Validation
-
-Only after the mathematical model is internally validated should it be compared with real rocket flight data.
+## Interpretation limits
@@ -191,29 +111 @@ Only after the mathematical model is internally validated should it be compared
-Potential measurements:
-
-- launch mass,
-- motor type,
-- measured altitude,
-- accelerometer data,
-- barometric altitude,
-- GPS trajectory,
-- video-derived ascent time.
-
-Real-world discrepancies can then be used to improve assumptions such as drag coefficient or atmospheric conditions.
-
----
-
-## Validation Log Template
-
-For each test:
-
-```text
-Test name:
-Date:
-Simulator version/commit:
-Parameters:
-Expected result:
-Observed result:
-Difference:
-Pass/fail:
-Notes:
-```
+Landing interpolation follows the discrete numerical segment; it is not an exact impact root. Event time, apogee, and landing metrics remain timestep-sensitive. The suite establishes correctness for the documented simplified equations and numerical contract, not agreement with real rockets. Real-flight comparison requires later calibration, uncertainty analysis, and measured data kept separate from evaluation data.
diff --git a/docs/decisions/decision_02_constant_thrust_state_model.md b/docs/decisions/decision_02_constant_thrust_state_model.md
new file mode 100644
index 0000000..d3b1d5e
--- /dev/null
+++ b/docs/decisions/decision_02_constant_thrust_state_model.md
@@ -0,0 +1,37 @@
+# Decision 02: Constant-thrust point-mass state model
+
+- Date: 2026-08-27
+- Status: accepted
+- Related prompt: `docs/prompts/prompt_02_physics.md`
+- Supersedes: none
+
+## Decision
+
+Milestone 1 represents the rocket as a constant-mass point with immutable recorded states containing time, 2D position, 2D velocity, instantaneous acceleration, mass, physical phase, and a liftoff flag. It applies only constant gravity and constant thrust at a fixed world angle during the half-open interval `0 <= t < burn_time`.
+
+The default vertical case is `m = 1 kg`, `T = 20 N`, `burn_time = 1 s`, `g = 9.81 m/s²`, and `dt = 0.01 s`. All physics values use SI units and +y points upward.
+
+## Context
+
+Prompt 02 requires the smallest physical model that produces powered ascent, burnout, coast, descent, and landing while remaining analytically understandable. Constant mass intentionally excludes propellant depletion. A fixed world thrust direction intentionally excludes attitude dynamics.
+
+## Options considered
+
+- Store mass only in configuration or repeat it in each state. Repeating it makes the invariant visible in telemetry and history while configuration remains authoritative.
+- Treat a non-lifting or under-resolved ground configuration as supported by a pad, allow negative altitude, or terminate at its initial state. Termination avoids inventing an unmodeled normal force or integrating underground.
+- Derive displayed acceleration from the last interval or from the current time. Instantaneous current-time acceleration keeps exact-burnout telemetry consistent with coast phase.
+
+## Rationale
+
+The accepted model keeps every force physically named, preserves explicit units and signs, supports independent closed-form validation, and avoids speculative motor, contact, or attitude abstractions.
+
+## Consequences and limits
+
+- Mass is exactly constant throughout a run.
+- At exact burnout, thrust is zero and telemetry reports coast acceleration.
+- A ground start needs non-negative initial vertical velocity and a positive-altitude endpoint for its first constant-force numerical segment.
+- A terminal state retains time-consistent thrust and acceleration at the instant of impact.
+- Gravity-only and zero-thrust references start above ground when needed.
+- The result is not a 3D, aerodynamic, calibrated, or engineering-grade prediction.
+
+No prior decision is superseded.
diff --git a/docs/decisions/decision_03_fixed_step_and_event_semantics.md b/docs/decisions/decision_03_fixed_step_and_event_semantics.md
new file mode 100644
index 0000000..7ed615e
--- /dev/null
+++ b/docs/decisions/decision_03_fixed_step_and_event_semantics.md
@@ -0,0 +1,38 @@
+# Decision 03: Fixed-step integration and event semantics
+
+- Date: 2026-08-27
+- Status: accepted
+- Related prompt: `docs/prompts/prompt_02_physics.md`
+- Supersedes: none
+
+## Decision
+
+Use semi-implicit Euler with a default fixed timestep of `0.01 s`, updating velocity before position. Accumulate unpaused wall time with compensated summation and consume only complete fixed physics steps, retaining fractional residue without dropping or fabricating elapsed time.
+
+Split any fixed step that spans burnout into powered and coast substeps at the exact half-open boundary. Detect a descending return to ground only after liftoff and linearly interpolate the first discrete crossing to `y = 0`; then stop and discard the unused remainder of that physics step.
+
+## Context
+
+The integrator, time-source boundary, and discontinuous events materially determine reproducibility, thrust impulse, displayed phase, and validation tolerances.
+
+## Options considered
+
+- Explicit Euler, semi-implicit Euler, and higher-order methods. Semi-implicit Euler is the required understandable first method; higher-order methods are unnecessary for this milestone.
+- Choose thrust once per outer step or split at burnout. Splitting preserves the exact configured powered duration when burnout is not aligned to `dt`.
+- End-of-step ground clamp, linear event interpolation, or analytical root solve. Linear interpolation is deterministic and modestly improves event reporting without claiming high-precision collision dynamics.
+- Cap accumulator substeps and drop excess time or consume all elapsed time. Consuming all time preserves FPS independence; no arbitrary time-dropping cap is used.
+
+## Rationale
+
+The scheme is simple, deterministic, testable against known first-order position error, and independent of rendering cadence. Exact burnout segmentation avoids a full-step impulse error at the force discontinuity.
+
+## Consequences and tradeoffs
+
+- Constant-acceleration velocity is exact to roundoff, but position has first-order error `0.5 a t dt`.
+- Position error should approximately halve with timestep.
+- A boundary state at burnout is coast even though the preceding interval was powered.
+- Landing is interpolation of the discrete path, not an exact physical impact solution, and remains timestep-sensitive.
+- Reset must clear state, trajectory, accumulator, and step count to reproduce a run.
+- Zero or representably subthreshold elapsed time never advances a physics step, including for very small positive configured timesteps.
+
+No prior decision is superseded.
diff --git a/docs/decisions/decision_04_specialist_review_workflow.md b/docs/decisions/decision_04_specialist_review_workflow.md
new file mode 100644
index 0000000..fccdfa4
--- /dev/null
+++ b/docs/decisions/decision_04_specialist_review_workflow.md
@@ -0,0 +1,35 @@
+# Decision 04: Persistent specialist review workflow
+
+- Date: 2026-08-27
+- Status: accepted
+- Related prompt: `docs/prompts/prompt_02_physics.md`
+- Supersedes: none
+
+## Decision
+
+Maintain project-scoped, read-only specialist definitions in `.codex/agents/` for physics, numerical-method, and test-evidence review. For scientific or numerical implementation work, the parent agent obtains all applicable pre-implementation reviews, reconciles their findings, remains the sole implementer, then obtains post-implementation reviews and resolves blocking or important findings before committing.
+
+If a Codex runtime cannot select a checked-in named custom agent directly, it may use explicitly named read-only delegated subagents that first read and follow the corresponding TOML definition. The prompt record must disclose that fallback rather than claim the custom type was hot-loaded.
+
+## Context
+
+Physics-model errors, integration-boundary errors, and circular tests require different scrutiny. Prompt 02 also requires the specialist strategy to persist in repository policy rather than exist only in one conversation.
+
+## Options considered
+
+- One general reviewer, three bounded specialists, or direct parent review only.
+- Allow reviewers to edit or keep implementation ownership centralized.
+- Treat lack of runtime hot-loading as failure or preserve configuration and use an explicit fallback.
+
+## Rationale
+
+Three narrow, read-only perspectives provide independent challenge without creating concurrent write conflicts. Central implementation ownership makes resolution and repository history auditable. The fallback preserves honest execution across Codex runtime capabilities.
+
+## Consequences and tradeoffs
+
+- Review adds process overhead to relevant scientific changes.
+- Reviewer findings are advisory until reconciled by the parent, but unresolved blocking findings prevent completion.
+- Agent TOML describes reviewer behavior; physics truth and validation criteria remain in project documentation and decisions.
+- The workflow does not authorize scope expansion or reviewer writes.
+
+No prior decision is superseded.
diff --git a/docs/product/PROJECT_UNDERSTANDING.md b/docs/product/PROJECT_UNDERSTANDING.md
index 964bdaf..40eb697 100644
--- a/docs/product/PROJECT_UNDERSTANDING.md
+++ b/docs/product/PROJECT_UNDERSTANDING.md
@@ -5 +5 @@
-This repository is the foundation for a scientifically inspectable 2D model-rocket flight simulator. Pygame will provide interaction and visualization, while explicit, testable equations will define the simulation.
+RocketSim is a trustworthy, understandable 2D model-rocket simulator rather than an engineering-grade launch predictor. Prompt 02 completes the first powered point-mass flight milestone: a visible Pygame application backed by a headless, deterministic physics core and independent numerical evidence.
@@ -7 +7 @@ This repository is the foundation for a scientifically inspectable 2D model-rock
-Prompt 01 establishes the Milestone 0 repository and Python tooling baseline only. The package is importable, but no application loop, renderer, simulation state, or flight physics exists yet.
+Prompt 03 has not begun.
@@ -9 +9 @@ Prompt 01 establishes the Milestone 0 repository and Python tooling baseline onl
-## Implemented repository layout
+## Implemented model
@@ -11,11 +11,6 @@ Prompt 01 establishes the Milestone 0 repository and Python tooling baseline onl
-```text
-rocketsim/
-├── docs/
-│   ├── decisions/       durable project decisions
-│   ├── product/         implementation-oriented project status
-│   └── prompts/         implementation prompts and commit records
-├── src/rocket_sim/      importable Python package
-├── tests/               pytest baseline tests
-├── pyproject.toml       project metadata and dependencies
-└── README.md            developer entry point
-```
+The rocket is a constant-mass point in a 2D flat world. Internally, all quantities use SI units, +x points right, +y points upward, and the ground is `y = 0`.
+
+The only forces are:
+
+- constant gravity `(0, -m g)`; and
+- constant thrust `T(cos(theta), sin(theta))` during `0 <= t < burn_time`.
@@ -23 +18 @@ rocketsim/
-The repository intentionally has no speculative physics, rendering, motor, environment, or experiment modules. Those boundaries will emerge from concrete implementation work.
+The default configuration is `m = 1 kg`, `T = 20 N`, `burn_time = 1 s`, `theta = 90 degrees`, `g = 9.81 m/s²`, and `dt = 0.01 s`. It is intentionally capable of liftoff. A ground start is accepted only when its initial vertical velocity is non-negative and its first constant-force numerical segment ends above ground. Otherwise it terminates at the initial ground state without recording negative altitude; no pad normal-force model is claimed.
@@ -25 +20,10 @@ The repository intentionally has no speculative physics, rendering, motor, envir
-## Python and dependency baseline
+## Implemented structure
+
+```text
+src/rocket_sim/config.py       validated immutable configuration and neutral Vector2
+src/rocket_sim/physics.py      force equations and semi-implicit Euler segment update
+src/rocket_sim/simulation.py   state, lifecycle, fixed-step clock, events, and history
+src/rocket_sim/rendering.py    world-to-screen transform, drawing, and telemetry
+src/rocket_sim/app.py          Pygame loop and controls
+src/rocket_sim/__main__.py     python -m rocket_sim entry point
+```
@@ -27,9 +31 @@ The repository intentionally has no speculative physics, rendering, motor, envir
-- Development requires an isolated Python 3.12 environment with its own pip.
-- The primary development machine uses the Miniconda environment named `rocketsim`, created with both `python=3.12` and `pip`.
-- The Conda environment is the single environment layer; it does not contain a nested `venv`.
-- Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`.
-- `pyproject.toml` is the only project and dependency declaration.
-- Pygame is the sole runtime dependency.
-- pytest is the sole development dependency.
-- Installation uses `python -m pip` so pip provenance matches the selected interpreter.
-- The project uses a `src/` package layout and editable development installation.
+The physics modules do not import Pygame. Rendering reads immutable state samples and cannot change simulation results.
@@ -37 +33 @@ The repository intentionally has no speculative physics, rendering, motor, envir
-## Architecture and scientific constraints
+## Numerical and event semantics
@@ -39,6 +35,6 @@ The repository intentionally has no speculative physics, rendering, motor, envir
-- The physics core must remain independent of Pygame wherever practical; Pygame owns display and input concerns.
-- Physics uses SI units and world coordinates: +x is right, +y is up, and gravity will act in -y.
-- Screen-coordinate inversion belongs only at the rendering boundary.
-- Physics simulation time must remain separate from wall-clock and display time.
-- The first physics implementation will use a documented fixed timestep independent of rendering FPS.
-- Physical effects will be added incrementally and validated against analytical or trusted reference results.
+- Each constant-force segment uses semi-implicit Euler: velocity is updated before position.
+- The display loop supplies elapsed wall time to a compensated accumulator; only complete fixed `physics_dt_s` steps advance the model, with no epsilon-created time.
+- Paused or pre-launch wall time is not accumulated, and reset clears accumulator residue.
+- A step spanning burnout is divided at the exact half-open burn boundary, preventing excess or missing thrust impulse.
+- Acceleration telemetry is the instantaneous acceleration at the resulting state time; at exact burnout it therefore shows coast acceleration.
+- Ground return is detected only after liftoff. The first descending discrete segment that crosses `y = 0` is linearly interpolated to the ground, then the flight becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact solve. A terminal sample represents the instant of impact, so thrust and instantaneous acceleration still reflect that time even when impact precedes burnout.
@@ -46 +42 @@ The repository intentionally has no speculative physics, rendering, motor, envir
-## Current validation
+## Validation status
@@ -48 +44 @@ The repository intentionally has no speculative physics, rendering, motor, envir
-The current pytest test imports `rocket_sim` from the editable installation and verifies its baseline package version. There are no physics tests because no physics is implemented.
+The headless test suite covers configuration validation, force signs and components, burn-boundary predicates, constant mass, Euler ordering, analytical gravity/powered/piecewise motion, non-aligned burnout splitting, limiting cases, first-order timestep convergence, reset determinism, interpolated ground return, 30/60/144 FPS partition independence, coordinate conversion, rendering non-mutation, controls, package import, and a bounded dummy-display application smoke test.
@@ -50 +46 @@ The current pytest test imports `rocket_sim` from the editable installation and
-## Current non-goals
+Analytical expected values are calculated independently in tests rather than through production force or integration helpers.
@@ -52 +48 @@ The current pytest test imports `rocket_sim` from the editable installation and
-This milestone does not implement a Pygame window, application loop, rocket state, forces, integration, rendering, telemetry, or any flight behavior. Drag, variable mass, thrust curves, atmosphere, recovery, rotation, stability, guidance, and optimization remain later work.
+## Current limits
@@ -54 +50 @@ This milestone does not implement a Pygame window, application loop, rocket stat
-## Immediate next task
+There is no drag, variable mass, real motor curve, atmosphere, wind, recovery, collision dynamics, rotation, stability, guidance, control, experiment export, calibration, or uncertainty model. The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction.
@@ -56 +52 @@ This milestone does not implement a Pygame window, application loop, rocket stat
-Prompt 02 should implement 2D constant-mass point-flight dynamics with constant gravity and finite-duration constant thrust, together with the minimum application/rendering boundary required to observe it and analytical validation of the motion equations.
+The next milestone remains out of scope for Prompt 02.
diff --git a/src/rocket_sim/__init__.py b/src/rocket_sim/__init__.py
index ac3a298..1dbf6ce 100644
--- a/src/rocket_sim/__init__.py
+++ b/src/rocket_sim/__init__.py
@@ -2,0 +3,3 @@
+from .config import SimulationConfig, Vector2
+from .simulation import FlightPhase, RocketState, Simulation
+
@@ -3,0 +7,9 @@ __version__ = "0.1.0"
+
+__all__ = [
+    "FlightPhase",
+    "RocketState",
+    "Simulation",
+    "SimulationConfig",
+    "Vector2",
+    "__version__",
+]
diff --git a/src/rocket_sim/__main__.py b/src/rocket_sim/__main__.py
new file mode 100644
index 0000000..8093865
--- /dev/null
+++ b/src/rocket_sim/__main__.py
@@ -0,0 +1,6 @@
+"""Module entry point for ``python -m rocket_sim``."""
+
+from .app import run
+
+
+raise SystemExit(run())
diff --git a/src/rocket_sim/app.py b/src/rocket_sim/app.py
new file mode 100644
index 0000000..dac8f3b
--- /dev/null
+++ b/src/rocket_sim/app.py
@@ -0,0 +1,57 @@
+"""Pygame application loop and input handling."""
+
+from __future__ import annotations
+
+import pygame
+
+from .rendering import Renderer
+from .simulation import Simulation
+
+
+WINDOW_SIZE = (900, 700)
+DISPLAY_FPS = 60
+
+
+def handle_keydown(key: int, simulation: Simulation) -> bool:
+    """Apply one key command and return whether the app should continue."""
+
+    if key == pygame.K_ESCAPE:
+        return False
+    if key == pygame.K_SPACE:
+        simulation.toggle_pause()
+    elif key == pygame.K_r:
+        simulation.reset()
+    return True
+
+
+def run(max_frames: int | None = None) -> int:
+    """Run the interactive app, optionally bounded for automated smoke tests."""
+
+    if max_frames is not None and max_frames < 0:
+        raise ValueError("max_frames must be non-negative or None")
+
+    pygame.init()
+    try:
+        surface = pygame.display.set_mode(WINDOW_SIZE)
+        pygame.display.set_caption("RocketSim — constant-thrust Milestone 1")
+        clock = pygame.time.Clock()
+        simulation = Simulation()
+        renderer = Renderer(*WINDOW_SIZE)
+        running = True
+        frames = 0
+
+        while running and (max_frames is None or frames < max_frames):
+            elapsed_s = clock.tick(DISPLAY_FPS) / 1000.0
+            for event in pygame.event.get():
+                if event.type == pygame.QUIT:
+                    running = False
+                elif event.type == pygame.KEYDOWN:
+                    running = handle_keydown(event.key, simulation)
+
+            simulation.advance_elapsed(elapsed_s)
+            renderer.draw(surface, simulation)
+            pygame.display.flip()
+            frames += 1
+    finally:
+        pygame.quit()
+    return 0
diff --git a/src/rocket_sim/config.py b/src/rocket_sim/config.py
new file mode 100644
index 0000000..8992897
--- /dev/null
+++ b/src/rocket_sim/config.py
@@ -0,0 +1,78 @@
+"""Validated configuration and neutral vector types for the simulator."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+import math
+
+
+@dataclass(frozen=True, slots=True)
+class Vector2:
+    """A small Pygame-independent two-dimensional vector."""
+
+    x: float
+    y: float
+
+    def __post_init__(self) -> None:
+        if not math.isfinite(self.x) or not math.isfinite(self.y):
+            raise ValueError("vector components must be finite")
+
+    def __add__(self, other: Vector2) -> Vector2:
+        return Vector2(self.x + other.x, self.y + other.y)
+
+    def __sub__(self, other: Vector2) -> Vector2:
+        return Vector2(self.x - other.x, self.y - other.y)
+
+    def __mul__(self, scalar: float) -> Vector2:
+        return Vector2(self.x * scalar, self.y * scalar)
+
+    def __rmul__(self, scalar: float) -> Vector2:
+        return self * scalar
+
+    @property
+    def magnitude(self) -> float:
+        return math.hypot(self.x, self.y)
+
+
+def _require_finite(name: str, value: float) -> None:
+    if not math.isfinite(value):
+        raise ValueError(f"{name} must be finite")
+
+
+@dataclass(frozen=True, slots=True)
+class SimulationConfig:
+    """Physical parameters for one deterministic Milestone 1 run."""
+
+    mass_kg: float = 1.0
+    thrust_n: float = 20.0
+    burn_time_s: float = 1.0
+    launch_angle_rad: float = math.pi / 2.0
+    gravity_m_s2: float = 9.81
+    physics_dt_s: float = 0.01
+    initial_position_m: Vector2 = field(default_factory=lambda: Vector2(0.0, 0.0))
+    initial_velocity_m_s: Vector2 = field(default_factory=lambda: Vector2(0.0, 0.0))
+
+    def __post_init__(self) -> None:
+        scalar_values = {
+            "mass_kg": self.mass_kg,
+            "thrust_n": self.thrust_n,
+            "burn_time_s": self.burn_time_s,
+            "launch_angle_rad": self.launch_angle_rad,
+            "gravity_m_s2": self.gravity_m_s2,
+            "physics_dt_s": self.physics_dt_s,
+        }
+        for name, value in scalar_values.items():
+            _require_finite(name, value)
+
+        if self.mass_kg <= 0.0:
+            raise ValueError("mass_kg must be greater than zero")
+        if self.physics_dt_s <= 0.0:
+            raise ValueError("physics_dt_s must be greater than zero")
+        if self.thrust_n < 0.0:
+            raise ValueError("thrust_n must be non-negative")
+        if self.burn_time_s < 0.0:
+            raise ValueError("burn_time_s must be non-negative")
+        if self.gravity_m_s2 < 0.0:
+            raise ValueError("gravity_m_s2 must be non-negative")
+        if self.initial_position_m.y < 0.0:
+            raise ValueError("initial altitude must be at or above ground")
diff --git a/src/rocket_sim/physics.py b/src/rocket_sim/physics.py
new file mode 100644
index 0000000..e675243
--- /dev/null
+++ b/src/rocket_sim/physics.py
@@ -0,0 +1,49 @@
+"""Pygame-independent force and integration functions."""
+
+from __future__ import annotations
+
+import math
+
+from .config import SimulationConfig, Vector2
+
+
+def gravity_force_n(mass_kg: float, gravity_m_s2: float) -> Vector2:
+    """Return the constant downward gravitational force in newtons."""
+
+    return Vector2(0.0, -mass_kg * gravity_m_s2)
+
+
+def thrust_force_n(config: SimulationConfig, time_s: float) -> Vector2:
+    """Return constant world-angle thrust on the half-open burn interval."""
+
+    if not math.isfinite(time_s):
+        raise ValueError("time_s must be finite")
+    if not 0.0 <= time_s < config.burn_time_s:
+        return Vector2(0.0, 0.0)
+    return Vector2(
+        config.thrust_n * math.cos(config.launch_angle_rad),
+        config.thrust_n * math.sin(config.launch_angle_rad),
+    )
+
+
+def acceleration_m_s2(config: SimulationConfig, time_s: float) -> Vector2:
+    """Return net acceleration from thrust and gravity at ``time_s``."""
+
+    thrust = thrust_force_n(config, time_s)
+    gravity = gravity_force_n(config.mass_kg, config.gravity_m_s2)
+    return (thrust + gravity) * (1.0 / config.mass_kg)
+
+
+def semi_implicit_euler(
+    position_m: Vector2,
+    velocity_m_s: Vector2,
+    acceleration: Vector2,
+    duration_s: float,
+) -> tuple[Vector2, Vector2]:
+    """Advance one constant-acceleration segment using updated velocity."""
+
+    if not math.isfinite(duration_s) or duration_s <= 0.0:
+        raise ValueError("duration_s must be finite and greater than zero")
+    new_velocity = velocity_m_s + acceleration * duration_s
+    new_position = position_m + new_velocity * duration_s
+    return new_position, new_velocity
diff --git a/src/rocket_sim/rendering.py b/src/rocket_sim/rendering.py
new file mode 100644
index 0000000..ae953bb
--- /dev/null
+++ b/src/rocket_sim/rendering.py
@@ -0,0 +1,100 @@
+"""Pygame presentation for RocketSim world state."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+
+import pygame
+
+from .config import Vector2
+from .simulation import FlightPhase, Simulation
+
+
+def world_to_screen(
+    position_m: Vector2,
+    origin_px: tuple[float, float],
+    pixels_per_metre: float,
+) -> tuple[int, int]:
+    """Map +y-up world metres to +y-down screen pixels."""
+
+    return (
+        round(origin_px[0] + position_m.x * pixels_per_metre),
+        round(origin_px[1] - position_m.y * pixels_per_metre),
+    )
+
+
+@dataclass(slots=True)
+class Renderer:
+    width_px: int = 900
+    height_px: int = 700
+    pixels_per_metre: float = 20.0
+    ground_y_px: int = 620
+    _font: pygame.font.Font = field(init=False, repr=False)
+
+    def __post_init__(self) -> None:
+        self._font = pygame.font.Font(None, 25)
+
+    @property
+    def origin_px(self) -> tuple[float, float]:
+        return (self.width_px / 2.0, float(self.ground_y_px))
+
+    def draw(self, surface: pygame.Surface, simulation: Simulation) -> None:
+        surface.fill((12, 20, 36))
+        pygame.draw.rect(
+            surface,
+            (52, 83, 55),
+            pygame.Rect(0, self.ground_y_px, self.width_px, self.height_px),
+        )
+        pygame.draw.line(
+            surface,
+            (142, 174, 125),
+            (0, self.ground_y_px),
+            (self.width_px, self.ground_y_px),
+            2,
+        )
+
+        points = [
+            world_to_screen(sample.position_m, self.origin_px, self.pixels_per_metre)
+            for sample in simulation.trajectory
+        ]
+        if len(points) >= 2:
+            pygame.draw.lines(surface, (96, 184, 255), False, points, 2)
+
+        rocket_x, rocket_y = world_to_screen(
+            simulation.state.position_m,
+            self.origin_px,
+            self.pixels_per_metre,
+        )
+        pygame.draw.polygon(
+            surface,
+            (245, 214, 96),
+            [(rocket_x, rocket_y - 12), (rocket_x - 6, rocket_y + 8), (rocket_x + 6, rocket_y + 8)],
+        )
+
+        self._draw_telemetry(surface, simulation)
+
+    def _draw_telemetry(self, surface: pygame.Surface, simulation: Simulation) -> None:
+        state = simulation.state
+        if state.phase is FlightPhase.READY:
+            status = "READY"
+        elif state.phase is FlightPhase.LANDED:
+            status = "LANDED"
+        elif simulation.is_paused:
+            status = f"PAUSED / {state.phase.value.upper()}"
+        else:
+            status = state.phase.value.upper()
+
+        rows = (
+            "SPACE launch/pause  |  R reset  |  ESC exit",
+            f"Phase: {status}",
+            f"Time: {state.time_s:7.3f} s",
+            f"Position: ({state.position_m.x:7.3f}, {state.position_m.y:7.3f}) m",
+            f"Velocity: ({state.velocity_m_s.x:7.3f}, {state.velocity_m_s.y:7.3f}) m/s",
+            f"Speed: {state.velocity_m_s.magnitude:7.3f} m/s",
+            f"Acceleration: ({state.acceleration_m_s2.x:7.3f}, {state.acceleration_m_s2.y:7.3f}) m/s²",
+            f"Mass: {state.mass_kg:7.3f} kg",
+            f"Thrust: {simulation.current_thrust_n:7.3f} N",
+        )
+        for index, text in enumerate(rows):
+            rendered = self._font.render(text, True, (232, 238, 247))
+            surface.blit(rendered, (18, 16 + index * 25))
diff --git a/src/rocket_sim/simulation.py b/src/rocket_sim/simulation.py
new file mode 100644
index 0000000..2791a80
--- /dev/null
+++ b/src/rocket_sim/simulation.py
@@ -0,0 +1,284 @@
+"""Deterministic flight lifecycle and fixed-timestep simulation."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass
+from enum import Enum
+import math
+
+from .config import SimulationConfig, Vector2
+from .physics import acceleration_m_s2, semi_implicit_euler
+
+
+class FlightPhase(str, Enum):
+    READY = "ready"
+    POWERED = "powered"
+    COAST = "coast"
+    LANDED = "landed"
+
+
+@dataclass(frozen=True, slots=True)
+class RocketState:
+    time_s: float
+    position_m: Vector2
+    velocity_m_s: Vector2
+    acceleration_m_s2: Vector2
+    mass_kg: float
+    phase: FlightPhase
+    has_lifted_off: bool
+
+
+class Simulation:
+    """Own a single constant-mass rocket flight and its recorded trajectory."""
+
+    def __init__(self, config: SimulationConfig | None = None) -> None:
+        self.config = config or SimulationConfig()
+        self._state = self._initial_state()
+        self._trajectory: list[RocketState] = [self._state]
+        self._accumulator_s = 0.0
+        self._accumulator_compensation_s = 0.0
+        self._is_running = False
+        self._physics_step_count = 0
+
+    @property
+    def state(self) -> RocketState:
+        return self._state
+
+    @property
+    def trajectory(self) -> tuple[RocketState, ...]:
+        return tuple(self._trajectory)
+
+    @property
+    def accumulator_s(self) -> float:
+        return self._accumulator_s - self._accumulator_compensation_s
+
+    @property
+    def physics_step_count(self) -> int:
+        return self._physics_step_count
+
+    @property
+    def is_running(self) -> bool:
+        return self._is_running
+
+    @property
+    def is_finished(self) -> bool:
+        return self._state.phase is FlightPhase.LANDED
+
+    @property
+    def is_paused(self) -> bool:
+        return (
+            not self._is_running
+            and self._state.phase not in (FlightPhase.READY, FlightPhase.LANDED)
+        )
+
+    @property
+    def current_thrust_n(self) -> float:
+        if self._state.phase is FlightPhase.READY:
+            return 0.0
+        if 0.0 <= self._state.time_s < self.config.burn_time_s:
+            return self.config.thrust_n
+        return 0.0
+
+    def _initial_state(self) -> RocketState:
+        return RocketState(
+            time_s=0.0,
+            position_m=self.config.initial_position_m,
+            velocity_m_s=self.config.initial_velocity_m_s,
+            acceleration_m_s2=Vector2(0.0, 0.0),
+            mass_kg=self.config.mass_kg,
+            phase=FlightPhase.READY,
+            has_lifted_off=self.config.initial_position_m.y > 0.0,
+        )
+
+    def launch(self) -> None:
+        """Start a ready flight without accumulating pre-launch wall time."""
+
+        if self._state.phase is not FlightPhase.READY:
+            return
+
+        initial_acceleration = acceleration_m_s2(self.config, 0.0)
+        can_leave_ground = self._state.position_m.y > 0.0
+        if self._state.position_m.y == 0.0 and self._state.velocity_m_s.y >= 0.0:
+            first_segment_s = self.config.physics_dt_s
+            if 0.0 < self.config.burn_time_s < first_segment_s:
+                first_segment_s = self.config.burn_time_s
+            trial_position, _ = semi_implicit_euler(
+                self._state.position_m,
+                self._state.velocity_m_s,
+                initial_acceleration,
+                first_segment_s,
+            )
+            can_leave_ground = trial_position.y > 0.0
+        if not can_leave_ground:
+            self._state = RocketState(
+                time_s=0.0,
+                position_m=Vector2(self._state.position_m.x, 0.0),
+                velocity_m_s=self._state.velocity_m_s,
+                acceleration_m_s2=initial_acceleration,
+                mass_kg=self.config.mass_kg,
+                phase=FlightPhase.LANDED,
+                has_lifted_off=False,
+            )
+            self._trajectory = [self._state]
+            return
+
+        self._state = RocketState(
+            time_s=0.0,
+            position_m=self._state.position_m,
+            velocity_m_s=self._state.velocity_m_s,
+            acceleration_m_s2=initial_acceleration,
+            mass_kg=self.config.mass_kg,
+            phase=self._phase_at(0.0),
+            has_lifted_off=self._state.has_lifted_off,
+        )
+        self._trajectory[0] = self._state
+        self._is_running = True
+
+    def toggle_pause(self) -> None:
+        """Launch when ready, otherwise pause or resume a live flight."""
+
+        if self._state.phase is FlightPhase.READY:
+            self.launch()
+        elif self._state.phase is not FlightPhase.LANDED:
+            self._is_running = not self._is_running
+
+    def reset(self) -> None:
+        """Restore all state, trajectory, timing, and lifecycle flags."""
+
+        self._state = self._initial_state()
+        self._trajectory = [self._state]
+        self._accumulator_s = 0.0
+        self._accumulator_compensation_s = 0.0
+        self._is_running = False
+        self._physics_step_count = 0
+
+    def advance_elapsed(self, elapsed_s: float) -> int:
+        """Consume wall time through fixed physics steps and return their count."""
+
+        if not math.isfinite(elapsed_s) or elapsed_s < 0.0:
+            raise ValueError("elapsed_s must be finite and non-negative")
+        if not self._is_running or self.is_finished:
+            return 0
+
+        self._add_accumulator(elapsed_s)
+        steps = 0
+        dt = self.config.physics_dt_s
+        while self.accumulator_s >= dt and self._is_running:
+            self._advance_fixed_step(dt)
+            self._physics_step_count += 1
+            steps += 1
+            self._add_accumulator(-dt)
+
+        if self.is_finished:
+            self._clear_accumulator()
+        return steps
+
+    def _add_accumulator(self, duration_s: float) -> None:
+        corrected = duration_s - self._accumulator_compensation_s
+        updated = self._accumulator_s + corrected
+        self._accumulator_compensation_s = (
+            updated - self._accumulator_s
+        ) - corrected
+        self._accumulator_s = updated
+
+    def _clear_accumulator(self) -> None:
+        self._accumulator_s = 0.0
+        self._accumulator_compensation_s = 0.0
+
+    def step(self) -> bool:
+        """Advance exactly one configured physics step when running."""
+
+        if not self._is_running or self.is_finished:
+            return False
+        self._advance_fixed_step(self.config.physics_dt_s)
+        self._physics_step_count += 1
+        return True
+
+    def _phase_at(self, time_s: float) -> FlightPhase:
+        if 0.0 <= time_s < self.config.burn_time_s:
+            return FlightPhase.POWERED
+        return FlightPhase.COAST
+
+    def _advance_fixed_step(self, duration_s: float) -> None:
+        start_s = self._state.time_s
+        target_s = start_s + duration_s
+        burnout_s = self.config.burn_time_s
+
+        if start_s < burnout_s < target_s:
+            self._advance_segment_to(burnout_s)
+            if not self.is_finished:
+                self._advance_segment_to(target_s)
+        else:
+            self._advance_segment_to(target_s)
+
+    def _advance_segment_to(self, target_time_s: float) -> None:
+        previous = self._state
+        duration_s = target_time_s - previous.time_s
+        acceleration = acceleration_m_s2(self.config, previous.time_s)
+        trial_position, trial_velocity = semi_implicit_euler(
+            previous.position_m,
+            previous.velocity_m_s,
+            acceleration,
+            duration_s,
+        )
+        lifted_off = previous.has_lifted_off or trial_position.y > 0.0
+
+        if (
+            previous.has_lifted_off
+            and previous.position_m.y > 0.0
+            and trial_position.y <= 0.0
+            and trial_velocity.y < 0.0
+        ):
+            alpha = previous.position_m.y / (
+                previous.position_m.y - trial_position.y
+            )
+            impact_time_s = previous.time_s + alpha * duration_s
+            impact_position = Vector2(
+                previous.position_m.x
+                + alpha * (trial_position.x - previous.position_m.x),
+                0.0,
+            )
+            impact_velocity = previous.velocity_m_s + (
+                trial_velocity - previous.velocity_m_s
+            ) * alpha
+            self._state = RocketState(
+                time_s=impact_time_s,
+                position_m=impact_position,
+                velocity_m_s=impact_velocity,
+                acceleration_m_s2=acceleration_m_s2(self.config, impact_time_s),
+                mass_kg=self.config.mass_kg,
+                phase=FlightPhase.LANDED,
+                has_lifted_off=True,
+            )
+            self._trajectory.append(self._state)
+            self._is_running = False
+            self._clear_accumulator()
+            return
+
+        if not previous.has_lifted_off and trial_position.y <= 0.0:
+            self._state = RocketState(
+                time_s=previous.time_s,
+                position_m=Vector2(previous.position_m.x, 0.0),
+                velocity_m_s=previous.velocity_m_s,
+                acceleration_m_s2=acceleration_m_s2(
+                    self.config, previous.time_s
+                ),
+                mass_kg=self.config.mass_kg,
+                phase=FlightPhase.LANDED,
+                has_lifted_off=False,
+            )
+            self._trajectory.append(self._state)
+            self._is_running = False
+            self._clear_accumulator()
+            return
+
+        self._state = RocketState(
+            time_s=target_time_s,
+            position_m=trial_position,
+            velocity_m_s=trial_velocity,
+            acceleration_m_s2=acceleration_m_s2(self.config, target_time_s),
+            mass_kg=self.config.mass_kg,
+            phase=self._phase_at(target_time_s),
+            has_lifted_off=lifted_off,
+        )
+        self._trajectory.append(self._state)
diff --git a/tests/test_analytical_validation.py b/tests/test_analytical_validation.py
new file mode 100644
index 0000000..9e784c0
--- /dev/null
+++ b/tests/test_analytical_validation.py
@@ -0,0 +1,148 @@
+import math
+
+import pytest
+
+from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+
+
+def _run_steps(simulation: Simulation, count: int) -> None:
+    simulation.launch()
+    for _ in range(count):
+        assert simulation.step()
+
+
+def test_gravity_only_matches_independent_projectile_reference() -> None:
+    dt = 0.01
+    duration = 1.0
+    config = SimulationConfig(
+        thrust_n=0.0,
+        burn_time_s=0.0,
+        gravity_m_s2=9.81,
+        physics_dt_s=dt,
+        initial_position_m=Vector2(2.0, 100.0),
+        initial_velocity_m_s=Vector2(3.0, 4.0),
+    )
+    simulation = Simulation(config)
+    _run_steps(simulation, round(duration / dt))
+
+    expected_x = 2.0 + 3.0 * duration
+    expected_y = 100.0 + 4.0 * duration - 0.5 * 9.81 * duration**2
+    expected_vy = 4.0 - 9.81 * duration
+    expected_position_error = 0.5 * (-9.81) * duration * dt
+
+    assert simulation.state.position_m.x == pytest.approx(expected_x, abs=1e-12)
+    assert simulation.state.velocity_m_s.x == 3.0
+    assert simulation.state.velocity_m_s.y == pytest.approx(expected_vy, abs=1e-12)
+    assert simulation.state.position_m.y - expected_y == pytest.approx(
+        expected_position_error, abs=1e-11
+    )
+
+
+def test_powered_motion_matches_independent_constant_acceleration_reference() -> None:
+    dt = 0.01
+    duration = 0.5
+    mass = 2.0
+    thrust = 12.0
+    angle = math.radians(30.0)
+    gravity = 3.0
+    config = SimulationConfig(
+        mass_kg=mass,
+        thrust_n=thrust,
+        burn_time_s=2.0,
+        launch_angle_rad=angle,
+        gravity_m_s2=gravity,
+        physics_dt_s=dt,
+        initial_position_m=Vector2(0.0, 10.0),
+        initial_velocity_m_s=Vector2(1.0, 2.0),
+    )
+    simulation = Simulation(config)
+    _run_steps(simulation, round(duration / dt))
+
+    ax = thrust * math.cos(angle) / mass
+    ay = thrust * math.sin(angle) / mass - gravity
+    expected_vx = 1.0 + ax * duration
+    expected_vy = 2.0 + ay * duration
+    expected_x = 1.0 * duration + 0.5 * ax * duration**2
+    expected_y = 10.0 + 2.0 * duration + 0.5 * ay * duration**2
+
+    assert simulation.state.velocity_m_s.x == pytest.approx(expected_vx, abs=1e-12)
+    assert simulation.state.velocity_m_s.y == pytest.approx(expected_vy, abs=1e-12)
+    assert simulation.state.position_m.x - expected_x == pytest.approx(
+        0.5 * ax * duration * dt, abs=1e-12
+    )
+    assert simulation.state.position_m.y - expected_y == pytest.approx(
+        0.5 * ay * duration * dt, abs=1e-12
+    )
+
+
+def test_piecewise_powered_and_coast_motion_matches_closed_form_error() -> None:
+    dt = 0.01
+    config = SimulationConfig(physics_dt_s=dt)
+    simulation = Simulation(config)
+    _run_steps(simulation, 150)
+
+    powered_acceleration = 20.0 - 9.81
+    coast_duration = 0.5
+    burnout_velocity = powered_acceleration * 1.0
+    burnout_altitude = 0.5 * powered_acceleration * 1.0**2
+    expected_velocity = burnout_velocity - 9.81 * coast_duration
+    expected_altitude = (
+        burnout_altitude
+        + burnout_velocity * coast_duration
+        - 0.5 * 9.81 * coast_duration**2
+    )
+    expected_error = 0.5 * dt * (
+        powered_acceleration * 1.0 - 9.81 * coast_duration
+    )
+
+    assert expected_velocity == pytest.approx(5.285, abs=1e-12)
+    assert expected_altitude == pytest.approx(8.96375, abs=1e-12)
+    assert simulation.state.velocity_m_s.y == pytest.approx(expected_velocity, abs=1e-11)
+    assert simulation.state.position_m.y - expected_altitude == pytest.approx(
+        expected_error, abs=1e-11
+    )
+    assert simulation.state.phase is FlightPhase.COAST
+
+
+def test_default_vertical_launch_has_negligible_horizontal_motion() -> None:
+    simulation = Simulation()
+    _run_steps(simulation, 150)
+
+    assert abs(simulation.state.position_m.x) < 1e-12
+    assert simulation.trajectory[50].velocity_m_s.y > 0.0
+    assert simulation.state.velocity_m_s.y < simulation.trajectory[100].velocity_m_s.y
+
+
+def test_zero_gravity_powered_then_coast_limit() -> None:
+    config = SimulationConfig(
+        mass_kg=2.0,
+        thrust_n=8.0,
+        burn_time_s=0.5,
+        launch_angle_rad=0.0,
+        gravity_m_s2=0.0,
+        physics_dt_s=0.01,
+        initial_position_m=Vector2(0.0, 1.0),
+    )
+    simulation = Simulation(config)
+    _run_steps(simulation, 100)
+
+    assert simulation.state.velocity_m_s.x == pytest.approx(2.0, abs=1e-12)
+    assert simulation.state.acceleration_m_s2 == Vector2(0.0, 0.0)
+    assert simulation.state.phase is FlightPhase.COAST
+
+
+def test_zero_force_preserves_uniform_motion() -> None:
+    config = SimulationConfig(
+        thrust_n=0.0,
+        burn_time_s=0.0,
+        gravity_m_s2=0.0,
+        physics_dt_s=0.01,
+        initial_position_m=Vector2(1.0, 10.0),
+        initial_velocity_m_s=Vector2(2.0, 3.0),
+    )
+    simulation = Simulation(config)
+    _run_steps(simulation, 100)
+
+    assert simulation.state.position_m.x == pytest.approx(3.0, abs=1e-12)
+    assert simulation.state.position_m.y == pytest.approx(13.0, abs=1e-12)
+    assert simulation.state.velocity_m_s == Vector2(2.0, 3.0)
diff --git a/tests/test_config.py b/tests/test_config.py
new file mode 100644
index 0000000..4f56fa3
--- /dev/null
+++ b/tests/test_config.py
@@ -0,0 +1,60 @@
+import math
+
+import pytest
+
+from rocket_sim import SimulationConfig, Vector2
+
+
+def test_zero_valued_limiting_parameters_are_valid() -> None:
+    config = SimulationConfig(thrust_n=0.0, burn_time_s=0.0, gravity_m_s2=0.0)
+
+    assert config.thrust_n == 0.0
+    assert config.burn_time_s == 0.0
+    assert config.gravity_m_s2 == 0.0
+
+
+@pytest.mark.parametrize(
+    ("field", "value"),
+    [
+        ("mass_kg", 0.0),
+        ("mass_kg", -1.0),
+        ("physics_dt_s", 0.0),
+        ("physics_dt_s", -0.01),
+        ("thrust_n", -1.0),
+        ("burn_time_s", -1.0),
+        ("gravity_m_s2", -1.0),
+    ],
+)
+def test_invalid_physical_ranges_are_rejected(field: str, value: float) -> None:
+    with pytest.raises(ValueError):
+        SimulationConfig(**{field: value})
+
+
+@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
+@pytest.mark.parametrize(
+    "field",
+    [
+        "mass_kg",
+        "physics_dt_s",
+        "thrust_n",
+        "burn_time_s",
+        "gravity_m_s2",
+        "launch_angle_rad",
+    ],
+)
+def test_non_finite_scalars_are_rejected(field: str, value: float) -> None:
+    with pytest.raises(ValueError):
+        SimulationConfig(**{field: value})
+
+
+@pytest.mark.parametrize("component", [math.nan, math.inf, -math.inf])
+def test_non_finite_vector_components_are_rejected(component: float) -> None:
+    with pytest.raises(ValueError):
+        Vector2(component, 0.0)
+    with pytest.raises(ValueError):
+        Vector2(0.0, component)
+
+
+def test_initial_altitude_below_ground_is_rejected() -> None:
+    with pytest.raises(ValueError, match="altitude"):
+        SimulationConfig(initial_position_m=Vector2(0.0, -0.01))
diff --git a/tests/test_convergence.py b/tests/test_convergence.py
new file mode 100644
index 0000000..070a219
--- /dev/null
+++ b/tests/test_convergence.py
@@ -0,0 +1,66 @@
+import math
+
+import pytest
+
+from rocket_sim import Simulation, SimulationConfig, Vector2
+
+
+def _powered_position_error(dt: float) -> float:
+    duration = 0.5
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_n=12.0,
+            burn_time_s=2.0,
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            physics_dt_s=dt,
+            initial_position_m=Vector2(0.0, 1.0),
+        )
+    )
+    simulation.launch()
+    for _ in range(round(duration / dt)):
+        assert simulation.step()
+
+    analytical_x = 0.5 * (12.0 / 2.0) * duration**2
+    return abs(simulation.state.position_m.x - analytical_x)
+
+
+def test_semi_implicit_euler_has_first_order_position_convergence() -> None:
+    errors = [_powered_position_error(dt) for dt in (0.02, 0.01, 0.005)]
+
+    assert errors[0] > errors[1] > errors[2]
+    assert errors[0] / errors[1] == pytest.approx(2.0, rel=0.05)
+    assert errors[1] / errors[2] == pytest.approx(2.0, rel=0.05)
+
+
+def _default_landing_time_error(dt: float, analytical_time_s: float) -> float:
+    simulation = Simulation(SimulationConfig(physics_dt_s=dt))
+    simulation.launch()
+    for _ in range(2000):
+        if not simulation.step():
+            break
+    assert simulation.is_finished
+    return abs(simulation.state.time_s - analytical_time_s)
+
+
+def test_interpolated_landing_time_converges_to_piecewise_analytical_root() -> None:
+    powered_acceleration = 20.0 - 9.81
+    burnout_altitude = 0.5 * powered_acceleration
+    burnout_velocity = powered_acceleration
+    coast_duration = (
+        burnout_velocity
+        + math.sqrt(
+            burnout_velocity**2 + 2.0 * 9.81 * burnout_altitude
+        )
+    ) / 9.81
+    analytical_landing_time_s = 1.0 + coast_duration
+
+    errors = [
+        _default_landing_time_error(dt, analytical_landing_time_s)
+        for dt in (0.02, 0.01, 0.005)
+    ]
+
+    assert errors[0] > errors[1] > errors[2]
+    assert errors[0] / errors[1] == pytest.approx(2.0, rel=0.05)
+    assert errors[1] / errors[2] == pytest.approx(2.0, rel=0.05)
diff --git a/tests/test_forces.py b/tests/test_forces.py
new file mode 100644
index 0000000..40da991
--- /dev/null
+++ b/tests/test_forces.py
@@ -0,0 +1,68 @@
+import math
+
+import pytest
+
+from rocket_sim import SimulationConfig
+from rocket_sim.physics import acceleration_m_s2, gravity_force_n, thrust_force_n
+
+
+def test_gravity_force_has_correct_units_and_direction() -> None:
+    force = gravity_force_n(2.0, 9.81)
+
+    assert force.x == 0.0
+    assert force.y == pytest.approx(-19.62, abs=1e-12)
+
+
+@pytest.mark.parametrize(
+    ("angle", "expected_x", "expected_y"),
+    [
+        (0.0, 10.0, 0.0),
+        (math.pi / 2.0, 0.0, 10.0),
+        (math.pi, -10.0, 0.0),
+    ],
+)
+def test_thrust_components_at_cardinal_angles(
+    angle: float, expected_x: float, expected_y: float
+) -> None:
+    config = SimulationConfig(
+        thrust_n=10.0, launch_angle_rad=angle, gravity_m_s2=0.0
+    )
+
+    force = thrust_force_n(config, 0.0)
+
+    assert force.x == pytest.approx(expected_x, abs=1e-12)
+    assert force.y == pytest.approx(expected_y, abs=1e-12)
+
+
+def test_net_acceleration_is_force_sum_divided_by_mass() -> None:
+    config = SimulationConfig(
+        mass_kg=2.0,
+        thrust_n=10.0,
+        launch_angle_rad=0.0,
+        gravity_m_s2=9.81,
+    )
+
+    acceleration = acceleration_m_s2(config, 0.25)
+
+    assert acceleration.x == pytest.approx(5.0, abs=1e-12)
+    assert acceleration.y == pytest.approx(-9.81, abs=1e-12)
+
+
+def test_thrust_uses_exact_half_open_burn_interval() -> None:
+    burn_time_s = 1.0
+    config = SimulationConfig(thrust_n=10.0, burn_time_s=burn_time_s)
+
+    assert thrust_force_n(config, 0.0).magnitude == pytest.approx(10.0, abs=1e-12)
+    assert thrust_force_n(
+        config, math.nextafter(burn_time_s, 0.0)
+    ).magnitude == pytest.approx(10.0, abs=1e-12)
+    assert thrust_force_n(config, burn_time_s).magnitude == 0.0
+    assert thrust_force_n(
+        config, math.nextafter(burn_time_s, math.inf)
+    ).magnitude == 0.0
+    assert thrust_force_n(config, -math.ulp(0.0)).magnitude == 0.0
+
+
+def test_non_finite_force_time_is_rejected() -> None:
+    with pytest.raises(ValueError):
+        thrust_force_n(SimulationConfig(), math.nan)
diff --git a/tests/test_integrator.py b/tests/test_integrator.py
new file mode 100644
index 0000000..9c2d716
--- /dev/null
+++ b/tests/test_integrator.py
@@ -0,0 +1,63 @@
+import pytest
+
+from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+from rocket_sim.physics import semi_implicit_euler
+
+
+def test_semi_implicit_euler_uses_updated_velocity_for_position() -> None:
+    position, velocity = semi_implicit_euler(
+        Vector2(3.0, 0.0),
+        Vector2(2.0, 0.0),
+        Vector2(4.0, 0.0),
+        0.5,
+    )
+
+    assert velocity.x == 4.0
+    assert position.x == 5.0
+
+
+def test_step_crossing_burnout_is_split_at_exact_boundary() -> None:
+    config = SimulationConfig(
+        mass_kg=1.0,
+        thrust_n=10.0,
+        burn_time_s=0.75,
+        launch_angle_rad=0.0,
+        gravity_m_s2=0.0,
+        physics_dt_s=0.5,
+        initial_position_m=Vector2(0.0, 1.0),
+    )
+    simulation = Simulation(config)
+    simulation.launch()
+
+    assert simulation.step()
+    assert simulation.state.time_s == 0.5
+    assert simulation.state.velocity_m_s.x == 5.0
+    assert simulation.state.position_m.x == 2.5
+
+    assert simulation.step()
+    assert simulation.state.time_s == 1.0
+    assert simulation.state.velocity_m_s.x == 7.5
+    assert simulation.state.position_m.x == 6.25
+    assert simulation.state.phase is FlightPhase.COAST
+    assert simulation.state.acceleration_m_s2.x == 0.0
+    assert sum(sample.time_s == 0.75 for sample in simulation.trajectory) == 1
+    transitions = [
+        (before.phase, after.phase)
+        for before, after in zip(
+            simulation.trajectory, simulation.trajectory[1:], strict=False
+        )
+        if before.phase is not after.phase
+    ]
+    assert transitions == [(FlightPhase.POWERED, FlightPhase.COAST)]
+    assert simulation.current_thrust_n == 0.0
+
+
+def test_mass_is_constant_across_powered_coast_and_landing_states() -> None:
+    simulation = Simulation()
+    simulation.launch()
+    for _ in range(1000):
+        if not simulation.step():
+            break
+
+    assert simulation.is_finished
+    assert {sample.mass_kg for sample in simulation.trajectory} == {1.0}
diff --git a/tests/test_rendering.py b/tests/test_rendering.py
new file mode 100644
index 0000000..5130f21
--- /dev/null
+++ b/tests/test_rendering.py
@@ -0,0 +1,70 @@
+import os
+import ast
+from pathlib import Path
+
+os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
+os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
+
+import pygame
+
+from rocket_sim import Simulation, Vector2
+from rocket_sim.app import handle_keydown, run
+from rocket_sim.rendering import Renderer, world_to_screen
+
+
+def test_world_to_screen_inverts_only_vertical_axis() -> None:
+    assert world_to_screen(Vector2(2.0, 3.0), (100.0, 200.0), 10.0) == (120, 170)
+
+
+def test_rendering_does_not_mutate_simulation_state() -> None:
+    pygame.init()
+    try:
+        surface = pygame.Surface((900, 700))
+        simulation = Simulation()
+        simulation.launch()
+        simulation.step()
+        before = (simulation.state, simulation.trajectory)
+
+        Renderer().draw(surface, simulation)
+
+        assert (simulation.state, simulation.trajectory) == before
+    finally:
+        pygame.quit()
+
+
+def test_core_modules_do_not_depend_on_pygame() -> None:
+    package_root = Path(__file__).parents[1] / "src" / "rocket_sim"
+
+    for module_name in ("config.py", "physics.py", "simulation.py"):
+        tree = ast.parse((package_root / module_name).read_text())
+        imported_roots = {
+            alias.name.split(".")[0]
+            for node in ast.walk(tree)
+            if isinstance(node, ast.Import)
+            for alias in node.names
+        }
+        imported_roots.update(
+            node.module.split(".")[0]
+            for node in ast.walk(tree)
+            if isinstance(node, ast.ImportFrom) and node.module
+        )
+        assert "pygame" not in imported_roots
+
+
+def test_keyboard_controls_launch_pause_reset_and_exit() -> None:
+    simulation = Simulation()
+
+    assert handle_keydown(pygame.K_SPACE, simulation)
+    assert simulation.is_running
+    assert handle_keydown(pygame.K_SPACE, simulation)
+    assert simulation.is_paused
+    assert handle_keydown(pygame.K_SPACE, simulation)
+    assert simulation.is_running
+    assert not simulation.is_paused
+    assert handle_keydown(pygame.K_r, simulation)
+    assert simulation.state.time_s == 0.0
+    assert not handle_keydown(pygame.K_ESCAPE, simulation)
+
+
+def test_bounded_dummy_driver_application_smoke() -> None:
+    assert run(max_frames=2) == 0
diff --git a/tests/test_simulation.py b/tests/test_simulation.py
new file mode 100644
index 0000000..eff6166
--- /dev/null
+++ b/tests/test_simulation.py
@@ -0,0 +1,208 @@
+import math
+
+import pytest
+
+from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+
+
+def test_default_flight_lifts_off_and_returns_to_ground_once() -> None:
+    simulation = Simulation()
+    simulation.launch()
+
+    assert simulation.state.phase is FlightPhase.POWERED
+    assert not simulation.is_finished
+    for _ in range(1000):
+        if not simulation.step():
+            break
+
+    assert simulation.is_finished
+    assert simulation.state.phase is FlightPhase.LANDED
+    assert simulation.state.has_lifted_off
+    assert simulation.state.position_m.y == 0.0
+    assert simulation.state.velocity_m_s.y < 0.0
+    final_state = simulation.state
+    final_history = simulation.trajectory
+
+    assert not simulation.step()
+    assert simulation.state == final_state
+    assert simulation.trajectory == final_history
+
+
+def test_ground_crossing_is_linearly_interpolated_on_discrete_segment() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            thrust_n=0.0,
+            burn_time_s=0.0,
+            gravity_m_s2=0.0,
+            physics_dt_s=0.2,
+            initial_position_m=Vector2(2.0, 0.1),
+            initial_velocity_m_s=Vector2(4.0, -1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.state.time_s == pytest.approx(0.1, abs=1e-12)
+    assert simulation.state.position_m == Vector2(2.4, 0.0)
+    assert simulation.state.velocity_m_s == Vector2(4.0, -1.0)
+    assert simulation.is_finished
+
+
+def test_accelerated_ground_crossing_interpolates_impact_velocity() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            thrust_n=0.0,
+            burn_time_s=0.0,
+            gravity_m_s2=2.0,
+            physics_dt_s=0.2,
+            initial_position_m=Vector2(2.0, 0.1),
+            initial_velocity_m_s=Vector2(4.0, -1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.state.time_s == pytest.approx(1.0 / 14.0, abs=1e-12)
+    assert simulation.state.position_m.x == pytest.approx(16.0 / 7.0, abs=1e-12)
+    assert simulation.state.position_m.y == 0.0
+    assert simulation.state.velocity_m_s.x == 4.0
+    assert simulation.state.velocity_m_s.y == pytest.approx(-8.0 / 7.0, abs=1e-12)
+
+
+def test_ground_configuration_that_cannot_lift_off_terminates_without_motion() -> None:
+    simulation = Simulation(
+        SimulationConfig(thrust_n=0.0, burn_time_s=0.0, gravity_m_s2=9.81)
+    )
+
+    simulation.launch()
+
+    assert simulation.is_finished
+    assert simulation.state.time_s == 0.0
+    assert simulation.state.position_m == Vector2(0.0, 0.0)
+    assert not simulation.state.has_lifted_off
+
+
+def test_under_resolved_ground_launch_never_records_negative_altitude() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            thrust_n=0.0,
+            burn_time_s=0.0,
+            gravity_m_s2=9.81,
+            physics_dt_s=0.1,
+            initial_velocity_m_s=Vector2(0.0, 0.1),
+        )
+    )
+
+    simulation.launch()
+
+    assert simulation.is_finished
+    assert simulation.state.time_s == 0.0
+    assert all(sample.position_m.y >= 0.0 for sample in simulation.trajectory)
+
+
+def test_ground_launch_with_downward_velocity_never_penetrates_ground() -> None:
+    simulation = Simulation(
+        SimulationConfig(initial_velocity_m_s=Vector2(0.0, -1.0))
+    )
+
+    simulation.launch()
+
+    assert simulation.is_finished
+    assert simulation.state.time_s == 0.0
+    assert all(sample.position_m.y >= 0.0 for sample in simulation.trajectory)
+
+
+def test_pre_burn_impact_telemetry_keeps_thrust_and_acceleration_consistent() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_n=1.0,
+            burn_time_s=1.0,
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            physics_dt_s=0.2,
+            initial_position_m=Vector2(0.0, 0.1),
+            initial_velocity_m_s=Vector2(0.0, -1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.is_finished
+    assert simulation.state.time_s < 1.0
+    assert simulation.current_thrust_n == 1.0
+    assert simulation.state.acceleration_m_s2 == Vector2(1.0, 0.0)
+
+
+def test_reset_reproduces_state_history_and_clears_fractional_accumulator() -> None:
+    simulation = Simulation()
+    frame_durations = [0.016, 0.017, 0.008, 0.021, 0.013]
+
+    simulation.launch()
+    for elapsed_s in frame_durations:
+        simulation.advance_elapsed(elapsed_s)
+    first_state = simulation.state
+    first_history = simulation.trajectory
+    first_steps = simulation.physics_step_count
+    assert simulation.accumulator_s > 0.0
+
+    simulation.reset()
+    assert simulation.accumulator_s == 0.0
+    assert simulation.physics_step_count == 0
+    assert simulation.state.phase is FlightPhase.READY
+    simulation.launch()
+    for elapsed_s in frame_durations:
+        simulation.advance_elapsed(elapsed_s)
+
+    assert simulation.state == first_state
+    assert simulation.trajectory == first_history
+    assert simulation.physics_step_count == first_steps
+
+
+@pytest.mark.parametrize("elapsed_s", [-0.01, math.nan, math.inf])
+def test_invalid_elapsed_time_is_rejected(elapsed_s: float) -> None:
+    with pytest.raises(ValueError):
+        Simulation().advance_elapsed(elapsed_s)
+
+
+def test_paused_wall_time_does_not_accumulate() -> None:
+    simulation = Simulation()
+    simulation.launch()
+    simulation.advance_elapsed(0.015)
+    simulation.toggle_pause()
+    state = simulation.state
+    accumulator = simulation.accumulator_s
+
+    assert simulation.advance_elapsed(1.0) == 0
+    assert simulation.state == state
+    assert simulation.accumulator_s == accumulator
+
+
+def test_pre_launch_wall_time_is_ignored_and_pause_can_resume() -> None:
+    simulation = Simulation()
+    initial_state = simulation.state
+    initial_history = simulation.trajectory
+
+    assert simulation.advance_elapsed(1.0) == 0
+    assert simulation.state == initial_state
+    assert simulation.trajectory == initial_history
+    assert simulation.accumulator_s == 0.0
+    assert simulation.physics_step_count == 0
+
+    simulation.toggle_pause()
+    simulation.advance_elapsed(0.015)
+    retained_accumulator = simulation.accumulator_s
+    simulation.toggle_pause()
+    assert simulation.is_paused
+    simulation.toggle_pause()
+    assert simulation.is_running
+    assert not simulation.is_paused
+    simulation.advance_elapsed(
+        simulation.config.physics_dt_s - simulation.accumulator_s
+    )
+
+    assert simulation.physics_step_count == 2
+    assert retained_accumulator == pytest.approx(0.005, abs=1e-15)
diff --git a/tests/test_time_accumulator.py b/tests/test_time_accumulator.py
new file mode 100644
index 0000000..c6858cb
--- /dev/null
+++ b/tests/test_time_accumulator.py
@@ -0,0 +1,50 @@
+import math
+
+import pytest
+
+from rocket_sim import Simulation, SimulationConfig
+
+
+def _run_partitioned(total_s: float, fps: int) -> Simulation:
+    simulation = Simulation()
+    simulation.launch()
+    frame_s = 1.0 / fps
+    elapsed_s = 0.0
+    while elapsed_s + frame_s < total_s:
+        simulation.advance_elapsed(frame_s)
+        elapsed_s += frame_s
+    simulation.advance_elapsed(total_s - elapsed_s)
+    return simulation
+
+
+def test_fixed_physics_results_are_independent_of_30_60_144_fps_partitions() -> None:
+    simulations = [_run_partitioned(0.5, fps) for fps in (30, 60, 144)]
+
+    for simulation in simulations:
+        assert simulation.physics_step_count == 50
+        assert simulation.state.time_s == pytest.approx(0.5, abs=1e-12)
+    assert simulations[0].state == simulations[1].state == simulations[2].state
+    assert (
+        simulations[0].trajectory
+        == simulations[1].trajectory
+        == simulations[2].trajectory
+    )
+
+
+def test_zero_elapsed_never_advances_even_with_very_small_valid_timestep() -> None:
+    simulation = Simulation(SimulationConfig(physics_dt_s=1e-15))
+    simulation.launch()
+
+    assert simulation.advance_elapsed(0.0) == 0
+    assert simulation.physics_step_count == 0
+    assert simulation.state.time_s == 0.0
+
+
+def test_representably_subthreshold_elapsed_time_does_not_advance() -> None:
+    dt = 0.01
+    simulation = Simulation(SimulationConfig(physics_dt_s=dt))
+    simulation.launch()
+
+    assert simulation.advance_elapsed(math.nextafter(dt, 0.0)) == 0
+    assert simulation.physics_step_count == 0
+    assert simulation.state.time_s == 0.0
~~~~~~
