# Learning Rocketry with RocketSim

RocketSim is your physics laboratory. It lets you predict a rocket's motion, observe the modeled forces and state, and explain why the motion followed. It is deliberately simple enough that every displayed quantity can be connected to an equation.

This course is written for a motivated high-school student or beginning undergraduate who knows basic algebra. Physical intuition comes first; vectors, equations, and numerical evidence follow.

You do not need prior calculus. A few supplied symbols are reading aids: `pi/2 rad` means `90 degrees`; `u_T` is a unit vector that points in the thrust direction; an integral means accumulated graph area; and `tanh` is a Python/calculator function used for one validation reference whose derivation is beyond this introductory course.

RocketSim is not a certified launch predictor. Its value is that its assumptions are visible and testable.

## How to use this course

Most activities follow this rhythm:

```text
Predict → Control → Launch → Observe → Explain
```

Before running an activity, write down what you expect. Identify which setup value you will change and which values you will hold constant. During the run, record actual numbers and signs. Afterward, use forces and equations—not visual plausibility alone—to explain the result.

Scientific truth for the implemented model lives in `docs/PHYSICS_MODEL.md`. Validation methods and quantitative evidence live in `docs/VALIDATION.md`. This course explains those sources for learners.

---

# Part I — Foundations

## 1. RocketSim as a Physics Laboratory

### What are we trying to understand?

How can a simulator help us learn physics without confusing a mathematical model with nature?

### Physical intuition

A rocket animation can look convincing and still be wrong. A scientific simulation should let you ask:

- Which forces are active?
- What values and units do they have?
- Which equation combines them?
- Which assumptions were omitted?
- Does a simpler case agree with an answer we can derive independently?

RocketSim exposes those questions through its Physics Inspector, force arrows, motor timeline, and deterministic stepping.

### REAL-WORLD PHYSICS

A real rocket rests on a launch pad or rail, burns propellant, moves through changing atmosphere, rotates, and may deploy recovery hardware. Measurements have uncertainty. A drawing of a rocket also has an attitude and shape.

### ROCKETSIM MODEL

The current rocket is a constant-mass point in a flat 2D world. It has no pad-support or rail force, no rotation, and no recovery system. The rocket-shaped marker shows position; its drawn orientation is not simulated attitude.

Before launch, READY deliberately displays inactive zero forces and zero stored acceleration. This is an interface state, not a claim that gravity disappeared or that a solved pad equilibrium exists.

### Controls

The app first asks you to choose **Sandbox** or **Missions**. Lessons 1–10 use Sandbox, where all six educational setup controls are available. Lesson 11 introduces Mission Mode.

```text
SPACE  launch; pause or resume a live flight (same as the primary mouse button)
RIGHT  advance one outer physics step only while a live flight is paused
R      Reset Flight: return to READY and preserve the selected setup
F      show or hide force vectors
I      show or hide the Physics Inspector
ESC    exit
```

Sandbox's PRE-LAUNCH LAB panel is active only in READY. Its `-` and `+` controls select mass, fixed thrust direction, `Cd`, reference area, constant air density, and constant gravity. The large mouse button performs the same Launch/Pause/Resume action as `SPACE`. **Reset Flight** clears flight state and trajectory but preserves those selected values. **Restore Defaults** is a different READY-only action that restores the exact production defaults. The panel reports the current motor/impulse and `Physics dt`, but both are read-only.

After launch, physical setup controls lock because changing them would be an unmodeled intervention during flight. Reset Flight unlocks them. `F` and `I` change presentation only. `RIGHT` does not act while READY, while running, or after landing.

Whenever an activity says to begin from **the default**, click **Restore Defaults** first. Reset Flight alone does not recover defaults after you have changed a setup value.

### Try it in RocketSim

Run:

```bash
conda run -n rocketsim python -m rocket_sim
```

#### Predict

Will hiding force arrows or the Inspector change the trajectory? Will reset produce the same run?

#### Observe

1. Confirm the panel says READY TO CONFIGURE, then click **Restore Defaults**.
2. Press `SPACE` or click **LAUNCH**.
3. Press `F`, then `I`, while the rocket flies.
4. Press `R` or click **RESET FLIGHT** after part or all of the flight.
5. Repeat the same launch without restoring defaults again.
6. If `F` or `I` left an overlay hidden, press that key again before continuing so both force vectors and the Inspector are visible.

#### Explain

The renderer reads simulation state and returns clicked actions but cannot modify physics. Reset Flight restores state, trajectory, outer-step count, and fractional wall-time accumulator while preserving the immutable selected configuration. It does not reset the renderer's `F` or `I` visibility toggles. The same configuration and elapsed-time sequence is deterministic. Restore Defaults replaces the READY configuration; it is not a flight-history operation.

### Check your understanding

1. Why is plausible animation insufficient evidence of correctness?
2. Why do READY's zero displayed forces not mean gravity ceased to exist?
3. What result would reveal that `F` or `I` had incorrectly changed physics?

---

## 2. Position, Velocity, and Acceleration

### Physical intuition

Position says where the rocket is. Velocity says how quickly and in which direction position is changing. Acceleration says how quickly velocity is changing.

