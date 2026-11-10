# Project Overview
- **Core Goal:** One-command autonomous Android debloater and notification sound optimization suite, specifically tuned for Chinese ROMs (Xiaomi HyperOS, MIUI, ColorOS, OriginOS, HarmonyOS) to eliminate bloatware, ensure zero data leakage, and guarantee reliable notification delivery with authentic per-app audio.
- **Target Audience:** Android power users, privacy-conscious individuals, and users struggling with silenced notifications or aggressive OEM background killing.

## Architecture & Tech Stack
- **Languages/Frameworks:** Python 3.10+, PowerShell, ADB (Android Debug Bridge)
- **Database/State Management:** JSON configuration catalogs, live Android System Settings (`settings`, `cmd appops`, `cmd notification`)
- **Tooling:** ADB wireless/USB, Pytest

## High-Level Rules
- Zero data loss: Never clear user data or delete apps without explicit user review and confirmation.
- Surgical modifications: Test and verify notification channels and system audio protocol before modifying.
- Always maintain Git synchronization.
