# This Python file uses the following encoding: utf-8
import os
import time
from pathlib import Path
import sys
import datetime
import random
from fpdf import FPDF
import textwrap

import comtrade
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal,QThread

from PyQt5 import uic
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.table as tbl
import pyqtgraph as pg
import pickle
from comtrade import Comtrade
from scipy import signal
import PPF as ppf
from segmentation import *
# from matplotlib.gridspec import GridSpec


# import plotly.graph_objects as go
# import plotly.subplots as subplots
# import plotly.io as pio
# from align import *
# from functions_for_reporting import *


 
   
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        uic.loadUi('Trial_UI_V2_1.ui', self)

        # Variables -----------------------------------------------------
        self.file_path = None  # File path of file user is going to load

        self.all_files1 = {}  # TODO: rename to better variable

        self.file_names = []
        self.plotted_plot = []
        self.plot_dict = {}
        self.color_index = 0
        self.color_list = [(222, 60, 0), (222, 60, 163), (200, 60, 222), (125, 114, 223), (71, 165, 247),
                           (20, 190, 209), (24, 255, 109), (168, 230, 76), (247, 255, 0), (255, 162, 0)] * 2

        self.number_of_files = 0
        self.com = Comtrade()  # Initializing at start so that it can be reused for all files.

        self.hidden = False
        self.b = None
        self.label_option.setVisible(False)

        #Instantneous tab
        self.PB_plot.clicked.connect(self.plot_instantaneous)
        self.count1 = 0
        self.scroll1 = QtWidgets.QScrollArea()
        self.verticalLayout_2.addWidget(self.scroll1)
        self.layout2 = QtWidgets.QVBoxLayout()

        # Tooltips:
        self.load_tooltips()
  
        # Signals -----------------------------------------------------
        # Tab-1 --> User input tab
        self.voltage_set_items = set([])
        self.current_set_items = set([])


        self.browse_file_location.clicked.connect(self.get_file)
        self.PB_load_file.clicked.connect(self.load_file)
        self.PB_move_to_voltage.clicked.connect(self.move_to_voltage)
        self.PB_move_to_current.clicked.connect(self.move_to_current)
        self.PB_remove_entry.clicked.connect(self.removeSel)
        
        # self.PB_compute_values.clicked.connect(self.startProgressBar)
        self.PB_compute_values.clicked.connect(self.compute_values)
        
        # self.PB_show.clicked.connect(self.manualSegmentation)
        self.PB_segment.clicked.connect(self.plot_segments)
        self.PB_add.clicked.connect(self.add_segments)
        self.PB_delete.clicked.connect(self.delete_segments)
        

        self.LW_voltage_set.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.LW_current_set.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # Here lambda function is used as I wanted to send argument to the functions (arguments being, the clicked/checked widget themselves)
        # Plotting signals:
        self.CB_voltage_rms.stateChanged.connect(self.plot_signal)
        self.CB_current_rms.stateChanged.connect(self.plot_signal)
        self.CB_avg_frequency.stateChanged.connect(self.plot_signal)
        self.CB_voltage_dft.stateChanged.connect(self.plot_signal)
        self.CB_current_dft.stateChanged.connect(self.plot_signal)
       
        self.CB_impedance.stateChanged.connect(self.plot_signal)
        self.CB_complex_impedance.stateChanged.connect(self.plot_signal)

        self.CB_real_power.stateChanged.connect(self.plot_signal)
        self.CB_reactive_power.stateChanged.connect(self.plot_signal)

        self.CB_voltage_positive.stateChanged.connect(self.plot_signal)
        self.CB_voltage_negative.stateChanged.connect(self.plot_signal)
        self.CB_voltage_zero.stateChanged.connect(self.plot_signal)

        self.CB_current_positive.stateChanged.connect(self.plot_signal)
        self.CB_current_negative.stateChanged.connect(self.plot_signal)
        self.CB_current_zero.stateChanged.connect(self.plot_signal)

        self.PB_move_left.clicked.connect(self.move_left)
        self.PB_move_right.clicked.connect(self.move_right)
        self.PB_move_up.clicked.connect(self.move_up)
        self.PB_move_down.clicked.connect(self.move_down)
        self.PB_scale.clicked.connect(self.scale)
        self.PB_clear.clicked.connect(self.clear_plots)

        self.CB_voltage_rms_2.stateChanged.connect(self.plot_rms_voltage_seg)
        self.CB_current_rms_2.stateChanged.connect(self.plot_rms_current_seg)
        self.CB_frequency_seg.stateChanged.connect(self.plot_avg_frequency_seg)
        
        # self.PB_shift_segment.clicked.connect(self.shift_segment)
        self.PB_move_left_seg.clicked.connect(self.shift_segment_left)
        self.PB_move_right_seg.clicked.connect(self.shift_segment_right)


        self.list_of_files.activated.connect(self.load_signals)
        # self.list_of_files_qty.activated.connect(self.plot_instantaneous)

        self.PB_hide_gb1.clicked.connect(self.hide_gb1)

        self.PB_save_state.clicked.connect(self.save_state)
        self.PB_AutoSegmentation.clicked.connect(self.autoSegmentation)
 
        # self.PB_report.clicked.connect(self.get_segmented_plots)
        self.PB_report.clicked.connect(self.generate_report)
        # self.PB_hide_gb2.clicked.connect(self.hide_gb2)
        # Default settings
        # self.LE_power_selection.setEnabled(False)

        self.plot_widget1.showGrid(x=True, y=True, alpha=1)
        self.plot_widget2.showGrid(x=True, y=True, alpha=1)
        self.plot_widget3.showGrid(x=True, y=True, alpha=1)
        self.plot_widget4.showGrid(x=True, y=True, alpha=1)
        self.plot_widget5.showGrid(x=True, y=True, alpha=1)
        self.plot_widget6.showGrid(x=True, y=True, alpha=1)
        self.plot_widget_7.showGrid(x=True,y=True,alpha=1)
        self.plot_widget8.showGrid(x=True, y=True, alpha=1)
        self.plot_widget9.showGrid(x=True, y=True, alpha=1)
        self.segment_plot.showGrid(x=True,y=True,alpha=1)
        self.plot_widget10.showGrid(x=True, y=True, alpha=1)
        # self.plot_widget11.showGrid(x=True, y=True, alpha=1)
        # self.plot_widget12.showGrid(x=True, y=True, alpha=1)
        self.plot_widget13.showGrid(x=True, y=True, alpha=1)
        # self.correlation_plot.showGrid(x=True, y=True, alpha=1)
        self.groupBox.setEnabled(False)
        # self.segment_shift = {}
        # self.segment_shift={'x':0} 
        self.q, self.z1, self.threshold = None, None, None
        self.super_q = None
        self.max_val = [0, 0]
        self.min_val = 0
        self.segments = None
        
        
        self.signal_dataItems = {}
        self.difference_dataItems = {}
           
      
        # self.PB_plot.clicked.connect(self.plot)

            
    #################################################################################################
    #  Tab-1 -> User input area:
    #################################################################################################
    def get_file(self):
        dlg = QtWidgets.QFileDialog(self)
        self.file_path = dlg.getOpenFileName(self, 'Choose directory',
                                             r"C:\Users\Admin\OneDrive\Desktop\Expert_System\Literature_Review\Disturbance data\Task_02_COMTRADE_data",
                                             filter="Config files (*.cfg *.CFG)")[0]
        self.LE_file_path.setText(self.file_path)

        filename = self.LE_file_path.text().split('/')[-1][:-4]
        self.voltage_set_items = set([])
        self.current_set_items = set([])

        try:
            self.com.load(self.file_path)
            self.LW_attribute_list.clear()
            self.LW_attribute_list.addItems(self.com.analog_channel_ids)
            self.LW_voltage_set.clear()
            self.LW_current_set.clear()
        except comtrade.ComtradeError as err:
            QtWidgets.QMessageBox.information(self,
                                              "Fail",
                                              "File browse failed, please check the filepath")

    def load_file(self):
        dlg = QtWidgets.QFileDialog(self)
        self.file_path = dlg.getOpenFileName(self, 'Choose directory',
                                             r"C:\Users\Admin\OneDrive\Desktop\Expert_System\Literature_Review\Disturbance data\Task_02_COMTRADE_data",
                                             filter="Pickle (*.pickle)")[0]

        self.LE_file_path.setText(self.file_path)
        filename = self.LE_file_path.text().split('/')[-1]

        self.LW_voltage_set.clear()
        self.LW_current_set.clear()
        self.LW_attribute_list.clear()

        try:
            with open(f"{self.file_path}", "rb") as infile:
                self.all_files1[filename] = pickle.load(infile)

            self.file_names = list(self.all_files1.keys())
            self.list_of_files.clear()
            self.list_of_files.addItems([""] + self.file_names)
            self.list_of_files_qty.clear()
            self.list_of_files_qty.addItems([""] + self.file_names)
            # self.list_of_files_3.addItems([""] + self.file_names)
            self.groupBox.setEnabled(True)

            self.number_of_files += 1
            self.label_list_of_files.setText(self.label_list_of_files.text() + f"\n\n{self.number_of_files}. {filename[:-7]}")
            self.all_files1[filename]['color_dict'] = self.color_list[self.color_index]
            self.color_index += 1

            QtWidgets.QMessageBox.information(self,
                                              "Success",
                                              "File loaded successfully, you can add more files/proceed to plotting")
        except FileNotFoundError as err:
            QtWidgets.QMessageBox.information(self,
                                              "Fail",
                                              "The file doesn't exist, please compute the values before trying to load a file")

    def move_to_voltage(self):
        item = self.LW_attribute_list.currentItem().text()
        # item = self.LW_attribute_list.selectedIndexes()
        if item not in self.voltage_set_items:
            self.LW_voltage_set.addItem(item)
            self.voltage_set_items.add(item)
            self.LW_attribute_list.clearSelection()
        if self.LW_voltage_set.count() > 3:
            self.LE_power_selection.setEnabled(True)

    def move_to_current(self):
        item = self.LW_attribute_list.currentItem().text()
        if item not in self.current_set_items:
            self.LW_current_set.addItem(item)
            self.current_set_items.add(item)
            self.LW_attribute_list.clearSelection()
        if self.LW_current_set.count() > 3:
            self.LE_power_selection.setEnabled(True)

    def removeSel(self):
        listItems1 = self.LW_voltage_set.selectedItems()
        listItems2 = self.LW_current_set.selectedItems()
        if not listItems1 and not listItems2:
            return
        if listItems1:
            for item in listItems1:
                self.LW_voltage_set.takeItem(self.LW_voltage_set.row(item))
                self.voltage_set_items.discard(item.text())
                self.LW_voltage_set.clearSelection()
        if listItems2:
            for item in listItems2:
                self.LW_current_set.takeItem(self.LW_current_set.row(item))
                self.current_set_items.discard(item.text())
                self.LW_current_set.clearSelection()

        if self.LW_current_set.count() <= 3 and self.LW_voltage_set.count() <= 3:
            self.LE_power_selection.setEnabled(False)

    
    def compute_values(self):
        
        df_dict = {}
        number_of_voltage_sets = self.LW_voltage_set.count() // 3
        number_of_current_sets = self.LW_current_set.count() // 3

        filename = self.LE_file_path.text().split('/')[-1][:-4]
        print(filename)

        df_dict['Time'] = self.com.time

        count = 0
        for i in range(self.LW_voltage_set.count()):
            if i % 3 == 0:
                count += 1
                df_dict[f'Va{count}'] = self.com.analog[
                    self.com.analog_channel_ids.index(self.LW_voltage_set.item(i).text())]
            if i % 3 == 1:
                df_dict[f'Vb{count}'] = self.com.analog[
                    self.com.analog_channel_ids.index(self.LW_voltage_set.item(i).text())]
            if i % 3 == 2:
                df_dict[f'Vc{count}'] = self.com.analog[
                    self.com.analog_channel_ids.index(self.LW_voltage_set.item(i).text())]

        for i in range(count):
            df_dict[f'RMS_voltage {i + 1}'] = ppf.instaLL_RMSVoltage(df_dict['Time'], df_dict[f'Va{i + 1}'],
                                                                     df_dict[f'Vb{i + 1}'], df_dict[f'Vc{i + 1}'])

        count = 0
        for i in range(self.LW_current_set.count()):
            if i % 3 == 0:
                count += 1
                df_dict[f'Ia{count}'] = self.com.analog[
                    self.com.analog_channel_ids.index(self.LW_current_set.item(i).text())]
            if i % 3 == 1:
                df_dict[f'Ib{count}'] = self.com.analog[
                    self.com.analog_channel_ids.index(self.LW_current_set.item(i).text())]
            if i % 3 == 2:
                df_dict[f'Ic{count}'] = self.com.analog[
                    self.com.analog_channel_ids.index(self.LW_current_set.item(i).text())]

        for i in range(count):
            df_dict[f'RMS_current {i + 1}'] = ppf.instaLL_RMSVoltage(df_dict['Time'], df_dict[f'Ia{i + 1}'],
                                                                     df_dict[f'Ib{i + 1}'], df_dict[f'Ic{i + 1}'])
            # df_dict[f'RMS_current_filtered {i+1}'] = ppf.lowpass_filter(df_dict['Time'],df_dict[f'RMS_current {i+1}'],0.1)

        df = pd.DataFrame(df_dict)
      

        # For derived quantities calculations:
        power_input = list(eval(self.LE_power_selection.text()))
        if type(power_input[0]) == int:
            if power_input[0] > number_of_voltage_sets or power_input[1] > number_of_current_sets:
                QtWidgets.QMessageBox.information(self, "Error", "Please input proper values for power calculation")
            try:
                va, vb, vc = df[f'Va{power_input[0]}'], df[f'Vb{power_input[0]}'], df[f'Vc{power_input[0]}']
                ia, ib, ic = df[f'Ia{power_input[1]}'], df[f'Ib{power_input[1]}'], df[f'Ic{power_input[1]}']

                df["Real power"], df['Reactive power'] = ppf.instant_power(va, vb, vc, ia, ib, ic)

                
               
                va_dft = ppf.window_phasor(np.array(va), np.array(df['Time']), 1, 1)[0]
                vb_dft = ppf.window_phasor(np.array(vb), np.array(df['Time']), 1, 1)[0]
                vc_dft = ppf.window_phasor(np.array(vc), np.array(df['Time']), 1, 1)[0]
                ia_dft = ppf.window_phasor(np.array(ia), np.array(df['Time']), 1, 1)[0]
                ib_dft = ppf.window_phasor(np.array(ib), np.array(df['Time']), 1, 1)[0]
                ic_dft = ppf.window_phasor(np.array(ic), np.array(df['Time']), 1, 1)[0]

                v_dft_rms = ppf.instaLL_RMSVoltage(np.array(df['Time']),np.abs(va_dft),np.abs(vb_dft),np.abs(vc_dft))

                i_dft_rms = ppf.insta_RMSCurrent(np.array(df['Time']),np.abs(ia_dft),np.abs(ib_dft),np.abs(ic_dft))
                df['RMSDFT_V'] = v_dft_rms
                df['RMSDFT_I'] = i_dft_rms
                

                Z = ppf.impedance(va, vb, vc, ia, ib, ic)
                df['Z(Impedance)'] = Z

                Z_complex = ppf.complex_impedance(np.array(df['Time']),va,vb,vc,ia,ib,ic)
                df['Complex_Impedance'] = Z_complex

                
                df['Positive sequence V'], df['Negative sequence V'], df['Zero sequence V'] = ppf.sequencetransform(
                    df['Time'], va_dft, vb_dft, vc_dft)
                df['Positive sequence I'], df['Negative sequence I'], df['Zero sequence I'] = ppf.sequencetransform(
                    df['Time'], ia_dft, ib_dft, ic_dft)
                
                fa = ppf.freq4mdftPhasor(va_dft, np.array(df['Time']),1)[0]
                fb = ppf.freq4mdftPhasor(vb_dft, np.array(df['Time']),1)[0]
                fc = ppf.freq4mdftPhasor(vc_dft, np.array(df['Time']),1)[0]

                fa[:np.argwhere(np.isnan(fa))[-1][0] + 1] = fa[np.argwhere(np.isnan(fa))[-1][0] + 1]
                fb[:np.argwhere(np.isnan(fb))[-1][0] + 1] = fb[np.argwhere(np.isnan(fb))[-1][0] + 1]
                fc[:np.argwhere(np.isnan(fc))[-1][0] + 1] = fc[np.argwhere(np.isnan(fc))[-1][0] + 1]

                f = (fa + fb + fc)/3

                df[f'Frequency Fa'] = np.real(fa)
                df[f'Frequency Fb'] = np.real(fb)
                df[f'Frequency Fc'] = np.real(fc)
                df[f'Frequency F_avg'] = np.real(f)

            except KeyError as err:
                QtWidgets.QMessageBox.information(self,
                                                  "Error",
                                                  "Didn't obtain correct number of values, please check your input lists")
        elif type(power_input[0]) == list:
            for _ in range(len(power_input)):
                try:
                    va, vb, vc = df[f'Va{power_input[_][0]}'], df[f'Vb{power_input[_][0]}'], df[
                        f'Vc{power_input[_][0]}']
                    ia, ib, ic = df[f'Ia{power_input[_][1]}'], df[f'Ib{power_input[_][1]}'], df[
                        f'Ic{power_input[_][1]}']

                    df[f"Real power {_ + 1}"], df[f'Reactive power {_ + 1}'] = ppf.instant_power(va, vb, vc, ia, ib, ic)
                    
                    va_dft = ppf.window_phasor(np.array(va), np.array(df['Time']), 1, 1)[0]
                    vb_dft = ppf.window_phasor(np.array(vb), np.array(df['Time']), 1, 1)[0]
                    vc_dft = ppf.window_phasor(np.array(vc), np.array(df['Time']), 1, 1)[0]
                    ia_dft = ppf.window_phasor(np.array(ia), np.array(df['Time']), 1, 1)[0]
                    ib_dft = ppf.window_phasor(np.array(ib), np.array(df['Time']), 1, 1)[0]
                    ic_dft = ppf.window_phasor(np.array(ic), np.array(df['Time']), 1, 1)[0]

                    v_dft_rms = ppf.instaLL_RMSVoltage(np.array(df['Time']),np.abs(va_dft),np.abs(vb_dft),np.abs(vc_dft))

                    i_dft_rms = ppf.insta_RMSCurrent(np.array(df['Time']),np.abs(ia_dft),np.abs(ib_dft),np.abs(ic_dft))
                    df['RMSDFT_V'] = v_dft_rms
                    df['RMSDFT_I'] = i_dft_rms

                    # Z = ppf.impedance(np.array(df['Time']), va, vb, vc, ia, ib, ic)
                    Z = ppf.impedance(va,vb,vc,ia,ib,ic)
                    df['Z(Impedance)'] = Z

                    Z_complex = ppf.complex_impedance(np.array(df['Time']),va,vb,vc,ia,ib,ic)
                    df['Complex_Impedance'] = Z_complex

                    df[f'']

                    df[f'Positive sequence V {_ + 1}'], df[f'Negative sequence V {_ + 1}'], df[f'Zero sequence V {_ + 1}'] = ppf.sequencetransform(df['Time'], va, vb, vc)
                    df[f'Positive sequence V {_ + 1}'], df[f'Negative sequence V {_ + 1}'], df[
                        f'Zero sequence V {_ + 1}'] = ppf.sequencetransform(
                        df['Time'], va_dft, vb_dft, vc_dft)
                    df[f'Positive sequence I {_ + 1}'], df[f'Negative sequence I {_ + 1}'], df[
                        f'Zero sequence I {_ + 1}'] = ppf.sequencetransform(
                        df['Time'], ia_dft, ib_dft, ic_dft)
                    
                                        
                    fa = ppf.freq4mdftPhasor(va_dft, np.array(df['Time']),1)[0]
                    fb = ppf.freq4mdftPhasor(vb_dft, np.array(df['Time']),1)[0]
                    fc = ppf.freq4mdftPhasor(vc_dft, np.array(df['Time']),1)[0]

                    # fa = ppf.freq4mdftPhasor(va_dft, np.array(df['time']), 1)
                    fa[:np.argwhere(np.isnan(fa))[-1][0] + 1] = fa[np.argwhere(np.isnan(fa))[-1][0] + 1]  # Replaces the rise cycle and Nan values to first Non Nan value.

                    # fb = ppf.freq4mdftPhasor(vb_dft, np.array(df['time']), 1)
                    fb[:np.argwhere(np.isnan(fb))[-1][0] + 1] = fb[np.argwhere(np.isnan(fb))[-1][0] + 1]

                    # fc = ppf.freq4mdftPhasor(vc_dft, np.array(df['time']), 1)
                    fc[:np.argwhere(np.isnan(fc))[-1][0] + 1] = fc[np.argwhere(np.isnan(fc))[-1][0] + 1]

                    f = (fa + fb + fc) / 3

                    df[f'Frequency Fa{_ + 1}'] = np.real(fa)
                    df[f'Frequency Fb{_ + 1}'] = np.real(fb)
                    df[f'Frequency Fc{_ + 1}'] = np.real(fc)
                    df[f'Frequency F_avg{_ + 1}'] = np.real(f)


                except KeyError as err:
                    QtWidgets.QMessageBox.information(self,
                                                      "Error",
                                                      "Didn't obtain correct number of values, please check your input lists")

        shift_values = {item: 0 for item in df.columns[1:]}
        shift_values['x'] = 0
        scale_values = {item: 1 for item in df.columns[1:]}
        
        self.all_files1[filename] = dict(data=df,
                                         shift_values=shift_values,
                                         scale_values = scale_values,
                                         color_dict=self.color_list[self.color_index],
                                                                                  
                                         )

        self.color_index += 1
        self.file_names = list(self.all_files1.keys())
        self.list_of_files.clear()
        self.list_of_files.addItems([""] + self.file_names)
        # self.list_of_files_2.clear()
        # self.list_of_files_2.addItems([""] + len(q+1))
        self.list_of_files_qty.clear()
        self.list_of_files_qty.addItems([""] + self.file_names)
        self.groupBox.setEnabled(True)

         
        with open(f"{self.LE_file_path.text()[:-4]}.pickle", "wb") as outfile:
            pickle.dump(self.all_files1[filename], outfile)
            print("Pickle file generated to load later after this session")

        QtWidgets.QMessageBox.information(self,
                                          "Success",
                                          "File loaded successfully, you can add more files/proceed to plotting")

        self.number_of_files += 1
        self.label_list_of_files.setText(self.label_list_of_files.text() + f"\n\n{self.number_of_files}. {filename}")
 
             
   
    #################################################################################################
    #  Tab-2 -> Plotting area:
    #################################################################################################
    
    
    def plot_signal(self,):
        # Calling function depending on the checkbox selected
        if self.CB_voltage_rms.isChecked():

            self.plot_rms_voltage()
        else:
            self.plot_widget1.clear()

        if self.CB_current_rms.isChecked():
            self.plot_rms_current()
        else:
            self.plot_widget2.clear()

        if self.CB_avg_frequency.isChecked():
            
            self.plot_avg_frequency()
        else:
            self.plot_widget6.clear()


        if self.CB_voltage_dft.isChecked():
            self.plot_rms_voltage_dft()

        else:
            self.plot_widget8.clear()

        if self.CB_current_dft.isChecked():
            self.plot_rms_current_dft()

        else:
            self.plot_widget9.clear()

        
        if self.CB_impedance.isChecked():
            self.plot_impedance()
        else:
            self.plot_widget10.clear()

        if self.CB_complex_impedance.isChecked():
            self.plot_complex_impedance()

        else:
            self.plot_widget13.clear()

       
        if self.CB_real_power.isChecked() and self.CB_reactive_power.isChecked():
            self.plot_widget3.clear()
            self.plot_real_power()
            self.plot_reactive_power()
        elif self.CB_real_power.isChecked():
            self.plot_widget3.clear()
            self.plot_real_power()
        elif self.CB_reactive_power.isChecked():
            self.plot_widget3.clear()
            self.plot_reactive_power()
        else:
            self.plot_widget3.clear()

        if self.CB_voltage_positive.isChecked() and self.CB_voltage_negative.isChecked() and self.CB_voltage_zero.isChecked():
            self.plot_widget4.clear()
            self.plot_positive_voltage()
            self.plot_negative_voltage()
            self.plot_zero_voltage()
        elif self.CB_voltage_positive.isChecked() and self.CB_voltage_negative.isChecked():
            self.plot_widget4.clear()
            self.plot_positive_voltage()
            self.plot_negative_voltage()
        elif self.CB_voltage_zero.isChecked() and self.CB_voltage_negative.isChecked():
            self.plot_widget4.clear()
            self.plot_zero_voltage()
            self.plot_negative_voltage()
        elif self.CB_voltage_positive.isChecked() and self.CB_voltage_zero.isChecked():
            self.plot_widget4.clear()
            self.plot_positive_voltage()
            self.plot_zero_voltage()
        elif self.CB_voltage_positive.isChecked():
            self.plot_widget4.clear()
            self.plot_positive_voltage()
        elif self.CB_voltage_negative.isChecked():
            self.plot_widget4.clear()
            self.plot_negative_voltage()
        elif self.CB_voltage_zero.isChecked():
            self.plot_widget4.clear()
            self.plot_zero_voltage()
        else:
            self.plot_widget4.clear()

        if self.CB_current_positive.isChecked() and self.CB_current_negative.isChecked() and self.CB_current_zero.isChecked():
            self.plot_widget5.clear()
            self.plot_positive_current()
            self.plot_negative_current()
            self.plot_zero_current()
        elif self.CB_current_positive.isChecked() and self.CB_current_negative.isChecked():
            self.plot_widget5.clear()
            self.plot_positive_current()
            self.plot_negative_current()
        elif self.CB_current_zero.isChecked() and self.CB_current_negative.isChecked():
            self.plot_widget5.clear()
            self.plot_zero_current()
            self.plot_negative_current()
        elif self.CB_current_positive.isChecked() and self.CB_current_zero.isChecked():
            self.plot_widget5.clear()
            self.plot_positive_current()
            self.plot_zero_current()
        elif self.CB_current_positive.isChecked():
            self.plot_widget5.clear()
            self.plot_positive_current()
        elif self.CB_current_negative.isChecked():
            self.plot_widget5.clear()
            self.plot_negative_current()
        elif self.CB_current_zero.isChecked():
            self.plot_widget5.clear()
            self.plot_zero_current()

            
        else:
            self.plot_widget5.clear()

    # Plotting functions:
            
    def plot_instantaneous(self):

        file = self.list_of_files_qty.currentText()
        if file == "":
            QtWidgets.QMessageBox.information(self,"Error","Please select a file")

            return
        
        if file not in self.plotted_plot:
            self.plotted_plot.append(file)
            ##Creating a dictionary, which will store the plots and layouts corresponding to each file

            if file not in self.plot_dict.keys():
                self.plot_dict[file] = {"plots": [],
                                        "h_layout": []}
            
            num_of_sets = max(len([item for item in self.all_files1[file]['data'].keys() if item.startswith("V")]),
                              len([item for item in self.all_files1[file]['data'].keys() if item.startswith("I")])) //3
            
            for val in range(num_of_sets):
                layout = QtWidgets.QHBoxLayout()
                plot = pg.PlotWidget()
                plot.addLegend(offset=(280,8))
                plot.setMinimumSize(480,250)
                plot.setMaximumSize(550,280)

                colors = ['r','y','b'] * 3
                color_count = 0

                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("V") and item.endswith(str(val+1))]:
                    pen = pg.mkPen(color=colors[color_count], width=1.5)
                    plot.plot(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                        self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                        pen=pen, name=file + f"_{column}")
                    color_count += 1

                layout.addWidget(plot)
                self.plot_dict[file]["plots"].append(plot)

                plot = pg.PlotWidget()
                plot.addLegend(offset=(280,8))
                plot.setMinimumSize(480,250)
                plot.setMaximumSize(550,280)
                color_count = 0
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("I") and item.endswith(str(val+1))]:
                    pen = pg.mkPen(color=colors[color_count], width=1.5)
                    plot.plot(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'] ,
                        self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                        pen=pen, name=file + f"_{column}")
                    color_count += 1

                layout.addWidget(plot)
                self.plot_dict[file]['plots'] += [plot]
                self.plot_dict[file]['h_layout'] += [layout]
                self.layout2.addLayout(layout)

            scrollContent = QtWidgets.QWidget()
            scrollContent.setLayout(self.layout2)
            self.scroll1.setWidget(scrollContent)
        
        else:
            QtWidgets.QMessageBox.information(self,"Error","File already plotted")

                      

        
        # self.count1 += 1
        # file = self.list_of_files_qty.currentText()
        # if file == "":
        #     QtWidgets.QMessageBox.information(self,"Error","Please select a file")

        #     return

        # if file not in self.plotted_plot:
        #     self.plotted_plot.append(file)
        
        # self.plot1 = pg.PlotWidget()
        # self.plot1.addLegend(offset=(280,8))
        # self.plot1.setMinimumSize(480,250)
        # self.plot1.setMaximumSize(550,280)

        # colors = ['r','y','b'] * 6
        # color_count = 0

        # for column in [item for item in self.all_files1[file]['data'].keys() if
        #                item.startswith("V")]:
        #     pen = pg.mkPen(color=colors[color_count], width=1.5)
        #     self.plot1.plot(
        #         self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
        #         self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
        #         pen=pen, name=file + f"_{column}")
        #     color_count += 1

        # self.plot2 = pg.PlotWidget()
        # self.plot2.addLegend(offset=(280,8))
        # self.plot2.setMinimumSize(480,250)
        # self.plot2.setMaximumSize(550,280)
        # for column in [item for item in self.all_files1[file]['data'].keys() if
        #                item.startswith("I")]:
        #     pen = pg.mkPen(color=colors[color_count], width=1.5)
        #     self.plot2.plot(
        #         self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'] ,
        #         self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
        #         pen=pen, name=file + f"_{column}")
        #     color_count += 1

        # layout = QtWidgets.QHBoxLayout()
        # layout.addWidget(self.plot1)
        # layout.addWidget(self.plot2)

        # self.layout2.addLayout(layout)
        # self.widget = QtWidgets.QWidget()
        # self.widget.setLayout(self.layout2)
        # self.scroll1.setWidget(self.widget)

    def clear_plots(self):

        file = self.list_of_files_qty.currentText()
        if file in self.plotted_plot:
            for h_layout in self.plot_dict[file]["h_layout"]:
                self.layout2.removeItem(h_layout)
            
            for plot in self.plot_dict[file]["plots"]:
                plot.deleteLater()
            self.plotted_plot.remove(file)

            del self.plot_dict[file]

        else:
            QtWidgets.QMessageBox.information(self,"Error","No plots to clear")
    #    h_layouts = self.scroll1.findChildren(QtWidgets.QHBoxLayout)
    #    print(h_layouts)
    #    plot_layout = self.scroll1.findChildren(pg.PlotWidget)
    #    print(plot_layout)
    #    file = self.list_of_files_qty.currentText()

    #    if file in self.plotted_plot:
            

    #         h_layout = h_layouts[self.plotted_plot.index(file)]
    #         self.layout2.removeItem(h_layout)
    #         plot_layout[0 + 2*self.plotted_plot.index(file)].deleteLater()
    #         plot_layout[1 + 2*self.plotted_plot.index(file)].deleteLater()
    #         self.plotted_plot.remove(file)

           
        
    
    def plot_rms_voltage(self):
        self.plot_widget1.clear()
        self.plot_widget1.addLegend(offset=(350, 8))

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:
                self.plot_widget1.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       (self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])*self.all_files1[file]['scale_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")

    def plot_rms_voltage_seg(self):
        self.plot_widget_7.clear()
        self.plot_widget_7.addLegend(offset=(350, 8))
        self.segment_plot.clear()

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:
                self.plot_widget_7.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       (self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])*self.all_files1[file]['scale_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")
            
                
    def plot_rms_voltage_dft(self):
        self.plot_widget8.clear()
        self.plot_widget8.addLegend(offset=(350, 8))

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMSDFT_V")]:
                self.plot_widget8.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")

            
    def plot_rms_current(self):
        self.plot_widget2.clear()
        self.plot_widget2.addLegend(offset=(350, 8))
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:
                self.plot_widget2.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       (self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])*self.all_files1[file]['scale_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")


    def plot_rms_current_seg(self):
        self.plot_widget_7.clear()
        self.plot_widget_7.addLegend(offset=(350, 8))
        self.segment_plot.clear()

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:
                self.plot_widget_7.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       (self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])*self.all_files1[file]['scale_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")
                

    def plot_rms_current_dft(self):
        self.plot_widget9.clear()
        self.plot_widget9.addLegend(offset=(350, 8))

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)

            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMSDFT_I")]:
                self.plot_widget9.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")
                
    def plot_impedance(self):
        self.plot_widget10.clear()
        self.plot_widget10.addLegend(offset=(350, 8))

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)

            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Z(Impedance)")]:
                self.plot_widget10.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")
                
    def plot_complex_impedance(self):
        self.plot_widget13.clear()
        self.plot_widget13.addLegend(offset=(350, 8))

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)

            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Complex_Impedance")]:
                self.plot_widget13.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")



    def plot_real_power(self):
        # self.plot_widget3.clear()
        self.plot_widget3.addLegend(offset=(350, 8))
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Real power")]:
                self.plot_widget3.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")

    def plot_reactive_power(self):
        # self.plot_widget3.clear()
        self.plot_widget3.addLegend(offset=(350, 8))
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Reactive power")]:
                self.plot_widget3.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")
                
    

    def plot_positive_voltage(self):
        
        self.plot_widget4.addLegend(offset=(350, 8))
        
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Positive sequence V")]:
                self.plot_widget4.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")

    def plot_negative_voltage(self):
        
        self.plot_widget4.addLegend(offset=(350, 8))
        
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Negative sequence V")]:
                self.plot_widget4.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")

    def plot_zero_voltage(self):
        
        self.plot_widget4.addLegend(offset=(350, 8))
        
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Zero sequence V")]:
                self.plot_widget4.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")

    def plot_positive_current(self):
        
        self.plot_widget5.addLegend(offset=(350, 8))
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Positive sequence I")]:
                self.plot_widget5.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")

    def plot_negative_current(self):
        # self.plot_widget5.clear()
        self.plot_widget5.addLegend(offset=(350, 8))
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Negative sequence I")]:
                self.plot_widget5.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")

    def plot_zero_current(self):
        # self.plot_widget5.clear()
        self.plot_widget5.addLegend(offset=(350, 8))
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Zero sequence I")]:
                self.plot_widget5.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       np.abs(self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]),
                                       pen=pen, name=file[:-4] + f"_{column}")
                
              
    
    def plot_avg_frequency(self):
        self.plot_widget6.clear()
        self.plot_widget6.addLegend(offset=(350, 8))
        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)

            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:
                self.plot_widget6.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")
                
    def plot_avg_frequency_seg(self):
        self.plot_widget_7.clear()
        self.plot_widget_7.addLegend(offset=(350, 8))
        self.segment_plot.clear()

        for file in self.file_names:
            pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)

            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:
                self.plot_widget_7.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],
                                       pen=pen, name=file[:-4] + f"_{column}")

    def move_left(self):
        try:
            shift = (-1) * float(self.LE_shift_value.text())
            new_val = round(float(self.x_shift_value.text()) + shift, 3)
            self.x_shift_value.setText(str(new_val))
            
            self.all_files1[self.list_of_files.currentText()]['shift_values']['x'] += shift  
            self.plot_signal()
        
                       
        except KeyError as err:
            QtWidgets.QMessageBox.information(self,
                                              "Error",
                                              "Please select a file to shift.")

    def move_right(self):
        try:
            shift = float(self.LE_shift_value.text())
            new_val = round(float(self.x_shift_value.text()) + shift, 3)
            self.x_shift_value.setText(str(new_val))
           
            self.all_files1[self.list_of_files.currentText()]['shift_values']['x'] += shift
            self.plot_signal()

            
        except KeyError as err:
            QtWidgets.QMessageBox.information(self,
                                              "Error",
                                              "Please select a file to shift.")
            
    
    def move_up(self):
        try:
            shift = float(self.LE_shift_value.text())
            new_val = float(self.y_shift_value.text()) + shift

            self.y_shift_value.setText(str(new_val))
            self.all_files1[self.list_of_files.currentText()]['shift_values'][self.CB_signals_list.currentText()] += shift
            self.plot_signal()

        except KeyError as err:
            QtWidgets.QMessageBox.information(self,
                                              "Error",
                                              "Please select a file to shift.")

    def move_down(self):
        try:
            shift = -float(self.LE_shift_value.text())
            new_val = float(self.y_shift_value.text()) + shift

            self.y_shift_value.setText(str(new_val))
            self.all_files1[self.list_of_files.currentText()]['shift_values'][self.CB_signals_list.currentText()] += shift
            self.plot_signal()

        except KeyError as err:
            QtWidgets.QMessageBox.information(self,
                                              "Error",
                                              "Please select a file to shift.")
            
    def scale(self):
        try:
            
            scale = float(self.LE_scale_value.text())
            new_scale_val = float(self.y_scale_value.text()) * scale
            self.y_scale_value.setText(str(new_scale_val))
            self.all_files1[self.list_of_files.currentText()]['scale_values'][self.CB_signals_list.currentText()] += scale 
            self.plot_signal()

        except KeyError as err:
            QtWidgets.QMessageBox.information(self,
                                              "Error",
                                              "Please select a file to scale.")

    def load_signals(self):
        filename = self.list_of_files.currentText()
        self.x_shift_value.setText('0')
        self.y_scale_value.setText('1')
        
        self.CB_signals_list.clear()
        if filename != "":
            self.CB_signals_list.addItems([""] + list(self.all_files1[filename]['shift_values'].keys())[:-1])

    def hide_gb1(self):
        if self.hidden == False:
            self.groupBox.hide()
            self.PB_hide_gb1.setText('▽')
            self.label_option.setVisible(True)
            self.hidden = True
            self.b = self.groupBox_2.pos()
            self.groupBox_2.move(self.groupBox.pos())
        else:
            self.groupBox.show()
            self.PB_hide_gb1.setText('△')
            self.label_option.setVisible(False)
            self.hidden = False
            self.groupBox_2.move(self.b)

    def save_state(self):
                
        for filename in self.file_names:
            with open(fr"C:\Users\Admin\OneDrive\Desktop\{filename}.pickle", "wb") as outfile:
                pickle.dump(self.all_files1[filename], outfile)
                print("Pickle file generated to load later after this session")

        QtWidgets.QMessageBox.information(self,
                                          "Success",
                                          "File loaded successfully, you can add more files/proceed to plotting")
        
            
    def autoSegmentation(self):
                
        error = pg.mkPen(color=(249, 53, 242), width=1.5)
        threshold_pen = pg.mkPen(color=(0, 94, 255), width=1.5)
        # segment_pen = pg.mkPen(color=(255, 255, 0), width=1.5)
        self.plot_widget_7.clear()
        self.segment_plot.clear()

        self.max_val = [0, 0]
        self.min_val = 0
        self.segments = None
        self.signal_dataItems = {}
        self.difference_dataItems = {}
        self.super_q = {}
        
        
       
        if self.CB_voltage_rms_2.isChecked():
            self.plot_rms_voltage_seg()
            for file in self.file_names:
                pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:
                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                               self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                    
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]

                    self.signal_dataItems[file + f"_{column}"] = pg.PlotDataItem(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                        (self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]) * self.all_files1[file]['scale_values'][column], 
                        pen=pen)
                    
                    self.difference_dataItems[file + f"_{column}"] = pg.PlotDataItem(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                        self.z1, pen=error)
                    
                                
                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1,pen=error)
                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']),pen=threshold_pen)

                                   
            self.merge_segments()
            self.plot_segmentation()
                                       
                            
        if self.CB_current_rms_2.isChecked():
            self.plot_rms_current_seg()
            for file in self.file_names:
                pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:
                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                               self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                    
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]

                    self.signal_dataItems[file + f"_{column}"] = pg.PlotDataItem(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                        (self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]) * self.all_files1[file]['scale_values'][column], 
                        pen=pen, name=file[:-4] + f"_{column}")
                    
                    self.difference_dataItems[file + f"_{column}"] = pg.PlotDataItem(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                        self.z1, pen=error)
                    
                                
                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1,pen=error)
                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']),pen=threshold_pen)

            self.merge_segments()
            self.plot_segmentation()
                   
                              
        if self.CB_frequency_seg.isChecked():
            self.plot_avg_frequency_seg()
            for file in self.file_names:
                pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:
                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                    
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]

                    self.signal_dataItems[file + f"_{column}"] = pg.PlotDataItem(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                        (self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]) * self.all_files1[file]['scale_values'][column], 
                        pen=pen, name=file[:-4] + f"_{column}")
                    
                    self.difference_dataItems[file + f"_{column}"] = pg.PlotDataItem(
                        self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                        self.z1, pen=error)
                    
                                
                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1,pen=error)
                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']),pen=threshold_pen)

            self.merge_segments()
            self.plot_segmentation()
            if not any([button.isChecked() for button in self.tab_3.findChildren(QtWidgets.QCheckBox)]):
                self.plot_widget_7.clear()
                self.segment_plot.clear()

               
        
        fig, ax = plt.subplots(2,1, figsize=(10, 10))
        if self.CB_voltage_rms_2.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Voltage (V)")
                    ax[0].set_ylabel("Voltage (V)")
                    

        # plt.savefig('Segmentation.png')
            plt.savefig('Segmentation_Voltage.png')

        if self.CB_current_rms_2.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Current (A)")
                    ax[0].set_ylabel("Current (A)")

            plt.savefig('Segmentation_Current.png')

        if self.CB_frequency_seg.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Frequency (Hz)")
                    ax[0].set_ylabel("Frequency (Hz)")

            plt.savefig('Segmentation_Frequency.png')
                      
      
    def plot_segments(self):  ## Manual Segmentation
        self.plot_widget_7.clear()
        self.segment_plot.clear()

        self.man_threshold = float(self.LE_segment_value.text())
        # signal_pen = pg.mkPen(color=(random.randint(30, 225), random.randint(30, 225), random.randint(30, 225)), width=1.5)
        error = pg.mkPen(color=(random.randint(30, 225), random.randint(30, 225), random.randint(30, 225)), width=1.5)
        threshold_pen = pg.mkPen(color=(random.randint(30, 225), random.randint(30, 225), random.randint(30, 225)), width=1.5)
        segment_pen = pg.mkPen(color=(random.randint(30, 225), random.randint(30, 225), random.randint(30, 225)), width=1.5)

        if self.CB_voltage_rms_2.isChecked():
            # self.plot_widget_7.clear()
            self.plot_rms_voltage_seg()
            # self.segment_plot.clear()
            for file in self.file_names:
                pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:
                    self.q, self.z1 = manual_segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],self.man_threshold)

                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.super_q[file] = self.q
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]

                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],[self.man_threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']),pen=threshold_pen)
                    # print("hello")
                  
                          
            self.merge_segments()
            self.plot_segmentation()

                    
        if self.CB_current_rms_2.isChecked():
            self.plot_widget_7.clear()
            self.plot_rms_current_seg()
            self.segment_plot.clear()
            for file in self.file_names:
                pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:
                   
                    # 
                    self.q, self.z1 = manual_segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],self.man_threshold)
                    
                    # print((self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']).shape, z1.shape)

                    # self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], z1,pen=error)

                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.super_q[file] = self.q
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]

                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],[self.man_threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']),pen=threshold_pen)
            self.merge_segments()
            self.plot_segmentation()

                    
        if self.CB_frequency_seg.isChecked():
            self.plot_widget_7.clear()
            self.plot_avg_frequency_seg()
            self.segment_plot.clear()
            for file in self.file_names:
                pen = pg.mkPen(color=self.all_files1[file]['color_dict'], width=1.5)
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:
                    
                    self.q, self.z1 = manual_segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                       self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column],self.man_threshold)

                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.super_q[file] = self.q
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]

                    self.segment_plot.plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],[self.man_threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']),pen=threshold_pen)
            self.merge_segments()
            self.plot_segmentation()

        fig, ax = plt.subplots(2,1, figsize=(10, 10))

        for file in self.file_names:
            name = file[:-4]
            for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:

                self.q, self.z1 = manual_segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                               self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], self.man_threshold)
                    
                self.super_q[file] = [val for val in self.q]
                signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]

                ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                ax[0].legend()
                ax[0].title.set_text("Signal Plot")  
                ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)              
                ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],[self.man_threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))
                ax[1].legend()
                ax[1].title.set_text("Derivative Plot")

                for i in range(len(self.segments)):
                                        
                    ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                    ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])

                ax[0].grid(True)
                ax[1].grid(True)
                
                ax[1].set_xlabel("Time (s)")
                ax[1].set_ylabel("Voltage (V)")
                ax[0].set_ylabel("Voltage (V)")
                
        plt.savefig('Segmentation_Voltage.png')


                                    
    def plot_segmentation(self):
        segment_pen = pg.mkPen(color=(255,255,0), width=1.5)
        self.plot_widget_7.addLegend(offset=(350, 8))
        self.segment_plot.addLegend(offset=(350, 8))

        if self.segments is not None:
            for i in range(len(self.segments)):
                print([self.min_val, 0, self.max_val[0]])
                print([0,0, self.max_val[1]])
                self.signal_dataItems[f"segment {i}"] = pg.PlotDataItem([self.segments[i]]*3,
                                                                          [self.min_val, 0, self.max_val[0]], pen=segment_pen)
                                                                          
                self.difference_dataItems[f"segment {i}"] = pg.PlotDataItem([self.segments[i]]*3,
                                                                              [0,0, self.max_val[1]], pen=segment_pen)
                       
        print(self.signal_dataItems.keys())
        print("********************************")
        
        self.ComB_segment_selection.clear()
        self.ComB_segment_selection.addItems([""] + list(map(str, list(range(len(self.segments))))))
        print(list(map(str, list(range(len(self.segments))))))
        
        
        for key in self.signal_dataItems.keys():
            print(key)
            self.plot_widget_7.addItem(self.signal_dataItems[key])
            self.segment_plot.addItem(self.difference_dataItems[key])

                  
                             
    def merge_segments(self):
        self.segments = None
        self.ComB_segment_selection.clear()
        left = []
        right = []

        for file in self.super_q.keys():
            if len(self.super_q[file]) == 0:
                continue

            else:
                for segment_indices in (self.super_q[file]):
                    left.append(
                    self.all_files1[file]['data']['Time'][segment_indices[0]] + self.all_files1[file]['shift_values']['x'])
                
                    right.append(
                    self.all_files1[file]['data']['Time'][segment_indices[-1]] + self.all_files1[file]['shift_values']['x'])

        if (len(left) == 0) or (len(right) == 0):
            return
        
        self.segments = sorted(left + right)
        output_list = []
        prev_value = None
        for value in self.segments:
            if prev_value is None or abs(value - prev_value) >= 0.02:
                output_list.append(value)
                prev_value = value

        self.segments = output_list
        self.ComB_segment_selection.addItems([""] + list(map(str, list(range(len(self.segments))))))

                     
    def plot_shifted_segment(self, segment_num = 0):
        segment_pen = pg.mkPen(color=(255,255,0), width=1.5)

        key =[f"segment {segment_num}"]
        for val in key:
            self.plot_widget_7.removeItem(self.signal_dataItems[val])
            del self.signal_dataItems[val]

            self.segment_plot.removeItem(self.difference_dataItems[val])
            del self.difference_dataItems[val]

        print(self.max_val)
        print(segment_num)

        self.signal_dataItems[f"segment {segment_num}"] = pg.PlotDataItem([self.segments[segment_num]]*2, [0,self.max_val[0]], pen=segment_pen)
        self.difference_dataItems[f"segment {segment_num}"] = pg.PlotDataItem([self.segments[segment_num]]*2, [0,self.max_val[1]], pen=segment_pen)

        for val in key:
            self.plot_widget_7.addItem(self.signal_dataItems[val])
            print(self.signal_dataItems[val])
            self.segment_plot.addItem(self.difference_dataItems[val])

        fig, ax = plt.subplots(2,1, figsize=(10, 10))

        if self.CB_voltage_rms_2.isChecked():

            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")

                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Voltage (V)")
                    ax[0].set_ylabel("Voltage (V)")
                    

            # plt.savefig('Segmentation.png')
            plt.savefig('Segmentation_Voltage.png')

        if self.CB_current_rms_2.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Current (A)")
                    ax[0].set_ylabel("Current (A)")

            plt.savefig('Segmentation_Current.png')

        if self.CB_frequency_seg.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Frequency (Hz)")
                    ax[0].set_ylabel("Frequency (Hz)")

            plt.savefig('Segmentation_Frequency.png')


                  
    # def shift_segment(self):
    #     segment_to_shift = int(self.ComB_segment_selection.currentText())
    #     shift_value = float(self.LE_segment_shift_value.text())
    #     self.segments[segment_to_shift] += shift_value
    #     self.plot_shifted_segment(segment_to_shift)
            
    def shift_segment_left(self):
        try:
            segment_to_shift = int(self.ComB_segment_selection.currentText())
            shift_value = -float(self.LE_segment_shift_value.text())
            self.segments[segment_to_shift] += shift_value
            self.plot_shifted_segment(segment_to_shift)
            new_val_seg = round(float(self.x_shift_value_seg.text()) + shift_value, 3)
            self.x_shift_value_seg.setText(str(new_val_seg))

                   
        except:
            QtWidgets.QMessageBox.information(self,
                                              "Error",
                                              "Please select a segment to shift.")
            
    def shift_segment_right(self):
        try:
            print('hi')
            segment_to_shift = int(self.ComB_segment_selection.currentText())
            shift_value = float(self.LE_segment_shift_value.text())
            self.segments[segment_to_shift] += shift_value
            print(self.segments[segment_to_shift])
            self.plot_shifted_segment(segment_to_shift)
            new_val_seg = round(float(self.x_shift_value_seg.text()) + shift_value, 3)
            self.x_shift_value_seg.setText(str(new_val_seg))


                  
        except:
            QtWidgets.QMessageBox.information(self,
                                              "Error",
                                              "Please select a segment right.")


    def add_segments(self):
        segments_to_add = eval(self.LE_add_segment_value.text())  ##Input the value/ co-ordinate
        print("Segments to add: ", segments_to_add) 
        if type(segments_to_add) in [float,int]:
            segments_to_add = [segments_to_add]
        max_dur = 0
        max_file = None

        for file in self.file_names:
            file_name = self.all_files1[file]['data']
            max_time = max(file_name['Time'])
            # print(file)


            if max_time > max_dur:
                max_dur = max_time
                max_file = file

        # print("Hi")
        # print(max_file)
        ##max
        time_rounded = list(np.around(np.array(self.all_files1[max_file]['data']["Time"] + self.all_files1[max_file]['shift_values']['x']) ,2))
        # time_list = list(self.all_files1[max_file]['data']["Time"] + self.all_files1[max_file]['shift_values']['x'])

        if self.segments is None:
            self.segments = []
           
        for time_value in segments_to_add:
            try:
                print(time_value)
                print(self.segments)
                self.segments.append(self.all_files1[max_file]['data']["Time"][time_rounded.index(time_value)] )
                
        
            except ValueError as err: 
                print(f'Please change time to add, the step size is {time_rounded[1]-time_rounded[0]}')
                return
            
        self.segments = sorted(list(set(self.segments)))
        keys = [val for val in self.signal_dataItems.keys() if val.startswith("segment")]

        for val in keys:
            
            self.plot_widget_7.removeItem(self.signal_dataItems[val])
            del self.signal_dataItems[val]

            self.segment_plot.removeItem(self.difference_dataItems[val])
            del self.difference_dataItems[val]

        print(f"{self.segments=}")
        print("hello")
        # for index, segment in enumerate(self.q,start=1):
        #     self.segments_string = self.segments_string + f'Change Point {index}: {round(time_list[segment[0]], 5)} : {round(time_list[segment[1]], 5)}\n'


        # self.merge_segments()
        self.plot_segmentation()
        print(self.signal_dataItems.keys())
        print("Add")

        fig, ax = plt.subplots(2,1, figsize=(10, 10))

        if self.CB_voltage_rms_2.isChecked():

            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[0].legend()
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))


                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Voltage (V)")
                    ax[0].set_ylabel("Voltage (V)")
                    ax[0].title.set_text("Signal Plot")
                    ax[1].title.set_text("Derivative Plot")
                    
            # plt.savefig('Segmentation.png')
            plt.savefig('Segmentation_Voltage.png')

        if self.CB_current_rms_2.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Current (A)")
                    ax[0].set_ylabel("Current (A)")

            plt.savefig('Segmentation_Current.png')

        if self.CB_frequency_seg.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Frequency (Hz)")
                    ax[0].set_ylabel("Frequency (Hz)")

            plt.savefig('Segmentation_Frequency.png')


        # print(f"Segments added! {self.segments_string}")

    def delete_segments(self):
        print("hi!")
        print(self.signal_dataItems.keys())
        print(self.difference_dataItems.keys())
    

        segments_remove = np.array(eval(self.LE_remove_segment_value.text())) 
        if type(segments_remove) in [float,int, np.int32]:
            segments_remove = [segments_remove]

        keys = []
        for i in segments_remove:
            keys.append(f"segment {i}")
            self.segments[i] = None
          
            print(self.segments[i])
            self.ComB_segment_selection.removeItem(self.ComB_segment_selection.findText(str(i)))

        self.segments = [val for val in self.segments if val is not None]
        print(f"{self.segments=}")
        for val in keys:
            print(val)
            self.plot_widget_7.removeItem(self.signal_dataItems[val])
            del self.signal_dataItems[val]

            self.segment_plot.removeItem(self.difference_dataItems[val])
            del self.difference_dataItems[val]

        
        key = [v for v in self.signal_dataItems.keys() if v.startswith("segment")]
        # key_1 = [a for a in self.difference_dataItems.keys() if a.startswith("segment")]

        for v, new_key in zip(list(key), list(map(str , list(range(len(self.segments)))))):
            self.signal_dataItems[f"segment {new_key}"] = self.signal_dataItems.pop(v)
            self.difference_dataItems[f"segment {new_key}"] = self.difference_dataItems.pop(v)

                                     
        self.ComB_segment_selection.clear()
        self.ComB_segment_selection.addItems([""] + list(map(str, list(range(len(self.segments))))) )
        # self.ComB_segment_selection.addItems([""] + [str(val + 1) for val in range(len(self.segments)) ] )

                    
        print(self.segments)
        print("after")
        print(list(map(str, list(range(len(self.segments))))))
        print(self.signal_dataItems.keys())
        print(self.difference_dataItems.keys())

        fig, ax = plt.subplots(2,1, figsize=(10, 10))

        if self.CB_frequency_seg.isChecked():
            for file in self.file_names:
                name = file[:-4]
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:

                    self.q, self.z1, self.threshold = segmentation_trendfilter(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'],
                                                self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column])
                        
                    self.super_q[file] = [val for val in self.q]
                    signal_ = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]
                    self.max_val[0] = max(signal_) if self.max_val[0] < max(signal_) else self.max_val[0]
                    self.max_val[1] = max(self.z1) if self.max_val[1] < max(self.z1) else self.max_val[1]


                    ax[0].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column], label = name)
                    ax[0].legend()
                    ax[0].title.set_text("Signal Plot")                
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], self.z1, label = name)
                    ax[1].legend()
                    ax[1].title.set_text("Derivative Plot")
                    
                    ax[1].plot(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x'], [self.threshold]*len(self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']))

                    for i in range(len(self.segments)):
                                            
                        ax[0].plot([self.segments[i]]*3,[self.min_val, 0, self.max_val[0]])
                        ax[1].plot([self.segments[i]]*3,[0,0, self.max_val[1]])
                    
                    ax[0].grid(True)
                    ax[1].grid(True)
                    
                    ax[1].set_xlabel("Time (s)")
                    ax[1].set_ylabel("Frequency (Hz)")
                    ax[0].set_ylabel("Frequency (Hz)")

            plt.savefig('Segmentation_Frequency.png')



    ### Get the waveforms from the individual segments
    
        
    def get_segmented_plots(self): 

        from collections import defaultdict   
        
        """I need to extract the waveforms from each of the segments and plot them"""
        """self.segments contains the coordinates of the segments (segment indices) and self.all_files1 contains the data"""
        
        
        segmented_data = [[] for _ in range(len(self.segments)-1)]
        segmented_data_positive = [[] for _ in range(len(self.segments)-1)]
        segmented_data_negative = [[] for _ in range(len(self.segments)-1)]
        segmented_data_zero = [[] for _ in range(len(self.segments)-1)]
        # segmented_before = list()
        # segmented_after = list()
        # slopes = list()
        # segmented_data = defaultdict(list)
        segmented_before = defaultdict(list)
        segmented_after = defaultdict(list)
        segmented_before_positive = defaultdict(list)
        segmented_before_negative = defaultdict(list)
        segmented_before_zero = defaultdict(list)
        segmented_after_positive = defaultdict(list)
        segmented_after_negative = defaultdict(list)
        segmented_after_zero = defaultdict(list)



        from scipy import stats
        # slopes = defaultdict(list) ##To store slopes of data
        # trends = defaultdict(list) ##To store trends of data
        slopes = list()

        # path = r"C:\Users\Admin\OneDrive\Desktop\Test"
        
        name_list = list()

        if self.CB_voltage_rms_2.isChecked():

            for file in self.file_names:
                name = file
                name_list.append(name)
                
                            
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_voltage")]:
                    time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                    data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                    # print(self.all_files1.keys())
                
                    ###Extracting data and time for first segment
                    time_01 = time_signal[time_signal <= self.segments[0]]
                    data_01 = data_signal[time_signal <= self.segments[0]]
                    
                    segmented_before[name].append((time_01, data_01))

                    ###Extracting data and time for last segment
                    time_last = time_signal[time_signal >= self.segments[-1]]
                    data_last = data_signal[time_signal >= self.segments[-1]]
                    
                    segmented_after[name].append((time_last, data_last))

                    ###Extracting data and time in between the segments

                    for i in range(len(self.segments)-1):
                        start_index = self.segments[i]
                        end_index = self.segments[i+1]
                        print(start_index)
                        print(end_index)

                        t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                        d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                        
                        # t = [t for t in time_signal if start_index<=t<=end_index]
                        # d = [data for data, t in zip(data_signal, time_signal) if start_index <= t <= end_index]

                        
                        segmented_data[i].append((t, d))
