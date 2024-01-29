import sys
import functools
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsPixmapItem, QGraphicsView, QGraphicsPolygonItem, QFileDialog
from PyQt5.QtCore import Qt, QPoint, QCoreApplication, QRectF
from PyQt5.QtGui import QPixmap, QPolygonF, QPen, QPainter, QImage, QColor
from PyQt5 import QtWidgets, QtCore
from mainwindow import Ui_MainWindow
from functions import CustomGraphicsScene
from extract_polygons import polygons_from_segmented_image
from list_widgets import ColorSelectionItemWidget
from classes import class_dict, class_color

class MainWindow(QMainWindow):
    """Mainwindow of the desktop application

    All widgets are initialized here
    """
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        

        self.draw_color = Qt.black
        self.drawing = False
        self.moving = False
        self.removing = False
        self.flipping = False
        self.resizing = False

        self.load_button_1 = self.ui.pushButton
        self.save_button_1 = self.ui.pushButton_2
        self.load_button_2 = self.ui.pushButton_7
        self.save_button_2 = self.ui.pushButton_9

        self.draw_button = self.ui.pushButton_3
        self.flip_button = self.ui.pushButton_8
        self.move_button = self.ui.pushButton_4
        self.remove_button = self.ui.pushButton_5
        self.clear_button = self.ui.pushButton_6
        self.resize_button = self.ui.pushButton_10

        self.check_box = self.ui.checkBox

        self.load_button_1.clicked.connect(self.load_image_1)
        self.load_button_2.clicked.connect(self.load_image_2)
        self.save_button_1.clicked.connect(self.save_image_1)
        self.save_button_2.clicked.connect(self.save_image_2)
        self.draw_button.clicked.connect(self.draw_on_image)
        self.move_button.clicked.connect(self.move_on_image)
        self.remove_button.clicked.connect(self.remove_on_image)
        self.clear_button.clicked.connect(self.clear_screen)
        self.flip_button.clicked.connect(self.flip_polygon)
        self.resize_button.clicked.connect(self.resize_polygon)

        self.whiten = False
        self.check_box.stateChanged.connect(self.on_whiten)        

        self.brush_width = 3
        self.slider = self.ui.verticalSlider
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(3)
        self.slider.valueChanged.connect(self.on_slider_change)

        self.resize_slider = self.ui.verticalSlider_2
        self.resize_slider.setMinimum(0)
        self.resize_slider.setMaximum(100)
        self.resize_slider.setValue(50)
        self.resize_slider.valueChanged.connect(self.on_resize_slider_change)

        # self.ui.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.ui.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.ui.graphicsView.setRenderHint(QPainter.Antialiasing)
        # self.ui.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        # self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.polygons = {1: [], 2:[]}
        self.polygon_color = {1: [], 2:[]}
        self.polygon_items = {1: [], 2:[]}
        self.old_polygon_items = {1: [], 2:[]}

        self.image_paths = {}
        self.images = {}
        self.image_items =  {}
        self.setup_color_list()
        self.show()
        self.setup_graphics_view()

    def on_slider_change(self, value):
        self.brush_width = value

    def on_resize_slider_change(self, value):
        self.scene.resize_polygon(value/50)
        
    def setup_graphics_view(self):
        self.scene = CustomGraphicsScene(self, self.polygon_items)
        self.ui.graphicsView.setScene(self.scene)
        # self.load_image("/home/rrr/joint_diffusion/bottle_book_mask.png")

    def setup_color_list(self):
        color_list_widget = self.ui.listWidget
        count = 0
        self.color_ind_map = {}
        for index, class_name in class_dict.items():
            r,g,b = class_color[index-1]
            self.color_ind_map[count] = index-1
            color = QColor(r,g,b)
            color_widget = ColorSelectionItemWidget(color, class_name)
            color_list_widget.addItem(color_widget)
            count += 1
        color_widget = ColorSelectionItemWidget(QColor(255,255,255), "white")
        color_list_widget.addItem(color_widget)
        self.color_ind_map[count] = len(class_dict)+1

        color_list_widget.itemClicked.connect(self.color_item_selected)

    def color_item_selected(self, item):
        index = self.sender().row(item)
        r,g,b = class_color[self.color_ind_map[index]]
        if index == 183:
            r,g,b = 255,255,255
        color = QColor(r,g,b)
        self.draw_color = color

    def on_whiten(self, state):
        if state == Qt.Checked:
            self.whiten = True
        else:
            self.whiten = False            

    def load_image_1(self):
        self.load_image(1)

    def load_image_2(self):
        self.load_image(2)

    def load_image(self, ind):
        options = QFileDialog.Options()
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        
        if image_path:
            polygons, polygon_color = polygons_from_segmented_image(image_path)
            self.polygons[ind] = polygons
            self.polygon_color[ind] = polygon_color
            self.image_paths[ind] = image_path
            # self.ui.graphicsView.scene().clear()
            self.image = QPixmap(image_path)
            self.image_item = QGraphicsPixmapItem(self.image)

            if ind == 2:
                self.image_item.setPos(self.image.width()+10, 0)
            

            self.images[ind] = self.image
            self.image_items[ind] = self.image_item
            # self.ui.graphicsView.fitInView(self.image_item, Qt.KeepAspectRatio)
            self.ui.graphicsView.scene().addItem(self.image_item)
            self.polygon_items[ind].clear()
            for polygon in polygons:
                if ind == 2:
                    polygon_item = QGraphicsPolygonItem(QPolygonF([QPoint(p[0]+self.image.width()+10, p[1]) for p in polygon]))
                else:
                    polygon_item = QGraphicsPolygonItem(QPolygonF([QPoint(p[0], p[1]) for p in polygon]))
                pen = QPen(Qt.white, 2, Qt.DashLine)
                polygon_item.setPen(pen)
                self.ui.graphicsView.scene().addItem(polygon_item)
                self.polygon_items[ind].append(polygon_item)
            self.old_polygon_items[ind] = self.polygon_items[ind].copy()

    def save_image_1(self):
        self.save_image(1)

    def save_image_2(self):
        self.save_image(2)
    
    def save_image(self, ind):
        save_path = self.image_paths[ind].split("/")
        save_path[-1] = save_path[-1].split(".")[0] + "_" + str(ind)+  "_edited.png" 
        final_save_path = "/".join(save_path)
        for i, polygon_item in enumerate(self.polygon_items[ind]):
            if polygon_item.scene() is not None:
                self.ui.graphicsView.scene().removeItem(polygon_item)
        
        for i, polygon_item in enumerate(self.old_polygon_items[ind]):
            if polygon_item.scene() is not None:
                self.ui.graphicsView.scene().removeItem(polygon_item)
        scene = self.ui.graphicsView.scene()
        image = QImage(self.images[ind].size(), QImage.Format_ARGB32)
        painter = QPainter(image)
        rect = QRectF(self.images[ind].rect())
        mapped_rect = self.image_items[ind].mapRectToScene(rect)
        scene.render(painter, QRectF(image.rect()), mapped_rect)
        painter.end()
        image.save(final_save_path)
        if self.image_items[ind].scene() is not None:
            self.ui.graphicsView.scene().removeItem(self.image_items[ind])
        # self.ui.graphicsView.scene().clear()

    def clear_screen(self):
        for d in self.polygon_items:
            for i, polygon_item in enumerate(self.polygon_items[d]):
                if polygon_item.scene() is not None:
                    self.ui.graphicsView.scene().removeItem(polygon_item)
            
        for d in self.polygon_items:
            for i, polygon_item in enumerate(self.polygon_items[d]):
                if polygon_item.scene() is not None:
                    self.ui.graphicsView.scene().removeItem(polygon_item)
        for d in self.image_items:
            if self.image_items[d].scene() is not None:
                self.ui.graphicsView.scene().removeItem(self.image_item)
        self.ui.graphicsView.scene().clear()
        self.drawing = False
        self.moving = False
        self.removing = False
        self.flipping = False

    def flip_polygon(self):
        self.drawing = False
        self.moving = False
        self.removing = False
        self.flipping = True
        self.resizing = False

    def draw_on_image(self):
        self.drawing = True
        self.moving = False
        self.removing = False
        self.flipping = False
        self.resizing = False

    def move_on_image(self):
        self.drawing = False
        self.moving = True
        self.removing = False
        self.flipping = False
        self.resizing = False

    def remove_on_image(self):
        self.drawing = False
        self.moving = False
        self.removing = True
        self.flipping = False
        self.resizing = False

    def resize_polygon(self):
        self.drawing = False
        self.moving = False
        self.removing = False
        self.flipping = False
        self.resizing = True

def catch_exceptions(job_func):
    """Wrapper function for the job_func
    """
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            return job_func(*args, **kwargs)
        except:
            import traceback
            print("%s",traceback.format_exc())
            return None
    return wrapper

@catch_exceptions
def main():
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    widget = MainWindow()
    app.exec()

if __name__ == "__main__":
    main()