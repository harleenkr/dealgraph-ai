.PHONY: install playground test

install:
	uv sync

playground:
	agents-cli playground

test:
	agents-cli run "{\"amount\": 150.0, \"submitter\": \"alice@company.com\", \"category\": \"software\", \"description\": \"IDE License\", \"date\": \"2026-06-06\"}" --start-server

serve:
	uv run uvicorn expense_agent.server:api --host 0.0.0.0 --port 8080

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	agents-cli eval grade --traces artifacts/traces/generated_traces.json --config tests/eval/eval_config.yaml --project my-project
