# bazel-buildkite-example

An example that builds a Python monorepo with Bazel and Buildkite!

[![Build status](https://badge.buildkite.com/57e0fc02c633be7eae646cb9b212cbf24043ba1618f89b6384.svg)](https://buildkite.com/nunciato/bazel-buildkite-example)

This example uses Bazel to build and test a Python package and then use that package in another Python program configured with a third-party dependency. The repo is also configured with a Buildkite pipeline that uploads the Bazel-built Python package as a Buildkite [build artifact](https://buildkite.com/docs/pipelines/configure/artifacts). 

```bash
$ bazel build //...

INFO: Analyzed 6 targets (88 packages loaded, 3606 targets configured).
INFO: Found 6 targets...
INFO: Elapsed time: 7.068s, Critical Path: 2.06s
INFO: 25 processes: 23 internal, 2 darwin-sandbox.
INFO: Build completed successfully, 25 total actions
```

```bash
$ bazel test //...

INFO: Analyzed 6 targets (88 packages loaded, 3606 targets configured).
INFO: Found 6 targets...
INFO: Elapsed time: 7.068s, Critical Path: 2.06s
INFO: 25 processes: 23 internal, 2 darwin-sandbox.
INFO: Build completed successfully, 25 total actions

bazel-buildkite-example  main took 7s 
➜ bazel test //...
INFO: Analyzed 6 targets (0 packages loaded, 0 targets configured).
INFO: From Testing //package:test_hello:
==================== Test output for //package:test_hello:
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
================================================================================
INFO: From Testing //app:test_main:
==================== Test output for //app:test_main:
The Python package says, 'Hi!'
================================================================================
INFO: Found 4 targets and 2 test targets...
INFO: Elapsed time: 1.560s, Critical Path: 1.12s
INFO: 3 processes: 4 darwin-sandbox.
INFO: Build completed successfully, 3 total actions
//app:test_main                                                          PASSED in 0.4s
//package:test_hello                                                     PASSED in 0.4s

Executed 2 out of 2 tests: 2 tests pass.
```

```bash
$ bazel run //app:main --ui_event_filters=-INFO --noshow_progress --show_result=0

The Python package says, 'Hi!'
```
