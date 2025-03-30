import sys
from utils import make_pipeline_step, to_json

pkg = sys.argv[1:]
step = make_pipeline_step(pkg)
print(to_json({"steps": [step]}, 4))
