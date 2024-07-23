# %%
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import plotly.graph_objects as go   
import plotly.io as pio
from plotly.subplots import make_subplots

COLORS = [(0,0,1), (1,0,0), (0,0.6,0.25)]
MAX_TIKZ_COLORS = 5

class mess:   
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'  # regular, 93m for high intensity
    BLUE = '\033[94m'
    PURPLE = '\033[95m'

class RectangularCuboid():
    """Geometrical rectangular cuboid in Euclidian space (x, y, z)
    Its origin is the bottom left corner of the back face.
    This class is mainly used to display any parallelepipedic shaped object.

    Attributes:
        pos {array of 3 floats} -- coordinates of its origin.
        dim {array of 3 floats} -- dimension resp. along the x, y and z-axis
            (length, width and height)
    """    

    def __init__(self, pos, dim):      
        self.pos = pos
        self.dim = dim

    @property
    def vertices(self):
        """Generate the coordinates of the 8 vertices of the cuboid.
        
        Returns:
            {list of 8 coord.} -- list of vertices
        """        
        x, y, z = self.pos
        w, l, h = self.dim
        return np.array([[x, y, z], [x, y+l, z], [x+w, y+l, z],[x+w, y, z],
                [x, y, z+h], [x, y+l, z+h], [x+w, y+l, z+h], [x+w, y, z+h]])
    
    @property
    def faces(self):
        """Generate the 6 faces of the cuboid.
        Each face is defined by a list of its 4 vertices.
        
        Returns:
            {list of 6 faces} -- list of faces
        """        
        vertices = self.vertices
        return [[vertices[0], vertices[1], vertices[2], vertices[3]],
                [vertices[0], vertices[1], vertices[5], vertices[4]],
                [vertices[1], vertices[2], vertices[6], vertices[5]],
                [vertices[2], vertices[3], vertices[7], vertices[6]],
                [vertices[3], vertices[0], vertices[4], vertices[7]],
                [vertices[4], vertices[5], vertices[6], vertices[7]]]

    def draw(self, ax, color_vertices=(0,0,1), color_faces=(0.7,0.7,0.7)):
        """Draw the rectangular cuboid in a given matplotlib.pyplot.axes.
        
        Arguments:
            ax {plt.axes} -- Axes in which the cuboid will be drawn
            color_vertices {tuple} -- RGB color of the vertices (default: {(0,0,1)})
            color_faces {tuple} -- RGB color of the faces (default: {(0.7,0.7,0.7)})
        """        
        faces = Poly3DCollection(self.faces, linestyle = '-', linewidths=1,
            edgecolors=color_vertices, facecolor=(color_faces))
        ax.add_collection3d(faces)
        # Plot the points themselves to force the scaling of the axes
        # vertices = self.verticesx
        # ax.scatter(vertices[:,0], vertices[:,1], vertices[:,2], s=0)

  
class Box():
    """Physical box that will be loaded into a container. Represent a feasible
    orientation of a given BoxType.
    
    Attributes:
        dim {list of 3 floats} -- dimension along the x, y and z-axis
        type {BoxType} -- type of the box
    """    
    def __init__(self, dim, boxtype):
        """[TODO] Check that dim is allowed by the boxtype"""
        self.dim = np.array(dim)
        self.type = boxtype

    @property
    def volume(self):        
        return np.prod(self.dim)

    @property
    def weight(self):
        return self.type.weight

    def __repr__(self):
        return f"{mess.YELLOW}{'·'.join([str(d) for d in self.dim])}{mess.END}, Weight: {self.weight}"

    def draw(self, pos, ax):
        RectangularCuboid(pos, self.dim).draw(ax, self.type.color, self.type.color + (0.1,))


