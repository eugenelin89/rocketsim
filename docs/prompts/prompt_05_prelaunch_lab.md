# Prompt 05 — Interactive Pre-Launch Laboratory and Efficient Agent Workflow

- Date completed: 2026-08-29
- Scope: pre-launch laboratory, learning workflow, and agent-review efficiency
- Starting commit: `b2d8251dec4ec49b20600507d737ae99ec85e97e`
- Implementation parent: `b2d8251dec4ec49b20600507d737ae99ec85e97e`
- Implementation commit: `91adc8daedc0c4ca7d411b7c30ec95975fe1fa0c`
- Implementation message: `Add interactive pre-launch laboratory controls`
- Prompt-record commit: this file's containing commit; resolve with `git log -1 --format=%H -- docs/prompts/prompt_05_prelaunch_lab.md`
- Zero-context implementation-diff SHA-256: `b9afe9e8b8302bf55b4aacaa36788182db219ad6a3573f1e034fe0d8d26e73c2`
- Exact patch recovery: `git show --no-ext-diff --binary --format= 91adc8daedc0c4ca7d411b7c30ec95975fe1fa0c`
- Digest reproduction: `git show --no-ext-diff --binary --unified=0 --format= 91adc8daedc0c4ca7d411b7c30ec95975fe1fa0c | shasum -a 256`

## Starting state

The prompt named `12b3fd2509a125d5123829279237b0d21b410efb` as the expected Prompt 04 record commit. The actual clean, pushed local/upstream/remote baseline was the newer `b2d8251dec4ec49b20600507d737ae99ec85e97e`. Its only additional file was the user's pre-existing `docs/RocketSim_Agent_Workflow_Token_Efficiency.pdf`; Prompt 05 preserved it untouched. Branch `main`, `origin/main`, and remote `main` agreed before implementation.

The established environment was Python `3.12.14` at `/Users/eugenelin/.conda/envs/rocketsim/bin/python`, with the editable project installed in the `rocketsim` Conda environment. The baseline complete suite reported `162 passed`.

## Reconciled implementation contract

Prompt 05 adds no physical effect. It exposes six already-validated `SimulationConfig` quantities only while READY:

| Quantity | UI range | Increment | Display |
| --- | ---: | ---: | ---: |
| mass | `0.1–10.0 kg` | `0.1 kg` | 2 decimals |
| fixed thrust direction | `10–90 deg` | `5 deg` | 0 decimals |
| `Cd` | `0–2` | `0.05` | 2 decimals |
| reference area | `0.001–0.100 m^2` | `0.001 m^2` | 3 decimals |
| constant air density | `0–2 kg/m^3` | `0.05 kg/m^3` | 3 decimals |
| constant gravity | `0–20 m/s^2` | `0.25 m/s^2` | 2 decimals |

The ranges are classroom interface bounds, not physical validation limits. The immutable active config is getter-only. An accepted READY replacement atomically rebuilds the initial state, singleton trajectory, accumulator, step count, and lifecycle flags. Replacement is rejected without observable change while running, paused, coast, or landed. Reset Flight rebuilds READY state under the exact selected config; Restore Defaults requests an exact `SimulationConfig()` only while READY.

The sampled motor and fixed physics timestep remain uneditable and are displayed read-only. Ordinary edits preserve exact motor identity, timestep, initial conditions, and every unedited config field. Direction is displayed in degrees and stored/used in radians. Its READY preview is labeled fixed thrust direction rather than attitude, carries no force magnitude, and does not rotate the point marker.

Keyboard and mouse inputs create the same typed application actions and use one dispatcher. Rendering owns button geometry, hit-testing, drawing, and formatting but cannot mutate simulation/configuration. No launchability shortcut was added.

## Review matrix and context-efficiency evidence

| Classification | Specialist | Why / minimum context supplied |
| --- | --- | --- |
| CORE | `learning_reviewer` | Learner workflow, relevant existing lessons, setup behavior, controlled experiments, actual UI/course diff, and quantitative experiment evidence |
| CORE | `test_reviewer` | Setup/lock/reset/default contract; relevant setup, simulation, app, renderer, and tests; focused/full results; actual changed seams |
| FOCUSED | `physics_reviewer` | Six exposed parameters, immutable READY boundary, existing force/config interfaces, relevant physics clarification/tests, and narrow hidden-intervention question |
| NOT REQUIRED | `numerical_reviewer` | No timestep control, integrator, event timing, or solver change; existing regressions passed |
| NOT REQUIRED | `propulsion_reviewer` | No curve interpolation, impulse, burn timing, motor selection, or motor scaling change; existing regressions passed |
| NOT REQUIRED | `aerodynamics_reviewer` | No aerodynamic equation or air-relative-velocity semantic change; existing drag regressions passed |

The parent and reviewers used High reasoning. Extra High was not needed. Specialists received the reconciled contract and domain-relevant current files/evidence rather than the full historical archive. No historical prompt record was reread; current authoritative documentation, accepted decisions, implementation, and tests were sufficient. Three complete-suite runs occurred during Prompt 05: baseline `162`, integrated pre-post-review `209`, and final `211`. Focused groups were used between material changes.

This milestone used no blanket review ritual. Only the three classified reviewers were invoked. Selective learning and test re-reviews occurred because their own BLOCKING/IMPORTANT findings were corrected; physics needed no resolution re-review. Hidden token counts were not estimated.

## Specialist findings and resolutions

### Pre-implementation

`physics_reviewer` required getter-only config ownership, atomic complete READY rebuilding, presentation-only direction preview, explicit run-level constant-mass wording, no snapping of off-grid defaults, and honest no-liftoff handling. All were adopted.

`learning_reviewer` found that `1.0 kg` versus `2.0 kg` would compare liftoff with no-liftoff, not two flights. Lesson 10 instead uses `1.0` versus `1.2 kg`. It also required retroactive control/reset wording, precise fixed-direction semantics, a more visible drag experiment, and explicit no-liftoff/non-return and constant-parameter limitations. All were adopted; the drag experiment uses `A=0.100 m^2` for both `Cd` runs.

