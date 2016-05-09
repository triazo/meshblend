import bpy
import bmesh

import sympy
import random
import importlib

import uv_map
importlib.reload(uv_map)

def new_grid(width, height, scale):
    # This function does what brandon's code should do eventually
    # But should be far easier to debug.
    
    nonce = ''.join(['0123456789abcdef'[random.randint(0,15)] for x in range(8)])
    
    me = bpy.data.meshes.new("GridMesh-"+nonce)
    bm = bmesh.new()

    for x in range(width + 1):
        for y in range(height + 1):
            bm.verts.new((x*scale, y*scale, .1))
            
    bm.verts.ensure_lookup_table()

    for x in range(width):
        for y in range(height):
            vo = [bm.verts[i] for i in [(height+1)*x + y, (height+1)*(x+1) + y, (height+1)*(x+1) + y + 1, (height+1)*x+y+1]]
            bm.faces.new(vo)
            
    bm.to_mesh(me)
    me.update()

    ob = bpy.data.objects.new("Grid-"+nonce, me)

    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
    me.update()
    
    # TODO: make and return data structure
    patches = []
    u,v = sympy.symbols('u v', real=True)
    for x in range(width//3):
        for y in range(height//3):
            verticies = [xx * (height+1) + yy for xx in range(x*3,x*3+4) for yy in range(y*3,y*3+4)]
            faces  = [xx * height + yy for xx in range(x*3,x*3+3) for yy in range(y*3,y*3+3)]
            patches.append((u * v, verticies, faces))
    return (ob, patches)

def test_select(ob, patch):
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    # A script to visually test the output from above somewhat
    for v in bm.verts:
        v.select = False
    
    for i in patch[1]:
        bm.verts[i].select = True
        
    bmesh.update_edit_mesh(ob.data, True)
    
def select_all(ob):
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        f.select = True

def deselect_all():
    scn = bpy.context.scene
    for o in scn.objects:
        o.select = False
        
    scn.objects.active = None
    
if __name__ == "__main__":
    if bpy.context.active_object:
        bpy.ops.object.mode_set(mode='OBJECT')
    deselect_all()
    ob, patches = new_grid(300,300,.1)
    #test_select(ob, patches[0])
    uv_map.map_patches(ob,None,patches)
    select_all(ob)