from math import sin, cos, pi, acos
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem,
                             QVBoxLayout, QPushButton, QWidget, QDockWidget, QListWidget, QMainWindow,
                             QGraphicsTextItem, QLabel, QTabWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox,
                             QMenu, QAction, QStyle, QTextEdit, QTreeWidget, QTreeWidgetItem, QGraphicsWidget,
                             QGraphicsLinearLayout, QCheckBox, QGraphicsSimpleTextItem, QGraphicsObject, QGraphicsItem,
                             QGraphicsProxyWidget, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QPen, QPolygonF, QFont, QPainterPath, QPainter, QFontMetrics, QColor, QIcon, QTextCursor
from PyQt5.QtCore import Qt, QPointF, QLineF, QSize, QRectF, QTimer
from collections import defaultdict, deque
import re

class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.node_counter = defaultdict(int)
        self.allocated_boundaries = []

        # Create the menu bar
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        viewMenu = menuBar.addMenu("&View")
        optionsMenu = menuBar.addMenu("&Options")
        helpMenu = menuBar.addMenu("&Help")

        fileMenu.addAction("&Open")
        fileMenu.addAction("&Save")
        fileMenu.addAction("&Import Metadata")
        fileMenu.addAction("&Modify Metadata")

        optionsMenu.addAction("&Scheduler")

        # Buttons
        self.validate_button = QPushButton('Validate')
        self.validate_button.setIcon(QIcon('check.ico'))  # Replace with the path to your validate icon
        self.validate_button.setIconSize(QSize(16, 16))  # Adjust icon size to your liking
        self.validate_button.clicked.connect(self.validate)

        self.run_button = QPushButton('Run')
        self.run_button.setIcon(QIcon('greenplay.ico'))  # Replace with the path to your run icon
        self.run_button.setIconSize(QSize(16, 16))  # Adjust icon size to your liking
        self.run_button.clicked.connect(self.run)

        # GraphWidget
        self.graphWidget = GraphWidget(self)

        # Camera snap button
        self.snap_button = QPushButton('Snap to Center')
        self.snap_button.clicked.connect(self.graphWidget.snap_to_center)

        # Zoom controls
        self.zoom_in_button = QPushButton('Zoom In')
        self.zoom_out_button = QPushButton('Zoom Out')
        self.zoom_level_dropdown = QComboBox()
        self.zoom_level_dropdown.addItems(['100%', '75%', '50%', 'Custom'])

        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_level_dropdown.currentTextChanged.connect(self.set_zoom_level)

        # Console
        self.consoleDock = QDockWidget("Console", self)
        self.console = Console(self)
        self.consoleDock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.consoleDock)
        self.consoleDock.setFloating(False)
        self.consoleDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.consoleDock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.consoleDock.setMinimumHeight(100)  # Set smaller default size
        self.consoleDock.setMaximumHeight(200)  # Set smaller maximum size
        self.console.append('>>> ')

        # Container widget for GraphWidget and buttons
        self.container_widget = QWidget()
        container_layout = QVBoxLayout(self.container_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.validate_button)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.zoom_in_button)
        button_layout.addWidget(self.zoom_out_button)
        button_layout.addWidget(self.zoom_level_dropdown)
        button_layout.addWidget(self.snap_button)
        button_layout.addStretch()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        button_layout.setSpacing(0)  # Remove space between elements

        container_layout.addLayout(button_layout)
        container_layout.addWidget(self.graphWidget)

        # Set container widget as central widget
        self.setCentralWidget(self.container_widget)

        # Function Table
        self.function_table = QTableWidget()
        self.function_table.setColumnCount(3)
        self.function_table.setHorizontalHeaderLabels(['Function', 'In-Nodes', 'Out-Nodes'])
        function_data = [['bene_generator.py', '1', '1'], ['data_parse.py', '1', 'n'], ['mixed_model_kickoff_csv.py', 'n', 'n'], ['compare.py', 'n', '1'], ['bene_compare.py', '1', '1']]
        self.function_table.setRowCount(len(function_data))
        for i, row_data in enumerate(function_data):
            for j, data in enumerate(row_data):
                self.function_table.setItem(i, j, QTableWidgetItem(str(data)))

        # Utility Table
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(3)
        self.input_table.setHorizontalHeaderLabels(['Utility', 'In-Nodes', 'Out-Nodes'])
        input_data = [['Start', '0', '1'], ['End', '1', '0'], ['Input File', '1', 'n'], ['Halt', '1', '1'], ['Resume', '1', '1']]
        self.input_table.setRowCount(len(input_data))
        for i, row_data in enumerate(input_data):
            for j, data in enumerate(row_data):
                self.input_table.setItem(i, j, QTableWidgetItem(str(data)))

        # Active Items
        self.activeItemsDock = QDockWidget("Active Items", self)
        self.activeItemsTree = QTreeWidget()
        self.activeItemsTree.setHeaderHidden(True)
        self.activeItemsDock.setWidget(self.activeItemsTree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.activeItemsDock)
        self.activeItemsDock.setFloating(False)
        self.activeItemsDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.activeItemsDock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.activeItemsDock.setMinimumWidth(150)  # Set smaller default size
        self.activeItemsDock.setMaximumWidth(200)  # Set smaller maximum size

        # Controls
        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_item)
        self.add_button.setFixedSize(100, 30)
        self.add_button.setEnabled(False)  # Disabled by default
        self.function_table.clicked.connect(lambda: self.add_button.setEnabled(True))  # Enable when a row is clicked
        self.input_table.clicked.connect(lambda: self.add_button.setEnabled(True))  # Enable when a row is clicked

        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setFixedSize(100, 30)

        self.start_connection_button = QPushButton('Start Connection')
        self.start_connection_button.setCheckable(True)
        self.start_connection_button.toggled.connect(self.toggle_connection_mode)
        self.start_connection_button.setFixedSize(100, 30)

        self.allocate_button = QPushButton('Allocate')
        self.allocate_button.clicked.connect(self.allocate)
        self.allocate_button.setFixedSize(100, 30)

        self.dock = QDockWidget("Junction Palette", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        self.tabWidget = QTabWidget(self.dock)

        self.functionTab = QWidget()
        self.inputsTab = QWidget()

        self.tabWidget.addTab(self.functionTab, "Functions")
        self.tabWidget.addTab(self.inputsTab, "Utilities")

        self.dock.setWidget(self.tabWidget)

        self.functionLayout = QVBoxLayout(self.functionTab)
        self.functionLayout.addWidget(self.function_table)

        self.inputsLayout = QVBoxLayout(self.inputsTab)
        self.inputsLayout.addWidget(self.input_table)

        self.buttonsDock = QDockWidget("Controls", self)
        self.buttonsDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.buttonsDock)

        buttonsWidget = QWidget()
        buttonsLayout = QVBoxLayout()
        buttonsLayout.addWidget(self.add_button)
        buttonsLayout.addWidget(self.delete_button)
        buttonsLayout.addWidget(self.start_connection_button)
        buttonsLayout.addWidget(self.allocate_button)
        buttonsWidget.setLayout(buttonsLayout)

        self.buttonsDock.setWidget(buttonsWidget)
        self.buttonsDock.setMinimumHeight(150)  # Set smaller default size
        self.buttonsDock.setMaximumHeight(200)  # Set smaller maximum size

        self.buttonsDock.setWidget(buttonsWidget)

    def showEvent(self, event):
        self.resize(1200, 800)

    def add_item(self):
        if self.tabWidget.currentIndex() == 0:  # Function tab
            selected_item = self.function_table.item(self.function_table.currentRow(), 0).text()
        else:  # Input tab
            selected_item = self.input_table.item(self.input_table.currentRow(), 0).text()
        self.node_counter[selected_item] += 1
        node_name = f'{selected_item}{self.node_counter[selected_item]}'
        self.graphWidget.add_node(selected_item, node_name, self)  # pass mainWidget instance here

        # Add the node_name to the Active Items dock
        self.activeItemsTree.addTopLevelItem(QTreeWidgetItem([node_name]))

        self.add_button.setEnabled(False)

    def delete_selected(self):
        for item in self.graphWidget.scene().selectedItems():
            if isinstance(item, Node):
                # Remove item from active items tree
                for i in range(self.activeItemsTree.topLevelItemCount()):
                    if self.activeItemsTree.topLevelItem(i).text(0) == item.node_name:  # Use `node_name` instead
                        self.activeItemsTree.takeTopLevelItem(i)
                        break

                # Correctly remove the edges associated with the node
                for edge in item.edges:
                    # Remove edge from the other node
                    if edge.source_node is item:
                        edge.dest_node.edges.remove(edge)
                    else:
                        edge.source_node.edges.remove(edge)

                    # Remove edge from the scene
                    self.graphWidget.scene().removeItem(edge)

                # Remove item from the scene
                self.graphWidget.scene().removeItem(item)

    def toggle_connection_mode(self, checked):
        if checked:
            self.graphWidget.start_adding_edges()
        else:
            self.graphWidget.stop_adding_edges()

        # Update the tree
        self.update_tree()

    def allocate(self):
        # Clear any existing boundaries
        for boundary in self.allocated_boundaries:
            self.graphWidget.scene().removeItem(boundary)
        self.allocated_boundaries = []

        visited = {}
        for item in self.graphWidget.scene().items():
            if isinstance(item, Node):
                visited[item] = False

        process_counter = 1
        for node, visit_status in visited.items():
            if not visit_status:
                bounding_rect = self.graphWidget.dfs(node, visited)
                boundary = self.graphWidget.draw_process_boundary(bounding_rect, process_counter)
                self.allocated_boundaries.append(boundary)
                process_counter += 1

    def zoom_in(self):
        self.graphWidget.scale(1.2, 1.2)

    def zoom_out(self):
        self.graphWidget.scale(1 / 1.2, 1 / 1.2)

    def set_zoom_level(self, level):
        if level == 'Custom':
            return
        scale = int(level[:-1]) / 100
        self.graphWidget.resetTransform()  # Reset zoom level to 100%
        self.graphWidget.scale(scale, scale)

    def validate(self):
        # Add the code to validate your setup here
        self.console.log("Validating...")  # Use the console to log messages
        self.validate_chain()

    def validate_chain(self):
        # Traverse each chain in the graph
        chains = self.graphWidget.get_chains()
        print(chains)
        if not chains:
            self.console.log("Validation Failed: No chains found in the graph.")
            self.console.log(">>> ")
            return

        all_chains_valid = True  # flag to track if all chains are valid

        for i, chain in enumerate(chains, 1):
            # Print the chain
            chain_names = [node.node_name for node in chain]
            self.console.log(f"Chain {i}: {chain_names}")

            # Check if chain has a defined start and end
            if not self.graphWidget.chain_has_start_and_end(chain):
                self.console.log(f"Validation Failed: Chain {chain_names} does not have a defined start and end.")
                all_chains_valid = False
                continue  # move to the next chain

            # Check that every node in the chain respects the in-nodes and out-nodes rules
            for node in chain:
                if not self.graphWidget.node_respects_rules(node):
                    self.console.log(f"Validation Failed: Node {node.node_name} in chain {chain_names} does not respect the in-nodes and out-nodes rules.")
                    all_chains_valid = False
                    break  # move to the next chain

            # Check that the chain is properly directed
            if not self.graphWidget.chain_is_properly_directed(chain):
                self.console.log(f"Validation Failed: Chain {chain_names} is not properly directed.")
                all_chains_valid = False
                continue  # move to the next chain

        if all_chains_valid:
            self.console.log("Validation Successful: All chains are valid.")
        else:
            self.console.log("Validation Failed: Not all chains are valid.")

        self.console.log(">>> ")

    def run(self):
        # Add the code to run your setup here
        self.console.log("Running...")
        # If the run is successful:
        self.console.log("Run successful!")
        # If the run fails:
        self.console.log("Run failed!")

    def update_tree(self):
        self.activeItemsTree.clear()
        for item in self.graphWidget.scene().items():
            if isinstance(item, Node):
                node_name = item.node_name  # Use the `node_name` attribute instead of `text.toPlainText()`
                node_item = QTreeWidgetItem([node_name])
                self.activeItemsTree.addTopLevelItem(node_item)
                for edge in item.edges:
                    if edge.source_node is item:
                        connected_node_name = edge.dest_node.node_name  # Use the `node_name` attribute
                        connected_node_item = QTreeWidgetItem([f'From: {connected_node_name}'])
                        node_item.addChild(connected_node_item)
                    if edge.dest_node is item:
                        connected_node_name = edge.source_node.node_name  # Use the `node_name` attribute
                        connected_node_item = QTreeWidgetItem([f'To: {connected_node_name}'])
                        node_item.addChild(connected_node_item)


    #console functions

    def create_function(self, function_name):
        # Check if function exists in function table
        for row in range(self.function_table.rowCount()):
            if self.function_table.item(row, 0).text() == function_name:
                # Function exists, create it
                self.node_counter[function_name] += 1
                node_name = f'{function_name}{self.node_counter[function_name]}'
                self.graphWidget.add_node(function_name, node_name, mainWidget)  # pass original name and node_name here
                self.activeItemsTree.addTopLevelItem(QTreeWidgetItem([node_name]))  # Add item to active items tree
                self.console.log(f"Function '{function_name}' created.")
                return
        self.console.log(f"No function '{function_name}'.")

    def delete_function(self, function_name):
        # Check if function exists in scene
        items_to_delete = []
        for item in self.graphWidget.scene().items():
            if isinstance(item, Node) and item.node_name.startswith(function_name):  # Use `node_name` instead
                items_to_delete.append(item)

        for item in items_to_delete:
            # Correctly remove the edges associated with the node
            for edge in item.edges:
                # Remove edge from the other node
                if edge.source_node is item:
                    edge.dest_node.edges.remove(edge)
                else:
                    edge.source_node.edges.remove(edge)

                # Remove edge from the scene
                self.graphWidget.scene().removeItem(edge)

            # Remove item from the scene
            self.graphWidget.scene().removeItem(item)

            # Remove item from active items tree
            for i in range(self.activeItemsTree.topLevelItemCount()):
                if self.activeItemsTree.topLevelItem(i).text(0) == item.node_name:
                    self.activeItemsTree.takeTopLevelItem(i)
                    break

        if items_to_delete:
            self.console.log(f"Function '{function_name}' deleted.")
            self.update_tree()  # Update the tree
        else:
            self.console.log(f"No function '{function_name}'.")



    def connect_functions(self, source_name, dest_name):
        # Find the source and destination nodes
        source_node = None
        dest_node = None
        for item in self.graphWidget.scene().items():
            if isinstance(item, Node):
                if item.node_name.startswith(source_name):  # Use `node_name` instead
                    source_node = item
                elif item.node_name.startswith(dest_name):  # Use `node_name` instead
                    dest_node = item
        if source_node and dest_node:
            edge = Edge(source_node, dest_node)
            self.graphWidget.scene().addItem(edge)
            self.update_tree()  # Update the tree
            self.console.log(f"Connected '{source_name}' to '{dest_name}'.")
        else:
            if not source_node:
                self.console.log(f"No function '{source_name}'.")
            if not dest_node:
                self.console.log(f"No function '{dest_name}'.")

