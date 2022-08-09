# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]

### Changed

- Covalent dispatcher flask web apis ported to FastAPI in `covalent_dispatcher/_service/app.py`
- Unit tests written for Covalent dispatcher flask web apis ported to FastAPI in `covalent_dispatcher_tests/_service/app.test.py`
- Web apis of `covalent_ui` refactored to adhere to v11 DB schema
- Electron graph mini map has been moved next to controls on the GUI.
- Lattice status and count of completed & total electrons has been moved to the top of the graph on the GUI.
- Some of the Flask APIs earlier consumed by the GUI have been deprecated & removed from the code base.
- APIs exposed by the web app back end have been re-factored to adhere to the new DB schema v10

### Added

- Added count of dispatches by status on the dispatch list section of the GUI.
- APIs that the GUI consumes have been re-written using FastAPI. This includes re-factoring of older APIs and adding of new APIs.

## [0.170.0] - 2022-08-08

### Authors

- Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Changed

- Temporarily allow executor plugin variable name to be either in uppercase or lowercase

## [0.169.0] - 2022-08-08

### Authors

- Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Added

- Adding a `covalent config` convenience CLI to quickly view retrive the covalent configuration

## [0.168.0] - 2022-08-08

### Authors

- Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Added

- Adding `setup/teardown` methods as placeholders for any executor specific setup and teardown tasks

## [0.167.0] - 2022-08-08

### Authors

- Poojith U Rao <106616820+poojithurao@users.noreply.github.com>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Co-authored-by: Alejandro Esquivel <ae@alejandro.ltd>


### Added

- S3 File transfer strategy

### Fixed

- Adding maximum number of retries and timeout parameter to the get result http call.

## [0.166.0] - 2022-08-07

### Authors

- Venkat Bala <venkat@agnostiq.ai>


### Tests

- Update dask cli test to match Covalent Dask cluster configuration


### Changed

- Remove newline from log stream formatter for better log statment output
- Jsonify covalent cluster cli outputs

## [0.165.0] - 2022-08-06

### Authors

- Casey Jao <casey@agnostiq.ai>


### Changed

- Make `BaseExecutor` and `BaseAsyncExecutor` class siblings, not parent and child.

### Operations

- Only validate webapp if the webapp was built

### Tests

- Fixed randomly failing lattice json serialization test

## [0.164.0] - 2022-08-05

### Authors

- Sankalp Sanand <sankalp@agnostiq.ai>
- Faiyaz Hasan <faiyaz@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: Will Cunningham <wjcunningham7@gmail.com>


### Changed

- Use `update_config` to modify dask configuration from the cluster process
- Simplify `set_config` logic for dask configuration options on `covalent start`
- Removed default values from click options for dask configuration related values

### Added

- Configured default dask configuration options in `defaults.py`

### Fixed 

- Overwriting config address issue.

### Tests

- Moved misplaced functional/integration tests from the unit tests folder to their respective folders.
- All of the unit tests now use test DB instead of hitting a live DB.
- Updated `tests.yml` so that functional tests are run whenever tests get changed or github actions are changed.
- Several broken tests were also fixed.

## [0.163.0] - 2022-08-04

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: Casey Jao <casey@agnostiq.ai>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Added

- Added `rsync` dependency in `Dockerfile`

### Removed

- `Makefile` which was previously improperly committed

### Operations

- Functional tests are run only on `develop`
- `tests.yml` can be run manually provided a commit SHA
- `tests.yml` uses a `build` filter to conditionally install and build Covalent if build files are modified
- `docker.yml` is now only for dev work, and is manually triggered given an SHA
- `release.yml` is enhanced to push stable and pre-release images to a public ECR repo

## [0.162.0] - 2022-08-04

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: Casey Jao <casey@agnostiq.ai>


### Changed

- Updated Base executor to support non-unique `retval_key`s, particularly for use in File Transfer where we may have several CallDeps with the reserved `retval_key` of value `files`.

## [0.161.2] - 2022-08-04

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Fixed

- Updated `covalent db migrations` to overwrite `alembic.ini` `script_location` with absolute path to migrations folder
- Updated `covalent db alembic [args]` command to use project root as `cwd` for alembic subprocess  

## [0.161.1] - 2022-08-03

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>
- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>
- Poojith U Rao <106616820+poojithurao@users.noreply.github.com>
- Co-authored-by: Casey Jao <casey@agnostiq.ai>


### Fixed

- When a list was passed to an electron, the generated electron list
  had metadata copied from the electron. This was resulting in
  call_before and call_after functions being called by the electron
  list as well. The metadata (apart from executor) is now set to
  default values for the electron list.

## [0.161.0] - 2022-08-03

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>
- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>


### Changed

- Replaced `Session(DispatchDB()._get_data_store().engine)` with `workflow_db.session()`

### Removed

- `DevDataStore` class from `datastore.py`
- workflows manager

## [0.160.1] - 2022-08-02

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>
- Scott Wyman Neagle <scott@agnostiq.ai>


### Fixed

- `script_location` key not found issue when installing with pip (second attempt)

### Docs

- Remove migration guide reference from README

### Operations

- Explicitly check `release == true` in tests.yml

## [0.160.0] - 2022-08-02

### Authors

- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>


### Changed

- `Executor.run()` now accepts a `task_metadata` dictionary. Current
  keys consist of `dispatch_id` and `node_id`.

## [0.159.0] - 2022-08-02

### Authors

- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>


### Changed

- Database schema has been updated to v11

### Operations

- `paths-filter` will only be run on PRs, i.e on workflow runs, the whole test suite will be run.
- Removed retry action from running on `pytest` steps since they instead use `pytest` retries.
- `codecov.yml` added to enable carry-forward flags
- UI front-end is only built for pull requests when the source changes
- Packaging is only validated on the `develop` branch

## [0.158.0] - 2022-07-29

### Authors

- Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>


### Changed

- Construct the result object in the dispatcher `entry_point.py` module in order to avoid the Missing Latticed Id error so frequently.
- Update the sleep statement length to 0.1 seconds in the results.manager.

## [0.157.1] - 2022-07-29

### Authors

- Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Casey Jao <casey@agnostiq.ai>

### Fixed

- Pass non-kwargs to electrons in the correct order during dispatch.

## [0.157.0] - 2022-07-28

### Authors

- Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Casey Jao <casey@agnostiq.ai>


### Changed

- Expose a public `wait()` function compatible with both calling and dispatching lattices

### Docs

- Updated the RTD on `wait_for()` to use the static `wait()` function

### Operations

- pre-commit autoupdate

### Docs

- Changed the custom executor how-to to be shorter and more concise.



## [0.156.0] - 2022-07-27

### Authors

- Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Added

- Bash decorator is introduced
- Lepton commands can be specified as a list of strings rather than strings alone.

## [0.155.1] - 2022-07-26

### Authors

- Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Fixed

- `script_location` key not found issue when running alembic programatically

### Operations

- Fixed syntax errors in `stale.yml` and in `hotfix.yml`
- `docker.yml` triggered after version bump in `develop` instead of before
- Enhanced `tests.yml` to upload coverage reports by domain

## [0.155.0] - 2022-07-26

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>


### Added

- Exposing `alembic {args}` cli commands through: `covalent db alembic {args}`

## [0.154.0] - 2022-07-25

### Authors

- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
- Alejandro Esquivel <ae@alejandro.ltd>


### Added

- Added methods to programatically fetch information from Alembic without needing subprocess

## [0.153.1] - 2022-07-25

### Authors

- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>


### Fixed

- Stdout and stderr are now captured when using the dask executor.


### Tests

- Fixed Dask cluster CLI tests

## [0.153.0] - 2022-07-25

### Authors

- Faiyaz Hasan <faiyaz@agnostiq.ai>


### Added

- Helper function to load and save files corresponding to the DB filenames.

### Changed

- Files with .txt, .log extensions are stored as strings.
- Get result web request timeout to 2 seconds.

## [0.152.0] - 2022-07-25

### Authors

- Faiyaz Hasan <faiyaz@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Changed

- Pass default DataStore object to node value retrieval method in the Results object.

## [0.151.1] - 2022-07-22

### Authors

- Faiyaz Hasan <faiyaz@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Fixed

- Adding maximum number of retries and timeout parameter to the get result http call.
- Disabling result_webhook for now.

## [0.151.0] - 2022-07-22

### Authors

- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Will Cunningham <wjcunningham7@gmail.com>
- Sankalp Sanand <sankalp@agnostiq.ai>


### Added

- `BaseAsyncExecutor` has been added which can be inherited by new async-aware executors.

### Changed

- Since tasks were basically submitting the functions to a Dask cluster by default, they have been converted into asyncio `Tasks` instead which support a far larger number of concurrent tasks than previously used `ThreadPool`.

- `tasks_pool` will still be used to schedule tasks which use non-async executors.

- Executor's `executor` will now receive a callable instead of a serialized function. This allows deserializing the function where it is going to be executed while providing a simplified `execute` at the same time.

- `uvloop` is being used instead of the default event loop of `asyncio` for better performance.

- Tests have also been updated to reflect above changes.

