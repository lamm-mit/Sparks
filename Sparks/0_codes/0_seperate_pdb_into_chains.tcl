### prepare
source path_lib.dat

set raw_pdb_file RAW_PDB
set prefix TestProt


# Load the PDB file
mol load pdb ./${raw_pdb_file}.pdb

# Handle water part
puts "Working on water part"
set water [atomselect top water]
$water writepdb ./${prefix}_water.pdb

# Handle all atoms (including all chains and other residues)
puts "Working on all atoms"
set all_atoms [atomselect top all]
$all_atoms writepdb ./${prefix}_chain_0.pdb

exit