class Console(QTextEdit):
    def __init__(self, mainWidget):
        super().__init__()
        self.mainWidget = mainWidget
        self.setReadOnly(False)
        self.setStyleSheet("background-color: white; color: black;")  # Set dark background and white text

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            command = self.toPlainText().split('\n')[-1][4:]  # Strip the '>>> ' from the command
            self.process_command(command)
            self.append('>>> ')
        else:
            super().keyPressEvent(event)

    def process_command(self, command):
        if command.startswith('do ['):
            # Check if the closing brackets exist
            if ']:' not in command or command[-1] != '}':
                self.log('Invalid "do" loop syntax. Correct syntax is "do [num]: {command}".')
                return
            num_end_index = command.find(']')
            num_times = command[4:num_end_index]
            try:
                num_times = int(num_times)
                if num_times > 100:
                    self.log('Number of repetitions exceeds the limit of 100.')
                    return
            except ValueError:
                self.log('Invalid number of repetitions.')
                return

            sub_command = command[num_end_index+3:-1].strip()  # Extract the command within the brackets
            sub_command = sub_command[1:-1]  # Strip the '{' and '}' from the command
            for _ in range(num_times):
                self.process_command(sub_command)
        elif command.startswith('create('):
            function_name = command[7:]
            if function_name.endswith(')'):
                function_name = function_name[:-1]
            self.mainWidget.create_function(function_name)
        elif command.startswith('delete('):
            function_name = command[7:]
            if function_name.endswith(')'):
                function_name = function_name[:-1]
            self.mainWidget.delete_function(function_name)
        elif command.startswith('connect('):
            function_names = command[8:]
            if function_names.endswith(')'):
                function_names = function_names[:-1]
            function_names = function_names.split(' to ')
            if len(function_names) == 2:
                self.mainWidget.connect_functions(*function_names)
            else:
                self.log('Command not recognized: ' + command)
        elif command == 'clear':
            self.clear_log()
        else:
            self.log('Command not recognized: ' + command)


    def log(self, message):
        self.append(message)

    def clear_log(self):
        self.clear()

