import os
import numpy as np
import matplotlib.pyplot as plt
import flopy
ws="workspace"
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
#gwf ground water flow  modelo de agua subterranea,ahora si lo esta creando 
model_nam_file = "{}.nam".format(name)
gwf = flopy.mf6.ModflowGwf(sim, modelname=name, model_nam_file=model_nam_file)

#se definen valores de espesor de filas y paquete de discretizacion espacial 
#bot sign¡nifica botton de fondo 
#delrow  es el espesor de las filas 
#dis es el paquete de discretizacion 
#ahi estamos diciendo cual es el modelo,cuales son las capas 
#en bot tenemos un np ,que es numpy y con un numpy hay un linspace que hace que va desde un valor minimo hasta un maximo en un numero especidicado de pasos 
# el top esta en 0,por eso va de -H hasta el fondo total hasta el numero decapas que tenemos ,filas iguales a columnas osea con cuadradas
bot = np.linspace(-H / Nlay, -H, Nlay)
delrow = delcol = L / (N - 1)  
dis = flopy.mf6.ModflowGwfdis(    
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
#el punto de partida el que se define en start y ic se indica como initial condicions 
#entonces esto trabaja con matrices 
start = h1 * np.ones((Nlay, N, N))
ic = flopy.mf6.ModflowGwfic(gwf, pname="ic", strt=start)  #condiciones iniciales 

#paquete que controla el flujo entre celdas,el cual esta condicionado por la permeabilidad
# npf not property flow 
#entonces en esos parentesis (gwf ya definido antes,icelltype=1 significa que el tipo de celda es para calcular el espesor de la celda ,1 espesor de la celda )
#k si es un valor pero se le podria meter una matriz 
k=np.ones([10,N,N])
k[1,:,:]=5e-1
npf = flopy.mf6.ModflowGwfnpf(gwf, icelltype=1, k=k, save_flows=True, save_specific_discharge =True)

# para poner la condicion de frontera 
#linea 1 esta creando una lista vacia y añade dentro de la lista una tupla con coordenadas:
# donde es capa,fila columna,osea en la capa 0 ,int lo convierte en entero la fila,y columna 12 y el valor despues es h2 el valor de la capa hidraulica 
#entonces chd tiene la coordenada y la carga y con un bucle FOR y un if ,esta recorriendo las celdas de los bordes 
chd_rec = []
chd_rec.append(((0, int(N / 4), int(N / 4)), h2))
chd_rec.append(((1, int(3*N / 4), int(3*N / 4)), h2-5))

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


# Create the output control (`OC`) Package
#me va a decir que imprimir en la salida 
headfile = "{}.hds".format(name)
head_filerecord = [headfile]
budgetfile = "{}.bud".format(name)
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

#condicion de exito  y corre el software 
success, buff = sim.run_simulation()
if not success:
    raise Exception("MODFLOW 6 did not terminate normally.")
    
#imprimiendo resultados 
headfile= 'workspace' +'/'+headfile
budgetfile= 'workspace' +'/'+budgetfile
headfile=os.path.join("workspace",headfile)
hds = flopy.utils.binaryfile.HeadFile(headfile)
h = hds.get_data(kstpkper=(0, 0))
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[0], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%2.1f")

#ya complete el modelo,pero ahora vamos a crear graficas 
#es para plotearotra capa,si se mira es lo mismo que la anterior pero cambia en h0 la primera capa y h-1 la ultima capa 
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[-5], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%1.1f")
#en h0 esta laprimera capa y en h1 la ultima 

#ploteando la seccionn transversal
z = np.linspace(-H / Nlay / 2, -H + H / Nlay / 2, Nlay)
fig = plt.figure(figsize=(5, 2.5))
ax = fig.add_subplot(1, 1, 1, aspect="auto")
c = ax.contour(x, z, h[:, 50, :], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%1.1f")


#grafico de flechasx3
head = flopy.utils.HeadFile('workspace/ejercicio .hds').get_data()
bud = flopy.utils.CellBudgetFile('workspace/ejercicio .bud', precision='double')
spdis = bud.get_data(text='DATA-SPDIS')[0]
fig=plt.figure(figsize=(30,30))
pmv=flopy.plot.PlotMapView(gwf)
pmv.plot_array(head)
pmv.plot_grid(colors='white')
pmv.contour_array(head, levels=[.2, .4, .6, .8], linewidths=3.)
pmv.plot_specific_discharge(spdis, color='red')

