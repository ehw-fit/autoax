

# script for evaluation of the module in dc.shell
proc evaluate { ds uid srcdir libList } {


    puts "UID: $uid"
    
    set prjdir $srcdir/synth/$uid
    file mkdir $prjdir

    # test if results already exist
    if {[file exists ${prjdir}/power_opt.rep]} {
        puts "Results already exist"
        return
    }

    foreach fn $libList {
        analyze -library work -format verilog $fn
    }
    #analyze -library work -format verilog $libList
    analyze -library work -format verilog ${srcdir}/${uid}.v 

    
    elaborate $uid -library work

    set_design_top $uid

    set_driving_cell  -lib_cell INVX1  [all_inputs]
    
    compile_ultra
    redirect "$prjdir/check.rep" { check_design }

    redirect "$prjdir/time_opt.rep" { report_timing }
    redirect "$prjdir/cell_opt.rep" { report_cell }
    redirect "$prjdir/power_opt.rep" { report_power }

}

