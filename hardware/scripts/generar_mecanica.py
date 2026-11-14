"""Ejecutar con el Python incluido en FreeCAD 1.1. Unidades: mm.
Sobrescribe archivos generados. Los objetos REFERENCIA no son piezas certificadas.
"""
from pathlib import Path
import json
import math
import shutil
import zipfile
import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mecanica"
OUT.mkdir(parents=True,exist_ok=True)
p = json.loads((ROOT/"parametros.json").read_text(encoding="utf-8"))
pcb, tray, box = p["pcb_mm"], p["bandeja_mm"], p["caja_referencia_mm"]
doc = App.newDocument("AnteproyectoNodo")
doc.Label = "SISCOM v0.1 - ANTEPROYECTO, cotas por verificar"

def add(name,label,shape,role,color=None):
    if shape.isNull() or not shape.isValid(): raise ValueError("Geometria invalida: "+name)
    obj=doc.addObject("PartDesign::Feature",name)
    obj.Label=label
    obj.Shape=shape
    obj.addProperty("App::PropertyString","Estado","Anteproyecto").Estado=role
    obj.addProperty("App::PropertyString","Advertencia","Anteproyecto").Advertencia="Cotas provisionales. No certifica IP."
    if obj.ViewObject and color: obj.ViewObject.ShapeColor=color
    return obj

def moved(shape,x,y,z):
    result=shape.copy(); result.translate(App.Vector(x,y,z)); return result

margin=tray["margen"]
length=pcb["largo"]+2*margin
width=pcb["ancho"]+2*margin
base=Part.makeBox(length,width,tray["espesor"])
fix=pcb["margen_fijacion"]
hole_offsets=[(fix,fix),(pcb["largo"]-fix,fix),(fix,pcb["ancho"]-fix),(pcb["largo"]-fix,pcb["ancho"]-fix)]
positions=[(margin+x,margin+y) for x,y in hole_offsets]
for x,y in positions:
    boss=Part.makeCylinder(tray["separador_diametro"]/2,tray["separador_alto"],App.Vector(x,y,tray["espesor"]))
    base=base.fuse(boss)
for x,y in positions:
    bore=Part.makeCylinder(pcb["taladro_fijacion"]/2,20,App.Vector(x,y,-1))
    base=base.cut(bore)
base=base.removeSplitter()
assert base.isValid() and len(base.Solids)==1

# Pieza imprimible independiente, en el origen de impresión.
Part.export([add("BandejaExport","Bandeja propia - ajuste provisional",base,"PROTOTIPO DE AJUSTE",(.7,.7,.72))],str(OUT/"BandejaPCB.step"))
mesh=MeshPart.meshFromShape(Shape=base,LinearDeflection=.12,AngularDeflection=.3,Relative=False)
mesh.write(str(OUT/"BandejaPCB.stl"))
doc.removeObject("BandejaExport")
tray_obj=add("Bandeja","Bandeja propia 88x58 - fijacion a caja pendiente",moved(base,5,5,3),"PROTOTIPO DE AJUSTE",(.7,.7,.72))

# PCB provisional, mismo contorno y patrón de fijación que el archivo KiCad.
board=Part.makeBox(pcb["largo"],pcb["ancho"],pcb["espesor"])
for x,y in hole_offsets:
    board=board.cut(Part.makeCylinder(pcb["taladro_fijacion"]/2,4,App.Vector(x,y,-1)))
board_z=3+tray["espesor"]+tray["separador_alto"]
add("PCB","PCB integradora 80x50 - sin rutear",moved(board,5+margin,5+margin,board_z),"PCB PROVISIONAL",(.10,.45,.28))
module=p["modulo_reserva_mm"]
add("RadioNode","Radio Node REFERENCIA - medir modulo",Part.makeBox(module["largo"],module["ancho"],module["alto"],App.Vector(19,18,board_z+pcb["espesor"])),"REFERENCIA NO MEDIDA",(.12,.30,.40))
batt=p["bateria"]["reserva_mm"]
add("Bateria","Bateria REFERENCIA - capacidad y formato pendientes",Part.makeBox(batt[1],batt[0],batt[2],App.Vector(94,5,3)),"REFERENCIA NO MEDIDA",(.90,.62,.18))