`test_reviewer` required evidence across real seams: literal all-hitbox wiring, actual Pygame event routing through the common dispatcher, complete READY snapshots and non-READY no-ops, exact rendered config sourcing, independent production-force oracles, reset/default distinction, motor/unexposed-field preservation, bounds/reversibility, and expanded non-mutation snapshots. Those gates shaped `tests/test_setup.py`.

### Post-implementation and selective resolution

The focused physics post-review passed with no BLOCKING or IMPORTANT finding. It confirmed unchanged equations, motor, timestep, events, and constant-within-run semantics.

The learning post-review found one BLOCKING UI/course mismatch: timestep was described as a controlled read-only condition but not visible. The panel now reports production `Physics dt`, and every experiment table counts motor/timestep as controlled/read-only. IMPORTANT corrections label mass accelerations as analytical instantaneous `t=0` predictions that a manual pause will not capture exactly, and replace an underspecified similar-speed drag comparison with recorded speed/drag plus `|F_drag|/speed^2`. Selective re-review confirmed all learning findings resolved.

The test post-review judged the large setup suite rigorous rather than gratuitously repetitive. It found two BLOCKING evidence gaps and two IMPORTANT hardening gaps: ordinary-edit preservation needed distinctive timestep/initial velocity; actual rendered labels/values needed capture; visible coast lockout was missing; and direct non-READY actions covered only `+`. Existing fixtures/parameterizations were strengthened and one recording-font draw test added. Selective re-review confirmed all test findings resolved.

No reviewer had an unresolved BLOCKING or IMPORTANT finding at implementation commit.

## Implementation summary

- Added Pygame-independent setup parameter specifications, display formatting, immutable config rebuilding, and typed actions.
- Made the simulation-owned configuration getter-only and its READY replacement atomic.
- Added one common action dispatcher for keyboard and mouse input.
- Added READY setup controls, primary Launch/Pause/Resume, Reset Flight, Restore Defaults, locked states, motor/timestep summary, and exact fixed-direction preview.
- Expanded the Inspector with fixed direction and gravity from production config.
- Added seam-level setup/application/rendering tests while preserving all lower-level independent physics oracles.
- Added Decision 08 and the permanent agent-context, selective-review, staged-validation, compact-resume, current-state, and Git-native provenance policies.
- Revised existing course instructions and added Lesson 10 controlled experiments for mass, drag coefficient, and fixed thrust direction.
- Updated current architecture, physics-boundary clarification, milestones, validation evidence, product understanding, and README.

## Files in the implementation commit

Created:

- `docs/decisions/decision_08_agent_context_and_review_efficiency.md`
- `src/rocket_sim/setup.py`
- `tests/test_setup.py`

Modified:

- `AGENTS.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/PHYSICS_MODEL.md`
- `docs/VALIDATION.md`
- `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md`
- `docs/product/PROJECT_UNDERSTANDING.md`
- `src/rocket_sim/app.py`
- `src/rocket_sim/rendering.py`
- `src/rocket_sim/simulation.py`
- `tests/test_rendering.py`

The pre-existing workflow PDF was not modified. `config.py`, `physics.py`, and `propulsion.py` were not changed.

## Quantitative and automated validation

- Final complete suite: `211 passed`.
- Final focused setup/rendering/simulation group: `82 passed`.
- Python: `3.12.14`; interpreter: `/Users/eugenelin/.conda/envs/rocketsim/bin/python`.
- `python -m compileall -q src tests`: passed.
- `import rocket_sim`: passed (`0.1.0`).
- Dummy SDL bounded application: passed.
- Real SDL bounded application: launched and exited successfully.
- `git diff --check`: passed before commit.
- The terminal-velocity course example produced `-3.8598482081 m/s` versus analytical `-3.8561103203 m/s`.
- The zero-at-ignition course example produced `T(0)=0`, first-interval impulse `0.028 N*s`, total impulse `17.28 N*s`, and final `vy=17.28 m/s`.
- Untouched GUI defaults and explicit `SimulationConfig()` produced identical final state, full trajectory, forces, and step count.

Lesson 10 production evidence:

| Experiment | Run A | Run B |
| --- | --- | --- |
| mass `1.0` vs `1.2 kg` | apogee `8.1031495 m`, landed `3.0579922 s` | apogee `4.6826747 m`, landed `2.4610537 s` |
| `Cd=0.5` vs `1.0`, both `A=0.100 m^2` | apogee `7.1906235 m`, landed `2.9186619 s` | apogee `6.4418044 m`, landed `2.8010351 s` |
| direction `90` vs `60 deg` | terminal `x` approximately zero | terminal `x=18.1176548 m` |

## Visual validation

Six production-rendered `1200x720` states were assembled and visually inspected: READY default, READY modified, running locked, paused locked, Reset Flight preserving/unlocking the modified selection, and Restore Defaults. Values, disabled-state styling, direction preview, motor/timestep summary, timeline, buttons, and Inspector were readable without panel overlap. The default upper angle increment was visibly disabled at its bound. Automated event and action tests—not visual inspection—are the behavioral oracle; physical manual mouse interaction is not claimed.

## Living Rocketry Course result

Earlier control, reset, default, mass, powered-flight, drag, terminal-velocity, limitation, and motor wording was revised rather than merely appending a note. Lesson 10 teaches independent, dependent, and controlled variables through Predict → Control → Launch → Observe → Explain. It includes reproducible mass, `Cd`, and direction experiments; distinguishes selected constants from omitted variable physics; and explains educational UI bounds, no-liftoff, non-return, absence of automatic comparison, model uncertainty limits, and fixed direction versus attitude.

## Scope audit and limitations

No new physical effect, physical equation, integration behavior, event semantic, dependency, GUI framework, timestep editor, motor editor, run-comparison engine, persistence, plot/export facility, variable mass, propellant depletion, wind, atmosphere variation, lift, rotation, stability, recovery, guidance, or Prompt 06 work was added.

