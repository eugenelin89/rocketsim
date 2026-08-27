# Project Brief

## Working Title

**2D Rocket Flight Physics Simulator**

## One-Sentence Description

A Pygame-based experimental simulator that models and visualizes rocket flight while progressively introducing propulsion, aerodynamics, atmosphere, stability, and control.

## Core Question

How accurately can increasingly realistic rocket-flight behavior be reproduced using a simple, modular 2D physics simulator?

## Primary Purpose

The project is intended to serve as:

1. a physics learning environment,
2. a software-engineering project,
3. a digital testbed for future rocket experiments,
4. and potentially the foundation for a more advanced science-fair investigation.

## Initial Scope

Version 1 models a rocket as a point mass in two dimensions with:

- gravity,
- finite-duration thrust,
- configurable launch angle,
- configurable mass,
- position and velocity integration,
- trajectory visualization.

The first version explicitly excludes:

- drag,
- wind,
- changing mass,
- rotation,
- aerodynamic stability,
- guidance,
- sensor simulation.

Those effects will be introduced later as independent milestones.

## Key Technical Principle

The project should not be built as a Pygame animation with physics embedded in rendering code.

Instead:

```text
Physics engine → state → renderer
```

This allows the same physics engine to later run automated experiments without graphics.

## Initial User Controls

Suggested controls:

```text
SPACE   launch / pause
R       reset
T       toggle trajectory
V       toggle velocity vector
F       toggle force vectors
+ / -   zoom
ESC     quit
```

Parameters should initially be edited in configuration rather than through a complex GUI.

## Initial Telemetry

Display:

```text
Time
Altitude
Horizontal position
Horizontal velocity
Vertical velocity
Speed
Motor state
```

Later:

```text
Acceleration
Mass
Dynamic pressure
Mach
Angle of attack
CG / CP
```

## Scientific Value

The simulator becomes scientifically useful when it can answer quantitative questions through controlled experiments.

Examples:

- How does drag coefficient affect apogee?
- What timestep is necessary for reliable simulation?
- How much performance changes as propellant mass decreases?
- What launch angle maximizes altitude under wind?
- How sensitive are predictions to uncertain aerodynamic parameters?

## Long-Term Vision

A mature version could act as a digital flight laboratory containing:

- simulated rocket dynamics,
- real motor curves,
- sensor models,
- simulated telemetry,
- flight-control algorithms,
- Monte Carlo uncertainty analysis,
- and multi-vehicle experiments.

The long-term goal is not merely to draw a rocket flying across the screen, but to create a reusable environment for testing aerospace ideas before hardware experiments.
