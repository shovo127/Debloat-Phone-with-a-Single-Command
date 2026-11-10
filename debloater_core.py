"""
Autonomous Android Debloater and Notification Sound Optimization Suite.
Provides package categorization, safe reversible debloating, and HyperOS notification audio restoration.
"""

import json
import os
import subprocess
from typing import Dict, List, Optional, Tuple


class DebloaterCore:
    def __init__(self, catalog_path: Optional[str] = None, target_device: Optional[str] = None):
        self.device = target_device
        if catalog_path is None:
            catalog_path = os.path.join(os.path.dirname(__file__), "catalog.json")
        self.catalog_path = catalog_path
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> dict:
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"safe_debloat": {}, "optional": {}, "critical_system": {}}

    def run_adb(self, command: str) -> Tuple[int, str]:
        cmd = ["adb"]
        if self.device:
            cmd.extend(["-s", self.device])
        cmd.extend(["shell", command])
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return res.returncode, (res.stdout + res.stderr).strip()
        except Exception as e:
            return -1, str(e)

    def get_installed_packages(self) -> Dict[str, str]:
        """Returns dict of package -> status ('enabled' or 'disabled')"""
        packages = {}
        code, out = self.run_adb("pm list packages -e")
        if code == 0:
            for line in out.splitlines():
                if line.startswith("package:"):
                    packages[line.replace("package:", "").strip()] = "enabled"
        code_d, out_d = self.run_adb("pm list packages -d")
        if code_d == 0:
            for line in out_d.splitlines():
                if line.startswith("package:"):
                    packages[line.replace("package:", "").strip()] = "disabled"
        return packages

    def audit_device(self) -> dict:
        """Classifies installed packages into safe debloat, optional, and critical."""
        installed = self.get_installed_packages()
        safe_candidates = []
        optional_candidates = []
        critical_present = []

        for pkg, info in self.catalog.get("safe_debloat", {}).items():
            if pkg in installed:
                safe_candidates.append({
                    "package": pkg,
                    "name": info.get("name", pkg),
                    "description": info.get("description", ""),
                    "status": installed[pkg],
                    "risk": info.get("risk", "Low")
                })

        for pkg, info in self.catalog.get("optional", {}).items():
            if pkg in installed:
                optional_candidates.append({
                    "package": pkg,
                    "name": info.get("name", pkg),
                    "description": info.get("description", ""),
                    "status": installed[pkg],
                    "risk": info.get("risk", "Medium")
                })

        for pkg, name in self.catalog.get("critical_system", {}).items():
            if pkg in installed:
                critical_present.append({"package": pkg, "name": name, "status": installed[pkg]})

        return {
            "safe_debloat": safe_candidates,
            "optional": optional_candidates,
            "critical_system": critical_present,
            "total_installed": len(installed)
        }

    def disable_package(self, package: str) -> Tuple[bool, str]:
        """Safely disables a package without deleting APK or clearing data."""
        if package in self.catalog.get("critical_system", {}):
            return False, f"Refusing to disable critical system package: {package}"
        code, out = self.run_adb(f"pm disable-user --user 0 {package}")
        return code == 0 and "disabled" in out.lower(), out

    def enable_package(self, package: str) -> Tuple[bool, str]:
        """Re-enables a previously disabled package."""
        code, out = self.run_adb(f"pm enable {package}")
        return code == 0 and "enabled" in out.lower(), out

    def apply_notification_sound_fixes(self) -> dict:
        """Applies HyperOS / Android global sound fixes without breaking phone stability."""
        results = {}
        # 1. Unmute global notification processing
        c1, o1 = self.run_adb("settings put global useNotification 1")
        results["useNotification"] = "Enabled" if c1 == 0 else f"Failed: {o1}"

        # 2. Prevent UI tap noises
        c2, o2 = self.run_adb("settings put system sound_effects_enabled 0")
        results["sound_effects_enabled"] = "Muted (No UI Tap Sounds)" if c2 == 0 else f"Failed: {o2}"

        # 3. Add global messaging apps to notificationbar_launch_list
        messaging_apps = [
            "com.facebook.orca", "com.whatsapp", "com.whatsapp.w4b",
            "com.google.android.gm", "com.imo.android.imoim", "com.discord",
            "org.telegram.messenger", "com.google.android.apps.messaging",
            "com.android.mms", "org.thoughtcrime.securesms"
        ]
        _, cur_list = self.run_adb("settings get system notificationbar_launch_list")
        cur_list = cur_list.strip() if cur_list else ""
        missing = [app for app in messaging_apps if app not in cur_list]
        if missing:
            new_list = cur_list + ("," if cur_list and not cur_list.endswith(",") else "") + ",".join(missing) + ","
            c3, o3 = self.run_adb(f'settings put system notificationbar_launch_list "{new_list}"')
            results["notificationbar_launch_list"] = f"Added {len(missing)} messaging apps" if c3 == 0 else f"Failed: {o3}"
        else:
            results["notificationbar_launch_list"] = "All messaging apps already whitelisted"

        # 4. Mute background ghost chime from MiLink service if present
        c4, o4 = self.run_adb("cmd appops set 10176 POST_NOTIFICATION ignore")
        results["milink_ghost_sound"] = "Muted UID 10176" if c4 == 0 else o4

        return results
