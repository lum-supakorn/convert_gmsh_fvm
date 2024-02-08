# All indices in mesh files are 1-based

import gmsh
import sys
import numpy as np

if len(sys.argv) < 2:
    print("Missing input mesh file.")
    sys.exit(1)

gmsh.initialize()

gmsh.open(str(sys.argv[1]))

# Nodes
node_tags, node_coords, _ = gmsh.model.mesh.getNodes(
      includeBoundary=True, returnParametricCoord=False)
node_tags = np.array(node_tags)
node_coords = np.array(node_coords).reshape(int(len(node_coords)/3), 3)
node_sort_idx = np.argsort(node_tags)
print(f'\nWriting {len(node_tags)} nodes...')
with open('mesh/node', 'w') as f:
    f.write(f'{len(node_tags)}\n')
    for i in range(len(node_tags)):
        f.write(f'{node_coords[node_sort_idx][i][0]} {node_coords[node_sort_idx][i][1]} ' +
                f'{node_coords[node_sort_idx][i][2]}')
        f.write('\n')

# Boundary faces
faces = []
face_node_tags = []
phys_group_assoc = [] # Physical group associated with each face
phys_groups = [pair[1] for pair in gmsh.model.getPhysicalGroups(dim=1)]
for phys_group in phys_groups:
    for ent_tag in gmsh.model.getEntitiesForPhysicalGroup(1, phys_group):
        _, current_face_tags, current_face_node_tags = \
                                    gmsh.model.mesh.getElements(dim=1, tag=ent_tag)
        for count, tag in enumerate(current_face_tags[0]):
            faces.append(tag)
            face_node_tags.append(current_face_node_tags[0][count*2])
            face_node_tags.append(current_face_node_tags[0][count*2+1])
            phys_group_assoc.append(phys_group)

# At this point all the boundary faces are stored. All that's left is to get the internal
# faces which are not given from Gmsh explicitly and must be collected from cell information.
_, cells, cell_node_tags = gmsh.model.mesh.getElements(dim=2)
cells = cells[0]
cell_node_tags = cell_node_tags[0]
face_count = len(faces)
cell_face_tags = []
for i in range(len(cells)):
    n = []
    for j in range(3):
        n.append(cell_node_tags[3*i+j])
    for j in range(3): # Loop over the cell's faces
        if j < 2:
            n1 = n[j]
            n2 = n[j+1]
        else:
            n1 = n[2]
            n2 = n[0]
        for k in range(face_count):
            n1_comp = face_node_tags[2*k]
            n2_comp = face_node_tags[2*k+1]
            are_same_edges = ((n1 == n1_comp) and (n2 == n2_comp)) or \
                    ((n1 == n2_comp) and (n2 == n1_comp))
            if (are_same_edges):
                cell_face_tags.append(k+1)
                break;
            elif k == face_count-1:
                face_node_tags.append(n1)
                face_node_tags.append(n2)
                face_count += 1
                cell_face_tags.append(face_count)

# Figure out each cell's face's associating neighbor cell
cell_face_neighbors = []
for i in range(len(cells)):
    for j in range(3):
        face = cell_face_tags[3*i+j]
        if face in faces: # Boundary face: no neighbor
            cell_face_neighbors.append(-1)
            continue
        for k in range(len(cells)): # Search for the neighbor cell
            for l in range(3):
                candidate = cell_face_tags[3*k+l]
                if face == candidate and i != k:
                    cell_face_neighbors.append(k+1)
                    break
            else:
                continue # Face not found in this cell, continue searching in other cells
            break # Face found (innermost loop terminated), terminate outer loop too

# Figure out each face's owner-neighbor tags
face_owner_neighbor = []
for i in range(face_count):
    face = i+1
    owner_found = False
    done_search = False
    for j in range(len(cells)):
        for k in range(3):
            candidate = cell_face_tags[3*j+k]
            if face == candidate:
                if (not owner_found):
                    face_owner_neighbor.append(j+1)
                    if face in faces: # Is a boundary face
                        face_owner_neighbor.append(-1)
                        done_search = True
                        break
                    owner_found = True
                    break # Done with this cell
                else:
                    face_owner_neighbor.append(j+1)
                    done_search = True
                    break # Done searching
        else:
            continue
        if (done_search):
            break

print(f'Writing {face_count} faces...')
with open('mesh/face', 'w') as f:
    f.write(f'{face_count}\n')
    for i in range(face_count):
        f.write(f'{face_node_tags[2*i]} {face_node_tags[2*i+1]}')
        if i < len(phys_group_assoc):
            f.write(f' {phys_group_assoc[i]} ')
        else:
            f.write(' -1 ')
        f.write(f'{face_owner_neighbor[2*i]} {face_owner_neighbor[2*i+1]}\n')

print(f'Writing {len(cells)} cells...')
with open('mesh/cell', 'w') as f:
    f.write(f'{len(cells)}\n')
    for i in range(len(cells)):
        f.write(f'{cell_node_tags[3*i]} {cell_node_tags[3*i+1]} {cell_node_tags[3*i+2]} ')
        f.write(f'{cell_face_tags[3*i]} {cell_face_tags[3*i+1]} {cell_face_tags[3*i+2]} ')
        f.write(f'{cell_face_neighbors[3*i]} {cell_face_neighbors[3*i+1]} ' + 
                f'{cell_face_neighbors[3*i+2]}\n')

gmsh.finalize()
print('Done')