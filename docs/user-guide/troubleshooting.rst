Troubleshooting
===============

Common issues and their solutions.

Button Presses Not Detected
---------------------------

**Symptoms:** Pressing mouse buttons does nothing.

**Solutions:**

1. **Verify MouseMaster is enabled**: Check that the status indicator shows
   "Active" (green)

2. **Check preset selection**: Ensure a preset is loaded with button mappings

3. **Verify mouse selection**: Confirm your mouse model matches the dropdown

4. **Check for conflicts**: Disable vendor software (Logitech Options+, etc.)
   that may intercept button events

5. **Try button detection**: Use "Detect New Mouse..." to verify button codes

6. **Check permissions** (Linux): Add yourself to the ``input`` group:

   .. code-block:: bash

      sudo usermod -a -G input $USER
      # Log out and back in

Mappings Not Working
--------------------

**Symptoms:** Button presses are detected but actions don't execute.

**Solutions:**

1. **Check action compatibility**: Some actions only work in specific modules

2. **Verify module context**: Context-sensitive bindings may override defaults

3. **Check Slicer console**: Look for error messages prefixed with
   ``[MouseMaster]``

4. **Test with simple action**: Try mapping to "Undo" which works universally

Presets Not Saving
------------------

**Symptoms:** Changes don't persist after restarting Slicer.

**Solutions:**

1. **Check write permissions**: Ensure you can write to Slicer settings:

   - Windows: ``%LOCALAPPDATA%/NA-MIC/``
   - macOS: ``~/Library/Application Support/NA-MIC/``
   - Linux: ``~/.config/NA-MIC/``

2. **Try explicit export**: Use "Export Preset..." to save to a specific file

3. **Check disk space**: Ensure sufficient free space

4. **Check for corruption**: Delete the user presets directory and restart

Context Bindings Not Working
----------------------------

**Symptoms:** Module-specific bindings don't activate.

**Solutions:**

1. **Verify context is enabled**: Check "Enable context-sensitive bindings"

2. **Check module name**: Context IDs must match exactly (case-sensitive)

3. **Test in target module**: Ensure you're in the correct module when testing

4. **Check for typos**: Inspect the preset JSON for context name errors

Platform-Specific Issues
------------------------

Windows
^^^^^^^

- **Run as Administrator** (temporarily): Some applications block button events
- **Disable gaming overlays**: Discord, Steam, etc. may intercept buttons
- **Check device drivers**: Update mouse drivers from manufacturer

macOS
^^^^^

- **Grant accessibility access**: System Preferences > Security & Privacy >
  Privacy > Accessibility > Add Slicer
- **Check Gatekeeper**: Allow Slicer in Security & Privacy if blocked

Linux
^^^^^

- **X11 vs Wayland**: MouseMaster works best with X11. On Wayland, try running
  Slicer with XWayland:

  .. code-block:: bash

     GDK_BACKEND=x11 ./Slicer

- **Check evdev permissions**: Ensure ``/dev/input/`` devices are readable

- **Verify Qt button codes**: Button codes may differ between desktop
  environments

Crashes
-------

**Symptoms:** Slicer crashes when using MouseMaster.

**Solutions:**

1. **Disable MouseMaster**: Restart Slicer without enabling the module

2. **Check Slicer logs**: Look in the Slicer application directory for crash
   logs

3. **Update Slicer**: Ensure you're using the latest stable release

4. **Reset settings**: Delete MouseMaster settings directory:

   .. code-block:: bash

      # Find and remove MouseMaster settings
      rm -rf ~/.config/NA-MIC/*/MouseMaster/  # Linux
      rm -rf ~/Library/Application\ Support/NA-MIC/*/MouseMaster/  # macOS

5. **Report the issue**: File a bug report with:

   - Slicer version
   - OS and version
   - Steps to reproduce
   - Error messages from console

Getting Help
------------

If you can't resolve your issue:

1. Check existing issues: `GitHub Issues <https://github.com/benzwick/SlicerMouseMaster/issues>`_

2. Search the Slicer forum: `Slicer Discourse <https://discourse.slicer.org/>`_

3. Open a new issue with:

   - Slicer version (Help > About)
   - Operating system and version
   - Mouse model
   - Steps to reproduce
   - Screenshots if applicable
   - Error messages from Python console (View > Python Console)

Debugging Tips
--------------

**Enable verbose logging:**

In Slicer Python console:

.. code-block:: python

   import logging
   logging.getLogger("MouseMaster").setLevel(logging.DEBUG)

**Check event filter status:**

.. code-block:: python

   # Verify event handler is installed
   from MouseMasterLib import EventHandler
   print(EventHandler.is_installed())

**Test action directly:**

.. code-block:: python

   # Execute an action without button press
   from MouseMasterLib import ActionRegistry
   registry = ActionRegistry.get_instance()
   registry.execute("edit_undo")
