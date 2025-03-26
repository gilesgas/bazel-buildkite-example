import subprocess
from collections import defaultdict
import json
import os

def run(command):
    return subprocess.run(
        command, capture_output=True, text=True, check=True
    ).stdout.strip()

print(run(["ls", "-al"]))

def make_step(emoji, label, commands=[], plugins=[]):
    step = {"label": f":{emoji}: {label}", "commands": commands}

    if len(plugins) > 0:
        step[plugins] = {"plugins": plugins}

    return step

def group_targets(targets, exclude=None):
    groups = set()
    
    for target in targets:
        directory, _, _ = target.rpartition(":")
        groups.add(directory.lstrip("/"))
    
    if exclude:
        groups.discard(exclude)
    
    return list(groups)

# By default, do nothing.
steps = []

# Get a list of all of the paths that changed in the latest commit.
changed_paths = run(["git", "diff-tree", "--name-only", "HEAD~1..HEAD"]).splitlines()
changed_dirs = list(filter(lambda p: os.path.isdir(f"{p}"), changed_paths))
bazel_paths = run(["bazel", "query", "'/...'"]).splitlines()
buildable_dirs = [item for item in changed_dirs if item in bazel_paths]

# For every changed path, build and test all targets.
for path in buildable_dirs:
    step = make_step("bazel", f"Build and test //{path}", [
        f"bazel build //{path}/...",
        f"bazel test //{path}/..."
    ])

    # Query the path for any libraries.
    libraries = run(["bazel", "query", f"kind(py_library, '//{path}/...')"]).splitlines()

    # For each one, determine whether it has any downstream dependencies. If it
    # does, and they aren't already in the list of paths to be build, add a step
    # to build and test them as well.
    for library in libraries:
        rdeps = run(["bazel", "query", f"rdeps(//..., //{path}/...)"]).splitlines()
        affected_paths = group_targets(rdeps, path)
        to_build = [item for item in affected_paths if item not in changed_paths]

        for dep in to_build:
            next_step = make_step("", f"Build and test //{dep}", [
                f"bazel build //{path}/...",
                f"bazel test //{path}/..."
            ])
            step["commands"].append(f"""echo '{json.dumps({"steps": next_step})}' | buildkite-agent pipeline upload""")

    steps.append(step)

print(json.dumps({"steps": steps}, indent=4))
