import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, Cursor, TextBox
from torch import os


class IRS:
    '''
    Interactive Region Selection for dataset
    '''

    def __init__(self, target: str) -> None:
        self.base_dir = target
        self.targets = os.listdir(target)
        self.ind = 0
        self.fig, self.ax = plt.subplots()
        self.rect_regions = []
        self.rects = []
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_left_click)
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_right_click)
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)
        axes = plt.axes([.81, 0, .1, .075])
        button = Button(axes, "Next", color="yellow")
        button.on_clicked(self.next)
        axes = plt.axes([0, 0, .2, .075])
        self.coordinate_box = TextBox(
            axes, "Coordinates", initial="Coordinates")
        plt.show()

    def next(self, _):
        if self.ind < len(self.targets):
            img = plt.imread(f"{self.base_dir}/{self.targets[self.ind]}")
            self.ax.imshow(img)
        self.write()
        self.clear()
        self.ind += 1

    def write(self):
        f = open("labels.csv", 'a+')
        header = f.readline()
        f.seek(0)
        if "path" not in header:
            f.write("path, file, label\n")
        if self.rect_regions:
            rect_regions_strs = []
            for rect_region in self.rect_regions:
                rect_regions_strs.append(f"{rect_region[0]},{rect_region[1]}")
            f.write(f"{self.base_dir}, {self.targets[self.ind]}, {','.join(rect_regions_strs)}")
        f.close()

    def clear(self):
        rects_num = len(self.rects)
        for _ in range(rects_num):
            rect = self.rects.pop()
            rect.remove()
            del rect
        self.rect_regions.clear()

    def on_left_click(self, e):
        if e.button != 1 or e.inaxes != self.ax:
            return
        xdata, ydata = int(e.xdata), int(e.ydata)
        self.coordinate_box.set_val(f"{xdata}, {ydata}")
        self.rect_regions.append((xdata, ydata))
        self.draw_rect()

    def draw_rect(self):
        if len(self.rect_regions) % 2 or not self.rect_regions:
            return
        # 2 diagonal points
        x11, y11 = self.rect_regions[-1]
        x00, y00 = self.rect_regions[-2]
        # find anchor points
        width = abs(x11 - x00)
        height = abs(y11 - y00)
        anchor_point = (min([x00, x11]), min([y00, y11]))
        rect = Rectangle(anchor_point, width, height,
                         edgecolor='red', facecolor='none', lw=1)
        self.ax.add_patch(rect)
        self.rects.append(rect)

    def on_right_click(self, e):
        if e.button != 3 or e.inaxes != self.ax:
            return
        rect_regions_num = len(self.rect_regions)
        if rect_regions_num >= 2:
            if rect_regions_num % 2:
                last_elem = self.rect_regions.pop()
                self.rect_regions = self.rect_regions[:-2] + [last_elem]
            else:
                self.rect_regions = self.rect_regions[:-2]
        if self.rects:
            rect = self.rects.pop()
            rect.remove()
            del rect    


IRS("./LSP/544479 宮瀬まひろ/NR")
