# EROSION ANALYSIS - BLENDER TOOL
Calculate the amount of erosion of a 3D model from its ideal original geometry.

Calculate the thickness of the separation between each face of a mesh ("original" surface) and a second mesh ("eroded" surface).
The "eroded" object is usually the digital 3D model of a building, generated with photogrammetry or lidar.
The "original" surface is usually an object generated by the user, and represents the expected original surface of the building before being eroded.
The "original" surface must be subdivided into a large number of tiles, small enough to act as the pixels of an image.
In this way, after running the script, the "original" surface can be colored like an image, to represent the erosion distribution.  

Only faces with Z within Zmin-Zmax and with erosion within erosion_max, are processed.
The erosion value is stored as a gray color in a new Color Attribute ("Erosion"), that can be used to colorcode the object surface based on the amount of erosion.
A transparent color is assigned to the faces where an erosion value is not calculated.
Face area, erosion and volume (area * erosion) are exported to a text file (.csv).
The format of the output text file is: face index, x, y, z (coordinates of the face center), cell area, erosion, volume.
The file can be opened in Excel for further analysis, i.e. calculate the total volume of erosion.

Inspired by:
https://blender.stackexchange.com/questions/91626/calculate-surfaces-thickness

Procedure to run the script, after loading it into Blender:
- update the "original_obj" and "eroded_obj" names
- set erosion_max, Zmin and Zmax (only cells within these values will be avaluated)
- set outfile (the output text file name .csv)
- run the script
