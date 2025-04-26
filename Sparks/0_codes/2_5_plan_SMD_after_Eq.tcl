### define functions
proc MinMax_id {id_list} {
  # set min_id [lindex get $id_list 0]
  # set max_id [lindex get $id_list 0]
  set min_id [lindex $id_list 0]
  set max_id [lindex $id_list 0]
  # loop
  foreach id $id_list {
    if {$id < $min_id} {set min_id $id}
    if {$id > $max_id} {set max_id $id}
  }
  return [list $min_id $max_id]
}


### prepare
# set raw_pdb_file 1ubq_from_web
set prefix TestProt
#
set chain 0

### tasks
### A. read in the last frame

# 1. read in the file
set resu_path ./1_Equilibrate_system
set resu_name TestProt_chain_0_after_psf_AlongX_NPT
set log_name 0_EneMin_NPT_withConstrain

set resu_psf ./TestProt_chain_0_after_psf.psf
set resu_dcd ${resu_path}/${resu_name}.dcd

# mol new $resu_psf
# mol addfile $resu_dcd
mol new $resu_psf type psf first 0 last -1 step 1 filebonds 1  autobonds 1 waitfor all
mol addfile $resu_dcd type dcd first 0 last -1 step 1 filebonds 1  autobonds 1 waitfor all

set nf [molinfo top get numframes]
set nf [expr $nf-1]
puts "readin frame #: ${nf}"

# set sel [atomselect top "protein and backbone and noh"]
set sel [atomselect top all] 
$sel frame $nf
$sel update
$sel writepdb ./${prefix}_chain_${chain}_after_psf_AlongX_AfterEq.pdb
puts "write the last frame of Eq"
# clean up
mol delete top

### B. geometry analysis
mol new ./${prefix}_chain_${chain}_after_psf.psf
mol addfile ./${prefix}_chain_${chain}_after_psf_AlongX_AfterEq.pdb

# find the min and max residues with ca
set sel [atomselect top "alpha"]
set ResidGot [$sel get resid]
set MinMaxResiId [MinMax_id $ResidGot]
set MinResiId [lindex $MinMaxResiId 0]
set MaxResiId [lindex $MinMaxResiId 1]

### ===================================================
### calculate the tension parameters


### Determine the distance of the farthest atom from the center of mass
set cen [measure center [atomselect top all] weight mass]
set x1 [lindex $cen 0]
set y1 [lindex $cen 1]
set z1 [lindex $cen 2]

set max 0
set max_x 0
set min_x 0
set max_y 0
set min_y 0
set max_z 0
set min_z 0

foreach atom [[atomselect top all] get index] {
  set pos [lindex [[atomselect top "index $atom"] get {x y z}] 0]
  set x2 [lindex $pos 0]
  set y2 [lindex $pos 1]
  set z2 [lindex $pos 2]
  set dist [expr pow(($x2-$x1)*($x2-$x1) + ($y2-$y1)*($y2-$y1) + ($z2-$z1)*($z2-$z1),0.5)]
  if {$dist > $max} {set max $dist}

  ####
  set diff_x [expr $x2-$x1]
  if {$diff_x > $max_x} {set max_x $diff_x}
  if {$diff_x < $min_x} {set min_x $diff_x}
  set diff_y [expr $y2-$y1]
  if {$diff_y > $max_y} {set max_y $diff_y}
  if {$diff_y < $min_y} {set min_y $diff_y}
  set diff_z [expr $z2-$z1]
  if {$diff_z > $max_z} {set max_z $diff_z}
  if {$diff_z < $min_z} {set min_z $diff_z}
  }
### output the results:
puts "Center of the Chain A: $x1, $y1, $z1"
# puts "Max R, Lx/2, Ly/2, Lz/2: $max, $max_x, $max_y, $max_z"
puts "Max R: $max"
puts "x min max: $min_x, $max_x"
puts "y min max: $min_y, $max_y"
puts "z min max: $min_z, $max_z"

# calculate the countour length
# one AA length: 4.0 A
set NumAA  [expr $MaxResiId-$MinResiId+1]
set LenUnF [expr 4.0*$NumAA*0.9]
set TensinLen [expr $LenUnF-($max_x-$min_x)]
set GapAfterEq [expr ($max_x-$min_x)]

# add some: for SMD in multiple steps
# ============================================
set smd_vel [expr 0.0001+0.]
# set smd_stiff [expr 1.0]
set smd_stiff [expr 0.5]
# ============================================

# # ============================================
# # # for debug
# set smd_vel [expr 0.001+0.]
# set smd_stiff [expr 0.5]
# # ============================================

# change this into a source file
# set n_stage [expr 10*1]
source ./SMD_step_set.tcl 

set RunStep [expr int(${TensinLen}/${smd_vel})]
set RunStep_S [expr int( ceil(${RunStep}/${n_stage}) )]

set RunStep_S [expr int( ceil(${RunStep_S}/1000) )*1000]
set RunStep [expr int( ceil(${RunStep}/1000) )*1000]

# +++++++++++++++++++++++++++++++++++++++
# write to file
set outfile [open ./box_dimension_after_eq.dat w]

puts $outfile "set TensinLen $TensinLen"
puts $outfile "set IniGapAfterEq $GapAfterEq"
puts $outfile "set TargetGap $LenUnF"

puts $outfile "set SMD_Vel ${smd_vel}"
puts $outfile "set SMD_Sti ${smd_stiff}"
puts $outfile "set n_stage ${n_stage}"
puts $outfile "set RunStep_tot ${RunStep}"
puts $outfile "set RunStep_sep ${RunStep_S}"

close $outfile

mol delete top

### +++++++++++++++++++++++++++++
### =====================================================
### add the ref file for atom fix and confinement

mol new ./${prefix}_chain_${chain}_after_psf.psf
mol addfile ./${prefix}_chain_${chain}_after_psf_AlongX_AfterEq.pdb

set allatoms [atomselect top all]

# 1. the x0 end: fix 
$allatoms set beta 0
set CA_0 [atomselect top "resid $MinResiId and name CA"]
$CA_0 set beta 1

# 2. the x1 end: confine in y and z
$allatoms set occupancy 0
set CA_1 [atomselect top "resid $MaxResiId and name CA"]
$CA_1 set occupancy 1

# 3. write out for reference
$allatoms writepdb ./${prefix}_chain_${chain}_after_psf_AlongX_AfterEq.ref

exit