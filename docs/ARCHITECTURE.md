# Architecture

This portable machine stores explicit filesystem artifacts. There is no global research
outlook and no privileged lead node. Nodes are local, may diverge, and change only by
accepting a proposal. Messages are immutable artifacts; recording one does not mutate a
recipient.

Artifacts: `problem`, `representation`, `evidence`, `message`, `literature`,
`computation`, `invocation`, node state, context manifests, dispatches, and proposals.
References—not a synthesized notebook—link them.

Ordinary treatment requests mathematical judgment from selected local material. Exploration
treatment requests a different organization from explicitly excluded representations, but
permits `no natural alternative found`. It is a capability, not a scheduler.

`fresh judgment != exploration`; likewise, parallel fresh agents are not themselves an
exploration mechanism. These are experimentally motivated operating constraints, not
universal claims about models.

Structural validation checks references and lifecycle only; it does not certify mathematics.

Deliberately absent: provider execution, canonical outlook, scheduler, swarm controller,
voting, markets, pruning, automatic synthesis, quotas, and novelty triggers.

## Execution layer

`math_automation.swarm` is an execution layer, not a research authority. A persistent run
spec plans stable jobs, contexts, and dispatches. It uses atomic JSON replacement and
locked event appends; successful jobs are never re-run by `resume`. Failed attempts remain
in a job's attempt history, while a later success becomes a new recorded attempt.

Every attempt records intended context/artifact order, dispatch hash, provider/model,
timestamps, status, raw response path/hash when present, and any observable transmitted
dispatch hash. Material treatment fidelity is recorded as `observable` only when the
transmitted text is available; otherwise it is explicitly `intended_only`.

There is no built-in Sol Ultra adapter. The first-run target is recorded as configuration
only; a provider/manual adapter must supply fresh isolated execution and returned text.

## CLI

`python3 -m math_automation.cli --root STATE init --name NAME`

Then use `artifact`, `node`, `message`, `proposal`, `decide`, `context`, `dispatch`,
`invocation`, `validate`, and `history`. Provider execution is a manual boundary: dispatches
can be exported and returned output recorded with its provider/configuration when known.
