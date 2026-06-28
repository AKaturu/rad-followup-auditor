# Release Guide

`rad-followup-auditor` publishes native command-line builds through GitHub Actions.

## Manual Test Build

1. Open the repository in GitHub.
2. Go to **Actions**.
3. Select **Desktop/native release**.
4. Choose **Run workflow** on `main`.
5. Download the Windows, macOS, and Linux artifacts from the completed run.

## Public Release

Create and push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow will build:

- Windows executable archive
- macOS executable archive
- Linux executable archive
- SHA-256 checksum files for each archive

When the tag build completes, the workflow creates a GitHub Release and attaches the archives.

## Local Native Build

```bash
python -m pip install -e ".[packaging]"
python scripts/build_native.py --app-name rad-followup-auditor --project-name rad-followup-auditor --module rad_followup_auditor.cli --package rad_followup_auditor
```

Artifacts are written to `dist/native/`.