A rocket can move upward while accelerating downward. That is exactly what happens during much of coast: upward velocity is being reduced by gravity and drag.

### Coordinate system and units

RocketSim uses SI units internally:

```text
+x  right
+y  upward
ground y = 0

position      metres (m)
velocity      metres per second (m/s)
acceleration  metres per second squared (m/s^2)
time          seconds (s)
```

Pygame screen coordinates increase downward. Only the renderer performs that inversion; stored world `+y` remains upward.

For a velocity vector:

```text
v = (vx, vy)
speed = |v| = sqrt(vx^2 + vy^2)
```

Velocity contains direction; speed does not.

### Try it in RocketSim

#### Predict

During coast ascent, what signs should `vy` and `ay` have?

#### Observe

1. Launch with `SPACE`.
2. Pause during upward coast with `SPACE`.
3. Record time, altitude, `vy`, speed, and `ay`.
4. Press `RIGHT` several times. Each press advances the configured `0.01 s` outer step and leaves the flight paused.

#### Explain

During upward coast, `vy > 0` while gravity and downward drag normally make `ay < 0`. The rocket is rising more slowly each step. Displayed endpoint acceleration is the instantaneous acceleration at that endpoint, not necessarily the exact average acceleration over the preceding step.

### Check your understanding

1. Can velocity be upward while acceleration is downward?
2. Can acceleration be zero while velocity is nonzero?
3. Why does screen-coordinate inversion not change the sign convention in the physics equations?

---

## 3. Forces and Newton's Second Law

### Physical intuition

A force changes momentum. Several forces can act at once, so direction matters. RocketSim adds force vectors and then divides their net by the constant mass.

Momentum is the vector

```text
p = m v
```

with units `kg*m/s`. Impulse changes momentum, and `1 N*s = 1 kg*m/s`.

### Governing equations

```text
F_net = sum of forces
a = F_net / m
```

Force uses newtons:

```text
1 N = 1 kg*m/s^2
```

The current forces are:

```text
F_net = F_thrust + F_gravity + F_drag
```

The Inspector shows components and magnitudes. Arrow lengths use one rendering-only pixels-per-newton scale; their positions and labels may be moved for readability without changing physical direction or magnitude.

### REAL-WORLD PHYSICS

Real rockets may also experience pad contact, rail forces, lift, aerodynamic moments, and recovery forces.

### ROCKETSIM MODEL

Only thrust, gravity, and quadratic drag are simulated. There is no hidden damping or “game feel” force.

### Try it in RocketSim

#### Predict

If the upward thrust arrow is longer than the downward gravity arrow, must acceleration be upward?

#### Observe

Pause during flight. Add the displayed x components and y components of thrust, gravity, and drag. Compare with displayed net force. Divide net components by the selected mass displayed in the Inspector and compare with acceleration. Small differences can appear because the Inspector rounds displayed decimals. If this activity is meant to use `1.000 kg`, click Restore Defaults before launch.

#### Explain

Thrust versus weight alone is not the full comparison once drag has a significant component. Newton's second law uses the complete vector sum.

### Check your understanding

1. What does zero net force imply about acceleration?
2. What does zero net force not imply about velocity?
3. Why can a large thrust coexist with downward acceleration in a nonvertical or high-drag situation?

---

## 4. Powered Flight

### Physical intuition

A motor pushes exhaust one way and the rocket gains momentum the other way. RocketSim does not model exhaust or combustion. It accepts a thrust magnitude versus time and applies it in one fixed world direction.

### Governing equations

```text
u_T = (cos(theta), sin(theta))
F_T(t) = T(t) u_T
F_g = (0, -m g)
```

After Restore Defaults, launch is vertical, so `theta = pi/2`. The default selected rocket mass is `1 kg`; its weight magnitude is:

```text
m g = (1 kg)(9.81 m/s^2) = 9.81 N
```

The default curve begins at `12 N`, so its free-flight initial vertical net force is positive before drag grows.

### REAL-WORLD PHYSICS

Real rockets lose mass as propellant burns. Their thrust direction follows the nozzle and changing attitude. A launch rail constrains early motion and supports the rocket before release.

### ROCKETSIM MODEL

Mass and thrust direction can be selected while READY, but both are constant for the entire flight. Thrust direction is fixed in world coordinates. There is no rail, pad reaction, hold-down, rotation, or thrust-vector control.

The READY line labeled **fixed thrust direction (not attitude)** uses the exact configured direction. Angle is measured counterclockwise from world `+x`: `90 deg` is upward and `60 deg` is up-right. The panel displays degrees for usability, while the physics equation continues using radians. The unrotated rocket-shaped marker is only a point-position symbol.

The launchable default starts above weight because a motor that begins at zero thrust would initially fall into the ground under this no-contact model. A separate airborne example in Lesson 9 safely demonstrates zero thrust at exact ignition.

### Try it in RocketSim

#### Predict

Must maximum acceleration occur at the same time as maximum thrust?

#### Observe

Click Restore Defaults, launch, pause during the declining portion of the motor timeline, and compare current thrust, weight, drag, net force, and acceleration. Single-step and watch thrust fall while it remains nonzero.

#### Explain