class BoxType():
    """Boxes that share the same dimensions and possible orientations are
    grouped into BoxTypes.

    Arguments:
        size {list of 3 floats} -- cf. Attributes
        permutation {list of 3 booleans} -- represents the allowed orientation
            if permutation[i], then the vertical alignment (z-axis) of the
            i-th dimension is allowed ;
            otherwise, the i-th dimension cannot be aligned with the z-axis

    Attributes:
        size {list of 3 floats} -- dimension of the Boxes, regardless of the orientation
        id {int} -- index for identifying types
        color {tuple} -- RGB color used to draw a Box
        permuted_boxes {list of Boxes} -- All possible orientation of a BoxType
        weight {float} -- weight of a single box
    """    
    id = 0
    def __init__(self, size, permutation=[0,0,1], weight=1.0,name="box"):
        assert len(permutation) == 3, "permutation must be a list of 3 items"
        assert permutation[2] == 1, "the vertical alignment of the z-axis must be allowed"
        self.name=name
        self.size = np.array(size)
        self.id = BoxType.id
        BoxType.id += 1
        self.color = COLORS[self.id % len(COLORS)]
        self.weight = weight
        
        # Set all permutation allowed
        orientations = [(self.size[[2,1,0]], self.size[[1,2,0]]),
                        (self.size[[0,2,1]], self.size[[2,0,1]]),
                        (self.size[[0,1,2]], self.size[[1,0,2]])] # height of box kept along z axis
        self.permuted_boxes = []
        for i, vertical_alignment_allowed in enumerate(permutation):
            if vertical_alignment_allowed:
                self.permuted_boxes.append(Box(orientations[i][0], self))
                self.permuted_boxes.append(Box(orientations[i][1], self))         
    
    def __repr__(self):
        return f"({self.id}) {mess.YELLOW}{'·'.join([str(d) for d in self.size])}{mess.END}, Weight: {self.weight}"

class Block():      
    """A Block is a composition of Boxes of the same BoxType.
    
    Attributes:
        box {Box} -- Box of which the Block is composed
        N {triplet of ints} -- N[0] is the number of boxes along the x-axis,
            so that N[0]*N[1]*N[2] is the total number of boxes in the block
        pos {coord.} -- position of the Block (i.e. of its bottom back left corner)
    """    
    def __init__(self, box, N, space):
        self.box = box
        self.N = np.array(N)
        # self.space = space
        self.pos = space.pos
    
    @property
    def dim(self):
        """Dimensions of the Block"""        
        return self.N * self.box.dim

    @property
    def Ntot(self):
        """Number of Boxes inside the Block"""
        return np.prod(self.N)

    @property
    def volume(self):
        """Volume of the Block"""
        return self.Ntot * self.box.volume

    def __gt__(self, other):
        return self.volume > other.volume

    def __repr__(self):
        return (mess.GREEN +
                'x'.join(str(n) for n in self.N) + ' ' +
                mess.YELLOW +
                '·'.join([str(d) for d in self.box.dim]) +
                mess.BLUE +
                ' (' + str(self.pos)[1:-1].replace(', ', ' ') + ')' +
                mess.END)
    
    def draw(self, ax):
        for n in np.ndindex(*self.N):
            self.box.draw(n * self.box.dim + self.pos, ax)

    

