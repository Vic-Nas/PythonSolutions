from itertools import product

# Default configuration constants
DEFAULT_UNIT_SIZE = 3
DEFAULT_VALUE_FILL_CHAR = "_"  # Character used to pad node values (e.g., "_5_")
DEFAULT_CONNECTOR_FILL_CHAR = "_"  # Character used to fill horizontal gaps between node pairs


class BinaryNode:
    """
    Represents a node in a binary tree.
    
    Args:
        val: The value stored in the node, or a list to build a tree from.
             If a list is provided, builds tree level by level from left to right.
             Use None in the list for missing nodes.
        left: Reference to the left child node (only used when val is not a list)
        right: Reference to the right child node (only used when val is not a list)
    
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
    """Centers a value within a fixed width string."""
    if unitSize is None:
        unitSize = DEFAULT_UNIT_SIZE
    if fillChar is None:
        fillChar = DEFAULT_VALUE_FILL_CHAR
    return str(val).center(unitSize, fillChar)


def getDepth(node: BinaryNode):
    """Calculates the depth (height) of a binary tree."""
    if node is None:
        return 0
    return 1 + max(getDepth(node.left), getDepth(node.right))


def mapNodesToCodes(node, valueFillChar, unitSize, code="", memo=None):
    """
    Recursively maps all nodes to their binary path codes.
    
    Each node is assigned a binary code representing its position:
    - Empty string "" for root
    - "0" appended for left child
    - "1" appended for right child
    
    Returns:
        Dictionary mapping binary codes to centered node values
    """
    if memo is None:
        memo = {}
    if node:
        memo[code] = center(node.val, unitSize=unitSize, fillChar=valueFillChar)
        mapNodesToCodes(node.left, valueFillChar, unitSize, code + "0", memo)
        mapNodesToCodes(node.right, valueFillChar, unitSize, code + "1", memo)
    return memo


def nodeToMat(node: BinaryNode, depth=-1, valueFillChar=None, connectorFillChar=None, unitSize=None, removeEmpty=True):
    """
    Converts a binary tree into a 2D matrix representation for visualization.
    
    The matrix includes:
    - Even rows (0, 2, 4...): Node values
    - Odd rows (1, 3, 5...): Connection lines (/ and \\)
    
    Args:
        node: The root node of the tree to visualize
        depth: The depth of the tree (-1 for auto-calculation)
        valueFillChar: Character for padding node values (e.g., "_5_")
        connectorFillChar: Character for filling horizontal gaps between node pairs
        unitSize: Size for centering values
        removeEmpty: Whether to remove empty leading columns
    """
    if unitSize is None:
        unitSize = DEFAULT_UNIT_SIZE
    if valueFillChar is None:
        valueFillChar = DEFAULT_VALUE_FILL_CHAR
    if connectorFillChar is None:
        connectorFillChar = DEFAULT_CONNECTOR_FILL_CHAR
    
    if depth == -1:
        depth = getDepth(node)
    
    # Map all nodes to their binary path codes
    tree = mapNodesToCodes(node, valueFillChar, unitSize)
    
    # Cache frequently used values
    numCols = 2 ** depth - 1  # Number of leaf positions (columns)
    numRows = 2 * depth - 1   # Total rows (values + connectors)
    
    # Initialize matrix with space-centered empty cells
    mat = [[center("", unitSize=unitSize, fillChar=" ") for _ in range(numCols)] for _ in range(numRows)]
    
    # Start with all even column indices (where values can be placed)
    valueIndexes = [i for i in range(numCols) if i % 2 == 0]
    prevValueIndexes = None
    
    # Build matrix from bottom to top
    for level in range(numRows - 1, -1, -1):
        # Odd levels: place connection characters (/ and \)
        if level % 2 != 0:
            for i, index in enumerate(valueIndexes):
                mat[level][index] = [center("/", unitSize=unitSize, fillChar=" "), 
                                    center("\\", unitSize=unitSize, fillChar=" ")][i % 2]
            
            # Calculate parent positions (midpoints between child pairs)
            nextValueIndexes = []
            for i in range(0, len(valueIndexes) - 1, 2):
                nextValueIndexes.append((valueIndexes[i] + valueIndexes[i + 1]) // 2)
            valueIndexes = nextValueIndexes
            continue
        
        # Even levels: place node values
        # Generate all binary codes for current level
        codes = list(product(*["01" for _ in range(level // 2)]))
        codes = ["".join(code) for code in codes]
        
        for i, index in enumerate(valueIndexes):
            if codes[i] in tree:
                mat[level][index] = tree[codes[i]]
        
        # Fill horizontal gaps between node pairs using connectorFillChar
        if prevValueIndexes is not None:
            for i in range(0, len(prevValueIndexes), 2):
                if i + 1 < len(prevValueIndexes):
                    # Calculate parent position (should not be overwritten)
                    parentCol = (prevValueIndexes[i] + prevValueIndexes[i + 1]) // 2
                    # Fill columns between children (inclusive), except parent position
                    for col in range(prevValueIndexes[i], prevValueIndexes[i + 1] + 1):
                        if col != parentCol:
                            mat[level][col] = center("", unitSize=unitSize, fillChar=connectorFillChar)
        
        # Save current valueIndexes for next even level
        prevValueIndexes = valueIndexes
    
    # Remove empty leading columns if requested
    if removeEmpty:
        centeredSpace = center("", unitSize=unitSize, fillChar=" ")
        centeredSlash = center("/", unitSize=unitSize, fillChar=" ")
        centeredBackslash = center("\\", unitSize=unitSize, fillChar=" ")
        
        for i in range(numCols):
            remove = all(
                mat[j][i] in [centeredSpace, centeredSlash, centeredBackslash]
                for j in range(numRows)
            )
            if not remove:
                break
            for j in range(numRows):
                mat[j][i] = ""
    
    return mat


def nodeToString(node: BinaryNode, depth=-1, valueFillChar=None, connectorFillChar=None, unitSize=None, removeEmpty=True, showConnectors=True):
    """
    Converts a binary tree into a string representation for visualization.
    
    Args:
        node: The root node of the tree to visualize
        depth: The depth of the tree (-1 for auto-calculation)
        valueFillChar: Character for padding node values (e.g., "_5_")
        connectorFillChar: Character for filling horizontal gaps between node pairs
        unitSize: Size for centering values
        removeEmpty: Whether to remove empty leading columns
        showConnectors: Whether to show connector lines (/ and \) between nodes
    """
    mat = nodeToMat(node, depth=depth, valueFillChar=valueFillChar, 
                    connectorFillChar=connectorFillChar, unitSize=unitSize, removeEmpty=removeEmpty)
    
    if showConnectors:
        return "\n".join("".join(row) for row in mat)
    else:
        # Only include even rows (node values, skip odd rows with connectors)
        return "\n".join("".join(mat[i]) for i in range(0, len(mat), 2))