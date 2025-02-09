# EROSION ANALYSIS - BLENDER TOOL
### Calculate the amount of erosion of a 3D model from its ideal original geometry.

Calculate the thickness of the separation between each face of a mesh ("original" surface) and a second mesh ("eroded" object).  
The "eroded" object is usually the digital 3D model of a building, generated with photogrammetry or lidar.  
The "original" surface is usually an object generated by the user, and represents the expected original surface of the building before being eroded. It must be subdivided into a large number of tiles, small enough to act as the pixels of an image. In this way, after running the analysis, the "original" surface can be colored like an image, to represent the erosion distribution.

Only faces within a specified Erosion Limit and Z range are processed.  
The erosion distribution will be represented over the original surface with colors based on either a Rainbow Scale or a Grey Scale. A transparent color is assigned to the faces where an erosion value cannot be calculated.  
Face area, erosion and volume (area * erosion) are exported to a text file (.csv) with this format:  
**| face index | x | y | z** *(coordinates of the face center)* **| cell area | erosion | volume |**  
The file can be opened in Excel for further analysis, i.e. calculate the total volume of erosion.  

Inspired by: [Calculate Surface Thickness](https://blender.stackexchange.com/questions/91626/calculate-surfaces-thickness)

### Procedure to run the Add-on:
- install the AddOn in Blender: Edit -> Preferences... -> Add-ons -> Install...
- open the Add-on from the side menu (press the "N" key)
- select the two objects representing the eroded object and the theoretical original surface 
- set the Erosion Limit, Z minimum and Zmaximum (only cells within these values will be evaluated)
- set the output file (with extension .csv)
- run the Analysis

### Files:
- **Erosion Analysis - Blender Tool.py** : the AddOn to be installed in Blender
- **Erosion Analysis - Objects.fbx** : the example 3D model to load in Blender in order to test the AddOn
- **README.md** : this help
