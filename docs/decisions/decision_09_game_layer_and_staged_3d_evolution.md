# Decision 09: Game layer and staged 3D evolution

- Date: 2026-09-19
- Status: accepted
- Supersedes: none

## Decision

RocketSim may evolve into a fun mission-based game, but gameplay must be layered on top of the validated simulator rather than silently altering physical behavior.

The architectural direction is:

```text
validated physics simulation
        ↓
flight/result data
        ↓
mission evaluation and scoring
        ↓
game presentation, feedback, progression, and effects
```

Game systems may observe simulation state and results, restrict which already-supported setup parameters a mission allows the player to edit, define objectives, score outcomes, present hints, trigger sounds or visual effects, and track progression. They must not secretly change thrust, gravity, drag, trajectory, timing, impact, or other validated physics to make a mission easier or more dramatic.

Difficulty should normally change information, constraints, hints, attempts, or scoring—not the governing physics.

## Near-term game direction

The preferred next product milestone is Mission Mode and Flight Results.

Mission Mode should reuse the current Prompt 05 laboratory and add a thin game layer built from deterministic simulation outputs. Candidate mission objectives include:

- reach a target altitude;
- land within a horizontal target zone;
- carry at least a specified payload mass;
- keep impact speed below a threshold;
- minimize peak drag while satisfying another objective;
- satisfy several simultaneous engineering constraints.

A mission may expose only the subset of current setup controls relevant to its learning goal. For example, a landing-target mission may let the player change launch direction while keeping the motor and environment fixed.

Scoring should be derived from physically meaningful outputs such as:

- apogee;
- landing position;
- impact speed;
- maximum speed;
- maximum acceleration;
- maximum drag;
- flight time;
- configured payload/mass;
- objective completion.

The physics core should not know about points, stars, achievements, campaigns, target zones, or progression.

## Presentation and game feel

RocketSim may add game-like presentation without changing simulation state, including:

- countdowns;
- mission HUD and live objective status;
- target zones and landmarks;
- launch, burnout, apogee, landing, success, and failure feedback;
- camera motion;
- trajectory styling;
- particles, smoke, exhaust, and screen effects;
- audio tied to production quantities such as normalized thrust;
- results screens, retry flow, stars, scores, and progression.

These remain presentation/game-layer behavior.

A NO LIFTOFF, overshoot, hard landing, or missed target should remain the actual simulation outcome; the game may explain it more clearly but must not correct it invisibly.

## 3D strategy

3D presentation and 3D physics are separate milestones.

### Stage 1 — Mission game in the existing validated 2D simulator

Build missions, objectives, scoring, flight results, target zones, feedback, and retry/progression while retaining current 2D point-mass physics.

### Stage 2 — Run comparison and experiment history

Allow learners/players to compare deterministic runs, trajectories, and mission metrics without changing the physical model.

### Stage 3 — 2.5D / 3D-style presentation prototype

Explore a more game-like scene with perspective, richer terrain/backgrounds, a 3D-looking rocket, camera follow, particles, and other presentation effects while the underlying physical trajectory remains the validated current model.

Any rocket orientation shown at this stage must be clearly presentation or fixed-thrust-direction visualization, not simulated rotational attitude.

### Stage 4 — True 3D rendering, if the prototype proves valuable

A later approved milestone may migrate or extend presentation technology to a genuine 3D renderer. This is a rendering/product decision and must not by itself redefine the simulation equations.

The project should reassess whether Pygame remains appropriate before committing to a major 3D rendering stack. A migration to Panda3D, Godot, Unity, ModernGL/PyOpenGL, or another technology requires a separate architecture decision; none is selected by this decision.

### Stage 5 — True 3D flight physics only as a separate scientific program

Full 3D physics is not a cosmetic conversion of the current simulator. It would require separately defining and validating some or all of:

- 3D position and velocity;
- body/world coordinate transforms;
- orientation;
- angular velocity;
- torque;
- moments of inertia;
- thrust direction relative to attitude;
- aerodynamic force direction and attitude dependence;
- center of mass / center of pressure;
- rotational and aerodynamic stability;
- 3D wind and air-relative velocity;
- new integration and event semantics.

True 3D physics therefore must be introduced only through explicit later scientific milestones with independent review and validation. It must not be smuggled into a graphics milestone.

## Modes

The long-term product may support three complementary modes:

- **Sandbox** — current laboratory-style free experimentation.
- **Missions** — objective/constraint/scoring gameplay using the same physics.
- **Science Lab** — structured prediction → experiment → observation → explanation activities tied to the Living Rocketry Course.

The same authoritative simulator should underpin all modes.

## Progression philosophy

Progression should unlock engineering tools, experiments, information, environments, or newly implemented physical systems—not arbitrary hidden performance bonuses.

For example, later approved progression might unlock:

- more setup controls;
- alternative validated motors;
- wind tools after wind is implemented;
- recovery controls after recovery is implemented;
- guidance controls after guidance is implemented.

Avoid arcade upgrades such as unexplained “+20% thrust” unless they correspond to an explicit, visible configuration or modeled physical change.

## Rationale

Prompt 05 made RocketSim experimentally usable. A game layer can now create motivation, replayability, and engineering challenges without weakening scientific integrity.

Building Mission Mode before true 3D has several advantages:

- it tests whether the core gameplay loop is fun before a graphics-engine migration;
- it reuses the validated simulator immediately;
- it creates a clean result/mission boundary useful for later 2D, 2.5D, or 3D presentation;
- it keeps future 3D rendering independent from future 3D physics;
- it turns new validated physics into future game mechanics rather than requiring physics compromises for entertainment.

## Consequences

- Mission/game code must remain outside the authoritative physics calculations.
- Game scoring must consume production simulation outputs.
- Existing Sandbox behavior remains available.
- Missions may constrain player choices but may not secretly alter physical outcomes.
- Living Rocketry Course updates remain required when learner-facing workflow changes.
- Prompt 06 should preferentially implement Mission Mode and Flight Results, with no new physical model.
- A 2.5D/3D presentation milestone should come only after the mission/game loop is proven useful.
- Full 3D flight dynamics remain a substantially later scientific undertaking requiring explicit approval.

## Prompt 06 implementation clarification

Prompt 06 implements the first mission layer described here. The existing `mass_kg` remains one total constant vehicle mass; RocketSim still has no separate payload, dry-mass, or propellant-mass model. Therefore the shipped Heavy Lift mission and score use “configured constant mass,” not the earlier candidate shorthand “payload.” A future true payload objective requires an explicit approved mass model.

## Superseding decision

None.
