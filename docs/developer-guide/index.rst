Developer Guide
===============

This guide covers how to extend and contribute to SlicerMouseMaster.

Overview
--------

SlicerMouseMaster is built with:

- **Python 3.9+**: Core logic and Slicer integration
- **Qt/PySide**: User interface
- **JSON**: Configuration and preset storage
- **pytest**: Unit testing

Key Concepts
------------

**Event Interception**
  MouseMaster installs a Qt application-level event filter to intercept mouse
  button presses before they reach Slicer's default handlers.

**Action Registry**
  Actions are registered in a central registry, allowing dynamic discovery and
  execution of Slicer operations.

**Platform Adaptation**
  Button codes differ between operating systems. Platform adapters normalize
  these differences.

**Preset System**
  User configurations are stored as JSON presets with support for versioning
  and migration.

Getting Started
---------------

1. :doc:`architecture` - Understand the codebase structure
2. :doc:`adding-actions` - Add new actions to the registry
3. :doc:`adding-mice` - Create profiles for new mice
4. :doc:`testing` - Run and write tests
5. :doc:`contributing` - Submit your changes

Development Setup
-----------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/benzwick/SlicerMouseMaster.git
   cd SlicerMouseMaster

   # Set up development environment
   uv sync

   # Install pre-commit hooks
   uv run pre-commit install

   # Run tests
   make test

   # Run linting and formatting
   make lint
   make format

   # Type checking
   make typecheck

   # Build documentation
   make docs

Project Structure
-----------------

::

   SlicerMouseMaster/
   ├── CMakeLists.txt              # Slicer extension configuration
   ├── MouseMaster/                # Main module
   │   ├── MouseMaster.py          # Slicer module entry point
   │   ├── MouseMasterLib/         # Core library
   │   │   ├── EventHandler.py     # Qt event filter
   │   │   ├── MouseProfile.py     # Mouse definitions
   │   │   ├── PresetManager.py    # Preset loading/saving
   │   │   ├── ActionRegistry.py   # Action management
   │   │   ├── PlatformAdapter.py  # Cross-platform support
   │   │   └── ButtonDetector.py   # Button detection wizard
   │   ├── Resources/              # Static resources
   │   │   └── MouseDefinitions/   # Mouse profile JSON files
   │   └── Testing/                # Test suites
   │       └── Python/             # pytest unit tests
   ├── presets/                    # Preset definitions
   │   ├── builtin/                # Shipped presets
   │   └── community/              # User-contributed presets
   ├── docs/                       # This documentation
   └── Screenshots/                # UI screenshots
