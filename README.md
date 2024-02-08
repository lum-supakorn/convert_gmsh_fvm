# convert_gmsh_fvm
## About
This repository contains a Python script that turns a 2D tetrahedral GMSH mesh file (MSH version 2) into a set of mesh files that contain important information for a finite-volume code (owner cells, neighbor cells, and other connectivity information). Note that the script is quite rough as I wrote it quickly in the development of a finite-volume code. It is unoptimized and messy but works for now. I will continually improve it whenever I find a chance. **Note that currently only MSH version 2 is supported.** I found out the hard way that MSH version 4 is problematic and have not found a solution to that yet. Support for 3D and other mesh primitives should come soon.
## Dependencies
The package [gmsh](https://pypi.org/project/gmsh/) must be installed to enable GMSH Python API.
## Usage

    python3 convert_gmsh_fvm.py [input .msh file]
    
 Three files will be generated in `mesh/` (make sure this directory is available): `node`, `face`, `cell` which contains information for mesh nodes, faces, and cells, respectively.
 
 ## Output Format
 All indices in the output files are 1-based. If you use a 0-based indexing system in your code, make sure to correct for this. If an index in the output file is `-1` that means the corresponding entity does not exist. For example, a boundary face does not have a neighbor cell; therefore, `neighbor_cell_idx` is `-1`.
 ### `node`
 The first line contains the number of nodes `n_nodes`. The next  `n_nodes` lines contain node information.

    number of nodes
	x y z coordinates
	...
 ### `face`
 The first line contains the number of faces `n_faces`. The next  `n_faces` lines contain face information.

    number of faces
	node_1_idx node_2_idx physical_group_idx owner_cell_idx neighbor_cell_idx
	...
 ### `cell`
 The first line contains the number of cells `n_cells`. The next  `n_cells` lines contain cell information.

    number of cells
	node_1_idx node_2_idx node_3_idx face_1_idx face_2_idx face_3_idx face_1_assoc_neighbor_cell_idx face_2_assoc_neighbor_cell_idx face_3_assoc_neighbor_cell_idx
	...
