import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import LogFormatter
from mpl_toolkits.mplot3d import proj3d
import numpy as np
from mantid.kernel import ConfigService
from mantid.kernel import V3D
from mantid import config
ConfigService.setConsoleLogLevel(2)
config['Q.convention'] = 'Crystallography'

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
        self.linSca = {linSca}
        self.linAbs = {linAbs}
        self.powerL = {powerL}
        self.minQ = {minQ}
        self.maxQ = {maxQ}
        self.numPeaksToFind = {numPeaksToFind}
        self.abcMin = {abcMin}
        self.abcMax = {abcMax}
        self.tolerance = {tolerance}
        self.peakRadius = {peakRadius}
        self.minIntensity = {minIntensity}
        self.nGrid = {nGrid}
        self.predictPeaks = {predictPeaks}
        self.outputDirectory = "{outputDirectory}"
        self.LorentzCorr = True

    def select_wksp(self):
        try:
            props=input.run().getProperties()
            self._wksp = input
        except:
            self._wksp = Load(Filename=self.eventFileName,OutputWorkspace="events")
            self._wksp = ConvertUnits(InputWorkspace = self._wksp,OutputWorkspace="eventWksp",Target="dSpacing",EMode="Elastic")
        try:
            print "omega,chi,phi=",self._wksp.run().getGoniometer().getEulerAngles('YZY')
        except:
            AddSampleLog(Workspace=self._wksp, LogName='phi', LogText=str(self.phi), LogType='Number')
            AddSampleLog(Workspace=self._wksp, LogName='chi', LogText=str(self.chi), LogType='Number')
            AddSampleLog(Workspace=self._wksp, LogName='omega', LogText=str(self.omega), LogType='Number')
            SetGoniometer(Workspace=self._wksp,Axis0="omega,0,1,0,1",Axis1="chi,0,0,1,1",Axis2="phi,0,1,0,1")
            print self._wksp.run().getGoniometer().getEulerAngles('YZY')
        self._wksp = CropWorkspace(InputWorkspace = self._wksp, XMin = self.minDSpacing,OutputWorkspace="eventWksp")
        self._wksp = ConvertUnits(InputWorkspace = self._wksp,OutputWorkspace="eventWksp",Target="Wavelength",EMode="Elastic")
        self._wksp = CropWorkspace(InputWorkspace = self._wksp, XMin = self.minWavelength, XMax = self.maxWavelength,OutputWorkspace="eventWksp")
        self.events = self._wksp.getNumberEvents()
        if self.calFileName:
            LoadIsawDetCal(InputWorkspace=self._wksp,Filename=str(self.calFileName))  # load cal file
        if self.sampleRadius > 0:
            self._wksp = AnvredCorrection(InputWorkspace = self._wksp,LinearScatteringCoef = self.linSca,LinearAbsorptionCoef = self.linAbs,
                Radius = self.sampleRadius,PowerLambda = self.powerL,OutputWorkspace="events")
            if self.powerL > 1.0:
                self.LorentzCorr = False
        if self._wksp:
            output = ConvertToMD(InputWorkspace = self._wksp, QDimensions = 'Q3D', dEAnalysisMode = 'Elastic',
                 LorentzCorrection = self.LorentzCorr, OutputWorkspace='output',
                 Q3DFrames = 'Q_sample', QConversionScales = 'Q in A^-1',
                 MinValues = str(self.minQ)+','+str(self.minQ)+','+str(self.minQ),
                 MaxValues = str(self.maxQ)+','+str(self.maxQ)+','+str(self.maxQ))
            self._md = output

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
        qp = np.linspace(self.minQ,self.maxQ,self.nGrid)
        g = self.meshgrid2(qp, qp, qp)
        positions = np.vstack(map(np.ravel, g))
        self.x,self.y,self.z = np.split(positions, 3)
        self.x = np.hstack(self.x)
        self.y = np.hstack(self.y)
        self.z = np.hstack(self.z)
        self.c = Box.getSignalArray()
        self.c = self.c.flatten()
        data = zip(self.c,self.x,self.y,self.z)
        data = [i for i in data if i[0] >= self.minIntensity]
        self.c,self.x,self.y,self.z = zip(*data)
        self.x = np.array(self.x)
        self.y = np.array(self.y)
        self.z = np.array(self.z)
        self.c = np.array(self.c)
        self.c[self.c<=1] = 1.
        self.s = np.ones([len(self.c)]) * 20
        fig = plt.figure("ReciprocalSpace"+str(self.events),figsize = (self.screen_x, self.screen_y))
        ax = fig.gca(projection = '3d')
        vmin = min(self.c)
        vmax = max(self.c)
        cm = plt.cm.get_cmap('rainbow')
        logNorm = colors.LogNorm(vmin = vmin, vmax = vmax)
        se = ax.scatter(self.x, self.y, self.z, c = self.c, vmin = vmin, vmax = vmax, cmap = cm, norm = logNorm, s = self.s, alpha = 1.0, picker = True)
        ax.text2D(0.05, 0.90, "# Events = "+str(self.events) +
                "\nHold mouse button to rotate." ,
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

    def plot_peaks(self):
            plt.rcParams.update({{'font.size': 6}})
            self.text = []
            distance_threshold = 0.9 * 6.28 / float(self.abcMax)
            #End Input from GUI
            bkg_inner_radius = self.peakRadius
            bkg_outer_radius = self.peakRadius  * 1.25992105 # A factor of 2 ^ (1/3)
            #Create peaks for all 3D grid point about minIntensity
            self.ws = CreatePeaksWorkspace(InstrumentWorkspace=self._wksp, NumberOfPeaks=0, OutputWorkspace="events")
            CopySample(InputWorkspace = self._md,OutputWorkspace = self.ws,CopyName = True,CopyMaterial = '0',CopyEnvironment = '0',CopyShape = '0')
            R=self._wksp.run().getGoniometer().getR()
        
            for i in range(len(self.x)):
#                try:
                qSample=V3D(self.x[i],self.y[i],self.z[i])
                qLab = R.dot(qSample)
                peak = self.ws.createPeak(qLab)
                peak.setQSampleFrame(qSample)
                peak.setBinCount(self.c[i])
                self.ws.addPeak(peak)
#                except:
#                    print "No peaks created", i, self.x[i], self.y[i], self.z[i]
    
            self.peaks_ws = FindPeaksMD( self._md, MaxPeaks = self.numPeaksToFind, OutputWorkspace="peaks",
                                    PeakDistanceThreshold = distance_threshold )
            self.instrument = self.peaks_ws.getInstrument()
         
            try:
                FindUBUsingFFT( PeaksWorkspace = self.peaks_ws, MinD = self.abcMin, MaxD = self.abcMax, Tolerance = self.tolerance )
                SaveIsawUB(self.peaks_ws, self.outputDirectory+"/Peaks"+str(self.events)+".mat")
                print "UB matrix: ", self.outputDirectory+"/Peaks"+str(self.events)+".mat"
                self.numInd,errInd = IndexPeaks( PeaksWorkspace = self.peaks_ws, Tolerance = self.tolerance, RoundHKLs = False )
                if self.predictPeaks:
                    self.peaks_ws = PredictPeaks(InputWorkspace=self.peaks_ws, WavelengthMin=self.minWavelength, WavelengthMax=self.maxWavelength, MinDSpacing=self.minDSpacing, OutputWorkspace="peaks")
            except:
                self.numInd = 0
                print "UB matrix not found"

            self.peaks_ws = IntegratePeaksMD( InputWorkspace = self._md, PeakRadius = self.peakRadius,
                              CoordinatesToUse = "Q (sample frame)",
                                BackgroundOuterRadius = bkg_outer_radius,
                              BackgroundInnerRadius = bkg_inner_radius,
                                PeaksWorkspace = self.peaks_ws, OutputWorkspace="peaks")
            SaveIsawPeaks(self.peaks_ws, self.outputDirectory+"/Peaks"+str(self.events)+".integrate")
            print "Peaks file: ", self.outputDirectory+"/Peaks"+str(self.events)+".integrate"
    
            self.npeaks = self.peaks_ws.getNumberPeaks()
            self.sumIsigI = 0.0
            self.sumIsigI2 = 0.0
            self.sumIsigI5 = 0.0
            figS, axs = plt.subplots(10, 10, sharex=False, sharey=False, figsize=(self.screen_x, self.screen_y))
            figS.canvas.set_window_title('Peaks'+str(self.events))
            axs = axs.flatten()
            for i in range(self.npeaks):
                j = i%len(axs)
                peak = self.peaks_ws.getPeak(i)
                hkl = str(int(peak.getH()+0.5))+','+str(int(peak.getK()+0.5))+','+str(int(peak.getL()+0.5))
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
                self.s = np.append(self.s,160)
                sl2d = BinMD(InputWorkspace=self._md, AxisAligned=False, BasisVector0='Q_sample_x,Angstrom^-1,1,0,0',
                    BasisVector1='Q_sample_y,Angstrom^-1,0,1,0', BasisVector2='Q_sample_z,Angstrom^-1,0,0,1',
                    OutputExtents=str(qsample.X()-self.peakRadius)+','+str(qsample.X()+self.peakRadius)+','+str(qsample.Y()-0.05)
                    +','+str(qsample.Y()+0.05)+','+str(qsample.Z()-self.peakRadius)+','+str(qsample.Z()+self.peakRadius),
                    OutputBins='100,1,100', Parallel=True)
                #10 subplots per page
                pcm=self.Plot2DMD(axs[j],sl2d, hkl, NumEvNorm=False)
                figS.colorbar(pcm,ax=axs[j])
#                plt.tight_layout(pad = 1.0, w_pad=2.0, h_pad=10.0)
                if j == len(axs)-1 and i < self.npeaks-1:
                    plt.show()
                    figS, axs = plt.subplots(10, 10, sharex=False, sharey=False, figsize=(self.screen_x, self.screen_y))
                    figS.canvas.set_window_title('Peaks'+str(self.events))
                    axs = axs.flatten()
            plt.show()
            self.sumIsigI /=  self.npeaks/100.0
            self.sumIsigI5 /=  self.npeaks/100.0
            self.sumIsigI2 /=  self.npeaks/100.0
    
    def plot_Qpeaks(self):
            plt.rcParams.update({{'font.size': 10}})
            CopySample(InputWorkspace = self.peaks_ws,OutputWorkspace = self.ws,CopyName = '0',CopyMaterial = '0',CopyEnvironment = '0',CopyShape = '0')
            try:
                IndexPeaks( PeaksWorkspace = self.ws, Tolerance = 1.0, RoundHKLs = False )
            except:
                print "UB matrix not found"
            npeaksTotal = self.ws.getNumberPeaks()
            self.ws = CombinePeaksWorkspaces(LHSWorkspace = self.ws, RHSWorkspace = self.peaks_ws, OutputWorkspace='events')
            npeaksTotal = self.ws.getNumberPeaks()
            for i in range(npeaksTotal):
                    peak = self.ws.getPeak(i)
                    if peak.getSigmaIntensity() !=  0.0:
                        IsigI = peak.getIntensity()/peak.getSigmaIntensity()
                    else:
                        IsigI = 0.0
                    detID = int(peak.getDetectorID())
                    bank = self.instrument.getDetector(detID).getName()
                    self.text.append('Counts:'+'%.3f'%(peak.getBinCount())
                        + '\nIntegral, I/sigI:'+'%.3f %.3f'%(peak.getIntensity(),IsigI)
                        +'\nDetector Number:'+bank
                        +'\nh,k,l:'+'%.3f %.3f %.3f'%(peak.getH(),peak.getK(),peak.getL())
                        +'\nQ$_X$,Q$_Y$,Q$_Z$:'+'%.3f %.3f %.3f'%(self.x[i],self.y[i],self.z[i])
                        +'\nQ($\AA^{{-1}}, 2\pi/d$):'+'%.3f'%(2*np.pi/peak.getDSpacing())
                        +'\nd-Spacing($\AA$):'+'%.3f'%(peak.getDSpacing())
                        +'\nWavelength($\AA$):'+'%.3f'%(peak.getWavelength())
                        +'\n2$\\theta$($^\circ$):'+'%.3f'%(peak.getScattering())
                        +'\nTime($\mu$s):'+'%.3f'%(peak.getTOF())
                        +'\nE(meV):'+'%.3f'%(peak.getFinalEnergy()))
            figP = plt.figure("EventsAndPeaks"+str(self.events),figsize = (self.screen_x, self.screen_y))
            self.axP = figP.gca(projection = '3d')
            self.c[self.c<=1] = 1.
            vmin = min(self.c)
            vmax = max(self.c)
            cm = plt.cm.get_cmap('rainbow')
            logNorm = colors.LogNorm(vmin = vmin, vmax = vmax)
            sp = self.axP.scatter(self.x, self.y, self.z, c = self.c, vmin = vmin, vmax = vmax, cmap = cm, norm = logNorm, s = self.s, alpha = 0.2, picker = True)
            self.props = dict(boxstyle = 'round', facecolor = 'wheat', alpha = 1.0)
    
            figP.canvas.mpl_connect('pick_event', self.onpick3)

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
                "\nClick on peak to see peak info." +
                "\nHold mouse button to rotate." ,
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

    def onpick3(self, event):
            ind = event.ind
            zdirs = None
            xp = np.take(self.x, ind)
            yp = np.take(self.y, ind)
            zp = np.take(self.z, ind)
            label = np.take(self.text, ind)
            global txt
            try:
                txt.remove()
            except:
                print "First peak picked"
            txt = self.axP.text(xp[0],yp[0],zp[0],label[0],zdirs, bbox = self.props)
    
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
 


if __name__ == '__main__':  # if we're running file directly and not importing it
    test = MantidEV()  # run the main function
    test.select_wksp()
    test.plot_Q()
    test.plot_peaks()
    test.plot_Qpeaks()
