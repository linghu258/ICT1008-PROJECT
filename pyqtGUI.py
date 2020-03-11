import io
import sys

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow
from qtconsole.qt import QtCore

from Dijkstra import *

import osmnx as ox
import networkx as nx


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set PyQt window size
        self.pathLabel = QtWidgets.QLabel()
        self.destinationLabel = QtWidgets.QLabel()
        self.sourceLabel = QtWidgets.QLabel()
        self.testLabel = QtWidgets.QLabel()
        self.destinationDDL = QtWidgets.QComboBox()
        self.sourceDDL = QtWidgets.QComboBox()
        self.busPathDDL = QtWidgets.QComboBox()
        self.title = "Group P2-6 ICT 1008 PROJECT"
        self.left = 200
        self.top = 100
        self.width = 1800
        self.height = 950

        self.initWindow()

    def initWindow(self):
        # set window title
        self.setWindowTitle(self.title)
        # set window geometry
        # self.setGeometry(self.left, self.top, self.width, self.height)
        # Disable PyQt 5 application from resizing
        self.setFixedSize(self.width, self.height)

        self.guiSettings()

        self.show()

    def guiSettings(self):
        # Button Label
        self.pathLabel.setText("Select Paths:")
        self.pathLabel.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Bold))
        self.pathLabel.setFixedSize(200, 30)

        walkingPathButton = QtWidgets.QPushButton("Walking Path")
        walkingPathButton.setFont(QtGui.QFont("Arial", 13, QtGui.QFont.Bold))
        walkingPathButton.setFixedSize(150, 80)
        walkingPathButton.setIcon(QtGui.QIcon("walk.png"))
        walkingPathButton.setIconSize(QtCore.QSize(30, 30))
        walkingPathButton.clicked.connect(self.generateWalkingPath)

        drivingPathButton = QtWidgets.QPushButton("Driving path")
        drivingPathButton.setFont(QtGui.QFont("Arial", 13, QtGui.QFont.Bold))
        drivingPathButton.setFixedSize(150, 80)
        drivingPathButton.setIcon(QtGui.QIcon("car.ico"))
        drivingPathButton.setIconSize(QtCore.QSize(30, 30))
        drivingPathButton.clicked.connect(self.generateDrivingPath)

        fastestPathButton = QtWidgets.QPushButton("Fastest path")
        fastestPathButton.setFont(QtGui.QFont("Arial", 13, QtGui.QFont.Bold))
        fastestPathButton.setIcon(QtGui.QIcon("bus.png"))
        fastestPathButton.setFixedSize(150, 80)
        fastestPathButton.setIconSize(QtCore.QSize(30, 30))

        showBusPathButton = QtWidgets.QPushButton("Show Bus Path")
        showBusPathButton.setFont(QtGui.QFont("Arial", 13, QtGui.QFont.Bold))
        showBusPathButton.setFixedSize(150, 70)

#######################################################################################################################

        with open('exportBuilding.geojson') as access_json:
            read_content = json.load(access_json)
            feature_access = read_content['features']

        # Source Label
        self.sourceLabel.setText("SELECT SOURCE")
        self.sourceLabel.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Bold))
        self.sourceLabel.setFixedSize(200, 30)

        # Destination Label
        self.destinationLabel.setText("SELECT DESTINATION")
        self.destinationLabel.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Bold))
        self.destinationLabel.setFixedSize(200, 30)

        # Retrieve names from json file (Drop Down List)
        for feature_data in feature_access:
            buildingName = feature_data['properties']
            if 'name' in buildingName:
                retrieveHDB = buildingName['name']
                self.sourceDDL.addItem(retrieveHDB)
                self.destinationDDL.addItem(retrieveHDB)

        # Set font size
        self.sourceDDL.setFixedSize(180, 70)
        self.sourceDDL.setFont(QtGui.QFont("Arial", 13))

        self.destinationDDL.setFixedSize(180, 70)
        self.destinationDDL.setFont(QtGui.QFont("Arial", 13))

        self.busPathDDL.setFixedSize(180, 70)
        self.busPathDDL.setFont(QtGui.QFont("Arial", 13))

