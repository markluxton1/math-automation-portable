# Math Automation Portable

Minimal filesystem-backed research machine reconstructed from the preserved v0.4 and
`distributed_experiment` substrate. It has no canonical mathematical outlook and no model
provider integration. Its provider-neutral swarm layer plans, materializes, validates, and
records run jobs; it does not choose mathematical direction or ship a provider adapter.

Run `python3 -m math_automation.cli --help` or `python3 -m unittest discover -s tests -v`.

Requires Python 3.10+ and only the standard library. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md),
[docs/EXECUTION.md](docs/EXECUTION.md), and [docs/MIGRATION.md](docs/MIGRATION.md).
