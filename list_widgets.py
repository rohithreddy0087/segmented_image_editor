from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QListWidgetItem
from PyQt5.QtGui import QIcon

class ColorSelectionItemWidget(QListWidgetItem):
    def __init__(self, color, text):
        super().__init__()

        # Create a widget that displays the color and name
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {color.name()};")
        widget.setMinimumSize(20, 20)  # Size of the color box

        self.setIcon(QIcon(widget.grab()) if widget.grab() else QIcon())

        self.setText(text)