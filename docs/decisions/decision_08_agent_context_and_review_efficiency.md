# Decision 08: Agent context and review efficiency

- Date: 2026-08-29
- Status: accepted
- Related prompt: `docs/prompts/prompt_05_prelaunch_lab.md`
- Supersedes: none

## Decision

RocketSim will preserve independent scientific review while using targeted context and staged validation. The parent agent owns broad repository and milestone context, reconciliation, implementation, integration, and final decisions. Read-only specialists receive the minimum sufficient context needed to independently judge their domain: the reconciled contract, relevant authoritative sections, relevant source and tests, quantitative evidence, and the relevant diff. They may request more context whenever needed.

Each milestone classifies specialists as `CORE`, `FOCUSED`, or `NOT REQUIRED` and records the matrix in its prompt record. Core reviewers normally perform appropriate pre- and post-implementation review. Focused reviewers receive a narrow regression or boundary question. A not-required reviewer is not invoked merely because the definition exists. Re-review is selective: reinvoke only when that specialist's BLOCKING or IMPORTANT finding was corrected and confirmation is useful, or when later work materially changed its reviewed domain.

The parent and specialist reviewers use High reasoning effort by default. Extra High is reserved for genuinely difficult scientific disagreement, numerical reconciliation, event-semantics changes, or hard-to-reverse architecture choices. Validation is staged from affected tests through subsystem groups to one complete pre-commit suite, with another full run only after a late material core change when warranted.

Current authoritative documents, accepted decisions, implementation, and tests are the normal working context. Historical prompt records remain available for provenance, supersession, regression archaeology, and ambiguity resolution rather than automatic rereading. Normal interruption recovery uses a compact repository-state resume and continues from the first incomplete gate without repeating completed reviews.

Prompt provenance is Git-native. Prompt records preserve the approved prompt verbatim, material requirement changes, reviewer resolutions, decisions, evidence, validation, and final repository state. They record the starting SHA, implementation parent and commit SHAs, prompt-record commit SHA where applicable, SHA-256 of the zero-context implementation diff, and an exact `git show --no-ext-diff --binary --format= <implementation-sha>` recovery command. The full patch is not embedded in Markdown by default because Git is its authoritative exact store.

Independent production calculations, test oracles, and specialist derivations remain intentionally separate evidence.

> The objective is more scientific confidence per unit of model context and reasoning, not fewer scientific checks merely for token savings.

## Context and problem

Prompt 04 achieved strong scientific confidence but consumed substantial model usage through repeated full-context reviewer instructions, broad historical rereading, blanket re-review, repeated complete-suite runs after minor edits, and a large Markdown copy of a patch already stored exactly by Git. Those costs did not all contribute independent evidence.

RocketSim still needs reviewers to challenge model semantics, numerical behavior, pedagogy, and tests independently. The problem is unnecessary context duplication, not the existence of multiple checks.

## Options considered

- Continue giving all specialists broad project and prompt history and rerun every reviewer after corrections.
- Remove specialist reviews and independent derivations to minimize usage.
- Use targeted context, explicit review classification, selective re-review, staged validation, and Git-native provenance while preserving independent checks.

The third option is accepted.

## Rationale

Domain reviewers produce their strongest signal when the question and evidence are bounded. The parent remains responsible for cross-domain reconciliation, so specialists do not need identical copies of broad history. Explicit classification makes omissions auditable. Selective re-review follows the changed domain rather than ceremony. Staged testing shortens feedback loops while retaining a complete pre-commit gate. Git already provides an immutable, recoverable exact patch, so duplicating it in Markdown adds little provenance value.

## Consequences and tradeoffs

- Milestone prompt records must include a review matrix and qualitative efficiency audit.
- The parent must prepare concise, sufficient reviewer briefs and honor requests for more context.
- A specialist can be reclassified if implementation unexpectedly changes its domain.
- Some milestones legitimately require several core reviewers; efficiency classification cannot waive necessary scientific review.
- Historical prompt records remain preserved but are read only when current state is ambiguous or provenance requires them.
- Prompt records become substantially smaller while remaining exactly recoverable from Git.
- Independent derivation and regression evidence remain mandatory where scientifically useful.

## Related prompt records

- `docs/prompts/prompt_05_prelaunch_lab.md`

## Superseding decision

None.