### Operations

- Made Santosh the sole owner of `/docs`

## [0.150.0] - 2022-07-22

### Authors

- Faiyaz Hasan <faiyaz@agnostiq.ai>


### Added

- Initialize database tables when the covalent server is started.

## [0.149.0] - 2022-07-21

### Authors

- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>


### Removed

- `result.save()`
- `result._write_dispatch_to_python_file()`

## [0.148.0] - 2022-07-21

### Authors

- Alejandro Esquivel <ae@alejandro.ltd>


### Changed

- Changed DataStore default db path to correspond to dispatch db config path

### Operations

- Added workflow to stale and close pull requests


### Docs

- Fixed `get_metadata` calls in examples to remove `results_dir` argument
- Removed YouTube video temporarily

## [0.147.0] - 2022-07-21

### Authors

- Casey Jao <casey@agnostiq.ai>


### Changed

- Simplified interface for custom executors. All the boilerplate has
  been moved to `BaseExecutor`.

## [0.146.0] - 2022-07-20

### Authors

- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
- Faiyaz Hasan <faiyaz@agnostiq.ai>



### Added

- Ensure that transportable objects are rendered correctly when printing the result object.

### Tests

- Check that user data is not unpickled by the Covalent server process

## [0.145.0] - 2022-07-20

### Authors

- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>


### Removed

- `entry_point.get_result()`

### Changed

- get_result to query an HTTP endpoint instead of a DB session

## [0.144.0] - 2022-07-20

### Authors

- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Alejandro Esquivel <ae@alejandro.ltd>


### Added

- Set up alembic migrations & added migration guide (`alembic/README.md`)

## [0.143.0] - 2022-07-19

### Authors

- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Changed

- Installation will fail if `cova` is installed while trying to install `covalent`.

## [0.142.0] - 2022-07-19

### Authors

- Poojith U Rao <106616820+poojithurao@users.noreply.github.com>
- Co-authored-by: Will Cunningham <wjcunningham7@gmail.com>
- Anna Hughes <annagwen42@gmail.com>
- Co-authored-by: Poojith <poojith@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Faiyaz Hasan <faiyaz@agnostiq.ai>


### Added

- `electron_num`, `completed_electron_num` fields to the Lattice table.

## [0.141.0] - 2022-07-19

### Authors

- Poojith U Rao <106616820+poojithurao@users.noreply.github.com>
- Co-authored-by: Will Cunningham <wjcunningham7@gmail.com>
- Anna Hughes <annagwen42@gmail.com>
- Co-authored-by: Poojith <poojith@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Changed

- Deprecate topological sort in favor of inspect in-degree of nodes until they are zero before dispatching task
- Use deepcopy to generate a copy of the metadata dictionary before saving result object to the database

### Docs

- Adding incomplete pennylane kernel tutorial
- Adding quantum ensemble tutorial

## [0.140.0] - 2022-07-19

### Authors

- Faiyaz Hasan <faiyaz@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>


### Added

- Fields `deps_filename`, `call_before_filename` and `call_after_filename` to the `Electron` table.
- Re-write the deps / call before and after file contents when inserting / updating electron record in the database.

### Changed

- Modify the test and implementation logic of inserting the electron record with these new fields.
- Field `key` to `key_filename` in `Electron` table.

## [0.139.1] - 2022-07-19

### Authors

- Divyanshu Singh <55018955+divshacker@users.noreply.github.com>
- Co-authored-by: Scott Wyman Neagle <wymnea@protonmail.com>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Will Cunningham <wjcunningham7@users.noreply.github.com>


### Fixed

