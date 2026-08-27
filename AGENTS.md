# Agent Instructions

These instructions apply to the entire repository.

## Required Reading

- Read this file before making repository changes.
- Read `Pygame_Rocket_Simulator_Project_Context.md` before changing simulation behavior, physics assumptions, architecture, milestone scope, units, coordinate conventions, or validation criteria.
- Read `docs/product/PROJECT_UNDERSTANDING.md` before implementation work once that file exists. It should record the current implementation-oriented understanding of the simulator and repository.
- Read relevant records in `docs/decisions/` and relevant subsystem documentation before changing an established physics, architecture, numerical-method, rendering, or workflow decision.
- Inspect the repository and working tree before editing. Documentation can become stale, so verify claims that depend on current code or configuration.

## General Workflow

- Keep changes scoped to the user's current request.
- Do not implement future milestones, placeholder systems, or speculative abstractions unless explicitly requested.
- Do not silently revise previously accepted physics assumptions or architecture decisions. If a decision changes, document the new decision and preserve the prior record.
- Preserve existing behavior unless the task explicitly requests a behavior change, model change, or bug fix.
- Preserve user changes and unrelated existing work. Never absorb unrelated work into a task commit.
- Prefer small, testable milestones and inspect before editing.
- Separate scientific-model changes from presentation/UI changes whenever practical.
- If a proposed change affects numerical correctness, explain the expected physical consequence before implementation.

## Scientific Modeling Policy

- Every simulated force or state transition must have a clearly stated physical meaning.
- Use SI units internally unless a documented decision explicitly says otherwise.
- Keep units explicit in variable names, configuration, documentation, or type structure where practical.
- Do not mix screen coordinates with simulation/world coordinates.
- Do not mix physics timestep with rendering framerate.
- Do not silently introduce empirical constants, tuning factors, or "game feel" adjustments into the physics model.
- If a model is approximate, document the approximation and its expected limits.
- Prefer simple models that can be analytically or numerically validated before adding realism.
- New realism should be introduced one physical effect at a time when practical.
- Do not present simplified 2D results as equivalent to full 3D flight dynamics.
- Do not claim engineering-grade launch prediction without documented calibration, uncertainty analysis, and validation against real data.

## Project Snapshot Policy

- Do not generate or update a full-repository snapshot during normal work.
- Prefer token-efficient historical records containing the user's prompt, implementation commit diff, and concise implementation metadata.
- Do not store entire repository snapshots in prompt records.
- Exclude `.git`, virtual environments, caches, build output, generated plots, replay data, exported frames, and unrelated scratch files from snapshot-style artifacts unless explicitly requested.
- If simulation output is needed for a prompt record, store a concise summary or a small representative artifact rather than large raw datasets unless the dataset itself is the requested result.

## Prompt Archive And Commit Policy

When a user prompt causes any repository file to be created, modified, moved, or deleted:

- Create a corresponding prompt record in `docs/prompts/`.
- Use this filename format:

  ```text
  prompt_[ID]_[scope].md
  ```

- Use the next unused integer ID, zero-padded to two digits.
- Choose the scope that the prompt primarily affects, such as `platform`, `physics`, `rendering`, `motor`, `atmosphere`, `validation`, `experiments`, or `docs`.
- Use `platform` for repository-wide or cross-subsystem work.
- Preserve the user's implementation prompt verbatim. Include material follow-up constraints or approvals that change how the prompt is implemented.
- Record the date/time when practical, relevant context and constraints, decisions made, implementation summary, files created/modified/deleted, validation performed, implementation commit SHA, and the implementation commit diff against its parent.
- Do not reconstruct prompt records for work that predates this policy unless the user explicitly requests it.
- Commit requested implementation or documentation changes first with a concise, descriptive implementation commit.
- Generate that commit's diff against its parent, then complete the prompt record with the commit SHA and diff.
- Commit the prompt record separately.
- If a meaningful durable decision is made, create or update its decision record and ensure it is committed as documentation, normally with the implementation it explains.
- Never include unrelated pre-existing work in either commit.
- Push when a remote exists and doing so is appropriate for the repository workflow. If no remote exists, record that no push was performed.
- If unrelated changes make a safe path-scoped commit impossible, stop and explain the specific conflict rather than modifying, unstaging, or absorbing those changes.

## Routine Commit Policy

Once the user has approved a task or instructed Codex to implement it, routine commits are part of the normal workflow and do not require separate conversational approval.

- Make the requested changes, run appropriate validation, review the resulting diff, and commit the implementation directly.
- Create or update required prompt and decision records and commit them according to this policy.
- Use sufficiently descriptive commit messages that identify the purpose and scope of the change.
- Prefer messages such as:
  - `Initialize Pygame rocket simulator repository`
  - `Implement gravity and powered point-mass flight`
  - `Add aerodynamic drag model and tests`
  - `Add motor thrust-curve interpolation`
  - `Separate simulation timestep from rendering framerate`
  - `Add analytical trajectory validation`
