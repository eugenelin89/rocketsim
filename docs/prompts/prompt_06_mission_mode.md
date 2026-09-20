# Prompt 06 — Mission Mode and Flight Results

- Date completed: 2026-09-19
- Scope: mission game layer, completed-flight metrics, scoring, progression, and learning workflow
- Starting commit: `fddeebbc11c05ac4f907bf3888facf6373b801c5`
- Implementation parent: `fddeebbc11c05ac4f907bf3888facf6373b801c5`
- Implementation commit: `88106787a88dd37fb4e8fefea1d60eebd307d770`
- Implementation message: `Add mission mode and flight results`
- Prompt-record commit: this file's containing commit; resolve with `git log -1 --format=%H -- docs/prompts/prompt_06_mission_mode.md`
- Zero-context implementation-diff SHA-256: `bd1037ffbb8d7370e5844857c3b6e5ef89cb05ae67ce1230c6ce5f60b50ac772`
- Exact patch recovery: `git show --no-ext-diff --binary --format= 88106787a88dd37fb4e8fefea1d60eebd307d770`
- Digest reproduction: `git show --no-ext-diff --binary --unified=0 --format= 88106787a88dd37fb4e8fefea1d60eebd307d770 | shasum -a 256`

## Starting state

The expected baseline was verified rather than assumed. Branch `main`, local `HEAD`, `origin/main`, and remote `refs/heads/main` all agreed at `fddeebbc11c05ac4f907bf3888facf6373b801c5`; the worktree was clean. That baseline includes Decision 09 and the approved staged game/3D roadmap. The isolated environment was Python `3.12.14` at `/Users/eugenelin/.conda/envs/rocketsim/bin/python`. The complete baseline suite reported `211 passed`.

## Reconciled implementation contract

Prompt 06 adds a one-way game layer without changing the validated model:

```text
validated Simulation
        -> immutable FlightResult
        -> explicit Mission evaluation
        -> objective outcomes + deterministic score/stars
        -> GameSession progression
        -> Pygame presentation
```

`FlightResult` is terminal-only and captures the completed run's immutable `SimulationConfig`. It distinguishes `LANDED` from `NO_LIFTOFF`; no-liftoff contact position and impact speed are unavailable rather than zero-filled. Apogee, maximum speed, maximum acceleration, and maximum drag are recorded-state numerical extrema, not exact continuous-flight extrema. Impact speed is total pre-contact ground-frame speed, not impact deceleration.

The current `mass_kg` remains one total constant vehicle mass, not payload. Decision 09 now records that Prompt 06 clarification. Countdown time is presentation-only. Missions never steer, snap, scale thrust, alter gravity/drag, change the motor/timestep, or fabricate an outcome.

## Review matrix and Decision 08 efficiency evidence

| Classification | Specialist | Minimum sufficient review context |
| --- | --- | --- |
| CORE | `test_reviewer` | Result provenance, objective/scoring rules, config restrictions, GameSession paths, mission/app/rendering tests, focused/full evidence, and current diff |
| CORE | `learning_reviewer` | Mission progression/hints/results, production reachability values, visual views, course changes, and mass/contact limitations |
| FOCUSED | `physics_reviewer` | Result/config/game seams, recorded metric semantics, countdown, target boundary, equivalence tests, and relevant docs |
| NOT REQUIRED | `numerical_reviewer` | No integrator, timestep, interpolation, convergence, event-time, or tolerance change |
| NOT REQUIRED | `propulsion_reviewer` | No thrust curve, impulse, burn timing, motor data, or propulsion behavior change |
| NOT REQUIRED | `aerodynamics_reviewer` | No drag equation, air-relative velocity, density model, area, or coefficient semantic change |

The parent owned all implementation and integration. Reviewers were read-only. Current authoritative sources and changed domain seams were used instead of historical prompt rereading. Validation was staged: baseline complete suite, focused result/game/UI groups, integrated suite, reviewer-required focused evidence, affected tests after fixes, and a final complete suite. Only specialists whose domains were classified CORE or FOCUSED were invoked. Selective resolution re-reviews were requested only for the findings they raised; no blanket re-review occurred.

## Specialist findings and resolutions

### Pre-implementation

