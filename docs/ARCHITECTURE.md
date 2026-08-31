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

## CLI

`python3 -m math_automation.cli --root STATE init --name NAME`

Then use `artifact`, `node`, `message`, `proposal`, `decide`, `context`, `dispatch`,
`invocation`, `validate`, and `history`. Provider execution is a manual boundary: dispatches
can be exported and returned output recorded with its provider/configuration when known.
