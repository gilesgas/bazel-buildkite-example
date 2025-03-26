from utils import run, group, is_dir, get_step, to_json


# By default, do nothing.
steps = []

# Get a list of all of the paths that changed in the latest commit.
changed_paths = run(["git", "diff-tree", "--name-only", "HEAD~1..HEAD"]).splitlines()
changed_dirs = list(filter(lambda p: is_dir(f"{p}"), changed_paths))
packages = run(["bazel", "query", "'/...'"]).splitlines()
package_paths = [p for p in changed_dirs if p in group(packages)]

# For every changed path, build and test all targets.
for path in package_paths:
    step = get_step(path, "bazel", f"Build and test //{path}/...", [
        f"bazel build //{path}/...",
        f"bazel test //{path}/..."
    ])

    # Query the path for any libraries.
    libs = run(["bazel", "query", f"kind(py_library, '//{path}/...')"]).splitlines()

    # For each one, determine whether it has any downstream dependencies. If it
    # does, and they aren't already in the list of paths to be build, add a step
    # to build and test them as well.
    for lib in libs:
        rdeps = run(["bazel", "query", f"rdeps(//..., //{path}/...)"]).splitlines()
        affected_paths = group(rdeps, path)
        to_build = [p for p in affected_paths if p not in changed_paths]

        for dep in to_build:
            next_step = get_step(dep, "bazel", f"Build and test downstream //{dep}/...", [
                f"bazel build //{dep}/...",
                f"bazel test //{dep}/..."
            ])
            next_step["depends_on"] = path
            step["commands"].append(f"""echo '{to_json({"steps": [next_step]})}' | buildkite-agent pipeline upload""")

    steps.append(step)

print(to_json({"steps": steps}, 4))
