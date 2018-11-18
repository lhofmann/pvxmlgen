
find_package(ParaView)

if (ParaView_FOUND)
    include(${PARAVIEW_USE_FILE})
    add_paraview_plugin(MyFilter 1.0
        SERVER_MANAGER_XML MyFilter.xml
        SERVER_MANAGER_SOURCES vtkMyFilter.cxx)
else ()
    add_library(MyFilter vtkMyFilter.cxx)
endif ()

pvxmlgen_generate(MyFilter INPUT vtkMyFilter.h OUTPUT MyFilter.xml)
