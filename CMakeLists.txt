cmake_minimum_required(VERSION 3.20.6...3.22.6 FATAL_ERROR)

project(SlicerMouseMaster)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://benzwick.github.io/SlicerMouseMaster")
set(EXTENSION_CONTRIBUTORS "Ben Zwick")
set(EXTENSION_DESCRIPTION "Advanced mouse button customization for multi-button mice with preset management and context-sensitive bindings.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/benzwick/SlicerMouseMaster/main/SlicerMouseMaster.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/benzwick/SlicerMouseMaster/main/Screenshots/main-ui.png https://raw.githubusercontent.com/benzwick/SlicerMouseMaster/main/Screenshots/button-mapping.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(MouseMaster)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