class Space():
    """Empty cuboidal space, which we are trying to fill with Blocks (of Boxes).
    
    Attributes:
        pos {array of 3 floats} -- coordinates of its origin.
        dim {array of 3 floats} -- dimension resp. along the x, y and z-axis
    """
    def __init__(self, pos, dim):
        self.dim = np.array(dim)
        self.pos = np.array(pos)
    
    def find_max_blocks(self, cargo):
        """Given a set of BoxTypes (cargo), find all maximal Blocks that can
        fill the Space. (i.e. for each BoxType b in quantity q, find the biggest
        Block that can fit into the Space)
        
        Arguments:
            cargo {dict[BoxType,int]} -- available BoxTypes (key) and their quantity (value)
        
        Returns:
            blocks {list[Blocks]} -- maximal Blocks that can fit into the Space
        """        
        blocks = []
        for boxtype, q in cargo.items():
            for box in boxtype.permuted_boxes:
                Nmax = 3*[0]
                if (q != 0) and np.all(self.dim >= box.dim):
                    Nmax[2] = min(int(self.dim[2] / box.dim[2]), q)
                    Nmax[1] = min(int(self.dim[1] / box.dim[1]), int(q / Nmax[2]))
                    Nmax[0] = min(int(self.dim[0] / box.dim[0]), int(q / (Nmax[2]*Nmax[1])))
                    blocks.append(Block(box, Nmax, self))
        return blocks
    
    def split(self, block):
        """Return the 3 new spaces generated after the loading of a block into
        the Space
        
        Arguments:
            block {Block} -- Block that will be loaded into the Space
        
        Returns:
            spaces {list of 3 Spaces} -- [side space, top space, front space]
        """
        spaces = []
        sp0, sp1, sp2 = self.pos
        bd0, bd1, bd2 = block.dim
        sd0, sd1, sd2 = self.dim
        
        # Create side space
        side_space_pos = [sp0, sp1 + bd1, sp2]
        side_space_dim = [bd0, sd1 - bd1, sd2]
        spaces.append(Space(side_space_pos, side_space_dim))
        
        """ # Create top space   - commented out since only allowed to stack similar boxes on top of each other
        top_space_pos = [sp0, sp1, sp2 + bd2]
        top_space_dim = [bd0, bd1, sd2 - bd2]
        spaces.append(Space(top_space_pos, top_space_dim)) """
        
        # Create front space
        front_space_pos = [sp0 + bd0, sp1, sp2]
        front_space_dim = [sd0 - bd0, sd1, sd2]
        spaces.append(Space(front_space_pos, front_space_dim))
        
        return spaces
    
    def distance(self):
        """Distance to the origin"""        
        return np.sqrt(np.sum(np.square(self.pos)))

    def __eq__(self, other):
        return all(self.dim == other.dim) and all(self.pos == other.pos)

    def __repr__(self):
        return mess.YELLOW + '·'.join([str(d) for d in self.dim]) + mess.BLUE + ' (' + str(self.pos)[1:-1].replace(', ', ' ') +')' + mess.END

    def draw(self, ax):
        ax.scatter(*[[x, max(self.dim)] for x in self.pos], s=0)
        RectangularCuboid(self.pos, self.dim).draw(ax, (0.7,0.7,0.7,1), (1,1,1,0))