- Avoid vague messages such as `changes`, `update`, `fix stuff`, `misc`, or `work`.
- For larger changes, use a concise subject and a useful body describing important physics, architecture, data, or validation implications.
- Run non-destructive bookkeeping such as `git status`, `git diff`, `git add`, `git commit`, and `git log` without asking for separate conversational approval during an already-approved task.
- This policy does not authorize destructive Git commands, discarding or overwriting user work, rewriting published history, force pushing, committing unrelated changes, or silently expanding task scope.

## Repository Push Workflow

The canonical remote for this repository is:

```text
https://github.com/eugenelin89/rocketsim.git
```

For an approved task that changes repository files, the normal completed-task workflow is:

```text
implement
→ validate
→ implementation commit
→ record implementation SHA + parent diff in the prompt record
→ prompt-record commit
→ push completed commits to origin/main
```

Once `origin` is established, routine completed task commits and their required prompt records should be pushed to `origin/main` without requiring separate conversational approval for each push. A push may be omitted only for a concrete blocker such as authentication, connectivity, permission, remote conflict, or unsafe unrelated repository state. Preserve local commits and report the exact blocker.

This workflow does not authorize force pushing, destructive Git operations, rewriting published history, discarding user work, or committing unrelated changes.

## Decision Archive

- Record meaningful durable project decisions in `docs/decisions/`.
- Use this filename format:

  ```text
  decision_[ID]_[short_slug].md
  ```

- Each record must include the decision, date, status (`accepted`, `superseded`, or `reversed`), context/problem, options considered when relevant, rationale, consequences/tradeoffs, related prompt records, and any superseding decision.
- Create a decision record when a choice materially constrains:
  - coordinate conventions
  - internal units
  - numerical integration method
  - timestep strategy
  - force-model semantics
  - rocket state representation
  - atmospheric model
  - motor model
  - collision/ground-contact behavior
  - logging/data format
  - experiment reproducibility
  - architecture boundaries
  - development workflow
- Do not create decision records for every transient coding detail.
- Decision history is append-preserving. When a decision changes, keep the previous record and mark or link it as superseded or reversed instead of erasing it.

## Architecture Boundaries

- The Pygame application layer owns:
  - window creation
  - input handling
  - drawing
  - HUD/UI
  - camera transforms
  - visualization of trajectories and vectors
  - display timing

- The physics core owns:
  - rocket state
  - force calculations
  - integration
  - environment state needed for physics
  - motor state needed for physics
  - event/state transitions such as ignition, burnout, apogee, landing, or parachute deployment when introduced

- The physics core should remain independent of Pygame wherever practical.
- Physics modules must not depend on screen resolution, pixels, fonts, or display coordinates.
- Simulation state should use world coordinates and SI units.
- Rendering should transform world state into screen coordinates at the UI boundary.
- The simulation clock and physics timestep must remain independent from Pygame's display FPS.
- Configuration/data loading should be separated from force calculations.
- Motor models should be interchangeable behind a clear interface once more than one motor model exists.
- Atmospheric models should be replaceable without rewriting rocket dynamics.
- Experiment and batch-run code should be able to run headlessly without opening a Pygame window.
- Do not introduce ECS, plugin systems, networking, cloud services, databases, or large frameworks unless an approved milestone requires them.

## Implementation Style

- Favor small components with focused responsibilities and testable interfaces.
- Keep equations readable and close to their documented physical form.
- Prefer named dataclasses or domain objects over unstructured dictionaries for durable simulation state.
- Avoid "magic numbers." Put physical constants and configuration values in named locations.
- Keep vectors explicit and consistent.
- If using `pygame.Vector2`, confine Pygame-specific vector usage to boundaries where practical; otherwise use a neutral project vector representation or simple numerical structure.
- Prefer deterministic simulations for the same configuration unless stochastic behavior is explicitly part of an experiment.
- Seed random number generators in experiments that use randomness.
- Preserve raw simulation outputs needed to reproduce derived metrics when practical.
- Do not optimize prematurely. Correctness and clarity come before micro-optimization.
- Do not add third-party dependencies without a clear, current need.
- Avoid broad formatting, renaming, or refactoring unrelated to the current task.

## Numerical Integration

- The initial project should use a documented fixed physics timestep.
- Rendering FPS must not alter simulation results.
- If Euler, semi-implicit Euler, RK4, or another integrator is used, document the choice and validation.
- Run timestep-convergence tests when adding forces whose error may be timestep-sensitive.
- Do not silently change the integrator or default timestep.
- When numerical instability appears, diagnose the physical model and timestep before adding arbitrary clamps.
- Clamps or limits that represent real physical constraints must be documented as such.

## Coordinate System And Units

Unless superseded by a decision record:

- use SI units internally
- position: meters
- velocity: meters per second
- acceleration: meters per second squared
- force: newtons
- mass: kilograms
- time: seconds
- angle: radians internally, degrees only for display/configuration when convenient
- world +x: horizontal/right
- world +y: upward
- gravity acts in -y
- screen-coordinate inversion belongs only in rendering