- `physics_reviewer` found the proposed boundary sound and required absent contact/impact values for `NO_LIFTOFF`, recorded-extrema wording, total pre-contact speed semantics, total-constant-mass wording, positive-gravity shipped missions, complete restriction paths, and one terminal simulation snapshot. All were incorporated.
- `learning_reviewer` blocked the candidate “payload” terminology because no payload model exists. Mission 3 became **Heavy Lift Challenge** using configured constant vehicle mass. It also required ground-contact rather than safety claims, non-monotonic aerodynamic/environmental target bands, an explicit low-gravity baseline comparison, epistemically pending terminal objectives, and retroactive Sandbox/course wording. All were incorporated.
- `test_reviewer` required terminal provenance/nonmutation, independently checked drag, captured-config scoring, full restriction-bypass coverage, successful/failing production evidence for every mission, terminal Sandbox equivalence, one-time finalization, exact score boundaries, and full navigation/render sourcing tests. Those requirements shaped the implementation and test suite.

### Post-implementation and selective resolution

- `test_reviewer` found three IMPORTANT gaps: NaN/infinite elapsed time could mutate countdown before raising; contact/apogee-accuracy formulas lacked independent numerical evidence; and results buttons had not traversed the real mouse/dispatcher path. Validation is now atomic before any countdown mutation, all score metrics have center/edge/clamp evidence, and Retry/Next/Missions/Sandbox are exercised through production routing. It also confirmed complete terminal and no-liftoff Sandbox equivalence. Selective re-check passed.
- `learning_reviewer` found two BLOCKING issues: the guided Precision Landing activity did not first unlock Mission 2, and results omitted a causal physics explanation. Lesson 11 now begins by completing First Flight, and results show a wrapped, labeled mission-specific physics explanation. It also required the full altitude band and exact score interpolation wording. Selective re-review passed.
- `physics_reviewer` found one IMPORTANT presentation issue: Environmental Challenge collapsed an inclusive apogee band to a midpoint line. The renderer now transforms both exact world-y bounds through the shared transform and displays a visible bracket. Selective re-review passed.

No specialist had an unresolved BLOCKING or IMPORTANT finding at implementation commit.

## Implementation summary

- Added Pygame-independent `FlightOutcome`, `FlightResult`, objective, scoring, evaluation, and five-mission domain types.
- Added a Pygame-independent `GameSession` for mode/view state, presentation-only countdown, restrictions, terminal finalization, retry, best results, and sequential in-memory unlocks.
- Preserved Sandbox and routed both modes through ordinary authoritative `Simulation` instances.
- Added Mission Select, brief, restricted configuration, world targets, live objective HUD, success/failure results, Retry, Next, Missions, and Sandbox navigation.
- Added deterministic 500-point mandatory plus 0–500-point physical-performance scoring and 500/750/900 star thresholds.
- Added result, evaluation, restriction, reachability, equivalence, state-machine, event-routing, target, HUD, result, and render-nonmutation tests.
- Revised README, architecture, milestones, validation, product understanding, Decision 09, and the Living Rocketry Course.

## Shipped missions and production reachability

| Mission | Allowed variable | Representative success | Representative failure |
| --- | --- | --- | --- |
| First Flight | constant vehicle mass | `1.0 kg`: apogee `8.1031495 m`, score `513` | `1.1 kg`: apogee `6.1481031 m` |
| Precision Landing | fixed thrust direction | `60 deg`: contact `x=18.1176548 m`, score `985` | `55 deg`: contact `x=19.1239115 m` |
| Heavy Lift Challenge | constant vehicle mass | `1.3 kg`: apogee `3.5667906 m`, score `1000` | `1.4 kg`: `NO_LIFTOFF` |
| Aerodynamic Challenge | constant `Cd` | `Cd=0.60`: contact `x=14.1232880 m`, score `942` | `Cd=1.00`: contact `x=13.7604330 m` |
| Environmental Challenge | mass at fixed `g=3.71 m/s^2` | `1.2 kg`: apogee `21.2114726 m`, score `904` | `1.0 kg`: apogee `30.2825187 m` |

Each mission also has automated inclusive boundary evidence and an allowed failing case. Mission 4 and Mission 5 use bands so blindly clicking to one parameter bound does not solve them. The low-gravity mission explicitly compares the same `1.0 kg` configuration against the default-gravity `8.1031495 m` result and does not claim a complete planet model.

