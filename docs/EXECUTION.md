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

The supplied Sol Ultra example is configuration, not a recommended ordinary/exploration
ratio. It requires creating the neutral problem, local nodes, and any selected representation
artifacts first. It neither imports archived STCI history nor launches a model.

Provider integration must remain outside mathematical state and must document the freshness,
wrapping, and transmitted-text observability of its actual execution surface.

To record a manually collected result, use `run-result RUN JOB --output-file RESPONSE.md`.
Optional provider metadata, observable transmitted text, and resulting artifact/proposal IDs can
be recorded with that command. The CLI does not launch a provider.