#######################################################################################################################

        self.view = QtWebEngineWidgets.QWebEngineView()
        # set margin for the map (left, top, right, down)
        self.view.setContentsMargins(5, 10, 10, 5)

        # Creating Folium Map
        self.m = folium.Map(location=[1.400150, 103.910172], titles="Punggol", zoom_start=17)
        nodeData = os.path.join('exportBuilding.geojson')

        geo_json = folium.GeoJson(nodeData, popup=folium.GeoJsonPopup(fields=['name']))
        geo_json.add_to(self.m)
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())

        # PyQt Horizontal Box layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QHBoxLayout(central_widget)

        # Create vertical layout container to contains all buttons, label, combobox, etc.
        controller_container = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(controller_container)
        vlay.addWidget(self.sourceLabel)
        vlay.addWidget(self.sourceDDL)
        vlay.addWidget(self.destinationLabel)
        vlay.addWidget(self.destinationDDL)
        vlay.addWidget(self.pathLabel)
        vlay.addWidget(walkingPathButton)
        vlay.addWidget(drivingPathButton)
        vlay.addWidget(fastestPathButton)
        vlay.addStretch()
        vlay.addWidget(self.busPathDDL)
        vlay.addWidget(showBusPathButton)
        vlay.addStretch()

        # Create vertical layout container to contain map and table
        map_container = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(map_container)
        # vlay.addWidget(checkbox_container)
        vlay.addWidget(self.view, stretch=1)

        lay.addWidget(controller_container)
        lay.addWidget(map_container)

#######################################################################################################################

    def generateWalkingPath(self):
        self.m = folium.Map(location=[1.400150, 103.910172], zoom_start=17)
        nodeData = os.path.join('exportBuilding.geojson')
        geo_json = folium.GeoJson(nodeData, popup=folium.GeoJsonPopup(fields=['name']))
        geo_json.add_to(self.m)
        src = self.sourceDDL.currentText()
        dest = self.destinationDDL.currentText()

        nodes = {}
        with open('exportBuilding.geojson') as access_json:
            read_content = json.load(access_json)
            feature_access = read_content['features']

            for feature_data in feature_access:
                buildingName = feature_data['properties']
                if 'name' in buildingName:
                    retrieveHDB = buildingName['name']
                    nodes[retrieveHDB] = find_midpoint(feature_data['geometry']['coordinates'])

        pathfinder = Dijkstra(nodes)
        pathfinder.create_edges()
        graph = pathfinder.build_graph()
        path = pathfinder.find_shortest_path(graph, src, dest)

        folium.PolyLine(path, opacity=1, color='red').add_to(self.m)
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())

    def generateDrivingPath(self):
        self.m = folium.Map(location=[1.400150, 103.910172], zoom_start=17)
        nodeData = os.path.join('exportBuilding.geojson')
        geo_json = folium.GeoJson(nodeData, popup=folium.GeoJsonPopup(fields=['name']))
        geo_json.add_to(self.m)
        src = self.sourceDDL.currentText()
        dest = self.destinationDDL.currentText()

        with open('exportBuilding.geojson') as access_json:
            read_content = json.load(access_json)
            feature_access = read_content['features']

            for feature_data in feature_access:
                buildingName = feature_data['properties']
                if buildingName['name'] == src:
                    coord = feature_data['geometry']['coordinates']
                    src_coord = coord[0][0]
                if buildingName['name'] == dest:
                    coord = feature_data['geometry']['coordinates']
                    dest_coord = coord[0][0]

        ox.config(log_console=True, use_cache=True)
        G_walk = ox.graph_from_place(src, network_type='drive')
        src_node = ox.get_nearest_node(G_walk, (src_coord[1], src_coord[0]))
        dest_node = ox.get_nearest_node(G_walk, (dest_coord[1], dest_coord[0]))

        route = nx.shortest_path(G_walk, src_node, dest_node, weight='length')

        ox.plot_route_folium(G_walk, route).add_to(self.m)
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())

#######################################################################################################################

if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec())