## Files in the implementation commit

Created:

- `src/rocket_sim/game.py`
- `src/rocket_sim/missions.py`
- `tests/test_mission_ui.py`
- `tests/test_missions.py`

Modified:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/VALIDATION.md`
- `docs/decisions/decision_09_game_layer_and_staged_3d_evolution.md`
- `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md`
- `docs/product/PROJECT_UNDERSTANDING.md`
- `src/rocket_sim/__init__.py`
- `src/rocket_sim/app.py`
- `src/rocket_sim/rendering.py`
- `src/rocket_sim/setup.py`
- `tests/test_rendering.py`

The authoritative physics, numerical integration, simulation lifecycle, propulsion, and aerodynamic source files were not changed.

## Automated and quantitative validation

- Python: `3.12.14`; interpreter: `/Users/eugenelin/.conda/envs/rocketsim/bin/python`.
- Final focused Prompt 06 mission/setup/rendering group: `113 passed`.
- Final complete suite: `261 passed`.
- `python -m compileall -q src tests`: passed.
- `import rocket_sim` and five-mission catalog assertion: passed.
- Bounded dummy-SDL application run: passed.
- `git diff --check`: passed before commit.
- Every shipped mission has a production successful and failing configuration.
- Mission/Sandbox angled active-drag runs match exactly at terminal state, complete trajectory, step count, forces, impulse, and result provenance for identical post-ignition elapsed partitions.
- Mission/Sandbox no-liftoff runs match exactly.
- Countdown-only time leaves state, trajectory, accumulator, and step count unchanged; a boundary-crossing frame advances only its post-ignition remainder.
- Maximum drag is checked against the independent literal `0.5 rho Cd A speed^2` oracle rather than the production helper.

## Visual and interaction validation

Six production-rendered `1200x720` frames were visually inspected: mission selection, brief, restricted configuration, live HUD/target, successful results, and failed results. A corrected Environmental Challenge frame separately verified the visible two-bound apogee bracket. Text, editable/fixed styling, objectives, score components, physics explanation, terminal metrics, navigation, target highlighting, Inspector, and motor timeline remained readable.

Automated tests exercised real Pygame mouse-event/dispatcher paths and repeated rendering nonmutation. A bounded dummy-SDL app run passed. Physical manual mouse/keyboard interaction was not performed and is not claimed; audio was optional and was not added.

## Living Rocketry Course result

Lessons 1–10 now explicitly use Sandbox. Lesson 11 teaches the engineering loop:

```text
Predict -> identify the allowed variable and fixed constraints
        -> launch unchanged production physics
        -> inspect objective/result evidence
        -> explain through implemented equations
        -> iterate purposefully
```

The course states that scoring evaluates rather than changes physics, distinguishes total constant mass from payload, limits “landing” to interpolated ground contact, explains pending versus knowable live outcomes, uses a reproducible Precision Landing activity, and adds a controlled default-gravity versus fixed-low-gravity comparison.

## Scope and efficiency audit

No new physical effect, equation, integration behavior, event semantic, motor behavior, dependency, GUI framework, disk persistence, accounts, networking, 2.5D/3D, variable mass, propellant depletion, motor editing/import, wind, atmosphere variation, rotation/stability, recovery, guidance, automatic optimization, run-history comparison, or Prompt 07 work was added.

The implementation uses two small Pygame-independent domain/session modules, the established typed action path, the existing `SimulationConfig` adjustment path, and the existing world transform. No scripting engine, plugin system, database, or second approximate configuration was introduced. Specialist context was limited to changed/relevant seams and quantitative evidence; scientific independence was preserved by literal test oracles and independent specialist review.

## Approved implementation prompt (verbatim)

# Prompt 06 — Mission Mode and Flight Results

Work in:

```text
/Users/eugenelin/dev/cwsf2027/rocketsim
```

Canonical repository:

```text
https://github.com/eugenelin89/rocketsim.git
```

This is **Prompt 06**.

Expected current pushed `main` at the start of this prompt:

```text
fddeebbc11c05ac4f907bf3888facf6373b801c5
```

Verify rather than assuming it.

Prompt 05 completed the interactive pre-launch laboratory.

Decision 08 defines the context-efficient agent/review workflow.

Decision 09 defines the approved game and staged-3D direction.

## Goal

Turn RocketSim into a genuinely fun mission-based engineering game **without changing the validated physics model**.

Prompt 06 should add:

```text
Sandbox
+
Mission Mode
+
Flight Results
+
Objectives
+
Scoring / stars
+
Target zones
+
Mission HUD
+
Results / retry flow
```

The same authoritative simulation must drive Sandbox and Mission Mode.

No new physical effect is introduced.

Do not begin 2.5D/3D rendering, true 3D physics, variable mass, wind, recovery, or Prompt 07 work.

Use **High reasoning** by default.

---

## 1. Repository and environment gate

Inspect:

```bash
git status
git branch -vv
git log --oneline --decorate -n 10
git ls-remote origin refs/heads/main
```

Require:

* branch `main`;
* clean working tree;
* local/upstream/remote agreement.

Verify:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -m pytest
```

