# Testing

### Using dedicated environment for testing

After trying dependency injection or fixtures to override settings on the fly, I decided the most straightforward way to do it would be to change OS env vars directly when running pytest.

There are two ways to do this:

1. `DEBUG=False pytest` -> this works well in CLI, and respects 12 factors. But VS Code tests does not work
2. Adding `pytest-env` and adding env vars to `pyproject.toml` for overriding -> does not respect 12 factors but works everywhere (CLI, vs code built-in tests, etc.)

**Fixtures**

Pytest fixtures are a way to set up and manage the state or resources needed for your tests in a clean and reusable way. They allow you to define reusable code that can be used across multiple test functions. Here are the key points:

1. **Setup and Teardown**: Fixtures can set up resources (like database connections, temporary files, or mock objects) before a test runs and clean them up afterward.

2. **Reusability**: You can define a fixture once and use it in multiple tests, making your tests more modular and reducing code duplication.
   
3. **Dependency Injection**: Fixtures use dependency injection, meaning they are passed as arguments to your test functions. Pytest automatically identifies and provides the fixtures.

Using a conftest.py file for your pytest fixtures offers several key benefits:

1. **Automatic Discovery** by Pytest, no imports needed.
2. **Centralized Fixture Management** and reduced duplication
