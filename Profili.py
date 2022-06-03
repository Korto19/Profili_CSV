# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Profili
                                 A QGIS plugin
 Profili
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-04-29
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Giulio Fattori
        email                : giulio.fattori@tin.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import *
from qgis.utils import iface

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Profili_dialog import ProfiliDialog

import math           
import csv
import os.path
import inspect
cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

import webbrowser

class Profili:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Profili_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Topographic Profile')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        # noinspection PyMethodMayBeStatic
    
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Profili', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Profili/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Topographic Profile'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Topographic Profile'),
                action)
            self.iface.removeToolBarIcon(action)

    def get_sb_layer(self):
        self.dlg.CB_Progressive.clear()
        self.dlg.CB_Progressive.addItems(self.layers.keys())
        
    def getClickedCoor(self, pnt):
        self.dlg.showMinimized()
        global pointTool
        pointTool = QgsMapToolEmitPoint(self.canvas)
        pointTool.canvasClicked.connect(lambda x: self.display_point(x,pnt))
        self.canvas.setMapTool(pointTool)
         
    def unset(self):
        self.canvas.unsetMapTool(pointTool)

    def display_point(self, pointTool, pnt):
        try:
            self.coorx = round(pointTool.x(),3)
            self.coory = round(pointTool.y(),3)
            if pnt == "start":
                self.dlg.sb_start_x.setValue(self.coorx)
                self.dlg.sb_start_y.setValue(self.coory)
        except AttributeError:
            pass
        self.unset()
        self.dlg.showNormal()

    def mQgsFileWidget_file_selected(self):
        #print('1',self.dlg.mQgsFileWidget.filePath())
        if self.dlg.mQgsFileWidget.filePath():
            #print('2','if')
            with open(self.dlg.mQgsFileWidget.filePath()) as csv_file:
            # creating an object of csv reader
            # with the delimiter as ,
                csv_reader = csv.reader(csv_file, delimiter = ',')
            # list to store the names of columns
                list_of_column_names = []
            # loop to iterate through the rows of csv
                for row in csv_reader:
                    # adding the first row
                    list_of_column_names.append(row)
                    #print(row)
                    # breaking the loop after the
                    # first iteration itself
                    break
            list_of_column_names[0].sort()
            #print('list ', list_of_column_names[0])
            #get fild name list sorted
            #lista_nomi = sorted(list_of_column_names[0][0].split(','))
            #print('3', lista_nomi)
            
            #if exist set combo box to "Progressive_Distances"
            self.dlg.CB_Progressive.clear()
            self.dlg.CB_Progressive.addItems(list_of_column_names[0])
            index = self.dlg.CB_Progressive.findText("Progressive_Distances", QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.dlg.CB_Progressive.setCurrentIndex(index)
            else:
                self.dlg.CB_Progressive.setCurrentIndex(-1)
                
            #if exist set combo box to "Ground_Levels"
            self.dlg.CB_Terreno.clear()
            self.dlg.CB_Terreno.addItems(list_of_column_names[0])
            index = self.dlg.CB_Terreno.findText("Ground_Levels", QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.dlg.CB_Terreno.setCurrentIndex(index)
            else:
                self.dlg.CB_Terreno.setCurrentIndex(-1)
                
            #if exist set combo box to "Pipeline_Levels"
            self.dlg.CB_Tubazione.clear()
            self.dlg.CB_Tubazione.addItems(list_of_column_names[0])
            index = self.dlg.CB_Tubazione.findText("Pipeline_Levels", QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.dlg.CB_Tubazione.setCurrentIndex(index)
            else:
                self.dlg.CB_Tubazione.setCurrentIndex(-1)
                
            #if exist set combo box to "Excavation_Levels"
            self.dlg.CB_FondoScavo.clear()
            self.dlg.CB_FondoScavo.addItems(list_of_column_names[0])
            index = self.dlg.CB_FondoScavo.findText("Excavation_Levels", QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.dlg.CB_FondoScavo.setCurrentIndex(index)
            else:
                self.dlg.CB_FondoScavo.setCurrentIndex(-1)
              
            #if exist set combo box to "Peg No"
            self.dlg.CB_Picchetto.clear()
            self.dlg.CB_Picchetto.addItems(list_of_column_names[0])
            index = self.dlg.CB_Picchetto.findText("Peg No", QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.dlg.CB_Picchetto.setCurrentIndex(index)
            else:
                self.dlg.CB_Picchetto.setCurrentIndex(-1)

        else:
            #print('else')
            #altrimenti azzera tutte
            #con ricerca per tipo e nome
            #self.findChild(QtWidgets.QComboBox,'CB_Progressive').clear()
            #indirizzamento diretto
            self.dlg.CB_Picchetto.clear()
            self.dlg.CB_Progressive.clear()
            self.dlg.CB_Terreno.clear()
            self.dlg.CB_Tubazione.clear()
            self.dlg.CB_FondoScavo.clear()
            #self.dlg.listWidget.clear()
          
    def min_max_val(self):
        res=[]
        with open(self.dlg.mQgsFileWidget.filePath()) as csv_file:
            data = csv.DictReader(csv_file)          
            for i, row in enumerate(data):
                if self.dlg.CB_Terreno.currentIndex() != -1:
                    if row.get(self.dlg.CB_Terreno.currentText()) != '':
                        res.append(row.get(self.dlg.CB_Terreno.currentText()))
                    else:
                        res.append('0')
                if self.dlg.CB_Tubazione.currentIndex() != -1:
                    if row.get(self.dlg.CB_Tubazione.currentText()) != '':
                        res.append(row.get(self.dlg.CB_Tubazione.currentText()))
                    else:
                        res.append('0')
                if self.dlg.CB_FondoScavo.currentIndex() != -1:
                    if row.get(self.dlg.CB_FondoScavo.currentText()) != '':
                        res.append(row.get(self.dlg.CB_FondoScavo.currentText()))
                    else:
                        res.append('0')
                        
        #print(res)
        #print('m: ', min(res), ' M: ', max(res))
        return -float(min(res)), float(max(res))
        
    def help_show(self):
       
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        help_path = os.path.join(self.plugin_dir,'help','help.html')
        print(help_path)
        webbrowser.open(help_path)
        
    def Bottom_clear_val(self):
        self.dlg.CB_FondoScavo.setCurrentIndex(-1)
        
    def Pipeline_clear_val(self):
        self.dlg.CB_Tubazione.setCurrentIndex(-1)
    
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = ProfiliDialog()
            
            #autoload example file
            exmp_path = os.path.join(self.plugin_dir,'dati','Profilo.csv')
            self.dlg.mQgsFileWidget.setFilePath(exmp_path)
            self.mQgsFileWidget_file_selected()
            
            self.dlg.help.clicked.connect(self.help_show)
            
            #self.layers = {layer.name():layer for layer in QgsProject.instance().mapLayers().values() if layer.type()== 0}
            #self.get_sb_layer()
            
            self.dlg.mQgsFileWidget.fileChanged.connect(self.mQgsFileWidget_file_selected)
            self.dlg.coord_pushButton.clicked.connect(lambda x:self.getClickedCoor("start"))
            
            self.dlg.Bottom_clear.clicked.connect(self.Bottom_clear_val)
            self.dlg.Pipeline_clear.clicked.connect(self.Pipeline_clear_val)
            
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        scala_x = float(self.dlg.X_Scale.currentText())                                                      
        scala_y = float(self.dlg.Y_Scale.currentText())
        q_ref, M = self.min_max_val()
        q_ref = math.floor(q_ref + self.dlg.H_ref_val.value())
        m_arr = 38.0
        H_label = [15.0, 5.0, 15.0, 0.0, 0.0, 0.0, 0.0]
        n_lines = -30
        
        #print(H_label)
        # See if OK was pressed
        if result:
            #get insertion point 0,0 default
            origin_x = self.dlg.sb_start_x.value()
            origin_y = self.dlg.sb_start_y.value()
            
            #add ground vertex layer
            ground_vertex = QgsVectorLayer("point?crs=epsg:32632", "Ground_Vertex", "memory")
            pr_ground_vertex = ground_vertex.dataProvider()
            pr_ground_vertex.addAttributes([QgsField("id_labl", QVariant.Int),
                                            QgsField("E_Label", QVariant.String),
                                            QgsField("Cat_str", QVariant.String)])
            ground_vertex.updateFields()
                   
            
            #add ground line layer
            ground_line = QgsVectorLayer("linestring?crs=epsg:32632", "Ground_Line", "memory")
            pr_ground_line = ground_line.dataProvider()
            pr_ground_line.addAttributes([QgsField("id_labl", QVariant.Int),
                                          QgsField("E_Label", QVariant.String),
                                          QgsField("Cat_str", QVariant.String)])
            ground_line.updateFields()
            
            if self.dlg.CB_Tubazione.currentIndex() != -1:
                #add pipe line layer
                pipe_line = QgsVectorLayer("linestring?crs=epsg:32632", "Pipe_Line", "memory")
                pr_pipe_line = pipe_line.dataProvider()
                pr_pipe_line.addAttributes([QgsField("id_labl", QVariant.Int),
                                            QgsField("E_Label", QVariant.String),
                                            QgsField("Cat_str", QVariant.String)])
                pipe_line.updateFields()
                
                H_label[0] = H_label[0] + 10.0
                H_label[3] = H_label[0]
                n_lines = n_lines - 10
                
            
            if self.dlg.CB_FondoScavo.currentIndex() != -1:
                #add bottom excavation line layer
                Bottom_line = QgsVectorLayer("linestring?crs=epsg:32632", "Bottom_line", "memory")
                pr_Bottom_line = Bottom_line.dataProvider()
                pr_Bottom_line.addAttributes([QgsField("id_labl", QVariant.Int),
                                              QgsField("E_Label", QVariant.String),
                                              QgsField("Cat_str", QVariant.String)])
                Bottom_line.updateFields()
                
                H_label[0] = H_label[0] + 10.0
                H_label[4] = H_label[0]
                n_lines = n_lines - 10
                
        
            #add finche line layer
            grid_line = QgsVectorLayer("linestring?crs=epsg:32632", "Grid_Line", "memory")
            pr_grid_line = grid_line.dataProvider()
            pr_grid_line.addAttributes([QgsField("id_labl", QVariant.Int),
                                          QgsField("E_Label", QVariant.String),
                                          QgsField("Cat_str", QVariant.String)])
            grid_line.updateFields()
            
            H_label[0] = H_label[0] + 10.0
            H_label[5] = H_label[0]
            
            
            #add labels layer
            labels_point = QgsVectorLayer("point?crs=epsg:32632", "Labels_point", "memory")
            pr_labels_point = labels_point.dataProvider()
            pr_labels_point.addAttributes([QgsField("id_labl", QVariant.Int),
                                           QgsField("E_Label", QVariant.String),
                                           QgsField("Cat_str", QVariant.String)])
            labels_point.updateFields()
            
            H_label[0] = H_label[0] + 10.0
            H_label[6] = H_label[0]
          
          
            f = QgsFeature()
            
            with open(self.dlg.mQgsFileWidget.filePath()) as csv_file:
                data = csv.DictReader(csv_file)
                
                for i, row in enumerate(data):
                    
                    #parameters
                    delta_x  =  float(row[self.dlg.CB_Progressive.currentText()]) / scala_x#x progressiva
                    delta_yg = (float(row[self.dlg.CB_Terreno.currentText()])+ q_ref ) / scala_y#z terreno
                    #print(self.dlg.CB_Tubazione.currentIndex())
                    if self.dlg.CB_Tubazione.currentIndex() != -1:
                        delta_yp = (float(row[self.dlg.CB_Tubazione.currentText()])+ q_ref ) / scala_y #z condotta
                    if self.dlg.CB_FondoScavo.currentIndex() != -1:
                        delta_yb = (float(row[self.dlg.CB_FondoScavo.currentText()])+ q_ref ) / scala_y #z scavo
 
                    #Add Ground vertex for each point
                    f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Terreno.currentText()],""])
                    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yg)))
                    
                    pr_ground_vertex.addFeature(f)
                    #ground_vertex.updateExtents()
                    QgsProject.instance().addMapLayer(ground_vertex)
            
            
                    #Ground line
                    if i > 0:
                        #f = QgsFeature()
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Terreno.currentText()],""])
                        
                        line_end = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yg)
                        
                        f.setGeometry(QgsGeometry.fromPolyline([line_start, line_end]))
                        
                        pr_ground_line.addFeature(f)
                        #ground_line.updateExtents()
                        QgsProject.instance().addMapLayer(ground_line)
                    
                    line_start   = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yg)
                    
                    #Pipe line
                    if i > 0 and self.dlg.CB_Tubazione.currentIndex() != -1:
                        #f = QgsFeature()
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Terreno.currentText()],""])
                        
                        line_end_pipe = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yp )
                        
                        f.setGeometry(QgsGeometry.fromPolyline([line_start_pipe, line_end_pipe]))
                        
                        pr_pipe_line.addFeature(f)
                        #pipe_line.updateExtents()
                        QgsProject.instance().addMapLayer(pipe_line)
                    
                    if self.dlg.CB_Tubazione.currentIndex() != -1:
                        line_start_pipe = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yp)


                    #Bottom excavation line
                    if i > 0 and self.dlg.CB_FondoScavo.currentIndex() != -1:
                        #f = QgsFeature()
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Terreno.currentText()],""])
                        
                        line_end_botexc = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yb )
                        
                        f.setGeometry(QgsGeometry.fromPolyline([line_start_botexc, line_end_botexc]))
                        
                        pr_Bottom_line.addFeature(f)
                        #Bottom_line.updateExtents()
                        QgsProject.instance().addMapLayer(Bottom_line)
                     
                    if self.dlg.CB_FondoScavo.currentIndex() != -1:
                        line_start_botexc = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yb)
 
 
                    #Finche  vertical line (candles)
                    if i >= 0:
                        
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Terreno.currentText()],""])
                        
                        line_start_finche = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value())
                        line_end_finche   = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + delta_yg)
                        
                        f.setGeometry(QgsGeometry.fromPolyline([line_start_finche, line_end_finche]))
                        
                        pr_grid_line.addFeature(f)
                        #grid_line.updateExtents()
      
      
                        #minicandles with step
                        for k in range(0, n_lines, -10):
                            line_start_finche = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + k)
                            line_end_finche   = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + k - 1)
                        
                            f.setGeometry(QgsGeometry.fromPolyline([line_start_finche, line_end_finche]))
                        
                            pr_grid_line.addFeature(f)
                            
                            line_start_finche = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + k - 9)
                            line_end_finche   = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + k - 10)
                        
                            f.setGeometry(QgsGeometry.fromPolyline([line_start_finche, line_end_finche]))
                        
                            pr_grid_line.addFeature(f)
                        
                        line_start_finche = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + k - 10)
                        line_end_finche   = QgsPoint(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() + k - 20)
                    
                        f.setGeometry(QgsGeometry.fromPolyline([line_start_finche, line_end_finche]))
                    
                        pr_grid_line.addFeature(f)
                        
                        QgsProject.instance().addMapLayer(grid_line)
                        

                    #Add Labels
                    #Picchetto o sezione prima riga
                    if i == 0:
                        #descrizione riga picchetto
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],self.dlg.CB_Picchetto.currentText(),'Row'])
                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x - m_arr, self.dlg.sb_start_y.value() - H_label[1])))
          
                        pr_labels_point.addFeature(f)      
                        QgsProject.instance().addMapLayer(labels_point)
                        
                    f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Picchetto.currentText()],'Peg'])
                    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() - H_label[1])))
      
                    pr_labels_point.addFeature(f)      
                    QgsProject.instance().addMapLayer(labels_point)
                    
                    #Quota Terreno seconda riga
                    if i == 0:
                        #descrizione riga
                        f.setAttributes([row[self.dlg.CB_Terreno.currentText()],self.dlg.CB_Terreno.currentText(),'Row'])
                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x - m_arr, self.dlg.sb_start_y.value() - H_label[2])))
          
                        pr_labels_point.addFeature(f)      
                        QgsProject.instance().addMapLayer(labels_point)
                        
                    f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Terreno.currentText()],'Ground'])
                    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() - H_label[2])))
      
                    pr_labels_point.addFeature(f)      
                    QgsProject.instance().addMapLayer(labels_point)
                    
                    
                    #Asse Condotta terza riga se presente
                    if self.dlg.CB_Tubazione.currentIndex() != -1:
                        if i == 0:
                            #descrizione riga
                            f.setAttributes([row[self.dlg.CB_Terreno.currentText()],self.dlg.CB_Tubazione.currentText(),'Row'])
                            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x - m_arr, self.dlg.sb_start_y.value() - H_label[3])))
              
                            pr_labels_point.addFeature(f)      
                            QgsProject.instance().addMapLayer(labels_point)
                            
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Tubazione.currentText()],'Pipeline'])
                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() - H_label[3])))
          
                        pr_labels_point.addFeature(f)      
                        QgsProject.instance().addMapLayer(labels_point)
                    
                     
                    #Fondo Scavo quarta riga se presente
                    if self.dlg.CB_FondoScavo.currentIndex() != -1:
                        if i == 0:
                            #descrizione riga
                            f.setAttributes([row[self.dlg.CB_Terreno.currentText()],self.dlg.CB_FondoScavo.currentText(),'Row'])
                            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x - m_arr, self.dlg.sb_start_y.value() - H_label[4])))
              
                            pr_labels_point.addFeature(f)      
                            QgsProject.instance().addMapLayer(labels_point)
                            
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_FondoScavo.currentText()],'Bottom'])
                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() - H_label[4])))
          
                        pr_labels_point.addFeature(f)      
                        QgsProject.instance().addMapLayer(labels_point)                   
                    
                    
                    #Distanza progressiva penultima riga
                    if i == 0:
                        #descrizione riga
                        f.setAttributes([row[self.dlg.CB_Terreno.currentText()],self.dlg.CB_Progressive.currentText(),'Row'])
                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x - m_arr, self.dlg.sb_start_y.value() - H_label[5])))
          
                        pr_labels_point.addFeature(f)      
                        QgsProject.instance().addMapLayer(labels_point)
                        
                    f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Progressive.currentText()],'Progressive'])
                    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x, self.dlg.sb_start_y.value() - H_label[5])))
      
                    pr_labels_point.addFeature(f)      
                    QgsProject.instance().addMapLayer(labels_point)


                    #Distanza parziale ultima riga
                    if i == 0:
                        #descrizione riga
                        f.setAttributes([row[self.dlg.CB_Terreno.currentText()],'Partial Distances','Row'])
                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x - m_arr, self.dlg.sb_start_y.value() - H_label[6])))
          
                        pr_labels_point.addFeature(f)      
                        QgsProject.instance().addMapLayer(labels_point)

                    else:
                        p_dist = float(row[self.dlg.CB_Progressive.currentText()]) - float(p_prec)
                        f.setAttributes([row[self.dlg.CB_Progressive.currentText()],p_dist,'Partial'])
                        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() + delta_x - (p_dist/scala_x)/2, self.dlg.sb_start_y.value() - H_label[6])))
      
                        pr_labels_point.addFeature(f)      
                        QgsProject.instance().addMapLayer(labels_point)
                        
                    p_prec = row[self.dlg.CB_Progressive.currentText()]    
                    
                    
                    
            #add horizontal finche line
            for k in range (0, n_lines - 20, -10):
                #f = QgsFeature()
                f.setAttributes([row[self.dlg.CB_Progressive.currentText()],row[self.dlg.CB_Terreno.currentText()],""])
                            
                line_start_finche = QgsPoint(self.dlg.sb_start_x.value() - 40.0, self.dlg.sb_start_y.value() + k)
                line_end_finche   = QgsPoint(self.dlg.sb_start_x.value() + delta_x + 5.0, self.dlg.sb_start_y.value() + k)
                            
                f.setGeometry(QgsGeometry.fromPolyline([line_start_finche, line_end_finche]))
                            
                pr_grid_line.addFeature(f)
                #grid_line.updateExtents()
                QgsProject.instance().addMapLayer(grid_line)
            
            #open and close finche
            line_start_finche = QgsPoint(self.dlg.sb_start_x.value() - 40.0, self.dlg.sb_start_y.value() + k)
            line_end_finche   = QgsPoint(self.dlg.sb_start_x.value() - 40.0, self.dlg.sb_start_y.value())
            f.setGeometry(QgsGeometry.fromPolyline([line_start_finche, line_end_finche]))            
            pr_grid_line.addFeature(f)
            
            line_start_finche = QgsPoint(self.dlg.sb_start_x.value() + delta_x + 5.0, self.dlg.sb_start_y.value())
            line_end_finche   = QgsPoint(self.dlg.sb_start_x.value() + delta_x + 5.0, self.dlg.sb_start_y.value() + k)
            f.setGeometry(QgsGeometry.fromPolyline([line_start_finche, line_end_finche]))            
            pr_grid_line.addFeature(f)
            QgsProject.instance().addMapLayer(grid_line)
          
            #quota di riferimento
            f.setAttributes([-q_ref,-q_ref,'Qrif'])
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() -20, self.dlg.sb_start_y.value() + 2)))

            pr_labels_point.addFeature(f)      
            QgsProject.instance().addMapLayer(labels_point)          
            
            #x scale
            f.setAttributes([scala_x,scala_x,'Xscale'])
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() -30, self.dlg.sb_start_y.value() + 20)))

            pr_labels_point.addFeature(f)      
            QgsProject.instance().addMapLayer(labels_point) 
            
            #y scale
            f.setAttributes([scala_y,scala_y,'Yscale'])
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.dlg.sb_start_x.value() -30, self.dlg.sb_start_y.value() + 17)))

            pr_labels_point.addFeature(f)      
            QgsProject.instance().addMapLayer(labels_point) 
            
            #make profile group with name from file name and move loaded layer in group
            root = QgsProject.instance().layerTreeRoot()
            file_name = os.path.basename(self.dlg.mQgsFileWidget.filePath())
            profile_group = root.addGroup(file_name)
            
            myLayer = root.findLayer(labels_point.id())
            myClone = myLayer.clone()
            parent = myLayer.parent()
            profile_group.insertChildNode(0, myClone)
            parent.removeChildNode(myLayer)            

            myLayer = root.findLayer(grid_line.id())
            myClone = myLayer.clone()
            parent = myLayer.parent()
            profile_group.insertChildNode(0, myClone)
            parent.removeChildNode(myLayer)
            
            if self.dlg.CB_FondoScavo.currentIndex() != -1:
                myLayer = root.findLayer(Bottom_line.id())
                myClone = myLayer.clone()
                parent = myLayer.parent()
                profile_group.insertChildNode(0, myClone)
                parent.removeChildNode(myLayer)
            
            if self.dlg.CB_Tubazione.currentIndex() != -1:
                myLayer = root.findLayer(pipe_line.id())
                myClone = myLayer.clone()
                parent = myLayer.parent()
                profile_group.insertChildNode(0, myClone)
                parent.removeChildNode(myLayer)
            
            myLayer = root.findLayer(ground_line.id())
            myClone = myLayer.clone()
            parent = myLayer.parent()
            profile_group.insertChildNode(0, myClone)
            parent.removeChildNode(myLayer)
            
            myLayer = root.findLayer(ground_vertex.id())
            myClone = myLayer.clone()
            parent = myLayer.parent()
            profile_group.insertChildNode(0, myClone)
            parent.removeChildNode(myLayer)  

            #Set styles
            ground_vertex.loadNamedStyle(os.path.join(os.path.join(cmd_folder, 'qml/GroundVx.qml')))
            ground_line.loadNamedStyle(os.path.join(os.path.join(cmd_folder, 'qml/Ground.qml')))
            if self.dlg.CB_Tubazione.currentIndex() != -1:
                pipe_line.loadNamedStyle(os.path.join(os.path.join(cmd_folder, 'qml/Pipe.qml')))
            if self.dlg.CB_FondoScavo.currentIndex() != -1:
                Bottom_line.loadNamedStyle(os.path.join(os.path.join(cmd_folder, 'qml/Bottom.qml')))
            grid_line.loadNamedStyle(os.path.join(os.path.join(cmd_folder, 'qml/Grid.qml')))
            labels_point.loadNamedStyle(os.path.join(os.path.join(cmd_folder, 'qml/Labels.qml')))            