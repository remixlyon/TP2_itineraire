import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QRadioButton, QButtonGroup, QCheckBox, QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt

import networkx as nx
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# import your graph logic file
import TP2_carte_son as graph_logic


class GraphCanvas(FigureCanvas):
    """Matplotlib canvas for embedding graphs in PySide6"""
    def __init__(self, parent=None):
        fig = Figure(figsize=(10, 10))
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.ax.axis('off')

    def draw_graph(self, func, *args, **kwargs):
        """Use a function from graph_logic to draw on this canvas"""
        self.ax.clear()
        self.ax.axis('off')
        fig, ax = func(*args, show_plot=False, **kwargs)
        self.figure = fig
        self.ax = ax
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Viewer")
        self.setMinimumSize(1200, 800)

        # State
        self.sommets = None
        self.graphe = None
        self.chemin_image = "carte.jpg"
        self.csv_sommets_path = ""
        self.csv_aretes_path = ""
        self.contrainte = ""

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Left: Canvas
        self.canvas = GraphCanvas(self)
        main_layout.addWidget(self.canvas, stretch=3)

        # Right: Controls
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        control_widget.setLayout(control_layout)
        main_layout.addWidget(control_widget, stretch=1)

        # CSV selection
        self.btn_load_sommets = QPushButton("Select sommets CSV")
        self.btn_load_sommets.clicked.connect(self.select_csv_sommets)
        control_layout.addWidget(self.btn_load_sommets)

        self.btn_load_aretes = QPushButton("Select aretes CSV")
        self.btn_load_aretes.clicked.connect(self.select_csv_aretes)
        control_layout.addWidget(self.btn_load_aretes)

        # Cities selection
        self.combo_city1 = QComboBox()
        self.combo_city1.currentIndexChanged.connect(self.city1_changed)
        self.combo_city2 = QComboBox()
        self.combo_city2.currentIndexChanged.connect(self.city2_changed)
        control_layout.addWidget(QLabel("City 1:"))
        control_layout.addWidget(self.combo_city1)
        control_layout.addWidget(QLabel("City 2:"))
        control_layout.addWidget(self.combo_city2)

        # Criteria radio buttons
        self.radio_cout = QRadioButton("Cout")
        self.radio_duree = QRadioButton("Duree")
        self.radio_duree.setChecked(True)
        self.criteria_group = QButtonGroup()
        self.criteria_group.addButton(self.radio_cout)
        self.criteria_group.addButton(self.radio_duree)
        control_layout.addWidget(self.radio_cout)
        control_layout.addWidget(self.radio_duree)

        # Route type checkboxes
        self.cb_autoroute = QCheckBox("Autoroutes")
        self.cb_depart = QCheckBox("Départementales")
        self.cb_autoroute.setChecked(True)
        self.cb_depart.setChecked(True)
        self.cb_autoroute.stateChanged.connect(self.update_contrainte)
        self.cb_depart.stateChanged.connect(self.update_contrainte)
        control_layout.addWidget(self.cb_autoroute)
        control_layout.addWidget(self.cb_depart)

        # Search button
        self.btn_search = QPushButton("Chercher")
        self.btn_search.clicked.connect(self.search_path)
        control_layout.addWidget(self.btn_search)

        # Detail box
        self.detail_box = QTextEdit()
        self.detail_box.setReadOnly(True)
        control_layout.addWidget(QLabel("Detail:"))
        control_layout.addWidget(self.detail_box)

        # Stretch
        control_layout.addStretch()

    def select_csv_sommets(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select sommets CSV", "", "CSV Files (*.csv)")
        if path:
            self.csv_sommets_path = path
            self.try_load_graph()

    def select_csv_aretes(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select aretes CSV", "", "CSV Files (*.csv)")
        if path:
            self.csv_aretes_path = path
            self.try_load_graph()

    def try_load_graph(self):
        if self.csv_sommets_path and self.csv_aretes_path:
            matrice_sommets = graph_logic.charger_csv_en_matrice(self.csv_sommets_path)
            matrice_aretes = graph_logic.charger_csv_en_matrice(self.csv_aretes_path)
            self.sommets = graph_logic.charger_sommets(matrice_sommets)
            self.graphe = graph_logic.creer_graphe(matrice_aretes)

            # Fill combo boxes
            self.combo_city1.clear()
            self.combo_city2.clear()
            for city in sorted(self.sommets.keys()):
                self.combo_city1.addItem(city)
                self.combo_city2.addItem(city)

            # Draw initial graph
            self.canvas.draw_graph(
                graph_logic.dessiner_graphe_sur_carte,
                graphe=self.graphe,
                sommets=self.sommets,
                chemin_image_carte=self.chemin_image,
                titre=f"Graph {'est connexe' if nx.is_connected(self.graphe) else 'n\'est pas connexe'}"
            )
            self.detail_box.setText(f"Graph {'est connexe' if nx.is_connected(self.graphe) else 'n\'est pas connexe'}")

    def city1_changed(self, index):
        # Update city2 combo so it cannot be same as city1
        city1 = self.combo_city1.currentText()
        city2_items = [c for c in sorted(self.sommets.keys()) if c != city1]
        self.combo_city2.clear()
        self.combo_city2.addItems(city2_items)

    def city2_changed(self, index):
        pass  # nothing needed yet

    def update_contrainte(self):
        # Ensure at least one checkbox is selected
        if not (self.cb_autoroute.isChecked() or self.cb_depart.isChecked()):
            # revert the change: force at least one
            sender = self.sender()
            sender.setChecked(True)

    def search_path(self):
        if not self.graphe:
            return
        city1 = self.combo_city1.currentText()
        city2 = self.combo_city2.currentText()
        critere = 'cout' if self.radio_cout.isChecked() else 'duree'

        # Determine contrainte based on checkbox
        if self.cb_autoroute.isChecked() and not self.cb_depart.isChecked():
            contrainte_type = 'd'  # exclude départementale
        elif self.cb_depart.isChecked() and not self.cb_autoroute.isChecked():
            contrainte_type = 'a'  # exclude autoroute
        else:
            contrainte_type = None

        G_filtered = self.graphe
        contrainte_str = ""
        if contrainte_type:
            G_filtered = graph_logic.filtre_graphe(self.graphe, contrainte_type)
            contrainte_str = f"without {'autoroutes' if contrainte_type=='a' else 'départementales'}"

        chemin = graph_logic.meilleur_chemin(G_filtered, city1, city2, critere)

        # Update detail box
        self.detail_box.clear()

        if len(chemin) < 2 or not self.graphe.has_edge(chemin[0], chemin[1]):
            self.detail_box.setText(f"Aucun chemin n'existe entre {city1} et {city2} sous la contrainte.")
            # Optional: clear previous drawing or show only the base graph
            self.canvas.draw_graph(
                graph_logic.dessiner_graphe_sur_carte_avec_chemin,
                graphe=self.graphe,
                sommets=self.sommets,
                chemin_image_carte=self.chemin_image,
                titre=f"Graph {city1} -> {city2} : pas de route"
            )
            return

        total_cout, total_duree = 0, 0
        for i in range(len(chemin) - 1):
            data = G_filtered.get_edge_data(chemin[i], chemin[i + 1])
            total_cout += data['cout']
            total_duree += data['duree']
        self.detail_box.append(f"Path: {' -> '.join(chemin)}")
        self.detail_box.append(f"Total Cout: {total_cout}€")
        self.detail_box.append(f"Total Duree: {total_duree}m")
        if contrainte_str:
            self.detail_box.append(f"Constraint: {contrainte_str}")

        # Draw path
        self.canvas.draw_graph(
            graph_logic.dessiner_graphe_sur_carte_avec_chemin,
            chemin=chemin,
            graphe=self.graphe,
            sommets=self.sommets,
            chemin_image_carte=self.chemin_image,
            critere=critere,
            contrainte=contrainte_str
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
