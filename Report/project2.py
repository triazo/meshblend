import bpy, bmesh, sympy
import mathutils
from mathutils import Vector

def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True
 
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
 
    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update()    
    return ob
 
def createMeshFromOperator(name, origin, verts, faces):
    bpy.ops.object.add(
        type='MESH', 
        enter_editmode=False,
        location=origin)
    ob = bpy.context.object
    ob.name = name
    ob.show_name = True
    me = ob.data
    me.name = name+'Mesh'
 
    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update()    
    # Set object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob
 
def createMeshFromPrimitive(name, origin):
    bpy.ops.mesh.primitive_cone_add(
        vertices=4, 
        radius=1, 
        depth=1, 
        cap_end=True, 
        view_align=False, 
        enter_editmode=False, 
        location=origin, 
        rotation=(0, 0, 0))
 
    ob = bpy.context.object
    ob.name = name
    ob.show_name = True
    me = ob.data
    me.name = name+'Mesh'
    return ob
 
def createArmatureFromData(name, origin):
    # Create armature and object
    amt = bpy.data.armatures.new(name+'Amt')
    ob = bpy.data.objects.new(name, amt)
    ob.location = origin
    ob.show_name = True
 
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
 
    # Create single bone
    bpy.ops.object.mode_set(mode='EDIT')
    bone = amt.edit_bones.new('Bone')
    bone.head = (0,0,0)
    bone.tail = (0,0,1)
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob
 
def createArmatureFromOperator(name, origin):
    bpy.ops.object.add(
        type='ARMATURE', 
        enter_editmode=True,
        location=origin)
    ob = bpy.context.object
    ob.name = name
    ob.show_name = True
    amt = ob.data
    amt.name = name+'Amt'
 
    # Create single bone
    bone = amt.edit_bones.new('Bone')
    bone.head = (0,0,0)
    bone.tail = (0,0,1)
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob
 
def createArmatureFromPrimitive(name, origin):
    bpy.ops.object.armature_add()
    bpy.ops.transform.translate(value=origin)
    ob = bpy.context.object
    ob.name = name
    ob.show_name = True
    amt = ob.data
    amt.name = name+'Amt'
    return ob

#get the active mesh
obj = bpy.context.active_object

# Get editmode changes
obj.update_from_editmode()

vertices = [tuple(x.co.xyz) for x in obj.data.vertices]

# edges have a start vertex and an end vertex
edges = [tuple(x.vertices) for x in obj.data.edges]

#clear the screen
print('\n'*100)

print('{0} edges found'.format(len(edges)))

print (edges)

for edge in edges:
    left_vert = vertices[edge[0]]
    right_vert = vertices[edge[1]]
    print("{0}: {1} --> {2}".format(str(edge),left_vert,right_vert))
    
print ('\n' * 5)

# get the face of the mesh
mesh = obj.data
print("# of faces=%d" % len(mesh.polygons))
faces = [tuple(x.vertices) for x in mesh.polygons]
print (faces)


all_verts = []
all_faces = []
vertex_to_new_face = {}

# As the faces are created, keep track of the points
# corresponding to the new face
# for each vertex mapping to the new face points
# create a new face

#for each face in the polygon
for j in range (0,len(faces)):
    face = faces[j]
    #assert(len(face)==4)
    f_verts = [sympy.Matrix(1,3,vertices[x]) for x in face]
    print (f_verts)
    n_verts = len(f_verts)
    # find the average value on a face
    for i in range(0,n_verts):
        sum = sympy.Matrix(1,3,[0,0,0])
        sum += f_verts[i]
    avg = sum/n_verts
    print('\t' + str(avg))
    to_add = []
    
    # find the corresponding new pt
    for i in range (0,n_verts):
        new_pt = avg/4.0 + f_verts[(i-1)%n_verts]/8.0 + f_verts[i%n_verts]/2.0 + f_verts[(i+1)%n_verts]/8.0
        
        tup_vert = tuple(f_verts[i])
        # keep track of the points in the new face corresponding to old face
        if tup_vert not in vertex_to_new_face.keys():
            vertex_to_new_face[tup_vert] = []
        vertex_to_new_face[tup_vert].append(tuple(new_pt))
        
        #inefficient change this
        if tuple(new_pt) not in all_verts:
            to_add.append(len(all_verts))
            all_verts.append(tuple(new_pt))  
        else:
            to_add.append(all_verts.index(tuple(new_pt)))    
            
        print('TEST:' + str(f_verts[i]))
    all_faces.append(to_add)
    print('New face\n*******************************\n')
    
print ("Length of vertices:{0}".format(len(all_verts)))    
# add back the faces for each vertex    
n_verts  = len(all_verts)
keys = list(vertex_to_new_face.keys())
"""
for i in range(0,len(keys)):
    vertex = vertex_to_new_face[keys[i]];
    # construct the new face
    new_face = []
    for j in range(0,len(vertex)):
        all_verts.append(vertex[j])
        new_face.append(n_verts + j)
    all_faces.append(new_face)
"""        
print ("NEW Length of vertices:{0}".format(len(all_verts)))          
                              
print (all_verts)
cone1 = createMeshFromData('DataCone', Vector((0,0,0)), tuple(all_verts), tuple(all_faces))