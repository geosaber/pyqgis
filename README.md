# ***QGIS Processing Toolbox Algorithm for Trend Surface Generation***

## **Python Script to Generate a Trend Surface**

Script to generate a trend surface from points

## **How to Install the Script:**
1. ***Save the code*** in a file called `TrendSurfaceAlgorithm.py`

2. **In QGIS:**
   - Go to Processing → Toolbox
   - Click the Scripts button (folder icon)
   - Go to Tools → Add Script from File
   - Select the saved file

3. **Or place it in the scripts folder:**
   - Default folder: `C:\Users\[User]\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\` (Windows)
   - Or `~/.local/share/QGIS/QGIS3/profiles/default/processing/scripts/` (Linux)

## **How to Use:**
1. **Run the script** through the Processing Toolbox
2. **Input Parameters:**
   - Point Layer
   - Z-Value Field
   - Degree polynomial (1=linear, 2=quadratic, etc.)
   - Cell size
   - Extent (optional)
   - Output file

## **Features:**

- ✅ Support for different polynomial degrees
- ✅ Least squares fitting
- ✅ Spatial resolution setting
- ✅ Automatically sets CRS
- ✅ Progress feedback
- ✅ Error handling

The script will create a raster containing the trend surface based on your input points!