Expected prior complete suite is approximately `211 passed`; use the actual result.

Read the minimum current authoritative context required by Decision 08:

```text
AGENTS.md
Decision 08
Decision 09
README.md
docs/ARCHITECTURE.md
docs/PHYSICS_MODEL.md
docs/VALIDATION.md
docs/MILESTONES.md
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
current app/rendering/setup/simulation code
relevant tests
```

Do not reread all historical prompt records unless genuinely necessary.

---

# 2. Non-negotiable architectural rule

Implement this pipeline:

```text
validated Simulation
        ↓
FlightResult
        ↓
Mission evaluation
        ↓
Score / objective status
        ↓
Game presentation
```

Mission/game code may **observe and evaluate** simulation output.

Mission/game code must not secretly modify:

* thrust;
* impulse;
* mass during a run;
* gravity;
* drag;
* integration;
* ground events;
* trajectory;
* impact;
* simulation clock;
* physics timestep.

The physics core must not know about:

* points;
* stars;
* achievements;
* missions;
* target zones;
* campaign progression.

Difficulty and scoring must never apply hidden physical assistance.

---

# 3. Preserve Sandbox

The existing Prompt 05 laboratory remains available as:

```text
SANDBOX
```

Sandbox should retain its current behavior.

Add a simple mode choice such as:

```text
SANDBOX
MISSIONS
```

Do not make Mission Mode replace the laboratory.

---

# 4. Add Pygame-independent FlightResult

Introduce the smallest clean representation for completed-run metrics.

A module such as:

```text
src/rocket_sim/missions.py
```

or a similarly appropriate game-domain module is acceptable.

A `FlightResult` should derive its values from the completed production simulation/history and contain useful physical outcomes such as:

```text
outcome
apogee_m
landing_x_m
impact_speed_m_s
max_speed_m_s
max_acceleration_m_s2
max_drag_n
flight_time_s
liftoff_occurred
configured mass
```

Add other metrics only where missions need them.

Clearly define exceptional outcomes such as:

```text
NO_LIFTOFF
LANDED
```

Do not fabricate a landing result when the simulation did not land.

Result extraction must not mutate the simulation.

---

# 5. Mission domain model

Create a small immutable/Pygame-independent mission representation.

Conceptually:

```text
Mission
    id
    title
    description
    allowed_setup_fields
    fixed/base configuration
    objectives
    scoring rules
    learning hint

MissionObjective
    description
    evaluate(FlightResult / config)

MissionEvaluation
    objective outcomes
    score
    stars
    success/failure
    useful explanatory feedback
```

Do not build a generic scripting engine, plugin system, database, or JSON schema framework.

Keep the first mission system explicit and inspectable.

---

# 6. Mission configuration restrictions

A mission may allow the player to change only selected existing Prompt 05 setup quantities.

Examples:

```text
mass
fixed thrust direction
Cd
reference area
air density
gravity
```

Mission setup should clearly distinguish:

```text
YOU MAY CHANGE
FIXED FOR THIS MISSION
```

Use the same production `SimulationConfig`.

Do not create a second approximate physical configuration.

The motor remains the same validated synthetic motor unless a mission explicitly uses another already-supported validated configuration.

Prompt 06 should not add motor editing.

