####Imports Section############
import ctypes
import sys
import math
###############################


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

def get_point_group():
    result = ctypes.windll.user32.MessageBoxExW(None,"Choose Point Group", ":)",0x00000021 | 0x00040000)
    if (result ==2):
        print("Exiting Script")
        return(True)
    cmd1 = IN_PromptUserForSelection().Run()
    print(cmd1.SelectedItems)
    cmd2 = IN_ConvertDataListToStringList(cmd1.SelectedItems).Run()
    cmd3 = IN_GetChildren(cmd2.StringList).Run()
    print(cmd3.ChildrenNamesList)
    return(cmd3.ChildrenNamesList)


###########MAIN###########
cmd1 = IN_CreatePointGroup("Mirror Offset Points",None,None,True,False).Run()
mirptobject = IN_Data(cmd1.NewPointGroup)
pathtomirgroup = str(mirptobject.Path)

mirppos_X,mirppos_Y,mirppos_Z,norm_x,norm_y,norm_z = get_mirror_plane_params()


mirrorgroup = get_point_group()
for i in mirrorgroup:
    print(i)
    apply_mirror_offset(i,mirppos_X,mirppos_Y,mirppos_Z,norm_x,norm_y,norm_z,pathtomirgroup)







