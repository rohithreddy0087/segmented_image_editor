import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPoint, QLineF
from PyQt5.QtGui import QPixmap, QPolygonF, QPen, QPainter, QColor

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent, polygon_items):
        super().__init__()
        self.parent = parent
        self.polygon_items = polygon_items
        self.is_dragging = False
        self.current_polygon_item = None
        self.current_polygon_index = None
        self.last_mouse_position = QPoint()
        self.last_position = QPoint()

    def mouseMoveEvent(self, event):
        if self.parent.moving and self.is_dragging:
            new_pos = event.scenePos()
            self.move_polygon(self.current_polygon_item, new_pos, self.last_mouse_position)
            self.last_mouse_position = new_pos
        if self.parent.drawing and self.is_dragging:
            if self.last_position != QPoint():
                pen = QPen(self.parent.draw_color, self.parent.brush_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                line = QGraphicsLineItem(self.last_position.x(), self.last_position.y(), event.scenePos().x(), event.scenePos().y())
                line.setPen(pen)
                self.parent.ui.graphicsView.scene().addItem(line)
            self.last_position = event.scenePos()


    def move_polygon(self, polygon_item, new_position, old_position):
        offset = new_position - old_position
        polygon_item.moveBy(offset.x(), offset.y())
        current_polygon = polygon_item.polygon()
        for i in range(current_polygon.size()):
            point = current_polygon[i]
            new_x = point.x() + offset.x()
            new_y = point.y() + offset.y()
            current_polygon[i] = QPoint(round(new_x), round(new_y))

        new_polygon_item = QGraphicsPolygonItem(current_polygon)
        self.current_polygon_item = new_polygon_item
        self.polygon_items[self.current_polygon_index] = new_polygon_item

    def mousePressEvent(self, event):
        if self.parent.moving and not self.is_dragging:
            for i, polygon_item in enumerate(self.polygon_items):
                polygon = polygon_item.polygon()
                if polygon.containsPoint(event.scenePos(), Qt.OddEvenFill):
                    self.is_dragging = True
                    self.current_polygon_item = polygon_item
                    # self.clear_area_under_polygon(self.current_polygon_item, Qt.white)
                    b,g,r = self.parent.polygon_color[i]
                    self.parent.draw_color = QColor(r,g,b)
                    self.current_polygon_index = i
                    self.last_mouse_position = event.scenePos()
                    break

        if self.parent.drawing and not self.is_dragging:
            self.last_position = event.pos()
            self.is_dragging = True

        if self.parent.removing and not self.is_dragging:
            for i, polygon_item in enumerate(self.polygon_items):
                polygon = polygon_item.polygon()
                if polygon.containsPoint(event.scenePos(), Qt.OddEvenFill):
                    self.is_dragging = True
                    self.current_polygon_item = polygon_item
                    self.clear_area_under_polygon(self.current_polygon_item, Qt.white)
                    self.current_polygon_index = i
                    self.last_mouse_position = event.scenePos()
                    break

    def mouseReleaseEvent(self, event):
        if self.parent.moving and self.is_dragging:
            self.is_dragging = False
            clear_rect = QGraphicsPolygonItem(self.polygon_items[self.current_polygon_index].polygon())
            clear_rect.setBrush(self.parent.draw_color)
            self.addItem(clear_rect)
            self.current_polygon_item = None

        if self.parent.drawing and self.is_dragging:
            self.is_dragging = False
        
        if self.parent.removing and self.is_dragging:
            self.is_dragging = False

    def clear_area_under_polygon(self, polygon_item, color):
        clear_rect = QGraphicsPolygonItem(polygon_item.polygon())
        clear_rect.setBrush(color)
        self.addItem(clear_rect)
