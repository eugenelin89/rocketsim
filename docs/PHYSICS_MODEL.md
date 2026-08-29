# Physics Model

## Implemented Milestone 2 model

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

Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, thrust magnitude, burn duration, fixed world launch angle, gravity magnitude, constant air density, constant drag coefficient, constant reference area, fixed physics timestep, and initial position and velocity.

All scalar and vector inputs must be finite. Mass and timestep must be positive. Thrust, burn duration, gravity magnitude, air density, drag coefficient, and reference area may be zero but not negative. Initial altitude may not be below ground.

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

For constant mass `m > 0`, gravity magnitude `g >= 0`, thrust magnitude `T >= 0`, fixed angle `theta`, burnout time `t_b >= 0`, air density `rho >= 0`, drag coefficient `Cd >= 0`, reference area `A >= 0`, and air-relative velocity vector `v_air`:

```text
F_g = (0, -m g)
```

Thrust uses the exact half-open time interval:

```text
F_T(t) = T(cos(theta), sin(theta))  when 0 <= t < t_b
F_T(t) = (0, 0)                    otherwise
```

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

Production code exposes these named vectors in one immutable `ForceBreakdown`. Integration and presentation consume the same calculation. Mass remains constant at ignition, burnout, coast, descent, and landing.

## Numerical integration

The default fixed physics timestep remains `dt = 0.01 s`. For each numerical segment, all forces are evaluated from the segment's starting time and velocity. Semi-implicit Euler then updates velocity before position:

```text
F_n = F(t_n, v_n)
a_n = F_n / m
v_(n+1) = v_n + a_n dt
p_(n+1) = p_n + v_(n+1) dt
```

Drag depends on velocity, so acceleration is not constant over the true continuous interval. The method freezes it only for one numerical segment. Prompt 02's constant-acceleration identity:

```text
p_numerical - p_analytical = 0.5 a t dt
```

continues to apply to the zero-drag constant-acceleration limit, but not generally with active drag. Active-drag accuracy is established by direct comparison with a nonlinear analytical solution and measured timestep convergence.

If a configured step begins before burnout and ends after it, the simulator performs a powered substep ending exactly at `t_b`, followed by a coast substep for the remainder. The coast substep reevaluates drag from the updated burnout velocity. A state at exact burnout reports zero thrust and force/acceleration evaluated from its burnout velocity.

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

Ground admission, liftoff, and landing retain Prompt 02 semantics. A ground start must have non-negative initial vertical velocity and a positive first drag-inclusive numerical endpoint. After liftoff, the first descending numerical segment that crosses `y = 0` is linearly interpolated in time, horizontal position, and velocity; altitude is set to exactly zero and the state becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact root.

A post-liftoff landed state represents the instant of impact. Its displayed drag is evaluated from the nonzero interpolated impact velocity, although no later motion is integrated. An unsupported ground start instead becomes a terminal no-liftoff initial state; it is not labeled as impact, and its force/acceleration snapshot describes the attempted launch. Before launch, READY deliberately reports zero/inactive forces and zero stored acceleration rather than implying thrust is already active or inventing an unmodeled pad-support force.

## Implemented default scenario

```text
mass              1.0 kg
thrust            20.0 N
burn duration     1.0 s
launch angle      pi/2 rad (vertical)
gravity           9.81 m/s^2
air density       1.225 kg/m^3
drag coefficient  0.75
reference area    0.01 m^2
physics timestep  0.01 s
```

For this educational approximation, the vertical terminal speed under gravity alone is about `46.21 m/s`. The default flight remains capable of liftoff.

## Explicit omissions and interpretation limits

The model has no wind, altitude-varying density, pressure or temperature, lift, orientation-dependent area, variable `Cd`, Mach/Reynolds/compressibility effects, propellant depletion, variable mass, sampled thrust curve, attitude change, rotation, aerodynamic stability, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. Its single direction-independent effective area makes it an isotropic point-mass drag approximation.

No empirical game-feel constants or clamps are applied. The model assumes physically meaningful finite inputs; extreme finite combinations can exceed floating-point range and are not a claim of physical applicability. Results are a validated learning model, not calibrated real-flight or engineering-grade predictions.