class Node(QGraphicsObject):
    def __init__(self, name, node_name, mainWidget):
        super().__init__()

        self.mainWidget = mainWidget
        self.name = name
        self.node_name = node_name
        self.edges = []

        unicode_dict = {
            'Start': '\u25B6',
            'End': '\u23F9',
            'Halt': '\u23F8',
            'Resume': '\u23E9',
            'Input File': '\U0001F4C1'
        }
        self.is_utility = self.name in unicode_dict
        display_text = self.node_name
        if self.is_utility:
            display_text = f'{unicode_dict[self.name]} {self.node_name}'

        self.label = QGraphicsSimpleTextItem(display_text, self)
        self.label.setZValue(1)  # Make the text be drawn on top
        self.label.setPos(10, 10)  # Add a margin around the text

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)  # Reduce spacing between buttons
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        if self.name == 'Input File':
            self.view_files_button = QPushButton("View Files")
            self.view_files_button.setFixedSize(100, 20)  # Smaller button
            self.view_files_button.setStyleSheet("color: black; border: 1px solid black;")  # Set darker text color and add thin border
            self.layout.addWidget(self.view_files_button)

        if not self.is_utility:
            self.view_nodes_button = QPushButton("View Nodes")
            self.view_nodes_button.setFixedSize(100, 20)  # Smaller button
            self.view_nodes_button.setStyleSheet("color: black; border: 1px solid black;")  # Set darker text color and add thin border
            self.layout.addWidget(self.view_nodes_button)

            self.details_button = QPushButton("Details")
            self.details_button.setFixedSize(100, 20)  # Smaller button
            self.details_button.setStyleSheet("color: black; border: 1px solid black;")  # Set darker text color and add thin border
            self.layout.addWidget(self.details_button)

        self.checkbox = QCheckBox("Disable/Enable Function")
        self.checkbox.setStyleSheet("color: black; border: none;")  # Set darker text color and remove border
        self.checkbox.stateChanged.connect(self.change_activity_state)
        self.layout.addWidget(self.checkbox)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.widget.setFixedSize(160, 110 if self.name == 'Input File' else (70 if self.is_utility else 140))  # Taller widget for 'Input File' utility node
        self.widget.setStyleSheet("border: 1px solid black; background-color: #F0F0F0;" if self.is_utility else "border: 2px solid black; background-color: #FFFFFF;")

        self.proxyWidget = QGraphicsProxyWidget(self)
        self.proxyWidget.setWidget(self.widget)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.border = QGraphicsRectItem(self.boundingRect(), self)
        self.border.setPen(QPen(Qt.NoPen))  # Invisible by default

    def boundingRect(self):
        return self.proxyWidget.boundingRect()

    def paint(self, painter, option, widget=None):
        pass

    def change_activity_state(self, state):
        if state == Qt.Checked:
            self.widget.setStyleSheet("background-color: gray; border: 1px solid black;" if self.is_utility else "background-color: #A0A0A0; border: 2px solid black;")  # Different inactive state color for utility nodes
        else:
            self.widget.setStyleSheet("border: 1px solid black; background-color: #F0F0F0;" if self.is_utility else "border: 2px solid black; background-color: #FFFFFF;")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.mainWidget.graphWidget.stop_adding_edges()  # Stop adding edges
            self.mainWidget.update_tree()  # Update the tree
            # Clear any allocated boundaries
            for boundary in self.mainWidget.allocated_boundaries:
                self.mainWidget.graphWidget.scene().removeItem(boundary)
            self.mainWidget.allocated_boundaries = []

            # Adjust all edges connected to this node
            for edge in self.edges:
                edge.adjust()
                
        return super().itemChange(change, value)

    def highlight(self):
        self.border.setPen(QPen(Qt.black, 2, Qt.DashLine))  # Make border visible
        self.border_timer = QTimer()
        self.border_timer.timeout.connect(self.toggle_border)
        self.border_timer.start(500)  # Change border style every 500 ms

    def unhighlight(self):
        self.border.setPen(QPen(Qt.NoPen))  # Make border invisible
        if hasattr(self, 'border_timer'):
            self.border_timer.stop()  # Stop the timer

    def toggle_border(self):
        if self.border.pen().style() == Qt.SolidLine:
            self.border.setPen(QPen(Qt.black, 2, Qt.DashLine))
        else:
            self.border.setPen(QPen(Qt.black, 2, Qt.SolidLine))

