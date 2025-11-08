from itertools import product

# Default configuration constants
DEFAULT_UNIT_SIZE = 3
DEFAULT_VALUE_FILL_CHAR = "_"
DEFAULT_GAP_FILL_CHAR = "_"


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
        fillChar: The character to use for padding (uses DEFAULT_VALUE_FILL_CHAR "_" if None)
        
    Returns:
        A centered string representation of val
    """
    if unitSize is None:
        unitSize = DEFAULT_UNIT_SIZE
    if fillChar is None:
        fillChar = DEFAULT_VALUE_FILL_CHAR
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


def register(node: BinaryNode, valueFillChar=None, unitSize=None, code="", mem=None):
    """
    Recursively registers all nodes in a tree with their binary path codes.
    
    Each node is assigned a binary code representing its position:
    - Empty string "" for root
    - "0" appended for left child
    - "1" appended for right child
    
    Args:
        node: The current node being processed
        valueFillChar: Character used for padding node values (uses DEFAULT_VALUE_FILL_CHAR "_" if None)
        unitSize: Size for centering values (uses DEFAULT_UNIT_SIZE if None)
        code: The binary path code for the current node
        mem: Dictionary mapping binary codes to centered node values
    """
    if mem is None:
        mem = {}
    if node:
        mem[code] = center(node.val, unitSize=unitSize, fillChar=valueFillChar)
        register(node.left, valueFillChar=valueFillChar, unitSize=unitSize, code=code + "0", mem=mem)
        register(node.right, valueFillChar=valueFillChar, unitSize=unitSize, code=code + "1", mem=mem)
    return mem


def nodeToMat(node: BinaryNode, depth=-1, valueFillChar=None, gapFillChar=None, unitSize=None, removeEmpty=True):
    """
    Converts a binary tree into a 2D matrix representation for visualization.
    
    The matrix includes:
    - Even rows (0, 2, 4...): Node values
    - Odd rows (1, 3, 5...): Connection lines (/ and \\)
    
    Args:
        node: The root node of the tree to visualize
        depth: The depth of the tree (-1 for auto-calculation)
        valueFillChar: Character for padding node values (uses DEFAULT_VALUE_FILL_CHAR "_" if None)
        gapFillChar: Character for filling gaps between pairs (uses DEFAULT_GAP_FILL_CHAR "_" if None)
        unitSize: Size for centering (uses DEFAULT_UNIT_SIZE if None)
        removeEmpty: Whether to remove empty leading columns
        
    Returns:
        A 2D list (matrix) representing the tree structure
    """
    if unitSize is None:
        unitSize = DEFAULT_UNIT_SIZE
    if valueFillChar is None:
        valueFillChar = DEFAULT_VALUE_FILL_CHAR
    if gapFillChar is None:
        gapFillChar = DEFAULT_GAP_FILL_CHAR
    
    if depth == -1:
        depth = getDepth(node)
    
    # Register all nodes with their binary path codes
    tree = register(node, valueFillChar=valueFillChar, unitSize=unitSize, code="", mem={})
    
    # Create matrix: (2*depth - 1) rows x (2^depth - 1) columns
    # Initialize with space-centered empty cells
    mat = [[center("", unitSize=unitSize, fillChar=" ") for _ in range(2 ** depth - 1)] for _ in range(2 * depth - 1)]
    
    # Start with all even column indices (where values can be placed)
    valueIndexes = [i for i in range(2 ** depth - 1) if i % 2 == 0]
    prev = None
    
    # Build matrix from bottom to top
    for level in range(2 * (depth - 1), -1, -1):
        # Odd levels: place connection characters (/ and \)
        if level % 2 != 0:
            for i, index in enumerate(valueIndexes):
                mat[level][index] = [center("/", unitSize=unitSize, fillChar=" "), center("\\", unitSize=unitSize, fillChar=" ")][i % 2]
            
            # Fill gaps between pairs on the even level below (level + 1)
            for i in range(0, len(valueIndexes), 2):
                if i + 1 < len(valueIndexes):
                    # Calculate parent position (should not be overwritten)
                    parent_col = (valueIndexes[i] + valueIndexes[i + 1]) // 2
                    # Fill columns between valueIndexes[i] and valueIndexes[i+1], except parent
                    for col in range(valueIndexes[i] + 1, valueIndexes[i + 1]):
                        if col != parent_col:
                            mat[level + 1][col] = center("", unitSize=unitSize, fillChar=gapFillChar)
            
            # Calculate parent positions (midpoints between child pairs)
            next = []
            for i in range(0, len(valueIndexes) - 1, 2):
                next.append((valueIndexes[i] + valueIndexes[i + 1]) // 2)
            prev = valueIndexes
            valueIndexes = next
            continue
        
        # Even levels: place node values
        # Generate all binary codes for current level
        codes = list(product(*["01" for _ in range(level // 2)]))
        codes = ["".join(code) for code in codes]
        
        for i, index in enumerate(valueIndexes):
            if codes[i] in tree:
                mat[level][index] = tree[codes[i]]
    
    # Remove empty leading columns if requested
    if removeEmpty:
        centeredSpace = center("", unitSize=unitSize, fillChar=" ")
        centeredSlash = center("/", unitSize=unitSize, fillChar=" ")
        centeredBackslash = center("\\", unitSize=unitSize, fillChar=" ")
        
        for i in range(2 ** depth - 1):
            remove = False
            if all(
                mat[j][i] in [centeredSpace, centeredSlash, centeredBackslash]
                for j in range(2 * depth - 1)
            ):
                remove = True
            if not remove:
                break
            for j in range(2 * depth - 1):
                mat[j][i] = ""
    
    return mat


def nodeToString(node: BinaryNode, depth=-1, valueFillChar=None, gapFillChar=None, unitSize=None, removeEmpty=True):
    """
    Converts a binary tree into a string representation for visualization.
    
    Args:
        node: The root node of the tree to visualize
        depth: The depth of the tree (-1 for auto-calculation)
        valueFillChar: Character for padding node values (uses DEFAULT_VALUE_FILL_CHAR "_" if None)
        gapFillChar: Character for filling gaps between pairs (uses DEFAULT_GAP_FILL_CHAR "_" if None)
        unitSize: Size for centering (uses DEFAULT_UNIT_SIZE if None)
        removeEmpty: Whether to remove empty leading columns
        
    Returns:
        A string representation of the tree with each row on a new line
    """
    mat = nodeToMat(node, depth=depth, valueFillChar=valueFillChar, gapFillChar=gapFillChar, unitSize=unitSize, removeEmpty=removeEmpty)
    return "\n".join("".join(row) for row in mat)