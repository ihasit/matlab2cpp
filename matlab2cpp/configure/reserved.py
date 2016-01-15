Var_i = "cx_double"
Get_linspace = "rowvec"

def Get_abs(node):
    node.type = node[0].type

def Get_any(node):
    if not node[0].num:
        return

    node.type = node[0].type

    # colvec or rowvec
    if node.dim in (1,2):
        node.dim = 0

    # matrix
    elif node.dim == 3:

        # axis input decides by second input
        if len(node) == 2:

            if  node[1].cls == "Int":
                val = node[1].value
                if val == "1":
                    node.dim = 2
                elif val == "2":
                    node.dim = 1

            # problem if arg not explicit
            else:
                node.num = False

    # cube
    else:
        node.dim = 3

Get_all = Get_any

def Get_size(node):

    # unknown input
    if node[0].type == "TYPE" or node.parent.cls == "Assigns":
        return

    var = str(node[0])

    # multiple args
    if len(node) > 1:
        
        # determine ax from second arg
        node.type = "uword"

    # colvec or rowvec
    elif node[0].dim in (1,2):
        node.type = "uword"

    # matrix (returns two values)
    elif node[0].dim == 3:
        node.type = "urowvec"

        if node.parent.cls == "Get":
            return

        # inline calls moved to own line
        if node.parent.cls not in ("Statement", "Assign"):
            return

        node.parent.backend = "reserved"
        node.parent.name = "size"

    # cube (return three values)
    elif node[0].dim == 4:
        node.type = "urowvec"

        if node.parent.cls == "Get":
            return

        # inline calls moved to own line
        if node.parent.cls not in ("Statement", "Assign"):
            return

        node.parent.backend = "reserved"
        node.parent.name = "size"

def Assigns_size(node):

    # suggest some types for matrix
    if len(node)==3:
        node[0].suggest = "int"
        node[1].suggest = "int"

    # suggest some types for cube
    if len(node)==4:

        node[0].suggest = "int"
        node[1].suggest = "int"
        node[2].suggest = "int"

def Get_length(node):
    node.type = "uword"

def Get_min(node):

    # everything scalar
    if not all([n.num for n in node]) or  all([(n.dim < 2) for n in node]):
        return

    node.type = node[0].type

    # single arg
    if len(node) == 1:

        # determine node dimensions
        if node.dim == 2:
            node.dim = 0
        else:
            node.dim = node.dim-1

    # three args
    if len(node) == 3:
        if node[2].dim == 0:

            # assues third arg is int and sets axis
            val = node[2].value
            if val == "1":
                node.dim = 2
            elif val == "2":
                node.dim = 1
            else:
                node.num = False
            
def Assigns_min(node):
    assert len(node) == 3

    var = node[2][0]

    # non-numerical assignment
    if not var.num:
        pass
    else:
        node[0].suggest = (0, var.mem)
        node[1].suggest = "int"

Get_max = Get_min

def Assigns_max(node):
    assert len(node) == 3

    # right hand side of assignment
    var = node[-1]

    # non-numerical input
    if not var.num:
        pass
    else:
        node[0].suggest = (0, var.mem)
        node[1].suggest = "int"

Get_eye = "mat"
Get_diag = "mat"

def Get_transpose(node):
    """Simple transpose
    """

    # colvec -> rowvec 
    if node[0].dim == 1:
        node.type = (2, node[0].mem)

    # rowvec -> colvec
    elif node[0].dim == 2:
        node.type = (1, node[0].mem)

    else:
        node.type = node[0].type
    
def Get_ctranspose(node):
    """Complex transpose
    """

    # colvec -> rowvec 
    if node[0].dim == 1:
        node.type = (2, node[0].mem)

    # rowvec -> colvec
    elif node[0].dim == 2:
        node.type = (1, node[0].mem)

    else:
        node.type = node[0].type

def Get_zeros(node):

    node.type = "uword"
    dim, mem = node.suggest_datatype()

    # set memory type
    if not (mem is None):
        node.mem = mem
    else:
        node.mem = 3

    # reset to uword if arg of array-node
    if node.group.cls in ("Get", "Cget", "Fget", "Nget", "Sget", "Set", "Cset",
            "Fset", "Nset", "Sset") and node.group.num:
        node.mem = 0
    
    # one argument
    if len(node) == 1:

        # arg input is vector
        if node[0].num and node[0].dim in (1,2):
            pass

        else:

            # use suggestions or defualts
            if dim in (1,2,3):
                node.dim = dim
            else:
                node.dim = 1 # default

    # double argument creates colvec/rowvec/matrix depending on context
    elif len(node) == 2:

        # use matrix, if suggested
        if dim == 3:
            node.dim = 3

        # use colvec if first index is '1'
        elif node[0].cls == "Int" and node[0].value == "1":
            node.dim = 2

        # use rowvec if second index is '1'
        elif node[1].cls == "Int" and node[1].value == "1":
            node.dim = 1

        # default to matrix
        else:
            node.dim = 3

    # triple arg create cube
    elif len(node) == 3:
        node.dim = 4

Get_ones = Get_zeros

def Get_round(node):
    if len(node) == 1:
        #int, float, double, uword
        if node[0].dim == 0 and node[0].mem != 4:
            node.type = "double"
        #arma types
        elif node[0].dim != 0:
            node.type = node[0].type
Var_rand = "vec"

def Get_rand(node):

    type = node[0].type

    # unknown input
    if type == "TYPE":
        return

    # one arg -> vec
    if len(node) == 1:
        node.type = "vec"

    # two args -> mat
    elif len(node) == 2:
        node.type = "mat"

    # three args -> cube
    elif len(node) == 3:
        node.type = "cube"

def Get_floor(node):

    # unknown input
    if node[0].type == "TYPE":
        pass

    # returns int
    elif node[0].mem > 1:
        node.type = (node[0].dim, 1)

def Get_nextpow2(node):
    node.type = "int"
    
def Get_fft(node):

    node.type = node[0].type
    if node.mem == 4:
        node.mem = 3

def Get_ifft(node):

    node.type = node[0].type

    # unknown input
    if not node.num:
        pass
    else:
        node.mem = 4
    
def Get_sum(node):

    arg = node[0]

    # unknown input
    if not arg.num or arg.dim == 0:
        return

    node.type = arg.type

    # determine output dimensions
    if arg.dim == 2:
        dim = 0
    elif arg.dim == 3:
        # sum along an axis
        if len(node) == 2 and node[1].cls == "Int" and node[1].value == "2":
            dim = 1
        else:
            dim = 2
    else:
        dim = arg.dim-1
    node.dim = dim
    
def Get_real(node):
    arg = node[0]
    # output always real
    if arg.num and arg.mem == 4:
        node.type = arg.type
        node.mem = 3

Get_tic = "string"

Get_toc = "string"
