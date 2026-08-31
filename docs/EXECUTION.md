# Swarm execution layer

Run specs are separate from research state. The checked-in structural schema is
`schemas/run_spec.schema.json`; runtime also validates referenced local problems, nodes, and
excluded representations. A spec names a problem, nodes, operation templates,
provider/model target, derived intended-invocation count, concurrency, retry limit, output
location, and explicit selected artifacts. They do
not contain a canonical outlook or mathematical conclusion.

Use `run-spec --file SPEC`, then `run-dry RUN-ID`. Dry run materializes every job, bounded
context, dispatch, and invocation-ready record without provider calls or fake responses.
`run-resume` only lists/provider-executes pending or retryable jobs; an interrupted `RUNNING`
attempt is preserved as a failed attempt before it becomes eligible to retry. This repository ships
no provider adapter. `run-result` records an externally collected output.

The two Sol Ultra files are experiment configuration, not an ordinary/exploration ratio
recommendation. [Wave 1](../examples/sol_ultra_wave1_neutral.example.json) is a 24-job,
ordinary-only, independent fresh swarm. It requires only the neutral problem and fresh empty
nodes; it has no selected evidence, literature, representations, exclusions, archived STCI
state, or prior outputs.

[Wave 2](../examples/sol_ultra_wave2_exploration.template.json) is deliberately only a later
template. It cannot be instantiated until a human has reviewed Wave 1 and created actual
representation artifacts (or deliberately supplied them for the new experiment), replacing
`REP-FROM-WAVE1-001`. It does not fabricate a representation or imply that Wave 2 must occur.

Wave 1 asks what representations emerge spontaneously from independent fresh research calls.
Wave 2 asks whether explicit open-ended exclusion can produce representational movement away
from representations that actually emerged in Wave 1.

This staging is experiment configuration, not a scheduler, automatic exploration trigger,
iterative-exclusion workflow, diversity threshold, or a requirement that every research run
have two waves. A human or later explicit run specification decides whether Wave 2 occurs and
which representation IDs it references.

Provider integration must remain outside mathematical state and must document the freshness,
wrapping, and transmitted-text observability of its actual execution surface.

To record a manually collected result, use `run-result RUN JOB --output-file RESPONSE.md`.
Optional provider metadata, observable transmitted text, and resulting artifact/proposal IDs can
be recorded with that command. The CLI does not launch a provider.
