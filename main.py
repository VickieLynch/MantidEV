#!/usr/bin/env python
from PyQt4 import QtGui, QtCore  # Import the PyQt4 module we'll need
import sys  # We need sys so that we can pass argv to QApplication

import design  # This file holds our MainWindow and all design related things

# it also keeps events etc that we defined in Qt Designer
import os  # For listing filepath methods
import string

class MantidEV(QtGui.QMainWindow, design.Ui_MantidEV):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        self.setDefaults()
        self.DataFileName_ledt.editingFinished.connect(self.change_file)
        self.DataFile_btn.clicked.connect(self.browse_file)  # When the button is pressed
        self.instrument_cmbx.currentIndexChanged.connect(self.change_instrument)
        self.seconds_ledt.editingFinished.connect(self.change_seconds)
        self.phi_ledt.editingFinished.connect(self.input_phi)
        self.chi_ledt.editingFinished.connect(self.input_chi)
        self.omega_ledt.editingFinished.connect(self.input_omega)
        self.CalFileName_ledt.editingFinished.connect(self.change_cal_file)
        self.CalFile_btn.clicked.connect(self.browse_cal_file)  # When the button is pressed
        self.mindSpacing_ledt.editingFinished.connect(self.change_mindSpacing)
        self.minWavelength_ledt.editingFinished.connect(self.change_minWavelength)
        self.maxWavelength_ledt.editingFinished.connect(self.change_maxWavelength)
        self.sampleRadius_ledt.editingFinished.connect(self.change_sampleRadius)
        self.linScatt_ledt.editingFinished.connect(self.change_linScatt)
        self.linAbs_ledt.editingFinished.connect(self.change_linAbs)
        self.powerWavelength_ledt.editingFinished.connect(self.change_powerWavelength)
        self.minQspace_ledt.editingFinished.connect(self.change_minQ)
        self.maxQspace_ledt.editingFinished.connect(self.change_maxQ)
        self.numberPeaks_ledt.editingFinished.connect(self.change_numPeaks)
        self.minABC_ledt.editingFinished.connect(self.change_minABC)
        self.maxABC_ledt.editingFinished.connect(self.change_maxABC)
        self.tolerance_ledt.editingFinished.connect(self.change_tolerance)
        self.peakRadius_ledt.editingFinished.connect(self.change_peakRadius)
        self.minIntensity_ledt.editingFinished.connect(self.change_minIntensity)
        self.numberGridPoints_ledt.editingFinished.connect(self.change_numberGridPoints)
        self.predictPeaks_chbx.stateChanged.connect(self.predict_peaks)  # When the button is pressed
        self.numOrientations_ledt.editingFinished.connect(self.change_numOrientations)
        self.edgePixels_ledt.editingFinished.connect(self.change_edgePixels)
        self.changePhi_chbx.stateChanged.connect(self.change_phi)  # When the button is pressed
        self.changeChi_chbx.stateChanged.connect(self.change_chi)  # When the button is pressed
        self.changeOmega_chbx.stateChanged.connect(self.change_omega)  # When the button is pressed
        self.useSymmetry_chbx.stateChanged.connect(self.use_symmetry)  # When the button is pressed
        self.addOrientations_chbx.stateChanged.connect(self.add_orientations)  # When the button is pressed
        self.outputDirectory_ledt.editingFinished.connect(self.change_dir)
        self.outputDirectory_btn.clicked.connect(self.browse_dir)  # When the button is pressed

    def format_template(self, name, outfile, **kwargs):
        "This fills in the values for the template called 'name' and writes it to 'outfile'"
        template = open(name).read()
        formatter = string.Formatter()
        data = formatter.format(template, **kwargs)
        f = open(outfile, "w")
        try:
            f.write(data)
        finally:
            f.close()

    def line_prepender(self, filename, line):
        with open(filename, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(line.rstrip('\r\n') + '\n' + content)

    def setDefaults(self):
        self.instrument = "TOPAZ"
        self.seconds = str(60)
        self.phi =str( 0.0)
        self.chi =str( 135.0)
        self.omega =str( 0.0)
        self.eventFileName=''
        self.calFileName=''
        self.minDSpacing =str( 0.5)
        self.minWavelength =str( 0.5)
        self.maxWavelength =str( 3.5)
        self.sampleRadius =str( 0.0)
        self.linSca =str( 0.0)
        self.linAbs =str( 0.0)
        self.powerL =str( 4.0)
        self.minQ=str(-20)
        self.maxQ=str(20)
        self.numPeaksToFind =str( 50)
        self.abcMin =str( 3)
        self.abcMax =str( 11)
        self.tolerance =str( 0.15)
        self.peakRadius =str( 0.15)
        self.minIntensity =str( 100)
        self.nGrid=str(410)
        self.predictPeaks =str(0)
        self.numOrientations=str(0)
        self.edgePixels=str(20)
        self.changePhi=str(1)
        self.changeChi=str(0)
        self.changeOmega=str(1)
        self.useSymmetry=str(0)
        self.addOrientations=str(0)
        self.outputDirectory="."

    def change_instrument(self):
        self.instrument = self.instrument_cmbx.currentText()

    def change_seconds(self):
        temp = self.seconds_ledt.text()
        self.seconds = int(temp)

    def input_phi(self):
        self.phi = self.toDouble(self.phi_ledt.text())

    def input_chi(self):
        self.chi = self.toDouble(self.chi_ledt.text())

    def input_omega(self):
        self.omega = self.toDouble(self.omega_ledt.text())

    def change_file(self):
        self.eventFileName = self.DataFileName_ledt.text()

    def change_cal_file(self):
        self.calFileName = self.CalFileName_ledt.text()

    def change_dir(self):
        self.outputDirectory = self.outputDirectory_ledt.text()

    def browse_file(self):
        self.eventFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', '*.nxs *.h5') # Filename line
        if self.eventFileName:
            self.DataFileName_ledt.setText(self.eventFileName)

    def browse_cal_file(self):
        self.calFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', '*.DetCal') # Filename line
        if self.calFileName:
            self.CalFileName_ledt.setText(self.calFileName)

    def browse_dir(self):
        self.outputDirectory = QtGui.QFileDialog.getExistingDirectory(self, 'Select Directory', '', options=QtGui.QFileDialog.ShowDirsOnly)
        if self.outputDirectory:
            self.outputDirectory_ledt.setText(self.outputDirectory)

    def change_mindSpacing(self):
        self.minDSpacing = self.toDouble(self.mindSpacing_ledt.text())

    def change_minWavelength(self):
        self.minWavelength = self.toDouble(self.minWavelength_ledt.text())

    def change_maxWavelength(self):
        self.maxWavelength = self.toDouble(self.maxWavelength_ledt.text())

    def change_sampleRadius(self):
        self.sampleRadius = self.toDouble(self.sampleRadius_ledt.text())

    def change_linScatt(self):
        self.linScatt = self.toDouble(self.linScatt_ledt.text())

    def change_linAbs(self):
        self.linAbs = self.toDouble(self.linAbs_ledt.text())

    def change_powerWavelength(self):
        self.powerL = self.toDouble(self.powerWavelength_ledt.text())

    def change_minQ(self):
        self.minQ = self.toDouble(self.minQspace_ledt.text())

    def change_maxQ(self):
        self.maxQ = self.toDouble(self.maxQspace_ledt.text())

    def toDouble(self, temp):
        if temp.contains('.') or temp.contains("e"):
            result = float(temp)
        else:
            temp_int = int(temp)
            result = float(temp_int)
        return result

    def predict_peaks(self, state):
        if state == QtCore.Qt.Checked:
            self.predictPeaks = True
        else:
            self.predictPeaks = False

    def change_phi(self, state):
        if state == QtCore.Qt.Checked:
            self.changePhi = True
        else:
            self.changePhi = False

    def change_chi(self, state):
        if state == QtCore.Qt.Checked:
            self.changeChi = True
        else:
            self.changeChi = False

    def change_omega(self, state):
        if state == QtCore.Qt.Checked:
            self.changeOmega = True
        else:
            self.changeOmega = False

    def use_symmetry(self, state):
        if state == QtCore.Qt.Checked:
            self.useSymmetry = True
        else:
            self.useSymmetry = False

    def add_orientations(self, state):
        if state == QtCore.Qt.Checked:
            self.addOrientations = True
        else:
            self.addOrientations = False

    def change_numPeaks(self):
        temp = self.numberPeaks_ledt.text()
        self.numPeaksToFind = int(temp)

    def change_minABC(self):
        self.abcMin = self.toDouble(self.minABC_ledt.text())

    def change_maxABC(self):
        self.abcMax = self.toDouble(self.maxABC_ledt.text())

    def change_tolerance(self):
        self.tolerance = self.toDouble(self.tolerance_ledt.text())

    def change_peakRadius(self):
        self.peakRadius = self.toDouble(self.peakRadius_ledt.text())

    def change_minIntensity(self):
        self.minIntensity = self.toDouble(self.minIntensity_ledt.text())

    def change_numberGridPoints(self):
        temp = self.numberGridPoints_ledt.text()
        self.nGrid = int(temp)

    def change_numOrientations(self):
        temp = self.numOrientations_ledt.text()
        self.numOrientations = int(temp)

    def change_edgePixels(self):
        temp = self.edgePixels_ledt.text()
        self.edgePixels = int(temp)

    def reject(self):
        quit()
        
    def accept(self):
        #Generate MantidEV.py file 
        
        kw = {
            "instrument": self.instrument,
            "seconds": self.seconds,
            "phi": self.phi,
            "chi": self.chi,
            "omega": self.omega,
            "eventFileName": self.eventFileName,
            "calFileName": self.calFileName,
            "minDSpacing": self.minDSpacing,
            "minWavelength": self.minWavelength,
            "maxWavelength": self.maxWavelength,
            "sampleRadius": self.sampleRadius,
            "linSca": self.linSca,
            "linAbs": self.linAbs,
            "powerL": self.powerL,
            "minQ": self.minQ,
            "maxQ": self.maxQ,
            "numPeaksToFind": self.numPeaksToFind,
            "abcMin": self.abcMin,
            "abcMax": self.abcMax,
            "tolerance": self.tolerance,
            "peakRadius": self.peakRadius,
            "minIntensity": self.minIntensity,
            "nGrid": self.nGrid,
            "predictPeaks": self.predictPeaks,
            "numOrientations": self.numOrientations,
            "edgePixels": self.edgePixels,
            "changePhi": self.changePhi,
            "changeChi": self.changeChi,
            "changeOmega": self.changeOmega,
            "useSymmetry": self.useSymmetry,
            "addOrientations": self.addOrientations,
            "outputDirectory": self.outputDirectory
        }

        templatePath = "./templateMantidEV.py"
        if self.eventFileName:
            path = self.outputDirectory+"/MantidEV.py"
            self.format_template(templatePath, path, **kw)
            #Reverse order since each line put at beginning
            self.line_prepender(path, 'from mantid.simpleapi import *')
            self.line_prepender(path, 'sys.path.append("/opt/mantidnightly/bin")')
            self.line_prepender(path, 'import sys')
            print "Python script for NeXus file: ",path
            os.system("/usr/bin/python "+str(path))
        else:
            path = self.outputDirectory+"/MantidEV.py"
            pathRun = self.outputDirectory+"/runMantidEV.py"
            templatePathRun = "./templateRunMantidEV.py"
            self.format_template(templatePath, path, **kw)
            print "PostProcessingScriptFilename for StartLiveData: ",path
            self.format_template(templatePathRun, pathRun, **kw)
            print "Python script for running StartLiveData: ",pathRun
            os.system("/usr/bin/python "+str(pathRun))
        quit()

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MantidEV()  # We set the form to be our MantidEV (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
