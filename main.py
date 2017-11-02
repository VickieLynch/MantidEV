#!/usr/bin/env python
from PyQt4 import QtGui, QtCore  # Import the PyQt4 module we'll need
import sys  # We need sys so that we can pass argv to QApplication
from subprocess import PIPE, Popen
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
        self.pointGroup_cmbx.currentIndexChanged.connect(self.change_pointGroup)
        self.laueGroup_cmbx.currentIndexChanged.connect(self.change_laueGroup)
        self.centering_cmbx.currentIndexChanged.connect(self.change_centering)
        self.sampleRadius_ledt.editingFinished.connect(self.change_sampleRadius)
        self.molecularFormula_ledt.editingFinished.connect(self.change_molecularFormula)
        self.Z_ledt.editingFinished.connect(self.change_Z)
        self.unitCellVolume_ledt.editingFinished.connect(self.change_unitCellVolume)
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
        self.pcharge_ledt.editingFinished.connect(self.change_pcharge)
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
        self.seconds = str(180)
        self.phi =str( 0.0)
        self.chi =str( 135.0)
        self.omega =str( 0.0)
        self.eventFileName=''
        self.calFileName=''
        self.minDSpacing =str( 0.5)
        self.minWavelength =str( 0.5)
        self.maxWavelength =str( 3.5)
        self.sampleRadius =str( 0.0)
        self.molecularFormula = ""
        self.Z =str( 0)
        self.unitCellVolume =str( 0)
        self.minQ=str(-20)
        self.maxQ=str(20)
        self.numPeaksToFind =str( 50)
        self.abcMin =str( 3)
        self.abcMax =str( 11)
        self.tolerance =str( 0.15)
        self.laueGroup = "Triclinic"
        self.pointGroup = "-1"
        self.centering = "P"
        self.peakRadius =str( 0.15)
        self.minIntensity =str( 100)
        self.nGrid=str(410)
        self.predictPeaks =str(0)
        self.numOrientations=str(0)
        self.pcharge=str(1.76e+13)
        self.edgePixels=str(20)
        self.changePhi=str(1)
        self.changeChi=str(0)
        self.changeOmega=str(1)
        self.useSymmetry=str(0)
        self.addOrientations=str(0)
        self.outputDirectory="."

    def change_instrument(self):
        self.instrument = self.instrument_cmbx.currentText()

    def change_laueGroup(self):
        self.laueGroup = self.laueGroup_cmbx.currentText()
        self.pointGroup_cmbx.clear()
        list1 = []
        if self.laueGroup == "Triclinic":
            list1 = [
                self.tr('-1'),
                self.tr('1'),
                ]
        elif self.laueGroup == "Monoclinic":
            list1 = [
                self.tr('2/m'),
                self.tr('2'),
                self.tr('m'),
                self.tr('112'),
                self.tr('112/m'),
                self.tr('11m'),
                ]
        elif self.laueGroup == "Orthorhombic":
            list1 = [
                self.tr('mmm'),
                self.tr('222'),
                self.tr('mm2'),
                self.tr('2mm'),
                self.tr('m2m'),
                ]
        elif self.laueGroup == "Tetragonal":
            list1 = [
                self.tr('4/m'),
                self.tr('4/mmm'),
                self.tr('-4'),
                self.tr('-42m'),
                self.tr('-4m2'),
                self.tr('4'),
                self.tr('422'),
                self.tr('4mm'),
                ]
        elif self.laueGroup == "Trigonal - Rhombohedral":
            list1 = [
                self.tr('-3'),
                self.tr('-3m'),
                self.tr('3'),
                self.tr('32'),
                self.tr('3m'),
                self.tr('-3 r'),
                self.tr('-31m'),
                self.tr('-3m r'),
                self.tr('-3m1'),
                self.tr('3 r'),
                self.tr('312'),
                self.tr('31m'),
                self.tr('32 r'),
                self.tr('321'),
                self.tr('3m r'),
                self.tr('3m1'),
                ]
        elif self.laueGroup == "Hexagonal":
            list1 = [
                self.tr('6/m'),
                self.tr('6/mmm'),
                self.tr('6'),
                self.tr('-6'),
                self.tr('622'),
                self.tr('6mm'),
                self.tr('-62m'),
                self.tr('-6m2'),
                ]
        elif self.laueGroup == "Cubic":
            list1 = [
                self.tr('m-3'),
                self.tr('m-3m'),
                self.tr('23'),
                self.tr('432'),
                self.tr('-43m'),
                ]
        self.pointGroup_cmbx.addItems(list1)


    def change_pointGroup(self):
        self.pointGroup = self.pointGroup_cmbx.currentText()

    def change_centering(self):
        self.centering = self.centering_cmbx.currentText()
        self.laueGroup_cmbx.clear()
        list1 = []
        if self.centering == "P":
            list1 = [
                self.tr('Triclinic'),
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                self.tr('Tetragonal'),
                self.tr('Trigonal - Rhombohedral'),
                self.tr('Hexagonal'),
                self.tr('Cubic'),
                ]
        elif self.centering == "I":
            list1 = [
                self.tr('Tetragonal'),
                self.tr('Monoclinic'),
                self.tr('Cubic'),
                ]
        elif self.centering == "A":
            list1 = [
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                ]
        elif self.centering == "B":
            list1 = [
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                ]
        elif self.centering == "C":
            list1 = [
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                ]
        elif self.centering == "F":
            list1 = [
                self.tr('Orthorhombic'),
                self.tr('Cubic'),
                ]
        elif self.centering == "Robv":
            list1 = [
                self.tr('Trigonal - Rhombohedral'),
                ]
        elif self.centering == "Rrev":
            list1 = [
                self.tr('Trigonal - Rhombohedral'),
                ]
        self.laueGroup_cmbx.addItems(list1)

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

    def change_molecularFormula(self):
        self.molecularFormula = self.molecularFormula_ledt.text()

    def change_Z(self):
        self.Z = self.toDouble(self.Z_ledt.text())

    def change_unitCellVolume(self):
        self.unitCellVolume = self.toDouble(self.unitCellVolume_ledt.text())

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

    def change_pcharge(self):
        temp = self.pcharge_ledt.text()
        self.pcharge = int(temp)

    def reject(self):
        print "script has been killed"
        self.proc.kill()
        
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
            "molecularFormula": self.molecularFormula,
            "Z": self.Z,
            "unitCellVolume": self.unitCellVolume,
            "minQ": self.minQ,
            "maxQ": self.maxQ,
            "numPeaksToFind": self.numPeaksToFind,
            "abcMin": self.abcMin,
            "abcMax": self.abcMax,
            "tolerance": self.tolerance,
            "pointGroup": self.pointGroup,
            "centering": self.centering,
            "peakRadius": self.peakRadius,
            "minIntensity": self.minIntensity,
            "nGrid": self.nGrid,
            "predictPeaks": self.predictPeaks,
            "numOrientations": self.numOrientations,
            "pcharge": self.pcharge,
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
            self.proc = Popen(['/usr/bin/python', str(path)], stdout=PIPE)
        else:
            path = self.outputDirectory+"/MantidEV.py"
            pathRun = self.outputDirectory+"/runMantidEV.py"
            templatePathRun = "./templateRunMantidEV.py"
            self.format_template(templatePath, path, **kw)
            print "PostProcessingScriptFilename for StartLiveData: ",path
            self.format_template(templatePathRun, pathRun, **kw)
            print "Python script for running StartLiveData: ",pathRun
            self.proc = Popen(['/usr/bin/python', str(path)], stdout=PIPE)
        while True:
            output = self.proc.stdout.readline()
            if output == '' and self.proc.poll() is not None:
                break
            if output:
                self.outputText.append(output.strip())
                QtGui.QApplication.processEvents()

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MantidEV()  # We set the form to be our MantidEV (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
