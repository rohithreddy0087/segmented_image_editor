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

        self.load_button = self.ui.pushButton
        self.save_button = self.ui.pushButton_2
        self.draw_button = self.ui.pushButton_3
        self.move_button = self.ui.pushButton_4
        self.remove_button = self.ui.pushButton_5
        self.clear_button = self.ui.pushButton_6

        self.load_button.clicked.connect(self.load_image)
        self.save_button.clicked.connect(self.save_scene_as_image)
        self.draw_button.clicked.connect(self.draw_on_image)
        self.move_button.clicked.connect(self.move_on_image)
        self.remove_button.clicked.connect(self.remove_on_image)
        self.clear_button.clicked.connect(self.clear_screen)

        self.brush_width = 3
        self.slider = self.ui.verticalSlider
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(3)
        self.slider.valueChanged.connect(self.on_slider_change)

        self.ui.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.ui.graphicsView.setRenderHint(QPainter.Antialiasing)
        # self.ui.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        # self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.polygon_items = []
        self.setup_color_list()
        self.show()
        self.setup_graphics_view()

    def on_slider_change(self, value):
        self.brush_width = value
        
    def setup_graphics_view(self):
        self.scene = CustomGraphicsScene(self, self.polygon_items)
        self.ui.graphicsView.setScene(self.scene)
        # self.load_image("/home/rrr/joint_diffusion/bottle_book_mask.png")

    def setup_color_list(self):
        color_list_widget = self.ui.listWidget
        count = 0
        self.color_ind_map = {}
        for index, class_name in class_dict.items():
            r,g,b = class_color[index]
            self.color_ind_map[count] = index
            color = QColor(r,g,b)
            color_widget = ColorSelectionItemWidget(color, class_name)
            color_list_widget.addItem(color_widget)
            count += 1

        color_list_widget.itemClicked.connect(self.color_item_selected)

    def color_item_selected(self, item):
        index = self.sender().row(item)
        r,g,b = class_color[self.color_ind_map[index]]
        color = QColor(r,g,b)
        self.draw_color = color

    def load_image(self):
        options = QFileDialog.Options()
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        self.polygons, self.polygon_color = polygons_from_segmented_image(self.image_path)
        # self.polygon_items = []
        # print(self.polygon_color)
        if self.image_path:
            self.ui.graphicsView.scene().clear()
            self.image = QPixmap(self.image_path)
            self.image_item = QGraphicsPixmapItem(self.image)
            # self.ui.graphicsView.fitInView(self.image_item, Qt.KeepAspectRatio)

            self.ui.graphicsView.scene().addItem(self.image_item)
            self.polygon_items.clear()
            for polygon in self.polygons:
                polygon_item = QGraphicsPolygonItem(QPolygonF([QPoint(p[0], p[1]) for p in polygon]))
                pen = QPen(Qt.white, 2, Qt.DashLine)
                polygon_item.setPen(pen)
                self.ui.graphicsView.scene().addItem(polygon_item)
                self.polygon_items.append(polygon_item)
            self.old_polygon_items = self.polygon_items.copy()

    def save_scene_as_image(self):
        save_path = self.image_path.split("/")
        save_path[-1] = save_path[-1].split(".")[0] + "_edited.png" 
        final_save_path = "/".join(save_path)
        for i, polygon_item in enumerate(self.polygon_items):
            if polygon_item.scene() is not None:
                self.ui.graphicsView.scene().removeItem(polygon_item)
        
        for i, polygon_item in enumerate(self.old_polygon_items):
            if polygon_item.scene() is not None:
                self.ui.graphicsView.scene().removeItem(polygon_item)
        scene = self.ui.graphicsView.scene()
        image = QImage(scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        scene.render(painter, QRectF(image.rect()), QRectF(self.image.rect()))
        painter.end()
        image.save(final_save_path)
        self.ui.graphicsView.scene().removeItem(self.image_item)
        self.ui.graphicsView.scene().clear()

    def clear_screen(self):
        for i, polygon_item in enumerate(self.polygon_items):
            if polygon_item.scene() is not None:
                self.ui.graphicsView.scene().removeItem(polygon_item)
        
        for i, polygon_item in enumerate(self.old_polygon_items):
            if polygon_item.scene() is not None:
                self.ui.graphicsView.scene().removeItem(polygon_item)
        self.ui.graphicsView.scene().removeItem(self.image_item)
        self.ui.graphicsView.scene().clear()
        self.drawing = False
        self.moving = False
        self.removing = False

    def draw_on_image(self):
        self.drawing = True
        self.moving = False
        self.removing = False

    def move_on_image(self):
        self.drawing = False
        self.moving = True
        self.removing = False

    def remove_on_image(self):
        self.drawing = False
        self.moving = False
        self.removing = True

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