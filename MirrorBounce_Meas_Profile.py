####Imports Section############
import ctypes
import sys
import math
###############################

###Reusable functions##########
def check_inst_Connection():
    while True:
        cmd  = IN_GetConnectedInstruments().Run()
        if not cmd.ConnectedInstruments:
            result = ctypes.windll.user32.MessageBoxExW(None,"Connect the instrument", "ERROR 001",0x00000021 | 0x00040000)
            if (result ==2):
                print("Exiting Script")
                sys.exit(0)
        else:
            return(True, cmd.ConnectedInstruments[0])
            break

def check_tracker_meas_status(trackername):
    while True:
        trackertocheck = IN_Instrument(trackername.Path)
        if not trackertocheck.ReadyToMeasure:
            result = ctypes.windll.user32.MessageBoxExW(None,"Instrument Not Ready To Measure", "ERROR 002",0x00000021 | 0x00040000)
            if (result ==2):
                print("Exiting Script")
                sys.exit(0)
        else:
            return(True)
            break

def force_profile_switches(trackername):
    tracker = IN_Instrument(trackername.Path)
    listacquisitionprofiles = tracker.GetInstrumentProfiles()
    print(listacquisitionprofiles)
    profiletofind = "Single Point"
    if profiletofind in listacquisitionprofiles:
        tracker.SetAcquisitionProfile("Single Point")
    else:
        result = ctypes.windll.user32.MessageBoxExW(None,"No Single Point Profile", "ERROR 003",0x00000021 | 0x00040000)
        if (result ==2):
            print("Exiting Script")
            sys.exit(0)

def measure_mirror_point(trackername):
    trackername = IN_Instrument(trackername.Path)
    result = ctypes.windll.user32.MessageBoxExW(None,"Click OK To Measure A Mirror Point", ":)",0x00000021 | 0x00040000)
    if (result ==2):
        print("Exiting Script")
        return(True)
        
    trackername.TakeMeasurement()
    return(False)

def retrieve_last_meas_point(parent):
    cmd1 = IN_GetChildren(List[str]([parent]),False,False).Run()
    lis = cmd1.ChildrenNamesList
    index = len(lis)-1
    lastpoint = lis[index]
    return(lastpoint)

def get_mirror_plane_params():
    result = ctypes.windll.user32.MessageBoxExW(None,"Choose Mirror Plane", ":)",0x00000021 | 0x00040000)
    if (result ==2):
        return(True)
        print("Exiting Script")
    else:
        cmd1 = IN_PromptUserForSelection("Features").Run()
        #should probably make sure they actually choose a plane here 
        mirp = IN_Plane((cmd1.SelectedItems[0]).GetNominalPath())
        #print(mirp)
        mirpnorm = str(mirp.Normal)
        #print(mirpnorm)
        mirpnorm = mirpnorm.split(",")
        mirpnorm_X = float(mirpnorm[0].strip())
        mirpnorm_Y = float(mirpnorm[1].strip())
        mirpnorm_Z = float(mirpnorm[2].strip())
        mirppos = str(mirp.Position)
        #print(mirppos)
        mirppos = mirppos.split(",")
        mirppos_X = float(mirppos[0].strip())
        mirppos_Y = float(mirppos[1].strip())
        mirppos_Z = float(mirppos[2].strip())
        #print(mirpnorm_X,mirpnorm_Y,mirpnorm_Z)
        #print(mirppos_X,mirppos_Y,mirppos_Z)

        #normalize plane normal vector components
        norm_magnitude = math.sqrt((mirpnorm_X**2)+(mirpnorm_Y**2)+(mirpnorm_Z**2))
        norm_x = mirpnorm_X/norm_magnitude
        norm_y = mirpnorm_Y/norm_magnitude
        norm_z = mirpnorm_Z/norm_magnitude
        return(mirppos_X,mirppos_Y,mirppos_Z,norm_x,norm_y,norm_z)

def apply_mirror_offset(lastpoint,mirppos_X,mirppos_Y,mirppos_Z,norm_x,norm_y,norm_z,parentnewpt):
    measpt = IN_Point(lastpoint)
    measpttrans = str(measpt.Position)
    measpt = measpttrans.split(",")
    measpt_X = float(measpt[0].strip())
    measpt_Y = float(measpt[1].strip())
    measpt_Z = float(measpt[2].strip())
    
    #vector pt to mirror plane origin 
    dx = measpt_X - mirppos_X
    dy = measpt_Y - mirppos_Y
    dz = measpt_Z - mirppos_Z
    #signed dist
    dist = dx * norm_x + dy * norm_y + dz * norm_z
    #final point pos
    fx = measpt_X - 2 * dist * norm_x
    fy = measpt_Y - 2 * dist * norm_y
    fz = measpt_Z - 2 * dist * norm_z
    print(fx,fy,fz)
    
    AddPoint = IN_AddPointFeature(None,None,str(lastpoint),False,False).Run()
    AddPoint.NewFeature.CreateNominal()
    Nominal = IN_Point(AddPoint.NewFeature.GetNominalPath())
    nomn = str(lastpoint).split("/")
    Nominal.Name = nomn[1]
    refname = "Original Points-"+str(nomn[1])+"/"+str(nomn[1])
    print(refname)
    Nominal.SetPosition(fx,fy,fz)
    t = IN_MakeOffsetCopies(refname,1,0,parentnewpt,False,None).Run()
    locationoffset = parentnewpt + "/" + nomn[1] + " 1"
    mirrorname = nomn[1]
    rename = IN_Rename(locationoffset,mirrorname).Run()
    IN_Delete(List[str]([AddPoint.NewFeature.Path])).Run()


###########MAIN###########

tracker_connected_bool, tracker_name_connected = check_inst_Connection()
tracker_meas_status_check_result = check_tracker_meas_status(tracker_name_connected)
profile_status = force_profile_switches(tracker_name_connected)

#did this in case someone measured multiple mirror locations in same job
cmd1 = IN_CreatePointGroup("Mirror Offset Points",None,None,True,False).Run()
mirptobject = IN_Data(cmd1.NewPointGroup)
pathtomirgroup = str(mirptobject.Path)

cmd1 = IN_CreatePointGroup("Original Points",None,None,True,True).Run()
origptobject = IN_Data(cmd1.NewPointGroup)
pathtomeasuredgroup = str(origptobject.Path)

cmd1 = IN_SetActiveAction(str(origptobject),0,True).Run()

mirppos_X,mirppos_Y,mirppos_Z,norm_x,norm_y,norm_z = get_mirror_plane_params()

Exitflag = False
while True:
    Exitflag = measure_mirror_point(tracker_name_connected)
    if (Exitflag == True):
        break
    lastpoint = retrieve_last_meas_point(pathtomeasuredgroup)
    apply_mirror_offset(lastpoint,mirppos_X,mirppos_Y,mirppos_Z,norm_x,norm_y,norm_z,pathtomirgroup)