- Fixes Reverse IP problem. All References to `0.0.0.0` are changed to `localhost` . More details can be found [here](https://github.com/AgnostiqHQ/covalent/issues/202)

## [0.139.0] - 2022-07-19

### Authors

- Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Faiyaz Hasan <faiyaz@agnostiq.ai>
- Co-authored-by: Will Cunningham <wjcunningham7@gmail.com>


### Added

- Columns `is_active` in the lattice, eLectron and Electron dependency tables.

### Docs

- Adding a RTD tutorial/steps on creating a custom executor

## [0.138.0] - 2022-07-19

### Authors

- Anna Hughes <annagwen42@gmail.com>
- Co-authored-by: Will Cunningham <wjcunningham7@gmail.com>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>


### Added

- Docker build workflow

### Changed

- Dockerfile uses multi-stage build

### Docs

- New tutorial demonstrating how to solve the MaxCut Problem with QAOA and Covalent

## [0.137.0] - 2022-07-19

### Authors

- Prasanna Venkatesh <54540812+Prasy12@users.noreply.github.com>
- Co-authored-by: Alejandro Esquivel <ae@alejandro.ltd>


### Added

- Ability to hide/show labels on the graph
- Graph layout with elk configurations

### Changed

- Changed API socket calls interval for graph optimization.

### Tests

- Disabled several dask functional tests

## [0.136.0] - 2022-07-18

### Authors

- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>


### Changed

- Result.save() has been deprecated in favor of Result.persist() and querying the database directly.

## [0.135.0] - 2022-07-18

### Authors

- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Alejandro Esquivel <ae@alejandro.ltd>


### Operations

- Psiog is only codeowner of js files
- Fix in changelog action to handle null author when a bot is committing

### Added

- Support injecting return values of calldeps into electrons during workflow execution

## [0.134.0] - 2022-07-15

### Authors

- Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Changed

- Covalent server can now process workflows without having their deps installed

## [0.133.0] - 2022-07-15

### Authors

- Will Cunningham <wjcunningham7@users.noreply.github.com>


### Removed

- Removed the deprecated function `draw_inline` as well as the `matplotlib` dependency.

### Operations

- Fixing the retry block for tests

## [0.132.0] - 2022-07-14

### Authors

- Will Cunningham <wjcunningham7@users.noreply.github.com>


### Added

- Bash lepton support reintroduced with some UX modifications to the Lepton class. Leptons which use scripting languages can be specified as either (1) a command run in the shell/console or (2) a call to a function in a library/script. Leptons which use compiled languages must specify a library and a function name.
- The keyword argument `display_name` can be used to override the name appearing in the UI. Particularly useful when the lepton is a command.
- All arguments except for language are now keyword arguments.
- Keyword arguments passed to a Bash lepton are understood to define environment variables within the shell.
- Non-keyword arguments fill in `$1`, `$2`, etc.
- Named outputs enumerate variables within the shell which will be returned to the user. These can be either `Lepton.OUTPUT` or `Lepton.INPUT_OUTPUT` types.

### Added

- New fields to the decomposed result object Database: 

## [0.131.0] - 2022-07-13

### Authors

- Sankalp Sanand <sankalp@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>


### Fixed

- `covalent --version` now looks for `covalent` metadata instead of `cova`

### Tests

- Updated the cli test to include whether the correct version number is shown when `covalent --version` is run

### Added

- Method to write electron id corresponding to sublattices in `execution.py` when running `_run_task`.

## [0.130.0] - 2022-07-12

### Authors

- Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>

### Changed

- Ignoring tests for `cancel_dispatch` and `construct_bash`
- Create a dummy requirements.txt file for pip deps tests
- Fix version of `Werkzeug` package to avoid running into ValueError (unexpected kwarg `as_tuple`)
- Update `customization` how to test by specifying the section header `sdk`

## [0.129.0] - 2022-07-12

### Authors

- Sankalp Sanand <sankalp@agnostiq.ai>
- Co-authored-by: Alejandro Esquivel <ae@alejandro.ltd>

### Added

- Support for `wait_for` type edges when two electrons are connected by their execution side effects instead of output-input relation.

### Changed

- `active_lattice.electron_outputs` now contains the node ids as well for the electron which is being post processed.

## [0.128.1] - 2022-07-12

### Authors

- Faiyaz Hasan <faiyaz@agnostiq.ai>


### Fixed

- `Result.persist` test in `result_test.py`.
- Electron dependency `arg_index` is changed back to Nullable.

## [0.128.0] - 2022-07-12

### Authors

- Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
- Co-authored-by: Casey Jao <casey@agnostiq.ai>
- Co-authored-by: Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

### Added

- File transfer support for leptons

## [0.127.0] - 2022-07-11

### Authors

- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>
- Co-authored-by: Venkat Bala <venkat@agnostiq.ai>


### Added

- When saving to DB, also persist to the new DB if running in develop mode

### Tests

- Flask app route tests

## [0.126.0] - 2022-07-11

### Authors

- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Co-authored-by: Sankalp Sanand <sankalp@agnostiq.ai>


### Added

- Added Folder class
- Added internal call before/after deps to execute File Transfer operations pre/post electron execution.

### Operations

- Enhanced hotfix action to create branches from existing commits

## [0.125.0] - 2022-07-09

### Authors

- Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
- Co-authored-by: Alejandro Esquivel <ae@alejandro.ltd>
- Venkat Bala <venkat@agnostiq.ai>
- Co-authored-by: Okechukwu Ochia <emmirald@gmail.com>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Added

- Dask Cluster CLI functional/unit tests

### Docs

- Updated RTD concepts, how-to-guides, and api docs with electron dependencies.

### Operations

- Separate out running tests and uploading coverage report to circumvent bug in
  retry action

## [0.124.0] - 2022-07-07

### Authors

- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>
- Faiyaz Hasan <faiyaz@agnostiq.ai>


### Added

- `Result.persist` method in `covalent/_results_manager/result.py`.

### Operations

- Package pre-releases go to `covalent` instead of `cova` on PyPI.

## [0.123.0] - 2022-07-07

### Authors

- Scott Wyman Neagle <scott@agnostiq.ai>
- Co-authored-by: Faiyaz Hasan <faiyaz@agnostiq.ai>
- Will Cunningham <wjcunningham7@users.noreply.github.com>
- Alejandro Esquivel <ae@alejandro.ltd>
- Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Added

- Added Folder class
- Added internal call before/after deps to execute File Transfer operations pre/post electron execution.

### Operations

- `codeql.yml` and `condabuild.yml` run nightly instead of on every PR.
- Style fixes in changelog

## [0.122.1] - 2022-07-06

### Authors

Will Cunningham <wjcunningham7@users.noreply.github.com>
Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Operations

- Added license scanner action
- Pre-commit autoupdate

### Tests

- Tests for running workflows with more than one iteration

### Fixed

- Attribute error caused by attempts to retrieve the name from the node function when the node function is set to None

## [0.122.0] - 2022-07-04

### Authors

Faiyaz Hasan <faiyaz@agnostiq.ai>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Added

- `covalent/_results_manager/write_result_to_db.py` module and methods to insert / update data in the DB.
- `tests/covalent_tests/results_manager_tests/write_result_to_db_test.py` containing the unit tests for corresponding functions.

### Changed

- Electron `type` column to a string type rather than an `ElectronType` in DB models.
- Primary keys from `BigInteger` to `Integer` in DB models.

## [0.121.0] - 2022-07-04

### Authors

Will Cunningham <wjcunningham7@users.noreply.github.com>
Co-authored-by: Alejandro Esquivel <ae@alejandro.ltd>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


### Removed

- Unused requirements `gunicorn` and `eventlet` in `requirements.txt` as well as `dask` in `tests/requirements.txt`, since it is already included in the core requirements.

### Docs

- Updated the compatibility matrix in the docs.

## [0.120.0] - 2022-07-04

### Authors

Okechukwu  Emmanuel Ochia <okechukwu@agnostiq.ai>
Co-authored-by: Venkat Bala <venkat@agnostiq.ai>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
Co-authored-by: Scott Wyman Neagle <scott@agnostiq.ai>


### Added

- Adding `cluster` CLI options to facilitate interacting with the backend Dask cluster
- Adding options to `covalent start` to enable specifying number of workers, memory limit and threads per worker at cluster startup

### Changed

- Update `DaskAdminWorker` docstring with better explanation

## [0.119.1] - 2022-07-04

### Authors

Scott Wyman Neagle <scott@agnostiq.ai>
Casey Jao <casey@agnostiq.ai>


### Fixed

- `covalent status` checks if the server process is still alive.

### Operations

- Updates to changelog logic to handle multiple authors

## [0.119.0] - 2022-07-03
### Authors
@cjao 


### Added

- Introduce support for pip dependencies

## [0.118.0] - 2022-07-02
### Authors
@AlejandroEsquivel 


### Added

- Introduced File, FileTransfer, and FileTransferStrategy classes to support various File Transfer use cases prior/post electron execution

## [0.117.0] - 2022-07-02
### Authors
@Emmanuel289 


### Added

- Included retry action in 'tests.yaml' workflow.

## [0.116.0] - 2022-06-29
### Authors
@Prasy12 

### Changed

- Changed API socket calls interval for graph optimization.

### Added

- Ability to change to different layouts from the GUI.

## [0.115.0] - 2022-06-28
### Authors
@cjao 


### Added

- Introduce support for `call_before`, `call_after`, and bash dependencies

### Operations

- Unit tests performed on Python 3.10 on Ubuntu and MacOS images as well as 3.9 on MacOS
- Updated codeowners so that AQ Engineers doesn't own this CHANGELOG
- pre-commit autoupdate

## [0.114.0] - 2022-06-23
### Authors
@dependabot[bot] 


### Changed

- Changed eventsource version on webapp yarn-lock file.

### Operations

- Added Github push changelog workflow to append commiters username
- Reusable JavaScript action to parse changelog and update version

## [0.113.0] - 2022-06-21

### Added

- Introduce new db models and object store backends

### Operations

- Syntax fix in hotfix.yml

### Docs

- Added new tutorial: Linear and convolutional autoencoders

## [0.112.0] - 2022-06-20

### Changed

- Changed async version on webapp package-lock file.

## [0.111.0] - 2022-06-20

### Changed

- Changed eventsource version on webapp package-lock file.

### Docs

- Added new tutorial: Covalentified version of the Pennylane Variational Classifier tutorial.

## [0.110.3] - 2022-06-17

### Fixed

- Fix error when parsing electron positional arguments in workflows

### Docs

- Remove hardcoding version info in README.md

## [0.110.2] - 2022-06-10

### Docs

- Fix MNIST tutorial
- Fix Quantum Gravity tutorial
- Update RTD with migration guide compatible with latest release
- Convert all references to `covalent start` from Jupyter notebooks to markdown statements
- Update release notes summary in README.md
- Fixed display issues with figure (in dark mode) and bullet points in tutorials

### Operations

- Added a retry block to the webapp build step in `tests.yml`

## [0.110.1] - 2022-06-10

### Fixed

- Configure dask to not use daemonic processes when creating a cluster

### Operations

- Sync the VERSION file within `covalent` directory to match the root level VERSION
- Manually patch `covalent/VERSION`

## [0.110.0] - 2022-06-10

### Changed

- Web GUI list size and status label colors changed.
- Web GUI graph running icon changed to non-static icon.

### Docs

- Removed references to the Dask executor in RTD as they are no longer needed.

## [0.109.1] - 2022-06-10

### Fixed

- `covalent --version` now works for PyPI releases

## [0.109.0] - 2022-06-10

### Docs

- Update CLI help statements

### Added

- Add CLI functionality to start covalent with/without Dask
- Add CLI support to parse `covalent_ui.log` file

### Operations

- Updating codeowners to establish engineering & psiog ownership

### Docs

- Added new tutorial: Training quantum embedding kernels for classification.

## [0.108.0] - 2022-06-08

### Added

- WCI yaml file

### Docs

- Add pandoc installation updates to contributing guide

## [0.107.0] - 2022-06-07

### Changed

- Skipping stdout/stderr redirection tests until implemented in Dask parent process

### Added

- Simplifed starting the dask cluster using `multiprocessing`
- Added `bokeh==2.4.3` to requirements.txt to enable view Dask dashboard

### Fixed

- Changelog-reminder action now works for PRs from forks.

## [0.106.2] - 2022-06-06

### Fixed

- Specifying the version for package `furo` to `2022.4.7` to prevent breaking doc builds

### Docs

- Added new tutorial: Using Covalent with PennyLane for hybrid computation.

## [0.106.1] - 2022-06-01

### Fixed

- Changelog-reminder action now works for PRs from forks

### Docs

- Removed references to microservices in RTD
- Updated README.md.
- Changed `ct.electron` to `ct.lattice(executor=dask_executor)` in MNIST classifier tutorial

## [0.106.0] - 2022-05-26

### Changed

- Visual theme for Webapp GUI changed in accordance to new theme
- Fonts, colors, icons have been updated

## [0.105.0] - 2022-05-25

### Added

- Add a pre-commit hook for `detect-secrets`.
- Updated the actions in accordance with the migration done in the previous version.

## [0.104.0] - 2022-05-23

### Changed

- Services have been moved to a different codebase. This repo is now hosting the Covalent SDK, local dispatcher backend, Covalent web GUI, and documentation. Version is bumped to `0.104.0` in order to avoid conflicts.
- Update tests to match the current dispatcher api
- Skip testing dask executor until dask executor plugin is made public
- Using 2 thread pools to manage multiple workflows better and the other one for executing electrons in parallel.

### Fixed

- Add psutil and PyYAML to requirements.txt
- Passing the same Electron to multiple inputs of an Electron now works. UI fix pending.
- Dask from `requirements.txt`.

### Removed

- Asyncio usage for electron level concurrency.
- References to dask

### Added

- Functional test added for dask executor with the cluster running locally.
- Scalability tests for different workflows and workflow sizes under `tests/stress_tests/scripts`
- Add sample performance testing workflows under `tests/stress_tests`
- Add pipelines to continuously run the tutorial notebooks
- Create notebook with tasks from RTD

## [0.32.3] - 2022-03-16

### Fixed

- Fix missing UI graph edges between parameters and electrons in certain cases.
- Fix UI crashes in cases where legacy localStorage state was being loaded.

## [0.32.2] - 2022-03-16

### Added

- Images for graphs generated in tutorials and how-tos.
- Note for quantum gravity tutorial to tell users that `tensorflow` doesn't work on M1 Macs.
- `Known Issues` added to `README.md`

### Fixed

- `draw` function usage in tutorials and how-tos now reflects the UI images generated instead of using graphviz.
- Images now render properly in RTD of how-tos.

### Changed

- Reran all the tutorials that could run, generating the outputs again.

## [0.32.1] - 2022-03-15

### Fixed

- CLI now starts server directly in the subprocess instead of as a daemon
- Logs are provided as pipes to Popen instead of using a shell redirect
- Restart behavior fixed
- Default port in `covalent_ui/app.py` uses the config manager

### Removed

- `_graceful_restart` function no longer needed without gunicorn

## [0.32.0] - 2022-03-11

### Added

- Dispatcher microservice API endpoint to dispatch and update workflow.
- Added get runnable task endpoint.

## [0.31.0] - 2022-03-11

### Added

- Runner component's main functionality to run a set of tasks, cancel a task, and get a task's status added to its api.

## [0.30.5] - 2022-03-11

### Updated

- Updated Workflow endpoints & API spec to support upload & download of result objects as pickle files

## [0.30.4] - 2022-03-11

### Fixed

- When executing a task on an alternate Conda environment, Covalent no longer has to be installed on that environment. Previously, a Covalent object (the execution function as a TransportableObject) was passed to the environment. Now it is deserialized to a "normal" Python function, which is passed to the alternate Conda environment.

## [0.30.3] - 2022-03-11

### Fixed

- Fixed the order of output storage in `post_process` which should have been the order in which the electron functions are called instead of being the order in which they are executed. This fixes the order in which the replacement of function calls with their output happens, which further fixes any discrepencies in the results obtained by the user.

- Fixed the `post_process` test to check the order as well.

## [0.30.2] - 2022-03-11

### Changed

- Updated eventlet to 0.31.0

## [0.30.1] - 2022-03-10

### Fixed

- Eliminate unhandled exception in Covalent UI backend when calling fetch_result.

## [0.30.0] - 2022-03-09

### Added

- Skeleton code for writing the different services corresponding to each component in the open source refactor.
- OpenAPI specifications for each of the services.

## [0.29.3] - 2022-03-09

### Fixed

- Covalent UI is built in the Dockerfile, the setup file, the pypi workflow, the tests workflow, and the conda build script.

## [0.29.2] - 2022-03-09

### Added

- Defaults defined in executor plugins are read and used to update the in-memory config, as well as the user config file. But only if the parameter in question wasn't already defined.

### Changed

- Input parameter names and docstrings in _shared_files.config.update_config were changed for clarity.

## [0.29.1] - 2022-03-07

### Changed

- Updated fail-fast strategy to run all tests.

## [0.29.0] - 2022-03-07

### Added

- DispatchDB for storing dispatched results

### Changed

- UI loads dispatches from DispatchDB instead of browser local storage

## [0.28.3] - 2022-03-03

### Fixed

Installed executor plugins don't have to be referred to by their full module name. Eg, use "custom_executor", instead of "covalent_custom_plugin.custom_executor".

## [0.28.2] - 2022-03-03

### Added

- A brief overview of the tutorial structure in the MNIST classification tutorial.

## [0.28.1] - 2022-03-02

### Added

- Conda installation is only supported for Linux in the `Getting Started` guide.
- MNIST classifier tutorial.

### Removed

- Removed handling of default values of function parameters in `get_named_params` in `covalent/_shared_files/utils.py`. So, it is actually being handled by not being handled since now `named_args` and `named_kwargs` will only contain parameters that were passed during the function call and not all of them.

## [0.28.0] - 2022-03-02

### Added

- Lepton support, including for Python modules and C libraries
- How-to guides showing how to use leptons for each of these

## [0.27.6] - 2022-03-01

### Added

- Added feature development basic steps in CONTRIBUTING.md.
- Added section on locally building RTD (read the docs) in the contributing guide.

## [0.27.5] - 2022-03-01

### Fixed

- Missing UI input data after backend change - needed to be derived from graph for electrons, lattice inputs fixed on server-side, combining name and positional args
- Broken UI graph due to variable->edge_name renaming
- Missing UI executor data after server-side renaming

## [0.27.4] - 2022-02-28

### Fixed

- Path used in `covalent/executor/__init__.py` for executor plugin modules needed updating to `covalent/executor/executor_plugins`

### Removed

- Disabled workflow cancellation test due to inconsistent outcomes. Test will be re-enabled after cancellation mechanisms are investigated further.

## [0.27.3] - 2022-02-25

### Added

- Added `USING_DOCKER.md` guide for running docker container.
- Added cli args to covalent UI flask server `covalent_ui/app.py` to modify port and log file path.

### Removed

- Removed gunicorn from cli and Dockerfile.

### Changed

- Updated cli `covalent_dispatcher/_cli/service.py` to run flask server directly, and removed dispatcher and UI flags.
- Using Flask blueprints to merge Dispatcher and UI servers.
- Updated Dockerfile to run flask server directly.
- Creating server PID file manually in `covalent_dispatcher/_cli/service.py`.
- Updated tests and docs to reflect merged servers.
- Changed all mentions of port 47007 (for old UI server) to 48008.

## [0.27.2] - 2022-02-24

### Changed

- Removed unnecessary blockquotes from the How-To guide for creating custom executors
- Changed "Covalent Cloud" to "Covalent" in the main code text

## [0.27.1] - 2022-02-24

### Removed

- Removed AQ-Engineers from CODEOWNERS in order to fix PR review notifications

## [0.27.0] - 2022-02-24

### Added

- Support for positional only, positional or keyword, variable positional, keyword only, variable keyword types of parameters is now added, e.g an electron can now use variable args and variable kwargs if the number/names of parameters are unknown during definition as `def task(*args, **kwargs)` which wasn't possible before.

- `Lattice.args` added to store positional arguments passed to the lattice's workflow function.

- `get_named_params` function added in `_shared_files/utils.py` which will return a tuple containing named positional arguments and named keyword arguments. The names help in showing and storing these parameters in the transport graph.

- Tests to verify whether all kinds of input paramaters are supported by electron or a lattice.

### Changed

- No longer merging positional arguments with keyword arguments, instead they are separately stored in respective nodes in the transport graph.

- `inputs` returned from `_get_inputs` function in `covalent_dispatcher/_core/execution.py` now contains positional as well as keyword arguments which further get passed to the executor.

- Executors now support positional and keyword arguments as inputs to their executable functions.

- Result object's `_inputs` attribute now contains both `args` and `kwargs`.

- `add_node_for_nested_iterables` is renamed to `connect_node_with_others` and `add_node_to_graph` also renamed to `add_collection_node_to_graph` in `electron.py`. Some more variable renames to have appropriate self-explanatory names.

- Nodes and edges in the transport graph now have a better interface to assign attributes to them.

- Edge attribute `variable` renamed to `edge_name`.

- In `serialize` function of the transport graph, if `metadata_only` is True, then only `metadata` attribute of node and `source` and `target` attributes of edge are kept in the then return serialized `data`.

- Updated the tests wherever necessary to reflect the above changes

### Removed

- Deprecated `required_params_passed` since an error will automatically be thrown by the `build_graph` function if any of the required parameters are not passed.

- Removed duplicate attributes from nodes in the transport graph.

## [0.26.1] - 2022-02-23

### Added

- Added Local Executor section to the API read the docs.

## [0.26.0] - 2022-02-23

### Added

- Automated reminders to update the changelog

## [0.25.3] - 2022-02-23

## Added

- Listed common mocking commands in the CONTRIBUTING.md guide.
- Additional guidelines on testing.

## [0.25.2] - 2022-02-21

### Changed

- `backend` metadata name changed to `executor`.
- `_plan_workflow` usage updated to reflect how that executor related information is now stored in the specific executor object.
- Updated tests to reflect the above changes.
- Improved the dispatch cancellation test to provide a robust solution which earlier took 10 minutes to run with uncertainty of failing every now and then.

### Removed

- Removed `TaskExecutionMetadata` as a consequence of removing `execution_args`.

## [0.25.1] - 2022-02-18

### Fixed

- Tracking imports that have been used in the workflow takes less time.

### Added

- User-imports are included in the dispatch_source.py script. Covalent-related imports are commented out.

## [0.25.0] - 2022-02-18

### Added

- UI: Lattice draw() method displays in web UI
- UI: New navigation panel

### Changed

- UI: Animated graph changes, panel opacity

### Fixed

- UI: Fixed "Not Found" pages

## [0.24.21] - 2022-02-18

### Added

- RST document describing the expectations from a tutorial.

## [0.24.20] - 2022-02-17

### Added

- Added how to create custom executors

### Changed

- Changed the description of the hyperlink for choosing executors
- Fixed typos in doc/source/api/getting_started/how_to/execution/creating_custom_executors.ipynb

## [0.24.19] - 2022-02-16

### Added

- CODEOWNERS for certain files.

## [0.24.18] - 2022-02-15

### Added

- The user configuration file can now specify an executor plugin directory.

## [0.24.17] - 2022-02-15

### Added

- Added a how-to for making custom executors.

## [0.24.16] - 2022-02-12

### Added

- Errors now contain the traceback as well as the error message in the result object.
- Added test for `_post_process` in `tests/covalent_dispatcher_tests/_core/execution_test.py`.

### Changed

- Post processing logic in `electron` and dispatcher now relies on the order of execution in the transport graph rather than node's function names to allow for a more reliable pairing of nodes and their outputs.

- Renamed `init_test.py` in `tests/covalent_dispatcher_tests/_core/` to `execution_test.py`.

### Removed

- `exclude_from_postprocess` list which contained some non executable node types removed since only executable nodes are post processed now.

## [0.24.15] - 2022-02-11

### Fixed

- If a user's configuration file does not have a needed exeutor parameter, the default parameter (defined in _shared_files/defaults.py) is used.
- Each executor plugin is no longer initialized upon the import of Covalent. This allows required parameters in executor plugins.

## Changed

- Upon updating the configuration data with a user's configuration file, the complete set is written back to file.

## Added

- Tests for the local and base executors.

## [0.24.14] - 2022-02-11

### Added

- UI: add dashboard cards
- UI: add scaling dots background

### Changed

- UI: reduce sidebar font sizes, refine color theme
- UI: refine scrollbar styling, show on container hover
- UI: format executor parameters as YAML code
- UI: update syntax highlighting scheme
- UI: update index.html description meta tag

## [0.24.13] - 2022-02-11

### Added

- Tests for covalent/_shared_files/config.py

## [0.24.12] - 2022-02-10

### Added

- CodeQL code analyzer

## [0.24.11] - 2022-02-10

### Added

- A new dictionary `_DEFAULT_CONSTRAINTS_DEPRECATED` in defaults.py

### Changed

- The `_DEFAULT_CONSTRAINT_VALUES` dictionary now only contains the `backend` argument

## [0.24.10] - 2022-02-09

### Fixed

- Sporadically failing workflow cancellation test in tests/workflow_stack_test.py

## [0.24.9] - 2022-02-09

## Changed

- Implementation of `_port_from_pid` in covalent_dispatcher/_cli/service.py.

## Added

- Unit tests for command line interface (CLI) functionalities in covalent_dispatcher/_cli/service.py and covalent_dispatcher/_cli/cli.py.

## [0.24.8] - 2022-02-07

### Fixed

- If a user's configuration file does not have a needed parameter, the default parameter (defined in _shared_files/defaults.py) is used.

## [0.24.7] - 2022-02-07

### Added

- Typing: Add Type hint `dispatch_info` parameter.
- Documentation: Updated the return_type description in docstring.

### Changed

- Typing: Change return type annotation to `Generator`.

## [0.24.6] - 2022-02-06

### Added

- Type hint to `deserialize` method of `TransportableObject` of `covalent/_workflow/transport.py`.

### Changed

- Description of `data` in `deserialize` method of `TransportableObject` of `covalent/_workflow/transport.py` from `The serialized transportable object` to `Cloudpickled function`.

## [0.24.5] - 2022-02-05

### Fixed

- Removed dependence on Sentinel module

## [0.24.4] - 2022-02-04

### Added

- Tests across multiple versions of Python and multiple operating systems
- Documentation reflecting supported configurations

## [0.24.3] - 2022-02-04

### Changed

- Typing: Use `bool` in place of `Optional[bool]` as type annotation for `develop` parameter in `covalent_dispatcher.service._graceful_start`
- Typing: Use `Any` in place of `Optional[Any]` as type annotation for `new_value` parameter in `covalent._shared_files.config.get_config`

## [0.24.2] - 2022-02-04

### Fixed

- Updated hyperlink of "How to get the results" from "./collection/query_electron_execution_result" to "./collection/query_multiple_lattice_execution_results" in "doc/source/how_to/index.rst".
- Updated hyperlink of "How to get the result of a particular electron" from "./collection/query_multiple_lattice_execution_results" to "./collection/query_electron_execution_result" in "doc/source/how_to/index.rst".

## [0.24.1] - 2022-02-04

### Changed

- Changelog entries are now required to have the current date to enforce ordering.

## [0.24.0] - 2022-02-03

### Added

- UI: log file output - display in Output tab of all available log file output
- UI: show lattice and electron inputs
- UI: display executor attributes
- UI: display error message on failed status for lattice and electron

### Changed

- UI: re-order sidebar sections according to latest figma designs
- UI: update favicon
- UI: remove dispatch id from tab title
- UI: fit new uuids
- UI: adjust theme text primary and secondary colors

### Fixed

- UI: auto-refresh result state on initial render of listing and graph pages
- UI: graph layout issues: truncate long electron/param names

## [0.23.0] - 2022-02-03

### Added

- Added `BaseDispatcher` class to be used for creating custom dispatchers which allow connection to a dispatcher server.
- `LocalDispatcher` inheriting from `BaseDispatcher` allows connection to a local dispatcher server running on the user's machine.
- Covalent only gives interface to the `LocalDispatcher`'s `dispatch` and `dispatch_sync` methods.
- Tests for both `LocalDispatcher` and `BaseDispatcher` added.

### Changed

- Switched from using `lattice.dispatch` and `lattice.dispatch_sync` to `covalent.dispatch` and `covalent.dispatch_sync`.
- Dispatcher address now is passed as a parameter (`dispatcher_addr`) to `covalent.dispatch` and `covalent.dispatch_sync` instead of a metadata field to lattice.
- Updated tests, how tos, and tutorials to use `covalent.dispatch` and `covalent.dispatch_sync`.
- All the contents of `covalent_dispatcher/_core/__init__.py` are moved to `covalent_dispatcher/_core/execution.py` for better organization. `__init__.py` only contains function imports which are needed by external modules.
- `dispatch`, `dispatch_sync` methods deprecated from `Lattice`.

### Removed

- `_server_dispatch` method removed from `Lattice`.
- `dispatcher` metadata field removed from `lattice`.

## [0.22.19] - 2022-02-03

### Fixed

- `_write_dispatch_to_python_file` isn't called each time a task is saved. It is now only called in the final save in `_run_planned_workflow` (in covalent_dispatcher/_core/__init__.py).

## [0.22.18] - 2022-02-03

### Fixed

- Added type information to result.py

## [0.22.17] - 2022-02-02

### Added

- Replaced `"typing.Optional"` with `"str"` in covalent/executor/base.py
- Added missing type hints to `get_dispatch_context` and `write_streams_to_file` in covalent/executor/base.py, BaseExecutor

## [0.22.16] - 2022-02-02

### Added

- Functions to check if UI and dispatcher servers are running.
- Tests for the `is_ui_running` and `is_server_running` in covalent_dispatcher/_cli/service.py.

## [0.22.15] - 2022-02-01

### Fixed

- Covalent CLI command `covalent purge` will now stop the servers before deleting all the pid files.

### Added

- Test for `purge` method in covalent_dispatcher/_cli/service.py.

### Removed

- Unused `covalent_dispatcher` import from covalent_dispatcher/_cli/service.py.

### Changed

- Moved `_config_manager` import from within the `purge` method to the covalent_dispatcher/_cli/service.py for the purpose of mocking in tests.

## [0.22.14] - 2022-02-01

### Added

- Type hint to `_server_dispatch` method in `covalent/_workflow/lattice.py`.

## [0.22.13] - 2022-01-26

### Fixed

- When the local executor's `log_stdout` and `log_stderr` config variables are relative paths, they should go inside the results directory. Previously that was queried from the config, but now it's queried from the lattice metadata.

### Added

- Tests for the corresponding functions in (`covalent_dispatcher/_core/__init__.py`, `covalent/executor/base.py`, `covalent/executor/executor_plugins/local.py` and `covalent/executor/__init__.py`) affected by the bug fix.

### Changed

- Refactored `_delete_result` in result manager to give the option of deleting the result parent directory.

## [0.22.12] - 2022-01-31

### Added

- Diff check in pypi.yml ensures correct files are packaged

## [0.22.11] - 2022-01-31

### Changed

- Removed codecov token
- Removed Slack notifications from feature branches

## [0.22.10] - 2022-01-29

### Changed

- Running tests, conda, and version workflows on pull requests, not just pushes

## [0.22.9] - 2022-01-27

### Fixed

- Fixing version check action so that it doesn't run on commits that are in develop
- Edited PR template so that markdown checklist appears properly

## [0.22.8] - 2022-01-27

### Fixed

- publish workflow, using `docker buildx` to build images for x86 and ARM, prepare manifest and push to ECR so that pulls will match the correct architecture.
- typo in CONTRIBUTING
- installing `gcc` in Docker image so Docker can build wheels for `dask` and other packages that don't provide ARM wheels

### Changed

- updated versions in `requirements.txt` for `matplotlib` and `dask`

## [0.22.7] - 2022-01-27

### Added

- `MANIFEST.in` did not have `covalent_dispatcher/_service` in it due to which the PyPi package was not being built correctly. Added the `covalent_dispatcher/_service` to the `MANIFEST.in` file.

### Fixed

- setuptools properly including data files during installation

## [0.22.6] - 2022-01-26

### Fixed

- Added service folder in covalent dispatcher to package.

## [0.22.5] - 2022-01-25

### Fixed

- `README.md` images now use master branch's raw image urls hosted on <https://github.com> instead of <https://raw.githubusercontent.com>. Also, switched image rendering from html to markdown.

## [0.22.4] - 2022-01-25

### Fixed

- dispatcher server app included in sdist
- raw image urls properly used

## [0.22.3] - 2022-01-25

### Fixed

- raw image urls used in readme

## [0.22.2] - 2022-01-25

### Fixed

- pypi upload

## [0.22.1] - 2022-01-25

### Added

- Code of conduct
- Manifest.in file
- Citation info
- Action to upload to pypi

### Fixed

- Absolute URLs used in README
- Workflow badges updated URLs
- `install_package_data` -> `include_package_data` in `setup.py`

## [0.22.0] - 2022-01-25

### Changed

- Using public ECR for Docker release

## [0.21.0] - 2022-01-25

### Added

- GitHub pull request templates

## [0.20.0] - 2022-01-25

### Added

- GitHub issue templates

## [0.19.0] - 2022-01-25

### Changed

- Covalent Beta Release

## [0.18.9] - 2022-01-24

### Fixed

- iframe in the docs landing page is now responsive

## [0.18.8] - 2022-01-24

### Changed

- Temporarily removed output tab
- Truncated dispatch id to fit left sidebar, add tooltip to show full id

## [0.18.7] - 2022-01-24

### Changed

- Many stylistic improvements to documentation, README, and CONTRIBUTING.

## [0.18.6] - 2022-01-24

### Added

- Test added to check whether an already decorated function works as expected with Covalent.
- `pennylane` package added to the `requirements-dev.txt` file.

### Changed

- Now using `inspect.signature` instead of `function.__code__` to get the names of function's parameters.

## [0.18.5] - 2022-01-21

### Fixed

- Various CI fixes, including rolling back regression in version validation, caching on s3 hosted badges, applying releases and tags correctly.

## [0.18.4] - 2022-01-21

### Changed

- Removed comments and unused functions in covalent_dispatcher
- `result_class.py` renamed to `result.py`

### Fixed

- Version was not being properly imported inside `covalent/__init__.py`
- `dispatch_sync` was not previously using the `results_dir` metadata field

### Removed

- Credentials in config
- `generate_random_filename_in_cache`
- `is_any_atom`
- `to_json`
- `show_subgraph` option in `draw`
- `calculate_node`

## [0.18.3] - 2022-01-20

### Fixed

- The gunicorn servers now restart more gracefully

## [0.18.2] - 2022-01-21

### Changed

- `tempdir` metadata field removed and replaced with `executor.local.cache_dir`

## [0.18.1] - 2022-01-11

## Added

- Concepts page

## [0.18.0] - 2022-01-20

### Added

- `Result.CANCELLED` status to represent the status of a cancelled dispatch.
- Condition to cancel the whole dispatch if any of the nodes are cancelled.
- `cancel_workflow` function which uses a shared variable provided by Dask (`dask.distributed.Variable`) in a dask client to inform nodes to stop execution.
- Cancel function for dispatcher server API which will allow the server to terminate the dispatch.
- How to notebook for cancelling a dispatched job.
- Test to verify whether cancellation of dispatched jobs is working as expected.
- `cancel` function is available as `covalent.cancel`.

### Changed

- In file `covalent/_shared_files/config.py` instead of using a variable to store and then return the config data, now directly returning the configuration.
- Using `fire_and_forget` to dispatch a job instead of a dictionary of Dask's `Future` objects so that we won't have to manage the lifecycle of those futures.
- The `test_run_dispatcher` test was changed to reflect that the dispatcher no longer uses a dictionary of future objects as it was not being utilized anywhere.

### Removed

- `with dask_client` context was removed as the client created in `covalent_dispatcher/_core/__init__.py` is already being used even without the context. Furthermore, it creates issues when that context is exited which is unnecessary at the first place hence not needed to be resolved.

## [0.17.5] - 2022-01-19

### Changed

- Results directory uses a relative path by default and can be overridden by the environment variable `COVALENT_RESULTS_DIR`.

## [0.17.4] - 2022-01-19

### Changed

- Executor parameters use defaults specified in config TOML
- If relative paths are supplied for stdout and stderr, those files are created inside the results directory

## [0.17.3] - 2022-01-18

### Added

- Sync function
- Covalent CLI tool can restart in developer mode

### Fixed

- Updated the UI address referenced in the README

## [0.17.2] - 2022-01-12

### Added

- Quantum gravity tutorial

### Changed

- Moved VERSION file to top level

## [0.17.1] - 2022-01-19

### Added

- `error` attribute was added to the results object to show which node failed and the reason behind it.
- `stdout` and `stderr` attributes were added to a node's result to store any stdout and stderr printing done inside an electron/node.
- Test to verify whether `stdout` and `stderr` are being stored in the result object.

### Changed

- Redesign of how `redirect_stdout` and `redirect_stderr` contexts in executor now work to allow storing their respective outputs.
- Executors now also return `stdout` and `stderr` strings, along with the execution output, so that they can be stored in their result object.

## [0.17.0] - 2022-01-18

### Added

- Added an attribute `__code__` to electron and lattice which is a copy of their respective function's `__code__` attribute.
- Positional arguments, `args`, are now merged with keyword arguments, `kwargs`, as close as possible to where they are passed. This was done to make sure we support both with minimal changes and without losing the name of variables passed.
- Tests to ensure usage of positional arguments works as intended.

### Changed

- Slight rework to how any print statements in lattice are sent to null.
- Changed `test_dispatcher_functional` in `basic_dispatcher_test.py` to account for the support of `args` and removed a an unnecessary `print` statement.

### Removed

- Removed `args` from electron's `init` as it wasn't being used anywhere.

## [0.16.1] - 2022-01-18

### Changed

- Requirement changed from `dask[complete]` to `dask[distributed]`.

## [0.16.0] - 2022-01-14

### Added

- New UI static demo build
- New UI toolbar functions - orientation, toggle params, minimap
- Sortable and searchable lattice name row

### Changed

- Numerous UI style tweaks, mostly around dispatches table states

### Fixed

- Node sidebar info now updates correctly

## [0.15.11] - 2022-01-18

### Removed

- Unused numpy requirement. Note that numpy is still being installed indirectly as other packages in the requirements rely on it.

## [0.15.10] - 2022-01-16

## Added

- How-to guide for Covalent dispatcher CLI.

## [0.15.9] - 2022-01-18

### Changed

- Switched from using human readable ids to using UUIDs

### Removed

- `human-id` package was removed along with its mention in `requirements.txt` and `meta.yaml`

## [0.15.8] - 2022-01-17

### Removed

- Code breaking text from CLI api documentation.
- Unwanted covalent_dispatcher rst file.

### Changed

- Installation of entire covalent_dispatcher instead of covalent_dispatcher/_service in setup.py.

## [0.15.7] - 2022-01-13

### Fixed

- Functions with multi-line or really long decorators are properly serialized in dispatch_source.py.
- Multi-line Covalent output is properly commented out in dispatch_source.py.

## [0.15.6] - 2022-01-11

### Fixed

- Sub-lattice functions are successfully serialized in the utils.py get_serialized_function_str.

### Added

- Function to scan utilized source files and return a set of imported modules (utils.get_imports_from_source)

## [0.15.5] - 2022-01-12

### Changed

- UI runs on port 47007 and the dispatcher runs on port 48008. This is so that when the servers are later merged, users continue using port 47007 in the browser.
- Small modifications to the documentation
- Small fix to the README

### Removed

- Removed a directory `generated` which was improperly added
- Dispatcher web interface
- sqlalchemy requirement

## [0.15.4] - 2022-01-11

### Changed

- In file `covalent/executor/base.py`, `pickle` was changed to `cloudpickle` because of its universal pickling ability.

### Added

- In docstring of `BaseExecutor`, a note was added specifying that `covalent` with its dependencies is assumed to be installed in the conda environments.
- Above note was also added to the conda env selector how-to.

## [0.15.3] - 2022-01-11

### Changed

- Replaced the generic `RuntimeError` telling users to check if there is an object manipulation taking place inside the lattice to a simple warning. This makes the original error more visible.

## [0.15.2] - 2022-01-11

### Added

- If condition added for handling the case where `__getattr__` of an electron is accessed to detect magic functions.

### Changed

- `ActiveLatticeManager` now subclasses from `threading.local` to make it thread-safe.
- `ValueError` in the lattice manager's `claim` function now also shows the name of the lattice that is currently claimed.
- Changed docstring of `ActiveLatticeManager` to note that now it is thread-safe.
- Sublattice dispatching now no longer deletes the result object file and is dispatched normally instead of in a serverless manner.
- `simulate_nitrogen_and_copper_slab_interaction.ipynb` notebook tutorial now does normal dispatching as well instead of serverless dispatching. Also, now 7 datapoints will be shown instead of 10 earlier.

## [0.15.1] - 2022-01-11

### Fixed

- Passing AWS credentials to reusable workflows as a secret

## [0.15.0] - 2022-01-10

### Added

- Action to push development image to ECR

### Changed

- Made the publish action reusable and callable

## [0.14.1] - 2022-01-02

### Changed

- Updated the README
- Updated classifiers in the setup.py file
- Massaged some RTD pages

## [0.14.0] - 2022-01-07

### Added

- Action to push static UI to S3

## [0.13.2] - 2022-01-07

### Changed

- Completed new UI design work

## [0.13.1] - 2022-01-02

### Added

- Added eventlet requirement

### Changed

- The CLI tool can now manage the UI flask server as well
- [Breaking] The CLI option `-t` has been changed to `-d`, which starts the servers in developer mode and exposes unit tests to the server.

## [0.13.0] - 2022-01-01

### Added

- Config manager in `covalent/_shared_files/config.py`
- Default location for the main config file can be overridden using the environment variable `COVALENT_CONFIG_DIR`
- Ability to set and get configuration using `get_config` and `set_config`

### Changed

- The flask servers now reference the config file
- Defaults reference the config file

### Fixed

- `ValueError` caught when running `covalent stop`
- One of the functional tests was using a malformed path

### Deprecated

- The `electron.to_json` function
- The `generate_random_filename_in_cache` function

### Removed

- The `get_api_token` function

## [0.12.13] - 2022-01-04

## Removed

- Tutorial section headings

## Fixed

- Plot background white color

## [0.12.12] - 2022-01-06

### Fixed

- Having a print statement inside electron and lattice code no longer causes the workflow to fail.

## [0.12.11] - 2022-01-04

### Added

- Completed UI feature set for first release

### Changed

- UI server result serialization improvements
- UI result update webhook no longer fails on request exceptions, logs warning intead

## [0.12.10] - 2021-12-17

### Added

- Astrophysics tutorial

## [0.12.9] - 2022-01-04

### Added

- Added `get_all_node_results` method in `result_class.py` to return result of all node executions.

- Added `test_parallelilization` test to verify whether the execution is now being achieved in parallel.

### Changed

- Removed `LocalCluster` cluster creation usage to a simple `Client` one from Dask.

- Removed unnecessary `to_run` function as we no longer needed to run execution through an asyncio loop.

- Removed `async` from function definition of previously asynchronous functions, `_run_task`, `_run_planned_workflow`, `_plan_workflow`, and `_run_workflow`.

- Removed `uvloop` from requirements.

- Renamed `test_get_results` to `test_get_result`.

- Reran the how to notebooks where execution time was mentioned.

- Changed how `dispatch_info` context manager was working to account for multiple nodes accessing it at the same time.

## [0.12.8] - 2022-01-02

### Changed

- Changed the software license to GNU Affero 3.0

### Removed

- `covalent-ui` directory

## [0.12.7] - 2021-12-29

### Fixed

- Gunicorn logging now uses the `capture-output` flag instead of redirecting stdout and stderr

## [0.12.6] - 2021-12-23

### Changed

- Cleaned up the requirements and moved developer requirements to a separate file inside `tests`

## [0.12.5] - 2021-12-16

### Added

- Conda build CI job

## [0.12.4] - 2021-12-23

### Changed

- Gunicorn server now checks for port availability before starting

### Fixed

- The `covalent start` function now prints the correct port if the server is already running.

## [0.12.3] - 2021-12-14

### Added

- Covalent tutorial comparing quantum support vector machines with support vector machine algorithms implemented in qiskit and scikit-learn.

## [0.12.2] - 2021-12-16

### Fixed

- Now using `--daemon` in gunicorn to start the server, which was the original intention.

## [0.12.1] - 2021-12-16

### Fixed

- Removed finance references from docs
- Fixed some other small errors

### Removed

- Removed one of the failing how-to tests from the functional test suite

## [0.12.0] - 2021-12-16

### Added

- Web UI prototype

## [0.11.1] - 2021-12-14

### Added

- CLI command `covalent status` shows port information

### Fixed

- gunicorn management improved

## [0.11.0] - 2021-12-14

### Added

- Slack notifications for test status

## [0.10.4] - 2021-12-15

### Fixed

- Specifying a non-default results directory in a sub-lattice no longer causes a failure in lattice execution.

## [0.10.3] - 2021-12-14

### Added

- Functional tests for how-to's in documentation

### Changed

- Moved example script to a functional test in the pipeline
- Added a test flag to the CLI tool

## [0.10.2] - 2021-12-14

### Fixed

- Check that only `kwargs` without any default values in the workflow definition need to be passed in `lattice.draw(ax=ax, **kwargs)`.

### Added

- Function to check whether all the parameters without default values for a callable function has been passed added to shared utils.

## [0.10.1] - 2021-12-13

### Fixed

- Content and style fixes for getting started doc.

## [0.10.0] - 2021-12-12

### Changed

- Remove all imports from the `covalent` to the `covalent_dispatcher`, except for `_dispatch_serverless`
- Moved CLI into `covalent_dispatcher`
- Moved executors to `covalent` directory

## [0.9.1] - 2021-12-13

### Fixed

- Updated CONTRIBUTING to clarify docstring style.
- Fixed docstrings for `calculate_node` and `check_constraint_specific_sum`.

## [0.9.0] - 2021-12-10

### Added

- `prefix_separator` for separating non-executable node types from executable ones.

- `subscript_prefix`, `generator_prefix`, `sublattice_prefix`, `attr_prefix` for prefixes of subscripts, generators,
  sublattices, and attributes, when called on an electron and added to the transport graph.

- `exclude_from_postprocess` list of prefixes to denote those nodes which won't be used in post processing the workflow.

- `__int__()`, `__float__()`, `__complex__()` for converting a node to an integer, float, or complex to a value of 0 then handling those types in post processing.

- `__iter__()` generator added to Electron for supporting multiple return values from an electron execution.

- `__getattr__()` added to Electron for supporting attribute access on the node output.

- `__getitem__()` added to Electron for supporting subscripting on the node output.

- `electron_outputs` added as an attribute to lattice.

### Changed

- `electron_list_prefix`, `electron_dict_prefix`, `parameter_prefix` modified to reflect new way to assign prefixes to nodes.

- In `build_graph` instead of ignoring all exceptions, now the exception is shown alongwith the runtime error notifying that object manipulation should be avoided inside a lattice.

- `node_id` changed to `self.node_id` in Electron's `__call__()`.

- `parameter` type electrons now have the default metadata instead of empty dictionary.

- Instead of deserializing and checking whether a sublattice is there, now a `sublattice_prefix` is used to denote when a node is a sublattice.

- In `dispatcher_stack_test`, `test_dispatcher_flow` updated to indicate the new use of `parameter_prefix`.

### Fixed

- When an execution fails due to something happening in `run_workflow`, then result object's status is now failed and the object is saved alongwith throwing the appropriate exception.

## [0.8.5] - 2021-12-10

### Added

- Added tests for choosing specific executors inside electron initialization.
- Added test for choosing specific Conda environments inside electron initialization.

## [0.8.4] - 2021-12-10

### Changed

- Removed _shared_files directory and contents from covalent_dispatcher. Logging in covalent_dispatcher now uses the logger in covalent/_shared_files/logging.py.

## [0.8.3] - 2021-12-10

### Fixed

- Decorator symbols were added to the pseudo-code in the quantum chemistry tutorial.

## [0.8.2] - 2021-12-06

### Added

- Quantum chemistry tutorial.

## [0.8.1] - 2021-12-08

### Added

- Docstrings with typehints for covalent dispatcher functions added.

### Changed

- Replaced `node` to `node_id` in `electron.py`.

- Removed unnecessary `enumerate` in `covalent_dispatcher/_core/__init__.py`.

- Removed `get_node_device_mapping` function from `covalent_dispatcher/_core/__init__.py`
  and moved the definition to directly add the mapping to `workflow_schedule`.

- Replaced iterable length comparison for `executor_specific_exec_cmds` from `if len(executor_specific_exec_cmds) > 0`
  to `if executor_specific_exec_cmds`.

## [0.8.0] - 2021-12-03

### Added

- Executors can now accept the name of a Conda environment. If that environment exists, the operations of any electron using that executor are performed in that Conda environment.

## [0.7.6] - 2021-12-02

### Changed

- How to estimate lattice execution time has been renamed to How to query lattice execution time.
- Change result querying syntax in how-to guides from `lattice.get_result` to
  `covalent.get_result`.
- Choose random port for Dask dashboard address by setting `dashboard_address` to ':0' in
  `LocalCluster`.

## [0.7.5] - 2021-12-02

### Fixed

- "Default" executor plugins are included as part of the package upon install.

## [0.7.4] - 2021-12-02

### Fixed

- Upgraded dask to 2021.10.0 based on a vulnerability report

## [0.7.3] - 2021-12-02

### Added

- Transportable object tests
- Transport graph tests

### Changed

- Variable name node_num to node_id
- Variable name node_idx to node_id

### Fixed

- Transport graph `get_dependencies()` method return type was changed from Dict to List

## [0.7.2] - 2021-12-01

### Fixed

- Date handling in changelog validation

### Removed

- GitLab CI YAML

## [0.7.1] - 2021-12-02

### Added

- A new parameter to a node's result called `sublattice_result` is added.
  This will be of a `Result` type and will contain the result of that sublattice's
  execution. If a normal electron is executed, this will be `None`.

- In `_delete_result` function in `results_manager.py`, an empty results directory
  will now be deleted.

- Name of a sublattice node will also contain `(sublattice)`.

- Added `_dispatch_sync_serverless` which synchronously dispatches without a server
  and waits for a result to be returned. This is the method used to dispatch a sublattice.

- Test for sublatticing is added.

- How-to guide added for sublatticing explaining the new features.

### Changed

- Partially changed `draw` function in `lattice.py` to also draw the subgraph
  of the sublattice when drawing the main graph of the lattice. The change is
  incomplete as we intend to add this feature later.

- Instead of returning `plt`, `draw` now returns the `ax` object.

- `__call__` function in `lattice.py` now runs the lattice's function normally
  instead of dispatching it.

- `_run_task` function now checks whether current node is a sublattice and acts
  accordingly.

### Fixed

- Unnecessary lines to rename the node's name in `covalent_dispatcher/_core/__init__.py` are removed.

- `test_electron_takes_nested_iterables` test was being ignored due to a spelling mistake. Fixed and
  modified to follow the new pattern.

## [0.7.0] - 2021-12-01

### Added

- Electrons can now accept an executor object using the "backend" keyword argument. "backend" can still take a string naming the executor module.
- Electrons and lattices no longer have Slurm metadata associated with the executor, as that information should be contained in the executor object being used as an input argument.
- The "backend" keyword can still be a string specifying the executor module, but only if the executor doesn't need any metadata.
- Executor plugin classes are now directly available to covalent, eg: covalent.executor.LocalExecutor().

## [0.6.7] - 2021-12-01

### Added

- Docstrings without examples for all the functions in core covalent.
- Typehints in those functions as well.
- Used `typing.TYPE_CHECKING` to prevent cyclic imports when writing typehints.

### Changed

- `convert_to_lattice_function` renamed to `convert_to_lattice_function_call`.
- Context managers now raise a `ValueError` instead of a generic `Exception`.

## [0.6.6] - 2021-11-30

### Fixed

- Fixed the version used in the documentation
- Fixed the badge URLs to prevent caching

## [0.6.5] - 2021-11-30

### Fixed

- Broken how-to links

### Removed

- Redundant lines from .gitignore
- *.ipynb from .gitignore

## [0.6.4] - 2021-11-30

### Added

- How-to guides for workflow orchestration.
  - How to construct an electron
  - How to construct a lattice
  - How to add an electron to lattice
  - How to visualize the lattice
  - How to add constraints to lattices
- How-to guides for workflow and subtask execution.
  - How to execute individual electrons
  - How to execute a lattice
  - How to execute multiple lattices
- How-to guides for status querying.
  - How to query electron execution status
  - How to query lattice execution status
  - How to query lattice execution time
- How-to guides for results collection
  - How to query electron execution results
  - How to query lattice execution results
  - How to query multiple lattice execution results
- Str method for the results object.

### Fixed

- Saving the electron execution status when the subtask is running.

## [0.6.3] - 2021-11-29

### Removed

- JWT token requirement.
- Covalent dispatcher login requirement.
- Update covalent login reference in README.md.
- Changed the default dispatcher server port from 5000 to 47007.

## [0.6.2] - 2021-11-28

### Added

- Github action for tests and coverage
- Badges for tests and coverage
- If tests pass then develop is pushed to master
- Add release action which tags and creates a release for minor version upgrades
- Add badges action which runs linter, and upload badges for version, linter score, and platform
- Add publish action (and badge) which builds a Docker image and uploads it to the AWS ECR

## [0.6.1] - 2021-11-27

### Added

- Github action which checks version increment and changelog entry

## [0.6.0] - 2021-11-26

### Added

- New Covalent RTD theme
- sphinx extension sphinx-click for CLI RTD
- Sections in RTD
- init.py in both covalent-dispatcher logger module and cli module for it to be importable in sphinx

### Changed

- docutils version that was conflicting with sphinx

### Removed

- Old aq-theme

## [0.5.1] - 2021-11-25

### Added

- Integration tests combining both covalent and covalent-dispatcher modules to test that
  lattice workflow are properly planned and executed.
- Integration tests for the covalent-dispatcher init module.
- pytest-asyncio added to requirements.

## [0.5.0] - 2021-11-23

### Added

- Results manager file to get results from a file, delete a result, and redispatch a result object.
- Results can also be awaited to only return a result if it has either been completed or failed.
- Results class which is used to store the results with all the information needed to be used again along with saving the results to a file functionality.
- A result object will be a mercurial object which will be updated by the dispatcher and saved to a file throughout the dispatching and execution parts.
- Direct manipulation of the transport graph inside a result object takes place.
- Utility to convert a function definition string to a function and vice-versa.
- Status class to denote the status of a result object and of each node execution in the transport graph.
- Start and end times are now also stored for each node execution as well as for the whole dispatch.
- Logging of `stdout` and `stderr` can be done by passing in the `log_stdout`, `log_stderr` named metadata respectively while dispatching.
- In order to get the result of a certain dispatch, the `dispatch_id`, the `results_dir`, and the `wait` parameter can be passed in. If everything is default, then only the dispatch id is required, waiting will not be done, and the result directory will be in the current working directory with folder name as `results/` inside which every new dispatch will have a new folder named according to their respective dispatch ids, containing:
  - `result.pkl` - (Cloud)pickled result object.
  - `result_info.yaml` - yaml file with high level information about the result and its execution.
  - `dispatch_source.py` - python file generated, containing the original function definitions of lattice and electrons which can be used to dispatch again.

### Changed

- `logfile` named metadata is now `slurm_logfile`.
- Instead of using `jsonpickle`, `cloudpickle` is being used everywhere to maintain consistency.
- `to_json` function uses `json` instead of `jsonpickle` now in electron and lattice definitions.
- `post_processing` moved to the dispatcher, so the dispatcher will now store a finished execution result in the results folder as specified by the user with no requirement of post processing it from the client/user side.
- `run_task` function in dispatcher modified to check if a node has completed execution and return it if it has, else continue its execution. This also takes care of cases if the server has been closed mid execution, then it can be started again from the last saved state, and the user won't have to wait for the whole execution.
- Instead of passing in the transport graph and dispatch id everywhere, the result object is being passed around, except for the `asyncio` part where the dispatch id and results directory is being passed which afterwards lets the core dispatcher know where to get the result object from and operate on it.
- Getting result of parent node executions of the graph, is now being done using the result object's graph. Storing of each execution's result is also done there.
- Tests updated to reflect the changes made. They are also being run in a serverless manner.

### Removed

- `LatticeResult` class removed.
- `jsonpickle` requirement removed.
- `WorkflowExecutionResult`, `TaskExecutionResult`, and `ExecutionError` singleton classes removed.

### Fixed

- Commented out the `jwt_required()` part in `covalent-dispatcher/_service/app.py`, may be removed in later iterations.
- Dispatcher server will now return the error message in the response of getting result if it fails instead of sending every result ever as a response.

## [0.4.3] - 2021-11-23

### Added

- Added a note in Known Issues regarding port conflict warning.

## [0.4.2] - 2021-11-24

### Added

- Added badges to README.md

## [0.4.1] - 2021-11-23

### Changed

- Removed old coverage badge and fixed the badge URL

## [0.4.0] - 2021-11-23

### Added

- Codecov integrations and badge

### Fixed

- Detached pipelines no longer created

## [0.3.0] - 2021-11-23

### Added

- Wrote a Code of Conduct based on <https://www.contributor-covenant.org/>
- Added installation and environment setup details in CONTRIBUTING
- Added Known Issues section to README

## [0.2.0] - 2021-11-22

### Changed

- Removed non-open-source executors from Covalent. The local SLURM executor is now
- a separate repo. Executors are now plugins.

## [0.1.0] - 2021-11-19

### Added

- Pythonic CLI tool. Install the package and run `covalent --help` for a usage description.
- Login and logout functionality.
- Executor registration/deregistration skeleton code.
- Dispatcher service start, stop, status, and restart.

### Changed

- JWT token is stored to file instead of in an environment variable.
- The Dask client attempts to connect to an existing server.

### Removed

- Removed the Bash CLI tool.

### Fixed

- Version assignment in the covalent init file.

## [0.0.3] - 2021-11-17

### Fixed

- Fixed the Dockerfile so that it runs the dispatcher server from the covalent repo.

## [0.0.2] - 2021-11-15

### Changed

- Single line change in ci script so that it doesn't exit after validating the version.
- Using `rules` in `pytest` so that the behavior in test stage is consistent.

## [0.0.1] - 2021-11-15

### Added

- CHANGELOG.md to track changes (this file).
- Semantic versioning in VERSION.
- CI pipeline job to enforce versioning.
