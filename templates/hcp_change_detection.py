#!/usr/bin/env python3
"""Queue exactly one HCP plan-only run; never request an apply."""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://app.terraform.io/api/v2"
ACTIVE = {
    "pending", "fetching", "fetching_completed", "pre_plan_running",
    "pre_plan_completed", "queuing", "plan_queued", "planning", "planned",
    "cost_estimating", "cost_estimated", "policy_checking", "policy_override",
    "policy_soft_failed", "policy_checked", "post_plan_running",
    "post_plan_completed",
}


class DetectionError(Exception):
    """An API request or run did not meet the expected contract."""


def identifier(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(prefix + r"-[A-Za-z0-9]+", value):
        raise DetectionError(f"Missing or invalid {prefix} identifier.")
    return value


def api(token, path, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE + path,
        data=body,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        },
        method="GET" if payload is None else "POST",
    )
    # No automatic retries: a timed-out POST may already have created a run.
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise DetectionError(f"HCP API HTTP {error.code}; inspect access and the workspace runs.") from error
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        raise DetectionError("HCP API transport/JSON failure; inspect workspace runs before retrying.") from error
    if not isinstance(result, dict):
        raise DetectionError("Expected a JSON API object.")
    return result


def detect(token, workspace, timeout=900, interval=20):
    identifier(workspace, "ws")
    if not token or token.strip() != token:
        raise DetectionError("Set HCP_TERRAFORM_TOKEN to a user token without surrounding whitespace.")
    started = time.monotonic()
    workspace_data = api(token, "/workspaces/" + workspace)["data"]
    configuration = workspace_data["relationships"]["current-configuration-version"]["data"]
    if not isinstance(configuration, dict):
        raise DetectionError("No current configuration version: complete a VCS run first.")
    configuration_id = identifier(configuration["id"], "cv")
    created = api(token, "/runs", {
        "data": {
            "type": "runs",
            "attributes": {
                "message": "Scheduled plan-only change detection (not pure drift classification)",
                "plan-only": True,
                "auto-apply": False,
                "refresh": True,
            },
            "relationships": {
                "workspace": {"data": {"type": "workspaces", "id": workspace}},
                "configuration-version": {
                    "data": {"type": "configuration-versions", "id": configuration_id}
                },
            },
        }
    })
    run_id = identifier(created["data"]["id"], "run")
    print(f"Queued {run_id}; inspect this run in HCP if this job stops.", flush=True)
    while time.monotonic() - started < timeout:
        run = api(token, "/runs/" + run_id)["data"]
        status = run["attributes"]["status"]
        if status == "planned_and_finished":
            plan_id = identifier(run["relationships"]["plan"]["data"]["id"], "plan")
            changes = api(token, "/plans/" + plan_id)["data"]["attributes"]["has-changes"]
            if not isinstance(changes, bool):
                raise DetectionError("Plan has-changes must be a boolean.")
            if changes:
                print("CHANGE DETECTED: review HCP plan. Could be drift, code or variable changes. No apply requested.")
                return 2
            print("No changes in this plan. No apply requested.")
            return 0
        if status not in ACTIVE:
            raise DetectionError(f"Run stopped in unexpected/failed status: {status!r}. Inspect HCP.")
        time.sleep(interval)
    raise DetectionError("Polling deadline reached. The HCP run may still be queued/running; inspect it before retrying.")


def main():
    try:
        return detect(
            os.environ.get("HCP_TERRAFORM_TOKEN", ""),
            os.environ.get("HCP_WORKSPACE_ID", ""),
        )
    except (DetectionError, KeyError, TypeError) as error:
        print(f"Change detection failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
