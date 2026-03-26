# Repository Structure Guide for SOLID Principles & Design Pattern Analysis

This document provides an overview of the fifteen repositories assigned for refactoring analysis. Each repository represents a different programming language and architectural approach, offering diverse opportunities to identify SOLID principles violations and design pattern issues.

---



## Repository index

| # | Repository | Language | Domain | Branch | Primary Source Path |
|---:|---|---|---|---|---|
| 1 | catchorg/Catch2 | C++ | Testing framework | `devel` | `src/` |
| 2 | FasterXML/jackson-core | Java | JSON processing | `3.x` | `src/main/java/` |
| 3 | alibaba/fastjson2 | Java | JSON processing | `main` | `core/` |
| 4 | elastic/logstash | Java + Ruby | Data ingestion pipeline | `main` | `logstash-core/src/main/java/` |
| 5 | google/gson | Java | JSON serialization | `main` | `gson/src/main/` |
| 6 | GoogleContainerTools/jib | Java | Container image build | (multi) | `*/src/main/java/` |
| 7 | ankidroid/Anki-Android | Kotlin/Java | Android flashcards | `main` | `AnkiDroid/src/main/java/...` |
| 8 | wordpress-mobile/WordPress-Android | Kotlin/Java | Android app | `trunk` | `WordPress/src/main/java/...` |
| 9 | Kotlin/kotlinx.coroutines | Kotlin | Concurrency library | `master` | `kotlinx-coroutines-core/` |
| 10 | Kotlin/kotlinx-datetime | Kotlin | Date/time library | `master` | `core/` |
| 11 | psf/requests | Python | HTTP client library | `main` | `src/requests/` |
| 12 | pallets/flask | Python | Web framework | `main` | `src/flask/` |
| 13 | pydata/xarray | Python | Labeled arrays / scientific computing | `main` | `xarray/` |
| 14 | mwaskom/seaborn | Python | Statistical visualization | `master` | `seaborn/` |
| 15 | pytest-dev/pytest | Python | Testing framework | `main` | `src/_pytest/` |

---

## 1) C++ — catchorg/Catch2

**Pinned path:**  
https://github.com/catchorg/Catch2/tree/devel/src


- **Primary source:** `src/` (Catch2 library implementation)

### Useful directories
- `tests/` — test suite
- `examples/` — usage examples
- `benchmarks/` — benchmark code
- `fuzzing/` — fuzz testing
- `tools/` — utilities
- `extras/` — integrations/utilities
- `docs/` — documentation
- `third_party/` — third-party dependencies

### Build systems
- CMake, Bazel, Meson (multiple build setups available)

---

## 2) Java — FasterXML/jackson-core

**Pinned path:**  
https://github.com/FasterXML/jackson-core/tree/3.x/src

- This directory typically follows the standard Maven project structure:
- `src/main/java/` - Main Java source code
- `src/test/java/` - Test source code


### Useful directories
- `src/test/java/` — tests
- `docs/` — documentation
- `release-notes/` — release notes

### Build system
- Maven (`pom.xml`, `mvnw`, `mvnw.cmd`)

---

## 3) Java — alibaba/fastjson2

**Pinned path:**  
https://github.com/alibaba/fastjson2/tree/main/core


- `core/` — core fastjson2 library

### Helpful modules (optional for broader SOLID/pattern exploration)
- Compatibility: `fastjson1-compatible/`
- Extensions: `extension/`, `extension-spring5/`, `extension-spring6/`, `extension-solon/`, `extension-jaxrs/`
- Codegen/testing: `codegen/`, `codegen-test/`, `safemode-test/`, `test-jdk17/`, `test-jdk25/`, `android-test/`
- Examples: `example-spring-test/`, `example-spring6-test/`, `example-solon-test/`
- Benchmarks: `benchmark/`, `benchmark_25/`
- Docs/scripts: `docs/`, `scripts/`

### Build system
- Maven (`pom.xml`, `mvnw`, `mvnw.cmd`)

---

## 4) Java + Ruby — elastic/logstash

**Pinned path:**  
https://github.com/elastic/logstash/tree/main/logstash-core/src/main/java

