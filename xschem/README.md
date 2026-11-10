# xschem/

The existing SSPLL design (cells, symbols, testbenches in `tb/`, and `xschemrc`) is imported here as the
baseline in step 4. Its `xschemrc` must start with

    source $env(PDK_ROOT)/$env(PDK)/libs.tech/xschem/xschemrc
    append XSCHEM_LIBRARY_PATH :[file dirname [file normalize [info script]]]

so the PDK symbols resolve on any machine. Then:  `./tools/netlist_all.sh && python3 tools/check_netlists.py`
