{
    "steps": [
        {
            "key": "library",
            "label": ":bazel: Build and test //library/...",
            "commands": [
                "bazel test //library/...",
                "bazel build //library/... --build_event_json_file=bazel-events.json",
                "echo '{\"steps\": [{\"key\": \"app\", \"label\": \":bazel: Build and test //app/...\", \"commands\": [\"bazel test //app/...\", \"bazel build //app/... --build_event_json_file=bazel-events.json\"], \"plugins\": [{\"bazel-annotate#v0.1.1\": {\"bep_file\": \"bazel-events.json\", \"skip_if_no_bep\": true}}], \"depends_on\": \"library\"}]}' | buildkite-agent pipeline upload"
            ],
            "plugins": [
                {
                    "bazel-annotate#v0.1.1": {
                        "bep_file": "bazel-events.json",
                        "skip_if_no_bep": true
                    }
                }
            ]
        }
    ]
}