If a different convention is adopted, document it before implementation.

## Repository Tooling

Recommended baseline:

- Python 3.12 or a clearly documented supported Python version
- Pygame for interactive visualization
- `pytest` for automated tests
- standard library `dataclasses`, `math`, `csv`, `json`, and `pathlib` where sufficient
- optional NumPy only when a real numerical need emerges

## Python Environment Policy

- Development must use an isolated Python 3.12 environment with its own pip capable of installing the project from `pyproject.toml`.
- On the primary development machine, use the Miniconda environment named `rocketsim`, created with:

  ```bash
  conda create -n rocketsim python=3.12 pip
  ```

- Do not use Conda `base` as the project environment, and do not nest a Python `venv` inside the `rocketsim` Conda environment.
- `pyproject.toml` is the canonical package and dependency configuration. Install the project into the active isolated environment with:

  ```bash
  python -m pip install -e ".[dev]"
  ```

- Prefer `python -m pip` to a bare `pip` command so installation uses the selected interpreter.
- Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`, when supported normally by their machine.
- Project validation must make interpreter provenance clear. On the primary development machine, automated commands should preferably use `conda run -n rocketsim python ...`.
- Do not install repository dependencies into Conda `base`, system Python, Homebrew Python, or user-global Python.

Suggested repository structure:

```text
pygame-rocket-sim/
├── src/
│   └── rocket_sim/
│       ├── app/
│       ├── physics/
│       ├── models/
│       ├── motors/
│       ├── environment/
│       ├── rendering/
│       ├── experiments/
│       └── config/
├── tests/
├── docs/
│   ├── product/
│   ├── prompts/
│   └── decisions/
├── data/
│   └── motors/
├── scripts/
├── examples/
├── README.md
├── AGENTS.md
└── Pygame_Rocket_Simulator_Project_Context.md
```

Do not restructure an established repository solely to match this illustrative tree.

## Documentation

- `Pygame_Rocket_Simulator_Project_Context.md` is the primary high-level product, scientific, and milestone document.
- `AGENTS.md` defines repository-wide agent, workflow, history, physics-discipline, and validation rules.
- `docs/product/PROJECT_UNDERSTANDING.md` should record the current implementation-oriented understanding of the simulator and repository once implementation begins.
- `docs/prompts/` contains historical implementation prompts and resulting change records. Prompt records describe what was known and requested at the time and must not be rewritten to reflect later knowledge.
- `docs/decisions/` contains durable scientific, numerical, product, and architecture decisions.
- Keep implementation-facing documentation consistent with meaningful code and structure changes.
- Update equations and assumptions when the implemented model changes.

## Testing And Validation

Physics changes require validation appropriate to the model.

### Minimum validation expectations

- Run unit tests for changed equations and state transitions.
- Compare simplified cases against analytical solutions whenever one exists.
- Confirm simulation results do not depend materially on display FPS.
- Run timestep-convergence checks for meaningful dynamics changes.
- Check dimensions/units of newly introduced equations.
- Validate zero-force, zero-thrust, zero-drag, and other limiting cases when relevant.
- Run `git diff --check` before finishing when practical.

### Examples

For gravity-only projectile motion:

```text
x(t) = x0 + vx0 * t
y(t) = y0 + vy0 * t - 0.5 * g * t^2
vy(t) = vy0 - g * t
```

For constant thrust with constant mass and fixed thrust direction, compare against constant-acceleration analytical results during powered flight.

For drag models:

- verify drag is zero at zero air-relative speed
- verify drag opposes air-relative velocity
- verify drag magnitude scales with v^2 for the quadratic model

For variable mass:

- verify mass never drops below dry mass
- verify propellant depletion and burnout timing
- verify thrust becomes zero after burnout unless the selected motor model says otherwise

For atmosphere:

- verify density remains positive
- verify sea-level values match documented assumptions
- verify altitude behavior is monotonic over the intended range when using a simple atmosphere model

### Physical-Data Validation

When the project begins comparing against real rocket flights:

- record the source and quality of measured data
- distinguish calibration data from evaluation data
- document sensor uncertainty and timing uncertainty
- do not tune and evaluate on the same run without saying so
- preserve the configuration used for every comparison

## What Not To Build Yet

Unless explicitly requested, do not add:

- 3D graphics
- full 6-DOF rigid-body dynamics
- CFD
- structural simulation
- combustion simulation
- launch-control hardware
- telemetry radio integration
- cloud accounts or backend
- multiplayer/networking
- machine learning
- swarm simulation
- autonomous guidance
- optimization/search over rocket designs
- engineering certification or safety claims

These may become future research directions, but the first objective is a trustworthy, understandable 2D rocket simulator.

## Completion Reporting

When finishing an implementation task, report:

1. what changed
2. what physics/model behavior changed, if any
3. files created or modified
4. validation performed
5. validation not performed and why
6. important assumptions or limitations
7. implementation commit SHA
8. prompt/decision records created
9. whether the remote was pushed
