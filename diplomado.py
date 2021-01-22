import os
import numpy as np
import matplotlib.pyplot as plt
import flopy

name = "ejercicio "
h1 = 100
h2 = 90
Nlay = 10
N = 101
L = 400.0
H = 50.0
k = 1.0
#busca mf6 en la carpeta especificada y guarda los archivos 
sim = flopy.mf6.MFSimulation(sim_name=name, exe_name="C:\Users\lauri\Downloads\mf6.2.0\bin", version="mf6", sim_ws="workspace")
 
#crea ibjetos de flopy TDIS
tdis = flopy.mf6.ModflowTdis(
    sim, pname="tdis", time_units="DAYS", nper=1, perioddata=[(1.0, 1, 1.0)]

#crea el paquete de objetos flopy tms 
ims = flopy.mf6.ModflowIms(sim, pname="ims", complexity="SIMPLE")

#crea el modelo del flujo de agua 
model_nam_file = "{}.nam".format(name)
gwf = flopy.mf6.ModflowGwf(sim, modelname=name, model_nam_file=model_nam_file)

