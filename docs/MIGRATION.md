# Historical provenance and future import boundary

This implementation selectively generalizes the preserved source:

- nodes: `distributed_experiment/fixtures/nodes/`
- evidence/messages/proposals/context manifests: corresponding schemas
- context and treatment materialization: `scripts/run_experiment.py`
- ordinary/exploration distinction: landscape and exploration runners
- exclusion wording: frozen exploration and Stage-1 dispatches
- literature/computation discipline: historical `state/literature/` and scripts

It intentionally does not carry forward the historical path
`research_outlook.md -> project_context.py/create_worker_context.py -> future context`.

Future STCI migration should import each old document as a literature, computation,
evidence, representation, or historical-interpretation artifact with explicit provenance.
It must not import `research_outlook.md` as global state. The archived checkout remains the
authoritative historical source until such imports are reviewed.
