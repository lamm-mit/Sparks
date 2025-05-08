### Part 1: calculate RMSD for the protein part

set resu_path ./1_Equilibrate_system
set resu_name TestProt_chain_0_after_psf_AlongX_NPT
set log_name 0_EneMin_NPT_withConstrain

set out_path    ./collect_results

source ./1_Equilibrate_system/ContiInfo.dat
set MinizeSte [expr ${MinStep}+0]

# 1. read in the file
set resu_psf ./TestProt_chain_0_after_psf.psf
set resu_dcd ${resu_path}/${resu_name}.dcd

# mol new $resu_psf
# mol addfile $resu_dcd
mol new $resu_psf type psf first 0 last -1 step 1 filebonds 1  autobonds 1 waitfor all
mol addfile $resu_dcd type dcd first 0 last -1 step 1 filebonds 1  autobonds 1 waitfor all

# 2. calculate rmsd of the backbone
set out_rmsd_file "${out_path}/${resu_name}_rmsd.dat"

set outfile [open ${out_rmsd_file} w]
set nf [molinfo top get numframes]
set frame0 [atomselect top "protein and backbone and noh" frame 0]
set sel [atomselect top "protein and backbone and noh"]
# rmsd calculation loop
for {set i 1} {$i <= $nf} {incr i} {
  $sel frame $i
  $sel move [measure fit $sel $frame0]
  puts $outfile "$i [measure rmsd $sel $frame0]"
  puts "$i [measure rmsd $sel $frame0]"
}

close $outfile

# 3. plot process energy
source fun_0_namdstats_adjusted.tcl

# # data_time "TOTAL" "${resu_path}/${log_name}.log" 10000 last
data_time_Ene_TEMP_PRESSURE "${out_path}" "TOTAL" "${resu_path}/${log_name}.log" ${MinizeSte} last

exit
