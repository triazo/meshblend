import bpy, bmesh, sympy
import mathutils
from collections import OrderedDict
from mathutils import Vector

#Provided from the Blender Wiki

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

#End of Wiki Code

def centroid(f_verts):
    n_verts = len(f_verts)    
    # find the average value on a face
    sum = sympy.Matrix(1,3,[0,0,0])
    for i in range(0,n_verts):
        sum += f_verts[i]
    return sum/n_verts

def add_faces_for_edges(edges_to_faces,all_faces, vertex_to_all):
    # add the faces for each edge
    edges = list(edges_to_faces.keys())
    for i in range(0,len(edges_to_faces)):
        new_face = []
        # get the faces and find the p primes
        face1 = True
        for j in range(0,len(edges_to_faces[edges[i]])):
            # face per edge
            f = edges_to_faces[edges[i]][j]
            #find the new points corresponding to the old point and face
            edgs = edges[i]
            
            if not face1:
                edgs = reversed(edgs)
            for k in edgs:
                new_face.append(vertex_to_all[face_to_new_pt[(f,k)]]) 

            face1 = False          
        all_faces.append(new_face)   
        
def add_faces_for_faces(faces,vertices, all_faces, all_verts):
    #for each face in the polygon
    for j in range (0,len(faces)):
        face = faces[j]
        f_verts = [sympy.Matrix(1,3,vertices[x]) for x in face]
        n_verts = len(f_verts)
        avg = centroid(f_verts)
        to_add = []
        
        # find the corresponding new pt
        for i in range (0,n_verts):
            new_pt = tuple(avg/4.0 + f_verts[(i-1)%n_verts]/8.0 
                    + f_verts[i%n_verts]/2.0 + f_verts[(i+1)%n_verts]/8.0)         
            i_vert = face[i]   
            if new_pt not in vertex_to_all.keys():
                all_vert_len = len(all_verts)
                to_add.append(len(all_verts))
                all_verts.append(new_pt) 
                vertex_to_all[new_pt] = all_vert_len 
            else:
                to_add.append(vertex_to_all[new_pt])
            face_to_new_pt[(j,i_vert)] = new_pt           
        all_faces.append(to_add)


def faces_to_centroids(faces,vertices):
    centroids = []
    for i in range(0, len(faces)):
        face = faces[i]
        f_verts = [sympy.Matrix(1,3,vertices[x]) for x in face]
        centroids.append(centroid(f_verts))
    return centroids
    
def get_faces_from_edges(face_edges):
    edges_to_faces = {}
    for i in range(0, len(face_edges)):
        fes = face_edges[i]
        for fe in fes:
            if fe not in edges_to_faces.keys():
                edges_to_faces[fe] = []
            edges_to_faces[fe].append(i)
    return edges_to_faces
#get the active mesh
obj = bpy.context.active_object

# Get editmode changes
obj.update_from_editmode()
vertices = [tuple(x.co.xyz) for x in obj.data.vertices]

# get the face of the mesh

mesh = obj.data
polys = mesh.polygons

faces = [tuple(x.vertices) for x in polys] # vertices of faces
face_edges = [tuple(x.edge_keys) for x in polys] 

edges_to_faces = get_faces_from_edges(face_edges)


all_verts = [] # new vertices for the generated surface
all_faces = [] # new face indicies for the generated surface
vertex_to_all = {} # mapping to avoid O(n) lookup
face_to_new_pt = {} # (f_index, pt) -> new pt
  
add_faces_for_faces(faces,vertices,all_faces,all_verts)
add_faces_for_edges(edges_to_faces,all_faces,vertex_to_all)

createMeshFromData('RefinedMesh', Vector((0,0,0)), 
                            tuple(all_verts), tuple(all_faces))

                                               
bpy.ops.object.editmode_toggle()
#flip the inside out panels
bpy.ops.mesh.normals_make_consistent(inside=False)
#add the faces corresponding to vertices
bpy.ops.object.select_pattern(pattern='RefinedMesh')
bpy.ops.mesh.edge_face_add()
bpy.ops.object.editmode_toggle()

quadnets = []

#get the active mesh
obj = bpy.context.active_object
# Get editmode changes
obj.update_from_editmode()

mesh = obj.data
polys = mesh.polygons

#ridiculous formula result
def rid_map(f_verts,i):
    tot = sympy.Matrix(1,3,[0,0,0])
    n = len(f_verts)
    beta  = (2/3 * (1 + sympy.cos(2*sympy.pi/n))).evalf()
    for j in range(0,n):
        tot = (tot + f_verts[j]*(1.0 + beta*(sympy.cos((2.0*sympy.pi*(j-i)/n)) + sympy.tan(sympy.pi/n)*sympy.sin((2.0*sympy.pi*(j-i))/n)))).evalf()
    return tot / n

#returns face index, and index on the face
def vertex_to_faces(faces):
    vert_to_face = {}
    for i in range(0,len(faces)):
        for j in range (0,len(faces[i])):
            vert = faces[i][j]
            if vert not in vert_to_face.keys():
                vert_to_face[vert] = []
            vert_to_face[vert].append((i,j))
    
    """
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='TOGGLE')
    mesh=bmesh.from_edit_mesh(bpy.context.object.data)
    mesh.verts.ensure_lookup_table()
    for item in vert_to_face.keys():
        if (len(vert_to_face[item])!= 4):
            print (vert_to_face[item])
            mesh.verts[item].select=True
            # trigger viewport update
            bpy.context.scene.objects.active = bpy.context.scene.objects.active
    """
    return vert_to_face

