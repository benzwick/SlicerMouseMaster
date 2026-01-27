Contributing
============

We welcome contributions to SlicerMouseMaster! This guide explains how to
contribute effectively.

Ways to Contribute
------------------

- **Bug reports**: File issues for problems you encounter
- **Feature requests**: Suggest new functionality
- **Code contributions**: Submit pull requests
- **Documentation**: Improve guides and examples
- **Presets**: Share your button configurations
- **Mouse profiles**: Add support for new mice

Development Setup
-----------------

1. Fork the repository on GitHub
2. Clone your fork:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/SlicerMouseMaster.git
      cd SlicerMouseMaster

3. Set up development environment:

   .. code-block:: bash

      uv sync
      uv run pre-commit install

4. Create a feature branch:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

Code Style
----------

We use automated tools to maintain consistent code style:

- **Ruff**: Linting and formatting
- **Mypy**: Type checking

Run checks before committing:

.. code-block:: bash

   make lint       # Run linter
   make format     # Format code
   make typecheck  # Run type checker
   make check      # Run lint and typecheck together

Pre-commit hooks run these automatically.

Commit Messages
---------------

Follow conventional commit format:

::

   <type>: <short summary>

   [optional body with details]

   [optional footer with references]

Types:

- ``feat``: New feature
- ``fix``: Bug fix
- ``docs``: Documentation only
- ``refactor``: Code change that neither fixes a bug nor adds a feature
- ``test``: Adding or updating tests
- ``chore``: Maintenance tasks

Examples:

::

   feat: add MX Master 4 support

   - Add mouse definition JSON
   - Create default preset
   - Update supported mice documentation

   Closes #42

::

   fix: handle missing preset file gracefully

   Previously the module would crash if a preset file was deleted
   while MouseMaster was running. Now it shows an error message
   and falls back to the default preset.

Pull Requests
-------------

1. **Keep PRs focused**: One feature or fix per PR

2. **Update documentation**: Add or update docs for your changes

3. **Add tests**: Include unit tests for new functionality

4. **Run the test suite**: Ensure all tests pass

5. **Write a clear description**: Explain what and why

PR Template:

::

   ## Summary

   Brief description of changes.

   ## Changes

   - Change 1
   - Change 2

   ## Testing

   - [ ] Unit tests pass
   - [ ] Manual testing completed
   - [ ] Documentation updated

   ## Related Issues

   Closes #123

Reporting Bugs
--------------

Good bug reports include:

1. **Slicer version**: Help > About 3D Slicer
2. **Operating system**: Windows/macOS/Linux and version
3. **Mouse model**: The mouse you're using
4. **Steps to reproduce**: Detailed steps to trigger the bug
5. **Expected behavior**: What should happen
6. **Actual behavior**: What actually happens
7. **Error messages**: From Python console (View > Python Console)
8. **Screenshots**: If applicable

Feature Requests
----------------

When requesting features:

1. **Check existing issues**: Someone may have already requested it
2. **Describe the use case**: Why do you need this?
3. **Suggest implementation**: If you have ideas
4. **Be open to discussion**: The best solution may differ from your initial idea

Contributing Presets
--------------------

Share your button configurations:

1. Export your preset from MouseMaster
2. Add author and description to the JSON
3. Submit via:

   - GitHub issue with the file attached
   - Pull request to ``presets/community/``

See :doc:`/reference/presets` for preset format details.

Contributing Mouse Profiles
---------------------------

Add support for new mice:

1. Create mouse definition JSON
2. Create default preset
3. Test on your hardware
4. Submit pull request

See :doc:`adding-mice` for detailed instructions.

Code of Conduct
---------------

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the `Slicer Community Guidelines <https://discourse.slicer.org/faq>`_

Getting Help
------------

- **Questions**: Open a GitHub Discussion
- **Chat**: Join the Slicer Discord
- **Forum**: Post on `Slicer Discourse <https://discourse.slicer.org/>`_

License
-------

By contributing, you agree that your contributions will be licensed under the
`Apache License 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.
