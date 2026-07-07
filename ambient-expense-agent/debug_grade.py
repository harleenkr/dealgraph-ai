import sys
import traceback
from click.testing import CliRunner
from google.agents.cli.eval.cmd_grade import grade

try:
    runner = CliRunner()
    result = runner.invoke(grade, ['--traces', 'artifacts/traces/generated_traces.json', '--config', 'tests/eval/eval_config.yaml', '--project', 'my-project'])
    print(result.output)
    if result.exception:
        traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
except Exception as e:
    traceback.print_exc()
