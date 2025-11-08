from itertools import product

# Default configuration constants
DEFAULT_UNIT_SIZE = 3
DEFAULT_FILL_CHAR = " "


class BinaryNode:
    """
    Represents a node in a binary tree.
    
    Args:
        val: The value stored in the node, or a list to build a tree from.
             If a list is provided, builds tree level by level from left to right.
             Use None in the list for missing nodes.
        left: Reference to the left child node (only used when val is not a list)
        right: Reference to the right child node (only used when val is not a list)
    
    Attributes:
        val: The value stored in the node
        left: Reference to the left child node
        right: Reference to the right child node
        
    Example:
        >>> # Create a single node
        >>> node = BinaryNode(5)
        >>> 
        >>> # Create a tree from a list
        >>> root = BinaryNode([1, 2, 3, 4, 5, None, 7])
        >>> # Creates:
        >>> #       1
        >>> #      / \
        >>> #     2   3
        >>> #    / \   \
        >>> #   4   5   7
    """
    def __init__(self, val=0, left=None, right=None):
        # If val is a list, build tree from it
        if isinstance(val, list):
            if not val or val[0] is None:
                raise ValueError("Cannot create tree from empty list or list starting with None")
            
            self.val = val[0]
            self.left = None
            self.right = None
            
            queue = [self]
            i = 1
            
            while queue and i < len(val):
                node = queue.pop(0)
                
                # Add left child
                if i < len(val) and val[i] is not None:
                    node.left = BinaryNode(val[i])
                    queue.append(node.left)
                i += 1
                
                # Add right child
                if i < len(val) and val[i] is not None:
                    node.right = BinaryNode(val[i])
                    queue.append(node.right)
                i += 1
        else:
            self.val = val
            self.left = left
            self.right = right
    
    def __str__(self):
        return str(self.val)
    
    def __repr__(self):
        return str(self)

def center(val, unitSize=None, fillChar=None):
    """
    Centers a value within a fixed width string.
    
    Args:
        val: The value to center
        unitSize: The total width of the output string (uses DEFAULT_UNIT_SIZE if None)
        fillChar: The character to use for padding (uses DEFAULT_FILL_CHAR if None)
        
    Returns:
        A centered string representation of val
    """
    if unitSize is None:
        unitSize = DEFAULT_UNIT_SIZE
    if fillChar is None:
        fillChar = DEFAULT_FILL_CHAR
    return str(val).center(unitSize, fillChar)


def getDepth(node: BinaryNode):
    """
    Calculates the depth (height) of a binary tree.
    
    Args:
        node: The root node of the tree
        
    Returns:
        The depth of the tree (number of levels from root to deepest leaf)
    """
    if node == None:
        return 0
    return 1 + max(getDepth(node.left), getDepth(node.right))


def register(node: BinaryNode, fillChar=None, unitSize=None, code="", mem=None):
    """
    Recursively registers all nodes in a tree with their binary path codes.
    
    Each node is assigned a binary code representing its position:
    - Empty string "" for root
    - "0" appended for left child
    - "1" appended for right child
    
    Args:
        node: The current node being processed
        fillChar: Character used for padding (uses DEFAULT_FILL_CHAR if None)
        unitSize: Size for centering values (uses DEFAULT_UNIT_SIZE if None)
        code: The binary path code for the current node
        mem: Dictionary mapping binary codes to centered node values
    """
    if mem is None:
        mem = {}
    if node:
        mem[code] = center(node.val, unitSize=unitSize, fillChar=fillChar)
        register(node.left, fillChar=fillChar, unitSize=unitSize, code=code + "0", mem=mem)
        register(node.right, fillChar=fillChar, unitSize=unitSize, code=code + "1", mem=mem)
    return mem


def nodeToMat(node: BinaryNode, depth=-1, fillChar=None, unitSize=None, removeEmpty=True):
    """
    Converts a binary tree into a 2D matrix representation for visualization.
    
    The matrix includes:
    - Even rows (0, 2, 4...): Node values
    - Odd rows (1, 3, 5...): Connection lines (/ and \\)
    
    Args:
        node: The root node of the tree to visualize
        depth: The depth of the tree (-1 for auto-calculation)
        fillChar: Character for padding (uses DEFAULT_FILL_CHAR if None)
        unitSize: Size for centering (uses DEFAULT_UNIT_SIZE if None)
        removeEmpty: Whether to remove empty leading columns
        
    Returns:
        A 2D list (matrix) representing the tree structure
    """
    if unitSize is None:
        unitSize = DEFAULT_UNIT_SIZE
    if fillChar is None:
        fillChar = DEFAULT_FILL_CHAR
    
    if depth == -1:
        depth = getDepth(node)
    
    # Register all nodes with their binary path codes
    tree = register(node, fillChar=fillChar, unitSize=unitSize, code="", mem={})
    
    # Create matrix: (2*depth - 1) rows x (2^depth - 1) columns
    mat = [[center("", unitSize=unitSize, fillChar=fillChar) for _ in range(2 ** depth - 1)] for _ in range(2 * depth - 1)]
    
    # Start with all even column indices (where values can be placed)
    valueIndexes = [i for i in range(2 ** depth - 1) if i % 2 == 0]
    
    # Build matrix from bottom to top
    for level in range(2 * (depth - 1), -1, -1):
        # Odd levels: place connection characters (/ and \)
        if level % 2 != 0:
            for i, index in enumerate(valueIndexes):
                mat[level][index] = [center("/", unitSize=unitSize, fillChar=fillChar), center("\\", unitSize=unitSize, fillChar=fillChar)][i % 2]
            
            # Calculate parent positions (midpoints between child pairs)
            newIndexes = []
            for i in range(0, len(valueIndexes) - 1, 2):
                newIndexes.append((valueIndexes[i] + valueIndexes[i + 1]) // 2)
            valueIndexes = newIndexes
            continue
        
        # Even levels: place node values
        # Generate all binary codes for current level
        codes = list(product(*["01" for _ in range(level // 2)]))
        codes = ["".join(code) for code in codes]
        
        for i, index in enumerate(valueIndexes):
            mat[level][index] = tree.get(codes[i], center("", unitSize=unitSize, fillChar=fillChar))
    
    # Remove empty leading columns if requested
    if removeEmpty:
        for i in range(2 ** depth - 1):
            remove = False
            if all(
                mat[j][i] in [
                    center("", unitSize=unitSize, fillChar=fillChar),
                    center("/", unitSize=unitSize, fillChar=fillChar),
                    center("\\", unitSize=unitSize, fillChar=fillChar)
                ] for j in range(2 * depth - 1)
            ):
                remove = True
            if not remove:
                break
            for j in range(2 * depth - 1):
                mat[j][i] = ""
    
    return mat


def nodeToString(node: BinaryNode, depth=-1, fillChar=None, unitSize=None, removeEmpty=True):
    """
    Converts a binary tree into a string representation for visualization.
    
    Args:
        node: The root node of the tree to visualize
        depth: The depth of the tree (-1 for auto-calculation)
        fillChar: Character for padding (uses DEFAULT_FILL_CHAR if None)
        unitSize: Size for centering (uses DEFAULT_UNIT_SIZE if None)
        removeEmpty: Whether to remove empty leading columns
        
    Returns:
        A string representation of the tree with each row on a new line
    """
    mat = nodeToMat(node, depth=depth, fillChar=fillChar, unitSize=unitSize, removeEmpty=removeEmpty)
    return "\n".join("".join(row) for row in mat)
