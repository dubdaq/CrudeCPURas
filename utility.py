import math, numpy

class vec2:
    def __init__(self, x, y) :
        self.x = x
        self.y = y

    def __iter__(self):
        return iter([self.x, self.y])

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and other.y == self.y

    def __hash__(self):
        return hash((float(self.x), float(self.y)))

    def dot(self, other):
        return self.x*other.x + self.y*other.y

    def normal(self):
        mgn = math.sqrt(self.x*self.x + self.y*self.y) 
        if mgn == 0: return None
        return vec2(-self.y/mgn, self.x/mgn)

class vec3 :
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.hmg = [x, y, z, 1]

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return vec3(self.x*other, self.y*other, self.z*other)
        else :
            return NotImplemented

    def __add__(self, other):
        if isinstance(other, vec3):
            return vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        else :
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, vec3):
            return vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        else :
            return NotImplemented

    def cross(self, other):
        return vec3(self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x)

    def dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z
    
    def mag(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def angle(pivot, A, B):
        u = A - pivot
        v = B - pivot
        angle = math.acos(u.dot(v) / (u.mag() * v.mag()))
        return angle

    def __iter__(self):
        return iter([self.x, self.y, self.z])
    
def clamp(val, a, b):
    return min(b, max(a, val))

def mag(vector):
    return math.sqrt(sum([i*i for i in vector]))

def normalize(vector, value = 1):
    return [i*value/mag(vector) for i in vector] if mag(vector) != 0 else None

def cross(vectorA, vectorB):
    a1, a2, a3 = vectorA
    b1, b2, b3 = vectorB
    return [a2*b3 - b2*a3, a3*b1 - b3*a1, a1*b2 - b1*a2]

def normal(A, B, C):
    return normalize(cross(C-A, B-A))



if __name__ == "__main__":
    a = vec2(1, 2)
    b = vec2(1, 1)
    b.y = 2
    l = set([a, b])
    print(a == b)
    print([f"{i.x},{i.y}" for i in l])