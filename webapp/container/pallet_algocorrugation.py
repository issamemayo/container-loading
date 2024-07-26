import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import numpy as np

def printf_clear(log_file):
    with open(log_file, 'w') as f:
        f.write('Hi, this is the log file.\n')

def printf(log_file, *text):
    with open(log_file, 'a', newline=None) as f:
        for t in text:
            f.write(str(t))
        f.write("\n")

class Box:
    def __init__(self, _L=1, _w=1, _h=1, _weight=1,name="box",crushing_strength=70):
        self.L = _L
        self.w = _w
        self.h = _h
        self.weight = _weight
        self.name=name
        self.crushing_strength=crushing_strength

    def ask_dim(self):
        print("Please enter the following values of the box :")
        self.L = int(input("Length : "))
        self.w = int(input("Width : "))
        self.h = int(input("Height : "))

    def get_dim(self):
        return [self.L, self.w, self.h]
    
    def get_volume(self):
        return self.L * self.w * self.h

class Pallet(Box):
    def __init__(self, _L=1200, _w=1000, _h=2200):
        super().__init__(_L, _w, _h)  
        self.content = []
        self.nb_box = 0
        self.cog_height=0
        
    def add_box(self, rotation, nb_L, nb_w, nb_h):
        if (nb_L * nb_w * nb_h) > 0:
            merged = False
            for i in range(len(self.content)):
                if rotation == self.content[i][0]:
                    if (nb_L * nb_w * nb_h) > (self.content[i][1] * self.content[i][2] * self.content[i][3]):
                        self.content[i] = [rotation, nb_L, nb_w, nb_h, self]
                        self.nb_box -= self.content[i][1] * self.content[i][2] * self.content[i][3]
                        self.nb_box += nb_L * nb_w * nb_h
                    merged = True
            if not merged:
                self.content.append([rotation, nb_L, nb_w, nb_h, self])
                self.nb_box += nb_L * nb_w * nb_h

    def remove_box(self, rotation, nb_L, nb_w, nb_h, debug=False, log_file=".log"):
        if len(self.content) == 0:
            return
        try:
            self.content.remove([rotation, nb_L, nb_w, nb_h, self])
            self.nb_box -= nb_L * nb_w * nb_h
        except:
            if debug:
                printf(log_file, "failed to remove boites from the pallet" + "*" * 10)
                printf(log_file, f"{self.content=}")

    def __gt__(self, other):
        return self.nb_box > other.nb_box

    def copy(self):
        new_box = Pallet(self.L, self.w, self.h)
        new_box.content = self.content[:]
        new_box.nb_box = self.nb_box
        return new_box

    def __str__(self):
        dimensions = self.get_dim()  
        return f"Pallet :\ndimensions : {dimensions[0]}x{dimensions[1]}x{dimensions[2]}\nnb_boxes : {self.nb_box}\ncontent : {self.content}"

    def combine(self, other):
        for i in range(len(other.content)):
            self.add_box(other.content[i][0], other.content[i][1], other.content[i][2], other.content[i][3])

    def print_way_fill(self, debug=False):
        text_to_print = ""
        nb_step = 1
        text_to_print += f"Way to fill the pallet :\n{nb_step}. Position the pallet with the long side facing you.\n"
        if debug: print(f"Way to fill the pallet :\n{nb_step}. Position the pallet with the long side facing you.")
        for step in self.content:
            nb_step += 1
            rotation_text = ""
            if step[0] == 1:
                rotation_text = "flat along the length of the pallet"
            elif step[0] == 2:
                rotation_text = "flat along the width of the pallet"
            
            if debug: print(f"{nb_step}. Position (L*w*h) {step[1]}*{step[2]}*{step[3]} = {step[1] * step[2] * step[3]} box(es) " + rotation_text)
            text_to_print += f"{nb_step}. Position {step[1] * step[2] * step[3]} box(es) " + rotation_text + "\n"
        
        return text_to_print

    def print_total(self, debug=False):
        if debug:
            print(f"You have now placed {self.nb_box} box(es) in the pallet")
        text_to_print_start = f"You have now placed"
        text_to_print_bold = f" {self.nb_box} "
        text_to_print_end = f"box(es) in the pallet\n"
        return (text_to_print_start, text_to_print_bold, text_to_print_end)

def possibilities(dimensions):
    # Only rotate length and width, keeping height constant
    return [
        [dimensions[0], dimensions[1], dimensions[2]],
        [dimensions[1], dimensions[0], dimensions[2]]
    ]

def fill_pallet(_pallet, box, fill_rest=True, _previous_pallet=Pallet(), debug=False, log_file=".log"):
    best_pallet = Pallet()

    for dim in possibilities(box.get_dim()):
        pallet = _pallet.copy()
        pallet_fill_rest = []
        previous_pallet = _previous_pallet.copy()

        nb_L = pallet.L // dim[0]
        L = dim[0] * nb_L

        nb_w = pallet.w // dim[1]
        w = dim[1] * nb_w

        max_boxes_height = box.crushing_strength // box.weight + 1
        nb_h = min(pallet.h // dim[2], max_boxes_height)
        h = dim[2] * nb_h

        if debug:
            printf(log_file, f"Trying box dimensions: {dim}, nb_L={nb_L}, nb_w={nb_w}, nb_h={nb_h}")

        if not nb_L * nb_w * nb_h == 0:
            L_r = pallet.L - L
            w_r = pallet.w - w
            h_r = pallet.h - h

            pallet.add_box(1, nb_L, nb_w, nb_h)  # Assuming rotation 1 for simplicity

            previous_pallet.combine(pallet)

            if previous_pallet > best_pallet:
                best_pallet = previous_pallet.copy()

            if fill_rest:
                pallet_L = Pallet(L_r, pallet.w, pallet.h)
                pallet_l = Pallet(pallet.L, w_r, pallet.h)
                pallet_h = Pallet(pallet.L, pallet.w, h_r)
                pallet_fill_rest.extend([pallet_L, pallet_l, pallet_h])
                for pallet in pallet_fill_rest:
                    best_little_pallet_fill = fill_pallet(pallet, box, False, previous_pallet.copy(), debug, log_file)
                    previous_pallet.combine(best_little_pallet_fill)
                    if previous_pallet > best_pallet:
                        best_pallet = previous_pallet.copy()

            pallet.remove_box(1, nb_L, nb_w, nb_h)

    return best_pallet

import numpy as np
import plotly.graph_objects as go

def plot_pallet_plotly(pallet, box):
    def create_box_faces(x, y, z, dx, dy, dz):
        # Define the vertices of the box
        vertices = np.array([
            [x, y, z],
            [x + dx, y, z],
            [x + dx, y + dy, z],
            [x, y + dy, z],
            [x, y, z + dz],
            [x + dx, y, z + dz],
            [x + dx, y + dy, z + dz],
            [x, y + dy, z + dz]
        ])

        # Define the faces of the box
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom face
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # Top face
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # Side face
            [vertices[1], vertices[2], vertices[6], vertices[5]],  # Side face
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # Side face
            [vertices[3], vertices[0], vertices[4], vertices[7]]   # Side face
        ]

        # Define the edges of the box
        edges = [
            [vertices[0], vertices[1]], [vertices[1], vertices[2]], [vertices[2], vertices[3]], [vertices[3], vertices[0]],  # Bottom face edges
            [vertices[4], vertices[5]], [vertices[5], vertices[6]], [vertices[6], vertices[7]], [vertices[7], vertices[4]],  # Top face edges
            [vertices[0], vertices[4]], [vertices[1], vertices[5]], [vertices[2], vertices[6]], [vertices[3], vertices[7]]   # Vertical edges
        ]

        return faces, edges

    # Create Plotly figure
    fig = go.Figure()

    # Add pallet edges
    pallet_vertices = [
        [0, 0, 0],
        [pallet.L, 0, 0],
        [pallet.L, pallet.w, 0],
        [0, pallet.w, 0],
        [0, 0, pallet.h],
        [pallet.L, 0, pallet.h],
        [pallet.L, pallet.w, pallet.h],
        [0, pallet.w, pallet.h]
    ]

    fig.add_trace(go.Scatter3d(
        x=[v[0] for v in pallet_vertices],
        y=[v[1] for v in pallet_vertices],
        z=[v[2] for v in pallet_vertices],
        mode='lines',
        line=dict(color='lightgrey', width=2),
        marker=dict(size=4)
    ))

    # Add box faces, edges, and calculate center of gravity
    box_color = '#3DED97'  # Color for all faces
    border_color = 'darkgreen'
    
    cog_x_sum = 0
    cog_y_sum = 0
    cog_z_sum = 0
    total_weight = 0

    # Initialize offsets
    current_x = 0
    current_y = 0

    for step in pallet.content:
        rotation = step[0]
        nb_L = step[1]
        nb_w = step[2]
        nb_h = int(step[3])
       

        for i in range(nb_L):
            for j in range(nb_w):
                for k in range(nb_h):
                    if rotation == 1:
                        x = current_x + i * box.L
                        y = current_y + j * box.w
                        z = k * box.h
                        dx = box.L
                        dy = box.w
                        dz = box.h
                    elif rotation == 2:
                        x = current_x + i * box.w
                        y = current_y + j * box.L
                        z = k * box.h
                        dx = box.w
                        dy = box.L
                        dz = box.h

                    # Calculate the center of gravity of the box
                    cog_x_sum += (x + dx / 2) * box.weight
                    cog_y_sum += (y + dy / 2) * box.weight
                    cog_z_sum += (z + dz / 2) * box.weight
                    total_weight += box.weight

                    # Create box faces and edges
                    faces, edges = create_box_faces(x, y, z, dx, dy, dz)
                    
                    # Add all faces with the same color
                    for face in faces:
                        fig.add_trace(go.Mesh3d(
                            x=[v[0] for v in face],
                            y=[v[1] for v in face],
                            z=[v[2] for v in face],
                            color=box_color,
                            opacity=0.5,
                            flatshading=True
                        ))

                    # Add edges with dark green color
                    for edge in edges:
                        fig.add_trace(go.Scatter3d(
                            x=[edge[0][0], edge[1][0]],
                            y=[edge[0][1], edge[1][1]],
                            z=[edge[0][2], edge[1][2]],
                            mode='lines',
                            line=dict(color=border_color, width=2)
                        ))

        # Update the current_x and current_y for the next rotation
        if rotation == 1:
            current_x += nb_L * box.L
        elif rotation == 2:
            current_y += nb_w * box.L

    # Calculate the final COG coordinates
    if total_weight != 0:
        cog_x = cog_x_sum / total_weight
        cog_y = cog_y_sum / total_weight
        cog_z = cog_z_sum / total_weight
        pallet.cog_height=cog_z
    else:
        cog_x, cog_y, cog_z = 0, 0, 0

    # Plot the center of gravity as a red dot
    fig.add_trace(go.Scatter3d(
        x=[cog_x],
        y=[cog_y],
        z=[cog_z],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Center of Gravity'
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Length (mm)',
            yaxis_title='Width (mm)',
            zaxis_title='Height (mm)',
            xaxis=dict(nticks=10, range=[0, pallet.L]),
            yaxis=dict(nticks=10, range=[0, pallet.w]),
            zaxis=dict(nticks=10, range=[0, pallet.h]),
            aspectmode='data'
        ),
        title='Pallet with Boxes',
        autosize=False,
        width=1200,  # Increase the width of the figure
        height=900   # Increase the height of the figure
    )

    return fig



