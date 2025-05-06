### tasks
### 1.
### 2.

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

# 1. read in the chain pdb
# mol load pdb ./${prefix}_chain_${chain}.pdb
# --- after initial psf
mol new ./${prefix}_chain_${chain}_after_psf.psf
mol addfile ./${prefix}_chain_${chain}_after_psf.pdb

# 2. move the center to origin
set allatom [atomselect top all]
# set allatomcen [measure center $allatom weight mass]
set allatomcen [measure center $allatom]
$allatom moveby [vecscale -1.0 $allatomcen]

# 3. find the min and max residues with ca
set sel [atomselect top "alpha"]
# set Residue_List [$sel get residue]
set ResidGot [$sel get resid]

set MinMaxResiId [MinMax_id $ResidGot]
set MinResiId [lindex $MinMaxResiId 0]
set MaxResiId [lindex $MinMaxResiId 1]

# 4. calculate the rotation
set CA_0 [atomselect top "resid $MinResiId and name CA"]
set CA_1 [atomselect top "resid $MaxResiId and name CA"]
# find the direction
set CA_0_Pos [lindex [$CA_0 get {x y z}] 0]
set CA_1_Pos [lindex [$CA_1 get {x y z}] 0]
set Vec_CA01 [vecnorm [vecsub $CA_1_Pos $CA_0_Pos]]

set RotMat [transvecinv $Vec_CA01]
$allatom move $RotMat

# do the centering again
set allatomcen [measure center $allatom weight mass]
# set allatomcen [measure center $allatom]
$allatom moveby [vecscale -1.0 $allatomcen]

# 5. writeout the pdb
$allatom writepdb ./${prefix}_chain_${chain}_after_psf_AlongX.pdb

# clean up
mol delete top

puts "$MinResiId"

### ===================================================
### calculate the tension parameters

### measure the original molecule
mol new ./${prefix}_chain_${chain}_after_psf.psf
mol addfile ./${prefix}_chain_${chain}_after_psf_AlongX.pdb

### Determine the center of mass of the molecule and store the coordinates
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

### Determine the distance of the farthest atom from the center of mass
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

# one AA length: 4.0 A
set NumAA  [expr $MaxResiId-$MinResiId+1]
set LenUnF [expr 4.0*$NumAA*0.9]
set TensinLen [expr $LenUnF-($max_x-$min_x)]

set x_add   [expr ($LenUnF-($max_x-$min_x))/2.]
set x_add_0 [expr ($LenUnF-($max_x-$min_x))*0.1]
set x_add_1 [expr ($LenUnF-($max_x-$min_x))*0.9]

set y_add [expr (4.)/2.]
set z_add [expr (4.)/2.]

set box_x0 [expr $min_x-$x_add_0]
set box_x1 [expr $max_x+$x_add_1]
set box_y0 [expr $min_y-$y_add]
set box_y1 [expr $max_y+$y_add]
set box_z0 [expr $min_z-$z_add]
set box_z1 [expr $max_z+$z_add]

set box_x_add_0 [expr $x_add_0+5.]
set box_x_add_1 [expr $x_add_1+5.]
set box_y_add   [expr $y_add+5.]
set box_z_add   [expr $z_add+5.]

### useful info for NPT simulation
set OX [expr ($box_x0+$box_x1)/2.]
set OY [expr ($box_y0+$box_y1)/2.]
set OZ [expr ($box_z0+$box_z1)/2.]
set LenX [expr ($box_x1-$box_x0)]
set LenY [expr ($box_y1-$box_y0)]
set LenZ [expr ($box_z1-$box_z0)]

# add some
# +++++++++++++++++++++++++++++++++++++++
set outfile [open ./box_dimension.dat w]

puts $outfile "set OX $OX"
puts $outfile "set OY $OY"
puts $outfile "set OZ $OZ"
puts $outfile "set LenX $LenX"
puts $outfile "set LenY $LenY"
puts $outfile "set LenZ $LenZ"

# add some: for SMD in multiple steps

set smd_vel [expr 0.0001+0.]
# set smd_stiff [expr 1.0]
set smd_stiff [expr 0.5]
# # for debug
# set smd_vel [expr 0.01+0.]

# change this into a source file
# set n_stage [expr 10*1]
source ./SMD_step_set.tcl 

set RunStep [expr int(${TensinLen}/${smd_vel})]
set RunStep_S [expr int( ceil(${RunStep}/${n_stage}) )]

set RunStep_S [expr int( ceil(${RunStep_S}/1000) )*1000]
set RunStep [expr int( ceil(${RunStep}/1000) )*1000]

# # for debug
# set RunStep_top [expr 120000]
# set RunStep_S   [expr 40000]

puts $outfile "set TensinLen $TensinLen"

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
mol addfile ./${prefix}_chain_${chain}_after_psf_AlongX.pdb

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
$allatoms writepdb ./${prefix}_chain_${chain}_after_psf_AlongX.ref

exit
