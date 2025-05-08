### collect the force and displacement info

set resu_path   ./2_Loading
set resu_file   0_Tension_AlongX_np
set out_path    ./collect_results
set out_file    smd_resu.dat

# 1. 
set log_file [open ${resu_path}/${resu_file}.log r]
set out_file [open ${out_path}/${out_file} w]

### add the values here
### 0.33588888663918554 0.3273905961923361 0.8831727200027835
set nx [expr 1.0]
set ny [expr 0.0]
set nz [expr 0.0]

### Loop over all lines of the log file
### set file [open ubq_ww_pcv.log r]
### set file [open chain_A_ws_pcv.log r]

while { [gets $log_file line] != -1 } {

### Determine if a line contains SMD output. If so, write the 
### timestep followed by f(dot)n to the output file
  if {[lindex $line 0] == "SMD"} {
    # puts $output "[lindex $line 1] [expr $nx*[lindex $line 5] + $ny*[lindex $line 6] + $nz*[lindex $line 7]]"
    #                  [time step] [posi         x] [posi         y] [posi         z] [Force       Fx] [Force       Fy] [Force       Fz] [Fn]
    puts $out_file "[lindex $line 1] [lindex $line 2] [lindex $line 3] [lindex $line 4] [lindex $line 5] [lindex $line 6] [lindex $line 7] [expr $nx*[lindex $line 5] + $ny*[lindex $line 6] + $nz*[lindex $line 7]]"
    }
  }

### Close the log file and the output .dat file
close $log_file
close $out_file

exit
