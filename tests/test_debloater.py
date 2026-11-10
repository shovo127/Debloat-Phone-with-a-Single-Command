import json
import unittest
from unittest.mock import MagicMock, patch
from debloater_core import DebloaterCore


class TestDebloaterCore(unittest.TestCase):
    def setUp(self):
        self.sample_catalog = {
            "safe_debloat": {
                "com.milink.service": {"name": "MiLink", "description": "Casting", "risk": "Low"},
                "com.mfashiongallery.emag": {"name": "Glance", "description": "Ads", "risk": "Low"}
            },
            "optional": {
                "com.google.android.googlequicksearchbox": {"name": "Google App", "description": "Search", "risk": "Medium"}
            },
            "critical_system": {
                "com.android.settings": "Settings",
                "com.android.systemui": "SystemUI"
            }
        }
        self.core = DebloaterCore()
        self.core.catalog = self.sample_catalog

    @patch.object(DebloaterCore, 'run_adb')
    def test_audit_device(self, mock_run_adb):
        # Mock pm list packages -e and -d
        mock_run_adb.side_effect = [
            (0, "package:com.milink.service\npackage:com.android.settings\npackage:com.google.android.googlequicksearchbox"),
            (0, "package:com.mfashiongallery.emag")
        ]
        audit = self.core.audit_device()
        self.assertEqual(len(audit["safe_debloat"]), 2)
        self.assertEqual(len(audit["optional"]), 1)
        self.assertEqual(len(audit["critical_system"]), 1)
        self.assertEqual(audit["total_installed"], 4)

    @patch.object(DebloaterCore, 'run_adb')
    def test_refuse_critical_disable(self, mock_run_adb):
        success, msg = self.core.disable_package("com.android.settings")
        self.assertFalse(success)
        self.assertIn("Refusing", msg)
        mock_run_adb.assert_not_called()

    @patch.object(DebloaterCore, 'run_adb')
    def test_safe_disable(self, mock_run_adb):
        mock_run_adb.return_value = (0, "Package com.milink.service new state: disabled-user")
        success, msg = self.core.disable_package("com.milink.service")
        self.assertTrue(success)
        mock_run_adb.assert_called_with("pm disable-user --user 0 com.milink.service")

    @patch.object(DebloaterCore, 'run_adb')
    def test_notification_fixes(self, mock_run_adb):
        mock_run_adb.side_effect = [
            (0, ""),
            (0, ""),
            (0, "com.miui.video,"),
            (0, ""),
            (0, "")
        ]
        res = self.core.apply_notification_sound_fixes()
        self.assertEqual(res["useNotification"], "Enabled")
        self.assertEqual(res["sound_effects_enabled"], "Muted (No UI Tap Sounds)")


if __name__ == "__main__":
    unittest.main()
