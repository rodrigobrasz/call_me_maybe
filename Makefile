VENV = call_me_maybe_venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


GREEN = \033[0;32m

install:
	@curl -LsSf https://astral.sh/uv/install.sh | sh
