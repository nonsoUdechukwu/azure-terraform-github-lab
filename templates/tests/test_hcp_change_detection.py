import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "detector", Path(__file__).resolve().parents[1] / "hcp_change_detection.py"
)
detector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(detector)

WORKSPACE = {"data": {"relationships": {"current-configuration-version": {"data": {"id": "cv-demo"}}}}}
CREATED = {"data": {"id": "run-demo"}}
FINISHED = {"data": {
    "attributes": {"status": "planned_and_finished"},
    "relationships": {"plan": {"data": {"id": "plan-demo"}}},
}}


class DetectorTests(unittest.TestCase):
    def test_complete_plan_and_non_applying_payload(self):
        for changes, expected in [(False, 0), (True, 2)]:
            with self.subTest(changes=changes):
                plan = {"data": {"attributes": {"has-changes": changes}}}
                with patch.object(detector, "api", side_effect=[WORKSPACE, CREATED, FINISHED, plan]) as api:
                    self.assertEqual(detector.detect("token", "ws-demo"), expected)
                    payload = api.call_args_list[1].args[2]["data"]
                    self.assertEqual(payload["attributes"]["plan-only"], True)
                    self.assertEqual(payload["attributes"]["auto-apply"], False)
                    self.assertEqual(payload["attributes"]["refresh"], True)
                    self.assertEqual(payload["relationships"]["configuration-version"]["data"]["id"], "cv-demo")
                    self.assertEqual([call.args[1] for call in api.call_args_list],
                                     ["/workspaces/ws-demo", "/runs", "/runs/run-demo", "/plans/plan-demo"])

    def test_failed_or_unknown_status_is_not_success(self):
        for status in ["errored", "canceled", "discarded", "applied", "unknown"]:
            with self.subTest(status=status):
                with patch.object(detector, "api", side_effect=[
                    WORKSPACE, CREATED, {"data": {"attributes": {"status": status}}}
                ]):
                    with self.assertRaises(detector.DetectionError):
                        detector.detect("token", "ws-demo")

    def test_polling_timeout_is_explicit(self):
        with patch.object(detector, "api", side_effect=[WORKSPACE, CREATED]):
            with self.assertRaisesRegex(detector.DetectionError, "may still be"):
                detector.detect("token", "ws-demo", timeout=0)

    def test_missing_configuration_stops_before_post(self):
        workspace = {"data": {"relationships": {"current-configuration-version": {"data": None}}}}
        with patch.object(detector, "api", return_value=workspace) as api:
            with self.assertRaisesRegex(detector.DetectionError, "VCS run first"):
                detector.detect("token", "ws-demo")
            self.assertEqual(api.call_count, 1)

    def test_non_boolean_plan_result_fails(self):
        with patch.object(detector, "api", side_effect=[
            WORKSPACE, CREATED, FINISHED, {"data": {"attributes": {"has-changes": "false"}}}
        ]):
            with self.assertRaisesRegex(detector.DetectionError, "boolean"):
                detector.detect("token", "ws-demo")

    def test_uncertain_post_is_not_retried(self):
        with patch.object(detector, "api", side_effect=[
            WORKSPACE, detector.DetectionError("transport failure")
        ]) as api:
            with self.assertRaises(detector.DetectionError):
                detector.detect("token", "ws-demo")
            self.assertEqual(api.call_count, 2)

    def test_invalid_workspace_does_not_call_api(self):
        with patch.object(detector, "api") as api:
            with self.assertRaises(detector.DetectionError):
                detector.detect("token", "../wrong")
            api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