Acceleration depends on all active forces. As speed changes, drag changes. Peak thrust and peak acceleration therefore need not occur at the same time.

### Check your understanding

1. Why is `T > mg` incomplete for an angled launch with drag?
2. Which RocketSim assumption keeps the thrust direction unchanged?
3. What important launch-pad physics is absent?

---

## 5. Burnout, Coast, and Apogee

### Physical intuition

Burnout means motor thrust ends. It does not mean velocity instantly becomes zero. Momentum carries the rocket upward while gravity and drag reduce its upward velocity.

### Motor and flight phases

The motor interval is half-open:

```text
0 <= t < burn_end  ACTIVE motor interval
t >= burn_end      motor COMPLETE; instantaneous thrust zero
```

The flight uses READY, POWERED, COAST, and LANDED. POWERED describes the configured motor-time interval; it does not guarantee `T(t) > 0` at every possible sample.

At apogee in a purely vertical flight:

```text
vy = 0 momentarily
```

Gravity is not zero. Drag is zero at exactly zero air-relative speed, so the rocket accelerates downward. Apogee is not a separate displayed phase in the current simulator.

### Try it in RocketSim

#### Predict

What will happen to thrust, velocity, and acceleration at burnout?

#### Observe

1. Pause anywhere during the declining burn.
2. Press `RIGHT` through the burnout boundary.
3. Watch current thrust, motor phase, delivered impulse, net force, acceleration, velocity, and the trajectory color.
4. Resume and observe coast toward apogee.

#### Explain

Instantaneous thrust is exactly zero at the half-open endpoint. Total impulse stays fixed at its final value, and velocity remains continuous. A curve with a nonzero final left-limit thrust can produce an acceleration jump at burnout. The default curve instead tails continuously to zero, although its motor and flight phases still change at the endpoint.

Ground return is found by interpolating the first descending discrete segment that crosses `y=0`. It is not an exact continuous collision solution and there is no motion after impact.

### Check your understanding

1. Why can the rocket continue upward after burnout?
2. Which quantities are zero at vertical apogee, and which are not?
3. Why is impact time still timestep-sensitive?

---

## 6. Aerodynamic Drag

### Physical intuition

Moving through air pushes air aside. The air pushes back opposite the rocket's velocity relative to the air. Faster motion produces much more drag in the quadratic model.

### Governing equation

```text
v_air = v_rocket_ground - v_air_ground

F_drag = -0.5 rho Cd A |v_air| v_air
```

Units and meanings:

```text
rho  air density                 kg/m^3
Cd   drag coefficient            dimensionless
A    effective reference area    m^2
v_air air-relative velocity      m/s
```

The vector form gives magnitude:

```text
|F_drag| = 0.5 rho Cd A speed^2
```

If speed doubles, drag magnitude becomes four times as large. At zero air-relative speed, drag is exactly zero. The minus sign makes drag oppose the complete velocity vector in every direction.

### REAL-WORLD PHYSICS

Atmospheric density varies with altitude and weather. Wind changes air-relative velocity. `Cd` and effective area can vary with Mach number, Reynolds number, attitude, and shape.

### ROCKETSIM MODEL

Air is still. Density, `Cd`, and one direction-independent effective area remain constant. The default values are educational, not calibrated vehicle measurements:

```text
rho = 1.225 kg/m^3
Cd  = 0.75
A   = 0.01 m^2
```

These three constants can be selected in the READY setup panel. Selecting a different value changes a model input between flights; it does not model changing weather, shape, attitude, or atmosphere during a flight. `Cd=0` or `rho=0` reaches the exact no-drag limiting case through the existing equation.

### Try it in RocketSim

#### Predict

Which direction should drag point during vertical ascent? During vertical descent?

#### Observe

Click Restore Defaults. Use `F` to show arrows. Observe drag during powered ascent, coast ascent, and descent. Pause and compare the sign of `vy` with the sign of vertical drag.

#### Explain

During ascent, air-relative velocity points upward and drag points downward. During descent, velocity points downward and drag points upward. In general 2D motion, say “opposite the velocity vector,” not merely “up” or “down.”

### Check your understanding

1. Why does doubling speed quadruple drag magnitude in this model?
2. Why is drag zero at zero air-relative speed?
3. How would wind change `v_air`, even though wind is not implemented?

---

## 7. Terminal Velocity

### Physical intuition

As a falling object speeds up, upward drag grows. Eventually drag can balance weight. Then net acceleration is zero while the object continues downward at nonzero velocity.

For vertical unpowered descent:

```text
F_drag + F_g = 0
```

For positive `m`, `g`, `rho`, `Cd`, and `A`, the modeled terminal-speed magnitude is:

```text
v_terminal = sqrt(2 m g / (rho Cd A))
```

The velocity vector at downward equilibrium is `(0, -v_terminal)`.

Terminal velocity is an equilibrium approached by the equations, not a speed clamp. The default flight is not claimed to reach it.

### Headless laboratory activity

This validation case intentionally needs settings outside the compact classroom panel: a zero motor, `A=1.0 m^2`, initial altitude `100 m`, and `dt=0.005 s`. The learner UI does not edit motors, initial conditions, or timestep, and its area limit is `0.100 m^2`, so use this complete tested headless configuration from the repository root:

```bash
conda run --no-capture-output -n rocketsim python - <<'PY'
import math

from rocket_sim import Simulation, SimulationConfig, ThrustCurve, Vector2

simulation = Simulation(
    SimulationConfig(
        mass_kg=2.0,
        thrust_curve=ThrustCurve.zero(),
        gravity_m_s2=8.0,
        air_density_kg_m3=2.0,
        drag_coefficient=1.0,
        reference_area_m2=1.0,
        physics_dt_s=0.005,
        initial_position_m=Vector2(0.0, 100.0),
    )
)
simulation.launch()
for _ in range(200):
    simulation.step()

expected_vy = -4.0 * math.tanh(2.0)
print("simulated vy:", simulation.state.velocity_m_s.y)
print("analytical vy:", expected_vy)
print("terminal-speed magnitude:", 4.0)
PY
```

#### Predict

At `t=1 s`, should the downward speed already equal `4 m/s`, or still be approaching it?

#### Observe and explain

Compare numerical and analytical values. The remaining difference contains fixed-timestep numerical error. The constant-density terminal speed is a statement about this model, not a measured real rocket.

### Check your understanding

1. Can acceleration be zero while velocity is nonzero?
2. What force direction restores a fall faster than terminal speed?
3. Why does the model's terminal speed not establish a real rocket's terminal speed?

---

## 8. Current Model Limitations

Scientific modeling means knowing what was left out.

| REAL-WORLD PHYSICS | CURRENT ROCKETSIM MODEL |
| --- | --- |
| Rocket rests on a pad/rail before liftoff | No support, rail, hold-down, or normal-force model |
| Motors consume propellant | Selected mass remains constant throughout one run |
| Motor curves may be measured with uncertainty | Default curve is a self-authored synthetic polyline |
| Thrust direction follows attitude/nozzle | READY-selectable, then fixed world direction |
| Atmosphere changes with altitude/weather | READY-selectable, then constant density and still air |
| Wind changes air-relative velocity | No wind |
| `Cd` and area depend on flow and attitude | READY-selectable constants; isotropic effective area |
| Rockets rotate and have stability dynamics | 2D point mass; no rotation, CG, or CP |
| Lift and compressibility may matter | No lift, Mach, Reynolds, or compressibility effects |
| Recovery and contact dynamics occur | Interpolated terminal ground event; no recovery or bounce |
| Continuous dynamics | Fixed outer timestep with internal knot segments |
| Measurements and calibration have uncertainty | No calibration or uncertainty model |

Semi-implicit position stepping and explicit start-velocity drag are numerical approximations. Exact motor impulse does not make position, apogee, landing time, or impact exact. The stored knot set is part of the numerical configuration: redundant collinear knots leave the thrust polyline and impulse unchanged but cause extra drag and position updates, so an active-drag trajectory can differ slightly. Extreme timestep/speed combinations can make explicit quadratic-drag integration unstable; RocketSim applies no arbitrary clamp to hide that.

Results are not 3D flight dynamics, engineering certification, or safety advice.

### Check your understanding

1. Which missing effect would change mass during the burn?
2. Which missing effects would make the thrust direction change?
3. Why should an educational default curve never be called real motor data?

---

# Part II — Propulsion

## 9. Rocket Motors, Thrust Curves, and Impulse

### What are we trying to understand?

How does thrust that changes with time build momentum, and why are peak thrust, average thrust, and total impulse different?

### Physical intuition

Thrust is a force at an instant. Impulse measures force accumulated over time. On a thrust-versus-time graph, motor impulse is the area under the curve.

Two curves can reach the same peak but enclose different areas. Two curves can enclose the same area but deliver it at different times. With drag active, different delivery timing can create different trajectories because speed—and therefore drag—changes along the way.

### REAL-WORLD PHYSICS

Real motor thrust changes during ignition, pressure rise, propellant burn, and tail-off. Real curves are measured, have sampling and measurement uncertainty, and can contain features missed by sparse data. The rocket also loses propellant mass.

### ROCKETSIM MODEL

RocketSim stores immutable samples and joins adjacent points with straight lines. The default samples are self-authored educational data:

| time (s) | thrust (N) |
| ---: | ---: |
| 0.00 | 12 |
| 0.05 | 28 |
| 0.12 | 24 |
| 0.35 | 20 |
| 0.70 | 16 |
| 0.95 | 8 |
| 1.05 | 0 |

This is not a commercial, measured, or certified motor.

Mass remains exactly `1 kg` in a restored-default run. A different mass may be selected before another run, but it then remains constant for that entire run. There is no propellant depletion, mass flow, specific impulse, exhaust velocity, chamber pressure, nozzle model, or combustion chemistry.

### Sampled interpolation

Between adjacent samples:

```text
T(t) = T_i
       + (T_(i+1) - T_i)
         (t - t_i) / (t_(i+1) - t_i)
```

Boundary rules are:

```text
T(t) = 0 for t < 0
T(t_i) = stored T_i at interior knots
T(t) = 0 for t >= burn_end
burn interval = [0, burn_end)
```