class Container():
    """Container in which boxes must be loaded.
    Container is described as a set of Spaces and Blocks.
    
    Attributes:
        dim {list of 3 floats} -- dimension resp. along x, y and z-axis
        cargo {dict[BoxType,int]} -- Boxtypes (and their quantity) that still
        blocks {list of Blocks} -- Blocks of boxes that have been loaded
        spaces {list of Space} -- the remaining spaces that can be filled
    """    
    def __init__(self, dim, cargo,max_weight=12500):
        self.dim = np.array(dim)
        self.spaces = [Space([0,0,0], self.dim)]
        self.blocks = []
        self.cargo = cargo
        self.boxtypes = list(cargo.keys())
        self.max_weight=max_weight
        self.current_weight = 0  # Initialize current weight of loaded boxes
    
    @property
    def volume(self):
        return np.prod(self.dim)

    def fill(self, eval=max):
        """[Round-robin] Select and fill one Block inside the Container
        
        Keyword Arguments:
            eval {function} -- Function to select one Block among a set
                of Blocks (default: {max})
        """
        if not self.spaces:
            return False
        
        self.spaces = sorted(self.spaces, key=Space.distance)
        space = self.spaces.pop(0)
        
        blocks_possible = []
        for boxtype in self.boxtypes:
            if self.cargo[boxtype] > 0:
                blocks_possible.extend(space.find_max_blocks({boxtype: self.cargo[boxtype]}))
        
        if blocks_possible:
            new_block = eval(blocks_possible)
            
            # Calculate weight of the new block
            block_weight = new_block.box.weight * new_block.Ntot
            
            if self.current_weight + block_weight <= self.max_weight:  # Check weight constraint
                new_spaces = space.split(new_block)
                self.spaces.extend(new_spaces)
                self.blocks.append(new_block)
                self.cargo[new_block.box.type] -= new_block.Ntot
                self.current_weight += block_weight  # Update current weight
                
                # Print available spaces after placing the block
                print("Available spaces after placing block:")
                for s in self.spaces:
                    print(f"Position: {s.pos}, Dimensions: {s.dim}")
                
                return True
        
        self.spaces.insert(0, space)  # Reinsert the space if no block is added
        return False

    def fill_all(self):
        """Fill the entire container using the fill method until all spaces are exhausted"""
        while self.spaces:
            self.spaces = sorted(self.spaces, key=Space.distance)
            space = self.spaces.pop(0)
            
            blocks_possible = []
            for boxtype in self.boxtypes:
                if self.cargo[boxtype] > 0:
                    blocks_possible.extend(space.find_max_blocks({boxtype: self.cargo[boxtype]}))
            
            
            if blocks_possible:
            
                # Sort blocks by volume in descending order
                blocks_possible.sort(key=lambda block: block.volume, reverse=True)
                
                # Try to place the largest block that fits
                block_placed = False
                for block in blocks_possible:
                    if space.dim[0] >= block.dim[0] and space.dim[1] >= block.dim[1] and space.dim[2] >= block.dim[2]:
                        # Calculate weight of the new block
                        block_weight = block.box.weight * block.Ntot
                        
                        if self.current_weight + block_weight <= self.max_weight:  # Check weight constraint
                            new_spaces = space.split(block)
                            self.spaces.extend(new_spaces)
                            self.blocks.append(block)
                            self.cargo[block.box.type] -= block.Ntot
                            self.current_weight += block_weight  # Update current weight
                            block_placed = True
                            
                            print(f"Placed {block.Ntot} boxes of type {block.box.type} in block {block}")
                            print(f"Container weight is{self.current_weight}")
                            
                            # Print remaining quantities of each box type
                            remaining_boxes = {boxtype: self.cargo[boxtype] for boxtype in self.boxtypes}
                            print(f"Remaining boxes: {remaining_boxes}")
                            
                            break  # Exit loop once a block is placed
                
                if not block_placed:
                    remaining_weight = self.max_weight - self.current_weight
                    box_weight = block.box.weight  # Assuming block.box.weight gives the weight of one box

                    # Calculate the maximum number of boxes that can be added
                    max_boxes_to_add = remaining_weight // box_weight

                    if max_boxes_to_add > 0:
                        # Create a new block with the maximum number of boxes that can be added
                        boxes_to_add = min(max_boxes_to_add, block.Ntot)  # Ensure we do not exceed the number of boxes in the block
                        
                        # Calculate the new dimensions for the block based on the number of boxes to add
                        new_N = np.array(block.N)
                        total_boxes_in_block = np.prod(block.N)
                        reduction_factor = boxes_to_add / total_boxes_in_block

                        # Adjust the dimensions proportionally (assuming uniform reduction)
                        new_N = np.round(new_N * (reduction_factor ** (1/3))).astype(int)
                        
                        # Create a new block with the adjusted dimensions
                        new_block = Block(box=block.box, N=new_N, space=space)

                        # Split the space and update container state
                        new_spaces = space.split(new_block)
                        self.spaces.extend(new_spaces)
                        self.blocks.append(new_block)
                        self.cargo[new_block.box.type] -= new_block.Ntot
                        self.current_weight += boxes_to_add * box_weight  # Update current weight
                        block_placed = True
                    else:
                        self.spaces.insert(0, space)  # Reinsert the space if no boxes can be added
                        print(f"Container weight is {self.current_weight}")
                        remaining_boxes = {boxtype: self.cargo[boxtype] for boxtype in self.boxtypes}
                        print(f"Remaining boxes: {remaining_boxes}")
                        print("No more blocks can fit in this space.")
                        break
            else:
                print("No more blocks can be added.")
                
    def __repr__(self):
        s = str(self.cargo)
        for b in self.blocks:
            s += "({b.box.type.id})" + mess.GREEN + 'x'.join(str(n) for n in b.N) + mess.END +', '
        for f in self.spaces:
            s += mess.YELLOW + '·'.join([str(d) for d in f.dim]) + mess.END + ', '
        return s
        
    def draw(self):
        fig = plt.figure(figsize=plt.figaspect(1)*1.5)
        ax = fig.add_subplot(111, projection='3d')  # Create a 3D subplot
        ax.scatter(*[[0, max(self.dim)]]*3, s=0)
        RectangularCuboid([0,0,0], self.dim).draw(ax, (0.7,0.7,0.7,1), (1,1,1,0))
        for block in self.blocks:
            block.draw(ax)
        plt.show()

