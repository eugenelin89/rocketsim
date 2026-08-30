# Physics Model

## Implemented Milestone 3 model

RocketSim models one constant-mass point rocket in a two-dimensional flat world. It uses SI units internally:

- position: metres (m)
- time: seconds (s)
- velocity: metres per second (m/s)
- acceleration: metres per second squared (m/s^2)
- mass: kilograms (kg)
- force: newtons (N)
- density: kilograms per cubic metre (kg/m^3)
- reference area: square metres (m^2)
- angle: radians

World +x is horizontal/right, world +y is upward, and the ground is `y = 0`. Screen-coordinate inversion exists only in the renderer.

## State and configuration

Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, one immutable sampled thrust curve, fixed world launch angle, gravity magnitude, constant air density, constant drag coefficient, constant reference area, fixed outer physics timestep, and initial position and velocity.

All scalar and vector inputs must be finite. Mass and timestep must be positive. Gravity magnitude, air density, drag coefficient, reference area, sample times, and sample thrust values may be zero but not negative. Initial altitude may not be below ground. A normal thrust curve has at least two samples, begins at exactly `t=0`, and has strictly increasing times. The zero-duration limiting curve is the single sample `(0 s, 0 N)`.

The default aerodynamic values are educational constants:

```text
air density      1.225 kg/m^3
drag coefficient 0.75
reference area   0.01 m^2
```

They provide visible but modest drag for the default 1 kg scenario. They are not measurements or calibration of a specific vehicle.

## Air-relative velocity

Prompt 03 assumes still air. In general, rocket velocity relative to the air is conceptually:

```text
v_air = v_rocket_ground - v_air_ground
```

The modeled air is stationary, so `v_air_ground = (0, 0)` and therefore:

```text
v_air = v_rocket_ground
```

These are numerically equal in this milestone but are not interchangeable physical concepts. No wind vector exists in the implementation.

## Forces and acceleration

For constant mass `m > 0`, gravity magnitude `g >= 0`, time-varying thrust magnitude `T(t) >= 0`, fixed angle `theta`, curve-defined burnout time `t_b >= 0`, air density `rho >= 0`, drag coefficient `Cd >= 0`, reference area `A >= 0`, and air-relative velocity vector `v_air`:

```text
F_g = (0, -m g)
```

The fixed world thrust direction is:

```text
u_T = (cos(theta), sin(theta))
F_T(t) = T(t) u_T
```

For adjacent stored samples `(t_i,T_i)` and `(t_(i+1),T_(i+1))`, instantaneous thrust is piecewise linear:

```text
T(t) = T_i
       + (T_(i+1) - T_i)
         (t - t_i) / (t_(i+1) - t_i)
```

The burn interval remains exactly half-open:

```text
T(t) = 0  for t < 0
T(t_i) = T_i  at an interior knot
T(t) = 0  for t >= t_b
```

The final stored thrust is the left-limit endpoint of the last linear interval even if it is nonzero; it contributes to the final trapezoidal impulse although instantaneous thrust at exact burn end is zero.

Define:

```text
k = 0.5 rho Cd A
speed = |v_air|
```

Quadratic drag is:

```text
F_drag = -k |v_air| v_air
```

and has scalar magnitude:

```text
|F_drag| = 0.5 rho Cd A speed^2
```

At exactly zero air-relative speed, drag is exactly `(0, 0)`; no zero vector is normalized. If `rho`, `Cd`, or `A` is zero, drag is also exactly zero and the same force path reduces naturally to Prompt 02.

The vector equation works in every quadrant without phase-specific direction cases. For positive aerodynamic parameters and nonzero velocity:

```text
F_drag dot v_air = -k |v_air|^3 < 0
```

Drag therefore removes mechanical energy from the rocket's motion: it points downward during ascent and upward during descent. Thrust may still add energy during powered flight.

The complete force and acceleration equations are:

```text
F_net = F_T + F_g + F_drag
a = F_net / m
```

Production code exposes these named instantaneous vectors in one immutable `ForceBreakdown` for state telemetry and presentation. Integration uses the same gravity and drag helpers but replaces instantaneous thrust with the exact curve impulse over each internal segment, so thrust is not counted twice. Mass remains constant at ignition, burnout, coast, descent, and landing.

## Motor impulse and metrics

