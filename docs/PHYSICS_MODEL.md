# Physics Model

## Purpose

This document defines the physical assumptions, equations, variables, and staged fidelity of the rocket simulator.

The simulator should use SI units internally:

- Position: metres (m)
- Time: seconds (s)
- Velocity: metres per second (m/s)
- Acceleration: metres per second squared (m/s²)
- Mass: kilograms (kg)
- Force: newtons (N)
- Angle: radians internally

Screen pixels should never be used as physics units.

---

## Coordinate System

Use a two-dimensional Cartesian coordinate system:

- +x = horizontal right
- +y = upward
- Ground = y = 0

Pygame screen coordinates increase downward, so the renderer must convert simulation coordinates to screen coordinates.

---

## Core State Variables

At minimum, the rocket state should contain:

```text
time
position_x
position_y
velocity_x
velocity_y
mass
```

Later versions may add:

```text
angle
angular_velocity
propellant_mass
acceleration_x
acceleration_y
mach_number
```

---

## Milestone 1 Physics

### Gravity

Assume constant gravitational acceleration:

```text
g = 9.81 m/s²
```

The gravitational force is:

```text
F_gravity = m g
```

acting downward.

In vector form:

```text
F_g = (0, -m g)
```

### Thrust

For the first implementation, assume constant thrust during the motor burn.

For thrust magnitude `T` and launch angle `theta`:

```text
F_thrust_x = T cos(theta)
F_thrust_y = T sin(theta)
```

After burnout:

```text
T = 0
```

### Net Force

```text
F_net = F_thrust + F_gravity
```

### Acceleration

Newton's second law:

```text
a = F_net / m
```

Therefore:

```text
a_x = F_net_x / m
a_y = F_net_y / m
```

---

## Numerical Integration

Use a fixed simulation timestep `dt` initially.

Recommended starting value:

```text
dt = 0.01 s
```

Use semi-implicit Euler integration:

```text
v_new = v_old + a * dt
x_new = x_old + v_new * dt
```

This is preferable to updating position using the old velocity because it is generally more stable for simple real-time simulations.

The physics timestep should be independent from the graphical frame rate if possible.

---

## Milestone 2: Aerodynamic Drag

Drag magnitude:

```text
F_drag = 0.5 * rho * C_d * A * v²
```

where:

- `rho` = air density
- `C_d` = drag coefficient
- `A` = reference/frontal area
- `v` = speed

Drag must point opposite the velocity vector.

For speed:

```text
v = sqrt(v_x² + v_y²)
```

If `v > 0`:

```text
F_drag_x = -F_drag * v_x / v
F_drag_y = -F_drag * v_y / v
```

Initial simplification:

```text
rho = 1.225 kg/m³
```

at sea level.

---

## Milestone 3: Variable Mass

Model propellant consumption during motor burn.

A simple first model:

```text
mass(t) = dry_mass + remaining_propellant_mass
```

For constant mass flow:

```text
propellant_mass_remaining = initial_propellant_mass - mass_flow_rate * t
```

Clamp remaining propellant mass to zero.

The reduced mass should automatically increase acceleration for the same thrust.

---

## Milestone 4: Real Motor Thrust Curve

Replace constant thrust with a time-dependent motor curve.

Example data:

```text
time_s,thrust_N
0.00,0
0.05,25
0.10,40
0.30,35
0.60,20
0.80,0
```

Interpolate between samples to obtain thrust at simulation time.

Possible future source: published model rocket motor test data.

---

## Milestone 5: Atmospheric Model

Allow air density to decrease with altitude.

A simple approximation can be introduced first. A more realistic standard-atmosphere model can be added later.

Potential variables:

```text
temperature
pressure
air_density
speed_of_sound
```

Mach number:

```text
Mach = speed / speed_of_sound
```

---

## Milestone 6: Attitude and Stability

Once translational motion is reliable, introduce rocket orientation.

State variables:

```text
angle theta
angular_velocity omega
angular_acceleration alpha
```

Rotational dynamics:

```text
torque = I * alpha
```

or:

```text
alpha = torque / I
```

Eventually, aerodynamic force should depend on angle of attack, center of pressure, and center of mass.

This milestone is a major increase in complexity and should not be started until earlier models are validated.

---

## Ground Interaction

The simulation begins with:

```text
y = 0
```

After launch, if the rocket returns to:

```text
y <= 0
```

and is descending, the flight should end.

For the first version, no bounce or impact dynamics are needed.

---

## Important Assumptions to Track

Every simulation run should make clear which assumptions are active.

Examples:

- Flat Earth over short range.
- Constant `g`.
- No Coriolis force.
- No wind unless enabled.
- Rocket treated as a point mass until attitude dynamics are added.
- Constant drag coefficient unless otherwise specified.
- No transonic aerodynamic correction unless explicitly implemented.

These assumptions should eventually appear in exported experiment metadata.