def draw_rectangular_cuboid_plotly(pos, dim, fig, color_faces=(0.7, 0.7, 0.7)):
    cuboid = RectangularCuboid(pos, dim)
    for face in cuboid.faces:
        fig.add_trace(go.Mesh3d(
            x=[v[0] for v in face],
            y=[v[1] for v in face],
            z=[v[2] for v in face],
            opacity=0.5,
            color='rgba({}, {}, {}, 0.5)'.format(*[int(c * 255) for c in color_faces])
        ))

def create_box_faces(x, y, z, dx, dy, dz):
    faces = [
        [[x, y, z], [x + dx, y, z], [x + dx, y + dy, z], [x, y + dy, z]],  # bottom face
        [[x, y, z], [x + dx, y, z], [x + dx, y, z + dz], [x, y, z + dz]],  # front face
        [[x, y, z], [x, y + dy, z], [x, y + dy, z + dz], [x, y, z + dz]],  # left face
        [[x + dx, y + dy, z], [x + dx, y, z], [x + dx, y, z + dz], [x + dx, y + dy, z + dz]],  # right face
        [[x, y + dy, z], [x + dx, y + dy, z], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]],  # back face
        [[x, y, z + dz], [x + dx, y, z + dz], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]]  # top face
    ]
    edges = [
        [(x, y, z), (x + dx, y, z)],
        [(x + dx, y, z), (x + dx, y + dy, z)],
        [(x + dx, y + dy, z), (x, y + dy, z)],
        [(x, y + dy, z), (x, y, z)],
        [(x, y, z + dz), (x + dx, y, z + dz)],
        [(x + dx, y, z + dz), (x + dx, y + dy, z + dz)],
        [(x + dx, y + dy, z + dz), (x, y + dy, z + dz)],
        [(x, y + dy, z + dz), (x, y, z + dz)],
        [(x, y, z), (x, y, z + dz)],
        [(x + dx, y, z), (x + dx, y, z + dz)],
        [(x + dx, y + dy, z), (x + dx, y + dy, z + dz)],
        [(x, y + dy, z), (x, y + dy, z + dz)]
    ]
    return faces, edges

box_type_colors={}

def get_box_color(box_type):
    if box_type not in box_type_colors:
        # Assign a new color for this box type
        color_index = len(box_type_colors)
        box_type_colors[box_type] = f'rgb({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)})'
    return box_type_colors[box_type]

def draw_box_plotly(pos, box, fig):
    color = get_box_color(box.type)
    draw_rectangular_cuboid_plotly(pos, box.dim, fig, color_faces=color)