### Java Source Code:
- Java core: `logstash-core/src/main/java/`
- `logstash-core/lib/` - Core library files
- `logstash-core-plugin-api/lib/` - Plugin API library


### Key directories
- Java libs: `logstash-core/lib/`, `logstash-core-plugin-api/lib/`
- Ruby code: `lib/bootstrap/`, `lib/pluginmanager/`, `lib/systeminstall/`, `lib/secretstore/`
- Config/data: `config/`, `data/`, `patterns/`
- Tooling: `tools/` (benchmark CLI, deps report, docgen)
- CI/QA/deploy: `qa/`, `docker/`, `.buildkite/scripts/`, `bin/`, `rakelib/`

### Build system
- Gradle (Java components)
- Rake (Ruby/build orchestration)
- Maven (some tooling)

---

## 5) Java — google/gson

**Pinned path:**  
https://github.com/google/gson/tree/main/gson/src/main


- `gson/` — core library module (production code under `gson/src/main/...`)

### Additional modules (optional)
- `extras/` — utilities/extensions
- `proto/` — protobuf integration
- `metrics/` — performance/metrics module
- Tests: `test-graal-native-image/`, `test-jpms/`, `test-shrinker/`

### Documentation highlights
- `UserGuide.md`, `Troubleshooting.md`, `GsonDesignDocument.md`
- `CHANGELOG.md`, `ReleaseProcess.md`

### Build system
- Maven (`pom.xml`, `.mvn/`)

---

## 6) Java — GoogleContainerTools/jib

### (multi-module)
Primary code exists per module (each typically has `src/main/java/` and `src/test/java/`):