faces = [tuple(x.vertices) for x in polys] # vertices of face
vertices = [tuple(x.co.xyz) for x in obj.data.vertices]
centroids = faces_to_centroids(faces,vertices)
face_vert_quad_map = {}
for i in range(0,len(faces)):
    f_verts = [sympy.Matrix(1,3,vertices[x]) for x in faces[i]]
    for j in range(0,len(faces[i])):
        face_vert_quad_map[(i,j)] = rid_map(f_verts,j) #TODO
    
vert_to_face = vertex_to_faces(faces)

# for each of the vertices
# find the surrounding faces 
# the pt corresponding to the vertex on the face and the counterclockwise point


quad_net = []  #vertices
quad_face = [] #faces

new_points = {}
#create a mapping from the vertex to the (face, new_pt, new_clockwise_pt)
vertex_to_new_pts = {}

for i in range(0,len(vert_to_face)):
    vert_faces = vert_to_face[i]
    for j in range(0, len(vert_faces)):
        
        to_add = []
        prev_len = len(quad_net)
        #vertex -> face_index, index_on_face
        new_vert = vert_faces[j]
        face_index = new_vert[0]
        index_on_face = new_vert[1]
        centroid = tuple(centroids[face_index])
                
        offset = -1
        if centroid not in new_points.keys():   
            quad_net.append(centroid)
            new_points[centroid] = prev_len
            prev_len = prev_len + 1
           
        to_add.append(new_points[centroid])
            
        n_verts = len(faces[face_index])
        vert_pt = tuple(face_vert_quad_map[(face_index,(index_on_face+offset)%n_verts)])
        if vert_pt not in new_points.keys():
            quad_net.append(vert_pt)
            new_points[vert_pt] = prev_len
            prev_len = prev_len + 1

        to_add.append(new_points[vert_pt])
        
        # get the clockwise point on the face
        clockwise_pt = tuple(face_vert_quad_map[(face_index, (index_on_face+offset+1)%n_verts)])
        if clockwise_pt  not in new_points.keys():
            quad_net.append(clockwise_pt)
            new_points[clockwise_pt] = prev_len
            prev_len = prev_len + 1
            
        to_add.append(new_points[clockwise_pt])
        
        vertex_to_new_pts[(i,face_index)] = (vert_pt,clockwise_pt) #??
        quad_face.append(tuple(to_add))

face_edges = [tuple(x.edge_keys) for x in polys]        
edges_to_faces = get_faces_from_edges(face_edges)


# edges have a start vertex and an end vertex

face_edges = {}
me = bpy.context.object.data
for poly in me.polygons:
    f_edges = []
    for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
        f_edges.append(me.loops[loop_index].vertex_index)
    face_edges[poly.index] = f_edges
    

#vertex index to quadnet points
# {vertex_index: {face: []}}
quad_nets = OrderedDict()

# map a vertex to a ordered list of the inner points  
# {vetex_index: {pt_1, pt_2,pt_3, pt_4}}
#inner_pts = OrderedDict()
           
for i in range(0,len(face_edges)):
    face = face_edges[i]
    n_verts = len(face)
    for j in range(0,n_verts):
        v_hat = face[j]
        v = face[(j+1) % n_verts]
        
        # vert_pt of the corresponding vertex and face        
        other_face = list(set(edges_to_faces[min((v_hat,v),(v,v_hat))])-set([i]))[0]        
        pt_1 = sympy.Matrix(1,3,vertex_to_new_pts[(v,i)][0])
        pt_2 = sympy.Matrix(1,3,vertex_to_new_pts[(v,other_face)][1])        
        new_pt = tuple(0.5 * pt_1 + 0.5*pt_2 + 1/6.0*(sympy.Matrix(1,3,vertices[v_hat]) - sympy.Matrix(1,3,vertices[v])))
        
        if new_pt not in new_points.keys():
            new_points[new_pt] = len(quad_net)
            quad_net.append(new_pt)
                
        quad_face.append((new_points[new_pt],new_points[tuple(pt_1)], new_points[tuple(pt_2)]))
        
               
        if v not in quad_nets.keys():
            quad_nets[v] = OrderedDict()
        
        if 'last_face' not in quad_nets[v].keys():
            quad_nets[v]['last_face'] = None
        
        last_face = quad_nets[v]['last_face']
            
        if 'points' not in quad_nets[v].keys() :
            quad_nets[v]['points'] = []
        
        if last_face == None:
            centroid = tuple(centroids[i])
            quad_nets[v]['points'].append(new_points[vertex_to_new_pts[(v,i)][1]]) # clockwise_pt
            quad_nets[v]['points'].append(new_points[centroid])
            quad_nets[v]['points'].append(new_points[vertex_to_new_pts[(v,i)][0]]) # new_pt
            quad_nets[v]['points'].append(new_points[new_pt])
            
        if last_face == i: 
            quad_nets[v]['last_face'] = other_face  
            centroid = tuple(centroids[other_face])
            quad_nets[v]['points'].append(new_points[vertex_to_new_pts[(v,other_face)][1]]) # clockwise_pt
            quad_nets[v]['points'].append(new_points[centroid])
            quad_nets[v]['points'].append(new_points[vertex_to_new_pts[(v,other_face)][0]]) # new_pt
            quad_nets[v]['points'].append(new_points[new_pt])

# these are the vertices in the dictionary new_points
quad_net_verts = [] 
            
for vert in quad_nets.keys():
    quad_net_verts.append(quad_nets[vert]['points'])
    #assert(len(quad_nets[vert]['points'])==16)
    
#print(quad_net_verts)


createMeshFromData('QuadTest', Vector((3,3,0)), 
                            tuple(quad_net), tuple(quad_face))                                                                                         
bpy.ops.object.editmode_toggle()

#flip the inside out panels
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.editmode_toggle()