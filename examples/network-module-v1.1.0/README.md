# Network v1.1.0 delta, not a standalone module

Start with all files in `../network-module`. Copy `outputs-addition.tf` into that
module's root and `upgrade.tftest.hcl` into its `tests/` directory. Preserve the
v1.0.0 resources and tests. The course validation script assembles this exact
combination in a temporary directory.

The additive release exposes `subnet_names`. It changes no Azure resources.
Do not copy this delta during the initial v1.0.0 lesson.