The motor phase is based on time, not on whether a particular instantaneous value is positive.

### Total and delivered impulse

```text
I_total = integral T(t) dt

I_delivered(t)
  = integral from 0 to clamp(t, 0, burn_end) of T(tau) d tau
```

For a linear segment, area is a trapezoid:

```text
segment impulse
  = 0.5 (T_left + T_right) delta_t
```

The default areas are:

| interval (s) | impulse (N*s) |
| --- | ---: |
| 0.00–0.05 | 1.00 |
| 0.05–0.12 | 1.82 |
| 0.12–0.35 | 5.06 |
| 0.35–0.70 | 6.30 |
| 0.70–0.95 | 3.00 |
| 0.95–1.05 | 0.40 |

Therefore:

```text
burn duration  = 1.05 s
total impulse  = 17.58 N*s
peak thrust    = 28 N
average thrust = 17.58 / 1.05
               = 16.742857... N
```

Average thrust is area divided by duration, not generally the arithmetic mean of all sample values. Piecewise-linear interpolation cannot exceed its endpoints, so `28 N` is the exact peak of this stored polyline. Sparse samples could still miss a real motor's true peak.

### Impulse and momentum

The general vector relation is:

```text
J_net = integral F_net dt = delta_p
```

For RocketSim's constant mass:

```text
m delta_v = J_thrust + J_gravity + J_drag
```

Only when gravity and drag are removed does the isolated thrust result become:

```text
delta_v = (I_total / m) u_T
```

RocketSim integrates motor impulse exactly for its stored piecewise-linear curve on every completed internal segment. The trajectory is still a fixed-timestep approximation: position is semi-implicit, drag is evaluated from segment-start velocity, and impact is interpolated from the discrete path.

### Read the motor timeline

The horizontal axis is motor time; the vertical axis is thrust in newtons. Orange line segments and yellow points are the exact configured polyline. A nonzero final stored sample is shown as an open left-limit point plus a filled zero-thrust point at exact burnout. The default curve already ends at zero, so its endpoint is a single filled point. The green cursor follows simulation time during the burn. In coast it is clamped at the burn endpoint and explicitly labeled “clamped at burnout”; the Inspector continues showing actual flight time. The magenta marker identifies burn end.

The timeline uses the same production curve as physics. It does not keep a second graph-only curve.

In READY, the plot shows the configured motor but current thrust remains inactive at `0 N`. After launch at `t=0`, the active default thrust is `12 N`.

The Inspector distinguishes:

```text
Current thrust        T(t), N
Motor phase           READY / ACTIVE / COMPLETE
Burn-time progress    elapsed burn-time fraction
Delivered impulse     curve area delivered so far, N*s
Total impulse         complete curve area, N*s
Peak stored / average thrust N
```

Burn-time progress and delivered-impulse fraction are not the same for a nonuniform curve.

### Guided motor experiment

#### Predict

Before launching, write answers:

1. At which plotted sample is thrust largest?
2. Must acceleration be largest at that same time?
3. What does area under the curve represent?
4. What happens to thrust, impulse, and velocity at burnout?

#### Observe

1. Click Restore Defaults, then launch with `SPACE` or the mouse LAUNCH button.
2. Use the highest plotted sample and the stored-peak readout to identify the early `0.05 s` peak; do not try to catch it manually.
3. Pause anywhere in the broad declining-thrust interval and record the actual displayed time.
4. Record current thrust, delivered impulse, velocity, drag, net force, and acceleration.
5. Press `RIGHT` repeatedly. Confirm that time, cursor, current thrust, delivered impulse, force arrows, acceleration, and velocity update while the simulation remains paused.
6. Step through `1.05 s` burnout.
7. Resume into coast. Confirm current thrust stays zero, total impulse stays `17.58 N*s`, and the labeled motor cursor remains at burn end while actual flight time continues.

#### Explain

Connect the chain:

```text
thrust curve
→ motor impulse
→ momentum change
→ velocity
→ quadratic drag
→ trajectory
```

Thrust timing influences velocity timing. Because drag scales with speed squared, two equal-impulse curves can produce different drag histories and trajectories.

### Zero-at-ignition laboratory example

Instantaneous zero thrust does not imply zero impulse over every finite interval. The original proposed curve starts at `0 N` and reaches `28 N` at `0.05 s`. It cannot be the ground default because RocketSim has no pad support and its first free-flight step would move below ground. Use it above ground with gravity disabled:

```bash
conda run --no-capture-output -n rocketsim python - <<'PY'
from rocket_sim import Simulation, SimulationConfig, ThrustCurve, ThrustSample, Vector2

curve = ThrustCurve(
    ThrustSample(t, thrust)
    for t, thrust in (
        (0.00, 0),
        (0.05, 28),
        (0.12, 24),
        (0.35, 20),
        (0.70, 16),
        (0.95, 8),
        (1.05, 0),
    )
)
simulation = Simulation(
    SimulationConfig(
        thrust_curve=curve,
        gravity_m_s2=0.0,
        air_density_kg_m3=0.0,
        initial_position_m=Vector2(0.0, 10.0),
    )
)
simulation.launch()
for _ in range(110):
    simulation.step()

print("T(0):", curve.thrust_at(0.0), "N")
print("Impulse over first 0.01 s:", curve.impulse_between_ns(0.0, 0.01), "N*s")
print("Total impulse:", curve.total_impulse_ns, "N*s")
print("Final vertical velocity:", simulation.state.velocity_m_s.y, "m/s")
PY
```