The UI remains a fixed `1200x720` Pygame layout with button increments rather than text entry or sliders. Setting area from `0.010` to `0.100 m^2` requires 90 clicks. Runs are compared by learner notes; the app stores no previous-run result. Broad valid UI combinations can produce NO LIFTOFF or non-returning zero-gravity coast under the documented simplified model.

## Material follow-up instruction (verbatim)

```text
Resume Prompt 05 from the exact current working tree.

Follow the Prompt 05 contract and the newly drafted Decision 08 / AGENTS agent-efficiency policy.

First inspect:

- git status
- git diff --check
- current focused-test state
- completed reviewer results

Do not restart completed work or repeat completed pre-reviews.

Known checkpoint:

- actual starting baseline is clean pushed `b2d8251`; its token-efficiency PDF is pre-existing user work and must remain untouched
- Decision 08 and the AGENTS efficiency policy are drafted
- learning_reviewer, test_reviewer, and focused physics_reviewer pre-reviews are complete
- reconciled design is implemented substantially
- six READY setup values rebuild an immutable validated configuration
- `Simulation.config` is getter-only and READY replacement is atomic
- mouse and keyboard actions share one dispatcher
- setup/lifecycle/rendering focused tests were passing
- course and documentation updates are substantially in place
- at least one production UI frame has been visually inspected

Continue from the first incomplete Prompt 05 gate.

Before post-review, finish the current implementation/documentation/visual checks and rerun the focused affected tests.

Then use the established Prompt 05 review matrix only:

CORE:

- learning_reviewer
- test_reviewer

FOCUSED:

- physics_reviewer

Do not invoke numerical_reviewer, propulsion_reviewer, or aerodynamics_reviewer unless the actual implementation unexpectedly changed their domains.

Give each reviewer only the minimum sufficient domain-relevant context under Decision 08.

Specifically ask test_reviewer to inspect whether the large `tests/test_setup.py` is appropriately rigorous or unnecessarily repetitive; simplify only if equivalent evidence can be preserved.

After findings:

- fix valid BLOCKING/IMPORTANT issues
- rerun affected tests
- re-review only domains materially changed
- do not perform a blanket reviewer round

Then complete:

- final course consistency audit
- final UI visual/dummy-SDL validation
- complete pytest suite
- compile/import checks
- `git diff --check`
- Decision 08 / AGENTS final policy audit
- qualitative Prompt 05 efficiency audit
- implementation commit
- compact Prompt 05 record using Git-native provenance
- DO NOT embed the full implementation patch
- separate prompt-record commit
- push to origin/main
- final local/upstream/remote SHA verification
- clean working tree

Do not begin Prompt 06.

Report the complete Prompt 05 completion report required by the original prompt.
```

## Approved original implementation prompt (verbatim)

# Prompt 05 — Interactive Pre-Launch Laboratory and Efficient Agent Workflow

Work in:

```text
/Users/eugenelin/dev/cwsf2027/rocketsim
```

Canonical repository:

```text
https://github.com/eugenelin89/rocketsim.git
```

This is **Prompt 05**.

Prompt 04 completed the sampled-thrust propulsion model, motor timeline, Living Rocketry Course, and scientific review infrastructure.

Prompt 05 deliberately introduces **no new physical effect**.

Its goals are:

1. make RocketSim configurable as an interactive pre-launch learning laboratory;
2. add an obvious mouse-accessible Launch workflow while preserving keyboard controls;
3. allow learners to modify selected already-implemented physical parameters before flight;
4. teach controlled experimentation using those parameters;
5. permanently improve the repository’s agent/subagent workflow so future milestones achieve the same scientific rigor with substantially less duplicated model context and reasoning.

Do not begin variable mass or any other Prompt 06 physics.

Use the parent model at **High reasoning effort** by default.

Use Extra High only if an unexpected scientific or architectural conflict genuinely requires difficult reconciliation.

---

# 1. Start from the current Prompt 04 baseline

Before editing, verify the repository is clean and matches the pushed Prompt 04 state.

Expected current Prompt 04 prompt-record commit:

```text
12b3fd2509a125d5123829279237b0d21b410efb
```

Inspect:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 10
git ls-remote origin refs/heads/main
```

Confirm:

* branch is `main`;
* working tree is clean;
* local `main`, `origin/main`, and remote `main` agree;
* Prompt 05 has not already begun.

Verify the established environment:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pytest
```

Do not create another Python environment.

---

# 2. Use current authoritative documentation, not full historical rereading

This prompt is the first milestone under the new context-efficiency policy.

The parent should read:

```text
AGENTS.md
README.md
docs/PHYSICS_MODEL.md
docs/VALIDATION.md
docs/ARCHITECTURE.md
docs/MILESTONES.md
docs/product/PROJECT_UNDERSTANDING.md
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
current accepted decisions relevant to this milestone
current source/tests affected by this milestone
```

Read Prompt 04's record only where needed for immediate regression/provenance context.

Do **not** automatically reread every historical prompt record from Prompt 01 onward.

Retrieve older history only if a current authoritative document or code contract is ambiguous.

---

# 3. First durable change: Agent Efficiency Policy

Before the main UI implementation, update the repository workflow so this and later milestones use model context more efficiently.

Update `AGENTS.md` with a concise permanent section approximately titled:

```text
## Agent Context and Review Efficiency
```

The policy must preserve scientific independence while reducing unnecessary duplicate context.

Codify the following principles.

## 3.1 Minimum sufficient specialist context

Specialists should receive the **minimum sufficient context** required to independently review their domain.

Do not instruct every specialist to reread:

* the complete milestone prompt;
* every historical prompt;
* every project document;
* every unrelated source module;
* every unrelated test.

The parent agent remains responsible for broad project context.

A specialist should normally receive or inspect:

```text
reconciled milestone contract
+
authoritative sections relevant to its domain
+
changed/relevant source files
+
changed/relevant tests
+
relevant quantitative evidence
+
relevant diff
```

A specialist may request additional context when necessary.

Efficiency must never prevent a reviewer from obtaining information needed to make a scientifically defensible judgment.

---

# 4. Core / focused / not-required review classification

For each milestone, the parent must classify specialists as:

```text
CORE
FOCUSED
NOT REQUIRED
```

### CORE

The milestone directly changes the specialist's domain.

A core reviewer normally participates in both appropriate pre-review and post-review.

### FOCUSED

The milestone touches or may regress the specialist's domain but does not change its governing model.

A focused reviewer receives a narrow question and only relevant context.

### NOT REQUIRED

The specialist's domain is unchanged and adequately protected by existing regression tests.

The specialist is not invoked merely because it exists.

Record the review matrix in the milestone record.

---

# 5. Selective re-review

A specialist must not automatically be reinvoked after every correction.

Reinvoke a specialist only when:

* a BLOCKING or IMPORTANT finding from that specialist was corrected and confirmation is useful; or
* subsequent implementation materially changed that specialist's reviewed domain.

Examples:

```text
course wording change
→ learning reviewer may recheck
→ numerical reviewer does not rerun

integrator change
→ numerical + possibly test reviewer recheck
→ learning reviewer only if learner-facing behavior changed
```

Do not rerun all specialists as a generic final ritual.

---

# 6. Reasoning-effort policy

Codify:

```text
parent agent:
    High by default

specialist reviewers:
    High by default
```

Use Extra High for the parent only when warranted by genuinely difficult:

* scientific disagreement;
* numerical-method reconciliation;
* event-semantics change;
* hard-to-reverse architecture choice.

Once such reconciliation is complete, ordinary implementation/validation/commit work should return to High where practical.

This is an efficiency policy, not a quality ceiling.

---

# 7. Staged validation policy

Do not repeatedly run the entire test suite after every minor edit.

Preferred sequence:

```text
during implementation
    affected/focused tests

after meaningful subsystem integration
    relevant subsystem groups

before post-review
    evidence required by reviewers

after material review fixes
    affected tests

before implementation commit
    complete suite
```

Run the full suite again after a late material core change when necessary.

A valid test result does not become invalid simply because unrelated documentation changed.

---

# 8. Git-native prompt provenance

Revise the existing prompt-history/archive policy deliberately.

By default, future prompt records should **not embed the complete implementation Git patch** in Markdown.

Git itself is the authoritative exact patch store.

Prompt records should instead contain:

```text
starting commit SHA
implementation parent SHA
implementation commit SHA
prompt-record commit SHA where applicable
zero-context implementation-diff SHA-256
exact command required to reproduce the patch
```

Use a recovery command equivalent to:

```bash
git show --no-ext-diff --binary --format= <implementation-sha>
```

The exact full patch may be embedded only when a specific reason requires preserving it outside Git.

Prompt records must still preserve:

* the approved original implementation prompt verbatim;
* material user corrections that changed requirements;
* important reviewer findings/resolutions;
* durable decisions;
* quantitative evidence;
* validation result;
* push/final state.

Routine resume messages that add no new requirement do not need to be copied verbatim into the permanent prompt record.

Material resume instructions that change requirements still must be preserved.

---

# 9. Compact resume policy

Codify that normal interruption recovery should rely on repository state.

A typical resume instruction should be able to say:

```text
Resume the approved current milestone from the exact working tree.

Inspect current Git state, diff, test state, and completed reviewer results.
Do not repeat completed reviews.
Continue from the first incomplete required gate.
```

Do not require a giant restatement of the milestone unless important state cannot be recovered from the repository.

---

# 10. Current-state-over-history policy

Current authoritative documentation should normally be preferred over historical prompt rereading.

Use:

```text
AGENTS.md
PHYSICS_MODEL.md
VALIDATION.md
ARCHITECTURE.md
accepted current decisions
current implementation/tests
```

as the normal working context.

Historical prompt records remain available for:

* provenance;
* supersession;
* regression archaeology;
* ambiguity resolution.

---

# 11. Preserve independent scientific derivation

Do **not** optimize away useful scientific independence.

For example:

```text
production calculation
!=
independent test oracle
!=
independent specialist derivation
```

Independent derivations are intentional evidence.

The efficiency target is irrelevant context duplication, not scientific cross-checking.

---

# 12. Create a durable workflow decision

Create the next actual decision record, expected approximately:

```text
docs/decisions/decision_08_agent_context_and_review_efficiency.md
```

Use the actual next available ID.

Record:

* why Prompt 04 consumed substantial model usage;
* parent vs specialist responsibilities;
* minimum-sufficient-context principle;
* core/focused/not-required classification;
* selective re-review;
* High-default reasoning policy;
* staged validation;
* current-state-over-history reading;
* compact resume behavior;
* Git-native prompt provenance;
* preservation of independent scientific reasoning.

This decision should explicitly state:

> The objective is more scientific confidence per unit of model context and reasoning, not fewer scientific checks merely for token savings.

---

# 13. Prompt 05 review matrix

Prompt 05 introduces no new physics.

Use this targeted review matrix:

```text
CORE
    learning_reviewer
    test_reviewer

FOCUSED
    physics_reviewer

NOT REQUIRED by default
    numerical_reviewer
    propulsion_reviewer
    aerodynamics_reviewer
```

### `learning_reviewer`

Core because Prompt 05 changes the learner workflow and Living Rocketry Course.

### `test_reviewer`

Core because the milestone adds interactive configuration and state-locking behavior.

### `physics_reviewer`

Focused review only.

Its narrow question is:

> Does the pre-launch configuration UI map faithfully to already-validated physical parameters without introducing hidden physics or allowing scientifically invalid mid-flight mutation?

It does not need to rederive all previous physics.

### `aerodynamics_reviewer`

Do not invoke automatically.

Existing drag equations do not change.

Invoke only if implementation changes aerodynamic model semantics rather than merely passing `rho`, `Cd`, and `A` through existing validated configuration.

### `propulsion_reviewer`

Do not invoke automatically.

