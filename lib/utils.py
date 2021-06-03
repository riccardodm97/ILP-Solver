from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import bisect

class Parameters:
    DECIMAL_PRECISION = 8

class ProblemSolution(Enum):
    FINITE = 1
    UNLIMITED = 2
    IMPOSSIBLE = 3

class DomainConstraintType(Enum):
    LESS_EQUAL = 1
    GREAT_EQUAL = 2
    EQUAL = 3

class DomainOptimizationType(Enum):
    MAX = 1
    MIN = 2

def plot_map(image_path, blocks, columns, sols):
    w, h = 100, 80      # Size of the box containing the values to plot
    fontsize = 7        # Size of the font
    padding_left = 5    # Left padding on the box

    cols_num = len(columns)
    vert_offset = 2 * h / (cols_num * 2 + 1)
    img = plt.imread(image_path)
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_aspect('equal')
    ax.imshow(img)

    for b_index, block in enumerate(blocks):
        x, y = block['coord'].values()
        left_x, top_y = x - w / 2, y - h / 2
        background = Rectangle((left_x, top_y), w, h, color="black")
        ax.add_patch(background)

        offset = vert_offset
        for c_index, column in enumerate(columns):
            ax.text(left_x + padding_left, top_y + offset, column['name'] + ": " + str(sols[b_index * cols_num + c_index]), fontsize=fontsize, va='center', color="white")
            offset += vert_offset
            
    plt.show()


class SortedList():
    
    def __init__(self, items=[]) -> None:
        self._list = list(items)
        
    def add(self, item):
        self._list.append(item)
        self._list.sort()

    
    def pop(self, n=0):
        return self._list.pop(n)

    def __bool__(self):
        return len(self._list) > 0