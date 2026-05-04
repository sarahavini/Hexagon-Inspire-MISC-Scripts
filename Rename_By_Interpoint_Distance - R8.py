####Imports Section############
import ctypes
import sys
import math
import numpy as np
from itertools import permutations
import socket
import os
import json
###############################

######Server Setup######
# update with the desired server IP and port
server_port = 8054
# expected max size of data for the socket
socket_buf_size = 4096

#GLOBALS
#if someone else is looking at this i know i shouldnt use these leave me alone >:( 
global server 
global client_socket 
global closedclient 

def temp_opener(name, flag, mode=0o777):
    return os.open(name, flag | os.O_TEMPORARY, mode)

def run_server():
    global server, client_socket, closedclient
    closedclient = False
    # create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, socket_buf_size)
    # bind the socket to a specific port
    server.bind(("", server_port))
    # listen for incoming connections
    server.listen(0)
    print(f"Listening on :{server_port}")
    client_socket, client_address = server.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

def send_to_client(message):
    global client_socket
    try:
        sms = "\n".join(message) + "\n"
        client_socket.sendall(sms.encode("utf-8"))
    except:
        print("Couldn't send message ¯_(ツ)_/¯")


###Reusable math functions##########
def load_point_grid(gridlocation):
    #TEXT FILE NEEDS TO BE FORMATTED NAME X Y Z SPACE DELIMETER
    points = np.loadtxt(gridlocation, delimiter=" ", dtype=str)
    #names of pts are zero column
    names = points[:, 0].astype('<U20')
    #xyz of pts are cols 1-4
    xyz = np.char.strip(points[:, 1:4])
    xyz = xyz.astype(float)   
    dtype = [('name', '<U20'), ('x', 'f8'), ('y', 'f8'), ('z', 'f8')]

    grid = np.empty(len(names), dtype=dtype)
    grid['name'] = names
    grid['x'] = xyz[:, 0]
    grid['y'] = xyz[:, 1]
    grid['z'] = xyz[:,2]
    return(grid)

def load_client_dictionary(measpointdict):
    names = list(measpointdict.keys())
    xyz = np.array(list(measpointdict.values()))
    
    dtype = [('name', '<U20'), ('x', 'f8'), ('y', 'f8'), ('z', 'f8')]
    grid = np.empty(len(names), dtype=dtype)

    grid['name'] = names
    grid['x'] = xyz[:, 0]
    grid['y'] = xyz[:, 1]
    grid['z'] = xyz[:, 2]

    return grid

def get_xyz_coords(fullgrid):
    #Get numpy arrays for each axis xyz
    x = fullgrid['x']
    y = fullgrid['y']
    z = fullgrid['z']
    #stacks the xyz axis into a "point cloud" that will let us calc a centroid later
    xyzcloud = np.column_stack((x,y,z))
    return(xyzcloud)

def kabsch(P, Q):
    # Centroids
    cP = np.mean(P, axis=0)
    cQ = np.mean(Q, axis=0)
    P_c = P - cP
    Q_c = Q - cQ
    # Covariance
    H = P_c.T @ Q_c
    # SVD
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    # Fix reflection if needed
    if np.linalg.det(R) < 0:
        Vt[1, :] *= -1
        R = Vt.T @ U.T
    t = cQ - R @ cP
    # Apply
    P_aligned = (R @ P.T).T + t
    rms = np.sqrt(np.mean(np.sum((P_aligned - Q)**2, axis=1)))
    # Extract rotation angle (in radians, positive = counterclockwise)
    angle = np.arctan2(R[1,0], R[0,0])
    return R, t, rms, angle, P_aligned


