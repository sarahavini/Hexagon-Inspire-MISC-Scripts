####Imports Section############
import ctypes
###############################

###Reusable functions##########
def force_single_selection():
    while True:
        returnedval = []
        cmd1 = IN_PromptUserForSelection("Any").Run()
        returnedval = cmd1.SelectedItems
        print(returnedval)
        if (len(returnedval) != 1):
            ctypes.windll.user32.MessageBoxExW(None,"Please Select ONE item >:(", "ERROR",0x40000)
            continue
        else:
            return(returnedval[0])
            break

def cross_product(a,b):
    a = a1, a2, a3 
    b = b1, b2, b3
    x = a2*b3 - a3*b2
    y = a3*b1 - a1*b3
    z = a1*b2 - a2*b1
    
    return(x, y,z) 

def find_R_perp_to_line1(MidpointDVLine, DVLine, VIpointLine, VILine):
    #need to find a line thats perpendicular to the line between virtual and direct point AND
    #passes through the midpoint of the vitrual and direct point AND
    #is on a plane that has both lines on it
    # Vector from MidpointDVLine to VIpointLine
    PQ = [VIpointLine[i] - MidpointDVLine[i] for i in range(3)]
    # Dot products
    dot_d1_d2 = sum(DVLine[i] * VILine[i] for i in range(3))
    dot_PQ_d1 = sum(PQ[i] * DVLine[i] for i in range(3))
    #make sure lines arent parallel
    if sum(x*x for x in DVLine) == 0:
        raise ValueError("DVLine cannot be zero")
    #dot it
    if abs(dot_d1_d2) < 1e-12:
        t = 0.0
    else:
        t = -dot_PQ_d1 / dot_d1_d2
    # Point on Virtual Pt Instrument Line where mirror plane will sit
    R = [VIpointLine[i] + t * VILine[i] for i in range(3)]
    #print(R)
    return R


###############################
cmd = IN_SetWorkingFrame("World").Run()


ctypes.windll.user32.MessageBoxExW(None,"Select the virtual point", "User Selection",0x40000)
UserSelectVirtual = force_single_selection()
VPTACT = IN_Point(UserSelectVirtual.GetActualPath())
VPTACT=str(VPTACT.Position)
VPTACTLIST = VPTACT.split(",")

Virtual_Point_X = float(VPTACTLIST[0].strip())
#print(Virtual_Point_X)
Virtual_Point_Y = float(VPTACTLIST[1].strip())
Virtual_Point_Z = float(VPTACTLIST[2].strip())

ctypes.windll.user32.MessageBoxExW(None,"Select the direct point", "User Selection",0x40000)
UserSelectDirect = force_single_selection()
DPTACT = IN_Point(UserSelectDirect.GetActualPath())
DPTACT=str(DPTACT.Position)
DPTACTLIST = DPTACT.split(",")


Direct_Point_X = float(DPTACTLIST[0].strip())
Direct_Point_Y = float(DPTACTLIST[1].strip())
Direct_Point_Z = float(DPTACTLIST[2].strip())

###Step 1 Calculate Line between direct and virtual points
Line_X = Direct_Point_X - Virtual_Point_X
Line_Y = Direct_Point_Y - Virtual_Point_Y
Line_Z = Direct_Point_Z - Virtual_Point_Z

###Step 2 Calculate midpoint between direct and virtual point
Midpoint_X = (Virtual_Point_X + Direct_Point_X) / 2
Midpoint_Y = (Virtual_Point_Y + Direct_Point_Y) / 2
Midpoint_Z = (Virtual_Point_Z + Direct_Point_Z) / 2

###Step 3/4 Get location of instrument base
cmd = IN_GetConnectedInstruments().Run()
instrument = cmd.ConnectedInstruments[0]
#print(cmd.ConnectedInstruments)
instrumenttransform = instrument.Transform
#print(instrumenttransform)
#print(instrument.Path)
INSTTRANSSPLIT = str(instrumenttransform).split(",")
INSTTRANSSPLITX = float((INSTTRANSSPLIT[2].split(" "))[-1])
#print(INSTTRANSSPLITX)
INSTTRANSSPLITY = float((INSTTRANSSPLIT[3].split(" "))[1])
#print(INSTTRANSSPLITY)
INSTTRANSSPLITZ = float((INSTTRANSSPLIT[4].split(" "))[1])
#print(INSTTRANSSPLITZ)

###Step 7 make line from virtual point to instrument base
Line2_X = Virtual_Point_X - INSTTRANSSPLITX
Line2_Y = Virtual_Point_Y - INSTTRANSSPLITY
Line2_Z = Virtual_Point_Z - INSTTRANSSPLITZ

###Step 8 find intersection of perpendicular line from midpoint to line 2
DVLine = [Line_X,Line_Y,Line_Z]
print("DVLINE = ", DVLine)
MidpointDVLine = [Midpoint_X,Midpoint_Y,Midpoint_Z]
print("MidpointDVLine = ", MidpointDVLine)
VILine = [Line2_X,Line2_Y,Line2_Z]
print("VILine =", VILine)
VIpointLine = [INSTTRANSSPLITX,INSTTRANSSPLITY,INSTTRANSSPLITZ]
print("VIpointLine = ", VIpointLine)

ORIGINMIRROR = find_R_perp_to_line1(MidpointDVLine, DVLine, VIpointLine, VILine)
print(ORIGINMIRROR[0])
print(ORIGINMIRROR[1])
print(ORIGINMIRROR[2])

cmd = IN_AddPlaneFeature(None,None,"Mirror Plane",False,False).Run()
feat = cmd.NewFeature.CreateNominal()
feat = cmd.NewFeature.GetNominalPath()
mirrorplane = IN_Plane(feat)
mirrorplane.SetPosition(float(ORIGINMIRROR[0]),float(ORIGINMIRROR[1]),float(ORIGINMIRROR[2]))
mirrorplane.SetNormal(float(Line_X),float(Line_Y),float(Line_Z))







