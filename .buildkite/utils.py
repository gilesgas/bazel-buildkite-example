import json, os, subprocess

# Runs an OS command, returning stdout as a list of lines.
def run(command):
    return (
        subprocess.run(command, capture_output=True, text=True, check=True)
        .stdout.strip()
        .splitlines()
    )

# Converts a list of file paths into a list of directories, omitting those that aren't.
def filter_dirs(paths):
    return list(filter(lambda p: os.path.isdir(p), paths))

# Converts a list of Bazel targets into a unique list of top-level paths. For example,
# turns this:
#   //app:main
#   //app:test_main
#   //library:hello
#   //library:test_hello
#
# into this:
#   app
#   library
def to_paths(targets, exclude=None):
    groups = set()

    for target in targets:
        directory, _, _ = target.rpartition(":")
        groups.add(directory.lstrip("/"))

    if exclude:
        groups.discard(exclude)

    return list(groups)


# Returns a Buildkite `command` step (as a Python dictionary to be serialized as
# JSON later) given an emoji, label, list of commands, and optional list of
# plugins. See the Buildkite docs for more options.
# https://buildkite.com/docs/pipelines/configure/defining-steps
def command_step(emoji, label, commands=[], plugins=[]):
    step = {"label": f":{emoji}: {label}", "commands": commands}

    if len(plugins) > 0:
        step["plugins"] = plugins

    return step


# Returns a Buildkite `command` step that builds, tests, and annotates (using
# our Bazel-annotation plugin) a given Bazel package.
def make_pipeline_step(package):
    return command_step(
        "bazel",
        f"Build and test //{package}/...",
        [
            f"bazel test //{package}/...",
            f"bazel build //{package}/... --build_event_json_file=bazel-events.json",
        ],
        [
            {
                # https://github.com/buildkite-plugins/bazel-annotate-buildkite-plugin
                "bazel-annotate#v0.1.0": {
                    "bep_file": f"bazel-events.json",
                },
            },
        ],
    )


# Converts a Python dictionary into a JSON string, with optional pretty-printing.
def to_json(data, indent=None):
    return json.dumps(data, indent=indent)
