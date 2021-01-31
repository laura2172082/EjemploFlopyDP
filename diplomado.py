import os
import numpy as np
import matplotlib.pyplot as plt
import flopy
#vamos a empezar hacer el modelo,este modelo tiene unas caracteristicas particulares y estan ahi expuestas al comienzo 
# name es el nombre del modelo 
#h1 y h2 son las cargas hidraulicas en los bordes
#Nlay es el numero de capas,por lo tanto este modelo tiene 10 capas por que Nlay=10
#N es el numero de celdas ,osea son 100 celdas 
#L son las dimensiones del modelo 
#H es la altura del modelo 
#k es la permeabilidad 
name = "ejercicio "
h1 = 100
h2 = 90
Nlay = 10
N = 101
L = 400.0
H = 50.0
k = 1.0
#busca mf6 en la carpeta especificada y guarda los archivos 
sim = flopy.mf6.MFSimulation(sim_name=name, exe_name="mf6", version="mf6", sim_ws="workspace")
 
#crea ibjetos de flopy TDIS,la simulacion  
#nper me estan diciendo que hay un solo periodo de estres (1 solo)
#y la amplitud de ese periodo de estres ,el numero de time steps,y el factor multiplicador perioddata=[(1.0, 1, 1.0)
#todo es uno,por que esto es sencillo 
tdis = flopy.mf6.ModflowTdis(sim, pname="tdis", time_units="DAYS", nper=1, perioddata=[(1.0, 1, 1.0)])

#crea el paquete de objetos flopy IMS 
#por ejemplo en modflow siempre esta todo calculado por paquetes  y en este caso para modflow 6 ,el solucionador es IMS 
#entonces la estructura basica mostrada se sigue asi,dentro del parentesis en :
#(sim simulacion con la que se trabaja,pname el nombre del paquete que es ims,y la complejidad)
ims =flopy.mf6.ModflowIms(sim,pname="ims",complexity="SIMPLE")

#crea el modelo del flujo de agua 
#lo de la linea 38,quiere decir que eso se lleno con el nombre del ejercicio pero termina en .nam 
#gwf modelo de agua subterranea,ahora si lo esta creando 
model_nam_file = "{}.nam".format(name)
gwf = flopy.mf6.ModflowGwf(sim, modelname=name, model_nam_file=model_nam_file)

#se definen valores de espesor de filas y paquete de discretizacion
bot = np.linspace(-H / Nlay, -H, Nlay)
delrow = delcol = L / (N - 1)  #espesor de filas 
dis = flopy.mf6.ModflowGwfdis(    #paquete de discretizacion
    gwf,
    nlay=Nlay,
    nrow=N,
    ncol=N,
    delr=delrow,
    delc=delcol,
    top=0.0,
    botm=bot,
)

#Entregar el valor de partida para el metodo de numerico
start = h1 * np.ones((Nlay, N, N))
ic = flopy.mf6.ModflowGwfic(gwf, pname="ic", strt=start)  #condiciones iniciales 

#paquete que controla el flujo entre celdas,el cual esta condicionado por la permeabilidad
npf = flopy.mf6.ModflowGwfnpf(gwf, icelltype=1, k=k, save_flows=True)

# 
chd_rec = []
chd_rec.append(((0, int(N / 4), int(N / 4)), h2))
for layer in range(0, Nlay):
    for row_col in range(0, N):
        chd_rec.append(((layer, row_col, 0), h1))
        chd_rec.append(((layer, row_col, N - 1), h1))
        if row_col != 0 and row_col != N - 1:
            chd_rec.append(((layer, 0, row_col), h1))
            chd_rec.append(((layer, N - 1, row_col), h1))
chd = flopy.mf6.ModflowGwfchd(
    gwf,
    maxbound=len(chd_rec),
    stress_period_data=chd_rec,
    save_flows=True,
)

#
iper = 0
ra = chd.stress_period_data.get_data(key=iper)
ra

#
# Create the output control (`OC`) Package
headfile = "{}.hds".format(name)
head_filerecord = [headfile]
budgetfile = "{}.cbb".format(name)
budget_filerecord = [budgetfile]
saverecord = [("HEAD", "ALL"), ("BUDGET", "ALL")]
printrecord = [("HEAD", "LAST")]
oc = flopy.mf6.ModflowGwfoc(
    gwf,
    saverecord=saverecord,
    head_filerecord=head_filerecord,
    budget_filerecord=budget_filerecord,
    printrecord=printrecord,
)
#construya los txt 
sim.write_simulation()

#condicion de exito 
success, buff = sim.run_simulation()
if not success:
    raise Exception("MODFLOW 6 did not terminate normally.")
    
#imprimiendo resultados 
headfile=os.path.join("workspace",headfile)
hds = flopy.utils.binaryfile.HeadFile(headfile)
h = hds.get_data(kstpkper=(0, 0))
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[0], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%2.1f")

#plot layer 10
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[-1], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%1.1f")
#en h0 esta laprimera capa y en h1 la ultima 

#ploteando la seccionn transversal
z = np.linspace(-H / Nlay / 2, -H + H / Nlay / 2, Nlay)
fig = plt.figure(figsize=(5, 2.5))
ax = fig.add_subplot(1, 1, 1, aspect="auto")
c = ax.contour(x, z, h[:, 50, :], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%1.1f")




