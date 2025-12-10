# Geometry Library - Reusable classes for geometric operations

from functools import cache



class Line:
    """Represents an infinite line in 2D space using equation ax + by = c"""
    
    def __init__(self, p1, p2, epsilon=1e-3):
        """
        Initialize a line through two points.
        
        Args:
            p1: (x, y) tuple - first point
            p2: (x, y) tuple - second point
            epsilon: tolerance for floating point comparisons
        """
        self.epsilon = epsilon
        x1, y1 = p1
        x2, y2 = p2
        
        if x1 == x2:
            # Vertical line: x = x1
            self.a, self.b, self.c = 1, 0, x1
        else:
            # General line: y = ax + b -> ax - y = -b
            a = (y1 - y2) / (x1 - x2)
            b = (x2 * y1 - x1 * y2) / (x2 - x1)
            self.a, self.b, self.c = a, -1, -b
        
        self.line = self
    
    def has(self, p):
        """Check if point p lies on this line"""
        if not p:
            return False
        x, y = p
        return abs(x * self.a + y * self.b - self.c) <= self.epsilon
    
    def inter(self, other):
        """
        Find intersection point with another line.
        
        Returns:
            (x, y) tuple if lines intersect, None if parallel
        """
        a, b, p = self.a, self.b, self.c
        c, d, q = other.a, other.b, other.c
        
        det = a * d - b * c
        if abs(det) <= self.epsilon:
            return None  # Lines are parallel
        
        # Solve system using Cramer's rule
        a, b, c, d = d, -b, -c, a
        x = a * p + b * q
        y = c * p + d * q
        return (x / det, y / det)


class Ray:
    """Represents a line segment (bounded portion of a line)"""
    
    def __init__(self, line, condition):
        """
        Initialize a ray with a line and boundary condition.
        
        Args:
            line: Line object
            condition: function(p) -> bool that checks if point is within bounds
        """
        self.line = line
        self.condition = condition
    
    def has(self, p):
        """Check if point p lies on this ray (on line AND within bounds)"""
        if not p:
            return False
        if not self.line.has(p):
            return False
        return self.condition(p)
    
    def inter(self, ray):
        """
        Check if this ray intersects with another ray.
        
        Returns:
            True if rays intersect, False otherwise
        """
        inter = self.line.inter(ray.line)
        if not inter:
            return False
        return self.has(inter) and ray.has(inter)


class Polygon:
    """Represents a polygon defined by its vertices"""
    
    def __init__(self, vertices, epsilon=1e-3):
        """
        Initialize a polygon with vertices.
        
        Args:
            vertices: List of (x, y) tuples
            epsilon: tolerance for floating point comparisons in Line operations
        """
        self.epsilon = epsilon
        
        # Build edges as rays from vertices
        self.edges = []
        n = len(vertices)
        
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            
            line = Line((x1, y1), (x2, y2), epsilon=self.epsilon)
            
            # Create condition for ray based on edge direction
            if x1 == x2:
                # Vertical edge: y must be in range
                def condition(p, Y1=y1, Y2=y2):
                    _, y = p
                    return min(Y1, Y2) <= y <= max(Y1, Y2)
            elif y1 == y2:
                # Horizontal edge: x must be in range
                def condition(p, X1=x1, X2=x2):
                    x, _ = p
                    return min(X1, X2) <= x <= max(X1, X2)
            else:
                # Diagonal edge: both x and y must be in range
                def condition(p, X1=x1, X2=x2, Y1=y1, Y2=y2):
                    x, y = p
                    return (min(X1, X2) <= x <= max(X1, X2) and 
                            min(Y1, Y2) <= y <= max(Y1, Y2))
            
            self.edges.append(Ray(line, condition))
    
    @cache
    def inside(self, p):
        """
        Check if point p is inside the polygon using ray casting algorithm.
        
        Args:
            p: (x, y) tuple
            
        Returns:
            True if point is inside polygon, False otherwise
        """
        x, y = p
        
        # Cast rays in four cardinal directions from the point
        # A point is inside if all four rays intersect at least one edge
        rays = [
            Ray(Line(p, (x - 10, y), epsilon=self.epsilon), 
                lambda p1, X=x: p1[0] <= X),  # Left
            Ray(Line(p, (x, y + 10), epsilon=self.epsilon), 
                lambda p1, Y=y: p1[1] >= Y),  # Up
            Ray(Line(p, (x + 10, y), epsilon=self.epsilon), 
                lambda p1, X=x: p1[0] >= X),  # Right
            Ray(Line(p, (x, y - 10), epsilon=self.epsilon), 
                lambda p1, Y=y: p1[1] <= Y)   # Down
        ]
        
        hits = [0, 0, 0, 0]
        for edge in self.edges:
            for i, ray in enumerate(rays):
                if ray.inter(edge):
                    hits[i] = 1
            # Early exit if all rays hit
            if sum(hits) == 4:
                return True
        
        return sum(hits) == 4