class Edge(QGraphicsLineItem):
    def __init__(self, source_node, dest_node):
        super().__init__()

        self.source_node = source_node
        self.dest_node = dest_node
        self.source_node.edges.append(self)
        self.dest_node.edges.append(self)

        self.setPen(QPen(Qt.black, 2))
        self.adjust()

        # Enable the itemIsSelectable flag to allow for double-click events
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)

        # Set the ZValue to a negative value to make the line appear behind other items
        self.setZValue(-1)

    def adjust(self):
        if not self.source_node or not self.dest_node:
            return
        line = QLineF(self.source_node.sceneBoundingRect().center(), 
                      self.dest_node.sceneBoundingRect().center())
        self.setLine(line)

    def paint(self, painter, option, widget=None):
        line = self.line()
        if line.length() == 0:
            return

        # Draw the line itself
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.drawLine(line)

        # Draw the arrow
        angle = acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (pi * 2) - angle

        arrow_p1 = line.pointAt(0.5) + QPointF(sin(angle + pi / 3) * 10, cos(angle + pi / 3) * 10)
        arrow_p2 = line.pointAt(0.5) + QPointF(sin(angle + pi - pi / 3) * 10, cos(angle + pi - pi / 3) * 10);

        painter.setBrush(Qt.black)
        painter.drawPolygon(QPolygonF([line.pointAt(0.5), arrow_p1, arrow_p2]))

        # Highlight the line when selected
        if option.state & QStyle.State_Selected:
            highlight_line = line
            highlight_line.setLength(highlight_line.length() + 20)  # Extend the line length
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            painter.drawLine(highlight_line)

    def mouseDoubleClickEvent(self, event):
        # On double click, swap the source and destination nodes
        self.source_node, self.dest_node = self.dest_node, self.source_node
        self.adjust()

        # Update the active items tree
        self.scene().views()[0].mainWidget.update_tree()


    def contextMenuEvent(self, event):
        context_menu = QMenu()
        delete_action = QAction("Delete", context_menu)
        delete_action.triggered.connect(self.delete)
        context_menu.addAction(delete_action)

        change_direction_action = QAction("Change direction", context_menu)
        change_direction_action.triggered.connect(self.change_direction)
        context_menu.addAction(change_direction_action)

        context_menu.exec_(event.screenPos())

    def delete(self):
        self.source_node.edges.remove(self)
        self.dest_node.edges.remove(self)
        self.scene().removeItem(self)

    def change_direction(self):
        self.source_node, self.dest_node = self.dest_node, self.source_node
        self.adjust()

