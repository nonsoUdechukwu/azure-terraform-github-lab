# 11 - Optional advanced: scheduled plan-only change detection

[Previous](10-drift.md) | [Course index](../README.md) | [Next](12-extensions.md)

## Objectives

Schedule a normal refreshing plan without creating an apply path, interpret
the result cautiously, and manage an HCP API token safely.
**Skip this lesson on your first pass if APIs/GitHub Actions are new.**
Manual lesson 10 is the required drift exercise.

## 1. Understand the limits before enabling anything

This is **change detection**, not HCP's paid Health Assessments and not a
pure-drift classifier. A plan may include unapplied code, variables, provider
behavior changes and out-of-band resource changes. The workflow never requests
an apply, but its HCP user token can have broader permissions. Treat that
secret as powerful. Pinning `plan-only` in a script is not a token permission
boundary.

GitHub executes the schedule on the default branch in UTC; runs can be delayed.
Scheduled workflows in inactive public repositories may be disabled after
GitHub's inactivity period. No cron delivery/latency SLA is implied.
HCP remote concurrency limits can delay the plan too.

## 2. Create and scope the token

In HCP, create a **user API token** for a user with only the workspace access
needed for reading workspace/run/plan metadata and queuing plans. API tokens
inherit user access; review the user's effective permissions and any plan-specific
team controls. Do not use an organization token: it cannot POST new runs.
If you cannot restrict an otherwise overprivileged user adequately, keep this
optional automation disabled and use manual plans.

Copy the token directly into the **live repository's** GitHub **Settings >
Secrets and variables > Actions > Secrets**, as `HCP_TERRAFORM_TOKEN`.
Do not put it in a repository variable, a file, an issue, a CLI argument or
the course repository. Set an expiration if available, record the owner, and
plan revocation in lesson 13.

In HCP workspace settings, find its ID (`ws-...`). Add GitHub **Actions >
Variables** named `HCP_WORKSPACE_ID`. This is a workspace ID, not its name.
The workspace must already have a current VCS configuration version from a
successful baseline run.

## 3. Copy the two explicit opt-in files

```bash
cd "$LAB_HOME/azure-platform-live"
git switch main
git pull --ff-only
git switch -c add-plan-only-detection
mkdir -p scripts .github/workflows
cp "$COURSE/templates/hcp_change_detection.py" scripts/hcp_change_detection.py
cp "$COURSE/templates/scheduled-change-detection.yml" .github/workflows/scheduled-change-detection.yml
```

Read [the complete workflow](../templates/scheduled-change-detection.yml) and
[script](../templates/hcp_change_detection.py) before committing.
Python 3's standard library is sufficient; no extra packages or Azure secrets
are required. The actual Azure plan still runs inside HCP and uses its OIDC
identity, not this GitHub job's identity.

The script:

1. GETs the exact workspace's current configuration-version ID.
2. POSTs **one** run with explicit workspace and configuration-version
   relationships, `plan-only: true`, `auto-apply: false`, `refresh: true`.
3. Polls every 20 seconds for at most 15 minutes; HTTP requests time out after
   30 seconds. The Actions job has a separate 20-minute ceiling.
4. Accepts terminal success only as `planned_and_finished`, fetches the
   associated plan, and requires boolean `has-changes`.
5. Exits 0 for no changes, 2 for changes requiring review, 1 for API/run/shape
   errors or timeout. All non-zero exits make the Actions job red; read the
   message to distinguish a review signal from a broken check.

No apply endpoint is called. No plan JSON/state is saved as a GitHub artifact.
Run IDs are logged for private HCP follow-up; API error bodies/tokens are not.
GET/POST failures fail explicitly. There are deliberately **no automatic POST
retries**, because a network timeout could happen after HCP already created the
run. Inspect HCP before manually rerunning.

This uses HCP's **current uploaded configuration**, not a fresh GitHub pull
inside the script. It does not merge or apply anything. Before interpreting
results as drift, confirm the selected configuration version/commit is the
desired default-branch version and review pending runs/variables.

## 4. Review, merge, test manually, then enable the schedule

```bash
git add scripts/hcp_change_detection.py .github/workflows/scheduled-change-detection.yml
git diff --cached
git commit -m "Add opt-in HCP plan-only change detection"
git push -u origin add-plan-only-detection
gh pr create --base main --title "Add scheduled plan-only detection" \
  --body "Queues one refreshing plan-only run; no apply. Requires a scoped HCP user token. Review access and token lifecycle before merging."
```

Have the instructor review the secret's scope without revealing its value.
Merge only if comfortable with the access. The schedule becomes eligible on
the default branch. For stricter staged rollout, remove the `schedule:` block
from your first PR, test via **Actions > HCP plan-only change detection > Run
workflow**, then add the schedule in a second reviewed PR.

Expected clean baseline: an HCP plan-only run and a green GitHub job. Introduce
the VNet tag drift from lesson 10; run manually again. Expected: red job with
`CHANGE DETECTED`, HCP proposed tag reconciliation, **no Azure write**. Reconcile
using lesson 10, not this workflow, then verify a green run.

## Expected result and checkpoint

You can find the created run, distinguish a non-empty plan from an API failure,
and show that no apply was requested. On timeout, check HCP: the remote run may
still be queued/running. Cancel/discard that specific run if appropriate before
retrying; never create a flood of duplicate runs.

**Exercise:** Explain why a GitHub success badge means only "this plan saw no
changes at that time," not "there is no drift anywhere in the subscription."

Sources: [Runs API](https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run),
[Plans API](https://developer.hashicorp.com/terraform/cloud-docs/api-docs/plans),
[API tokens](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens).

[Previous](10-drift.md) | [Course index](../README.md) | [Next](12-extensions.md)
