def lin_abs_coef(formulaString, zParameter, unitCellVolume, weight):
    import math
    # Get user input
    formulaList = formulaString.split()
    numberOfIsotopes = len(formulaList)     # the number of elements or isotopes in the formula        
    calcRadius = True
    XsecDirectory = "/SNS/software/ISAW/Databases/"
    
    sumScatXs = 0.0
    sumAbsXs = 0.0
    sumAtWt = 0.0
    
    logFileName = 'lin_abs_coef.log'
    logFile = open( logFileName, 'w' )
    logFile.write('Output from lin_abs_coef.py script:\n\n')
    
    logFile.write('Chemical formula: ' + formulaString + '\n')
    logFile.write('Number of formula units in the unit cell (Z): %6.3f\n' % zParameter)
    logFile.write('Unit cell volume (A^3): %8.2f\n' % unitCellVolume)
    
    logFile.write('\nCross sections in units of barns ( 1 barn = 1E-24 cm^2)\n')
    logFile.write('Absorption cross section for 2200 m/s neutrons (wavelength = 1.8 A)\n')
    logFile.write('For further information and references, see ...\ISAW\Databases\NIST_cross-sections.dat\n')
    
    print '\nAtom      ScatXs      AbsXs'	# print headings
    print   '----      ------      -----'
    logFile.write('\nAtom      ScatXs      AbsXs\n')
    logFile.write(  '----      ------      -----\n')
    
    # Except for hydrogen, cross-section values are from the NIST web site:
    # http://www.ncnr.nist.gov/resources/n-lengths/list.html
    # which are from:
    # V. F. Sears, Neutron News, Vol. 3, No. 3, 1992, pp. 29-37.
    # Hydrogen cross-sections are from:
    # Howard, J. A. K.; Johnson, O.; Schultz, A. J.; Stringer, A. M.
    #	J. Appl. Cryst. 1987, 20, 120-122.
            
    filename = XsecDirectory + 'NIST_cross-sections.dat'
    
    # begin loop through each atom in the formula
    for i in range(numberOfIsotopes):
    
        lenAtom = len(formulaList[i])   # length of symbol plus number in formula
        
        # begin test for number of characters in the isotope name or symbol
        for j in range(lenAtom):          
            lenSymbol = lenAtom - j - 1
            if formulaList[i][lenSymbol].isalpha(): break
        lenSymbol = lenSymbol + 1
        
        input = open(filename, 'r')         # this has the effect of rewinding the file
        lineString = input.readline()       # read the first comment line
        while lineString[0] == '#':         # search for the end of the comments block
            lineString = input.readline()
    
        # Begin to search the table for element/isotope match.
        
        lineList = lineString.split()       # this should be the H atom
    
        while formulaList[i][0:lenSymbol] != lineList[0]:
            lineString = input.readline()
            lineList = lineString.split()
    
        scatteringXs = float(lineList[1])   # the total scattering cross section
        absorptionXs = float(lineList[2])   # the true absorption cross section at 1.8 A
        atomicWeight = float(lineList[4])   # atomic weight
        number = float(formulaList[i][lenSymbol:])   # the number of this nuclei in the formula
        
        print '%-5s %10.5f %10.5f' % (lineList[0], scatteringXs, absorptionXs)
        logFile.write('%-5s %10.5f %10.5f\n' % (lineList[0], scatteringXs, absorptionXs))
        
        sumScatXs = sumScatXs + ( number * scatteringXs )
        sumAbsXs = sumAbsXs + ( number * absorptionXs )
        sumAtWt = sumAtWt + ( number * atomicWeight )
        
        input.close()
    # end loop
    
    # Calculate the linear absorption coefficients in units of cm^-1
    muScat = sumScatXs * zParameter / unitCellVolume
    muAbs = sumAbsXs * zParameter / unitCellVolume
    
    # Calculate the density of the crystal in g/cc
    density = (sumAtWt / 0.6022) * zParameter / unitCellVolume
    
    # Print the results.
    print '\n'
    print 'The linear absorption coefficent for total scattering is %6.3f cm^-1' % muScat
    print 'The linear absorption coefficent for true absorption at 1.8 A is %6.3f cm^-1' % muAbs
    print 'The calculated density is %6.3f grams/cm^3' % density
    logFile.write('\n')
    logFile.write('The linear absorption coefficent for total scattering is %6.3f cm^-1\n' % muScat)
    logFile.write('The linear absorption coefficent for true absorption at 1.8 A is %6.3f cm^-1\n' % muAbs)
    logFile.write('\nThe calculated density is %6.3f grams/cm^3\n' % density)
    
    # if calcRadius:
    if weight != 0.0:
        crystalVolume = weight / (density)   # sample volume in mm^3
        print 'For a weight of %6.3f mg, the crystal volume is %6.3f mm^3' % (weight, crystalVolume)
        logFile.write('\nFor a weight of %6.3f mg, the crystal volume is %6.3f mm^3\n' % (weight, crystalVolume))
        crystalRadius = ( crystalVolume / ((4.0/3.0)*math.pi) )**(1.0/3.0)   # radius in mm
        print 'The crystal radius is %6.3f mm, or %6.4f cm' % (crystalRadius, crystalRadius/10.)
        logFile.write('The crystal radius is %6.3f mm, or %6.4f cm\n' % (crystalRadius, crystalRadius/10.))
        # volCalc = (4.0/3.0) * math.pi * crystalRadius**3
        # print 'volCalc = %6.3f' % volCalc
    else:
        crystalRadius = 0.
    
    logFile.close()
    return muScat, muAbs, crystalRadius/10.    
