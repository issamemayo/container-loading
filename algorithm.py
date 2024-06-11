import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # visualization of containers

#Box definition 
class Box:
    def __init__(self, width, breadth, height, label):
        self.width = width
        self.breadth = breadth
        self.height = height
        self.label = label
        self.volume = width * breadth * height

#Container definition
class Container:
    def __init__(self, width, breadth, height):
        self.width = width
        self.breadth = breadth
        self.height = height
        self.volume = width * breadth * height
        self.boxes = []

    def place_box(self, box, x, y, z):
        #Collision with container
        if (
            x >= 0 and y >= 0 and z >= 0 and
            x + box.width <= self.width and
            y + box.height <= self.height and
            z + box.breadth <= self.breadth
        ):
            #Collision with existing boxes in current container
            for existing_box, bx, by, bz in self.boxes:
                if (
                    x < bx + existing_box.width and x + box.width > bx and
                    y < by + existing_box.height and y + box.height > by and
                    z < bz + existing_box.breadth and z + box.breadth > bz
                ):
                    return False

            self.boxes.append((box, x, y, z))
            return True

        return False

def visualize_containers(containers):   
    num_containers = len(containers)
    fig = plt.figure(figsize=(10, num_containers * 4))
    
    #Setting dimensions of containers for plot
    for i, container in enumerate(containers):
        ax = fig.add_subplot(num_containers, 1, i + 1, projection='3d')
        ax.set_xlim(0, container.width)
        ax.set_ylim(0, container.height)
        ax.set_zlim(0, container.breadth)
        
        # Drawing the container
        vertices = [
            [0, 0, 0], [container.width, 0, 0], [container.width, container.height, 0], [0, container.height, 0],
            [0, 0, container.breadth], [container.width, 0, container.breadth], [container.width, container.height, container.breadth], [0, container.height, container.breadth]
        ]
        faces = [
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[7], vertices[6], vertices[2], vertices[3]],
            [vertices[0], vertices[3], vertices[7], vertices[4]],
            [vertices[1], vertices[2], vertices[6], vertices[5]],
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]]
        ]
        
        poly3d = Poly3DCollection(faces, facecolors='cyan', linewidths=1, edgecolors='r', alpha=0.1)
        ax.add_collection3d(poly3d)
        #Placement of boxes within the containers
        for box, x, y, z in container.boxes:
            ax.bar3d(x, y, z, box.width, box.height, box.breadth, alpha=0.5)
            #Label placement for boxes
            ax.text(x + box.width / 2, y + box.height / 2, z + box.breadth / 2, box.label, color='black', ha='center', va='center')
        
        ax.set_title(f"Container {i + 1}")
    
    plt.tight_layout()
    plt.show()

def best_fit_decreasing(containers, boxes):
    # Sort on basis of decreasing order of volume
    sorted_boxes = sorted(boxes, key=lambda b: b.volume, reverse=True)

    for box in sorted_boxes:
        print(box.label)
        placed = False

        # Placing box in existing containers
        for container in containers:
            for z in range(container.breadth):
                for y in range(container.height):
                    for x in range(container.width):
                        if container.place_box(box, x, y, z):
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break
            if placed:
                break

        # New Container created if no space for box in old containers
        if not placed:
            new_container = Container(containers[0].width, containers[0].breadth, containers[0].height)
            containers.append(new_container)
            for z in range(new_container.breadth):
                for y in range(new_container.height):
                    for x in range(new_container.width):
                        if new_container.place_box(box, x, y, z):
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break

            if not placed:
                return False

    return True

def main():
    initial_container_size = (100, 100, 100)
    containers = [Container(*initial_container_size)]
    boxes = [
        Box(20, 30, 40, 'Box1'),
        Box(50, 50, 50, 'Box2'),
        Box(30, 20, 10, 'Box3'),
        Box(10, 10, 10, 'Box4'),
        Box(40, 60, 30, 'Box5'),
        Box(40, 30, 30, 'Box6'),
        Box(60, 20, 10, 'Box7'),
        

    ]

    if not best_fit_decreasing(containers, boxes):
        print("Error: No valid arrangement of boxes found.")

    for i, container in enumerate(containers):
        used_vol = sum(box.volume for box, _, _, _ in container.boxes)
        print(f"Container {i + 1} - Percentage of Volume used is {round((used_vol / container.volume) * 100, 2)}%")
    
    visualize_containers(containers)

if __name__ == '__main__':
    main()
