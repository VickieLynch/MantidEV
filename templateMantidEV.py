import matplotlib.pyplot as plt
from lin_abs_coef import lin_abs_coef
from matplotlib import colors
from matplotlib.ticker import LogFormatter
from mpl_toolkits.mplot3d import proj3d
import numpy as np
from mantid.kernel import ConfigService
from mantid.kernel import V3D
from mantid.geometry import OrientedLattice, PointGroupFactory
from mantid import config
ConfigService.setConsoleLogLevel(2)
config['Q.convention'] = 'Crystallography'
from scipy.optimize import basinhopping
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import current_process

class MantidEV():
    def __init__(self):
        self.eventFileName = "{eventFileName}"
        self.phi = {phi}
        self.chi = {chi}
        self.omega = {omega}
        self.calFileName = "{calFileName}"
        self.minDSpacing = {minDSpacing}
        self.minWavelength = {minWavelength}
        self.maxWavelength = {maxWavelength}
        self.sampleRadius = {sampleRadius}
        self.molecularFormula = "{molecularFormula}"
        self.Z = {Z}
        self.unitCellVolume = {unitCellVolume}
        self.minQ = {minQ}
        self.maxQ = {maxQ}
        self.numPeaksToFind = {numPeaksToFind}
        self.abcMin = {abcMin}
        self.abcMax = {abcMax}
        self.tolerance = {tolerance}
        self.pointGroup = "{pointGroup}"
        self.centering = "{centering}"
        self.peakRadius = {peakRadius}
        self.minIntensity = {minIntensity}
        self.nGrid = {nGrid}
        self.predictPeaks = {predictPeaks}
        self.outputDirectory = "{outputDirectory}"
        self.LorentzCorr = True
        self.numOrientations = {numOrientations}
        self.pcharge = {pcharge}
        self.edgePixels = {edgePixels}
        self.changePhi = {changePhi}
        self.changeChi = {changeChi}
        self.changeOmega = {changeOmega}
        self.useSymmetry = {useSymmetry}
        self.addOrientations = {addOrientations}
        self.seconds = {seconds}

    def select_wksp(self):
        try:
            props=input.run().getProperties()
            self._wksp = input
            SetGoniometer(Workspace=self._wksp,Axis0="omega,0,1,0,1",Axis1="chi,0,0,1,1",Axis2="phi,0,1,0,1")
            self.last = 1
        except:
            self._wksp = Load(Filename=self.eventFileName,OutputWorkspace="eventWksp",
                              FilterByTimeStart = self.time_start, FilterByTimeStop = self.time_stop)
            self.time_start = self.time_stop
            self.time_stop += int(self.seconds)
            duration = self._wksp.getRun().getProperty("duration").value
            if self.time_start > duration:
                print ("No events next time")
                self.last = 1
        angles = self._wksp.run().getGoniometer().getEulerAngles('YZY')
        if angles[1] == 0.0:
            AddSampleLog(Workspace=self._wksp, LogName='phi', LogText=str(self.phi), LogType='Number')
            AddSampleLog(Workspace=self._wksp, LogName='chi', LogText=str(self.chi), LogType='Number')
            AddSampleLog(Workspace=self._wksp, LogName='omega', LogText=str(self.omega), LogType='Number')
            SetGoniometer(Workspace=self._wksp,Axis0="omega,0,1,0,1",Axis1="chi,0,0,1,1",Axis2="phi,0,1,0,1")
            angles = self._wksp.run().getGoniometer().getEulerAngles('YZY')
        print ("phi,chi,omega=",angles[0],angles[1],angles[2])

        if self.calFileName:
            LoadIsawDetCal(InputWorkspace=self._wksp,Filename=str(self.calFileName))  # load cal file
        
        try:
            self._wksp = ConvertUnits(InputWorkspace = self._wksp,OutputWorkspace="eventWksp",Target="dSpacing",EMode="Elastic")
            self._wksp = CropWorkspace(InputWorkspace = self._wksp, XMin = self.minDSpacing,OutputWorkspace="eventWksp")
            self._wksp = ConvertUnits(InputWorkspace = self._wksp,OutputWorkspace="eventWksp",Target="Wavelength",EMode="Elastic")
            self._wksp = CropWorkspace(InputWorkspace = self._wksp, XMin = self.minWavelength, XMax = self.maxWavelength,OutputWorkspace="eventWksp")
        except:
            pass

        if self.sampleRadius > 0:
            linSca, linAbs, calculatedRadius = lin_abs_coef(self.molecularFormula, self.Z, self.unitCellVolume, 0)
            self._wksp = AnvredCorrection(InputWorkspace = self._wksp,LinearScatteringCoef = linSca,LinearAbsorptionCoef = linAbs,
                Radius = self.sampleRadius,PowerLambda = 4.0,OutputWorkspace="eventWksp")
            # Lorentz correction already added so not in ConvertToMD
            self.LorentzCorr = False

        if self._wksp:
            try:
                output = ConvertToMD(InputWorkspace = self._wksp, QDimensions = 'Q3D', dEAnalysisMode = 'Elastic',
                     LorentzCorrection = self.LorentzCorr, OutputWorkspace='output',
                     Q3DFrames = 'Q_sample', QConversionScales = 'Q in A^-1',
                     MinValues = str(self.minQ)+','+str(self.minQ)+','+str(self.minQ),
                     MaxValues = str(self.maxQ)+','+str(self.maxQ)+','+str(self.maxQ))
            except:
                print ("Viewer failed with no data: decrease minimum intensity")
                sys.exit()
            if self.time_start <= self.seconds:
                self._md = CloneMDWorkspace(InputWorkspace=output, OutputWorkspace='sum_output')
            else:
                self._md += output
            self.events = self._md.getNEvents()
        else:
            self.events = 0

    def crystalplan(self):
        angles = self.peaks_ws.run().getGoniometer().getEulerAngles('YZY')
        X0 = []
        self.numAngles = 0
        if self.changePhi:
            self.numAngles += 1
            X0.append(angles[0])
        if self.changeChi:
            self.numAngles += 1
            X0.append(angles[1])
        if self.changeOmega:
            self.numAngles += 1
            X0.append(angles[2])
        pool = ThreadPool(2)
        threadNo = range(2)
        results = pool.map(self.optimize, threadNo)
        minPeaks = 0
        for i in range(len(results)):
            if results[i].fun < minPeaks:
                X = results[i].x
                minPeaks = results[i].fun
        pool.close()
        pool.join()
        if (self.addOrientations):
            X = np.concatenate((X0, X))
        self.csv_write(X)
        self.fopt(X)

    def csv_write(self, X):
        import csv

        fileName = self.outputDirectory+"/CrystalPlan"+str(self.events)+".csv"
        print ("Goniometer plan: ", fileName)
        f = open(fileName, 'wt')
        comment0 = '\"measured\"'
        commentn = '\"optimized\"'
        try:
            writer = csv.writer(f, quotechar = "'")
            writer.writerow( ('#Title:','\"text\"'))
            writer.writerow( ('#Comment:',''))
            if self.numAngles == 1:
                writer.writerow( ('Phi', 'CountFor', 'CountValue', 'Comment') )
            elif self.numAngles == 2:
                writer.writerow( ('Phi', 'Omega', 'CountFor', 'CountValue', 'Comment') )
            elif self.numAngles == 2:
                writer.writerow( ('Phi','Chi', 'Omega', 'CountFor', 'CountValue', 'Comment') )
            for i in range(len(X)/self.numAngles):
                if i == 0 and self.addOrientations:
                   comment = comment0
                else:
                   comment = commentn
                if self.numAngles == 1:
                    writer.writerow((X[self.numAngles*i], 'pcharge', self.pcharge, comment))
                elif self.numAngles == 2:
                    writer.writerow((X[self.numAngles*i], X[self.numAngles*i+1], 'pcharge', self.pcharge, comment))
                elif self.numAngles == 3:
                    writer.writerow((X[self.numAngles*i], X[self.numAngles*i+1], X[self.numAngles*i+2], 'pcharge', self.pcharge, comment))
        finally:
            f.close()

        print (open(fileName, 'rt').read())

    def optimize(self, seed):
        # the starting point
        np.random.seed(seed)
        # the starting point
        x0 = []
        for i in range(2*self.numOrientations):
            x0.append(np.random.uniform(0., 360.0))
        
        # define the new step taking routine and pass it to basinhopping
        mytakestep = RandomDisplacementBounds(0.0, 360.0)
        
        # use method
        minimizer_kwargs = dict(method="Nelder-Mead", options={{'disp': False, 'ftol':1.00, 'maxiter':3, 'maxfev':15}})
        result = basinhopping(self.f, x0, niter=1, minimizer_kwargs=minimizer_kwargs, take_step=mytakestep)
        return result

    def orthogonal_proj(self, zfront, zback):
        a = (zfront+zback)/(zfront-zback)
        b = -2*(zfront*zback)/(zfront-zback)
        return np.array([[1,0,0,0],
                            [0,1,0,0],
                            [0,0,a,b],
                            [0,0,-0.0001,zback]])

    def plot_Q(self):
        proj3d.persp_transformation = self.orthogonal_proj
        try:
        # Find size of screen
            import curses
            stdscr = curses.initscr()
            self.screen_x,self.screen_y = stdscr.getmaxyx()
            self.screen_x = min(self.screen_x, self.screen_y)
            self.screen_y = self.screen_x
        except:
            self.screen_x = 40
            self.screen_y = 40
        Box = BinMD(InputWorkspace = self._md,
                 AlignedDim0 = 'Q_sample_x,'+str(self.minQ)+','+str(self.maxQ)+','+str(self.nGrid),
                 AlignedDim1 = 'Q_sample_y,'+str(self.minQ)+','+str(self.maxQ)+','+str(self.nGrid),
                 AlignedDim2 = 'Q_sample_z,'+str(self.minQ)+','+str(self.maxQ)+','+str(self.nGrid))
        signal = Box.getSignalArray()
        step = float(self.maxQ-self.minQ)/(self.nGrid-1)
        self.c = []
        self.x = []
        self.y = []
        self.z = []
        self.s = []
        for Hj in range(self.nGrid):
            for Kj in range(self.nGrid):
                for Lj in range(self.nGrid):
                    if signal[Lj,Kj,Hj] >= self.minIntensity:
                        self.c.append(signal[Lj,Kj,Hj])
                        self.x.append(self.minQ+step*Lj)
                        self.y.append(self.minQ+step*Kj)
                        self.z.append(self.minQ+step*Hj)
                        self.s.append(10)
        if (len(self.c)) < 1:
            print ("Viewer failed with no data: decrease minimum intensity")
            sys.exit()
        fig = plt.figure("ReciprocalSpace"+str(self.events),figsize = (self.screen_x, self.screen_y))
        ax = fig.gca(projection = '3d')
        vmin = min(self.c)
        vmax = max(self.c)
        cm = plt.cm.get_cmap('rainbow')
        logNorm = colors.LogNorm(vmin = vmin, vmax = vmax)
        se = ax.scatter(self.x, self.y, self.z, c = self.c, vmin = vmin, vmax = vmax, cmap = cm, norm = logNorm, s = self.s, alpha = 1.0, picker = True)
        ax.text2D(0.05, 0.90, "# Events = "+str(self.events) +
                "\nHold mouse button to rotate." +
                "\nClose window to continue." ,
            fontsize = 20, transform = ax.transAxes)
        ax.set_xlabel('Q$_X$')
        ax.set_ylabel('Q$_Y$')
        ax.set_zlabel('Q$_Z$')
    
    
        formatter = LogFormatter(10, labelOnlyBase = False)
        plt.colorbar(se,ticks = [10,20,50,100,200,500,1000,2000,5000,10000,20000,50000,1e5,2e5,5e5,1e6,2e6,5e6,1e7,2e7,2e8], format = formatter)
        # Create cubic bounding box to simulate equal aspect ratio
        max_range = max([max(self.x)-min(self.x), max(self.y)-min(self.y), max(self.z)-min(self.z)])
        Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(max(self.x)+min(self.x))
        Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(max(self.y)+min(self.y))
        Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(max(self.z)+min(self.z))
        # Comment or uncomment following both lines to test the fake bounding box:
        for xb, yb, zb in zip(Xb, Yb, Zb):
           ax.plot([xb], [yb], [zb], 'w')
        plt.show()

    def find_peaks(self):
        distance_threshold = 0.9 * 6.28 / float(self.abcMax)
        #End Input from GUI
        self.bkg_inner_radius = self.peakRadius
        self.bkg_outer_radius = self.peakRadius  * 1.25992105 # A factor of 2 ^ (1/3)
        #Create peaks for all 3D grid point about minIntensity

        self.peaks_ws = FindPeaksMD( self._md, MaxPeaks = self.numPeaksToFind, OutputWorkspace="peaks",
                                PeakDistanceThreshold = distance_threshold )
        self.instrument = self.peaks_ws.getInstrument()
        self.npeaks = self.peaks_ws.getNumberPeaks()
     
        try:
            FindUBUsingFFT( PeaksWorkspace = self.peaks_ws, MinD = self.abcMin, MaxD = self.abcMax, Tolerance = self.tolerance)
            SaveIsawUB(self.peaks_ws, self.outputDirectory+"/Peaks"+str(self.events)+".mat")
            print ("UB matrix: ", self.outputDirectory+"/Peaks"+str(self.events)+".mat")
            self.numInd,errInd = IndexPeaks( PeaksWorkspace = self.peaks_ws, Tolerance = self.tolerance, RoundHKLs = False)
            try:
                pg = PointGroupFactory.createPointGroup(self.pointGroup)
                self.numInd,errInd = SelectCellOfType( PeaksWorkspace=self.peaks_ws, CellType=str(pg.getLatticeSystem()), 
                      Centering=self.centering, AllowPermutations=True, Apply=True, Tolerance=self.tolerance )
                SaveIsawUB(self.peaks_ws, self.outputDirectory+"/PeaksSym"+str(self.events)+".mat")
                print ("UB matrix: ", self.outputDirectory+"/PeaksSym"+str(self.events)+".mat")
            except:
                print ("Point group symmetry failed")
            if self.predictPeaks or self.addOrientations:
                self.peaks_ws = PredictPeaks(InputWorkspace=self.peaks_ws, WavelengthMin=self.minWavelength,
                     EdgePixels=self.edgePixels,
                     WavelengthMax=self.maxWavelength, MinDSpacing=self.minDSpacing, OutputWorkspace="peaks")
            CopySample(InputWorkspace = self.peaks_ws,OutputWorkspace = self._wksp,CopyName = '0',CopyMaterial = '0',CopyEnvironment = '0',CopyShape = '0')
        except:
            self.numInd = 0
            print ("UB matrix not found")

        # this is number of predicted peaks if that option is selected
        nPeaks = self.peaks_ws.getNumberPeaks()
        self.sumIsigI = 0.0
        self.sumIsigI2 = 0.0
        self.sumIsigI5 = 0.0
        for i in range(nPeaks):
            peak = self.peaks_ws.getPeak(i)
            qsample = peak.getQSampleFrame()
            intensity = peak.getIntensity()
            sigI = peak.getSigmaIntensity()
            if sigI !=  0.0:
                IsigI = intensity/sigI
                if (IsigI > 10.):
                    self.sumIsigI +=  1.0
                if (IsigI > 5.):
                    self.sumIsigI5 +=  1.0
                if (IsigI > 2.):
                    self.sumIsigI2 +=  1.0
            else:
                IsigI = 0.0
            detID = int(peak.getDetectorID())
            bank = self.instrument.getDetector(detID).getName()
            self.c = np.append(self.c,max(self.minIntensity,intensity))
            self.x = np.append(self.x,qsample.X())
            self.y = np.append(self.y,qsample.Y())
            self.z = np.append(self.z,qsample.Z())
            self.s = np.append(self.s,320)
        self.sumIsigI /=  nPeaks/100.0
        self.sumIsigI5 /=  nPeaks/100.0
        self.sumIsigI2 /=  nPeaks/100.0

    def plot_peaks(self, xy):
        plt.rcParams.update({{'font.size': 6}})
        figS, axs = plt.subplots(10, 10, sharex=False, sharey=False, figsize=(self.screen_x, self.screen_y))
        figS.canvas.set_window_title('Peaks'+str(self.events))
        axs = axs.flatten()
        if xy:
            peakRadius2 = self.peakRadius
            peakRadius3 = 0.05
            bins = '100,100,1'
        else:
            peakRadius2 = 0.05
            peakRadius3 = self.peakRadius
            bins = '100,1,100'
        nPeaks = self.peaks_ws.getNumberPeaks()
        for i in range(nPeaks):
            j = i%len(axs)
            peak = self.peaks_ws.getPeak(i)
            hkl = str(int(peak.getH()+0.5))+','+str(int(peak.getK()+0.5))+','+str(int(peak.getL()+0.5))
            qsample = peak.getQSampleFrame()
            sl2d = BinMD(InputWorkspace=self._md, AxisAligned=False, BasisVector0='Q_sample_x,Angstrom^-1,1,0,0',
                BasisVector1='Q_sample_y,Angstrom^-1,0,1,0', BasisVector2='Q_sample_z,Angstrom^-1,0,0,1',
                OutputExtents=str(qsample.X()-self.peakRadius)+','+str(qsample.X()+self.peakRadius)+','+str(qsample.Y()-peakRadius2)
                +','+str(qsample.Y()+peakRadius2)+','+str(qsample.Z()-peakRadius3)+','+str(qsample.Z()+peakRadius3),
                OutputBins=bins, Parallel=True)
            #10 subplots per page
            pcm=self.Plot2DMD(axs[j],sl2d, hkl, NumEvNorm=False)
            figS.colorbar(pcm,ax=axs[j])
            if j == len(axs)-1 and i < nPeaks-1:
                plt.show()
                figS, axs = plt.subplots(10, 10, sharex=False, sharey=False, figsize=(self.screen_x, self.screen_y))
                figS.canvas.set_window_title('Peaks'+str(self.events))
                axs = axs.flatten()
            # do not draw axes for non-existant peaks
            for k in range(j+1,len(axs)):
                axs[k].axis('off')
        plt.show()
    
    def plot_Qpeaks(self):
        plt.rcParams.update({{'font.size': 10}})
        self.ws = CreatePeaksWorkspace(InstrumentWorkspace=self._wksp, NumberOfPeaks=0, OutputWorkspace="events")
        CopySample(InputWorkspace = self.peaks_ws,OutputWorkspace = self.ws,CopyName = '0',CopyMaterial = '0',CopyEnvironment = '0',CopyShape = '0')
        figP = plt.figure("EventsAndPeaks"+str(self.events),figsize = (self.screen_x, self.screen_y))
        self.axP = figP.gca(projection = '3d')
        self.plot_lattice('green')
        self.c[self.c<=1] = 1.
        vmin = min(self.c)
        vmax = max(self.c)
        cm = plt.cm.get_cmap('rainbow')
        logNorm = colors.LogNorm(vmin = vmin, vmax = vmax)
        sp = self.axP.scatter(self.x, self.y, self.z, c = self.c, vmin = vmin, vmax = vmax, cmap = cm, norm = logNorm, s = self.s, alpha = 0.2, picker = True)
        self.props = dict(boxstyle = 'round', facecolor = 'wheat', alpha = 1.0)

        cid = figP.canvas.mpl_connect('pick_event', self.onpick3)

        try:
            lattice = self.peaks_ws.sample().getOrientedLattice()
        except:
            lattice = OrientedLattice(1,1,1)

        self.axP.text2D(0.05, 0.70, "# Events = "+str(self.events)+
            "\nPeaks with I/sigI > 10 = "+'%.1f'%(self.sumIsigI) +
            "%\nPeaks with I/sigI > 5 = "+'%.1f'%(self.sumIsigI5) +
            "%\nPeaks with I/sigI > 2 = "+'%.1f'%(self.sumIsigI2) +
            "%\n# peaks indexed = "+str(self.numInd) + " out of " + str(self.npeaks) +
            "\nLattice = " + " " + "{{:.2f}}".format(lattice.a()) + " " + "{{:.2f}}".format(lattice.b()) + " " + "{{:.2f}}".format(lattice.c()) + " " +
            "{{:.2f}}".format(lattice.alpha()) + " " + "{{:.2f}}".format(lattice.beta()) + " " + "{{:.2f}}".format(lattice.gamma()) +
            "\nError = " + " " + "{{:.2E}}".format(lattice.errora()) + " " + "{{:.2E}}".format(lattice.errorb()) + " " + "{{:.2E}}".format(lattice.errorc()) + " " +
            "{{:.2E}}".format(lattice.erroralpha()) + " " + "{{:.2E}}".format(lattice.errorbeta()) + " " + "{{:.2E}}".format(lattice.errorgamma()) +
            "\nClick on peak to see peak info." +
            "\nHold mouse button to rotate." +
            "\nClose window to continue." ,
            fontsize = 20, transform = self.axP.transAxes)
        self.axP.set_xlabel('Q$_X$')
        self.axP.set_ylabel('Q$_Y$')
        self.axP.set_zlabel('Q$_Z$')


        formatter = LogFormatter(10, labelOnlyBase = False)
        plt.colorbar(sp,ticks = [1,2,5,10,20,50,100,200,500,1000,2000,5000,10000,20000,50000,100000], format = formatter)
        # Create cubic bounding box to simulate equal aspect ratio
        max_range = max([max(self.x)-min(self.x), max(self.y)-min(self.y), max(self.z)-min(self.z)])
        Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(max(self.x)+min(self.x))
        Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(max(self.y)+min(self.y))
        Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(max(self.z)+min(self.z))
        # Comment or uncomment following both lines to test the fake bounding box:
        for xb, yb, zb in zip(Xb, Yb, Zb):
           self.axP.plot([xb], [yb], [zb], 'w')
        plt.show()
        figP.canvas.mpl_disconnect(cid)

    def plot_lattice(self, latColor):
        predict_peaks_ws = PredictPeaks(InputWorkspace=self.peaks_ws, WavelengthMin=self.minWavelength,
             WavelengthMax=self.maxWavelength, MinDSpacing=self.minDSpacing, 
             OutputWorkspace="predict")
        self.predict_dict = {{}}
        for i in range(predict_peaks_ws.getNumberPeaks()):
            peak = predict_peaks_ws.getPeak(i)
            self.predict_dict.update({{peak.getHKL(): peak.getQSampleFrame()}}) 
        for Hj in range(int(self.minQ),int(self.maxQ)+1):
            for Kj in range(int(self.minQ),int(self.maxQ)+1):
                for Lj in range(int(self.minQ),int(self.maxQ)+1):
                    if V3D(Hj,Kj,Lj) in self.predict_dict:
                        xyz0 = self.predict_dict[V3D(Hj,Kj,Lj)]
                        if V3D(Hj,Kj,Lj+1) in self.predict_dict:
                            qx = []
                            qy = []
                            qz = []
                            qx = np.append(qx, xyz0.getX())
                            qy = np.append(qy, xyz0.getY())
                            qz = np.append(qz, xyz0.getZ())
                            xyz = self.predict_dict[V3D(Hj,Kj,Lj+1)]
                            qx = np.append(qx, xyz.getX())
                            qy = np.append(qy, xyz.getY())
                            qz = np.append(qz, xyz.getZ())
                            self.axP.plot(qx,qy,qz, color=latColor, linewidth=1, alpha=0.2)
                        if V3D(Hj,Kj+1,Lj) in self.predict_dict:
                            qx = []
                            qy = []
                            qz = []
                            qx = np.append(qx, xyz0.getX())
                            qy = np.append(qy, xyz0.getY())
                            qz = np.append(qz, xyz0.getZ())
                            xyz = self.predict_dict[V3D(Hj,Kj+1,Lj)]
                            qx = np.append(qx, xyz.getX())
                            qy = np.append(qy, xyz.getY())
                            qz = np.append(qz, xyz.getZ())
                            self.axP.plot(qx,qy,qz, color=latColor, linewidth=1, alpha=0.2)
                        if V3D(Hj+1,Kj,Lj) in self.predict_dict:
                            qx = []
                            qy = []
                            qz = []
                            qx = np.append(qx, xyz0.getX())
                            qy = np.append(qy, xyz0.getY())
                            qz = np.append(qz, xyz0.getZ())
                            xyz = self.predict_dict[V3D(Hj+1,Kj,Lj)]
                            qx = np.append(qx, xyz.getX())
                            qy = np.append(qy, xyz.getY())
                            qz = np.append(qz, xyz.getZ())
                            self.axP.plot(qx,qy,qz, color=latColor, linewidth=1, alpha=0.2)

    def plot_crystalplan(self, unique, completeness, redundancy, multiple):
            self.x = []
            self.y = []
            self.z = []
            self.c = []
            self.s = []
            plt.rcParams.update({{'font.size': 10}})
            npeaksTotal = self.ws.getNumberPeaks()
            for i in range(npeaksTotal):
                    peak = self.ws.getPeak(i)
                    qsample = peak.getQSampleFrame()
                    intensity = peak.getIntensity()
                    self.c = np.append(self.c,max(self.minIntensity,intensity))
                    self.x = np.append(self.x,qsample.X())
                    self.y = np.append(self.y,qsample.Y())
                    self.z = np.append(self.z,qsample.Z())
                    self.s = np.append(self.s,40)
            figP = plt.figure("CrystalPlan"+str(self.events),figsize = (self.screen_x, self.screen_y))
            self.axP = figP.gca(projection = '3d')
            self.c[self.c<=1] = 1.
            vmin = min(self.c)
            vmax = max(self.c)
            cm = plt.cm.get_cmap('rainbow')
            logNorm = colors.LogNorm(vmin = vmin, vmax = vmax)
            sp = self.axP.scatter(self.x, self.y, self.z, c = self.c, vmin = vmin, vmax = vmax, cmap = cm, norm = logNorm, s = self.s, alpha = 0.2, picker = True)
            self.props = dict(boxstyle = 'round', facecolor = 'wheat', alpha = 1.0)
    
            cid = figP.canvas.mpl_connect('pick_event', self.onpick3)

            try:
                lattice = self.peaks_ws.sample().getOrientedLattice()
            except:
                lattice = OrientedLattice(1,1,1)

            self.axP.text2D(0.05, 0.70, "Peaks = "+str(npeaksTotal)+
                '\nUnique: {{0}}'.format(unique)+
                '\nCompleteness: {{0}}%'.format(round(completeness * 100, 2))+
                '\nRedundancy: {{0}}'.format(round(redundancy, 2))+
                '\nMeasured multiple times: {{0}}%'.format(round(multiple*100, 2))+
                "\nLattice = " + " " + "{{:.2f}}".format(lattice.a()) + " " + "{{:.2f}}".format(lattice.b()) + " " + "{{:.2f}}".format(lattice.c()) + " " +
                "{{:.2f}}".format(lattice.alpha()) + " " + "{{:.2f}}".format(lattice.beta()) + " " + "{{:.2f}}".format(lattice.gamma()) +
                "\nError = " + " " + "{{:.2E}}".format(lattice.errora()) + " " + "{{:.2E}}".format(lattice.errorb()) + " " + "{{:.2E}}".format(lattice.errorc()) + " " +
                "{{:.2E}}".format(lattice.erroralpha()) + " " + "{{:.2E}}".format(lattice.errorbeta()) + " " + "{{:.2E}}".format(lattice.errorgamma()) +
                "\nHold mouse button to rotate." +
                "\nClose window to continue." ,
                fontsize = 20, transform = self.axP.transAxes)
            self.axP.set_xlabel('Q$_X$')
            self.axP.set_ylabel('Q$_Y$')
            self.axP.set_zlabel('Q$_Z$')
    
    
            formatter = LogFormatter(10, labelOnlyBase = False)
            plt.colorbar(sp,ticks = [1,2,5,10,20,50,100,200,500,1000,2000,5000,10000,20000,50000,100000], format = formatter)
            # Create cubic bounding box to simulate equal aspect ratio
            max_range = max([max(self.x)-min(self.x), max(self.y)-min(self.y), max(self.z)-min(self.z)])
            Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(max(self.x)+min(self.x))
            Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(max(self.y)+min(self.y))
            Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(max(self.z)+min(self.z))
            # Comment or uncomment following both lines to test the fake bounding box:
            for xb, yb, zb in zip(Xb, Yb, Zb):
               self.axP.plot([xb], [yb], [zb], 'w')
            plt.show()
            figP.canvas.mpl_disconnect(cid)

    def onpick3(self, event):
        ind = event.ind
        zdirs = None
        xp = np.take(self.x, ind)
        yp = np.take(self.y, ind)
        zp = np.take(self.z, ind)
        cp = np.take(self.c, ind)
        qSample=V3D(xp[0],yp[0],zp[0])
        R=self._wksp.run().getGoniometer().getR()
        qLab = R.dot(qSample)
        peak = self.ws.createPeak(qLab)
        peak.setQSampleFrame(qSample)
        peak.setBinCount(cp[0])
        self.ws.addPeak(peak)
        try:
            IndexPeaks( PeaksWorkspace = self.ws, Tolerance = 1.0, RoundHKLs = False )
        except:
            print ("UB matrix not found")
        self.ws = IntegratePeaksMD( InputWorkspace = self._md, PeakRadius = self.peakRadius,
                          CoordinatesToUse = "Q (sample frame)",
                          BackgroundOuterRadius = self.bkg_outer_radius,
                          BackgroundInnerRadius = self.bkg_inner_radius,
                          PeaksWorkspace = self.ws, OutputWorkspace="events")
        peak = self.ws.getPeak(0)
        if peak.getSigmaIntensity() !=  0.0:
            IsigI = peak.getIntensity()/peak.getSigmaIntensity()
        else:
            IsigI = 0.0
        detID = int(peak.getDetectorID())
        bank = self.instrument.getDetector(detID).getName()
        label = 'Counts:'+'%.3f'%(peak.getBinCount())+ \
             '\nIntegral, I/sigI:'+'%.3f %.3f'%(peak.getIntensity(),IsigI)+ \
            '\nDetector Number:'+bank+ \
            '\nh,k,l:'+'%.3f %.3f %.3f'%(peak.getH(),peak.getK(),peak.getL())+ \
            '\nQ$_X$,Q$_Y$,Q$_Z$:'+'%.3f %.3f %.3f'%(xp[0],yp[0],zp[0])+ \
            '\nQ($\AA^{{-1}}, 2\pi/d$):'+'%.3f'%(2*np.pi/peak.getDSpacing())+ \
            '\nd-Spacing($\AA$):'+'%.3f'%(peak.getDSpacing())+ \
            '\nWavelength($\AA$):'+'%.3f'%(peak.getWavelength())+ \
            '\n2$\\theta$($^\circ$):'+'%.3f'%(peak.getScattering())+ \
            '\nTime($\mu$s):'+'%.3f'%(peak.getTOF())+ \
            '\nE(meV):'+'%.3f'%(peak.getFinalEnergy())
        self.ws.removePeak(0)
        txt = self.axP.text(xp[0],yp[0],zp[0],label,zdirs, bbox = self.props)
        plt.pause(2)
        txt.remove()
    
    def dim2array(self, d,center=True):
        """
        Create a numpy array containing bin centers along the dimension d
        input: d - IMDDimension
        return: numpy array, from min+st/2 to max-st/2 with step st  
        """
        dmin=d.getMinimum()
        dmax=d.getMaximum()
        dstep=d.getX(1)-d.getX(0)
        if center:
            return np.arange(dmin+dstep/2,dmax,dstep)
        else:
            return np.linspace(dmin,dmax,d.getNBins()+1)
    
    def Plot2DMD(self, ax,ws, hkl, NumEvNorm=False,**kwargs):
        """
        Plot a 2D slice from an MDHistoWorkspace (assume all other dimensions are 1)
        input: ax - axis object
        input: ws - handle to the workspace
        input: NumEvNorm - must be set to true if data was converted to MD from a histo workspace (like NXSPE) and no MDNorm... algorithms were used
        input: kwargs - arguments that are passed to plot, such as plotting symbol, color, label, etc.
        """
        dims=ws.getNonIntegratedDimensions()
        if len(dims)!=2:
            raise ValueError("The workspace dimensionality is not 2")
        dimx=dims[0]
        x=self.dim2array(dimx,center=False)
        dimy=dims[1]
        y=self.dim2array(dimy,center=False)
        intensity=ws.getSignalArray()*1.
        if NumEvNorm:
            nev=ws.getNumEventsArray()
            intensity/=nev
        intensity=intensity.squeeze()
        intensity=np.ma.masked_where(np.isnan(intensity),intensity)
        XX,YY=np.meshgrid(x,y,indexing='ij')
        pcm=ax.pcolorfast(XX,YY,intensity,**kwargs)
        ax.set_xlabel(dimx.getName())
        ax.set_ylabel(hkl + "  " + dimy.getName())
        ax.set(aspect=1)
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        return pcm


    def meshgrid2(self, *arrs):
         arrs = tuple(reversed(arrs))
         lens = map(len, arrs)
         dim = len(arrs)
         sz = 1
         for s in lens:
            sz *= s
         ans = []
         for i, arr in enumerate(arrs):
             slc = [1]*dim
             slc[i] = lens[i]
             arr2 = np.asarray(arr).reshape(slc)
             for j, sz in enumerate(lens):
                 if j != i:
                     arr2 = arr2.repeat(sz, axis=j)
             ans.append(arr2)
         return tuple(ans)
 
    def addOrientation(self, x, id):
        ivar = 0
        if self.changePhi:
            AddSampleLog(Workspace=self._wksp, LogName='phi', LogText=str(x[ivar]), LogType='Number')
            ivar += 1
        if self.changeChi:
            AddSampleLog(Workspace=self._wksp, LogName='chi', LogText=str(x[ivar]), LogType='Number')
            ivar += 1
        if self.changeOmega:
            AddSampleLog(Workspace=self._wksp, LogName='omega', LogText=str(x[ivar]), LogType='Number')
            ivar += 1
        SetGoniometer(Workspace=self._wksp,Axis0="omega,0,1,0,1",Axis1="chi,0,0,1,1",Axis2="phi,0,1,0,1")
        peaks = PredictPeaks(InputWorkspace=self._wksp, WavelengthMin=self.minWavelength, 
            EdgePixels=self.edgePixels,
            WavelengthMax=self.maxWavelength, MinDSpacing=self.minDSpacing, OutputWorkspace='result'+str(id)+current_process().name)
        return peaks
        
    def f(self, x): 
        listoflists = zip(*[iter(x)]*self.numAngles)
        if (self.addOrientations):
            peaks = self.peaks_ws
        else:
            peaks = CreatePeaksWorkspace(InstrumentWorkspace=self._wksp, NumberOfPeaks=0, OutputWorkspace='peaks'+current_process().name)
            CopySample(InputWorkspace = self.peaks_ws,OutputWorkspace = peaks,CopyName = '0',CopyMaterial = '0',CopyEnvironment = '0',CopyShape = '0')
        for i in range(len(listoflists)):
            result = self.addOrientation(listoflists[i], i)
            peaks = CombinePeaksWorkspaces(peaks, result, OutputWorkspace='peaks'+current_process().name)
            AnalysisDataService.remove( result.getName() )
        if self.useSymmetry:
            unique, completeness, redundancy, multiple = CountReflections(peaks, PointGroup=self.pointGroup,
                                                              LatticeCentering=self.centering, MinDSpacing=self.minDSpacing,
                                                              MissingReflectionsWorkspace='')
        else:
            unique, completeness, redundancy, multiple = CountReflections(peaks, PointGroup='-1',
                                                              LatticeCentering='P', MinDSpacing=self.minDSpacing,
                                                              MissingReflectionsWorkspace='')
        AnalysisDataService.remove( peaks.getName() )
        return -unique
    
    def fopt(self, x): 
        listoflists = zip(*[iter(x)]*self.numAngles)
        count = []
        complete = []
        if (self.addOrientations):
            self.ws = self.peaks_ws
        else:
            self.ws = CreatePeaksWorkspace(InstrumentWorkspace=self._wksp, NumberOfPeaks=0, OutputWorkspace='peaks'+current_process().name)
            CopySample(InputWorkspace = self.peaks_ws,OutputWorkspace = self.ws,CopyName = '0',CopyMaterial = '0',CopyEnvironment = '0',CopyShape = '0')
        for i in range(len(listoflists)):
            result = self.addOrientation(listoflists[i], i)
            self.ws = CombinePeaksWorkspaces(self.ws, result, OutputWorkspace='peaks'+current_process().name)
            AnalysisDataService.remove( result.getName() )
            if self.useSymmetry:
                unique, completeness, redundancy, multiple = CountReflections(self.ws, PointGroup=self.pointGroup,
                                                                  LatticeCentering=self.centering, MinDSpacing=self.minDSpacing,
                                                                  MissingReflectionsWorkspace='')
            else:
                unique, completeness, redundancy, multiple = CountReflections(self.ws, PointGroup='-1',
                                                                  LatticeCentering='P', MinDSpacing=self.minDSpacing,
                                                                  MissingReflectionsWorkspace='')
            count.append(i+1)
            complete.append(round(completeness * 100, 2))
        self.plot_crystalplan(unique, completeness, redundancy, multiple)
        plt.rcParams.update({{'font.size': 40}})
        plt.figure("Completeness"+str(self.events),figsize = (self.screen_x, self.screen_y))
        plt.plot(count, complete, 'ro')
        plt.ylabel('Orientations')
        plt.ylabel('Completeness (%)')
        plt.show()
    
    
    def func(self, x):
        fx = self.f(x)
        """ Derivative of objective function """
        eps = 10
        dfdx = []
        for i in range(self.numAngles*self.numOrientations):
            x2 = list(x)
            x2[i] = x[i]+eps
            dfdx.append(self.f(x2)-fx)
        dfdx_array = np.array(dfdx)
        return fx, dfdx_array

    
class RandomDisplacementBounds(object):
    """random displacement with bounds"""
    def __init__(self, xmin, xmax, stepsize=30.0):
        self.xmin = xmin
        self.xmax = xmax
        self.stepsize = stepsize

    def __call__(self, x):
        """take a random step but ensure the new position is within the bounds"""
        while True:
            xnew = x + np.random.uniform(-self.stepsize, self.stepsize, np.shape(x))
            if np.all(xnew < self.xmax) and np.all(xnew > self.xmin):
                break
        return xnew



if __name__ == '__main__':  # if we're running file directly and not importing it
    print ("Wait a few minutes for events in reciprocal space")
    test = MantidEV()  # run the main function
    test.time_start = 0
    test.time_stop = test.time_start + test.seconds
    test.last = 0
    while test.last == 0:
        test.select_wksp()
        if test.events > 0:
            test.plot_Q()
            test.find_peaks()
            test.plot_peaks(True)
            test.plot_peaks(False)
            test.plot_Qpeaks()
            if test.numOrientations > 0:
                test.crystalplan()
#    else:
#        print ("No events")
    print ("Plotting finished for current data")


