### render the pulling process

# display resize 1280 720 

color Display Background white
display depthcue off
display projection Orthographic
axes location Off
display shadows on                    
display ambientocclusion on

# box info
source box_dimension.dat
set Box_X0 [expr $OX-$LenX/2.]
set Box_X1 [expr $OX+$LenX/2.]
set Box_Y0 [expr $OY-$LenY/2.]
set Box_Y1 [expr $OY+$LenY/2.]
set Box_Z0 [expr $OZ-$LenZ/2.]
set Box_Z1 [expr $OZ+$LenZ/2.]
set disp_LenX [expr int($LenX*1.2)*5]
set disp_LenY [expr int($LenY*1.5)*5]

puts "disp Len X Y: $disp_LenX, $disp_LenY"
# display height 4.0
# display resize $disp_LenX $disp_LenY
# 
# display reposition  10  900
# display distance -1.
# set s_val [expr 100.0*1]
# eval "scale to  $s_val"



### prepare
set raw_pdb_file 1ubq_from_web
set prefix TestProt
#
set chain 0
#
set resu_path   ./2_Loading
set resu_name   smdout
#
set pict_path ./md_pict


# display resize 720 72 
# display resize 720 72 

package require timeline 2.0

# 1. load the files
# mol new ./${prefix}_chain_${chain}_after_psf_AlongX_CubeWB.psf
# mol addfile ${resu_path}/${resu_name}.dcd

mol new ./${prefix}_chain_${chain}_after_psf.psf type psf first 0 last -1 step 1 filebonds 1  autobonds 1 waitfor all
mol addfile ${resu_path}/${resu_name}.dcd type dcd first 0 last -1 step 1 filebonds 1  autobonds 1 waitfor all
        
# set WaterSet [atomselect top "waters"]
# set ProteSet [atomselect top "protein"]

# mol modselect rep_number molecule_number selection

# mol addrep 1

# mol selection "waters"
# mol selection "protein"

# mol list

# 
set frame_num [molinfo top get numframes]

animate goto 0

# add a new material for water part
# ref: material23 in http://www.ks.uiuc.edu/Training/Tutorials/vmd/vmd-tutorial.pdf
material add MateWater
material change opacity   MateWater 0.110000
material change ambient   MateWater 0.30
material change diffuse   MateWater 0.50
material change specular  MateWater 0.87
material change shininess MateWater 0.85

mol modselect 0 0 waters
mol modmaterial 0 0 MateWater
mol modstyle 0 0 QuickSurf
mol modcolor 0 0 ResName

# move to the protein part
mol addrep 0
mol modselect   1 0 protein
mol modmaterial 1 0 AOEdgy
mol modcolor    1 0 Structure
mol modstyle    1 0 NewCartoon

# for debug

# set frame_num 1

# set allatom [atomselect top all]
# $allatom moveby [vecscale -1.0 {$LenX/2.  0.  0.}]



# =========================================
display resize $disp_LenX $disp_LenY
scale by 2

# translate by -9  0  0
translate by -5  0  0

for {set ii 1} {$ii<=$frame_num} {incr ii} {
	
	set filename [format "%05d" $ii].tga
	
	if { [file exists ${pict_path}/${filename}]!=1 } {
	
		set i_frame [expr $ii-1]
		animate goto $i_frame
		# display update
		# update ss for the protein
		mol ssrecalc 0

		# for debug:
		puts "woring on ${i_frame}"

		# set filename [format "%05d" $ii].tga
		# # render snapshot ${pict_path}/${ii}.bmp
		# render TachyonLOptiXInternal ${pict_path}/${filename} 
		set filename [format "%05d" $ii].tga
		render TachyonInternal ${pict_path}/${filename}
		
	}
}

# animate goto 50
# mol ssrecalc 0

# render snapshot ${pict_path}/50.bmp
exit

