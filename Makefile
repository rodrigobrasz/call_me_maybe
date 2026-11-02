VENV = call_me_maybe_venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


GREEN = \033[0;32m


install:
	@python3 -m venv $(VENV)
	@echo "$(GREEN)\nVirtual Enviroment Successfully Installed"
	@echo "Use: 'source $(VENV)/bin/activate'\n$(RESET)"
