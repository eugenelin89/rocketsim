# Decision 04: Persistent specialist review workflow

- Date: 2026-08-27
- Status: accepted
- Related prompt: `docs/prompts/prompt_02_physics.md`
- Supersedes: none

## Decision

Maintain project-scoped, read-only specialist definitions in `.codex/agents/` for physics, numerical-method, and test-evidence review. For scientific or numerical implementation work, the parent agent obtains all applicable pre-implementation reviews, reconciles their findings, remains the sole implementer, then obtains post-implementation reviews and resolves blocking or important findings before committing.

If a Codex runtime cannot select a checked-in named custom agent directly, it may use explicitly named read-only delegated subagents that first read and follow the corresponding TOML definition. The prompt record must disclose that fallback rather than claim the custom type was hot-loaded.

## Context

Physics-model errors, integration-boundary errors, and circular tests require different scrutiny. Prompt 02 also requires the specialist strategy to persist in repository policy rather than exist only in one conversation.

## Options considered

- One general reviewer, three bounded specialists, or direct parent review only.
- Allow reviewers to edit or keep implementation ownership centralized.
- Treat lack of runtime hot-loading as failure or preserve configuration and use an explicit fallback.

## Rationale

Three narrow, read-only perspectives provide independent challenge without creating concurrent write conflicts. Central implementation ownership makes resolution and repository history auditable. The fallback preserves honest execution across Codex runtime capabilities.

## Consequences and tradeoffs

- Review adds process overhead to relevant scientific changes.
- Reviewer findings are advisory until reconciled by the parent, but unresolved blocking findings prevent completion.
- Agent TOML describes reviewer behavior; physics truth and validation criteria remain in project documentation and decisions.
- The workflow does not authorize scope expansion or reviewer writes.

No prior decision is superseded.