Predict the four printed values before running. The independent expectations are:

```text
T(0)                         0 N
impulse over first 0.01 s    0.028 N*s
total impulse                17.28 N*s
final vertical velocity      17.28 m/s
```

The last equality uses `m=1 kg`, constant mass, vertical thrust, zero gravity, and zero drag. It is not a general statement for an actual flight.

### Check your understanding

1. Why are newtons and newton-seconds different quantities?
2. Why is average thrust not generally the mean of all listed thrust samples?
3. Can two motors have the same peak thrust but different total impulse?
4. With gravity and drag removed, what does equal total impulse imply for equal constant masses and directions?
5. Why can equal-impulse curves produce different trajectories when drag is active?
6. How can `T(0)=0` coexist with positive impulse over the next interval?
7. Which Prompt 04 quantities are exact for the stored curve, and which flight quantities remain numerical approximations?
8. Why does current RocketSim keep mass constant even though real motors consume propellant?

---

## 10. Designing Controlled Experiments in Sandbox

### What are we trying to understand?

How can changing one model input at a time reveal a cause-and-effect relationship without confusing several effects?

### The experimental roles

- The **independent variable** is the one setup value you deliberately change.
- A **dependent variable** is an observed result that may respond, such as acceleration, apogee, flight time, final horizontal position, or drag force.
- **Controlled variables** are every setup value held identical between runs.

Changing mass, angle, and drag coefficient together may make a dramatic trajectory, but it cannot tell you which change caused which part. RocketSim therefore supports a deliberate loop:

```text
PREDICT  What should change, in which direction, and why?
CONTROL  Restore a baseline; change one independent variable only.
LAUNCH   Run the same production model.
OBSERVE  Record Inspector values and visible outcomes.
EXPLAIN  Connect the difference to an implemented equation.
```

Sandbox has no automatic comparison history. Write each run's settings and observations before Reset Flight clears the trajectory. Reset Flight preserves your selected values for a repeat; Restore Defaults recovers the common baseline before a new experiment.

### What the six controls mean

| READY control | Range / step | Meaning during one run | What it does not add |
| --- | --- | --- | --- |
| mass | `0.1–10 kg` / `0.1 kg` | one constant point mass | propellant depletion, wet/dry mass |
| fixed thrust direction | `10–90 deg` / `5 deg` | `u_T=(cos(theta), sin(theta))`, angle from world `+x` | attitude, rail angle, rotation, stability |
| `Cd` | `0–2` / `0.05` | one constant isotropic drag coefficient | shape/Mach/Reynolds/attitude variation |
| reference area | `0.001–0.100 m^2` / `0.001 m^2` | one constant effective isotropic area | changing projected area or geometry |
| air density | `0–2 kg/m^3` / `0.05 kg/m^3` | one constant still-air density | weather, wind, altitude variation |
| gravity | `0–20 m/s^2` / `0.25 m/s^2` | one constant downward magnitude | spherical planets or altitude variation |

These are educational button ranges, not claims that nature is limited to them. Changing a model parameter is also not the same as constructing a real rocket that achieves it. The simulator includes no manufacturing constraints, measurement uncertainty, calibration uncertainty, or safety assessment. Its results remain predictions of the documented educational model.

The restored values `rho=1.225 kg/m^3` and `g=9.81 m/s^2` lie between the button step grids. The controls step from the current value, so `+` then `-` returns to the exact displayed default instead of snapping it to a different grid point.

### A valid result can be NO LIFTOFF—or no return

The full range is intentionally exploratory, not a promise that every combination flies. RocketSim has no pad support, rail, surface sliding, or hold-down. A heavy rocket, high gravity, or a shallow fixed thrust direction may fail the existing first-step ground-admission rule and enter **NO LIFTOFF** at `t=0`. With restored defaults, directions around `45 deg` and below do this. That is a result of this simplified free-flight boundary, not a broken button and not a realistic launch-pad prediction.

At the other limit, `g=0` with positive upward motion may never return to ground. Use Reset Flight to end that activity. `Cd=0` or `rho=0` removes drag from this model; it does not create a complete vacuum or spaceflight model.

### Experiment A — constant selected mass

Begin with Restore Defaults. These masses were chosen because both lift off under the no-pad boundary:

| setting | Run A | Run B |
| --- | ---: | ---: |
| mass — independent | `1.0 kg` | `1.2 kg` |
| direction — controlled | `90 deg` | `90 deg` |
| `Cd` — controlled | `0.75` | `0.75` |
| area — controlled | `0.010 m^2` | `0.010 m^2` |
| density — controlled | `1.225 kg/m^3` | `1.225 kg/m^3` |
| gravity — controlled | `9.81 m/s^2` | `9.81 m/s^2` |
| motor and physics timestep — controlled/read-only | default curve; `0.010 s` | default curve; `0.010 s` |