Prompt 05 must not edit or scale thrust-curve physics.

### `numerical_reviewer`

Do not invoke automatically.

Prompt 05 must not expose or change `physics_dt_s` through the user UI and must not change integration semantics.

If implementation unexpectedly requires changing any of those domains, reclassify the relevant specialist before proceeding and document why.

This review matrix is itself part of Prompt 05's efficiency evidence.

---

# 14. Prompt 05 product goal

RocketSim currently excels at:

```text
observe physics
```

Prompt 05 should add:

```text
configure
→ predict
→ launch
→ observe
→ pause / inspect / single-step
→ explain
→ reset / modify
→ repeat
```

The simulator should feel like an interactive laboratory rather than a fixed demonstration.

---

# 15. Add a pre-launch Setup panel

Create a learner-facing setup panel visible while the simulation is READY.

Allow editing only selected physics already implemented and validated.

At minimum expose:

```text
Rocket
    mass

Launch
    launch angle

Aerodynamics
    Cd
    reference area

Environment
    air density
    gravity
```

Do not expose `physics_dt_s` as an ordinary learner control.

Do not expose thrust-curve editing in Prompt 05.

The currently configured sampled motor remains visible/read-only through the existing motor timeline/Inspector.

---

# 16. Editable parameters

Recommended learner-facing parameters:

```text
mass_kg
launch_angle_rad displayed as degrees
drag_coefficient
reference_area_m2
air_density_kg_m3
gravity_m_s2
```

Use SI units everywhere except launch angle may be displayed/edited in degrees for usability while the physics core continues using radians internally.

The UI conversion must be presentation/configuration logic only.

Do not change the internal coordinate convention.

---

# 17. Educational UI ranges

The underlying physical model remains governed by `SimulationConfig` validation.

The setup panel may additionally impose sensible **educational UI ranges** to keep controls usable.

Choose and document reasonable ranges after focused review.

For example, ranges may be approximately:

```text
mass              0.1 – 10 kg
launch angle      10 – 90 deg
Cd                0.0 – 2.0
area              0.001 – 0.10 m^2
air density       0.0 – 2.0 kg/m^3
gravity           0.0 – 20 m/s^2
```

These are interface bounds, not statements that nature is limited to them.

If reviewers recommend better pedagogical ranges, use those and document them.

---

# 18. Control design

Use simple Pygame-native controls.

Do not add a GUI framework dependency.

A suitable pattern is:

```text
MASS
[-]  1.00 kg  [+]

ANGLE
[-]  90 deg   [+]

Cd
[-]  0.75     [+]

AREA
[-]  0.010 m^2 [+]

AIR DENSITY
[-]  1.225 kg/m^3 [+]

GRAVITY
[-]  9.81 m/s^2 [+]
```

Sliders are acceptable if they remain simple and testable, but precise step controls may be easier to validate and teach.

The parent should prefer the simplest readable interaction.

Avoid elaborate widgets.

---

# 19. Step sizes

Choose useful deterministic increments.

For example:

```text
mass          0.10 kg
angle         5 deg
Cd            0.05
area          0.001 m^2
density       0.05 kg/m^3
gravity       0.25 m/s^2
```

These are UI increments only.

Values must remain validated and formatted sensibly.

---

# 20. Restore Defaults

Provide an obvious READY-only action:

```text
[ RESTORE DEFAULTS ]
```

It should restore exactly the current documented Prompt 04 default configuration.

Do not duplicate default numbers throughout rendering code.

Use authoritative configuration/default constructors or data.

Test that restore-default behavior matches the production defaults.

---

# 21. Add an on-screen Launch control

SPACE must continue to work.

Also provide an obvious mouse-accessible primary action.

In READY:

```text
[ LAUNCH ]
```

During flight it may become:

```text
[ PAUSE ]
```

and when paused:

```text
[ RESUME ]
```

or equivalent.

The mouse action and SPACE must use the same production application/simulation path.

Do not implement separate launch/pause/resume physics logic for the button.

---

# 22. Reset workflow

Preserve keyboard:

```text
R = reset
```

Add a mouse-accessible reset action.

Recommended semantics:

> Reset returns the flight to READY while preserving the learner's currently selected setup values.

This supports repeated controlled experiments.

Add a separate:

```text
RESTORE DEFAULTS
```

for resetting configuration.

Clearly distinguish:

```text
RESET FLIGHT
vs.
RESTORE DEFAULTS
```

Document and test both.

---

# 23. Configuration locking

Physical parameters may be edited only while:

```text
FlightPhase.READY
```

Once launched:

```text
RUNNING
PAUSED
COAST
LANDED
```

the physical setup controls must be locked.

Do not allow arbitrary mid-flight mutations of:

* mass;
* launch angle;
* `Cd`;
* area;
* air density;
* gravity.

This is a scientific requirement.

Changing a physical parameter during flight would imply an unmodeled physical intervention.

The UI may visually disable controls and explain:

```text
Reset flight to modify setup.
```

---

# 24. Reset then modify

After a flight:

```text
R
```

or the Reset Flight button should return to READY.

The learner may then modify parameters and relaunch.

The intended loop is:

```text
configure A
→ launch
→ observe
→ reset
→ change one variable
→ launch
→ compare observations
```

---

# 25. Rebuild configuration safely

The existing model uses immutable `SimulationConfig`.

Preserve that principle.

Do not mutate a live config object in place.

When a READY parameter changes, use the smallest clean architecture to create a new validated configuration / READY simulation state.

Do not let the renderer directly mutate physics internals.

Application/UI code may request a configuration change; simulation/configuration ownership should remain explicit.

---

# 26. Preserve motor configuration

Prompt 05 does not add motor editing.

Changing other setup parameters must preserve the currently selected/default `ThrustCurve` exactly.

Do not accidentally reconstruct an approximate motor curve.

Do not scale thrust with mass.

Do not automatically choose a different motor.

The learner is changing one variable in the physical experiment, not invoking hidden coupled behavior.

---

# 27. Preserve all Prompt 04 physics