Total motor impulse is the exact area under the stored piecewise-linear curve:

```text
I_total = integral T(t) dt
        = sum[0.5 (T_i + T_(i+1)) (t_(i+1) - t_i)]
```

Impulse has units `N*s = kg*m/s`. Delivered impulse clamps the query time to the represented burn:

```text
I_delivered(t) = integral from 0 to clamp(t, 0, t_b) of T(tau) d tau
```

It is zero before ignition, monotonic because thrust is non-negative, and equals total impulse at and after burn end. Average and peak thrust are:

```text
T_average = I_total / t_b  for t_b > 0
T_average = 0              for the zero-duration curve
T_peak,stored = max stored sample thrust
```

Piecewise-linear interpolation cannot exceed its endpoint samples, so this stored peak is the exact supremum of the represented polyline. If a unique nonzero peak occurs only at the final stored endpoint, it is a left-limit value rather than an attained value of the public half-open instantaneous function, because `T(t_b) = 0`. It is not a claim that sparse samples capture the true peak of a measured motor.

For constant mass with gravity and drag disabled, thrust impulse gives:

```text
delta_v = (I_total / m) u_T
```

With gravity and drag active, the general momentum balance also includes their impulses. Equal motor impulse alone need not produce the same trajectory.

## Numerical integration

The default fixed outer physics timestep remains `dt = 0.01 s`. Every outer step is split internally at each strictly crossed thrust-curve knot, including a non-aligned burn end. For one internal segment `[t_n,t_(n+1)]` of duration `h`, RocketSim integrates the represented linear thrust exactly while retaining the established explicit drag and semi-implicit position rules:

```text
J_T = integral from t_n to t_(n+1) of T(t) dt
    = 0.5 (T_left + T_right) h

F_other_start = F_g + F_drag(v_n)

v_(n+1) = v_n
            + (J_T / m) u_T
            + (F_other_start / m) h

p_(n+1) = p_n + v_(n+1) h
```

`T_left` and `T_right` above are the stored ordinates that bound the represented linear interval. On the final interval, a nonzero `T_right` is the burn-end left limit used by the trapezoid even though the public instantaneous value at exact burnout is zero.

The motor impulse contribution to velocity is exact for every completed internal segment of the stored polyline, and gravity's velocity impulse is exact because gravity is constant. Position is not exact, and drag remains frozen from segment-start velocity. Prompt 02's constant-acceleration identity:

```text
p_numerical - p_analytical = 0.5 a t dt
```

continues to apply to the zero-drag constant-acceleration limit, but not generally with active drag. Active-drag accuracy is established by direct comparison with a nonlinear analytical solution and measured timestep convergence.

If a configured outer step crosses one or more curve knots, every boundary produces a completed internal segment and drag is reevaluated from the updated boundary velocity. A state at exact burnout reports zero thrust and force/acceleration evaluated from its burnout velocity. The outer wall-time accumulator and physics-step count still advance once per configured outer timestep.

Because curve knots are numerical boundaries, adding a redundant collinear sample can introduce an extra drag/position update even though it leaves `T(t)` and motor impulse unchanged. The immutable sample set is therefore part of the numerical configuration. Convergence comparisons keep the same knot set.

Recorded acceleration is always the instantaneous force result for the recorded state's time and velocity, not the acceleration frozen over the preceding segment. This also applies to the interpolated impact velocity.

The drag update is explicit with respect to velocity and is not unconditionally stable. A useful drag-only nondimensional step measure is:

```text
q = k |v| dt / m
```

Large `q` can cause an unphysical one-step reversal, oscillation, or growth. The default case keeps `q` small; no arbitrary speed or force clamp hides timestep instability.

## Vertical quadratic-drag analytical reference

For vertical fall from rest in still air with positive `m`, `g`, and `k`, define the terminal downward speed magnitude:

```text
v_terminal = sqrt(m g / k)
           = sqrt(2 m g / (rho Cd A))
```

With +y upward and initial altitude `y0`:

```text
v_y(t) = -v_terminal tanh(g t / v_terminal)

y(t) = y0
       - (v_terminal^2 / g)
         ln(cosh(g t / v_terminal))
```

