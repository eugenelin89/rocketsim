# Software Architecture

## Objective

The simulator should be designed so that the physics can run independently of Pygame. Pygame should be a visualization and input layer, not the physics engine itself.

This separation will make it easier to:

- test the physics,
- run simulations faster than real time,
- run parameter sweeps,
- compare models,
- add alternative visualizations later,
- and potentially reuse the simulator for autonomous-control experiments.

---

## Proposed Components

### `main.py`

Responsibilities:

- Initialize Pygame.
- Create the simulation.
- Run the application loop.
- Handle top-level user input.
- Coordinate physics updates and rendering.

It should contain as little physics logic as possible.

### `simulation.py`

Responsibilities:

- Own simulation time.
- Advance the simulation by a timestep.
- Coordinate forces and environment.
- Determine when a flight starts and ends.
- Record trajectory/history data.

Possible interface:

```python
simulation.step(dt)
simulation.reset()
simulation.is_finished
```

### `rocket.py`

Responsibilities:

- Store rocket physical properties.
- Store current rocket state.
- Update state from calculated forces.

Possible properties:

```text
position
velocity
mass
dry_mass
reference_area
drag_coefficient
```

Later:

```text
angle
angular_velocity
moment_of_inertia
center_of_mass
center_of_pressure
```

### `motor.py`

Responsibilities:

- Motor burn duration.
- Thrust as a function of time.
- Propellant mass.
- Mass flow.

Possible interface:

```python
motor.thrust_at(t)
motor.propellant_mass_at(t)
motor.is_burning(t)
```

### `environment.py`

Responsibilities:

- Gravity.
- Air density.
- Wind.
- Atmospheric properties.

Possible interface:

```python
environment.gravity_at(position)
environment.air_density_at(altitude)
environment.wind_at(altitude, time)
```

### `renderer.py`

Responsibilities:

- Convert world coordinates to screen coordinates.
- Draw rocket.
- Draw trajectory.
- Draw ground.
- Draw telemetry.
- Draw force vectors when enabled.

The renderer must not modify physical state.

### `config.py`

Responsibilities:

- Store initial simulation parameters.
- Keep tuning values out of physics code.

Example configuration:

```python
ROCKET_MASS_KG = 1.5
THRUST_N = 35.0
BURN_TIME_S = 1.0
LAUNCH_ANGLE_DEG = 85.0
PHYSICS_DT = 0.01
```

Eventually, replace or supplement this with JSON/TOML experiment configuration files.

---

## Main Loop

Conceptually:

```text
initialize

while running:
    process user input

    accumulate real elapsed time

    while accumulated_time >= physics_dt:
        simulation.step(physics_dt)
        accumulated_time -= physics_dt

    renderer.draw(simulation)
    display frame
```

This fixed-timestep structure prevents simulation results from changing significantly when graphical frame rate changes.

---

## Data Flow

```text
User Input
    ↓
Configuration
    ↓
Simulation
    ↓
Rocket + Motor + Environment
    ↓
Force Calculation
    ↓
Numerical Integration
    ↓
Updated Rocket State
    ↓
Renderer
    ↓
Pygame Display
```

Trajectory data should also be stored separately for later plotting and analysis.

---

## Design Rules

### Rule 1: SI units internally

Never mix screen pixels with metres.

### Rule 2: Renderer does not own physics

Changing zoom or window size must not change simulation results.

### Rule 3: Fixed physics timestep

Physics should not depend directly on FPS.

### Rule 4: One source of truth for state

Rocket position and velocity should be stored in one location only.

### Rule 5: Keep models replaceable

For example, `ConstantThrustMotor` should later be replaceable by `ThrustCurveMotor` without rewriting the simulation.

### Rule 6: Record experiment parameters

A result is not scientifically useful if the simulator cannot reproduce the run.

---

## Suggested First Classes

```text
Vector2 / pygame.math.Vector2
Rocket
Motor
Environment
Simulation
Renderer
```

Using `pygame.math.Vector2` is acceptable for vector arithmetic in the first version.

---

## Future Architecture Possibilities

Later, the simulator may benefit from:

- an `Experiment` class,
- batch simulation mode,
- CSV export,
- plotting with Matplotlib,
- Monte Carlo runs,
- sensor simulation,
- autopilot/controller modules,
- multiple vehicles,
- reinforcement learning environments,
- and a headless mode without Pygame.

These should remain future extensions rather than requirements for the first implementation.