---

# 7. Initial mission set

Implement a **small polished set**, preferably 4–5 missions.

Do not optimize for quantity.

Candidate progression:

### Mission 1 — First Flight

Teach the mission loop.

Example goal:

```text
Reach a specified minimum altitude.
```

Expose only a simple relevant parameter such as mass.

---

### Mission 2 — Precision Landing

Goal:

```text
Land inside a horizontal target zone.
```

Primary adjustable parameter:

```text
fixed thrust direction
```

This should visually show the target zone in world coordinates.

Prompt 05 evidence suggests a 60° run lands near `x = 18.118 m`; use actual production runs to choose a fair target.

---

### Mission 3 — Payload Challenge

Goal:

```text
Carry as much mass as possible
while still reaching a required altitude.
```

This should reward a genuine tradeoff rather than simply “use minimum mass.”

---

### Mission 4 — Aerodynamic Challenge

Use an intentionally educational fixed environment/configuration and allow an aerodynamic parameter such as `Cd` or area to matter visibly.

Require some useful flight objective so the optimal choice is connected to the physics.

---

### Mission 5 — Environmental Challenge

Optionally use an already-supported alternate gravity or density environment.

Do not add new atmosphere/wind physics.

The mission should demonstrate that the same rocket behaves differently when an existing modeled environmental constant changes.

---

## Mission validation requirement

The exact thresholds above are suggestions, not hardcoded truth.

Before finalizing each mission:

1. run the production simulation;
2. demonstrate that the mission is achievable within allowed setup bounds;
3. demonstrate that failure is also possible;
4. avoid a trivially automatic solution;
5. document representative successful values.

Do not invent mission thresholds solely from visual intuition.

---

# 8. Scoring

Make scoring simple, deterministic, explainable, and tied to physical outcomes.

A mission can award points for quantities such as:

```text
objective completion
landing accuracy
payload mass
impact safety
altitude accuracy
efficiency against the mission criterion
```

Avoid arbitrary opaque formulas.

The results screen should explain where the score came from.

Example:

```text
MISSION COMPLETE

Landing error          0.62 m    +700
Payload                1.20 kg   +240
Safe impact                       +200
Objective bonus                   +300

TOTAL                            1440

★★★
```

Exact numbers/formulas are implementation choices, but tests must make them deterministic.

Three-star scoring is encouraged:

```text
★
★★
★★★
```

Define thresholds clearly.

---

# 9. No physics-based cheating

Explicitly prohibit game code that:

* steers the rocket toward a target;
* modifies gravity near the target;
* increases/decreases drag for difficulty;
* adjusts thrust based on mission state;
* alters impact velocity;
* changes timestep;
* snaps the rocket into a landing zone;
* awards a physically false result.

A missed target remains missed.

A NO LIFTOFF remains NO LIFTOFF.

The game may provide a useful explanation and a Retry button.

---

# 10. Mission UI

Create a coherent game loop:

```text
MISSION SELECT
      ↓
MISSION BRIEF
      ↓
CONFIGURE
      ↓
LAUNCH
      ↓
LIVE OBJECTIVES
      ↓
RESULTS
      ↓
RETRY / NEXT / MISSIONS / SANDBOX
```

Keep it within the current Pygame architecture.

Do not add a new GUI framework.

---

# 11. Mission selection

Provide a readable mission-selection view/panel showing:

* mission number/title;
* short objective;
* relevant learning concept;
* best stars/score during the current application session if simple.

Do not add disk persistence/accounts/cloud saves yet.

In-memory progression is acceptable.

---

# 12. Mission brief

Before launch, clearly show:

```text
OBJECTIVE
CONSTRAINTS
CONTROLS YOU MAY CHANGE
PHYSICS HINT
```

The hint should teach rather than give the exact solution.

Example:

```text
Landing farther away requires horizontal motion,
but reducing the vertical thrust component also changes
your flight time and altitude.
```

---

# 13. World target visualization

For missions involving position/altitude, draw the objective in the world.

Examples:

* ground landing zone;
* target altitude band;
* target marker;
* safe landing region.

These visuals must use the same world-to-screen transformation as the simulation.

Do not duplicate physical coordinates with unrelated pixel-space rules.

Target visuals are game geometry, not forces.

