import time
import socket
import os
import json
import re
###########Reusable Functions
def GetFeatureListByKind(kind):

#PossibleType = [IN_Point, IN_Line,IN_Plane, IN_Circle, IN_Slot, IN_Ellipse, IN_Cylinder, IN_Sphere, IN_Cone, IN_Torus, IN_Paraboloid, IN_Frame, IN_LinearDimension, IN_AngularDimension]

 #Capture the Features and place into features
 features = IN_GetTypedObjects("Features")
 features.Run()

 #Initialize the filteredfeatures for a list 
 filteredfeatures = []
 for i in features.Items:
    print(i)

    # get children of the feature. shoudl be at least "Input", "Actual"...
    try:
        if "Smart" in i.Name:
            continue
            
        chidrenlist = IN_GetChildren(List[str]([i.Path]),False,False)
        chidrenlist.Run()
    
    # check if at least one child is a specific kind of geometry
        if any([ item for item in chidrenlist.ChildrenItemList if type(item) is kind]): #Change to IN_Circle for only circle features as exemple
        #add this specific feature in the final result if kind is correct
            filteredfeatures.append(i)
    except:
        continue
    
 #Now we can return all Filter Features
 return (filteredfeatures)

######Main
"""
#Organize old
cmd10 = IN_CreateFolderCommand("Organized",None,True,-1).Run()
cmd = IN_GetTypedObjects("Features").Run()
for i in cmd.Items:
    cmd17 = IN_Move(List[str]([str(i.Path)]),str(cmd10.FolderName),False,-1).Run()
cmd = IN_GetConnectedInstruments().Run()
#cmd12 = IN_Move(List[str]([str(cmd.ConnectedInstruments[0])]),str(cmd10.FolderName),False,8).Run()

#add new tracker and connect
currenttracker = IN_AddInstrument("Laser_Tracker_Simulator", None,True,True).Run()
"""
#start watching for the expected number of tie in points
#when script from hardware button request is done we can raise done flag from a diff button (other client called tprobe or something)
currentlist = []
while len(currentlist)<3:
    currentlist = []
    filteredfeatures = GetFeatureListByKind(IN_Point)
    for i in filteredfeatures:
        path = i.Path
        if ("/") not in path:
            currentlist.append(path)
            #BUG youre appending the same point name over and over
    time.sleep(6)
print(currentlist)

#organize measured data to feed numpy grid in exe
measptdict = {}
for i in currentlist:
    actp = (IN_Feature(i)).GetActualPath()
    pt = IN_Point(actp)
    key = i
    xcoord = pt.Position.x
    ycoord = pt.Position.y
    zcoord = pt.Position.z
    measptdict[key] = (xcoord,ycoord,zcoord)
print(measptdict)

##########LAUNCH SERVER EXE FILE
json_data = json.dumps(measptdict)

exe_path = r"C:\Users\sarahavino\source\repos\Inspire_GridLock\dist\Rename_By_Interpoint_Distance_R8.exe"

print(f"Launching server with {len(measptdict)} measured points...")

# Launch hidden in background
#cmd = f'start /B /MIN "" "{exe_path}" "{json_data}"'
#launch visible
escaped_json = json_data.replace('"', '\\"')   # escape inner double quotes

cmd = f'start "" "{exe_path}" "{escaped_json}"'
os.system(cmd)

print("Waiting for server to start (this may take a few seconds)...")
time.sleep(5)   # Increased wait time

########CONNECT TO SERVER
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connected = False
for attempt in range(8):        # Try up to 8 times
    try:
        client.connect(("localhost", 8054))
        print(f"Successfully connected to server on attempt {attempt+1}")
        connected = True
        break
    except Exception as e:
        print(f"Attempt {attempt+1}/8 failed: {e}")
        time.sleep(1.5)

if not connected:
    print("Could not connect to server after 8 attempts. Clear socket use in task manager")
else:
    print("Sending 'compute' command...")
    client.sendall(b"compute\n")
    
    # Get response
    response = client.recv(8192).decode("utf-8").strip()
    print("Received response from server")
    print(response)
client.close()
lines = [line.strip() for line in response.split('\n') if line.strip()]
parsed_matches = []

for line in lines:
    match = re.match(r'(\S+)\s*->\s*(\S+)\s+\(\s*([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\s*\)', line)
    
    if match:
        measname = match.group(1)
        nomname  = match.group(2)
        x = float(match.group(3))
        y = float(match.group(4))
        z = float(match.group(5))
        
        parsed_matches.append({
            'measname': measname,
            'nomname': nomname,
            'x': x,
            'y': y,
            'z': z,
            'line': line
        })

# Show results and add for best fit later
ptnames = []
bestfitnominals = []
bestfitactuals = []

for m in parsed_matches:
    measname = m['measname']
    print(f"{measname} -> {m['nomname']}  ({m['x']:.4f}, {m['y']:.4f}, {m['z']:.4f})")
    ptnames.append(str(measname))
    measpt = IN_Feature(str(measname))
    cmd = measpt.CreateNominal()
    nom = IN_Point(measpt.GetNominalPath())
    nom.SetPosition(x,y,z)
    bestfitnominals.append(str(nom.Path))
    measact = IN_Point(measpt.GetActualPath())
    bestfitactuals.append(str(measact.Path))
    

print(bestfitnominals)
print(bestfitactuals)

cmd = IN_GetConnectedInstruments()
inst = cmd.ConnectedInstruments

cmd0 = IN_AddRpsAlignment("Instruments/Leica AT960 Laser Tracker-1",True,List[str](ptnames)).Run()
#testing in simulation only
#cmd = IN_AddRpsAlignment("Laser Tracker Simulator-1",True,List[str](ptnames)).Run()


#NOW AUTOMEASURE REST OF NOMINALS SINCE WE ARE ROUGH ALIGNED
aln = str(cmd0.NewAlignment.Name)
cmd = IN_WaitForCalculationsToComplete().Run()
cmd = IN_Delete(List[str]([aln])).Run()
nominallocation = r"C:\\Users\\sarahavino\\source\\repos\\Inspire_GridLock\\Nominals2.txt"
cmd3 = IN_ImportPoints(nominallocation,"Name,X,Y,Z",None,"Points","Space","Point","None","",r"#/\$'<>?*[]&","Inches","Degrees",0,True,None).Run()

reflist = IN_GetChildren(List[str](["Nominals2.txt"])).Run()
reflist = reflist.ChildrenNamesList

print(reflist)

connectedinst = IN_GetConnectedInstruments().Run()
connectedinst = connectedinst.ConnectedInstruments[0]

cmd = IN_AddAutoMeasure(connectedinst.Path,reflist,1).Run()

nameauto = cmd.NewAutoMeasure
cmd = IN_ExecuteAutomeasures(List[str]([nameauto.Name])).Run()

cmd24 = IN_AddBestFitAlignment(connectedinst.Path,True,List[str](["Nominals2.txt"]),List[str](["Automeasure1/Checks/Pass1"])).Run()
BFName = cmd24.NewAlignment.Name

cmd = IN_CreateFolderCommand("ScriptAlignment").Run()
foldername = cmd.FolderName

cmd = IN_Move(List[str](["Nominals2.txt",nameauto.Name,BFName]),foldername,False,0).Run()








