SHELL := /bin/bash
UV := $(HOME)/.local/bin/uv
SGOINFRE := $(shell [ -d /sgoinfre/$(USER) ] && echo /sgoinfre/$(USER) || echo $(HOME))

UV_ENV := UV_CACHE_DIR=$(SGOINFRE)/.cache/uv \
          UV_PROJECT_ENVIRONMENT=$(SGOINFRE)/.venv_cmm \
          HF_HOME=$(SGOINFRE)/.cache/huggingface

BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;33m
RESET := \033[0m

.PHONY: install run debug clean fclean lint help re

prepare-cache:
	@mkdir -p "$(SGOINFRE)/.cache/uv"
	@mkdir -p "$(SGOINFRE)/.venv_cmm"
	@mkdir -p "$(SGOINFRE)/.cache/huggingface"

install: prepare-cache
	@printf "$(BLUE)▶ Installing dependencies...$(RESET)\n"
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@$(UV_ENV) $(UV) sync
	@printf "$(GREEN)✔ Installation complete$(RESET)\n"

run: prepare-cache
	@printf "$(BLUE)▶ Running project...$(RESET)\n"
	@$(UV_ENV) $(UV) run python -m src

debug: prepare-cache
	@printf "$(YELLOW)▶ Starting debugger...$(RESET)\n"
	@$(UV_ENV) $(UV) run python -m pdb -m src

clean:
	@printf "$(YELLOW)▶ Cleaning caches...$(RESET)\n"
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	@printf "$(GREEN)✔ Cache cleanup done$(RESET)\n"

fclean: clean
	@printf "$(YELLOW)▶ Removing virtual environment and outputs...$(RESET)\n"
	@rm -rf .venv
	@rm -rf "$(SGOINFRE)/.venv_cmm"
	@rm -rf data/output
	@printf "$(GREEN)✔ Full cleanup done$(RESET)\n"

lint: prepare-cache
	@printf "$(BLUE)▶ Running lint checks...$(RESET)\n"
	@$(UV_ENV) $(UV) run flake8 .
	@$(UV_ENV) $(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@printf "$(GREEN)✔ Lint passed$(RESET)\n"

re: fclean install

help:
	@printf "$(BLUE)Available targets:$(RESET)\n"
	@printf "  make install      - install dependencies\n"
	@printf "  make run          - run the project\n"
	@printf "  make debug        - run in debugger\n"
	@printf "  make clean        - remove caches\n"
	@printf "  make fclean       - remove caches, .venv and output\n"
	@printf "  make lint         - run flake8 and mypy\n"
	@printf "  make re           - clean and reinstall\n"
	@printf "  make help         - show this help\n"