No change is permitted to:

* `ThrustCurve` interpolation;
* impulse;
* burn-end semantics;
* knot splitting;
* gravity equation;
* quadratic-drag equation;
* force composition;
* constant-mass-within-run semantics;
* ground admission;
* impact interpolation;
* accumulator;
* FPS independence;
* paused stepping.

Mass may differ **between runs**, but remains constant throughout each individual run.

This distinction must be documented clearly.

---

# 28. Physics Inspector integration

The Physics Inspector should show the configured values already used by the current simulation.

Where useful, make the setup-to-Inspector relationship obvious.

For example:

```text
SETUP                     INSPECTOR DURING FLIGHT

Mass 2.00 kg      →       Mass 2.000 kg
Cd 1.00           →       Cd 1.000
Area 0.020 m²     →       Area 0.020 m²
rho 1.000         →       rho 1.000 kg/m³
gravity 9.81      →       gravity / force behavior
```

Do not create a second independent parameter store that can disagree with the production `SimulationConfig`.

---

# 29. Launch-angle visualization

Because launch angle is now configurable, ensure the learner can visually understand it before launch.

A simple preview is appropriate:

```text
ground
──────────────
      /
     / 90° etc.
    🚀
```

or an equivalent launch-direction indicator.

The preview is rendering-only.

It must use the exact configured launch angle.

Do not add rocket rotation dynamics.

The rocket remains a point-mass model with fixed world thrust direction.

---

# 30. Do not imply orientation dynamics

If the drawn rocket marker is rotated to match the configured launch angle for clarity, document clearly:

> The marker shows configured thrust direction, not simulated rotational attitude.

No torque, angle of attack, rotational inertia, CG/CP, or stability is introduced.

---

# 31. Setup summary

Provide a concise READY-state experimental summary such as:

```text
READY TO LAUNCH

Mass             1.00 kg
Launch angle     90°
Cd               0.75
Area             0.010 m²
Air density      1.225 kg/m³
Gravity          9.81 m/s²

Motor            Synthetic educational curve
Total impulse    17.58 N*s
```

Do not overwhelm the UI.

The existing timeline and Inspector remain authoritative for detailed propulsion data.

---

# 32. Optional launchability feedback

Do not invent a simplistic:

```text
T(0) > mg → launchable
```

indicator.

The sampled motor and impulse-aware ground-admission semantics make that insufficient in general.

Only add launchability feedback if it calls the same side-effect-free production admission logic or an independently justified equivalent.

Otherwise omit the indicator.

Avoid misleading educational shortcuts.

---

# 33. Mouse event architecture

Implement mouse interaction cleanly.

The renderer should own layout/drawing geometry.

Application-level input handling may interpret mouse events and request actions.

Physics/simulation modules must not import Pygame.

Do not move simulation ownership into rendering code.

---

# 34. Keyboard behavior remains

Preserve:

```text
SPACE   launch / pause / resume
RIGHT   single-step while paused
R       reset flight
F       force vectors
I       Physics Inspector
ESC     exit
```

Mouse buttons supplement these controls.

They do not replace them.

---

# 35. Required behavioral tests

Add tests covering at least:

1. READY parameter editing works.
2. Parameter changes produce a new validated configuration.
3. The configured values reach production simulation physics.
4. Mass change affects acceleration according to the existing model.
5. Angle change affects thrust vector using the existing physics path.
6. `Cd` change reaches drag calculation.
7. area change reaches drag calculation.
8. air-density change reaches drag calculation.
9. gravity change reaches gravity calculation.
10. thrust curve is preserved when unrelated setup parameters change.
11. setup controls are locked after launch.
12. setup controls remain locked while paused.
13. setup controls are locked after landing until reset.
14. Reset Flight returns to READY and preserves selected setup.
15. Restore Defaults restores exact documented defaults.
16. mouse Launch uses the same behavior as SPACE.
17. mouse Pause/Resume uses the same state transitions as SPACE.
18. mouse Reset uses the same flight-reset semantics as R.
19. renderer does not mutate simulation/configuration.
20. launch-angle preview comes from configured angle.

Avoid duplicate test implementations of physical equations where established lower-level tests already cover them.

Use targeted integration checks to prove UI → configuration → production physics wiring.

---

# 36. Regression tests

Preserve all existing tests.

The Prompt 04 sampled-motor default should still reproduce its validated flight when the learner leaves setup at defaults.

Explicitly verify that:

```text
default GUI setup
==
default SimulationConfig
```

for every exposed parameter.

No GUI layer should silently alter the default run.

---

# 37. Living Rocketry Course update

Update:

```text
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

because Prompt 05 materially changes the learner workflow.

Revise existing simulator-control instructions where appropriate.

Do not merely append a note.

---

# 38. Add a controlled-experiments lesson

Add the next lesson, approximately:

```text
Lesson 10 — Designing Experiments with RocketSim
```

Teach:

* independent variable;
* dependent variable;
* controlled variables;
* changing one thing at a time;
* prediction before simulation;
* recording observations;
* explaining results using physics;
* why changing several parameters simultaneously makes causal interpretation harder.

Use RocketSim as the laboratory.

---

# 39. Guided experiment: mass

Use the setup panel.

Example:

```text
Run A
mass = 1.0 kg

Run B
mass = 2.0 kg

all other settings identical
```

Ask the learner to predict:

* initial acceleration;
* powered-flight behavior;
* apogee;
* why motor impulse is unchanged;
* why drag history may also change indirectly because velocity changes.

Be precise that mass remains constant within each run.

Do not teach propellant depletion yet.

---

# 40. Guided experiment: drag coefficient

Example:

```text
Run A
Cd = 0.50

Run B
Cd = 1.00

