# Contributing to SlicerMouseMaster

Thank you for your interest in contributing to SlicerMouseMaster!

## Quick Links

- [Full Contributing Guide](https://benzwick.github.io/SlicerMouseMaster/developer-guide/contributing.html)
- [Developer Guide](https://benzwick.github.io/SlicerMouseMaster/developer-guide/)
- [Issue Tracker](https://github.com/benzwick/SlicerMouseMaster/issues)

## Ways to Contribute

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new functionality
- **Code**: Submit pull requests
- **Documentation**: Improve guides and examples
- **Presets**: Share your button configurations
- **Mouse Profiles**: Add support for new mice

## Getting Started

```bash
# Clone the repository
git clone https://github.com/benzwick/SlicerMouseMaster.git
cd SlicerMouseMaster

# Set up development environment
uv sync
uv run pre-commit install

# Run tests
make test

# Run linting and formatting
make lint
make format
```

## Code Style

We use automated tools:
- **Ruff**: Linting and formatting
- **Mypy**: Type checking

Run `make check` to run all style checks, or use pre-commit hooks which run automatically.

## Commit Messages

Use conventional commit format:

```
<type>: <short summary>

Types: feat, fix, docs, refactor, test, chore
```

## Pull Requests

1. Keep PRs focused (one feature or fix per PR)
2. Update documentation for your changes
3. Add tests for new functionality
4. Ensure all tests pass

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE.txt).
