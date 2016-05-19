import sympy

u,v = sympy.symbols('s t', real=True)

def dot_product(a, b):
    return sum([a_ * b_ for a_,b_ in zip(a,b)])

def cross_product(a, b):
    # a2b3 - a3b2,a3b1 - a1b3, a1b2 - a2,b1
    rtrn = [None, None, None]
    rtrn[0] = (a[1]*b[2] - a[2]*b[1])
    rtrn[1] = (a[2]*b[0] - a[0]*b[2])
    rtrn[2] = (a[0]*b[1] - a[1]*b[0])
    return tuple(rtrn)

def norm(vector):
    if (len(vector) != 3):
        print("SOMETHING IS WRONG: %d"%len(vector))
    return sympy.sqrt(sum([v**2 for v in vector]))

def unit_normal(du, dv):
    cross = cross_product(du,dv)
    n = norm(cross)
    return tuple([c/n for c in cross])

def FFF(du,dv):
    if len(du) != 3 or len(dv) != 3:
        print("SOMETHING IS WRONG: %d"%len(du))
    E = dot_product(du, du)
    F = dot_product(du, dv)
    G = dot_product(dv, dv)
    
    return (E,F,G)

def SFF(du, dv):
    normal = unit_normal(du, dv)
    
    duu = tuple([sympy.diff(s,u) for s in du])
    duv = tuple([sympy.diff(s,v) for s in du])
    dvv = tuple([sympy.diff(s,v) for s in dv])
    
    L = dot_product(duu, normal)
    M = dot_product(duv, normal)
    N = dot_product(dvv, normal)
    
    return (L,M,N)

def gaussian_curvature(surface):
    du = tuple([sympy.diff(s, u) for s in surface])

    dv = tuple([sympy.diff(s, v) for s in surface])
    
    E,F,G = FFF(du,dv)
    L,M,N = SFF(du,dv)
    
    return (L*N - M**2) / (E*G - F**2)

if __name__ == "__main__":
    print("Gaussian curvature of sphere is:")
    print(sympy.simplify(gaussian_curvature((sympy.cos(u) * sympy.sin(v),
                                             sympy.sin(u) * sympy.sin(v),
                                             sympy.cos(v)))))