###components of voltage/current
                
                    
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Positive sequence V")]:
                        time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                        data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                        time_before_positive = time_signal[time_signal <= self.segments[0]]
                        data_before_positive = data_signal[time_signal <= self.segments[0]]

                        segmented_before_positive[name].append((time_before_positive, data_before_positive)) ##before first segment postive

                        time_after_positive = time_signal[time_signal >= self.segments[-1]]
                        data_after_positive = data_signal[time_signal >= self.segments[-1]]

                        segmented_after_positive[name].append((time_after_positive, data_after_positive))  ##afterr last segment positive

                        for i in range(len(self.segments)-1):
                            start_index = self.segments[i]
                            end_index = self.segments[i+1]
                            print(start_index)
                            print(end_index)

                            t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                            d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]

                            segmented_data_positive[i].append((t, d))    ##in beteween segments positive
                        
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Negative sequence V")]:
                        time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                        data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                        time_before_negative = time_signal[time_signal <= self.segments[0]]
                        data_before_negative = data_signal[time_signal <= self.segments[0]]

                        segmented_before_negative[name].append((time_before_negative, data_before_negative))

                        time_after_negative = time_signal[time_signal >= self.segments[-1]]
                        data_after_negative = data_signal[time_signal >= self.segments[-1]]

                        segmented_after_negative[name].append((time_after_negative, data_after_negative))

                        for i in range(len(self.segments)-1):
                            start_index = self.segments[i]
                            end_index = self.segments[i+1]
                            print(start_index)
                            print(end_index)

                            t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                            d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]

                            segmented_data_negative[i].append((t, d))

                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Zero sequence V")]:
                        time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                        data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                        time_before_zero = time_signal[time_signal <= self.segments[0]]
                        data_before_zero = data_signal[time_signal <= self.segments[0]]

                        segmented_before_zero[name].append((time_before_zero, data_before_zero))

                        time_after_zero = time_signal[time_signal >= self.segments[-1]]
                        data_after_zero = data_signal[time_signal >= self.segments[-1]]

                        segmented_after_zero[name].append((time_after_zero, data_after_zero))

                        for i in range(len(self.segments)-1):
                            start_index = self.segments[i]
                            end_index = self.segments[i+1]
                            print(start_index)
                            print(end_index)

                            t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                            d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]

                            segmented_data_zero[i].append((t, d))

                

            fig, axs = plt.subplots(len(self.segments) + 1, 1, figsize = (10,8))
            # figsize = (10,10)
            
            # fig, axs = plt.subplots(2*(len(self.segments) + 1), 1, figsize=(10, 10))
            # fig = subplots.make_subplots(rows = len(self.segments) + 1, cols = 1, subplot_titles = [f'Waveforms from 0 to {np.round(self.segments[0], 3)}s'] + [f'Waveforms from {np.round(self.segments[i], 3)} to {np.round(self.segments[i+1], 3)}s' for i in range(len(self.segments)-1)] + [f'Waveforms from {np.round(self.segments[-1], 3)}s to end'])


                    
            # for k in range(0, 2*(len(self.segments) + 1), 2):
            for k in range(len(self.segments) + 1):
            # for k in range(2*(len(self.segments) + 1)):

                if k == 0:   ##Before first segment data
                    # table_data = [['', '', ''],['Filename', 'Slope', 'Trend']]
                    table_data = [['Filename', 'Slope', 'Trend', 'Negative unbalance', 'Zero Unbalance']]
                    
                    # table_data_final = []
                    # file_ind = 0
                    voltage_positive = defaultdict(list)
                    voltage_negative = defaultdict(list)
                    voltage_zero = defaultdict(list)
                    for name, segments in segmented_before.items():
                        print(f"*********************** File --> {name} *************************")
                        slopes = list()
                        flag = False
                        for t,d in segments:
                            if not flag:
                                flag = True
                                # fig.add_trace(go.Scatter(x = t, y = d, name = name), row = k+1, col = 1)
                                axs[k].plot(t,d,label = name)
                                axs[k].legend()
                                
                                                                                   
                            else:
                                axs[k].plot(t,d)
                                

                                
                                # fig.add_trace(go.Scatter(x = t, y = d, name = name), row = 1, col = 1)

                            axs[k].tick_params(axis = 'x', which = 'major', labelsize = 8)
                            axs[k].set_title(f'Waveforms from {0} to {np.round(self.segments[0], 3)}s')

                            axs[k].grid(True)
                                # axs[k].set_xlabel("Time (s)")
                            axs[k].set_ylabel("Voltage (V)")

                            # print("data brfore 0.4:", d)
                            try:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                                slope = round(slope, 5)
                                slopes.append(slope)
                                
                                # axs[k].plot(t, slopes*t + intercept)

                                for val in slopes:
                                    if val > 0:

                                        trend = "Increasing"
                                    elif val == 0:

                                        trend = "Constant"
                                    else:
                                        trend = "Decreasing"

                                # for name_p, data in segmented_before_positive.items(): ##components positive extraction and calculation
                                try:
                                    # voltage_positive = list()

                                    for t,d in segmented_before_positive[name]:
                                        # print("D:", type(d))
                                        Vp = abs(d)
                                        Vp = np.median(Vp)

                                    voltage_positive[name].append(Vp)

                                    print(f'Positive sequence voltage: {name}, {Vp}')

                                except Exception as e:
                                    print("Exception block:", e)
                                    Vp = "N/A"
                                    print(f'Positive sequence voltage: {name}, {Vp}')
                                        # voltage_positive[name].append(Vp)
                                    
                                # for name_n, data in segmented_before_negative.items():
                                try:
                                    
                                    for t,d in segmented_before_negative[name]:
                                        Vn = abs(d)
                                        Vn = np.median(Vn)
                                                                    
                                    voltage_negative[name].append(Vn)
                                    print(f'Negative sequence voltage: {name}, {Vn}')

                                except:
                                    Vn = "N/A"
                                    print(f'Negative sequence voltage: {name}, {Vn}')
                                    # voltage_negative[name].append(Vn)

                                # for name_z, data in segmented_before_zero.items():
                                try:
                                    
                                    for t,d in segmented_before_zero[name]:
                                        Vz = abs(d)
                                        Vz = np.median(Vz)
                                        # self.correlation_plot.plot(t,abs(d))

                                    voltage_zero[name].append(Vz)

                                    print(f'Zero sequence voltage: {name}, {Vz}')

                                except:
                                    Vz = "N/A"
                                    print(f'Zero sequence voltage: {name}, {Vz}')

                                percent_zero_unbalance = Vz/Vp if Vp!= float('nan') else "N/A"
                                percent_zero_unbalance = round(percent_zero_unbalance, 3)
                                percent_negative_unbalance = Vn/Vp if Vp!= float('nan') else "N/A"
                                percent_negative_unbalance = round(percent_negative_unbalance, 3)
                                

                            except:
                                slope = "N/A"
                                trend = "N/A"
                                percent_negative_unbalance = "N/A"
                                percent_zero_unbalance = "N/A"
                                
                                print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}' )

                            # print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}')
                            # table_data.append([name, slope, trend])

                        
                        print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}' )
                        table_data.append([name, slope, trend, percent_negative_unbalance, percent_zero_unbalance])

                        #     # table_data_final.append([name, slope, trend])

                    # table_data.pop(0)
                    
                    
                    # table = axs[k].table(cellText=table_data[1:], colLabels=table_data[0], cellLoc='center', loc = 'bottom') ###bbox = [0.2,0.68,0.89,0.88]
                    
                    table = axs[k].table(cellText=table_data[1:],colLabels=table_data[0], cellLoc='center', bbox=[0, -1, 1 , 0.6], edges= 'closed')
                    table.auto_set_font_size(False)                                   ###[xmin,ymin,width, height]
                    table.set_fontsize(8)
                    table.scale(2,2)
                    # axs[k].autoscale()
                    # # plt.subplots_adjust(right = 0.35)
                    plt.subplots_adjust(left = 0.2, bottom = 0.35)

                    # axs[k].set_xticks([])
                    # axs[k].tick_params(axis = 'x', direction = 'in', width=3, length = 10)

                    # file_ind += 1            
                

                elif k == len(self.segments):  ##After last segment data
                    table_data = [['Filename', 'Slope', 'Trend', 'Negative unbalance', 'Zero Unbalance']]
                    # table_data_final = []
                    voltage_positive = defaultdict(list)
                    voltage_negative = defaultdict(list)
                    voltage_zero = defaultdict(list)
                    for name, segments in segmented_after.items():
                        flag = False
                        for t,d in segments:
                            if not flag:
                                flag = True
                                # fig.add_trace(go.Scatter(x = t, y = d, name = name), row = k+1, col = 1)
                                axs[k].plot(t,d,label = name)
                                axs[k].legend()
                                
                            else:
                                axs[k].plot(t,d)
                                # fig.add_trace(go.Scatter(x = t, y = d), row = k+1, col = 1)
                            
                            axs[k].tick_params(axis = 'x', which = 'major', labelsize = 8)
                            axs[k].set_title(f'Segmented waveforms from {np.round(self.segments[-1], 3)}s onwards')
                            # axs[k].legend()
                            axs[k].grid(True)
                            axs[k].set_xlabel("Time (s)", fontsize = 8)
                            axs[k].xaxis.labelpad = -7
                            axs[k].set_ylabel("Voltage (V)")

                            try:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                                slope = round(slope, 5)
                                slopes.append(slope)
                                # corr_coeff = stats.pearsonr(d)
                                # print(corr_coeff)

                               
                                # axs[k].plot(t, slopes*t + intercept)

                                for val in slopes:
                                    if val > 0:

                                        trend = "Increasing"
                                    elif val == 0:

                                        trend = "Constant"
                                    else:
                                        trend = "Decreasing"

                                # for name, data in segmented_after_positive.items():
                                try:
                                    
                                    for t,d in segmented_after_positive[name]:
                                        Vp = (abs(d))
                                        Vp = np.median(Vp)
                                    voltage_positive[name].append(Vp)
                                    print(f'Positive sequence voltage: {name}, {Vp}')
                                
                                except:
                                    Vp = "N/A"
                                    print(f'Positive sequence voltage: {name}, {Vp}')
                                        # voltage_positive[name].append(Vp)

                                # for name, data in segmented_after_negative.items():
                                try:
                                    
                                    for t,d in segmented_after_negative[name]:
                                        Vn = (abs(d))
                                        Vn = np.median(Vn)
                                    voltage_negative[name].append(Vn)
                                    print(f'Negative sequence voltage: {name}, {Vn}')

                                except:
                                    Vn = "N/A"
                                    print(f'Negative sequence voltage: {name}, {Vn}')
                                            # voltage_negative[name].append(Vn)

                                # for name, data in segmented_after_zero.items():
                                        
                                try:
                                    
                                    for t,d in segmented_after_zero[name]:
                                        Vz = (abs(d))
                                        Vz = np.median(Vz)
                                    voltage_zero[name].append(Vz)
                                    print(f'Zero sequence voltage: {name}, {Vz}')

                                except:
                                    Vz = "N/A"
                                    print(f'Zero sequence voltage: {name}, {Vz}')

                                percent_zero_unbalance = Vz/Vp if Vp!= float('nan') else "N/A"
                                percent_zero_unbalance = round(percent_zero_unbalance, 3)
                                percent_negative_unbalance = Vn/Vp if Vp!= float('nan') else "N/A"
                                percent_negative_unbalance = round(percent_negative_unbalance, 3)
                                
                            
                            except ValueError as err:
                                slope = "N/A"
                                trend = "N/A"
                                percent_negative_unbalance = "N/A"
                                percent_zero_unbalance = "N/A"
                                print(f'After last segment: filename:{name}, slope:{slope}, trend:{trend}')

                        
                        print(f'After last segment: filename:{name}, slope:{slope}, trend:{trend}, %Negative Unbalance:{percent_negative_unbalance}, %Zero Unbalance:{percent_zero_unbalance}' )
                        table_data.append([name, slope, trend, percent_negative_unbalance, percent_zero_unbalance])
                    # table_data_final.append([name, slope, trend])
                    
                                        
                    
                    # table_data.pop(0)
                    table = axs[k].table(cellText=table_data[1:], colLabels=table_data[0], cellLoc='center', bbox = [0, -1, 1 , 0.6], edges= 'closed')
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(2,2)

                    # axs[k].set_xticks([])
                    # axs[k].tick_params(axis = 'x', direction = 'in', width=3, length = 10)
                                   
                    # table_data[0].visible(False)
                    # plt.subplots_adjust(right= 0.5)
                    # axs[k].autoscale()
                    # plt.subplots_adjust(hspace = 1)
                    # left=0.2, bottom=0.5
                    plt.subplots_adjust(left = 0.2, bottom = 0.35)

                     
                else:  ##In between segments data
                    
                    table_data = [['Filename', 'Slope', 'Trend', 'Negative unbalance', 'Zero Unbalance']]
                    # table_data_final = []
                    # for name, segments in segmented_data.items():
                    label_set = set()
                    i = 0
                    print("Value of k: ", k)
                    voltage_positive = defaultdict(list)
                    voltage_negative = defaultdict(list)
                    voltage_zero = defaultdict(list)
                    
                    for t,d in segmented_data[k-1]:
                    # for t, d in segmented_data[k//2 - 2]:
                        name = name_list[i]
                        # print(name)
                    
                        if name not in label_set:
                            label_set.add(name)
                            # fig.add_trace(go.Scatter(x = t, y = d, name = name), row = k, col = 1)

                            axs[k].plot(t,d, label = name) ##axs[0].plot(t,d)  
                            axs[k].legend()
                        else:
                            axs[k].plot(t,d)
                            # fig.add_trace(go.Scatter(x = t, y = d), row = k, col = 1)
            
                        axs[k].tick_params(axis = 'x', which = 'major', labelsize = 8)
                        axs[k].set_title(f'Segmented waveforms from {np.round(self.segments[k-1], 3)}s to {np.round(self.segments[k], 3)}s')
                        axs[k].grid(True)
                        axs[k].set_ylabel("Voltage (V)")

                        i = i+1

                        try:
                            slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                            slope = round(slope, 5)
                            slopes.append(slope)
                            # corr_coeff = stats.pearsonr(d)
                            # print(corr_coeff)
                            # axs[k].plot(t, slopes*t + intercept)

                            for val in slopes:
                                if val > 0:

                                    trend = "Increasing"
                                elif val == 0:

                                    trend = "Constant"
                                else:
                                    trend = "Decreasing"

                            for t, d in segmented_data_positive[k-1]: ##in between segments ka positive component of voltage
                            # for t,d in segmented_data_positive[k//2 - 2]:
                                try:
                                    
                                    # Vp = np.median(d)
                                    Vp = abs(d)
                                    Vp = np.median(Vp)
                                    voltage_positive[name].append(Vp)
                                    print(f'Positive sequence voltage: {name}, {Vp}')
                                
                                except:
                                    Vp = "N/A"
                                    print(f'Positive sequence voltage: {name}, {Vp}')
                                    # voltage_positive[name].append(Vp)
                            for t, d in segmented_data_negative[k-1]:
                            # for t,d in segmented_data_negative[k//2 - 2]:
                                try:
                
                                    # Vn = np.median(d)
                                    Vn = abs(d)
                                    Vn = np.median(Vn)
                                    
                                    voltage_negative[name].append(Vn)
                                    print(f'Negative sequence voltage: {name}, {Vn}')

                                except:
                                    Vn = "N/A"
                                    print(f'Negative sequence voltage: {name}, {Vn}')
                                    # voltage_negative[name].append(Vn)

                            for t, d in segmented_data_zero[k-1]:
                            # for t,d in segmented_data_zero[k//2 - 2]:
                                try:                         
                                
                                    # Vz = np.median(d)
                                    Vz = abs(d)
                                    Vz = np.median(Vz)
                                    voltage_zero[name].append(Vz)
                                    print(f'Zero sequence voltage: {name}, {Vz}')

                                except:
                            
                                    Vz = "N/A"
                                    print(f'Zero sequence voltage: {name}, {Vz}')
                            
                            percent_negative_unbalance = Vn/Vp if Vp!= float('nan') else "N/A"
                            percent_negative_unbalance = round(percent_negative_unbalance, 3)
                            percent_zero_unbalance = Vz/Vp if Vp!= float('nan') else "N/A"
                            percent_zero_unbalance = round(percent_zero_unbalance, 3)

                        except:
                            slope = "N/A"
                            trend = "N/A"
                            percent_negative_unbalance = "N/A"
                            percent_zero_unbalance = "N/A"
                            print(f'In between segments: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}')

                        
                        
                        print(f'In between segments: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}' )
                        table_data.append([name, slope, trend, percent_negative_unbalance, percent_zero_unbalance])

                    
                    # print("KK", k)
                    # table_data.pop(0)
                    # print("Table data:", table_data)
                    table = axs[k].table(cellText=table_data[1:],colLabels=table_data[0], cellLoc='center',bbox=[0, -1, 1 , 0.6], edges= 'closed')
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(2,2)
                    # axs[k].set_xticks([])
                    # axs[k].tick_params(axis = 'x', direction = 'in', width=3, length = 10)
                    # plt.subplots_adjust(right = 0.5)
                    # axs[k].autoscale()
                    # # plt.subplots_adjust(hspace = 1)
                    plt.subplots_adjust(left = 0.2, bottom = 0.35)
                   
                                
                                            
            plt.tight_layout()
        
                
            plt.savefig('segmented_plots_voltage.png')
            # pio.write_image(fig, 'segmented_plots_voltage.png')


        if self.CB_current_rms_2.isChecked():

            for file in self.file_names:
                name = file
                name_list.append(name)
                
                            
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("RMS_current")]:
                    time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                    data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                    # print(self.all_files1.keys())
                
                    ###Extracting data and time for first segment
                    time_01 = time_signal[time_signal <= self.segments[0]]
                    data_01 = data_signal[time_signal <= self.segments[0]]
                    
                    segmented_before[name].append((time_01, data_01))

                    ###Extracting data and time for last segment
                    time_last = time_signal[time_signal >= self.segments[-1]]
                    data_last = data_signal[time_signal >= self.segments[-1]]
                    
                    segmented_after[name].append((time_last, data_last))

                    ###Extracting data and time in between the segments

                    for i in range(len(self.segments)-1):
                        start_index = self.segments[i]
                        end_index = self.segments[i+1]
                        print(start_index)
                        print(end_index)

                        t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                        d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                        
                        # t = [t for t in time_signal if start_index<=t<=end_index]
                        # d = [data for data, t in zip(data_signal, time_signal) if start_index <= t <= end_index]

                        
                        segmented_data[i].append((t, d))

                
                    
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Positive sequence I")]:
                        time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                        data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                        time_before_positive = time_signal[time_signal <= self.segments[0]]
                        data_before_positive = data_signal[time_signal <= self.segments[0]]

                        segmented_before_positive[name].append((time_before_positive, data_before_positive))

                        time_after_positive = time_signal[time_signal >= self.segments[-1]]
                        data_after_positive = data_signal[time_signal >= self.segments[-1]]
                        segmented_after_positive[name].append((time_after_positive, data_after_positive))

                        for i in range(len(self.segments)-1):
                            start_index = self.segments[i]
                            end_index = self.segments[i+1]
                            print(start_index)
                            print(end_index)

                            t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                            d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]

                            segmented_data_positive[i].append((t, d))

                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Negative sequence I")]:
                        time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                        data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                        time_before_negative = time_signal[time_signal <= self.segments[0]]
                        data_before_negative = data_signal[time_signal <= self.segments[0]]

                        segmented_before_negative[name].append((time_before_negative, data_before_negative))

                        time_after_negative = time_signal[time_signal >= self.segments[-1]]
                        data_after_negative = data_signal[time_signal >= self.segments[-1]]

                        segmented_after_negative[name].append((time_after_negative, data_after_negative))

                        for i in range(len(self.segments)-1):
                            start_index = self.segments[i]
                            end_index = self.segments[i+1]
                            print(start_index)
                            print(end_index)

                            t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                            d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]

                            segmented_data_negative[i].append((t, d))

                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Zero sequence I")]:
                        time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                        data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                        time_before_negative = time_signal[time_signal <= self.segments[0]]
                        data_before_negative = data_signal[time_signal <= self.segments[0]]

                        segmented_before_zero[name].append((time_before_negative, data_before_negative))

                        time_after_negative = time_signal[time_signal >= self.segments[-1]]
                        data_after_negative = data_signal[time_signal >= self.segments[-1]]

                        segmented_after_zero[name].append((time_after_negative, data_after_negative))

                        for i in range(len(self.segments)-1):
                            start_index = self.segments[i]
                            end_index = self.segments[i+1]
                            print(start_index)
                            print(end_index)

                            t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                            d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]

                            segmented_data_zero[i].append((t, d))


            fig, axs = plt.subplots(len(self.segments) + 1, 1, figsize=(10, 10))

            # for k in range(0, 2*(len(self.segments) + 1), 2):
            for k in range(len(self.segments) + 1):
                        
                if k == 0:   ##Before first segment data
                    # table_data = [['', '', ''],['Filename', 'Slope', 'Trend']]
                    table_data = [['Filename', 'Slope', 'Trend', 'Negative unbalance', 'Zero Unbalance']]
                    current_positive = defaultdict(list)
                    current_negative = defaultdict(list)
                    current_zero = defaultdict(list)
                    # table_data_final = []
                    for name, segments in segmented_before.items():
                        slopes = list()
                        flag = False
                        for t,d in segments:
                            if not flag:
                                flag = True
                                axs[k].plot(t,d,label = name)
                                axs[k].legend()
                                
                                                    
                            else:
                                axs[k].plot(t,d)

                            axs[k].set_title(f'Waveforms from {0} to {np.round(self.segments[0], 3)}s')
                            axs[k].grid(True)
                                # axs[k].set_xlabel("Time (s)")
                            axs[k].set_ylabel("Current (A)")

                            try:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                                slope = round(slope, 5)
                                slopes.append(slope)

                                # axs[k].plot(t, slopes*t + intercept)

                                for val in slopes:
                                    if val > 0:

                                        trend = "Increasing"
                                    elif val == 0:

                                        trend = "Constant"
                                    else:

                                        trend = "Decreasing"

                                # for name_p, data in segmented_before_positive.items(): ##components positive extraction and calculation
                                try:
                                    # voltage_positive = list()

                                    for t,d in segmented_before_positive[name]:
                                        # print("D:", type(d))
                                        Ip = abs(d)
                                        Ip = np.median(Ip)

                                    current_positive[name].append(Ip)

                                    print(f'Positive sequence current: {name}, {Ip}')

                                except Exception as e:
                                    print("Exception block:", e)
                                    Ip = "N/A"
                                    print(f'Positive sequence current: {name}, {Ip}')
                                        # voltage_positive[name].append(Vp)
                                    
                                # for name_n, data in segmented_before_negative.items():
                                try:
                                    
                                    for t,d in segmented_before_negative[name]:
                                        In = abs(d)
                                        In = np.median(In)
                                                                    
                                    current_negative[name].append(In)
                                    print(f'Negative sequence current: {name}, {In}')

                                except:
                                    Vn = "N/A"
                                    print(f'Negative sequence current: {name}, {In}')
                                    # voltage_negative[name].append(Vn)

                                # for name_z, data in segmented_before_zero.items():
                                try:
                                    
                                    for t,d in segmented_before_zero[name]:
                                        Iz = abs(d)
                                        Iz = np.median(Iz)
                                        # self.correlation_plot.plot(t,abs(d))

                                    current_zero[name].append(Iz)

                                    print(f'Zero sequence current: {name}, {Iz}')

                                except:
                                    Iz = "N/A"
                                    print(f'Zero sequence current: {name}, {Iz}')

                                percent_zero_unbalance = Iz/Ip if Ip!= float('nan') else "N/A"
                                percent_zero_unbalance = round(percent_zero_unbalance, 3)
                                percent_negative_unbalance = In/Ip if Ip!= float('nan') else "N/A"
                                percent_negative_unbalance = round(percent_negative_unbalance, 3)
                            

                            except:
                                slope = "N/A"
                                trend = "N/A"
                                percent_negative_unbalance = "N/A"
                                percent_zero_unbalance = "N/A"
                                
                                print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}' )

                            # print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}')
                            # table_data.append([name, slope, trend])

                        
                        print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}' )
                        table_data.append([name, slope, trend, percent_negative_unbalance, percent_zero_unbalance])
                        #     # table_data_final.append([name, slope, trend])

                    # table_data.pop(0)
                    
                    
                    # table = axs[k].table(cellText=table_data[1:], colLabels=table_data[0], cellLoc='center', loc = 'bottom') ###bbox = [0.2,0.68,0.89,0.88]
                    table = axs[k].table(cellText=table_data[1:],colLabels=table_data[0], cellLoc='center', bbox=[0, -1, 1 , 0.6], edges= 'closed')
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(2,2)
                    # axs[k].autoscale()
                    # # plt.subplots_adjust(right = 0.35)
                    plt.subplots_adjust(left = 0.2, bottom = 0.35)

                    # axs[k].set_xticks([])

                      # print("data brfore 0.4:", d)
                            
                                      # self.correlation_plot.plot(t, abs(Vp)/abs(Vn))
                    # print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}' )
                    # table_data.append([name, slope, trend, percent_negative_unbalance, percent_zero_unbalance])
                    # #     # table_data_final.append([name, slope, trend])

                    # # table_data.pop(0)
                    # table = axs[k].table(cellText=table_data[1:], colLabels=table_data[0], cellLoc='center', loc = 'bottom') ###bbox = [0.2,0.68,0.89,0.88]
                    # table.auto_set_font_size(False)
                    # table.set_fontsize(10)
                    # table.scale(1,1.5)
                    # # axs[k].autoscale()
                    # # plt.subplots_adjust(left=0.2, bottom=0.35)
                    # # plt.subplots_adjust(right = 0.5)

                    # axs[k].set_xticks([])
                                

                elif k == len(self.segments):  ##After last segment data
                    table_data = [['Filename', 'Slope', 'Trend', 'Negative unbalance', 'Zero Unbalance']]
                    current_positive = defaultdict(list)
                    current_negative = defaultdict(list)
                    current_zero = defaultdict(list)
                    # table_data_final = []
                    for name, segments in segmented_after.items():
                        flag = False
                        for t,d in segments:
                            if not flag:
                                flag = True
                                axs[k].plot(t,d,label = name)
                                axs[k].legend()
                                
                            else:
                                axs[k].plot(t,d)
                            
                            axs[k].set_title(f'Segmented waveforms from {np.round(self.segments[-1], 3)}s onwards')
                            # axs[k].legend()
                            axs[k].grid(True)
                            axs[k].set_xlabel("Time (s)", fontsize = 8)
                            axs[k].xaxis.labelpad = -7
                            axs[k].set_ylabel("Current (A)")

                            try:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                                slope = round(slope, 5)
                                slopes.append(slope)

                                # axs[k].plot(t, slopes*t + intercept)

                                for val in slopes:
                                    if val > 0:

                                        trend = "Increasing"
                                    elif val == 0:

                                        trend = "Constant"
                                    else:
                                        trend = "Decreasing"
                                try:
                                    
                                    for t,d in segmented_after_positive[name]:
                                        Ip = (abs(d))
                                        Ip = np.median(Ip)
                                    current_positive[name].append(Ip)
                                    print(f'Positive sequence current: {name}, {Ip}')
                                
                                except:
                                    Ip = "N/A"
                                    print(f'Positive sequence current: {name}, {Ip}')
                                        # voltage_positive[name].append(Vp)

                                # for name, data in segmented_after_negative.items():
                                try:
                                    
                                    for t,d in segmented_after_negative[name]:
                                        In = (abs(d))
                                        In = np.median(In)
                                    current_negative[name].append(In)
                                    print(f'Negative sequence current: {name}, {In}')
                                except:
                                    In = "N/A"
                                    print(f'Negative sequence current: {name}, {In}')
                                            # voltage_negative[name].append(Vn)

                                # for name, data in segmented_after_zero.items():
                                        
                                try:
                                    
                                    for t,d in segmented_after_zero[name]:
                                        Iz = (abs(d))
                                        Iz = np.median(Iz)
                                    current_zero[name].append(Iz)
                                    print(f'Zero sequence current: {name}, {Iz}')

                                except:
                                    Iz = "N/A"
                                    print(f'Zero sequence current: {name}, {Vz}')

                                percent_zero_unbalance = Iz/Ip if Ip!= float('nan') else "N/A"
                                percent_zero_unbalance = round(percent_zero_unbalance, 3)
                                percent_negative_unbalance = In/Ip if Ip!= float('nan') else "N/A"
                                percent_negative_unbalance = round(percent_negative_unbalance, 3)
                                
                            
                            except ValueError as err:
                                slope = "N/A"
                                trend = "N/A"
                                percent_negative_unbalance = "N/A"
                                percent_zero_unbalance = "N/A"
                                print(f'After last segment: filename:{name}, slope:{slope}, trend:{trend}')

                        
                        print(f'After last segment: filename:{name}, slope:{slope}, trend:{trend}, %Negative Unbalance:{percent_negative_unbalance}, %Zero Unbalance:{percent_zero_unbalance}' )
                        table_data.append([name, slope, trend, percent_negative_unbalance, percent_zero_unbalance])
                    # table_data_final.append([name, slope, trend])
                    
                                        
                    
                    # table_data.pop(0)
                    table = axs[k].table(cellText=table_data[1:], colLabels=table_data[0], cellLoc='center', bbox=[0, -1, 1 , 0.6], edges= 'closed')
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(2,2)

                    # axs[k].set_xticks([])
                                   
                    # table_data[0].visible(False)
                    # plt.subplots_adjust(right= 0.5)
                    # axs[k].autoscale()
                    # plt.subplots_adjust(hspace = 1)
                    # left=0.2, bottom=0.5
                    plt.subplots_adjust(left = 0.2, bottom = 0.35)

                            
                            # except ValueError as err:
                            #     slope = "N/A"
                            #     trend = "N/A"
                            #     print(f'After last segment: filename:{name}, slope:{slope}, trend:{trend}')


                     
                else:  ##In between segments data
                    
                    table_data = [['Filename', 'Slope', 'Trend', 'Negative unbalance', 'Zero Unbalance']]

                    # table_data_final = []
                    # for name, segments in segmented_data.items():
                    label_set = set()
                    i = 0
                    print("Value of k: ", k)
                    current_positive = defaultdict(list)
                    current_negative = defaultdict(list)
                    current_zero = defaultdict(list)
                    
                    for t,d in segmented_data[k-1]:
                    # for t, d in segmented_data[k//2 - 2]:
                        name = name_list[i]
                        # print(name)
                    
                        if name not in label_set:
                            label_set.add(name)
                            axs[k].plot(t,d, label = name) ##axs[0].plot(t,d)  
                            axs[k].legend()
                        else:
                            axs[k].plot(t,d)
            

                        axs[k].set_title(f'Segmented waveforms from {np.round(self.segments[k-1], 3)}s to {np.round(self.segments[k], 3)}s')
                        axs[k].grid(True)
                        axs[k].set_ylabel("Current (A)")

                        i = i+1

                        try:
                            slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                            slope = round(slope, 5)
                            slopes.append(slope)

                            # axs[k].plot(t, slopes*t + intercept)

                            for val in slopes:
                                if val > 0:

                                    trend = "Increasing"
                                elif val == 0:

                                    trend = "Constant"
                                else:
                                    trend = "Decreasing"

                            for t, d in segmented_data_positive[k-1]: ##in between segments ka positive component of voltage
                            # for t,d in segmented_data_positive[k//2 - 2]:
                                try:
                                    
                                    # Vp = np.median(d)
                                    Ip = abs(d)
                                    Ip = np.median(Ip)
                                    current_positive[name].append(Ip)
                                    print(f'Positive sequence current: {name}, {Ip}')
                                
                                except:
                                    Ip = "N/A"
                                    print(f'Positive sequence current: {name}, {Ip}')
                                    # voltage_positive[name].append(Vp)
                            for t, d in segmented_data_negative[k-1]:
                            # for t,d in segmented_data_negative[k//2 - 2]:
                                try:
                
                                    # Vn = np.median(d)
                                    In = abs(d)
                                    In = np.median(In)
                                    
                                    current_negative[name].append(In)
                                    print(f'Negative sequence current: {name}, {In}')

                                except:
                                    In = "N/A"
                                    print(f'Negative sequence current: {name}, {In}')
                                    # voltage_negative[name].append(Vn)

                            for t, d in segmented_data_zero[k-1]:
                            # for t,d in segmented_data_zero[k//2 - 2]:
                                try:                         
                                
                                    # Vz = np.median(d)
                                    Iz = abs(d)
                                    Iz = np.median(Iz)
                                    current_zero[name].append(Iz)
                                    print(f'Zero sequence current: {name}, {Iz}')

                                except:
                            
                                    Iz = "N/A"
                                    print(f'Zero sequence current: {name}, {Iz}')
                            
                            percent_negative_unbalance = In/Ip if Ip!= float('nan') else "N/A"
                            percent_negative_unbalance = round(percent_negative_unbalance, 3)
                            percent_zero_unbalance = Iz/Ip if Ip!= float('nan') else "N/A"
                            percent_zero_unbalance = round(percent_zero_unbalance, 3)

                        except:
                            slope = "N/A"
                            trend = "N/A"
                            percent_negative_unbalance = "N/A"
                            percent_zero_unbalance = "N/A"
                            print(f'In between segments: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}')

                        
                        
                        print(f'In between segments: filename:{name}, slope:{slope}, trend:{trend}, Negative Unbalance:{percent_negative_unbalance}, Zero Unbalance:{percent_zero_unbalance}' )
                        table_data.append([name, slope, trend, percent_negative_unbalance, percent_zero_unbalance])

                    
                    # print("KK", k)
                    # table_data.pop(0)
                    # print("Table data:", table_data)
                    table = axs[k].table(cellText=table_data[1:],colLabels=table_data[0], cellLoc='center',bbox=[0, -1, 1 , 0.6], edges= 'closed')
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)
                    table.scale(2,2)
                    # axs[k].set_xticks([])
                    # plt.subplots_adjust(right = 0.5)
                    # axs[k].autoscale()
                    # # plt.subplots_adjust(hspace = 1)
                    plt.subplots_adjust(left = 0.2, bottom = 0.35)
                            
                                            
            plt.tight_layout()
        
            plt.savefig('segmented_plots_current.png')

        if self.CB_frequency_seg.isChecked():

            for file in self.file_names:
                name = file
                name_list.append(name)
                
                            
                for column in [item for item in self.all_files1[file]['data'].keys() if item.startswith("Frequency F_avg")]:
                    time_signal = self.all_files1[file]['data']["Time"] + self.all_files1[file]['shift_values']['x']
                    data_signal = self.all_files1[file]['data'][column] + self.all_files1[file]['shift_values'][column]

                    # print(self.all_files1.keys())
                
                    ###Extracting data and time for first segment
                    time_01 = time_signal[time_signal <= self.segments[0]]
                    data_01 = data_signal[time_signal <= self.segments[0]]
                    
                    segmented_before[name].append((time_01, data_01))

                    ###Extracting data and time for last segment
                    time_last = time_signal[time_signal >= self.segments[-1]]
                    data_last = data_signal[time_signal >= self.segments[-1]]
                    
                    segmented_after[name].append((time_last, data_last))

                    ###Extracting data and time in between the segments

                    for i in range(len(self.segments)-1):
                        start_index = self.segments[i]
                        end_index = self.segments[i+1]
                        print(start_index)
                        print(end_index)

                        t = time_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                        d = data_signal[(time_signal>=start_index) & (time_signal<=end_index)]
                        
                        # t = [t for t in time_signal if start_index<=t<=end_index]
                        # d = [data for data, t in zip(data_signal, time_signal) if start_index <= t <= end_index]

                        
                        segmented_data[i].append((t, d))

            fig, axs = plt.subplots(len(self.segments) + 1, 1, figsize=(10, 10))

            # for k in range(0, 2*(len(self.segments) + 1), 2):
            for k in range(len(self.segments) + 1):
                        
                if k == 0:   ##Before first segment data
                    # table_data = [['', '', ''],['Filename', 'Slope', 'Trend']]
                    table_data = [['Filename', 'Slope', 'Trend']]
                    
                    # table_data_final = []
                    for name, segments in segmented_before.items():
                        slopes = list()
                        flag = False
                        for t,d in segments:
                            if not flag:
                                flag = True
                                axs[k].plot(t,d,label = name)
                                axs[k].legend()
                                
                                                    
                            else:
                                axs[k].plot(t,d)

                            axs[k].set_title(f'Waveforms from {0} to {np.round(self.segments[0], 3)}s')
                            axs[k].grid(True)
                                # axs[k].set_xlabel("Time (s)")
                            axs[k].set_ylabel("Frequency (Hz)")

                            try:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                                slope = round(slope, 5)
                                slopes.append(slope)

                                # axs[k].plot(t, slopes*t + intercept)

                                for val in slopes:
                                    if val > 0:

                                        trend = "Increasing"
                                    elif val == 0:

                                        trend = "Constant"
                                    else:

                                        trend = "Decreasing"

                            except:
                                slope = "N/A"
                                trend = "N/A"
                            print(f'Before first segment: filename:{name}, slope:{slope}, trend:{trend}')

                            table_data.append([name, slope, trend])

                        table = axs[k].table(cellText=table_data[1:],colLabels=table_data[0], cellLoc='center',bbox=[0, -1, 1 , 0.6], edges= 'closed')
                        table.auto_set_font_size(False)
                        table.set_fontsize(8)
                        table.scale(2,2)
                        # axs[k].set_xticks([])
                        plt.subplots_adjust(left = 0.2, bottom = 0.2)

                           
                elif k == len(self.segments):

                    table_data = [['Filename', 'Slope', 'Trend']]
                    for name, segments in segmented_after.items():
                        flag = False
                        for t,d in segments:
                            if not flag:
                                flag = True
                                axs[k].plot(t,d,label = name)
                                axs[k].legend()
                                
                            else:
                                axs[k].plot(t,d)
                            
                            axs[k].set_title(f'Segmented waveforms from {np.round(self.segments[-1], 3)}s onwards')
                            # axs[k].legend()
                            axs[k].grid(True)
                            axs[k].set_xlabel("Time (s)", fontsize = 8)
                            axs[k].xaxis.labelpad = -7
                            axs[k].set_ylabel("Frequency (Hz)")

                            try:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                                slope = round(slope, 5)
                                slopes.append(slope)

                                # axs[k].plot(t, slopes*t + intercept)

                                for val in slopes:
                                    if val > 0:

                                        trend = "Increasing"
                                    elif val == 0:

                                        trend = "Constant"
                                    else:
                                        trend = "Decreasing"

                            except:
                                slope = "N/A"
                                trend = "N/A"

                            print(f'After last segment: filename:{name}, slope:{slope}, trend:{trend}')

                            table_data.append([name, slope, trend])

                        table = axs[k].table(cellText=table_data[1:],colLabels=table_data[0], cellLoc='center',bbox=[0, -1, 1 , 0.6], edges= 'closed')
                        table.auto_set_font_size(False)
                        table.set_fontsize(8)
                        table.scale(2,2)
                        # axs[k].set_xticks([])
                        plt.subplots_adjust(left = 0.2, bottom = 0.2)

                else:

                    table_data = [['Filename', 'Slope', 'Trend']]
                    label_set = set()
                    i = 0
                    
                    for t,d in segmented_data[k-1]:
                    # for t, d in segmented_data[k//2 - 2]:
                        name = name_list[i]
                        # print(name)
                    
                        if name not in label_set:
                            label_set.add(name)
                            axs[k].plot(t,d, label = name) ##axs[0].plot(t,d)  
                            axs[k].legend()
                        else:
                            axs[k].plot(t,d)
            

                        axs[k].set_title(f'Segmented waveforms from {np.round(self.segments[k-1], 3)}s to {np.round(self.segments[k], 3)}s')
                        axs[k].grid(True)
                        axs[k].set_ylabel("Frequency (Hz)")

                        i = i+1

                        try:
                            slope, intercept, r_value, p_value, std_err = stats.linregress(t,d/(max(d)-min(d)))
                            slope = round(slope, 5)
                            slopes.append(slope)

                            # axs[k].plot(t, slopes*t + intercept)

                            for val in slopes:
                                if val > 0:

                                    trend = "Increasing"
                                elif val == 0:

                                    trend = "Constant"
                                else:
                                    trend = "Decreasing"

                        except:
                            slope = "N/A"
                            trend = "N/A"

                        print(f'In between segments: filename:{name}, slope:{slope}, trend:{trend}')

                        table_data.append([name, slope, trend])

                    table = axs[k].table(cellText=table_data[1:],colLabels=table_data[0], cellLoc='center',bbox=[0, -1, 1 , 0.6], edges= 'closed')
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(2,2)
                    # axs[k].set_xticks([])
                    plt.subplots_adjust(left = 0.2, bottom = 0.2)



            plt.tight_layout()
            plt.savefig('segmented_plots_frequency.png')
                

        # pdf = FPDF()
          
        # pdf.add_page()
        # pdf.set_font("Arial", size = 12)

        # segmented_plot_files = os.path.join(path, f'segmented_plots.png' )
        # plt.savefig(segmented_plot_files)
        # segmented_plot.append(segmented_plot_files)
        # plt.savefig('segmented_plot.png')

                
        # for plots in segmented_plot:
        #     pdf.image(plots, w=200,h=200)

        # pdf.output('VoltageReport.pdf','F')
        # print("success")

        # pdf.output(path + 'VoltageReport.pdf','F')
        
        # print("success!!")

    

    def generate_report(self):

        pdf = FPDF()
        path = r"C:\Users\Admin\OneDrive\Desktop\Test"

              
        if self.LE_add_segment_value.text() == "":
            # QtWidgets.QMessageBox.information(self,"No segments added!")
            print("No segments added!")
            
        else:
            
            self.add_segments()
            print("Segments are added!")

        if self.LE_segment_shift_value.text() == "":
            print("No segments to be shifted!")
        
            # QtWidgets.QMessageBox.information(self,"No segments shifted!")
            
        else:
        
            self.plot_shifted_segment()
            print("Segment shifted!")
        # plt.savefig('Segmentation_Voltage.png')

        if self.LE_remove_segment_value.text() == "":
            print("No segments are deleted!")
        else:
            self.delete_segments()
            print("Segments are deleted!")

        self.get_segmented_plots()
           
        pdf.add_page()
        pdf.set_font("Arial", size = 12)
        if self.CB_voltage_rms_2.isChecked():
            pdf.cell(60, 10, 'Voltage Report.', 0, 1, 'C')
                        
            pdf.image('Segmentation_Voltage.png', w=200,h=200)
            pdf.ln(20)
      
            pdf.image('segmented_plots_voltage.png', w=200,h=200)

            pdf.output(path + 'VoltageReport.pdf','F')

        if self.CB_current_rms_2.isChecked():
            pdf.cell(60, 10, 'Current Report.', 0, 1, 'C')
                        
            pdf.image('Segmentation_Current.png', w=200,h=200)
            pdf.ln(20)
      
            pdf.image('segmented_plots_current.png', w=200,h=200)

            pdf.output(path + 'CurrentReport.pdf','F')

        if self.CB_frequency_seg.isChecked():
            pdf.cell(60,10, 'Frequency Report.', 0, 1, 'C')
            pdf.image('Segmentation_Frequency.png', w=200,h=200)
            pdf.ln(20)
            pdf.image('segmented_plots_frequency.png',w=200, h=200)
            pdf.output(path + 'FrequencyReport.pdf','F')

        print("Success!")
        QtWidgets.QMessageBox.information(self,"Success","Report Generated Successfully!")


    
                
    def load_tooltips(self):
        self.TT_remove_selection.setToolTip('To de-select item from list, click on list on a blank area')
        self.label_2.setToolTip('The voltages will be grouped in groups of 3, so enter variables appropriately')
        self.TT_voltage_set.setToolTip(
            'The voltages will be grouped in groups of 3, so enter variables appropriately\nThe order will be:\nA-phase,\nB-phase,\nC-phase')
        self.label_3.setToolTip('The currents will be grouped in groups of 3, so enter variables appropriately')
        self.TT_current_set.setToolTip(
            'The currents will be grouped in groups of 3, so enter variables appropriately\nThe order will be:\nA-phase,\nB-phase,\nC-phase')
        self.TT_set_selection.setToolTip('By default, the 1st set for each will be chosen')

        self.TT_plotting_voltage_rms.setToolTip(f'Calculations done using: √(Va² + Vb² + Vc²)')
        self.TT_plotting_current_rms.setToolTip("Calculations done using: (1/√3) × √(Ia² + Ib² + Ic²)")
        self.TT_plotting_power.setToolTip("Calculations done using:\n"
                                          "P = Va×Ia + Vb×Ib + Vc×Ic\n"
                                          "Q = (1/√3) × ((Va-Vb)×Ic + (Vb-Vc)×Ia + (Vc-Va)×Ic)")

        self.TT_plotting_sequence.setToolTip("Calculations done using:\n"
                                             "⍺ = 1∠120°\n\n"
                                             "Sₜ = ⌜ 1 1 1  ⌝\n"
                                             "       | ⍺² ⍺ 1  |\n"
                                             "       ⌞ ⍺ ⍺² 1⌟\n\n"
                                             "⌜ Vp ⌝          ⌜ Va ⌝\n"
                                             "|  Vn  | = Sₜ⁻¹ | Vb   |\n"
                                             "⌞ V0 ⌟          ⌞ Vc ⌟\n")
        

class DeselectableTreeView(QtWidgets.QListWidget):


    def __init__(self, parent):
        super().__init__(parent)

    def mousePressEvent(self, event):
        super(DeselectableTreeView, self).mousePressEvent(event)
        if not self.indexAt(event.pos()).isValid():
            self.clearSelection()
        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
