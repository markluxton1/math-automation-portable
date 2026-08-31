# STCI Ultra goal entry point

These instructions govern a fresh Ultra `/goal` run in this repository. The
authoritative, neutral mathematical problem is
[`examples/neutral_quartic_problem.json`](examples/neutral_quartic_problem.json).
Read that file verbatim before doing mathematical work. It does not silently fix a
base field or characteristic: every claimed conclusion must state the field and
characteristic assumptions under which it is asserted.

Then read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
[`docs/EXECUTION.md`](docs/EXECUTION.md). Use the repository's artifact store,
proposal lifecycle, contexts, dispatches, invocation records, and run records; do
not create a parallel notebook, research-management system, global synthesis, or
privileged lead. `docs/MIGRATION.md` is provenance/import policy, not mathematical
context for the initial run.

## Goal and completion

The research objective is to prove or disprove the authoritative problem. A field-
or characteristic-dependent answer must say exactly what it establishes and what
remains open. The goal is complete only when a rigorous proof or disproof, its
assumptions, and the provenance needed to audit its literature and computational
dependencies have been recorded in the repository research state and accepted
through the proposal lifecycle. Structural validation or completion of invocation
jobs does not certify the mathematics and does not by itself complete the goal.

## Hard research invariants

- There is no canonical outlook, global research state, or privileged lead. Local
  nodes may hold competing interpretations and representations.
- Store problems, representations, evidence, messages, literature, computations,
  and invocations as typed artifacts with explicit references and provenance.
  Context manifests and dispatches must name the selected local material.
- Messages are immutable referenced artifacts. Recording a message does not update
  its recipient. A node's research state changes only through an explicitly
  accepted proposal; creating an artifact or a message is not a state update.
- Preserve competing and dormant representations as separate artifacts. Preserve
  rejected proposals and failed attempts in their lifecycle/history records. Do
  not overwrite or delete them merely because another direction is active.
- Ordinary fresh judgment and exploration are different operations. Parallel fresh
  calls are not automatically exploration.
- If an approach fails, record the failure and its support with provenance rather
  than erasing it or treating it as completion. Exploration may validly report that
  no natural alternative was found; do not manufacture one. That report also does
  not complete the research goal.

## Neutral first-run boundary

Wave 1 is the initial configuration in
[`examples/sol_ultra_wave1_neutral.example.json`](examples/sol_ultra_wave1_neutral.example.json).
It must start from a new store, the neutral problem artifact, and fresh empty nodes.
Its jobs are ordinary, independent fresh judgments with empty `selected_artifacts`
and no excluded representations. Do not inspect, search, import, summarize, or use
archived or prior STCI research, prior STCI outputs, prior representations,
evidence, literature, computations, exclusions, or any accumulated research
outlook during Wave 1. Repository architecture and execution material may be
inspected only to operate and validate the machine, not as mathematical context.

Wave 2 is not part of the neutral starting context and is not automatic. The file
[`examples/sol_ultra_wave2_exploration.template.json`](examples/sol_ultra_wave2_exploration.template.json)
may be instantiated only after actual representations have emerged, their artifacts
have been created from reviewed results, and the representations to exclude have
been explicitly selected by real artifact ID. A placeholder, inferred framing, or
unreviewed output cannot unlock Wave 2. Later historical material may enter a local
context only after explicit authorization and reviewed, typed import with source
provenance under `docs/MIGRATION.md`; it must never become a global outlook.

## State and provenance locations

Use one repository store root, `state/`, for this goal. `python3 -m
math_automation.cli --root state init --name STCI` creates the durable layout.
Import the neutral fixture's `payload` unchanged as the problem artifact with its
declared ID, then create the nodes listed in the Wave-1 spec against that problem;
each node must still have empty local state. Those referenced objects must exist
before passing the checked-in Wave-1 file to `run-spec`.
Write typed artifacts under `state/artifacts/`, node states under `state/nodes/`,
proposals under `state/proposals/`, bounded contexts and dispatches under
`state/contexts/` and `state/dispatches/`, invocation outputs and run records under
`state/outputs/` and `state/runs/`, and the append-only provenance trail under
`state/history/`. Use `python3 -m math_automation.cli --root state validate` after
state changes. Use the Wave-1 spec through `run-spec` and `run-dry` before any real
provider boundary; a dry run makes no provider calls.
