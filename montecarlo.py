import os						      # Import the Pyhton standard package for use of operating system dependent functionality
import random                                                 # Imports the Python standard package for random number generation
import arcpy                                                  # Imports the ArcGIS's Python site package ArcPy 

class LicenseError(Exception):
    pass
	
# Checking ArcGIS license of Spatial Analyst module
try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        raise LicenseError

    arcpy.env.workspace = os.getcwd()                      # Sets folder with script and map file(s) as workspace
    dem = arcpy.sa.Raster('cley_lidar.asc')                 # Enters ARCGIS name of DEM file (it must in the same folder as this script)
    extent = dem.extent                                     # Sets study area to have the same extent as that of 'dem'
    cellSize = (dem.meanCellHeight + dem.meanCellWidth)/2   # Sets cell size of output raster layers to be the same as that of 'dem'
    random.seed()	                                        # Initializes random number generator
    nsims = 100                                             # Sets number of simulations
    for i in range(nsims):                                  # Initializes for loop from 1 through 100 iterations
        print 'Simulating DEM.Simulation {0}'.format(i+1)
        pre_rand = arcpy.CreateRandomRaster_management(out_path = arcpy.env.workspace,     # Location of the output the raster dataset
                                                       out_name = 'pre_rand',              # Name of output random layer
                                                       distribution = 'UNIFORM 0 1',       # Random probability model (Uniform in the range 0 to 1)
                                                       raster_extent = extent,             # Extent of the random layer
                                                       cellsize = cellSize)                # Cell size of the random layer
        rand = 150.0 - (arcpy.sa.Raster(pre_rand)*300.0)    # Creates random height values based on RMS error signature of the terrain model raster layer 'dem'
        rand.save('rand')                                   # Saves 'rand' raster layer to disk
        print 'rand saved'
	arcpy.Delete_management(pre_rand)                   # Deletes 'pre_rand' raster layer
        dtm = dem + rand                                    # Creates a new terrain model raster layer with random values added to the terrain model raster layer 'dem'
        dtm.save('dtm')                                     # Saves 'dtm' raster layer to disk
        print 'dtm saved'
	inund = arcpy.sa.Con(dtm > 890, 1, 0)               # Reclassifies the randomised terrain model raster layer into above (1) and below (0) sea level
        inund.save('inund')                                 # Saves 'inund' raster layer to disk
        print 'inund saved'
	if i == 0:                                          # If it is the first simulation:
            freq = arcpy.sa.Raster('inund')                 # Obtain a copy of the conditional binary map and name it 'freq'
            freq.save('freq')                               # Save the frequency map to disk
        else:                                               # Else:
            freq_2 = arcpy.sa.Raster('inund') + \
                     arcpy.sa.Raster('freq')                # Add the conditional binary map to the existing frequency map and name it 'freq_2'
            freq_2.save('freq_2')                           # Save the newer frequency map to disk
            arcpy.Delete_management('freq')                 # Delete the older frequency map
            arcpy.CopyRaster_management('freq_2','freq')    # Obtain a copy of the newer frequency map and name it 'freq'
            arcpy.Delete_management(freq_2)      			# Delete the frequency map 'freq_2'
        arcpy.Delete_management(rand)                       # Deletes 'rand' raster layer
        arcpy.Delete_management(dtm)                        # Deletes 'dtm' raster layer
        arcpy.Delete_management(inund)                      # Deletes 'inund' raster layer
	print 'files deleted'
	print 'Done (check workspace folder for output raster layer)'

except LicenseError:
        print "Spatial Analyst license is unavailable" 
except:
    print arcpy.GetMessages(2)
finally:
    arcpy.CheckInExtension("Spatial")
