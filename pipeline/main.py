import json

def get_step(emoji, label, command, plugins=[]):
    step = {"label": f":{emoji}: {label}", "command": command}

    if len(plugins) > 0:
        step[plugins] = {"plugins": plugins}

    return step


test_package = get_step("bazel", "Test the package", "bazel test //package:all")
build_package = get_step("bazel", "Build the package", ["bazel build //package:all"])
test_app = get_step("bazel", "Test the app", "bazel test //app:all")
build_app = get_step("bazel", "Build the package", "bazel build //app:all")

steps = []
steps.extend(
    [
        test_package,
        build_package,
        test_app,
        build_app,
    ]
)

print(json.dumps({"steps": steps}, indent=4))
