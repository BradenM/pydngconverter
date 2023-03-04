<a name="unreleased"></a>
## [Unreleased]

### Bug Fixes
- **deps:** update black/mypy versions
- **main:** remove sub py3.9 asyncio queue loop parameter.
- **pkg:** dep version constraints

### CI
- **chlog:** add changelog generation workflow.
- **main:** add missed install step.
- **main:** update main test workflow.

### Features
- **deps:** add pre-commit dev dep.
- **dx:** add ruff config.
- **pkg:** update troves, update includes.
- **pkg:** use dependency group for docs deps


<a name="v0.2.0"></a>
## [v0.2.0] - 2021-02-14
### Bug Fixes
- **compat:** error if env_override not provided to resolve_executable
- **compat:** incorrect type for resolve exec
- **compat:** index error template issue
- **compat:** resolve app ext incorrect map ref
- **compat:** correctly display env override error message
- **macos:** dng converter not launching on macos
- **main:** handle implicit destination correctly
- **pydng:** only throw wand import error if using jpeg extract

### CI
- add workflow for running tests
- remove travis ci file
- **cov:** fix coveralls upload

### Features
- **compat:** add compat module for x-platform compatibility
- **compat:** add xplatform method for resolving binary executable path
- **compat:** make compat module async
- **compat:** add check for binary path resolution overrides via env variable
- **convert:** remove cr2 file match in favor of simple file glob
- **convert:** add dataclass DNGParameters to handle converter config options
- **convert:** add DNGJob and DNGBatchJob dataclasses for hosting job information
- **deps:** remove no longer used deps, update packaging info
- **dng:** add support for lossy compression param
- **flags:** refactor all flag enums to flags module
- **pkg:** set correct min python requirements, update lockfile, update bump config
- **pkg:** add bump2version dev dep, enable signed tags
- **pkg:** migrate to poetry, update pkgs
- **pkg:** move docs deps to extras
- **pkg:** update setup file
- **pydng:** collect and return results from convert, cleanup codestyle
- **pydng:** rewrite DNGConverter to be async and execute conversions in parallel
- **pydng:** add max_workers arg
- **util:** add util for executing sync func in thread
- **util:** add async compat timeit util

### Performance Improvements
- Batch Convert by CPU Count, Yield Each Proc on Completion


<a name="v0.1.0"></a>
## v0.1.0 - 2019-08-28
### Features
- Ensure exiftool is installed if Extract option is passed
- Option to Extract Thumbnail from Raw File
- Implemented Multiprocessing for Converting Images
- Add Parameter and Process Handling for DNGConverter
- Add Cli Flag Enums
- Initial commit


[Unreleased]: https://github.com/BradenM/pydngconverter/compare/v0.2.0...HEAD
[v0.2.0]: https://github.com/BradenM/pydngconverter/compare/v0.1.0...v0.2.0
