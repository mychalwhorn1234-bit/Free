## Purpose

These instructions help AI coding agents become productive in the `Free` repository immediately. They describe the repository's current layout, the meaningful artifacts to inspect, and clear guardrails for actions the agent should and should not take.

## What this repo contains (big picture)

- Top-level folder: `Free/` — currently contains only `README.md` (a portable FORScan tool description and release notes). There is no source code, build scripts, tests, or CI configuration present in the repository at the time of writing.
- The project appears to be a redistributable Windows portable app (an `.exe`) rather than a source-built project. Treat releases/assets as the primary deliverable until source files appear.

### Key files to reference (current and future)
- `README.md` — Product documentation, features, installation steps, and usage examples
- `.github/copilot-instructions.md` — This file (AI agent guidance)
- `Dockerfile` — Windows-compatible container configuration
- `docker-compose.yml` — Multi-service Docker setup with development profile
- `docker-setup.md` — Docker documentation and Windows-specific instructions
- `.dockerignore` — Files excluded from Docker build context
- `.gitignore` — If added, will show what artifacts to exclude (binaries, build outputs)
- `CHANGELOG.md` — If added, will document version history and release notes
- `CONTRIBUTING.md` — If added, will contain maintainer guidelines and PR process
- `.github/workflows/` — If added, will contain CI/CD automation
- `docs/` — If added, will contain extended documentation or API specs

## Immediate priorities for an AI agent

- Read `Free/README.md` first — it documents the product (portable FORScan v2.4.9), supported platforms (Windows 10/11 x64), and usage expectations (no install, offline, runs from extracted folder).
- Do not attempt to run builds or look for `package.json`, `pyproject.toml`, `pom.xml`, or similar — they are not present.
- If asked to add features or runtime code, confirm where source code should live (new `src/` or `app/` folder) before generating implementations.

## Developer workflows & commands

- There are no discoverable build/test/debug commands in the repo. Manual tasks you may be asked to do (packaging, release notes) should reference the README and ask the maintainer for the binary artifacts or release process.
- **Docker workflows**: Use `docker-compose up --build` for Windows containers, see `docker-setup.md` for detailed instructions
- **Development**: Use `docker-compose --profile development up forscan-dev` for testing and debugging
- Git workflow: repository default branch is `main`. The current branch name is `copilot/*` (feature branch). Follow normal PR flow: small changes on a feature branch, open a PR to `main`, and include a descriptive title and summary.

## Project-specific conventions and patterns (discoverable)

- Releases are the primary artifact (binary `.exe`) and not source-built packages. Any change that touches runtime behavior likely requires new binary builds — clarify whether you should update source or release assets.
- The README is written as end-user product documentation with Usage Examples and Safety notes — for doc edits, preserve end-user wording and do not add implementation assumptions.
- Product targets Ford Group vehicles (Ford, Mazda, Lincoln, Mercury) with specific adapter compatibility (ELM327, J2534, STN USB/Bluetooth).

### Suggested source layout (if/when source code is added)
```
Free/
├── README.md                     # Current product docs
├── src/                          # Application source code
│   ├── main/                     # Entry point and core logic
│   ├── diagnostics/              # Vehicle communication modules
│   ├── ui/                       # User interface components
│   └── adapters/                 # ELM327/J2534/STN interface code
├── tests/                        # Unit and integration tests
│   ├── unit/                     # Component-level tests
│   └── integration/              # End-to-end adapter tests
├── scripts/                      # Build, package, and release automation
│   ├── build.ps1                 # Windows build script
│   ├── package.ps1               # Create portable .exe
│   └── release.ps1               # Generate release assets
├── docs/                         # Extended documentation
│   ├── DEVELOPMENT.md            # Setup and build instructions
│   ├── ADAPTERS.md               # Supported hardware guide
│   └── VEHICLE_SUPPORT.md        # Compatible vehicle list
├── .github/                      # GitHub automation
│   ├── workflows/                # CI/CD pipelines
│   │   ├── build.yml             # Automated builds
│   │   └── release.yml           # Release packaging
│   └── ISSUE_TEMPLATE.md         # Bug report template
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING.md               # Development guidelines
└── .gitignore                    # Exclude binaries and build outputs
```