wall=box["pared"]
shell=Part.makeBox(box["largo"],box["ancho"],box["alto"]-4)
shell=shell.cut(Part.makeBox(box["largo"]-2*wall,box["ancho"]-2*wall,box["alto"],App.Vector(wall,wall,wall)))
add("CajaReferencia","Caja principal REFERENCIA 120x80x60 - elegir comercial IP",shell,"REFERENCIA, NO FABRICAR",(.78,.81,.83))
# Tapa desplazada arriba para inspeccionar; no se modela una junta no elegida.
add("TapaReferencia","Tapa REFERENCIA desplazada 25 mm - junta no seleccionada",Part.makeBox(box["largo"],box["ancho"],4,App.Vector(0,0,box["alto"]-4+25)),"REFERENCIA EXPLOTADA",(.82,.84,.86))

# Cabezal separado: cámara de referencia con reservas para ventana y cable.
head=p["cabezal_referencia_mm"]
hx,hy,hz=150,20,18
camera=Part.makeBox(head["largo"],head["ancho"],head["alto"],App.Vector(hx,hy,hz))
camera=camera.cut(Part.makeBox(head["largo"]-4,head["ancho"]-4,head["alto"]-4,App.Vector(hx+2,hy+2,hz+2)))
cx,cy=hx+head["largo"]/2,hy+head["ancho"]/2
camera=camera.cut(Part.makeCylinder(head["ventana_reserva_diametro"]/2,5,App.Vector(cx,cy,hz-1)))
camera=camera.cut(Part.makeCylinder(head["cable_reserva_diametro"]/2,5,App.Vector(hx-1,cy,hz+15),App.Vector(1,0,0)))
add("CapsulaReferencia","Capsula sensor REFERENCIA - sellos y soporte pendientes",camera,"REFERENCIA, NO FABRICAR",(.82,.84,.86))
mem=Part.makeCylinder(head["ventana_reserva_diametro"]/2,.2,App.Vector(cx,cy,hz))
add("MembranaReferencia","Membrana REFERENCIA - elegir IP y permeabilidad",mem,"REFERENCIA SIN PRODUCTO ELEGIDO",(.20,.72,.80))
add("BMEReferencia","Modulo BME280 REFERENCIA - medir y ubicar junto a ventana",Part.makeBox(15,12,1.6,App.Vector(cx-7.5,cy-6,hz+3)),"REFERENCIA NO MEDIDA",(.15,.42,.48))

# Pantalla de radiación conceptual. Anillos intermedios y tapa superior cerrada.
shield=p["protector_mm"]
outer=shield["diametro"]/2
inner=shield["abertura_interior_diametro"]/2
assert inner > math.hypot(head["largo"]/2,head["ancho"]/2)
plates=[]
for i in range(shield["platos"]):
    z=5+i*shield["paso"]
    plate=Part.makeCylinder(outer,shield["espesor"],App.Vector(cx,cy,z))
    if i<shield["platos"]-1:
        opening=12 if i==0 else inner
        plate=plate.cut(Part.makeCylinder(opening,shield["espesor"]+2,App.Vector(cx,cy,z-1)))
    for angle in [0,120,240]:
        a=math.radians(angle)
        plate=plate.cut(Part.makeCylinder(1.7,shield["espesor"]+2,App.Vector(cx+31*math.cos(a),cy+31*math.sin(a),z-1)))
    plates.append(plate)
add("PantallaReferencia","Protector solar REFERENCIA - 6 platos, fijacion pendiente",Part.makeCompound(plates),"CONCEPTO SIN VALIDAR VENTILACION",(.93,.93,.90))

doc.recompute()
for obj in doc.Objects:
    if hasattr(obj,"Shape") and not obj.Shape.isValid(): raise ValueError(obj.Name)
target=OUT/"AnteproyectoNodo.FCStd"
try:
    doc.saveAs(str(target))
except OSError:
    # Algunas instalaciones Windows completan el ZIP pero falla el renombrado
    # nativo. Recuperar solamente el archivo generado dentro de este directorio.
    archives=sorted(OUT.glob(target.name+".*"),key=lambda f:f.stat().st_mtime,reverse=True)
    if not archives: raise
    archive=archives[0]
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or "Document.xml" not in z.namelist(): raise
    shutil.copyfile(archive,target)
    if archive.resolve().parent==OUT.resolve(): archive.unlink()
summary={"estado":"ANTEPROYECTO", "bandeja_solidos":len(base.Solids),"bandeja_valida":base.isValid(),"bandeja_mm":[base.BoundBox.XLength,base.BoundBox.YLength,base.BoundBox.ZLength],"objetos":len(doc.Objects),"geometrias_validas":True,"soporte_capsula_resuelto":False,"gabinete_certificado_seleccionado":False}
(OUT/"geometria_verificada.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary))
