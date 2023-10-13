# script for evaluation of the module in vivado
proc evaluate { ds uid srcdir libList } {
#set uid random_79F4B8
#set srcdir tmp/vivado/random
    puts "UID: $uid"
    
    set prjdir $srcdir/synth/$uid
    file mkdir $prjdir

    # teest if results already exist
    if {[file exists ${prjdir}/results_resource.txt]} {
        puts "Results already exist"
        return
    }

        if {[file exists ${prjdir}/project_${uid}.xpr]} {
        puts "Project already exist"
        return
    }

    create_project project_${uid} ${prjdir} -part xc7vx485tffg1157-1


    add_files -norecurse -scan_for_includes ${srcdir}/${uid}.v 
    foreach i $libList {
        add_files -norecurse -scan_for_includes $i
    }
    update_compile_order -fileset sources_1

    set_property STEPS.SYNTH_DESIGN.ARGS.MAX_DSP 0 [get_runs synth_1]
    launch_runs synth_1 -jobs 8
    wait_on_run -timeout 60 synth_1
    launch_runs impl_1 -jobs 8
    wait_on_run -timeout 60 impl_1
    open_run impl_1

    report_power -file ${prjdir}/results_power.txt
    report_design_analysis -file ${prjdir}/results_time.txt
    report_utilization -file ${prjdir}/results_resource.txt
    close_project
}