all other settings identical
```

Have the learner compare:

* drag force at similar speeds;
* trajectory;
* apogee;
* flight behavior.

Explain that comparing drag at exactly equal speed is cleaner than simply assuming the entire trajectory scales linearly.

---

# 41. Guided experiment: launch angle

Example:

```text
90°
vs.
60°
```

Teach:

* vector thrust components;
* horizontal and vertical motion;
* why the same motor can produce a different trajectory.

Do not introduce aerodynamic lift or stability.

---

# 42. Predict → Observe → Explain loop

The UI and course should reinforce:

```text
PREDICT
What will change?

CONTROL
What remains constant?

LAUNCH
Run the model.

OBSERVE
Record actual quantities.

EXPLAIN
Use implemented equations.
```

This should become the primary educational workflow.

---

# 43. Course limitations

Explicitly explain:

* parameters are changed between simulations, not physically changed during flight;
* UI slider/button ranges are educational interface choices;
* changing a model parameter is not the same thing as building a real rocket that achieves that parameter;
* no uncertainty/calibration is modeled;
* results remain educational model predictions.

---

# 44. No comparison engine yet

Do not add in Prompt 05:

* automatic side-by-side run comparison;
* persistent run database;
* ghost trajectories;
* plots across multiple runs;
* parameter sweeps;
* CSV export;
* optimization.

The learner may manually record observations.

These are strong future features but should be separate milestones.

---

# 45. No new physics

Explicitly do not add:

* variable mass;
* propellant depletion;
* specific impulse;
* motor editing;
* motor imports;
* wind;
* altitude-varying atmosphere;
* Mach effects;
* variable `Cd`;
* lift;
* rotation;
* stability;
* recovery;
* staging;
* guidance/control.

Prompt 05 is an **experimental-interface milestone**, not a physical-model milestone.

---

# 46. Focused pre-review

Before implementing the setup behavior, use only the relevant reviewers.

## Core: learning reviewer

Give it:

* this milestone's learner workflow;
* relevant course sections;
* proposed setup parameters;
* proposed controlled experiments;
* relevant UI behavior.

Ask:

> Will the proposed configuration workflow teach controlled rocketry experiments accurately without implying unimplemented physics?

Do not require it to reread unrelated source/tests.

## Core: test reviewer

Give it:

* setup-state contract;
* configuration-lock rules;
* mouse/keyboard equivalence;
* reset/default semantics;
* relevant app/config/rendering/simulation files and tests.

Ask:

> Could UI state or parameter wiring be wrong while the proposed tests still pass?

## Focused: physics reviewer

Give it only:

* exposed parameters;
* READY-only edit contract;
* immutable-config rebuilding plan;
* existing authoritative equations/sections;
* relevant config/app/simulation interfaces.

Ask:

> Does this UI faithfully expose existing physical parameters without changing the physical model or allowing hidden mid-flight interventions?

Wait for these reviews and reconcile their findings.

Do not invoke unrelated specialists unless the reconciled design actually changes their domains.

---

# 47. Implementation

After focused pre-review:

* parent agent implements;
* run affected tests incrementally;
* update UI;
* update course;
* update documentation.

The parent remains the only write-authority agent.

---

# 48. Focused post-review

After implementation:

### learning reviewer — CORE

Inspect:

* actual setup UI;
* actual controls;
* Lesson 10;
* revised earlier instructions;
* experiment wording.

### test reviewer — CORE

Inspect:

* changed implementation;
* new tests;
* reset/default/locking behavior;
* mouse-keyboard equivalence;
* renderer/config separation.

### physics reviewer — FOCUSED

Inspect only whether final UI → config → physics wiring preserves existing equations and run-level constant-mass semantics.

Do not automatically invoke numerical, propulsion, or aerodynamic reviewers.

Invoke one only if implementation unexpectedly altered its domain.

---

# 49. Selective resolution review

If review findings require changes:

* rerun affected tests;
* reinvoke only specialists whose reviewed domain materially changed.

Do not perform a blanket six-agent final-resolution round.

Record this as evidence that Decision 08's efficiency workflow is functioning.

---

# 50. Documentation updates

Review/update only where applicable:

```text
AGENTS.md
README.md
docs/ARCHITECTURE.md
docs/MILESTONES.md
docs/product/PROJECT_UNDERSTANDING.md
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

Update `docs/PHYSICS_MODEL.md` only if clarification is needed.

There should be no new governing physical equation in Prompt 05.

Update `docs/VALIDATION.md` with actual UI/configuration/regression evidence where appropriate.

Create Decision 08.

Do not create unnecessary decisions for individual widgets.

---

# 51. Architecture expectation

Likely responsibility remains approximately:

```text
config.py
    immutable validated physical configuration

propulsion.py
    unchanged motor curve

physics.py
    unchanged physical equations

simulation.py
    deterministic run under one configuration

app.py
    keyboard/mouse action handling
    READY configuration requests

rendering.py
    setup controls
    launch/reset/default buttons
    angle preview
    Physics Inspector/timeline

docs/learning/
    interactive controlled-experiment course
```

If a small new Pygame-independent setup-state helper materially improves separation, it is acceptable.

Do not create a generalized UI framework.

---

# 52. Visual validation

Inspect at least:

### READY default

* setup controls readable;
* defaults correct;
* Launch button obvious;
* timeline/Inspector remain usable.

### Modified setup

* changed values visibly reflected;
* launch-angle preview correct.

### Running

* setup controls visibly locked;
* Pause action works.

### Paused

* setup remains locked;
* RIGHT single-step remains functional.

### Reset

* selected setup preserved;
* controls unlock.

### Restore Defaults

* documented defaults restored exactly.

Check small-screen/layout overlap within the existing application size.

---

# 53. Automated validation

Run focused groups during development.

