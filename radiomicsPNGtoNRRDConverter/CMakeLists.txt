#-----------------------------------------------------------------------------
set(MODULE_NAME radiomicspngtonrrdconverter)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  PNGRadiomicsToolsLib/__init__
  PNGRadiomicsToolsLib/radiomicsDatabase
  PNGRadiomicsToolsLib/path
  PNGRadiomicsToolsLib/pngConverter
  )

set(MODULE_PYTHON_RESOURCES
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )
