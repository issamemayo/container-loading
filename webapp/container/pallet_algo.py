import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
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
    def __init__(self, _L=1, _w=1, _h=1):
        self.L = _L
        self.w = _w
        self.h = _h

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
    def __init__(self, _L=1, _w=1, _h=1):
        super().__init__(_L, _w, _h)  
        self.content = []
        self.nb_box = 0

    def add_box(self, rotation, nb_L, nb_w, nb_h):
        if (nb_L * nb_w * nb_h) > 0:
            merged = False
            for i in range(len(self.content)):
                if rotation == self.content[i][0]:
                    if (nb_L * nb_w * nb_h) > (self.content[i][1] * self.content[i][2] * self.content[i][3]):
                        self.content[i] = [rotation, nb_L, nb_w, nb_h]
                        self.nb_box -= self.content[i][1] * self.content[i][2] * self.content[i][3]
                        self.nb_box += nb_L * nb_w * nb_h
                    merged = True
            if not merged:
                self.content.append([rotation, nb_L, nb_w, nb_h])
                self.nb_box += nb_L * nb_w * nb_h

    def remove_box(self, rotation, nb_L, nb_w, nb_h, debug=False, log_file=".log"):
        if len(self.content) == 0:
            return
        try:
            self.content.remove([rotation, nb_L, nb_w, nb_h])
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
                rotation_text = "vertically on the long edge, along the length of the pallet"
            elif step[0] == 3:
                rotation_text = "flat along the width of the pallet"
            elif step[0] == 4:
                rotation_text = "vertically on the short edge, parallel to the length of the pallet"
            elif step[0] == 5:
                rotation_text = "vertically on the long edge, along the width of the pallet"
            elif step[0] == 6:
                rotation_text = "vertically on the short edge, parallel to the width of the pallet"
            
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
    p = []
    for i in range(3):
        k = [0, 1, 2]
        n1 = k[i]
        k.remove(n1)
        for j in range(2):
            n2 = k[j % 2]
            n3 = k[(j + 1) % 2]
            a = [dimensions[n1], dimensions[n2], dimensions[n3]]
            p.append(a)
    return p

def fill_pallet(_pallet, box, fill_rest=True, _previous_pallet=Pallet(), debug=False, log_file=".log"):
    best_pallet = Pallet()
    
    n = 0
    for dim in possibilities(box.get_dim()):
        pallet = _pallet.copy()
        pallet_fill_rest = []
        previous_pallet = _previous_pallet.copy()

        if debug:
            if fill_rest: printf(log_file, "\n" * 2 + "-+*+-" * 10 + "________base")
            else: printf(log_file, "________rest")
            printf(log_file, dim, " in ", pallet.get_dim())

        n += 1
        if debug: printf(log_file, "n=", n)

        nb_L = pallet.L // dim[0]
        L = dim[0] * nb_L

        nb_w = pallet.w // dim[1]
        w = dim[1] * nb_w

        nb_h = pallet.h // dim[2]
        h = dim[2] * nb_h

        L_r, w_r, h_r = 0, 0, 0
        if not nb_L * nb_w * nb_h == 0:
            L_r = pallet.L - L
            w_r = pallet.w - w
            h_r = pallet.h - h

        pallet.add_box(n, nb_L, nb_w, nb_h)

        previous_pallet.combine(pallet)

        if debug:
            printf(log_file, "nb box=", nb_L, "x", nb_w, "x", nb_h, " =", nb_L * nb_w * nb_h)
            printf(log_file, "nb box in pallet=", nb_L, "x", nb_w, "x", nb_h, " =", pallet.nb_box)
            printf(log_file, "total=", previous_pallet.nb_box)
            printf(log_file, "total=", previous_pallet.content)
            printf(log_file, "total=", L, "x", w, "x", h)
            printf(log_file, "rest=", L_r, "x", w_r, "x", h_r)

        if previous_pallet > best_pallet:
            best_pallet = previous_pallet.copy()

        if fill_rest:
            pallet_L = Pallet(L_r, pallet.w, pallet.h)
            pallet_l = Pallet(pallet.L, w_r, pallet.h)
            pallet_h = Pallet(pallet.L, pallet.w, h_r)
            pallet_fill_rest.append(pallet_L)
            pallet_fill_rest.append(pallet_l)
            pallet_fill_rest.append(pallet_h)
            if debug:
                printf(log_file, "=" * 10 + "\nPallets to fill \n" + "=" * 10)
                for c in pallet_fill_rest:
                    printf(log_file, c)
            for pallet in pallet_fill_rest:
                best_little_pallet_fill = fill_pallet(pallet, box, False, previous_pallet.copy(), debug, log_file)
                previous_pallet.combine(best_little_pallet_fill)

                if previous_pallet > best_pallet:
                    best_pallet = previous_pallet.copy()

        pallet.remove_box(n, nb_L, nb_w, nb_h, log_file, debug)

    if debug:
        printf(log_file, "\n\n\n")
        printf(log_file, "*" * 20)
        printf(log_file, "End function")
        printf(log_file, "Best Pallet\n")
        printf(log_file, best_pallet)
        printf(log_file, "*" * 20)
        printf(log_file, "\n\n\n")

    return best_pallet


