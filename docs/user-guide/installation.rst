Installation
============

System Requirements
-------------------

- **3D Slicer**: Version 5.0 or later (5.4+ recommended)
- **Python**: 3.9+ (included with Slicer)
- **Operating System**: Windows, macOS, or Linux
- **Mouse**: Any mouse works; multi-button mice get the most benefit

From Extension Manager (Recommended)
------------------------------------

1. Open 3D Slicer
2. Go to **View > Extension Manager**
3. Search for "MouseMaster"
4. Click **Install**
5. Restart Slicer when prompted

The extension will be available in **Modules > Utilities > MouseMaster**.

From Source (Development)
-------------------------

For developers or if you want the latest unreleased features:

.. code-block:: bash

   git clone https://github.com/benzwick/SlicerMouseMaster.git

Then add the module to Slicer:

1. Open 3D Slicer
2. Go to **Edit > Application Settings > Modules**
3. Add the path to ``SlicerMouseMaster/MouseMaster`` to **Additional module paths**
4. Restart Slicer

Verifying Installation
----------------------

After installation:

1. Open the module selector dropdown
2. Navigate to **Utilities > MouseMaster**
3. The MouseMaster panel should appear

If you see an error, check the :doc:`troubleshooting` guide.

Updating
--------

**From Extension Manager:**

1. Open **View > Extension Manager**
2. Go to the **Installed** tab
3. Click **Update** next to MouseMaster if available
4. Restart Slicer

**From Source:**

.. code-block:: bash

   cd SlicerMouseMaster
   git pull origin main

Then reload the module in Slicer.
