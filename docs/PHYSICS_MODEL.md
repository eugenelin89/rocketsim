# Physics Model

## Implemented Milestone 1 model

RocketSim currently models one constant-mass point rocket in a two-dimensional flat world. It uses SI units internally:

- position: metres (m)
- time: seconds (s)
- velocity: metres per second (m/s)
- acceleration: metres per second squared (m/s²)
- mass: kilograms (kg)
- force: newtons (N)
- angle: radians

World +x is horizontal/right, world +y is upward, and the ground is `y = 0`. Screen-coordinate inversion exists only in the renderer.

## State and configuration

Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, thrust magnitude, burn duration, fixed world launch angle, gravity magnitude, fixed physics timestep, and initial position and velocity.

All scalar and vector inputs must be finite. Mass and timestep must be positive. Thrust, burn duration, and gravity magnitude may be zero but not negative. Initial altitude may not be below ground.

## Forces and acceleration

For constant mass `m > 0`, gravity magnitude `g >= 0`, thrust magnitude `T >= 0`, fixed launch angle `theta`, and burn duration `t_b >= 0`:

```text
F_g = (0, -m g)
```

Thrust uses an exact half-open time interval:

```text
F_T(t) = T(cos(theta), sin(theta))  when 0 <= t < t_b
F_T(t) = (0, 0)                    otherwise
```

Negative time never produces thrust. Net acceleration is:

```text
a(t) = (F_T(t) + F_g) / m
```

Therefore the powered and coast accelerations are:

```text
a_power = (T cos(theta) / m, T sin(theta) / m - g)
a_coast = (0, -g)
```

Mass does not change at ignition, burnout, coast, or landing.

## Numerical integration

The default fixed physics timestep is `dt = 0.01 s`. Every interval over which acceleration is constant uses semi-implicit Euler in this exact order:

```text
v_next = v_current + a_current dt
p_next = p_current + v_next dt
```

If a configured step begins before burnout and ends after it, the simulator performs a powered substep ending exactly at `t_b`, followed by a coast substep for the remaining duration. A step ending exactly at burnout is powered for its entire interval; the resulting state at `t_b` reports coast phase and coast acceleration. A step starting at burnout is entirely coast.

For constant acceleration over `t = N dt`, velocity is exact apart from floating-point roundoff. Semi-implicit position differs from the continuous solution by:

```text
p_numerical - p_analytical = 0.5 a t dt
```

Position is therefore first-order accurate: its error should approximately halve when `dt` halves.

## Continuous analytical references

For a constant acceleration `a` over duration `t`:

```text
v(t) = v0 + a t
p(t) = p0 + v0 t + 0.5 a t²
```

For a powered/coast case, evaluate those equations with `a_power` through `t_b` to obtain `p_b` and `v_b`, then with `a_coast` for `tau = t - t_b`:

```text
v(t) = v_b + a_coast tau
p(t) = p_b + v_b tau + 0.5 a_coast tau²
```

These continuous equations are the independent test oracle, with tolerances derived from the known Euler position error.

## Ground boundary

Landing cannot trigger merely because the initial position is on the ground. The state first has to attain positive altitude. On the first later descending numerical segment whose endpoints cross from `y > 0` to `y <= 0`, the simulator linearly interpolates time, horizontal position, and velocity between the discrete endpoints, sets altitude to exactly zero, and enters a terminal landed phase. Any remainder of that physics step is discarded.

This is deterministic event interpolation, not an exact root solve. Landing time, range, and impact velocity remain timestep-sensitive and must not be reported as exact.

A configuration starting on the ground is accepted only when its initial vertical velocity is non-negative and the endpoint of its first constant-force numerical segment is above ground. A downward initial velocity or a short flight that is too under-resolved to produce a positive first endpoint terminates at the initial ground state without recording negative altitude. Holding or resolving such a rocket on a pad would require an unimplemented contact/normal-force model. Gravity-only and zero-thrust analytical cases therefore start above ground or use a timestep that resolves their upward motion.

The terminal state represents the instant of impact. If impact occurs before burnout, its instantaneous acceleration and reported thrust still follow the half-open burn model at that impact time; no later motion is integrated.

## Implemented default scenario

```text
mass              1.0 kg
thrust            20.0 N
burn duration     1.0 s
launch angle      pi/2 rad (vertical)
gravity           9.81 m/s²
physics timestep  0.01 s
```

The continuous powered acceleration is `10.19 m/s²` upward, so this scenario leaves the ground.

## Explicit omissions

The model has no aerodynamic drag, wind, atmospheric variation, propellant depletion, variable mass, sampled thrust curve, attitude change, rotation, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. No empirical game-feel constants or clamps are applied.

These omissions bound the meaning of results. The 2D point-mass trajectory is a validated learning model, not a calibrated real-flight or engineering-grade prediction.
