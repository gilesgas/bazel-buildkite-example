from utils import run, to_paths, command_step, to_json, dirs

def build_and_test(package, depends_on=None):
    return command_step(package, "bazel", f"Build and test //{package}/...", [
        f"bazel build //{package}/... --build_event_json_file=bazel-events-{package}.json",
        f"bazel test //{package}/...",
    ], [{
        "mcncl/bazel-annotate#v0.1.0": {
            "bep_file": f"bazel-events-{package}.json",
            "skip_if_no_bep": True,
        }
    }], depends_on)

# By default, do nothing.
steps = []

# Get a list of directories changed in the most recent commit.
changed_paths = run(["git", "diff-tree", "--name-only", "HEAD~1..HEAD"])
changed_dirs = dirs(changed_paths)

# Query the Bazel workspace for a list of all packages (libraries, binaries, etc.).
all_packages = run(["bazel", "query", "'/...'"])

# Using both lists, assemble a list of affected Bazel packages.
changed_packages = [p for p in changed_dirs if p in to_paths(all_packages)]

# For each changed package, build and test all of its targets.
for pkg in changed_packages:
    package_step = build_and_test(pkg)

    # Query the package for any Python libraries.
    libraries = run(["bazel", "query", f"kind(py_library, '//{pkg}/...')"])

    # If the package does contain libraries, query the Bazel graph to assemble a
    # list of each library's reverse dependencies (i.e., the packages that
    # depend on it), adding a step to the Buildkite pipeline dynamically to
    # build and test each one. (Skipping the ones that have already been queued).
    for lib in libraries:
        reverse_deps = run(["bazel", "query", f"rdeps(//..., //{pkg}/...)"])
        rdeps_to_build = [p for p in to_paths(reverse_deps, pkg) if p not in changed_packages]

        for dep in rdeps_to_build:
            rdep_step = build_and_test(dep, pkg)
            rdep_step["depends_on"] = pkg
            package_step["commands"].append(f"""echo '{to_json({"steps": [rdep_step]})}' | buildkite-agent pipeline upload""")

    steps.append(package_step)

print(to_json({"steps": steps}, 4))