def draw_block_plotly(block, fig):
    for n in np.ndindex(*block.N):
        pos = n * block.box.dim + block.pos
        draw_box_plotly(pos, block.box, fig)
        # Draw edges to show individual boxes
        faces, edges = create_box_faces(pos[0], pos[1], pos[2], block.box.dim[0], block.box.dim[1], block.box.dim[2])
        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=[edge[0][0], edge[1][0]],
                y=[edge[0][1], edge[1][1]],
                z=[edge[0][2], edge[1][2]],
                mode='lines',
                line=dict(color='black', width=1)
            ))
        # Annotate dimensions
        x, y, z = pos
        dx, dy, dz = block.box.dim
        fig.add_trace(go.Scatter3d(
            x=[x + dx/2], y=[y + dy/2], z=[z + dz],
            mode='text',
            text=[f'{dx} mm'],
            textposition='bottom center',
            showlegend=False
        ))
        fig.add_trace(go.Scatter3d(
            x=[x + dx/2], y=[y + dy], z=[z + dz/2],
            mode='text',
            text=[f'{dy} mm'],
            textposition='bottom center',
            showlegend=False
        ))
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y + dy/2], z=[z + dz/2],
            mode='text',
            text=[f'{dz} mm'],
            textposition='bottom center',
            showlegend=False
        ))

def draw_space_plotly(space, fig):
    fig.add_trace(go.Scatter3d(
        x=[space.pos[0], space.pos[0]],
        y=[space.pos[1], space.pos[1] + space.dim[1]],
        z=[space.pos[2], space.pos[2]],
        mode='markers',
        marker=dict(size=0)
    ))
    draw_rectangular_cuboid_plotly(space.pos, space.dim, fig, color_faces=(0.7, 0.7, 0.7))

def render_plotly_plot(container):
    box_type_colors.clear()
    fig = go.Figure()
    
    container_vertices = [
        [0, 0, 0],
        [container.dim[0], 0, 0],
        [container.dim[0], container.dim[1], 0],
        [0, container.dim[1], 0],
        [0, 0, container.dim[2]],
        [container.dim[0], 0, container.dim[2]],
        [container.dim[0], container.dim[1], container.dim[2]],
        [0, container.dim[1], container.dim[2]]
    ]

    fig.add_trace(go.Scatter3d(
        x=[v[0] for v in container_vertices],
        y=[v[1] for v in container_vertices],
        z=[v[2] for v in container_vertices],
        mode='lines',
        line=dict(color='lightgrey', width=2),
        marker=dict(size=4)
    ))

    for block in container.blocks:
        pos = block.pos
        dim = block.dim
        box_color = get_box_color(block.box.type)

        x, y, z = pos
        dx, dy, dz = dim

        faces, edges = create_box_faces(x, y, z, dx, dy, dz)

        for face in faces:
            fig.add_trace(go.Mesh3d(
                x=[v[0] for v in face],
                y=[v[1] for v in face],
                z=[v[2] for v in face],
                color=box_color,
                opacity=0.5,
                flatshading=True
            ))

        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=[edge[0][0], edge[1][0]],
                y=[edge[0][1], edge[1][1]],
                z=[edge[0][2], edge[1][2]],
                mode='lines',
                line=dict(color='darkgreen', width=2)
            ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Length (mm)',
            yaxis_title='Width (mm)',
            zaxis_title='Height (mm)',
            xaxis=dict(nticks=10, range=[0, container.dim[0]]),
            yaxis=dict(nticks=10, range=[0, container.dim[1]]),
            zaxis=dict(nticks=10, range=[0, container.dim[2]]),
            aspectmode='data'
        ),
        title='Container with Boxes',
        autosize=False,
        width=1200,
        height=900
    )

    # Add legend
    legend_entries = []
    for box_type, color in box_type_colors.items():
        legend_entries.append(
            go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=box_type.name
            )
        )
    fig.add_traces(legend_entries)

    return fig

if __name__ == "__main__": 
    B1 = BoxType([450, 210, 210], [0, 0, 1],1,"b1")
    B2 = BoxType([355, 224, 360], [0, 0, 1],1,"b2")
    B3 = BoxType([355, 235, 360], [0, 0, 1],1,"b3")
    
    # Initialize container with cargo
    container = Container([9750, 2550, 2900], {B1: 1000, B3: 350, B2: 908})
    
    # Iteratively fill the container until no more blocks can be added
    container.fill_all()
    
    # Draw the filled container
    container.draw()
    
