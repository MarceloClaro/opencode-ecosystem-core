# SPEC-SCI-036: Uv
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Checks whether the uv Python package manager is installed and installs it if

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: uv command is string
- [x] CT-3: install method returns dict
- [x] CT-4: install has status
- [x] CT-5: install empty packages
- [x] CT-6: install empty packages error
- [x] CT-7: list installed returns dict
- [x] CT-8: list installed has status
- [x] CT-9: version returns str or none
- [x] CT-10: uv not available install

## Engine
scripts/uv_installer.py -> UVInstaller

## Test File
tests/test_uv.py
