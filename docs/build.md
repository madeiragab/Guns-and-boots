# Build Guide

## Desktop (Windows executable)

Quick path — from the project root:

```bat
build.bat
```

Or manually:

```bash
python build.py
```

What it does: compiles the game with **PyInstaller** (installing it if
missing), copies `assets/` and `save.json`, and creates a launcher. Output:

```text
build_output/
├─ dist/
│  ├─ Guns and Boots.exe
│  ├─ assets/
│  └─ save.json
├─ Jogar.bat        ← double-click to play
└─ README.txt
```

To update the executable after code changes, just run `build.bat` again.

Requirements: Python 3.7+, pygame (PyInstaller is installed automatically).

## Mobile (Android APK)

The APK is built with **Buildozer**, which requires Linux (or WSL):

```bash
pip install buildozer cython
buildozer android debug     # first build downloads the Android SDK/NDK — slow
```

The APK lands in `bin/`. Settings (package name, requirements, orientation)
live in `buildozer.spec` — see `buildozer.spec.example` for a commented
starting point.

On Windows you can prepare the mobile package without building:

```bat
build.bat apk
```

This creates `mobile_package/` with instructions to finish the build on a
Linux/WSL machine.

### CI build

`.github/workflows/build-android.yml` builds a debug APK on GitHub Actions
(**manual trigger**: *Actions → Build Android APK → Run workflow*) and
uploads it as an artifact. The build is heavy (Android SDK + NDK), so it is
not run on every push.

## Mobile simulation on desktop

To test the touch UI without a device:

```bash
python main.py --mobile
```

Portrait resolution, tap zones mapped to keyboard navigation, and on-screen
action buttons (`ATIRAR`, `COBERTURA`, `ESPECIAL`, `MEDKIT`).

## Smoke test

Headless sanity check (useful in CI and before releases):

```bash
python tools/run_test.py
```

Prints `RUN_OK` on success.