def plot_pallet(pallet, box):
    def draw_pallet(ax, pallet, color='lightgrey', alpha=0.3):
        pallet_vertices = [
            (0, 0, 0),
            (pallet.L, 0, 0),
            (pallet.L, pallet.w, 0),
            (0, pallet.w, 0),
            (0, 0, pallet.h),
            (pallet.L, 0, pallet.h),
            (pallet.L, pallet.w, pallet.h),
            (0, pallet.w, pallet.h)
        ]
        pallet_faces = [
            [pallet_vertices[0], pallet_vertices[1], pallet_vertices[2], pallet_vertices[3]],
            [pallet_vertices[4], pallet_vertices[5], pallet_vertices[6], pallet_vertices[7]],
            [pallet_vertices[0], pallet_vertices[1], pallet_vertices[5], pallet_vertices[4]],
            [pallet_vertices[1], pallet_vertices[2], pallet_vertices[6], pallet_vertices[5]],
            [pallet_vertices[2], pallet_vertices[3], pallet_vertices[7], pallet_vertices[6]],
            [pallet_vertices[3], pallet_vertices[0], pallet_vertices[4], pallet_vertices[7]]
        ]
        

    def draw_boxes(ax, pallet, box):
        box_colors = ['#97BC62']
        box_color_index = 0

        position_offsets = {
            1: [0, 0, 0],
            2: [0, 0, 0]
        }

        current_x = 0
        current_y = 0

        cog_x_sum = 0
        cog_y_sum = 0
        cog_z_sum = 0
        total_weight = 0

        for step in pallet.content:
            rotation = step[0]
            nb_L = step[1]
            nb_w = step[2]
            nb_h = step[3]

            for i in range(nb_L):
                for j in range(nb_w):
                    for k in range(nb_h):
                        if box_color_index >= len(box_colors):
                            box_color_index = 0  
                        color = box_colors[box_color_index]
                        box_color_index += 1

                        offset = position_offsets[rotation]

                        if rotation == 1:
                            x = current_x + i * box.L
                            y = current_y + j * box.w
                            z = k * box.h
                            dx = box.L
                            dy = box.w
                            dz = box.h
                        elif rotation == 2:
                            x = current_x + i * box.w
                            y = current_y + j * box.L
                            z = k * box.h
                            dx = box.w
                            dy = box.L
                            dz = box.h

                        ax.bar3d(x, y, z, dx, dy, dz, color=color, edgecolor='#2C5F2D',alpha=0.25)

                        # Update COG calculation
                        cog_x_sum += (x + dx / 2) * box.weight
                        cog_y_sum += (y + dy / 2) * box.weight
                        cog_z_sum += (z + dz / 2) * box.weight
                        total_weight += box.weight

            # Update the current_x and current_y for the next rotation
            if rotation == 1:
                current_x += nb_L * box.L
            elif rotation == 2:
                current_y += nb_w * box.L

        # Calculate the final COG coordinates
        if total_weight != 0:
            cog_x = cog_x_sum / total_weight
            cog_y = cog_y_sum / total_weight
            cog_z = cog_z_sum / total_weight
            pallet.cog_height=cog_z
        else:
            cog_x, cog_y, cog_z = 0, 0, 0

        ax.set_xlim(0, pallet.L)
        ax.set_ylim(0, pallet.w)
        ax.set_zlim(0, pallet.h)

        return cog_x, cog_y, cog_z

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Length (mm)')
    ax.set_ylabel('Width (mm)')
    ax.set_zlabel('Height (mm)')

    draw_pallet(ax, pallet, color='lightgrey', alpha=0.3)
    cog_x, cog_y, cog_z = draw_boxes(ax, pallet, box)

    ax.set_title(f"Pallet with boxes")

    # Plot the center of gravity
    print(f"{cog_x} - {cog_y} - {cog_z}")
    
    ax.scatter(cog_x, cog_y, cog_z, color='darkred', s=100, label='Center of Gravity', depthshade=True)
    ax.legend()

    plt.tight_layout()
    plt.show()

def report(optimized_pallet,box):
    total_weight=optimized_pallet.nb_box*box.weight
    stack_num=optimized_pallet.content[0][3]
    height_in_mm= optimized_pallet.content[0][3]*box.h
    
    text=f"""{box.name}
    Total weight of boxes in pallet is : {total_weight}kg\n\n
    Number of boxes stacked : {stack_num}\n\n
    Height of boxes is : {height_in_mm}mm\n\n
    Center of Gravity is at a height of : {optimized_pallet.cog_height}mm\n\n
    Crushing strength employed is : {box.crushing_strength}kg\n\n
    """
    return text
    

def main():
    with open("pallet_log.txt", 'w'):  
        pass  

    box = Box(700,400,377, 10)
    print(box.L, box.w, box.h)

    pallet = Pallet(1200, 1000, 2200)
    print(pallet.get_dim())
    optimized_pallet = fill_pallet(pallet, box, True, Pallet(pallet.L, pallet.w, pallet.h), debug=True, log_file="pallet_log.txt")
    print(optimized_pallet.nb_box)
    optimized_pallet.print_way_fill(True)
    
    optimized_pallet.print_total(True)
    plot_pallet(optimized_pallet, box)

if __name__ == "__main__":
    main()
