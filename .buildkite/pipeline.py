from utils import run, filter_dirs, get_paths, get_package_step, to_json

# By default, do nothing.
steps = []

# Get a list of directories changed in the most recent commit.
changed_paths = run(["git", "diff-tree", "--name-only", "HEAD~1..HEAD"])
changed_dirs = filter_dirs(changed_paths)

# Query the Bazel workspace for a list of all packages (libraries, binaries, etc.).
all_packages = run(["bazel", "query", "'/...'"])

# Using both lists, figure out which packages need to be built. The goal is to
# assemble a pipeline that builds only those.
changed_packages = [p for p in changed_dirs if p in get_paths(all_packages)]

# For each changed Bazel package, assemble a pipeline step programmatically to
# build and test all of its targets.
#
# Additionally, if the package defines one or more Python libraries, query the
# Bazel graph to assemble a list of each library's reverse dependencies (i.e.,
# the Bazel packages that depend on it), adding a step to the Buildkite pipeline
# at runtime to build and test each of those as well -- for example, to guard
# against downstream regressions.
for pkg in changed_packages:

    # Make a step that runs `bazel build` and `bazel test` for this package.
    package_step = get_package_step(pkg)

    # Use Bazel to query the package for any Python libraries.
    libraries = run(["bazel", "query", f"kind(py_library, '//{pkg}/...')"])

    for lib in libraries:

        # Find the library's reverse dependencies.
        reverse_deps = run(["bazel", "query", f"rdeps(//..., //{pkg}/...)"])

        # Filter this list to exclude any package that already belongs to the
        # changed_packages set. (There's no need to build these a second time.)
        reverse_deps_to_build = [
            p for p in get_paths(reverse_deps, pkg) if p not in changed_packages
        ]

        for dep in reverse_deps_to_build:
            rdep_step = get_package_step(dep)

            # Append a step at runtime to the changed_package's list to build
            # and test the reverse dependency also.
            package_step["commands"].extend([
                f"echo 'Adding a step to the pipeline for {dep}...'",
                f"python3 .buildkite/step.py {dep} | buildkite-agent pipeline upload"
            ])

    # Add this package step to the pipeline.
    steps.append(package_step)

# Emit the pipeline as JSON to be uploaded to Buildkite.
print(to_json({"steps": steps}, 4))
