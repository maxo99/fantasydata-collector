
# Run Standard
main: 
	uv run main.py

main-record:
	uv run main.py --record

main-replay:
	uv run main.py --replay

view_traces:
	playwright show-traces trace.zip