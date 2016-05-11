import bpy
import bmesh
import os

# Change this to determine the positions of things.
# Will need to alter this line to take into account the buffer built into the uv map.
positions = [(x/3,y/3) for y in range(3,-1,-1) for x in range(4)]

def new_mat(filename):
    img = bpy.data.images.load(os.path.realpath(filename))
    
    tex = bpy.data.textures.new(filename + 'tex', type='IMAGE')
    tex.image = img
    
    mat = bpy.data.materials.new(filename + 'mat')
    mtx = mat.texture_slots.add()
    mtx.texture = tex
    mtx.texture_coords = 'UV'
    
    # Not sure how necessary this is
    mtx.use_map_color_diffuse = True 
    mtx.use_map_color_emission = True 
    mtx.emission_color_factor = 0.5
    mtx.use_map_density = True 
    mtx.mapping = 'FLAT'
    
    return mat

def map_patches(object, filename, patches):
    bpy.ops.object.mode_set(mode='EDIT')
    
    mat = new_mat(filename)
    object.data.materials.append(mat)
    
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