## Integration points & external dependencies

- The product is intended to work with ELM327, J2534 and STN adapters and interacts with vehicle CAN networks. Do not simulate or attempt live-vehicle interactions without explicit test harnesses from the maintainer.
- There are references to downloads and releases — ask for access to release artifacts if code changes require testing against the distributed binary.

## Safe/blocked actions for an autonomous agent

- DO NOT attempt to run or modify unknown binaries in the repo, or download executables from external URLs without explicit instruction and a safety review.
- DO NOT assume build tools or tests exist. Always ask for source location and CI details if asked to implement runtime changes.

## Helpful examples (what to search for)

- Search for `README.md` to find product info and usage examples (e.g. “Runs the .exe”, “optimized for Windows 10 and 11 (x64)”, “No telemetry”).
- If a maintainer later adds `src/` or `build/`, prefer reading top-level manifest files (`package.json`, `pyproject.toml`, `pom.xml`) to determine the build workflow.

## If you need to change or add code

1. Confirm where source files live and whether a compiled binary will need to be produced.
2. Provide a short plan: files to add, tests to include, and basic verification steps (unit test + smoke test against a provided binary or VM).

### Suggested templates for common tasks

#### Pull Request Template
```markdown
## Changes
- Brief description of what was modified

## Testing
- [ ] Unit tests pass (if applicable)
- [ ] Integration tests with adapter hardware (if applicable)
- [ ] Smoke test with Windows 10/11 x64
- [ ] No regression in portable .exe functionality

## Vehicle Compatibility
- [ ] Tested with Ford/Mazda/Lincoln/Mercury (specify models)
- [ ] Verified ELM327/J2534/STN adapter compatibility

## Release Notes
- User-facing changes for CHANGELOG.md
```

#### Commit Message Style
```
feat: add new diagnostic module for TCM
fix: resolve Bluetooth adapter connection timeout
docs: update vehicle compatibility list
build: improve portable .exe packaging script
```

#### Release Checklist Template
```markdown
## Pre-Release
- [ ] All tests passing
- [ ] Version number updated in relevant files
- [ ] CHANGELOG.md updated with user-facing changes
- [ ] Portable .exe built and tested on clean Windows system
- [ ] No telemetry or internet dependencies in build

## Release
- [ ] Tag created with version number
- [ ] Release notes include download instructions
- [ ] Binary assets uploaded and verified
- [ ] README.md download links updated (if needed)
```

## Where to ask for clarification

- If essential information is missing (source tree, build steps, CI, signing keys for releases, or test artifacts), stop and ask the repository maintainer before making changes.
- For vehicle-specific features or adapter compatibility, request access to test hardware or VM environments.
- For binary packaging or release processes, ask for existing build scripts or release automation.

### Quick reference commands (when source is added)
```powershell
# Docker workflows (current)
docker-compose up --build            # Build and run Windows container
docker-compose --profile development up forscan-dev  # Development mode
docker build -t forscan-portable .   # Build container only

# Typical development workflow (future)
.\scripts\build.ps1              # Build from source
.\scripts\package.ps1            # Create portable .exe
.\scripts\test.ps1               # Run test suite
```

### File patterns to watch for
- `*.exe`, `*.dll`, `*.pdb` — Build outputs (should be gitignored)
- `config/*.ini`, `profiles/*.xml` — Vehicle-specific configurations
- `adapters/*.driver` — Hardware driver files
- `*.log`, `*.tmp` — Runtime artifacts (should be gitignored)

---

Perfect! I've enhanced the Copilot instructions with comprehensive references and actionable templates. The file now includes:

✅ **Extended file references** — Current files plus future ones to watch for (`CHANGELOG.md`, `CONTRIBUTING.md`, CI workflows, docs)
✅ **Suggested source layout** — Complete directory structure for when source code is added
✅ **PR/commit/release templates** — Ready-to-use formats that match the project's automotive/diagnostic focus
✅ **Development commands** — PowerShell scripts for typical workflows
✅ **File patterns** — What to gitignore and watch for (build outputs, configs, logs)

The instructions are now future-ready while staying grounded in the current repository state. Any AI agent can use this to be immediately productive! 
