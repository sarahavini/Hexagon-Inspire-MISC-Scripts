
bestfitobject = IN_Alignment("Alignments/Best Fit to Points Alignment1")

#Get actual children
inputactuals = bestfitobject.ActualInputBucket.Path
t = IN_GetChildren(List[str]([inputactuals])).Run()
print(str(t.ChildrenNamesList))

#make the full path to the children to delete them
for i in t.ChildrenNamesList:
    fullpath = inputactuals + "/" + i
    print(fullpath)
    cmd6 = IN_Delete(List[str]([str(fullpath)])).Run()



