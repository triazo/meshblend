import bpy
import bmesh


def poke(bm):
    for i,e in enumerate(bm.edges):
        if e.seam:
            print(("edge %d has seam value {}"%i).format(e.seam))
  
    #bm.edges.ensure_lookup_table()
  
    print("tex length initial: %d"%len(bm.faces.layers.tex))
    print("uv length initial:  %d"%len(bm.loops.layers.uv))

    uv_layer = bm.loops.layers.uv.verify()
    tv_layer = bm.faces.layers.tex.verify()
  
    print("tex length post: %d"%len(bm.faces.layers.tex))
    print("uv length post:  %d"%len(bm.loops.layers.uv))

    fn,ln = (0,0)
    print(dir(bm.faces[0]))
    for f in bm.faces:
        if f.select:
            for l in f.loops:
                luv = l[uv_layer]
                luv.uv.x = luv.uv.x - .1
                if l.edge.seam:
                    print(("face %d loop %d edge %d uv1 {}"%(fn, ln, l.edge.index)).format(luv.uv))
  
                ln += 1
        ln = 0
        fn += 1
  
  
  
if __name__ == "__main__":
    print("="*20 + "RUNNING SCRIPT" + "="*20)
    bpy.ops.object.mode_set(mode='EDIT')
    me = bpy.context.active_object.data
    bm = bmesh.from_edit_mesh(me)
  
    poke(bm)
  
    bmesh.update_edit_mesh(me)
    bpy.ops.object.mode_set(mode='EDIT')