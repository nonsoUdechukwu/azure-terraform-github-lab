# 06: Git, CI and the retail capstone

**Goal:** make a change, test it, and explain an end-to-end pipeline. Time:
3–5 hours. All local steps are free; Azure deployment is optional and paid.

## 1. Make a safe working copy

Fork this repository on GitHub if you do not own it. Clone **your fork** using
the URL shown by GitHub, then:

```bash
cd azure-terraform-github-lab
git switch -c retail-lab-practice
cd data-engineering-lab
python3 -m unittest discover -s tests -v
python3 src/pipeline.py
```

Expected: three tests pass and 9/6/2/6. Inspect Git without staging generated
data: `git status --short`. The `.db` file is ignored. Do not commit credentials.

## 2. Add and test a change

Write a new test in `tests/test_pipeline.py` for an order with an unknown
product, following the existing test that appends events to a temporary input
copy. Run `python3 -m unittest discover -s tests -v`; it should pass and the
new event should be quarantined, not counted in silver or gold. Next add a
valid later event in a separate test, check its changed revenue, and rerun
the pipeline to check no duplicate order appears. Tests must use temporary
files and leave the tracked dataset unchanged.

From the **repository root**, review and publish your own work:

```bash
cd ..
git diff -- data-engineering-lab
git status --short
git add data-engineering-lab/tests/test_pipeline.py
git commit -m "Add retail data quality tests"
git push -u origin retail-lab-practice
```

Open a pull request in your fork on GitHub. Under **Checks/Actions**, inspect
the `Data engineering lab` workflow. It runs unit tests and the local pipeline
only, with read-only repository permission and no Azure credentials. If
Actions are disabled in your fork, enable them in repository settings, or run
the same commands locally. A green check proves these offline checks passed;
it does not prove a Databricks or Azure deployment.

## 3. Complete the capstone

Create a short report in your own notes (not necessarily committed):

1. Draw `source CSV → bronze events → validation → quarantine / silver orders
   → customer/product joins → gold daily revenue`. Label both fact grains.
2. Show baseline evidence: 9 bronze, 6 silver, 2 quarantine, 6 gold groups,
   total 77.00. Name E008/E009 and explain E007 replacing E002.
3. Perform the new-event exercise in lesson 02 (or reproduce with local
   temporary input). Show 82.00 and demonstrate the same result after a rerun.
   Explain that bronze is merged incrementally but downstream results are
   recomputed, and invalid latest events do not cancel earlier valid ones.
4. Write a SQL query returning revenue per region and a window query ranking
   orders within a region. Compare your results with `sql/analysis.sql`.
5. Explain how you would alert on failed ADF/Databricks runs, limit access,
   investigate quarantine, and correct/reprocess a bad event with the same ID.
   Describe how you would handle deletes and historical dimensions in a real
   design; they are outside this small implementation.
6. If you chose the optional Azure route, include one ADF manual-run ID and
   activity outcomes, Databricks run evidence, SQL plan/IO observations,
   cost estimate versus observed cost, and cleanup confirmation. Never include
   secrets or personal customer data. Do not label unperformed work as experience.

## 4. Documented optional deployment

This lab intentionally has **no automatic cloud deployment**. After CI passes
and a human reviews the diff, deploy by importing the checked-out
`databricks/retail_notebook.py` into the intended Azure workspace, uploading
the three matching CSVs or configuring the ADF external-volume route in lesson
04, setting widgets, and manually running the notebook once. Verify the counts
and total before any downstream consumption. For a change, repeat with a fresh
isolated schema, compare outputs, then explicitly approve promotion; to roll
back, re-import the previously reviewed notebook and use an isolated clean
schema/input rather than assuming old Delta data was undone.

For production, separately design artifact/version promotion, protected
environments, least-privilege federated identities, integration tests, schema
migrations, rollback and data retention; no such deployment is implemented or
validated here. Clean up after practice using [lesson 07](07-cost-cleanup.md).

**Checkpoint:** can another learner run your tests and reproduce your totals?
Can you explain what CI did *not* verify?
