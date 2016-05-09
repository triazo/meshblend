import bpy
import bmesh

# Change this to determine the positions of things.
# Will need to alter this line to take into account the buffer built into the uv map.
positions = [(x/3,y/3) for y in range(4) for x in range(4)]

def map_patches(object, image, patches):
    bpy.ops.object.mode_set(mode='EDIT')
    me = object.data
    bm = bmesh.from_edit_mesh(me)
    
    n = len(patches)
    
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    
    uv_layer = bm.loops.layers.uv.verify()
    tv_layer = bm.faces.layers.tex.verify()
    
    for i, patch in enumerate(patches):
        for f in [bm.faces[j] for j in patch[2]] :
            for l in f.loops:
                # Can this line be optimized? maybe.
                coords = positions[patch[1].index(l.vert.index)]
                coords = (coords[0], (coords[1] + i)/n)
                luv = l[uv_layer]
                luv.uv = coords
                
    bmesh.update_edit_mesh(me)

if __name__ == "__main__":
    print("This should only be used as a module")