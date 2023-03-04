<a name="v0.2.0"></a>

## [0.3.0](https://github.com/BradenM/pydngconverter/compare/v0.2.0...v0.3.0) (2023-03-04)


### Features

* **deps:** Add pre-commit dev dep. ([28df1d0](https://github.com/BradenM/pydngconverter/commit/28df1d098b63d2736d41ed16c5125e88aaa41e5b))
* **deps:** Remove bump2version dev-dep ([7893ac8](https://github.com/BradenM/pydngconverter/commit/7893ac8ec482601f6fed2f48b25d915a3f495b42))
* **deps:** Update rich/typing-extensions ([e288076](https://github.com/BradenM/pydngconverter/commit/e288076e8a4c04eed428bf7b388dd07e7c7130b9))
* **dng:** Update flags for parity with latest Adobe DNG Converter v14.5 ([b434cf4](https://github.com/BradenM/pydngconverter/commit/b434cf48271be7ba2f95efe08f4f724b28cf86d5))
* **dx:** Add ruff config. ([effa2e3](https://github.com/BradenM/pydngconverter/commit/effa2e33742e8c77597d5370eb3cb1b9f94d701c))
* **pkg:** Update troves, update includes. ([df27d47](https://github.com/BradenM/pydngconverter/commit/df27d4709cb9d247c2b9594f99b336c90bea914f))
* **pkg:** Use dependency group for docs deps ([33cff8c](https://github.com/BradenM/pydngconverter/commit/33cff8c2cfad592210620abf41a24ee731b2a2a6))


### Bug Fixes

* **deps:** Update black/mypy versions ([012a61b](https://github.com/BradenM/pydngconverter/commit/012a61b603087a20bb85ad2e1219c9f6f9d30e92))
* **deps:** Update dependency psutil to ~5.9 ([0239fca](https://github.com/BradenM/pydngconverter/commit/0239fca415ae12a7ff128110dd3fdc2df98f11f2))
* **dng:** Linear flag should depend on linear option, not fast load. ([c1470e6](https://github.com/BradenM/pydngconverter/commit/c1470e6e9580a115450838dbfe2d499eba3f9910))
* **main:** Remove sub py3.9 asyncio queue loop parameter. ([03ce54d](https://github.com/BradenM/pydngconverter/commit/03ce54d6dc5f79450467e4faa1e6fa4627c13c54))
* **pkg:** Dep version constraints ([fb8e9e7](https://github.com/BradenM/pydngconverter/commit/fb8e9e72c5bf1c1e9fe471278395b485bfe475bc))


### Documentation

* **chglog:** Generate changelog. ([4b7abdf](https://github.com/BradenM/pydngconverter/commit/4b7abdf866eca600aa68b54119b1833a608f0a8c))
* **chglog:** Patch up for release-please ([151db83](https://github.com/BradenM/pydngconverter/commit/151db834c1340344c2e2f11bdeb16671a881d975))

## [v0.2.0] - 2021-02-14

### Bug Fixes

-   **compat:** error if env_override not provided to resolve_executable
-   **compat:** incorrect type for resolve exec
-   **compat:** index error template issue
-   **compat:** resolve app ext incorrect map ref
-   **compat:** correctly display env override error message
-   **macos:** dng converter not launching on macos
-   **main:** handle implicit destination correctly
-   **pydng:** only throw wand import error if using jpeg extract

### CI

-   add workflow for running tests
-   remove travis ci file
-   **cov:** fix coveralls upload

### Features

-   **compat:** add compat module for x-platform compatibility
-   **compat:** add xplatform method for resolving binary executable path
-   **compat:** make compat module async
-   **compat:** add check for binary path resolution overrides via env variable
-   **convert:** remove cr2 file match in favor of simple file glob
-   **convert:** add dataclass DNGParameters to handle converter config options
-   **convert:** add DNGJob and DNGBatchJob dataclasses for hosting job information
-   **deps:** remove no longer used deps, update packaging info
-   **dng:** add support for lossy compression param
-   **flags:** refactor all flag enums to flags module
-   **pkg:** set correct min python requirements, update lockfile, update bump config
-   **pkg:** add bump2version dev dep, enable signed tags
-   **pkg:** migrate to poetry, update pkgs
-   **pkg:** move docs deps to extras
-   **pkg:** update setup file
-   **pydng:** collect and return results from convert, cleanup codestyle
-   **pydng:** rewrite DNGConverter to be async and execute conversions in parallel
-   **pydng:** add max_workers arg
-   **util:** add util for executing sync func in thread
-   **util:** add async compat timeit util

### Performance Improvements

-   Batch Convert by CPU Count, Yield Each Proc on Completion

<a name="v0.1.0"></a>

## v0.1.0 - 2019-08-28

### Features

-   Ensure exiftool is installed if Extract option is passed
-   Option to Extract Thumbnail from Raw File
-   Implemented Multiprocessing for Converting Images
-   Add Parameter and Process Handling for DNGConverter
-   Add Cli Flag Enums
-   Initial commit

[v0.2.0]: https://github.com/BradenM/pydngconverter/compare/v0.1.0...v0.2.0