---

# 14. Live mission HUD

During the flight show a compact HUD such as:

```text
OBJECTIVES

Reach 8 m             ✓
Land 16–20 m          …
Impact < 5 m/s        …
```

Only mark an objective complete when it is logically knowable.

Do not prematurely mark landing objectives before landing.

The HUD may celebrate intermediate events without changing simulation state.

---

# 15. Results screen

On terminal mission outcome, show:

* mission name;
* success/failure;
* stars;
* score;
* actual physical metrics;
* objective-by-objective results;
* brief physics explanation;
* Retry;
* mission selection;
* Sandbox;
* Next Mission if appropriate.

For failure, explain what physically happened.

Examples:

```text
NO LIFTOFF
Your selected mass produced no admissible free-flight launch.

MISSED LONG
Landing x = 22.4 m
Target = 16–20 m

HARD LANDING
Impact speed = ...
Limit = ...
```

Do not patronize the learner.

---

# 16. Game feel — restrained Prompt 06 scope

Add inexpensive presentation polish that does not threaten scope.

Appropriate examples:

* `3...2...1...IGNITION` countdown;
* target highlighting;
* success/failure banner;
* small particles/confetti on mission success;
* clearer launch/burnout/apogee cues;
* trajectory styling;
* score animation if simple.

Do not migrate rendering engines.

Do not implement real 3D or 2.5D yet.

Do not let countdown alter simulation time semantics; the simulation should begin only when launch actually occurs.

Audio is optional, not required.

---

# 17. Retry semantics

Retry should:

* return the mission to READY;
* preserve the player's mission-allowed selected parameters;
* clear prior flight trajectory/result;
* keep the same mission;
* not alter the mission's fixed configuration.

A separate mission reset may restore mission defaults.

Reuse existing deterministic reset/configuration paths where possible.

---

# 18. Progression

Use only lightweight in-memory progression for Prompt 06.

A reasonable rule:

```text
complete Mission N
→ unlock Mission N+1
```

Allow replay.

Do not add accounts, files, databases, networking, or cloud persistence.

For development/testing, provide a clean way to access missions without destructive hacks.

---

# 19. Living Rocketry Course

Update the course because the learner workflow changes.

Add a concise section/lesson on engineering missions:

```text
Prediction
→ choose design variables
→ satisfy constraints
→ launch
→ inspect result
→ explain success/failure
→ iterate
```

Connect missions to controlled experimentation.

Clarify that:

> the game score evaluates the simulator; it does not modify the physics.

Do not turn the course into a game manual.

---

# 20. Review matrix under Decision 08

Use targeted context.

## CORE — test_reviewer

Review:

* FlightResult correctness;
* mission objective evaluation;
* scoring;
* mission config restrictions;
* Sandbox equivalence;
* retry/reset;
* event routing;
* results/HUD sourcing;
* game/physics separation.

Ask:

> Could mission gameplay appear correct while silently using wrong simulation results or altering the validated run?

---

## CORE — learning_reviewer

Review:

* mission progression;
* hints;
* physical explanations;
* course update;
* objective wording;
* whether gameplay encourages reasoning rather than arbitrary clicking.

Ask:

> Does Mission Mode remain scientifically honest and reinforce engineering reasoning while becoming more engaging?

---

## FOCUSED — physics_reviewer

Give only the relevant game/result/config seams.

Ask:

> Does the game layer merely evaluate validated physics, or has any hidden game assistance or physical-semantic change leaked into the simulation?

---

## NOT REQUIRED by default

```text
numerical_reviewer
propulsion_reviewer
aerodynamics_reviewer
```

Do not invoke them unless their actual domains change.

No blanket review round.

Selective re-review only when Decision 08 requires it.

---

# 21. Required tests

At minimum independently test:

### FlightResult

* apogee from production trajectory;
* landing x;
* impact speed;
* max speed;
* max acceleration;
* max drag;
* flight time;
* NO LIFTOFF;
* result extraction does not mutate simulation.

### Mission evaluation

* exact pass/fail at boundaries;
* deterministic score;
* deterministic stars;
* objective evaluation uses production result/config;
* impossible/unlanded values handled honestly.

### Mission setup

