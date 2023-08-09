import sys
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QSpinBox
from PySide6.QtGui import QPixmap, QPalette
from PySide6.QtCore import Qt
import io
import igraph as ig
import graph as g

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Graph Visualizer')
        self.setWindowState(Qt.WindowMaximized)

        self.graph = g.Graph()

        # Create a vertical layout and a widget to contain the image and the button
        layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Generate the graph and show it
        self.container_image = QLabel(self)
        self.table_adjacency = QTableWidget(self)
        self.table_adjacency.cellChanged.connect(self.on_cell_changed)
        self.table_adjacency.setMaximumHeight(300)

        layout_result = QVBoxLayout()
        layout_result.setAlignment(Qt.AlignTop)
        
        graph_widget_layout = QHBoxLayout()
        graph_widget = QWidget()
        graph_widget.setLayout(graph_widget_layout)
        layout_result.addWidget(graph_widget)

        self.label_cut_vertices = QLabel('Cut Points:')
        self.label_cut_vertices_list = QLabel('')

        self.label_bridges = QLabel('Bridges:')
        self.label_bridges_list = QLabel('')

        graph_widget_layout.addWidget(self.container_image)

        legends_layout = QVBoxLayout()
        legends_widget = QWidget()
        legends_widget.setLayout(legends_layout)
        legends_widget.setMaximumWidth(200)
        legends_layout.setAlignment(Qt.AlignTop)

        legends_layout.addWidget(self.label_cut_vertices)
        legends_layout.addWidget(self.label_cut_vertices_list)
        legends_layout.addWidget(self.label_bridges)
        legends_layout.addWidget(self.label_bridges_list)

        graph_widget_layout.addWidget(legends_widget)

        layout_result.addWidget(self.table_adjacency)

        widget_result = QWidget()
        widget_result.setLayout(layout_result)
        layout.addWidget(widget_result)

        # Fields
        self.label_vertex = QLabel('Vertexes:')
        self.spin_box_vertex = QSpinBox()
        self.spin_box_vertex.setMinimum(0)
        self.spin_box_vertex.setMaximum(99)
        self.spin_box_vertex.setDisabled(True) # Remove this line to enable the spin box
        self.spin_box_vertex.valueChanged.connect(self.on_vertex_changed)

        self.label_source = QLabel('Source:')
        self.line_edit_source = QLineEdit()

        self.label_target = QLabel('Target:')
        self.line_edit_target = QLineEdit()

        self.label_weight = QLabel('Weight:')
        self.line_edit_weight = QLineEdit()

        # Add edge
        self.add_edge_button = QPushButton('Add Edge', self)
        self.add_edge_button.clicked.connect(self.on_edge_added)

        # Add the refresh button
        self.add_vertex_button = QPushButton('Add Vertex', self)
        self.add_vertex_button.clicked.connect(self.add_vertex)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset_graph)

        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.refresh)

        controls = QWidget()
        controls.setMaximumWidth(200)
        controls_layout = QVBoxLayout()
        controls.setLayout(controls_layout)

        top_controls = QWidget()
        top_controls_layout = QVBoxLayout()
        top_controls.setLayout(top_controls_layout)

        bottom_controls = QWidget()
        bottom_controls_layout = QVBoxLayout()
        bottom_controls.setLayout(bottom_controls_layout)

        controls_layout.addWidget(top_controls)
        controls_layout.addWidget(bottom_controls)

        top_controls_layout.addWidget(self.label_vertex)
        top_controls_layout.addWidget(self.spin_box_vertex)
        top_controls_layout.addWidget(self.label_source)
        top_controls_layout.addWidget(self.line_edit_source)
        top_controls_layout.addWidget(self.label_target)
        top_controls_layout.addWidget(self.line_edit_target)
        top_controls_layout.addWidget(self.label_weight)
        top_controls_layout.addWidget(self.line_edit_weight)
        top_controls_layout.addWidget(self.add_edge_button)

        bottom_controls_layout.addWidget(self.add_vertex_button)
        bottom_controls_layout.addWidget(self.reset_button)
        bottom_controls_layout.addWidget(self.refresh_button)

        top_controls_layout.setAlignment(Qt.AlignTop)
        bottom_controls_layout.setAlignment(Qt.AlignBottom)

        layout.addWidget(controls)

        self.initialize_table_adjacency()
    
    def make_table_item(self, text):
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def on_vertex_changed(self, size):
        graph = g.Graph()
        self.initialize_table_adjacency()

        graph.set_vertices(size)
        
        diff = graph.get_vertices_count() - self.graph.get_vertices_count()
        if diff > 0:
            for _ in range(abs(diff)):
                self.add_column()
        else:
            self.table_adjacency.setColumnCount(graph.get_vertices_count())
            self.table_adjacency.setRowCount(graph.get_vertices_count())

        graph.add_edges(self.graph.get_edgelist())
        for edge in range(min(self.graph.get_edges_count()(), graph.get_edges_count()())):
            for attr_name in self.graph.es.attributes():
                graph.es[edge][attr_name] = self.graph.es[edge][attr_name]
        
        self.graph = graph
        self.refresh_image()
    
    def add_vertex(self):
        self.graph.add_vertex()
        self.refresh_image()
        self.spin_box_vertex.blockSignals(True)
        self.spin_box_vertex.setValue(self.graph.get_vertices_count())
        self.spin_box_vertex.blockSignals(False)
        self.add_column()

    def add_column(self):
        columnCount = self.table_adjacency.columnCount()
        self.table_adjacency.insertColumn(columnCount - 1)
        self.table_adjacency.insertRow(columnCount - 1)
        self.table_adjacency.setHorizontalHeaderItem(columnCount - 1, QTableWidgetItem(str(columnCount - 1)))
        self.table_adjacency.setVerticalHeaderItem(columnCount - 1, QTableWidgetItem(str(columnCount - 1)))

        for i in range(columnCount):
            self.table_adjacency.blockSignals(True)
            self.table_adjacency.setItem(columnCount - 1, i, self.make_table_item("0"))
            self.table_adjacency.setItem(i, columnCount - 1, self.make_table_item("0"))
            self.table_adjacency.blockSignals(False)

    def on_edge_added(self):
        source = self.line_edit_source.text()
        target = self.line_edit_target.text()
        weight = self.line_edit_weight.text()

        if source == "" or target == "" or weight == "":
            return

        self.add_edge(int(source), int(target), int(weight))
        self.refresh()
    
    def add_edge(self, source, target, weight):
        if (source >= self.graph.get_vertices_count() or target >= self.graph.get_vertices_count()):
            return

        weight = weight if weight > 0 else 0

        try:
            self.graph.delete_edge(source, target)
        except:
            pass

        if (weight > 0):
            self.graph.add_edge(source, target, weight)

        self.table_adjacency.blockSignals(True)
        self.table_adjacency.setItem(source, target, self.make_table_item(str(weight)))
        self.table_adjacency.setItem(target, source, self.make_table_item(str(weight)))
        self.table_adjacency.blockSignals(False)

    def on_cell_changed(self, row, column):
        if (row < self.graph.get_vertices_count() and column < self.graph.get_vertices_count()):
            try:
                weight = int(self.table_adjacency.item(row, column).text())
            except:
                weight = 0
            self.add_edge(row, column, weight)
            self.refresh()

    def get_graph(self):
        graph = ig.Graph()
        graph.add_vertices(self.graph.get_vertices_count())
        for edge in self.graph.edges:
            source, target, weight = edge
            graph.add_edge(source, target, weight=weight)

        bg_color = self.palette().color(QPalette.ColorRole.Window).name()

        _, ax = plt.subplots()

        ax.set_facecolor(bg_color)

        ig.plot(
            graph,
            target=ax,
            layout="kk",
            vertex_label=range(self.graph.get_vertices_count()),
            vertex_color="lightblue",
            edge_label=[(self.format_edge_name(i) + " (" + str(graph.es[i]["weight"] if graph.ecount() > 0 else 0) + ")") for i in range(graph.ecount())], 
            edge_background=bg_color,
        )

        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor=bg_color)
        buf.seek(0)
        plt.close()

        return buf
    
    def reset_graph(self):
        self.graph = g.Graph()
        self.initialize_table_adjacency()
        self.refresh()

    def refresh(self):
        self.refresh_image()
        self.refresh_degrees()
        self.refresh_cut_vertices()
        self.refresh_bridges()

    def refresh_cut_vertices(self):
        if (self.graph.is_connected()):
            self.label_cut_vertices_list.setText("".join(str(i) for i in self.graph.get_cut_vertices()))
        else:
            self.label_cut_vertices_list.setText("Graph is not connected")

    def format_edge_name(self, index):
        return "a" + chr(8320 + int(index))

    def refresh_bridges(self):
        if (self.graph.is_connected()):
            self.label_bridges_list.setText(" ".join([str((bridge)) for bridge in self.graph.get_bridges()]))
        else:
            self.label_bridges_list.setText("Graph is not connected")

    def refresh_image(self):
        pixmap = QPixmap()
        if self.graph.get_vertices_count() > 0:
            buf = self.get_graph()
            pixmap.loadFromData(buf.read())
            pixmap.scaled(self.container_image.size(), Qt.KeepAspectRatio)
            buf.close()
        else:
            pixmap.fill(Qt.transparent)
        self.container_image.setPixmap(pixmap)

    def initialize_table_adjacency(self):
        self.table_adjacency.setRowCount(1)
        self.table_adjacency.setColumnCount(1)
        self.table_adjacency.setHorizontalHeaderLabels(['Degrees'] )
        self.table_adjacency.setVerticalHeaderLabels(['Degrees'] )
        item = self.make_table_item("0")
        item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table_adjacency.setItem(0, 0, item)

    def refresh_degrees(self):
        columnCount = self.table_adjacency.columnCount()
        vertexCount = self.graph.get_vertices_count()
        for i in range(columnCount - 1):
            self.table_adjacency.setRowHeight(vertexCount, 30)
            self.table_adjacency.setColumnWidth(vertexCount, 90)
            item = self.make_table_item(str(self.graph.get_degrees()[i] if vertexCount > 0 else 0))
            item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table_adjacency.blockSignals(True)
            self.table_adjacency.setItem(vertexCount, i, item.clone())
            self.table_adjacency.setItem(i, vertexCount, item.clone())
            self.table_adjacency.blockSignals(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())