class GraphWidget(QGraphicsView):
    def __init__(self, mainWidget):
        super().__init__()

        self.setScene(QGraphicsScene(self))
        self.mainWidget = mainWidget
        self.start_node = None
        self.adding_edges = False
        self.last_node_position = QPointF(0, 0)
        self.setBackgroundBrush(Qt.lightGray)
        self.setRenderHint(QPainter.Antialiasing)
        self.highlighted_node = None

    def drawBackground(self, painter, rect):
        # Draw a dot grid on the scene's background
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        first_left = left - (left % 20)
        first_top = top - (top % 20)

        # Draw vertical lines
        x = first_left
        while x < right:
            y = first_top
            while y < bottom:
                painter.drawPoint(x, y)
                y += 20
            x += 20

    def snap_to_center(self):
        # Calculate the bounding rectangle of all nodes
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        if not nodes:
            return

        # Calculate bounding rectangle encompassing all nodes
        bounding_rect = QRectF(nodes[0].sceneBoundingRect())
        for node in nodes[1:]:
            bounding_rect = bounding_rect.united(node.sceneBoundingRect())

        # Adjust view to fit the bounding rectangle of all nodes, and center on it
        self.fitInView(bounding_rect, Qt.KeepAspectRatio)
        self.centerOn(bounding_rect.center())

    def add_node(self, name, node_name, mainWidget):
        node = Node(name, node_name, mainWidget)  # pass mainWidget instance here
        node.setPos(self.last_node_position)
        self.last_node_position += QPointF(60, 60)
        self.scene().addItem(node)

    def delete_selected(self):
        for item in self.scene().selectedItems():
            if isinstance(item, Node):
                # Logic to remove nodes from the "active items tree"
                if hasattr(item, 'node_name'):
                    active_tree = None
                    # Determine the correct reference to the activeItemsTree, depending on the structure of the code
                    if hasattr(self, 'mainWidget'):
                        active_tree = self.mainWidget.activeItemsTree
                    elif hasattr(self, 'parent') and hasattr(self.parent(), 'activeItemsTree'):
                        active_tree = self.parent().activeItemsTree
                    
                    if active_tree:
                        for i in range(active_tree.topLevelItemCount()):
                            if active_tree.topLevelItem(i).text(0) == item.node_name:
                                active_tree.takeTopLevelItem(i)
                                break

                # Correctly remove the edges associated with the node
                for edge in item.edges:
                    # Remove edge from the other node
                    if edge.source_node is item:
                        edge.dest_node.edges.remove(edge)
                    else:
                        edge.source_node.edges.remove(edge)
                    
                    # Remove edge from the scene
                    self.scene().removeItem(edge)

            # Logic to remove edges from the "active items tree"
            elif isinstance(item, Edge):
                active_tree = None
                # Determine the correct reference to the activeItemsTree, depending on the structure of the code
                if hasattr(self, 'mainWidget'):
                    active_tree = self.mainWidget.activeItemsTree
                elif hasattr(self, 'parent') and hasattr(self.parent(), 'activeItemsTree'):
                    active_tree = self.parent().activeItemsTree
                
                edge_name = f"{item.source_node.node_name} -> {item.dest_node.node_name}"  # Assuming this format for edge representation
                
                if active_tree:
                    for i in range(active_tree.topLevelItemCount()):
                        if active_tree.topLevelItem(i).text(0) == edge_name:
                            active_tree.takeTopLevelItem(i)
                            break

            # Remove item from the scene
            self.scene().removeItem(item)
        # Immediately update the active items tree after deletions
        if hasattr(self, 'mainWidget') and hasattr(self.mainWidget, 'update_tree'):
            self.mainWidget.update_tree()
        elif hasattr(self, 'update_tree'):
            self.update_tree()
    

    def mousePressEvent(self, event):
        if self.adding_edges:
            pos = self.mapToScene(event.pos())
            items = self.scene().items(pos)
            if items:
                item = items[0]
                if isinstance(item, Node) or isinstance(item.parentItem(), Node):
                    node = item if isinstance(item, Node) else item.parentItem()
                    if self.start_node is None:
                        self.start_node = node
                        self.start_node.highlight()  # Highlight the start node
                        self.highlighted_node = self.start_node
                    elif node is not self.start_node:
                        edge = Edge(self.start_node, node)
                        self.scene().addItem(edge)
                        self.start_node.unhighlight()  # Unhighlight the start node
                        self.start_node = None
                        self.highlighted_node = None
                        self.mainWidget.update_tree()  # Update the tree
                    elif node is self.start_node:
                        self.start_node.unhighlight()  # Unhighlight the start node if clicked again
                        self.start_node = None
                        self.highlighted_node = None
        super().mousePressEvent(event)

    def start_adding_edges(self):
        self.adding_edges = True
        self.setMouseTracking(True)

    def stop_adding_edges(self):
        self.adding_edges = False
        self.start_node = None
        self.setMouseTracking(False)
        if self.temp_line:
            self.scene().removeItem(self.temp_line)
            self.temp_line = None
        if self.highlighted_node:  # If a node is highlighted, unhighlight it
            self.highlighted_node.unhighlight()
            self.highlighted_node = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
        super().keyPressEvent(event)

    def start_adding_edges(self):
        self.adding_edges = True

    def stop_adding_edges(self):
        self.adding_edges = False
        self.start_node = None

    def dfs(self, node, visited):
        if visited[node]:
            # Skip this node because it's already been visited
            return QRectF()

        visited[node] = True
        bounding_rect = node.sceneBoundingRect()
        for edge in node.edges:
            if edge.source_node is node:
                other_node = edge.dest_node
            else:
                other_node = edge.source_node
            other_bounding_rect = self.dfs(other_node, visited)
            bounding_rect = bounding_rect.united(other_bounding_rect)
        
        return bounding_rect

    def draw_process_boundary(self, bounding_rect, process_counter):
        boundary = QGraphicsRectItem(bounding_rect)
        boundary.setPen(QPen(Qt.black, 1, Qt.DotLine))
        self.scene().addItem(boundary)

        label = QGraphicsTextItem(f'process{process_counter}', boundary)
        label.setPos(bounding_rect.topLeft() - QPointF(0, label.boundingRect().height()))

        return boundary

    #validate

    def get_all_nodes(self):
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        print(f"Found {len(nodes)} nodes in the scene.")
        return nodes

    def is_start_node(self, node):
        is_start = node.node_name.startswith("Start")
        print(f"Node '{node.node_name}' is a start node: {is_start}")
        return is_start

    def is_end_node(self, node):
        is_end = node.node_name.startswith("End")
        print(f"Node '{node.node_name}' is an end node: {is_end}")
        return is_end

    def bfs(self, start_node):
        queue = deque([[start_node]])
        valid_chains = []
        while queue:
            chain = queue.popleft()
            node = chain[-1]
            print(f"Current node: {node.node_name}")
            for edge in node.edges:
                if edge.source_node is node:
                    other_node = edge.dest_node
                else:
                    other_node = edge.source_node
                if other_node not in chain:  # only add new node if it's not already in the chain
                    new_chain = list(chain)
                    new_chain.append(other_node)
                    queue.append(new_chain)
                    if self.is_end_node(other_node):
                        valid_chains.append(new_chain)  # Add the chain to valid_chains only if it ends with an 'End' node
        print(f"Found {len(valid_chains)} valid chains from node '{start_node.node_name}'.")
        return valid_chains

    def get_chains(self):
        chains = []
        all_nodes = self.get_all_nodes()  # get all nodes in the scene
        start_nodes = [node for node in all_nodes if self.is_start_node(node)]
        end_nodes = [node for node in all_nodes if self.is_end_node(node)]

        if not all_nodes:
            #self.mainWidget.console.log("Validation Failed: No chains found in the graph.")
            return []

        # If there are no 'Start' or 'End' nodes, perform a DFS from each unvisited node
        if not start_nodes or not end_nodes:
            visited = {node: False for node in all_nodes}
            for node in all_nodes:
                if not visited[node]:
                    chain = self.dfs_chain(node, visited)
                    chains.append(chain)
            for chain in chains:
                if not self.chain_has_start_and_end(chain):
                    chain_names = [node.node_name for node in chain]
                    #self.mainWidget.console.log(f"Validation Failed: Chain {chain_names} does not have a defined start and end.")
                    return chains
        else:
            for start_node in start_nodes:
                chains_from_node = self.bfs(start_node)
                chains.extend(chains_from_node)

        for chain in chains:
            # Check if each node respects the rules for in-nodes and out-nodes
            for node in chain:
                if not self.node_respects_rules(node):
                    #self.mainWidget.console.log(f"Chain from '{chain[0].node_name}' to '{chain[-1].node_name}' is invalid: node '{node.node_name}' does not respect the rules for in-nodes and out-nodes.")
                    return chains
            # Check if the chain is properly directed
            if not self.chain_is_properly_directed(chain):
                self.mainWidget.console.log(f"Chain from '{chain[0].node_name}' to '{chain[-1].node_name}' is invalid: it is not properly directed.")
                return chains
            # If the chain has passed all the checks, it's valid
            #self.mainWidget.console.log(f"Chain from '{chain[0].node_name}' to '{chain[-1].node_name}' is valid.")

        return chains

    def dfs_chain(self, start_node, visited):
        stack = [start_node]
        chain = []
        while stack:
            node = stack.pop()
            if not visited[node]:
                visited[node] = True
                chain.append(node)
                for edge in node.edges:
                    if edge.source_node is node:
                        other_node = edge.dest_node
                    else:
                        other_node = edge.source_node
                    if not visited[other_node]:
                        stack.append(other_node)
        return chain


    def chain_has_start_and_end(self, chain):
        return self.is_start_node(chain[0]) and self.is_end_node(chain[-1])

    def get_in_out_nodes(self, node):
        in_nodes = sum(1 for edge in node.edges if edge.source_node is node)
        out_nodes = sum(1 for edge in node.edges if edge.dest_node is node)
        print(f"Node '{node.node_name}' has {in_nodes} in-nodes and {out_nodes} out-nodes.")
        return in_nodes, out_nodes

    def node_respects_rules(self, node):
        in_nodes, out_nodes = self.get_in_out_nodes(node)
        return self.respects_in_nodes_rules(node, in_nodes) and self.respects_out_nodes_rules(node, out_nodes)

    def respects_in_nodes_rules(self, node, in_nodes):
        # Adjust this function based on your rules
        if node.node_name.startswith("Start"):
            is_respected = in_nodes == 0
        elif node.node_name.startswith("End"):
            is_respected = in_nodes == 1
        else:
            is_respected = in_nodes >= 1
        print(f"In-nodes rules are respected by node '{node.node_name}': {is_respected}")
        return is_respected

    def respects_out_nodes_rules(self, node, out_nodes):
        # Adjust this function based on your rules
        if node.node_name.startswith("Start"):
            is_respected = out_nodes == 1
        elif node.node_name.startswith("End"):
            is_respected = out_nodes == 0
        else:
            is_respected = out_nodes >= 1
        print(f"Out-nodes rules are respected by node '{node.node_name}': {is_respected}")
        return is_respected

    def is_directed_from_to(self, node1, node2):
        print(f"All edges of {node1.node_name}:")
        for edge in node1.edges:
            print(f"Edge from {edge.source_node.node_name} to {edge.dest_node.node_name}")
        result = any(edge.dest_node is node2 for edge in node1.edges)
        print(f"Checking if {node1.node_name} is directed to {node2.node_name}: {result}")
        return result

    def chain_is_properly_directed(self, chain):
        # Check if all consecutive nodes in the chain are properly directed
        result = True
        for i in range(len(chain) - 1):
            node1 = chain[i]
            node2 = chain[i+1]
            in_nodes1, out_nodes1 = self.get_in_out_nodes(node1)
            in_nodes2, out_nodes2 = self.get_in_out_nodes(node2)
            if not (out_nodes1 > 0 and in_nodes2 > 0):
                result = False
                print(f"Chain from {node1.name} to {node2.name} is not properly directed.")
                break
        print(f"Checking if chain is properly directed: {result}")
        return result

app = QApplication([])
mainWidget = MainWidget()
mainWidget.resize(800, 600)  # Set the default size of the application window to be larger
mainWidget.show()
app.exec_()