import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QGridLayout, 
                             QDialog, QMenuBar, QMenu, QGraphicsView, QGraphicsScene, QLabel, QComboBox)
# Assuming you have a file named wizard.py with a class named ProjectWizard. If not, please comment this line.
from wizard import ProjectWizard  
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QAction

class LandingPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Process Flow Automator")
        self.setGeometry(100, 100, 800, 600)

        # Setup the ribbon menus
        menu_bar = QMenuBar(self)
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        view_menu = QMenu("View", self)
        options_menu = QMenu("Options", self)
        help_menu = QMenu("Help", self)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(view_menu)
        menu_bar.addMenu(options_menu)
        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)

        # Populate the File menu
        create_action = QAction("Create", self)
        open_action = QAction("Open", self)
        open_recent_action = QAction("Open Recent", self)
        export_action = QAction("Export", self)
        import_action = QAction("Import", self)
        
        # Only the first three options are enabled
        create_action.setEnabled(True)
        open_action.setEnabled(True)
        open_recent_action.setEnabled(True)
        export_action.setEnabled(False)
        import_action.setEnabled(False)
        
        file_menu.addAction(create_action)
        file_menu.addAction(open_action)
        file_menu.addAction(open_recent_action)
        file_menu.addSeparator()
        file_menu.addAction(export_action)
        file_menu.addAction(import_action)

        # Setup the canvas with a dotted grid
        self.canvas = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(QRectF(self.rect()))
        
        self.canvas.setScene(self.scene)
        self.setCentralWidget(self.canvas)

        # Store grid lines for later removal
        self.grid_lines = []

        self.draw_grid()  # Draw grid initially

        # Add InnerWindow as a widget to the QGraphicsScene
        self.central_widget = InnerWindow(self)
        self.proxy_widget = self.scene.addWidget(self.central_widget)
        # Set the InnerWindow's Z-order to ensure it's above the grid lines
        self.proxy_widget.setZValue(1)
        self.proxy_widget.setPos(self.width() // 4, self.height() // 4)

    def draw_grid(self):
        # Remove the previous grid lines
        for line in self.grid_lines:
            self.scene.removeItem(line)
        self.grid_lines.clear()

        # Draw the grid based on the current window size
        grid_pen = QPen(Qt.gray, 0.5, Qt.DotLine)
        for x in range(0, int(self.scene.width()), 20):
            line = self.scene.addLine(x, 0, x, int(self.scene.height()), grid_pen)
            self.grid_lines.append(line)
        for y in range(0, int(self.scene.height()), 20):
            line = self.scene.addLine(0, y, int(self.scene.width()), y, grid_pen)
            self.grid_lines.append(line)

    def resizeEvent(self, event):
        # Update the scene rect and draw grid
        self.scene.setSceneRect(QRectF(self.rect()))
        self.draw_grid()
        super().resizeEvent(event)


class InnerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.FramelessWindowHint | Qt.Dialog)
        self.setGeometry(parent.width() // 4, parent.height() // 4, parent.width() // 2, parent.height() // 2)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 220); border: 1px solid black;")  # Semi-transparent with border

        layout = QVBoxLayout()

        title_label = QLabel("ProcFlow", self)
        title_label.setStyleSheet("border: none;")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Uniform button sizes
        button_size = (120, 25)
        
        grid_layout = QGridLayout()
        
        self.open_btn = QPushButton("Open")
        self.open_btn.setFixedSize(*button_size)
        grid_layout.addWidget(self.open_btn, 0, 0)

        self.create_btn = QPushButton("Create Project")
        self.create_btn.setFixedSize(*button_size)
        self.create_btn.clicked.connect(self.create_project)
        grid_layout.addWidget(self.create_btn, 0, 1)

        # Dropdown for recent projects
        self.recent_projects = QComboBox()
        self.recent_projects.setFixedSize(*button_size)
        self.recent_projects.addItem("Recent Projects")
        # Dummy recent projects for demonstration
        self.recent_projects.addItems(["Project A", "Project B", "Project C"])
        grid_layout.addWidget(self.recent_projects, 1, 0)

        self.help_btn = QPushButton("Help")
        self.help_btn.setFixedSize(*button_size)
        grid_layout.addWidget(self.help_btn, 1, 1)

        layout.addLayout(grid_layout)
        layout.setSpacing(15)  # Adjust the spacing between the widgets
        self.setLayout(layout)

        # Add a close button to the InnerWindow
        close_button = QPushButton("X", self)
        close_button.setStyleSheet("background-color: red; border: none; color: white; font-weight: bold;")
        close_button.setFixedSize(25, 25)
        close_button.move(self.width() - 30, 5)
        close_button.clicked.connect(self.close)
        
    def create_project(self):
        self.wizard = ProjectWizard()
        self.wizard.show()

    def moveEvent(self, event):
        # Ensure the InnerWindow stays within the boundaries of the LandingPage
        if self.parent():
            rect = self.parent().rect()
            if not rect.contains(event.pos()):
                if event.pos().x() < rect.left():
                    self.move(rect.left(), self.pos().y())
                elif event.pos().x() + self.width() > rect.right():
                    self.move(rect.right() - self.width(), self.pos().y())
                if event.pos().y() < rect.top():
                    self.move(self.pos().x(), rect.top())
                elif event.pos().y() + self.height() > rect.bottom():
                    self.move(self.pos().x(), rect.bottom() - self.height())
        super().moveEvent(event)

    # Overriding the closeEvent to add a close button
    def closeEvent(self, event):
        self.hide()
        event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LandingPage()
    window.show()
    sys.exit(app.exec_())
