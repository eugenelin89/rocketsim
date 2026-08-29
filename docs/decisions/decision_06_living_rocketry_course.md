# Decision 06: Living Rocketry Course

- Date: 2026-08-29
- Status: accepted
- Related prompt: `docs/prompts/prompt_04_propulsion_learning.md`
- Supersedes: none

## Decision

RocketSim is both a scientifically inspectable simulator and an educational environment for learning rocketry. Maintain one learner-facing course at:

```text
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

Every approved milestone that changes implemented physics, propulsion, scientifically meaningful numerical interpretation, events/phases, Physics Inspector content, educational visualization, learner controls, or simulator experiments must perform a Living Course impact review before completion. The parent agent must update applicable material without waiting for a future prompt to request it, including revising earlier lessons when a later model supersedes or qualifies an earlier simplification.

Scientific truth remains in `docs/PHYSICS_MODEL.md`; validation methodology and evidence remain in `docs/VALIDATION.md`. The course is the pedagogical projection of those sources and actual simulator behavior, not an independent physics authority.

The course uses a progressive prediction → observation → explanation approach, distinguishes real-world nature from RocketSim's approximation, states assumptions and limits, supplies reproducible hands-on activities, and includes reasoning-based checks for understanding. A read-only `learning_reviewer` reviews the complete course before any affected milestone completes.

## Context and problem

RocketSim already exposes forces, equations, phases, and numerical state, but developer-facing documentation alone does not teach a learner how to connect those quantities. A course appended only when explicitly requested would become stale as models, controls, and visualizations evolve. An educational product identity therefore needs a durable repository policy and a retroactive maintenance rule.

## Options considered

- Maintain one living tutorial tied to authoritative scientific documentation and implementation.
- Write a one-time Prompt 04 propulsion tutorial with no future maintenance requirement.
- Treat developer documentation as the learner course.
- Split immediately into many chapter files and a course framework.

## Rationale

One coherent document is easy to discover, review, and revise at the current project size. Explicit source-of-truth boundaries prevent pedagogical wording from silently redefining equations or evidence. Whole-course specialist review catches older chapters made obsolete by later physics. Prediction, observation, and explanation turns the simulator into an interactive laboratory rather than a passive animation.

## Consequences and tradeoffs

- Physics and educational milestones acquire a course-impact and learning-review completion gate.
- Course updates may touch older lessons even when a milestone adds a new later topic.
- Activities must match actual controls and configurations; future features may be named only as unimplemented.
- Automated behavior tests protect concrete UI/data contracts, but scientific and pedagogical prose remains primarily a specialist-review responsibility.
- The course adds maintenance work and must not duplicate or replace authoritative physics and validation documents.

## Related prompt records

- `docs/prompts/prompt_04_propulsion_learning.md`

## Superseding decision

None.
