# Developer Experience

## Linting

Here is my experience trying to install clean linting with VS Code, FastAPI.

### Preliminary notes

- Ruff is a no brainer as it's lighting fast and all-in-one tool.
- We can't remove Pylance extension at all since it's responsible for autocomplete, auto-imports.
- We could install mypy as Python package and use it in CLI only to double-check the codebase with a second type checker, without using the extension in the IDE.

### ✅ Ruff Extension + Pylance Extension 
- Works well (very fast, simple config)
- But there is an overlap as Pylance checks same rules than Ruff. If we deactivate linting with Pylance, we'll lose typing.
- Pylance can't be configured in `pyproject.toml` but needs `settings.json` from VS Code.

### ❌ Ruff Extension + Mypy Extension + Pylance Extension (with type checking off) 
- In this case, there is no overlapping as Mypy only warns on typing, and Ruff only on other linting rules.
- But Mypy is very slow, and only run at saving