Before implementation commit run at least:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -m compileall -q src tests
conda run -n rocketsim python -m pytest
conda run -n rocketsim python -c "import rocket_sim"
git diff --check
```

Run bounded dummy SDL validation.

Run the real application where possible for visual inspection.

Do not falsely claim physical mouse/keyboard interaction if unavailable.

---

# 54. Efficiency audit

Before commit, explicitly assess whether Prompt 05 followed Decision 08.

Record:

```text
review matrix
which specialists were invoked
why each was invoked
context each received
which reviewers were not invoked
whether any re-review occurred
why
reasoning level used
number of full-suite runs
whether full historical prompts were reread
```

Do not attempt to estimate hidden token counts.

The purpose is qualitative process evidence.

---

# 55. Final repository audit

Confirm:

* no new physical effect;
* no mid-flight parameter mutation;
* no physics timestep learner control;
* no motor editor;
* no new dependency;
* no GUI framework;
* no variable mass;
* no wind/atmosphere/stability/etc.;
* course updated;
* Decision 08 implemented;
* prompt archive policy updated;
* current defaults preserved;
* all tests pass;
* `git diff --check` passes.

---

# 56. Implementation commit

After all required review/validation gates pass, create the implementation commit.

Suggested message:

```text
Add interactive pre-launch laboratory controls
```

This commit should include:

* agent-efficiency workflow policy;
* Decision 08;
* setup UI;
* launch/reset/default controls;
* configuration wiring;
* tests;
* course updates;
* relevant documentation.

Do not include the Prompt 05 record yet.

---

# 57. Prompt 05 record — new compact provenance format

Create:

```text
docs/prompts/prompt_05_prelaunch_lab.md
```

using the actual repository naming convention.

Preserve this approved Prompt 05 verbatim.

Record:

* starting SHA;
* review matrix;
* specialist findings;
* implementation summary;
* files changed;
* tests/validation;
* visual validation;
* course updates;
* efficiency-policy evidence;
* Decision 08;
* implementation commit SHA;
* parent SHA;
* SHA-256 of the zero-context implementation diff;
* exact recovery command.

Do **not** embed the entire Git implementation patch by default.

Use:

```bash
git show --no-ext-diff --binary --format= <implementation-sha>
```

as the recorded exact-recovery command.

If there is a material user follow-up that changes requirements, preserve it.

Do not preserve routine resume instructions merely because an interruption occurred.

---

# 58. Prompt-record commit and push

Commit the Prompt 05 record separately.

Suggested message:

```text
Record prompt 05 pre-launch laboratory implementation
```

Then:

```bash
git push origin main
```

No force push.

Verify:

```bash
git status
git branch -vv
git log --oneline --decorate -n 10
git ls-remote origin refs/heads/main
```

Confirm:

* implementation commit;
* separate prompt-record commit;
* local/upstream/remote agreement;
* clean worktree.

---

# 59. Definition of done — interactive laboratory

Prompt 05 is complete only if:

* learners can modify selected physical parameters in READY;
* parameters use production `SimulationConfig`;
* no duplicate physical source of truth exists;
* mass, angle, `Cd`, area, density, and gravity are configurable;
* current thrust curve remains unchanged/read-only;
* mouse Launch exists;
* SPACE still launches;
* mouse/keyboard actions use common behavior;
* Reset Flight preserves selected setup;
* Restore Defaults restores actual defaults;
* controls lock after launch;
* controls unlock after reset;
* no arbitrary mid-flight physical changes are possible;
* angle preview reflects configured thrust direction;
* existing Inspector/timeline remain correct.

---

# 60. Definition of done — learning

Prompt 05 is complete only if:

* Living Rocketry Course is updated;
* new controlled-experiment lesson exists;
* mass experiment exists;
* drag experiment exists;
* launch-angle experiment exists;
* independent/dependent/controlled variables are taught;
* prediction → observation → explanation is reinforced;
* model/UI limitations are explicit;
* learning reviewer has no unresolved BLOCKING finding.

---

# 61. Definition of done — efficiency workflow

Prompt 05 is incomplete unless:

* `AGENTS.md` contains the new agent-context/review-efficiency policy;
* Decision 08 is accepted;
* core/focused/not-required review classification is implemented;
* specialists use targeted context rather than automatic full-history reading;
* selective re-review is implemented;
* High is established as normal reasoning default;
* staged validation is implemented;
* current-authoritative-document reading is preferred;
* compact resume behavior is documented;
* prompt records use Git-native provenance rather than embedded full patches by default;
* independent scientific derivations remain protected;
* Prompt 05 itself demonstrates the new workflow.

---

# 62. Do not begin Prompt 06

Prompt 06 is not automatically variable mass.

After Prompt 05, reassess the next educational/scientific need.

Strong candidates include:

```text
variable mass / propellant depletion
run comparison / experiment history
altitude-dependent atmosphere
constant wind
```

Do not implement any of them in Prompt 05.

---

# 63. Completion report

When finished, report:

1. starting repository/Git state;
2. Python environment;
3. Decision 08 path and policy summary;
4. changes to `AGENTS.md`;
5. new prompt-provenance policy;
6. review matrix;
7. specialists actually invoked;
8. specialists intentionally not invoked;
9. whether any re-review was required and why;
10. parent reasoning level used;
11. exposed setup parameters;
12. UI ranges/increments;
13. immutable configuration update design;
14. launch-button behavior;
15. keyboard equivalence;
16. Reset Flight semantics;
17. Restore Defaults semantics;
18. configuration locking;
19. launch-angle preview;
20. motor preservation;
21. regression result for default Prompt 04 run;
22. new behavioral tests;
23. final complete pytest result;
24. SDL/visual validation;
25. Living Rocketry Course changes;
26. Lesson 10 structure;
27. controlled mass experiment;
28. controlled drag experiment;
29. controlled launch-angle experiment;
30. learning review result;
31. test review result;
32. focused physics review result;
33. review-driven corrections;
34. full-suite run count during Prompt 05;
35. historical-prompt rereading performed, if any, and why;
36. final documentation updates;
37. `git diff --check`;
38. implementation commit SHA/message;
39. implementation parent SHA;
40. implementation-diff SHA-256;
41. exact Git recovery command;
42. Prompt 05 record path;
43. prompt-record commit SHA/message;
44. push result;
45. final local/upstream/remote SHA;
46. final clean working-tree status;
47. remaining UI/scientific limitations;
48. recommended candidates for Prompt 06.

Do not begin Prompt 06.
