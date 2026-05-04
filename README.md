# Hexagon-Inspire-Python-Scripts

Contains Python scripts for Hexagon Inspire Metrology Software

Delete_alignment_input_buckets_bestfit.py
  This snip will get the inputs of a best fit alignment and delete them if they exist. Working in V2025.1.169.0
  Old method of getting children of alignment is depreciated
  Not backwards compatible

DeletealignmentinputbucketsRPS.py
  This snip will get the inputs of a RPS alignment and delete them if they exist. Working in V2025.1.169.0
  Old method of getting children of alignment is depreciated
  Not backwards compatible

GrabAllCirclesOfSizeX.ipy
  This snip will grab circles that exist in the job within a size range
  Shows how to get features from tree and evaluate the properties
  BUilt in V2023 

GrabFailingCircles.ipy
  This snip will grab circles that exist in the job and evaluate the criteria of each for failing flags

MirrorBounce.py
  This py will let you calculate a mirror face plane inside of inspire using a direct and virtual point. a direct point a taken directly from laser tracker to SMR mirror cube. a virtual point is taken by bouncing the mirror beam through the mirror face, to the SMR, and catching it again with the tracker.

mirrorbouncetest.sai
  This is a native inspire file that wil allow you to test the MirrorBounce.py file if needed to understand its functionality.

Mirror_Point_Group.py
  This will let you choose a plane then choose a point group to mirror across that plane (mirror face)

MirrorBounce_Meas_Profile.py
  This script acts as a measurment profile. It will have guides for measuring mirror points. First it asks for a mirror plane. Then you can hit "ok" to measure a mirror point. Each mirror point is auto mirrored across the plane and put in a result point group in the tree.

Nominals.txt
  This txt file can be used for testing with the "MeasuredNominalPointsSetup.sai" file

MeasuredNominalPointsSetup.sai
  Inspire file that allows testing in simulation of the rename by interpoint distance client server scripts

Rename_By_InterPoint_Distance- R8.py
  This is the server side of the client server connection for an inspire project that allows and operator to live measure three points in a room (known pre set grid of nominal points AKA nominals.txt) then will best fit the instrument into the grid and trigger and auto measure for the rest of the targets. This py script should be packaged into an exe file AND CALLED FROM THE INSPIRE CLIENT SCRIPT. It was left as a .py so you can edit.

Inspire Client - R9.py
  This the client side that runs from inside of inspire and pairs with "Rename_By_InterPoint_Distance-R8.py" above. This should be embedded in the actions tab. There are several places where there are hard coded paths. You can swap from simulation to live instrument by commenting out the lines triggering points and switching there.



  
