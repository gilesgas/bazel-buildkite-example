import json

steps = []


def get_step(emoji, label, command, plugins=[]):
    step = {"label": f":{emoji}: {label}", "command": command}

    if len(plugins) > 0:
        step[plugins] = {"plugins": plugins}

    return step


build_package = get_step("bazel", "Build the package", ["bazel build //package:all"])
test_package = get_step("bazel", "Test the package", "bazel test //package:all")
build_app = get_step("bazel", "Build the package", "bazel build //app:all")
test_app = get_step("bazel", "Test the app", "bazel test //app:all")

steps.extend(
    [
        test_package,
        build_package,
        test_app,
        build_app,
    ]
)

print(json.dumps({"steps": steps}, indent=4))
