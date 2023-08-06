import sys
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import io
import igraph as ig

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Graph Visualizer')
        self.setWindowState(Qt.WindowMaximized)

        self.graph = ig.Graph()

        # Create a vertical layout and a widget to contain the image and the button
        layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Generate the graph and show it
        self.label = QLabel(self)
        self.table_adjacency = QTableWidget(self)
        self.table_adjacency.cellChanged.connect(self.on_cell_changed)


        layout_result = QVBoxLayout()
        layout_result.setAlignment(Qt.AlignTop)

        layout_result.addWidget(self.label)
        layout_result.addWidget(self.table_adjacency)

        widget_result = QWidget()
        widget_result.setLayout(layout_result)
        layout.addWidget(widget_result)

        

        # Fields
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

        controls_layout.addWidget(self.label_source)
        controls_layout.addWidget(self.line_edit_source)
        controls_layout.addWidget(self.label_target)
        controls_layout.addWidget(self.line_edit_target)
        controls_layout.addWidget(self.label_weight)
        controls_layout.addWidget(self.line_edit_weight)


        controls_layout.addWidget(self.add_edge_button)
        controls_layout.addWidget(self.add_vertex_button)
        controls_layout.addWidget(self.reset_button)
        controls_layout.addWidget(self.refresh_button)

        controls_layout.setAlignment(Qt.AlignTop)

        layout.addWidget(controls)

        self.initialize_table_adjacency()
    
    def make_table_item(self, text):
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignCenter)
        return item
    
    def add_vertex(self):
        columnCount = self.table_adjacency.columnCount()
        self.graph.add_vertex()
        self.refresh_image()
        self.table_adjacency.insertColumn(columnCount - 1)
        self.table_adjacency.insertRow(columnCount - 1)
        self.table_adjacency.setHorizontalHeaderItem(columnCount - 1, QTableWidgetItem(str(columnCount - 1)))
        self.table_adjacency.setVerticalHeaderItem(columnCount - 1, QTableWidgetItem(str(columnCount - 1)))

        for i in range(columnCount):
            self.table_adjacency.setItem(columnCount - 1, i, self.make_table_item("0"))
            self.table_adjacency.setItem(i, columnCount - 1, self.make_table_item("0"))
        self.refresh_degrees()

    def on_edge_added(self):
        source = self.line_edit_source.text()
        target = self.line_edit_target.text()
        weight = self.line_edit_weight.text()

        if source == "" or target == "" or weight == "":
            return

        self.add_edge(int(source), int(target), int(weight))
        self.refresh()
    
    def add_edge(self, source, target, weight):
        weight = weight if weight > 0 else 0

        try:
            self.graph.delete_edges(self.graph.get_eid(source, target))
        except:
            pass

        if (weight > 0):
            self.graph.add_edge(source, int(target), weight=weight)


        self.table_adjacency.blockSignals(True)
        self.table_adjacency.setItem(source, target, self.make_table_item(str(weight)))
        self.table_adjacency.setItem(target, source, self.make_table_item(str(weight)))
        self.table_adjacency.blockSignals(False)

    def on_cell_changed(self, row, column):
        if (row < self.graph.vcount() and column < self.graph.vcount()):
            weight = int(self.table_adjacency.item(row, column).text())
            self.add_edge(row, column, weight)
            self.refresh()

    def get_graph(self):
        facecolor = "#ececec"

        _, ax = plt.subplots()

        ax.set_facecolor(facecolor)

        ig.plot(
            self.graph,
            target=ax,
            layout="circle",
            vertex_label=range(self.graph.vcount()),
            vertex_color="lightblue",
            edge_label=self.graph.es["weight"] if self.graph.ecount() > 0 else 0, 
            edge_background="#ececec",
        )

        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor=facecolor)
        buf.seek(0)
        plt.close()

        return buf
    
    def reset_graph(self):
        self.graph = ig.Graph()
        self.initialize_table_adjacency()
        self.refresh()
        self.refresh_image()

    def refresh(self):
        self.refresh_image()
        self.refresh_degrees()

    def refresh_image(self):
        buf = self.get_graph()
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        buf.close()
        self.label.setPixmap(pixmap)
        pixmap.scaled(self.label.size(), Qt.KeepAspectRatio)

    def initialize_table_adjacency(self):
        self.table_adjacency.setRowCount(1)
        self.table_adjacency.setColumnCount(1)
        self.table_adjacency.setHorizontalHeaderLabels(['Degrees'] )
        self.table_adjacency.setVerticalHeaderLabels(['Degrees'] )
        disabled_item = QTableWidgetItem("0")
        disabled_item.setFlags(Qt.ItemFlag.NoItemFlags)
        self.table_adjacency.setItem(0, 0, disabled_item)
        self.refresh_degrees()
                
    def refresh_degrees(self):

        for i in range(self.table_adjacency.rowCount()):
            self.table_adjacency.setRowHeight(self.graph.vcount(), 30)
            self.table_adjacency.setColumnWidth(self.graph.vcount(), 90)
            item = self.make_table_item(str(self.graph.degree(i) if self.graph.vcount() > 0 else 0))
            item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table_adjacency.setItem(self.graph.vcount(), i, item.clone())
            self.table_adjacency.setItem(i, self.graph.vcount(), item.clone())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())