def rename_interpt_dist(nominal_grid, measured_grid, max_rms_mm=.5):
    xyz_nom = get_xyz_coords(nominal_grid)
    names_nom = nominal_grid['name']
    xyz_meas = get_xyz_coords(measured_grid)
    n_meas = len(xyz_meas)
    if n_meas < 3:
        raise ValueError("Need at least 3 points")

    best_rms = float('inf')
    best_perm = None
    best_R = None
    best_t = None
    best_angle = None
    
    for perm in permutations(range(n_meas)):
        nom_subset = xyz_nom[list(perm)]      
        
        R, t, rms, angle, _ = kabsch(nom_subset, xyz_meas)
        
        if rms < best_rms:
            best_rms = rms
            best_perm = perm
            best_R = R
            best_t = t
            best_angle = angle
    
    if best_rms > max_rms_mm:
        print("Match quality is pretty whack.... make the max rms arg larger or fix your monuments")
    else:
        print("Good match")
    
    # Assign nominal names
    renamed = measured_grid.copy()
    renamed['name'] = names_nom[list(best_perm)]
    
    return renamed, best_R, best_t, best_angle, best_rms

###########MAIN###########
run_server()

measptdict = {}

if len(sys.argv) > 1:
    raw = sys.argv[1]
    print(f"Raw argument length: {len(raw)}")
    
    for attempt in ["direct", "cleaned", "doubleclean"]:
        try:
            if attempt == "direct":
                measptdict = json.loads(raw)
            elif attempt == "cleaned":
                cleaned = raw.strip('"').replace('\\"', '"')
                measptdict = json.loads(cleaned)
            else:
                cleaned = raw.replace('""', '"').strip('"')
                measptdict = json.loads(cleaned)
                
            print(f"✅ SUCCESS on attempt '{attempt}' — Loaded {len(measptdict)} points")
            print(measptdict)
            break
        except Exception as e:
            print(f"Attempt '{attempt}' failed: {e}")
            continue
else:
    print("No argument received - running in manual mode")

while True:
    if closedclient == True:
        # accept incoming connections
        client_socket, client_address = server.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        closedclient = False
    try:
        request = client_socket.recv(socket_buf_size)
        request = request.decode("utf-8").strip().lower() # convert bytes to string
        print(f"Request from client {request}")
    except:
        print("client isn't connected")
        closedclient = True
        continue

    if not request:
        continue

    # if we receive "close" from the client, then we break
    # out of the loop and close the connection
    if request == "close":
        print("closereq")
        # send response to the client which acknowledges that the
        # connection should be closed and break out of the loop
        # close connection socket with the client
        client_socket.close()
        closedclient = True
        print("Connection to client closed")
        continue

    if request == "stop":
        print("Request to stop server from client")
        if closedclient == False:
            client_socket.close()
            closedclient = True
        break


    if request in ["compute"]:
        try:
            print("=== START COMPUTE ===")
            print("Received measptdict keys:", list(measptdict.keys()) if 'measptdict' in locals() else "NOT DEFINED")
            
            nominal_grid = load_point_grid(r"C:\\Users\\sarahavino\\source\\repos\\Inspire_GridLock\\Nominals2.txt")
            print("✓ Nominal grid loaded successfully")
            print("Nominal names:", nominal_grid['name'])

            measured_grid = load_client_dictionary(measptdict)
            print("✓ Measured grid loaded successfully")
            print("Measured names:", measured_grid['name'])

            renamed_grid, R, t, angle, rms = rename_interpt_dist(nominal_grid, measured_grid)
            print("✓ rename_interpt_dist completed, RMS =", rms)


            results_list_message = []
            print("Result RMS = " + str(rms))
            print("Proposed name changes")
            for i in range(len(measured_grid)):
                measname = measured_grid['name'][i]
                nomname = nominal_grid['name'][i]
                nomx = nominal_grid['x'][i]
                nomy = nominal_grid['y'][i]
                nomz = nominal_grid['z'][i]
                print(str(measname) + " -> " + str(nomname))
                results_list_message.append(f"{measname} -> {nomname}    ({nomx:.4f}, {nomy:.4f}, {nomz:.4f})")

            send_to_client(results_list_message)

        except Exception as e:
            import traceback
            print("!!! EXCEPTION OCCURRED !!!")
            print(traceback.format_exc())
            send_to_client(f"Broken :( \n{type(e).__name__}: {str(e)}")