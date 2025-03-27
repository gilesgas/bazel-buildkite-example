from utils import run, filter_dirs, to_paths, make_pipeline_step, to_json

# By default, do nothing.
steps = []

# Get a list of directories changed in the most recent commit.
changed_paths = run(["git", "diff-tree", "--name-only", "HEAD~1..HEAD"])
changed_dirs = filter_dirs(changed_paths)

# Query the Bazel workspace for a list of all packages (libraries, binaries, etc.).
all_packages = run(["bazel", "query", "'/...'"])

# Using both lists, figure out which packages need to be built, so we can assemble
# a pipeline that builds only those.
changed_packages = [p for p in changed_dirs if p in to_paths(all_packages)]

# For each of those packages, build and test all of its targets.
for pkg in changed_packages:
    package_step = make_pipeline_step(pkg)

    # Query the package for any Python libraries.
    libraries = run(["bazel", "query", f"kind(py_library, '//{pkg}/...')"])

    # If the package contain one or more Python libraries, query the Bazel graph
    # to assemble a list of each library's reverse dependencies (i.e., the Bazel
    # packages that depend on it), adding a step to the Buildkite pipeline
    # dynamically to build and test each one -- for example, to guard against
    # accidental regressions.
    for lib in libraries:
        reverse_deps = run(["bazel", "query", f"rdeps(//..., //{pkg}/...)"])

        # Skip (re-)building any reverse_deps that also belong to the
        # changed_packages set. (There's no need to build them a second time.)
        rdeps_to_build = [
            p for p in to_paths(reverse_deps, pkg) if p not in changed_packages
        ]

        for dep in rdeps_to_build:
            rdep_step = make_pipeline_step(dep, pkg)
            package_step["commands"].append(
                f"""echo '{to_json({"steps": [rdep_step]})}' | buildkite-agent pipeline upload"""
            )

    steps.append(package_step)

print(to_json({"steps": steps}, 4))