def plot_multiple_pallets(pallets, box):
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
        ax.add_collection3d(Poly3DCollection(pallet_faces, facecolors=color, linewidths=1, edgecolors='k', alpha=alpha))

    def draw_boxes(ax, pallet, box, rotation_type):
        box_colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightseagreen', 'lightskyblue']
        box_color_index = 0

        for step in pallet.content:
            rotation = step[0]
            if rotation != rotation_type:
                continue
            
            nb_L = step[1]
            nb_w = step[2]
            nb_h = step[3]

            for i in range(nb_L):
                for j in range(nb_w):
                    for k in range(nb_h):
                        if box_color_index >= len(box_colors):
                            box_color_index = 0  # Reset color index if all colors used
                        color = box_colors[box_color_index]
                        box_color_index += 1

                        if rotation == 1:
                            x = i * box.L
                            y = j * box.w
                            z = k * box.h
                            dx = box.L
                            dy = box.w
                            dz = box.h
                        elif rotation == 2:
                            x = i * box.L
                            y = j * box.h
                            z = k * box.w
                            dx = box.L
                            dy = box.h
                            dz = box.w
                        elif rotation == 3:
                            x = i * box.w
                            y = j * box.L
                            z = k * box.h
                            dx = box.w
                            dy = box.L
                            dz = box.h
                        elif rotation == 4:
                            x = i * box.h
                            y = j * box.L
                            z = k * box.w
                            dx = box.h
                            dy = box.L
                            dz = box.w
                        elif rotation == 5:
                            x = i * box.w
                            y = j * box.h
                            z = k * box.L
                            dx = box.w
                            dy = box.h
                            dz = box.L
                        elif rotation == 6:
                            x = i * box.h
                            y = j * box.w
                            z = k * box.L
                            dx = box.h
                            dy = box.w
                            dz = box.L

                        # Check if box fits within pallet dimensions
                        if x + dx <= pallet.L and y + dy <= pallet.w and z + dz <= pallet.h:
                            ax.bar3d(x, y, z, dx, dy, dz, color=color, edgecolor='black')

        ax.set_xlim(0, pallet.L)
        ax.set_ylim(0, pallet.w)
        ax.set_zlim(0, pallet.h)

    rotation_types = {
        1: "flat along the length of the pallet",
        2: "flat along the width of the pallet",
        3: "flat along the length and height of the pallet",
        4: "flat along the width and height of the pallet",
        5: "flat along the height and length of the pallet",
        6: "flat along the height and width of the pallet"
    }
    
    for pallet in pallets:
        if not pallet.content:  # Skip empty pallets
            continue
        
        fig = plt.figure(figsize=(16, 8))

        non_empty_rotations = [rt for rt in rotation_types if any(step[0] == rt for step in pallet.content)]

        for i, rotation_type in enumerate(non_empty_rotations):
            ax = fig.add_subplot(2, 3, i + 1, projection='3d')
            ax.set_xlabel('Length (mm)')
            ax.set_ylabel('Width (mm)')
            ax.set_zlabel('Height (mm)')

            draw_pallet(ax, pallet, color='lightgrey', alpha=0.3)
            draw_boxes(ax, pallet, box, rotation_type)

            ax.set_title(f"Pallet with boxes {rotation_types[rotation_type]}")

        plt.tight_layout()
        plt.show()

def main():
    with open("pallet_log.txt", 'w'):  
        pass  

    box = Box(500, 300, 200)
    print(box.w, box.L, box.h)  

    pallet = Pallet(1200, 1300, 2200)
    print(pallet.get_dim())

    optimized_pallet = fill_pallet(pallet, box, True, Pallet(pallet.L,pallet.w,pallet.h), debug=True, log_file="pallet_log.txt")
    print(optimized_pallet)
    optimized_pallet.print_way_fill(True)
    optimized_pallet.print_total(True)
    plot_multiple_pallets([optimized_pallet], box)


if __name__ == "__main__":
    main()