- [`jib-core/`](https://github.com/GoogleContainerTools/jib/tree/master/jib-core) — core library  
  - `jib-core/src/main/java/`
- [`jib-gradle-plugin/`](https://github.com/GoogleContainerTools/jib/tree/master/jib-gradle-plugin) — Gradle plugin  
  - `jib-gradle-plugin/src/main/java/`
- [`jib-maven-plugin/`](https://github.com/GoogleContainerTools/jib/tree/master/jib-maven-plugin) — Maven plugin  
  - `jib-maven-plugin/src/main/java/`
- [`jib-cli/`](https://github.com/GoogleContainerTools/jib/tree/master/jib-cli) — command-line interface  
  - `jib-cli/src/main/java/`
- [`jib-plugins-common/`](https://github.com/GoogleContainerTools/jib/tree/master/jib-plugins-common) — shared plugin code  
  - `jib-plugins-common/src/main/java/`
- [`jib-build-plan/`](https://github.com/GoogleContainerTools/jib/tree/master/jib-build-plan) — build plan API  
  - `jib-build-plan/src/main/java/`


### Build system
- Mixed per module (Maven/Gradle depending on module)

---

## Kotlin resource — kotlin-bench article

Reference article (not a codebase):  
https://www.firebender.com/blog/kotlin-bench

Use this as background reading for benchmarking practices in Kotlin projects.

---

## 7) Kotlin/Java — ankidroid/Anki-Android

**Pinned path:**  
https://github.com/ankidroid/Anki-Android/tree/main/AnkiDroid/src/main/java/com/ichi2


- `AnkiDroid/` — main Android app (Kotlin/Java)
- Primary package path example: `AnkiDroid/src/main/java/com/ichi2`

### Supporting modules
- `api/`, `common/`, `libanki/`
- Tooling/testing: `annotations/`, `lint-rules/`, `testlib/`, `tools/`, `vbpd/`
- Docs/CI: `docs/`, `fastlane/`

### Build system
- Gradle (Kotlin DSL present: `build.gradle.kts`, `settings.gradle.kts`, wrapper)

---

## 8) Kotlin/Java — wordpress-mobile/WordPress-Android

**Pinned path:**  
https://github.com/wordpress-mobile/WordPress-Android/tree/trunk/WordPress/src/main/java/org/wordpress/android


- `WordPress/src/main/java/org/wordpress/android` — main Android source

### Supporting directories
- `libs/`, `aars/`, `config/`
- Docs/CI: `docs/`, `fastlane/`, `.buildkite/`, `.configure-files/`, `trunk` branch tooling

### Build system
- Gradle

### Branch note
- Mainline branch is `trunk` (not `main`/`master`)

---

## 9) Kotlin — Kotlin/kotlinx.coroutines

**Pinned path:**  
https://github.com/Kotlin/kotlinx.coroutines/tree/master/kotlinx-coroutines-core


- `kotlinx-coroutines-core/` — core library module

### Other modules (optional)
- Debug/test: `kotlinx-coroutines-debug/`, `kotlinx-coroutines-test/`
- Integrations: `reactive/`, `ui/`, `integration/`
- Packaging: `kotlinx-coroutines-bom/`
- Bench/testing/build: `benchmarks/`, `integration-testing/`, `test-utils/`, `buildSrc/`
- Docs/site: `docs/`, `site/`

### Build system
- Gradle + Kotlin DSL

---

## 10) Kotlin — Kotlin/kotlinx-datetime

**Pinned path:**  
https://github.com/Kotlin/kotlinx-datetime/tree/master/core


- `core/` — main datetime library module
- `timezones/` — timezone functionality (good for additional design exploration)

### Supporting directories
- `benchmarks/`, `integration-testing/`, `buildSrc/`, `kotlin-js-store/`, `.teamcity/`, `license/`

### Build system
- Gradle + Kotlin DSL  
- Kotlin Multiplatform (dates/times)

---

## 11) Python — psf/requests

**Repository:** https://github.com/psf/requests  
**Source:** https://github.com/psf/requests/tree/main/src/requests  
**Tests:** https://github.com/psf/requests/tree/main/tests  


- `src/requests/` — main library implementation (src-layout)

### Key directories
- `tests/` — unit/integration tests



---

## 12) Python — pallets/flask

**Repository:** https://github.com/pallets/flask  
**Source:** https://github.com/pallets/flask/tree/main/src/flask  
**Tests:** https://github.com/pallets/flask/tree/main/tests  

- `src/flask/` — core framework implementation (src-layout)

### Key directories
- `tests/` — test suite
- `examples/` — example applications / usage patterns (if present)


---

## 13) Python — pydata/xarray

**Repository:** https://github.com/pydata/xarray  
**Source:** https://github.com/pydata/xarray/tree/main/xarray  

### What to analyze
- `xarray/` — main library package (flat layout)

### Tests & testing utilities (within the package)
- `xarray/tests/` — tests
- `xarray/testing/` — testing helpers/utilities



---

## 14) Python — mwaskom/seaborn

**Repository:** https://github.com/mwaskom/seaborn  
**Source:** https://github.com/mwaskom/seaborn/tree/master/seaborn  
**Tests:** https://github.com/mwaskom/seaborn/tree/master/tests  


- `seaborn/` — main library package

### Key directories
- `tests/` — test suite



---

## 15) Python — pytest-dev/pytest

**Repository:** https://github.com/pytest-dev/pytest  
**Source:** https://github.com/pytest-dev/pytest/tree/main/src/_pytest  
**Tests:** https://github.com/pytest-dev/pytest/tree/main/testing  


- `src/_pytest/` — core framework implementation (src-layout)

### Key directories
- `testing/` — test suite (note: `testing/`, not `tests/`)


---

> **Important**: After refactoring, ensure all existing tests pass to confirm no regression.


---

## Resources

- **SOLID Principles**: https://en.wikipedia.org/wiki/SOLID
- **Design Patterns**: *Design Patterns: Elements of Reusable Object-Oriented Software* — Gang of Four
- **Refactoring**: *Refactoring: Improving the Design of Existing Code* — Martin Fowler ([refactoring.guru](https://refactoring.guru/))
- **Clean Architecture**: *Clean Architecture* — Robert C. Martin

---

## Notes

- Each repository represents different architectural challenges suited to different SOLID principles
- Focus on understanding the domain and existing design intent before refactoring
- Document your findings and the rationale behind each refactoring decision
- Maintain code readability and maintainability as the primary goals


---

# Appendix — Repository Source File Statistics

This appendix provides verified source file and line counts for each repository's analysed path. All counts cover only source files of the primary language extension (`.cpp`, `.java`, `.kt`, or `.py`) within the tracked path and branch.

---

## Master index (all entries)

| #  | Repository                         | Language    | Domain                              | Branch   | Pinned path                           | Ext     | Files | Lines    | LOC/file | URL  |
| -- | ---------------------------------- | ----------- | ----------------------------------- | -------- | ------------------------------------- | ------- | ----- | -------- | ------- | ---- |
| 1  | catchorg/Catch2                    | C++         | Testing framework                   | `devel`  | `src`                                 | `.cpp`  | 106   | 13,291   | 125.4   | [link](https://github.com/catchorg/Catch2/tree/devel/src) |
| 2  | FasterXML/jackson-core             | Java        | JSON processing                     | `3.x`    | `src`                                 | `.java` | 390   | 120,296  | 308.5   | [link](https://github.com/FasterXML/jackson-core/tree/3.x/src) |
| 3  | alibaba/fastjson2                  | Java        | JSON processing                     | `main`   | `core`                                | `.java` | 2,733 | 408,084  | 149.3   | [link](https://github.com/alibaba/fastjson2/tree/main/core) |
| 4  | elastic/logstash                   | Java + Ruby | Data ingestion pipeline             | `main`   | `logstash-core/src/main/java`         | `.java` | 386   | 46,292   | 119.9   | [link](https://github.com/elastic/logstash/tree/main/logstash-core/src/main/java) |
| 5  | google/gson                        | Java        | JSON serialization                  | `main`   | `gson/src/main`                       | `.java` | 87    | 19,303   | 221.9   | [link](https://github.com/google/gson/tree/main/gson/src/main) |
| 6  | GoogleContainerTools/jib           | Java        | Container image build               | `master` | `jib-core/src/main/java`              | `.java` | 165   | 22,997   | 139.4   | [link](https://github.com/GoogleContainerTools/jib/tree/master/jib-core/src/main/java) |
| 7  | ankidroid/Anki-Android             | Kotlin/Java | Android flashcards                  | `main`   | `AnkiDroid/src/main/java/com/ichi2`   | `.kt`   | 610   | 109,634  | 179.7   | [link](https://github.com/ankidroid/Anki-Android/tree/main/AnkiDroid/src/main/java/com/ichi2) |
| 8  | wordpress-mobile/WordPress-Android | Kotlin/Java | Android app                         | `trunk`  | `WordPress/src/main/java/org/wordpress/android` | `.kt` | 2,049 | 231,006  | 112.7   | [link](https://github.com/wordpress-mobile/WordPress-Android/tree/trunk/WordPress/src/main/java/org/wordpress/android) |
| 9  | Kotlin/kotlinx.coroutines          | Kotlin      | Concurrency library                 | `master` | `kotlinx-coroutines-core`             | `.kt`   | 698   | 75,956   | 108.8   | [link](https://github.com/Kotlin/kotlinx.coroutines/tree/master/kotlinx-coroutines-core) |
| 10 | Kotlin/kotlinx-datetime            | Kotlin      | Date/time library                   | `master` | `core`                                | `.kt`   | 181   | 30,564   | 168.9   | [link](https://github.com/Kotlin/kotlinx-datetime/tree/master/core) |
| 11 | psf/requests                       | Python      | HTTP client library                 | `main`   | `src/requests`                        | `.py`   | 18    | 5,644    | 313.6   | [link](https://github.com/psf/requests/tree/main/src/requests) |
| 12 | pallets/flask                      | Python      | Web framework                       | `main`   | `src/flask`                           | `.py`   | 24    | 9,449    | 393.7   | [link](https://github.com/pallets/flask/tree/main/src/flask) |
| 13 | pydata/xarray                      | Python      | Labeled arrays / scientific computing | `main` | `xarray`                              | `.py`   | 197   | 189,240  | 961.6   | [link](https://github.com/pydata/xarray/tree/main/xarray) |
| 14 | mwaskom/seaborn                    | Python      | Statistical visualization           | `master` | `seaborn`                             | `.py`   | 54    | 29,278   | 542.2   | [link](https://github.com/mwaskom/seaborn/tree/master/seaborn) |
| 15 | pytest-dev/pytest                  | Python      | Testing framework                   | `main`   | `src/_pytest`                         | `.py`   | 70    | 35,161   | 502.3   | [link](https://github.com/pytest-dev/pytest/tree/main/src/_pytest) |
                   
---