At `v_y = -v_terminal`, upward drag balances downward weight and net vertical acceleration is zero. A smaller downward speed produces downward acceleration; a larger downward speed produces upward restoring acceleration. Terminal speed is an equilibrium, not a clamp.

## Ground boundary and lifecycle presentation

Ground admission, liftoff, and landing retain Prompt 02 semantics. A ground start must have non-negative initial vertical velocity and a positive first propulsion-aware internal numerical endpoint. That endpoint uses exact curve impulse plus gravity and start-velocity drag; it does not sample only `T(0)`. RocketSim still has no launch-pad, rail, normal-force, or hold-down model.

The original proposed educational curve began at zero thrust and would move below ground in the first free-flight timestep. It is therefore retained only as an airborne or zero-gravity validation example, not as the ground-launch default. The actual default begins at `12 N`, above the default rocket's `9.81 N` weight. This is a model-scope correction, not a hidden ground clamp.

After liftoff, the first descending numerical segment that crosses `y = 0` is linearly interpolated in time, horizontal position, and velocity; altitude is set to exactly zero and the state becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact root. If impact occurs during time-varying thrust, the interpolated impact velocity is not claimed to equal an exact partial-segment impulse solution. Current forces and delivered impulse are nevertheless recomputed from the reported impact time and velocity.

A post-liftoff landed state represents the instant of impact. Its displayed drag is evaluated from the nonzero interpolated impact velocity, although no later motion is integrated. An unsupported ground start instead becomes a terminal no-liftoff initial state; it is not labeled as impact, and its force/acceleration snapshot describes the attempted launch. Before launch, READY deliberately reports zero/inactive forces and zero stored acceleration rather than implying thrust is already active or inventing an unmodeled pad-support force.

## Implemented default scenario

```text
mass              1.0 kg
sampled thrust    (0.00 s, 12 N)
                  (0.05 s, 28 N)
                  (0.12 s, 24 N)
                  (0.35 s, 20 N)
                  (0.70 s, 16 N)
                  (0.95 s,  8 N)
                  (1.05 s,  0 N)
burn duration     1.05 s
total impulse     17.58 N*s
peak thrust       28.0 N
average thrust    16.742857... N
launch angle      pi/2 rad (vertical)
gravity           9.81 m/s^2
air density       1.225 kg/m^3
drag coefficient  0.75
reference area    0.01 m^2
physics timestep  0.01 s
```

The thrust curve is self-authored synthetic educational data, not measurement or certification of a commercial motor. For this educational approximation, the vertical terminal speed under gravity alone is about `46.21 m/s`. The default flight remains capable of liftoff without a pad-support rule.

## Pre-launch configuration boundary

Prompt 05 changes how an existing `SimulationConfig` is selected, not the equations above. While READY, the learner may replace the complete immutable configuration through controls for mass, fixed world thrust direction, `Cd`, effective reference area, constant air density, and constant gravitational magnitude. Direction is displayed in degrees but converted to the same internal radians used by `u_T = (cos(theta), sin(theta))`.

After launch, the owned configuration cannot be replaced in powered, paused, coast, or landed states. Every selected scalar—and especially mass—remains constant for the entire run. Reset Flight rebuilds the run under the same selected configuration; Restore Defaults while READY creates the exact implemented default configuration. Neither action changes the curve physics, scales thrust with mass, or introduces propellant depletion.

The setup ranges are presentation constraints for classroom usability, not physical validation limits. Their broad combinations intentionally include zero-drag and zero-gravity limiting cases as well as configurations that fail the existing impulse-aware ground-admission rule. No hidden launchability correction, support force, rail, or hold-down is added. The READY direction guide has no force magnitude and represents fixed thrust direction only, not attitude or rotation.

## Explicit omissions and interpretation limits

The model has no wind, altitude-varying density, pressure or temperature, lift, orientation-dependent area, variable `Cd`, Mach/Reynolds/compressibility effects, propellant depletion, variable mass, measured motor-data import, pad or launch-rail contact, attitude change, rotation, aerodynamic stability, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. Its single direction-independent effective area makes it an isotropic point-mass drag approximation.

No empirical game-feel constants or clamps are applied. The model assumes physically meaningful finite inputs; extreme finite combinations can exceed floating-point range and are not a claim of physical applicability. Results are a validated learning model, not calibrated real-flight or engineering-grade predictions.
