# Validation and Testing

## Current evidence standard

RocketSim validates simple cases against independently calculated known answers before relying on integrated flight behavior. Expected analytical values in tests are computed directly from literal parameters and closed-form equations, not by calling production force, phase, or integration helpers.

The suite runs headlessly with:

```bash
conda run -n rocketsim python -m pytest
```

## Implemented checks

### Configuration and force algebra

- finite input enforcement
- positive mass and timestep
- non-negative thrust, burn duration, and gravity
- valid zero-valued limiting cases
- gravitational sign and magnitude
- thrust components at 0, 90, and 180 degrees
- net acceleration from force divided by mass
- thrust immediately before, exactly at, and immediately after burnout
- negative time producing no thrust
- constant mass throughout a complete run

Direct identities use approximately `1e-12` absolute tolerance where floating-point trigonometry is involved.

### Integration and event boundaries

- one-step ordering that distinguishes semi-implicit from explicit Euler
- a deliberately non-grid-aligned fixed step that crosses burnout
- exact powered impulse and coast remainder in the crossing step
- coast phase and instantaneous coast acceleration at the resulting boundary
- no false landing at launch
- deterministic interpolated ground crossing and terminal immutability
- deterministic no-liftoff behavior for an unsupported ground configuration
- no negative-altitude history for a downward or under-resolved ground start
- consistent thrust and acceleration telemetry for an impact before burnout

### Independent analytical motion

The continuous references are:

```text
v(t) = v0 + a t
p(t) = p0 + v0 t + 0.5 a t²
```

They are applied independently to gravity-only, powered constant-acceleration, and piecewise powered/coast cases. Velocity is expected to agree to roundoff during constant-acceleration intervals. Position expectations include the known semi-implicit Euler error:

```text
p_numerical - p_analytical = 0.5 a t dt
```

The suite also checks vertical horizontal displacement, zero thrust, zero gravity, and uniform zero-force motion.

### Convergence

An analytically referenced powered case runs with:

```text
dt = 0.02 s
dt = 0.01 s
dt = 0.005 s
```

Position error must decrease monotonically and the error ratio must remain close to two, which is evidence of first-order convergence. A finer run from the same production integrator is not used as the sole correctness oracle.

The default vertical flight also compares interpolated landing time at those three timesteps with the independently solved positive root of the piecewise powered/coast trajectory. Landing-time error must decrease and approximately halve with timestep.

### Lifecycle and time separation

- full flight leaves the ground and later terminates while descending
- reset restores state, history, flags, counter, and fractional accumulator
- replaying the same elapsed-time sequence after reset gives exactly the same history
- paused wall time does not accumulate
- pre-launch wall time does not accumulate and pause can resume with retained fractional time
- zero elapsed time at a very small valid timestep cannot fabricate a physics step
- a representably subthreshold elapsed interval cannot fabricate a physics step
- equal `0.5 s` elapsed durations partitioned at 30, 60, and 144 FPS produce the same 50 fixed physics steps and identical trajectory

FPS validation feeds frame durations through the public accumulator rather than bypassing it with direct physics calls.

### Rendering and application

- physics modules have no Pygame import
- world-to-screen conversion reverses only the vertical axis
- drawing does not mutate physics state or trajectory
- keyboard controls exercise launch/pause, reset, and exit
- a dummy SDL display runs the application for a bounded number of frames and exits normally

## Full validation procedure

Before a completed implementation is committed and pushed:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -m compileall -q src tests
conda run -n rocketsim python -m pytest
conda run -n rocketsim python -c "import rocket_sim"
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy conda run -n rocketsim python -c "from rocket_sim.app import run; raise SystemExit(run(max_frames=2))"
git diff --check
```

## Interpretation limits

Landing interpolation follows the discrete numerical segment; it is not an exact impact root. Event time, apogee, and landing metrics remain timestep-sensitive. The suite establishes correctness for the documented simplified equations and numerical contract, not agreement with real rockets. Real-flight comparison requires later calibration, uncertainty analysis, and measured data kept separate from evaluation data.
