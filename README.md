# bazel-buildkite-example

An example that builds a simple Python monorepo with Bazel and Buildkite! :kite:

[![Build status](https://badge.buildkite.com/57e0fc02c633be7eae646cb9b212cbf24043ba1618f89b6384.svg)](https://buildkite.com/nunciato/bazel-buildkite-example)

This simple hello-world example uses Bazel to build and test and a Python library (a `py_library` package, in Bazel parlance) and a Python script (or `py_binary`, as they say). The binary depends on the library, and the library gets built and packaged (by Bazel) as a Python wheel.

The repo is also configured with a Buildkite [pipeline](https://buildkite.com/nunciato/bazel-buildkite-example) that uses [`bazel query`](https://bazel.build/query/quickstart) and Buildkite [dynamic pipelines](https://buildkite.com/docs/pipelines/configure/dynamic-pipelines) to compute a pipeline definition at runtime based on the content of each commit. Bazel-built Python packages are also uploaded as Buildkite [build artifacts](https://buildkite.com/docs/pipelines/configure/artifacts). 

[![The Buildkite pipeline that builds this repository](https://github.com/user-attachments/assets/896f7bf7-9387-4f72-a27f-0f25e78f16a5)](https://buildkite.com/nunciato/bazel-buildkite-example)

```bash
$ bazel build //...

INFO: Analyzed 6 targets (0 packages loaded, 0 targets configured).
INFO: Found 6 targets...
INFO: Elapsed time: 0.127s, Critical Path: 0.00s
INFO: 1 process: 1 internal.
INFO: Build completed successfully, 1 total action
```

```bash
$ bazel test //...

INFO: Analyzed 6 targets (0 packages loaded, 0 targets configured).
INFO: Found 4 targets and 2 test targets...
INFO: Elapsed time: 0.095s, Critical Path: 0.00s
INFO: 1 process: 1 internal.
INFO: Build completed successfully, 1 total action
PASSED: //app:test_main
INFO: From Testing //app:test_main
==================== Test output for //app:test_main:
Hey! there's a message from the Python library: 'Hello, world!'
================================================================================
PASSED: //library:test_hello
INFO: From Testing //library:test_hello
==================== Test output for //library:test_hello:
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
================================================================================
//app:test_main                                                 (cached) PASSED in 0.1s
//library:test_hello                                            (cached) PASSED in 0.3s

Executed 0 out of 2 tests: 2 tests pass.
```

```bash
$ bazel run //app:main --ui_event_filters=-INFO --noshow_progress --show_result=0

The Python package says, 'Hi!'
```
