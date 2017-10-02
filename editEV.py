#!/usr/bin/env python
import string
import os

def format_template(name, outfile, **kwargs):
    "This fills in the values for the template called 'name' and writes it to 'outfile'"
    template = open(name).read()
    formatter = string.Formatter()
    data = formatter.format(template, **kwargs)
    f = open(outfile, "w")
    try:
        f.write(data)
    finally:
        f.close()

#Generate livEV.py file 
eventFileName='TOPAZ_15629'
phi =str( -83.4225)
chi =str( 135.0)
omega =str( 53.172)
calFileName='/SNS/TOPAZ/shared/PeakIntegration/calibration/TOPAZ_2016A.DetCal'
minDSpacing =str( 0.5)
minWavelength =str( 0.5)
maxWavelength =str( 3.5)
sampleRadius =str( 0.0656)
linSca =str( 0.670)
linAbs =str( 0.733)
powerL =str( 4.0)
minQ=str(-20)
maxQ=str(20)
numPeaksToFind =str( 200)
abcMin =str( 6)
abcMax =str( 11)
tolerance =str( 0.2)
peakRadius =str( 0.16)
minIntensity =str( 100)
nGrid=str(410)
predictPeaks =str(0)

name = "liveEV.py"
outdir = "/home/vel/MantidEV"
path = os.path.join(outdir, name)
template = "templateLiveEV.py"
templatePath = os.path.join(outdir, template)
kw = {
    "eventFileName": eventFileName,
    "phi": phi,
    "chi": chi,
    "omega": omega,
    "calFileName": calFileName,
    "minDSpacing": minDSpacing,
    "minWavelength": minWavelength,
    "maxWavelength": maxWavelength,
    "sampleRadius": sampleRadius,
    "linSca": linSca,
    "linAbs": linAbs,
    "powerL": powerL,
    "minQ": minQ,
    "maxQ": maxQ,
    "numPeaksToFind": numPeaksToFind,
    "abcMin": abcMin,
    "abcMax": abcMax,
    "tolerance": tolerance,
    "peakRadius": peakRadius,
    "minIntensity": minIntensity,
    "nGrid": nGrid,
    "predictPeaks": predictPeaks
}
format_template(templatePath, path, **kw)