#### Predict

Which run should have greater launch acceleration and apogee? Will total motor impulse change? As an analytical instantaneous `t=0` prediction, before drag grows, compare `a_y = T/m - g` using `T(0)=12 N`: the model predicts `2.19 m/s^2` for Run A and `0.19 m/s^2` for Run B. Launch starts the running clock, so a manual pause will normally show a later time and a different rising-curve thrust. Use the `t=0` values to predict the sign and ordering, not as exact manually paused readouts.

#### Observe

1. Run A, pausing early to record actual time, mass, thrust, weight, net force, and acceleration. Check the predicted sign and cross-run ordering rather than expecting the exact `t=0` numbers.
2. Resume, visually note maximum height, and record landed flight time before Reset Flight.
3. Reset Flight, increase mass twice to `1.2 kg`, and confirm every other displayed setup value is unchanged.
4. Repeat the same observations for Run B.

For the current validated timestep, representative production results are about `8.103 m` versus `4.683 m` apogee and `3.058 s` versus `2.461 s` landed time. Use the Inspector and trajectory for your own run rather than treating rounded values as exact analytical answers.

#### Explain

The motor curve and its `17.58 N*s` total impulse are identical. More constant mass means less velocity change per unit net impulse. Drag history also changes indirectly: the slower velocity history changes the `speed^2` force even though `rho`, `Cd`, and area were controlled. Mass is different **between** runs but never decreases **within** either run.

### Experiment B — drag coefficient at a useful visible scale

Begin with Restore Defaults, then set area to `0.100 m^2` in both runs so the difference is readable at the current display scale:

| setting | Run A | Run B |
| --- | ---: | ---: |
| `Cd` — independent | `0.50` | `1.00` |
| area — controlled | `0.100 m^2` | `0.100 m^2` |
| mass, direction, density, gravity, motor, physics timestep | restored defaults | restored defaults |

#### Predict

At exactly equal velocity, doubling `Cd` doubles drag magnitude because:

```text
|F_drag| = 0.5 rho Cd A speed^2
```

Does that mean every trajectory result must scale by exactly two? Why not?

#### Observe

Run each case, recording both actual speed and drag at a roughly similar speed, qualitative trajectory height, and landed flight time. Treat the near-equal-speed observation as qualitative. For a cleaner numerical comparison, calculate `|F_drag|/speed^2` from each recorded pair; with controlled `rho` and area, that ratio should scale directly with `Cd`. Representative production results are about `7.190 m` versus `6.442 m` apogee and `2.919 s` versus `2.801 s` landed time. The current app does not retain Run A automatically, so record it before reset.

#### Explain

Equal-speed force comparison isolates the direct `Cd` factor. The complete trajectory does not scale linearly because changing drag changes velocity, which feeds back through `speed^2`, and thrust and gravity continue acting.

### Experiment C — fixed thrust direction

Begin with Restore Defaults:

| setting | Run A | Run B |
| --- | ---: | ---: |
| fixed direction — independent | `90 deg` | `60 deg` |
| every other setup value, motor, and physics timestep | restored defaults | restored defaults |

Immediately before interpreting this experiment, remember:

- angle is counterclockwise from world `+x`;
- `90 deg` is upward and `60 deg` is up-right;
- degrees are displayed, but radians are used internally;
- the same scalar `T(t)` is split into x and y components;
- the preview and rocket marker do not represent simulated attitude; and
- there is no rotation, stability, rail constraint, lift, or angle-dependent drag area.

#### Predict

For `60 deg`, which thrust component becomes positive horizontally? Is its vertical thrust component larger or smaller than for `90 deg`? Predict the sign of final horizontal position.

#### Observe

Run both cases. Compare thrust components just after launch, trajectory shape, apogee, and final x position. The current production model's `60 deg` run lands near `x=18.118 m`; the vertical run remains near `x=0`.

#### Explain

The motor did not become weaker. Its vector changed:

```text
F_Tx = T cos(theta)
F_Ty = T sin(theta)
```

At `60 deg`, some of the same thrust magnitude builds horizontal momentum, while the vertical component opposing weight is smaller. The new 2D trajectory follows fixed world components, not a rotating vehicle.

### Check your understanding

1. In the mass experiment, name the independent variable, at least two dependent variables, and the controlled conditions.
2. Why is `1.0 kg` versus `2.0 kg` a poor default experiment in this simulator?
3. Why should drag be compared at similar speed when isolating `Cd`?
4. Why does doubling `Cd` not simply halve the whole trajectory?
5. What exactly does the launch-direction preview represent?
6. Why are setup controls locked during a paused flight?
7. Which action repeats a selected experiment, and which recovers its baseline defaults?
8. Why are NO LIFTOFF and non-returning zero-gravity coast valid modeled outcomes but not complete real launch predictions?

---

## 11. Engineering Missions: Predict, Test, Explain, Iterate

### What are we trying to understand?

How can a constrained objective turn a controlled experiment into an engineering design cycle without changing the governing physics?

Mission Mode uses the same `Simulation`, motor, force equations, timestep, and ground event as Sandbox. The game layer follows this one-way chain:

```text
production simulation
→ completed FlightResult
→ objective evaluation
→ score and stars
→ results presentation
```

The score **evaluates** the production result. It never steers the rocket, changes gravity or drag, scales thrust, snaps a trajectory into a target, changes the timestep, or invents a landing. A miss remains a miss, and NO LIFTOFF has no ground-contact position or impact speed.

### The mission engineering loop

```text
PREDICT    Decide how the allowed variable should affect the objective.
CONSTRAIN  Identify every fixed value and the one value you may change.
LAUNCH     Run the unchanged production simulation after the countdown.
INSPECT    Read the recorded result and objective-by-objective feedback.
EXPLAIN    Connect success or failure to an implemented force or equation.
ITERATE    Retry with a purposeful change while holding constraints fixed.
```

The countdown is presentation time only. Simulation time remains `t=0` until ignition. During flight, an altitude objective may become known once the recorded trajectory reaches it. Ground-contact and impact outcomes remain pending until terminal contact because they do not exist earlier.

### What the five missions teach

| mission | allowed variable | physical question |
| --- | --- | --- |
| First Flight | constant vehicle mass | Can the same motor and gravity produce the required recorded apogee? |
| Precision Landing | fixed world thrust direction | How does splitting the same thrust into horizontal and vertical components change ground-contact position? |
| Heavy Lift Challenge | constant vehicle mass | How much total constant point mass can the unchanged motor lift above the altitude constraint? |
| Aerodynamic Challenge | constant `Cd` | How does drag feedback shift ground-contact position into or out of a target band? |
| Environmental Challenge | constant vehicle mass under fixed low `g` | How must mass change to meet an altitude band when modeled weight is lower? |

“Heavy Lift” does not introduce a payload model. The configured `mass_kg` remains one total constant point mass; there is no dry mass, propellant mass, or separate payload. “Precision Landing” means the simulator's interpolated first descending ground contact. It does not model recovery, bounce, structural survival, or real-world landing safety. Recorded apogee and maximum values are numerical maxima over stored states, not exact continuous-flight extrema.

### Guided mission activity — Precision Landing

#### Predict

Before changing the control, write down:

1. Is the starting `55 deg` direction expected to put more or less thrust horizontally than `60 deg`?
2. Will increasing the fixed direction increase or decrease the vertical thrust component?
3. Which values must remain fixed for the comparison to isolate direction?

Remember that the direction is measured counterclockwise from world `+x`. It is a fixed force direction, not simulated rocket attitude.

#### Observe

1. Complete First Flight once to unlock the next mission. Then choose Precision Landing and read the objective, constraints, hint, and scoring rule before configuring.
2. Run the mission once at its starting `55 deg`. Record ground-contact `x`, recorded apogee, modeled impact speed, and the “missed long/short” explanation.
3. Retry. Retry preserves the selected allowed value and clears the prior trajectory/result.
4. Change only the direction by one `5 deg` step and launch again.
5. Confirm the target is drawn in world coordinates and the landing objective remains pending until ground contact.

Representative production evidence is approximately:

```text
55 deg → ground-contact x = 19.124 m → beyond the 17.5–18.7 m zone
60 deg → ground-contact x = 18.118 m → inside the zone
```

Treat those values as results of the current documented numerical model, not analytical truths or real-flight predictions.

#### Explain

At `60 deg`, the thrust components are:

```text
F_Tx = T cos(60 deg)
F_Ty = T sin(60 deg)
```

Compared with `55 deg`, the horizontal fraction is smaller and the vertical fraction is larger. That changes horizontal acceleration and flight time together, so ground-contact distance is a trajectory result rather than a single-component calculation. The game awards points only after the production run supplies that result.

### Controlled environmental comparison

Environmental Challenge fixes `g=3.71 m/s^2` but does not claim to model a complete planet. With the same `1.0 kg` mass and all other current model values controlled, representative recorded apogees are about:

```text
default g = 9.81 m/s^2 → 8.10 m
fixed low g = 3.71 m/s^2 → 30.28 m
```

That comparison isolates the modeled constant-gravity change. The mission then asks you to retune mass to enter a `20–23 m` band; about `1.2 kg` produces `21.21 m` in the current production model.

### Check your understanding

1. Why must score calculation occur after, rather than inside, the physics update?
2. Which mission outcomes can become known during ascent, and which must remain pending?
3. Why is the Heavy Lift configured mass not a payload measurement?
4. Why can changing only `Cd` alter both drag and later velocity rather than shifting range linearly?
5. What does Retry preserve, and what does Mission Defaults restore?
6. Why does a low-gravity mission not by itself model Mars or another complete planet?
7. What evidence would show that Mission Mode secretly changed physics, and how could a Sandbox/Mission comparison detect it?

---

# Looking ahead without claiming implementation

Later approved milestones may add one validated effect at a time. If variable mass is added, Lessons 3, 4, 5, 8, and 9 must be revisited. If atmosphere changes with altitude, Lessons 6 and 7 must change. Wind would revise air-relative velocity. Rotation and stability would revise vectors, powered flight, drag, and the meaning of the rocket drawing.

Those features are not implemented now. The course evolves retroactively so older explanations never remain silently obsolete.
