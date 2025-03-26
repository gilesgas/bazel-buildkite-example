import subprocess
import json

def run_command(command):
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip().split()

def get_step(emoji, label, command, plugins=[]):
    step = {"label": f":{emoji}: {label}", "command": command}

    if len(plugins) > 0:
        step[plugins] = {"plugins": plugins}

    return step

# Step definitions for each Bazel-buildable thing.
test_package = get_step("bazel", "Test the package", "bazel test //package:all")
build_package = get_step("bazel", "Build the package", ["bazel build //package:all"])
test_app = get_step("bazel", "Test the app", "bazel test //app:all")
build_app = get_step("bazel", "Build the package", "bazel build //app:all")

# Get a list of all of the paths that changed in the latest commit.
changed_paths = run_command(["git", "diff-tree", "--name-only", "HEAD~1..HEAD"])

# By default, do nothing.
steps = []

if "package" in changed_paths:

    # Use Bazel to determine what should be built and tested.
    rdeps = run_command(["bazel", "query", "rdeps(//..., //package:hello) except kind(test, //...)"])
    for dep in rdeps:
        steps.append(get_step("bazel", f"Test {dep}", f"bazel test {dep}"))
        steps.append(get_step("bazel", f"Build {dep}", f"bazel build {dep}"))

print(json.dumps({"steps": steps}, indent=4))