* only allowed fields editable;
* mission-fixed values cannot be changed through UI/actions;
* underlying config remains authoritative;
* motor/timestep preserved unless explicitly part of a future mission.

### Physics integrity

For identical configuration and elapsed-time sequence:

```text
Sandbox trajectory/state
==
Mission trajectory/state
```

Mission Mode must not change physics.

This is a critical Prompt 06 regression.

### UI/game loop

* mission select → brief → ready → running → result;
* retry;
* next mission;
* sandbox return;
* target/HUD values sourced from mission/result data;
* rendering non-mutation.

---

# 22. Validation

Use staged validation under Decision 08.

Before implementation commit run:

```bash
conda run -n rocketsim python -m compileall -q src tests
conda run -n rocketsim python -m pytest
conda run -n rocketsim python -c "import rocket_sim"
git diff --check
```

Also:

* bounded dummy SDL run;
* representative mission runs;
* production-frame inspection for mission selection, brief/setup, live HUD, success result, failure result;
* verify Sandbox still behaves as Prompt 05;
* independently demonstrate every shipped mission has at least one achievable production configuration.

Do not claim manual interaction you did not perform.

---

# 23. Documentation

Update only applicable current documentation, likely:

```text
README.md
docs/ARCHITECTURE.md
docs/MILESTONES.md
docs/VALIDATION.md
docs/product/PROJECT_UNDERSTANDING.md
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

Decision 09 already defines the durable game/3D architecture.

Do not create another decision unless Prompt 06 makes a genuinely new durable choice not covered by Decision 09.

---

# 24. Explicit non-goals

Prompt 06 must not add:

* 2.5D;
* true 3D rendering;
* true 3D physics;
* renderer migration;
* variable mass;
* propellant depletion;
* motor editing/import;
* wind;
* altitude-dependent atmosphere;
* rotation/stability;
* recovery;
* guidance;
* trajectory auto-correction;
* automatic optimization;
* run-history comparison;
* disk persistence;
* networking;
* user accounts.

Those remain later milestones.

---

# 25. Definition of done

Prompt 06 is complete only when:

* Sandbox remains intact;
* Mission Mode exists;
* FlightResult is Pygame-independent;
* missions evaluate production simulation data;
* at least 4 polished achievable missions exist;
* setup restrictions work;
* world target visualization works;
* live objectives work;
* deterministic scoring/stars work;
* success and useful failure results work;
* retry works;
* lightweight progression works;
* Sandbox and Mission Mode produce identical physics for identical configs;
* no hidden physical assistance exists;
* Living Course is updated;
* targeted specialists have no unresolved BLOCKING/IMPORTANT findings;
* all tests pass;
* graphical smoke/visual validation passes.

---

# 26. Commit, prompt record, and push

Follow AGENTS.md and Decision 08.

Create implementation commit first.

Suggested message:

```text
Add mission mode and flight results
```

Then create compact:

```text
docs/prompts/prompt_06_mission_mode.md
```

Preserve this approved prompt verbatim plus material requirement-changing follow-ups.

Use Git-native provenance:

* starting SHA;
* parent SHA;
* implementation SHA;
* diff SHA-256;
* exact `git show` recovery command;
* review matrix/results;
* mission reachability evidence;
* final validation;
* efficiency audit.

Do not embed the full implementation patch.

Commit the prompt record separately.

Suggested message:

```text
Record prompt 06 mission mode implementation
```

Push `main` without force.

Verify:

```bash
git status
git branch -vv
git log --oneline --decorate -n 10
git ls-remote origin refs/heads/main
```

Require clean local/upstream/remote agreement.

Do not begin Prompt 07.

---

# 27. Completion report

Report concisely:

* starting SHA;
* review matrix;
* files/modules created;
* FlightResult metrics;
* mission model;
* shipped missions and validated successful configurations;
* scoring/star rules;
* Sandbox equivalence evidence;
* mission restriction behavior;
* HUD/target/results behavior;
* retry/progression;
* game polish added;
* course changes;
* final pytest result;
* SDL/visual validation;
* specialist findings/resolutions;
* implementation SHA;
* prompt-record SHA;
* remote verification;
* clean working tree;
* recommendations for the later run-comparison and 2.5D/3D presentation milestones.

Do not begin Prompt 07.
