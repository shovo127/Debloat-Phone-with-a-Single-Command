"""
CLI Entry point for One-Command Phone Debloater and Notification Sound Optimizer.
"""

import argparse
import sys
from debloater_core import DebloaterCore


def print_banner():
    print("=" * 65)
    print("  ONE-COMMAND ANDROID DEBLOATER & NOTIFICATION AUDIO SUITE")
    print("=" * 65)


def run_audit(core: DebloaterCore):
    print("\n🔍 Scanning connected Android device...\n")
    audit = core.audit_device()
    print(f"Total installed packages detected: {audit['total_installed']}")

    print("\n[ SAFE DEBLOAT CANDIDATES (Telemetry, Ads, Ghost Audio Culprits) ]")
    if not audit["safe_debloat"]:
        print("  None detected.")
    else:
        for item in audit["safe_debloat"]:
            print(f"  • {item['name']} ({item['package']})")
            print(f"    Status: {item['status'].upper()} | Risk: {item['risk']}")
            print(f"    Why: {item['description']}\n")

    print("[ OPTIONAL OEM & USER APPS (Review Before Disabling) ]")
    if not audit["optional"]:
        print("  None detected.")
    else:
        for item in audit["optional"]:
            print(f"  • {item['name']} ({item['package']}) - Status: {item['status'].upper()}")
            print(f"    Info: {item['description']}\n")

    print(f"[ CRITICAL SYSTEM PACKAGES PROTECTED: {len(audit['critical_system'])} verified safe ]\n")


def run_fix_audio(core: DebloaterCore):
    print("\n🔊 Restoring HyperOS Notification Audio Settings...")
    res = core.apply_notification_sound_fixes()
    for k, v in res.items():
        print(f"  ✔ {k}: {v}")
    print("\nNotification audio hardening successfully applied.\n")


def main():
    parser = argparse.ArgumentParser(description="One-Command Phone Debloater and Notification Audio Suite")
    parser.add_argument("--device", "-s", type=str, help="ADB target serial or IP:port")
    parser.add_argument("--audit", action="store_true", help="Audit device without modifying any packages")
    parser.add_argument("--fix-audio", action="store_true", help="Apply HyperOS notification sound fixes")
    parser.add_argument("--disable", type=str, help="Safely disable a specific package")
    parser.add_argument("--enable", type=str, help="Re-enable a specific package")

    args = parser.parse_args()
    print_banner()

    core = DebloaterCore(target_device=args.device)

    if args.fix_audio:
        run_fix_audio(core)

    if args.disable:
        success, msg = core.disable_package(args.disable)
        status = "SUCCESS" if success else "FAILED"
        print(f"[{status}] Disabling {args.disable}: {msg}")

    if args.enable:
        success, msg = core.enable_package(args.enable)
        status = "SUCCESS" if success else "FAILED"
        print(f"[{status}] Enabling {args.enable}: {msg}")

    if args.audit or (not args.fix_audio and not args.disable and not args.enable):
        run_audit(core)


if __name__ == "__main__":
    main()
