"""Regenera el anteproyecto KiCad. Ejecutar con el Python incluido en KiCad 10.
Sobrescribe los archivos generados: guardar antes cualquier edición manual.
"""
from pathlib import Path
import csv
import json
import uuid
import pcbnew as k

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pcb"
OUT.mkdir(parents=True, exist_ok=True)
PARAM = json.loads((ROOT / "parametros.json").read_text(encoding="utf-8"))
NAME = "NodoIntegrador"

def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "siscom-hardware-v01/" + key))

def q(value):
    return json.dumps(str(value), ensure_ascii=False)

def grid(value):
    return round(round(float(value)/1.27)*1.27,4)

def effects(size=1.0, hide=False, left=False):
    return f'(effects (font (size {size} {size})){" (justify left)" if left else ""}{" hide" if hide else ""})'

HEADER = "Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical"
RFP = "Resistor_SMD:R_0805_2012Metric"
CFP = "Capacitor_SMD:C_0805_2012Metric"
MFP = "MountingHole:MountingHole_3.2mm_M3"

components = [
    dict(ref="J1", kind="BAT_IN", value="BATERIA 1S PROTEGIDA", pins=["BAT_PROT", "GND"], sch=[50,45], pcb=[110,134], footprint=HEADER.format(n=2)),
    dict(ref="J2", kind="BAT_OUT", value="A BAT DEL RADIO NODE", pins=["VBAT_SW", "GND"], sch=[100,45], pcb=[134,134], footprint=HEADER.format(n=2)),
    dict(ref="J3", kind="NODE_BUS", value="BUS RADIO NODE / ARNES", pins=["3V3", "GND", "SDA", "SCL", "VBAT_ADC"], sch=[100,80], pcb=[155,110], footprint=HEADER.format(n=5)),
    dict(ref="J4", kind="SENSOR_BUS", value="BME280 / CABEZAL", pins=["3V3", "GND", "SDA", "SCL"], sch=[100,117], pcb=[169,128], footprint=HEADER.format(n=4)),
    dict(ref="J5", kind="SWITCH", value="INTERRUPTOR INTERNO", pins=["BAT_PROT", "VBAT_SW"], sch=[50,72], pcb=[122,134], footprint=HEADER.format(n=2)),
    dict(ref="R1", kind="R", value="150k 1%", pins=["VBAT_SW", "VBAT_ADC"], sch=[170,60], pcb=[148,133], footprint=RFP),
    dict(ref="R2", kind="R", value="150k 1%", pins=["VBAT_ADC", "GND"], sch=[170,80], pcb=[148,139], footprint=RFP),
    dict(ref="C1", kind="C", value="100nF", pins=["VBAT_ADC", "GND"], sch=[195,80], pcb=[155,139], footprint=CFP),
    dict(ref="C2", kind="C", value="100nF", pins=["3V3", "GND"], sch=[195,120], pcb=[163,139], footprint=CFP),
    dict(ref="R3", kind="R", value="4k7 DNP", pins=["3V3", "SDA"], sch=[240,60], pcb=[162,123], footprint=RFP, dnp=True),
    dict(ref="R4", kind="R", value="4k7 DNP", pins=["3V3", "SCL"], sch=[265,60], pcb=[162,128], footprint=RFP, dnp=True),
]
pcb = PARAM["pcb_mm"]
fix=pcb["margen_fijacion"]
hole_offsets=[(fix,fix),(pcb["largo"]-fix,fix),(fix,pcb["ancho"]-fix),(pcb["largo"]-fix,pcb["ancho"]-fix)]
hole_positions = [(100+dx,100+dy) for dx,dy in hole_offsets]
for i,position in enumerate(hole_positions,1):
    components.append(dict(ref=f"H{i}", kind="MountingHole", value="M3 3.2mm", pins=[], sch=[155+(i-1)*25,145], pcb=position, footprint=MFP))

def library_symbol(kind, embedded=True):
    full = f"Anteproyecto:{kind}" if embedded else kind
    data = next((c for c in components if c["kind"] == kind), None)
    is_conn = kind not in ["R", "C", "MountingHole"]
    prefix = "J" if is_conn else ("H" if kind == "MountingHole" else kind)
    s = [f'(symbol {q(full)} (pin_names (offset 0.5)) (in_bom {"no" if kind == "MountingHole" else "yes"}) (on_board yes)',
         f'(property "Reference" {q(prefix)} (at 0 3.81 0) {effects()})',
         f'(property "Value" {q(kind)} (at 0 -3.81 0) {effects()})',
         f'(property "Footprint" "" (at 0 0 0) {effects(hide=True)})',
         f'(property "Datasheet" "" (at 0 0 0) {effects(hide=True)})',
         f'(symbol {q(kind+"_0_1")}']
    if is_conn:
        bottom = -(len(data["pins"])-1)*2.54 - 2.0
        s.append(f'(rectangle (start -2.54 2) (end 5.08 {bottom}) (stroke (width 0.254) (type default)) (fill (type background)))')
    elif kind == "R":
        s.append('(rectangle (start -1.016 2.54) (end 1.016 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))')
    elif kind == "C":
        for y in [-0.762,0.762]:
            s.append(f'(polyline (pts (xy -2.032 {y}) (xy 2.032 {y})) (stroke (width 0.254) (type default)) (fill (type none)))')
    else:
        s.append('(circle (center 0 0) (radius 1.5) (stroke (width 0.254) (type default)) (fill (type none)))')
    s.extend([')', f'(symbol {q(kind+"_1_1")}'])
    if is_conn:
        for i,net in enumerate(data["pins"]):
            s.append(f'(pin passive line (at -5.08 {-i*2.54:g} 0) (length 2.54) (name {q(net)} {effects(0.85)}) (number {q(i+1)} {effects(0.85)}))')
    elif kind in ["R", "C"]:
        pin_length = 2.54 if kind == "R" else 4.318
        for num,y,rot in [(1,5.08,270),(2,-5.08,90)]:
            s.append(f'(pin passive line (at 0 {y} {rot}) (length {pin_length}) (name "~" {effects()}) (number {q(num)} {effects()}))')
    s.extend([')', ')'])
    return "\n".join(s)

kinds = list(dict.fromkeys(c["kind"] for c in components))
lib = '(kicad_symbol_lib (version 20241209) (generator "siscom_anteproyecto")\n' + "\n".join(library_symbol(t,False) for t in kinds) + '\n)\n'
(OUT / "Anteproyecto.kicad_sym").write_text(lib, encoding="utf-8")
(OUT / "sym-lib-table").write_text('(sym_lib_table (lib (name "Anteproyecto") (type "KiCad") (uri "${KIPRJMOD}/Anteproyecto.kicad_sym") (options "") (descr "Simbolos locales del anteproyecto")))\n', encoding="utf-8")

root_uuid = uid("sheet")
s = [f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root_uuid}) (paper "A4")',
     '(title_block (title "Nodo remoto - PCB integradora") (date "2026-10-25") (rev "0.1") (comment 1 "ANTEPROYECTO - NO FABRICAR"))',
     '(lib_symbols', *[library_symbol(t) for t in kinds], ')']

def text(t,x,y,size=1.27):
    s.append(f'(text {q(t)} (at {x} {y} 0) {effects(size,left=True)} (uuid {uid("text/"+t)}))')

def wire(x1,y1,x2,y2):
    s.append(f'(wire (pts (xy {grid(x1):g} {grid(y1):g}) (xy {grid(x2):g} {grid(y2):g})) (stroke (width 0) (type default)) (uuid {uid(f"wire/{x1}/{y1}/{x2}/{y2}")}))')

def label(t,x,y):
    s.append(f'(label {q(t)} (at {grid(x):g} {grid(y):g} 0) {effects(1.0,left=True)} (uuid {uid(f"label/{t}/{x}/{y}")}))')

text("ANTEPROYECTO v0.1 | PCB integradora + cabezal BME280 separado",15,15,1.8)
text("NO FABRICAR: medir modulos y elegir conectores, bateria y gabinete antes del ruteo.",15,23)
for c in components:
    x,y = c["sch"]
    reference_y = y-8 if c["kind"] not in ["R","C"] else y-1
    value_y = y-5 if c["kind"] not in ["R","C"] else y+1.5
    tx = x if c["kind"] not in ["R","C"] else x+3
    s.append(f'(symbol (lib_id {q("Anteproyecto:"+c["kind"])}) (at {grid(x)} {grid(y)} 0) (unit 1) (in_bom {"no" if c["kind"] == "MountingHole" else "yes"}) (on_board yes) (dnp {"yes" if c.get("dnp") else "no"}) (uuid {uid(c["ref"])})')
    for prop,value,px,py,hidden in [("Reference",c["ref"],tx,reference_y,False),("Value",c["value"],tx,value_y,False),("Footprint",c["footprint"],x,y,True),("Datasheet","",x,y,True)]:
        s.append(f'(property {q(prop)} {q(value)} (at {px} {py} 0) {effects(1.0,hidden,True)})')
    for i in range(len(c["pins"])):
        s.append(f'(pin {q(i+1)} (uuid {uid(c["ref"]+"/pin/"+str(i+1))}))')
    s.append(f'(instances (project "{NAME}" (path "/{root_uuid}" (reference {q(c["ref"])}) (unit 1)))) )')
    if c["kind"] not in ["R", "C", "MountingHole"]:
        for i,net in enumerate(c["pins"]):
            py = y+i*2.54
            wire(x-15.24,py,x-5.08,py)
            label(net,x-15.24,py)

# Divisor vertical y capacitor del ADC.
wire(170,45,170,54.92); label("VBAT_SW",170,45)
wire(170,65.08,170,70); wire(170,70,170,74.92)
wire(170,70,195,70); wire(195,70,195,74.92); label("VBAT_ADC",170,70)
s.append(f'(junction (at {grid(170)} {grid(70)}) (diameter 0) (color 0 0 0 0) (uuid {uid("junction/adc")}))')
wire(170,85.08,170,90); label("GND",170,90)
wire(195,85.08,195,90); label("GND",195,90)
wire(195,105,195,114.92); label("3V3",195,105)
wire(195,125.08,195,130); label("GND",195,130)
for x,net in [(240,"SDA"),(265,"SCL")]:
    wire(x,45,x,54.92); label("3V3",x,45)
    wire(x,65.08,x,75); label(net,x,75)
text("Divisor: 150k + 150k / C1 100nF",150,38)
text("R3/R4 DNP: revisar pull-ups existentes",225,87,1.0)
text("J3 toma 3V3 del nodo. Nunca conectar VBAT a 3V3.",15,145)
text("J2: arnes a entrada BAT del nodo; comprobar polaridad fisica.",15,151)
text("J5: interruptor interno en serie. Bateria 1S protegida externa.",15,157)
text("J4: cabezal separado, cable corto; comprobar I2C y estanqueidad.",15,163)
text("Headers y taladros provisionales. Modulo sin huella verificada.",15,169)
text("Fijaciones PCB: patron 72 x 42 mm, agujeros 3.2 mm.",145,155,1.0)
s.append('(embedded_fonts no)\n)\n')
(OUT / f"{NAME}.kicad_sch").write_text("\n".join(s),encoding="utf-8")

project = {"meta":{"filename":NAME+".kicad_pro","version":1}, "text_variables":{"ESTADO":"ANTEPROYECTO - NO FABRICAR"}, "net_settings":{"classes":[{"name":"Default","clearance":0.25,"track_width":0.3,"via_diameter":0.8,"via_drill":0.4,"diff_pair_width":0.3,"diff_pair_gap":0.25,"diff_pair_via_gap":0.25,"pcb_color":"rgba(0, 0, 0, 0.000)","schematic_color":"rgba(0, 0, 0, 0.000)","wire_width":6,"bus_width":12,"line_style":0}],"meta":{"version":4},"net_colors":None,"netclass_assignments":None,"netclass_patterns":[]}}
(OUT/f"{NAME}.kicad_pro").write_text(json.dumps(project,indent=2),encoding="utf-8")

b = k.BOARD()
b.GetDesignSettings().SetBoardThickness(k.FromMM(pcb["espesor"]))
nets = {}
for net in sorted({net for c in components for net in c["pins"]}):
    info = k.NETINFO_ITEM(b,"/"+net)
    b.Add(info); nets[net] = info

def vec(x,y): return k.VECTOR2I(k.FromMM(x),k.FromMM(y))

fp_root = Path("C:/Program Files/KiCad/10.0/share/kicad/footprints")
for c in components:
    libname,fpname = c["footprint"].split(":")
    fp = k.FootprintLoad(str(fp_root/(libname+".pretty")),fpname)
    if fp is None: raise RuntimeError(c["footprint"])
    fp.SetReference(c["ref"]); fp.SetValue(c["value"])
    fp.SetFPID(k.LIB_ID(libname,fpname))
    fp.SetPosition(vec(*c["pcb"]))
    path = k.KIID_PATH()
    path.push_back(k.KIID(root_uuid)); path.push_back(k.KIID(uid(c["ref"])))
    fp.SetPath(path)
    if c.get("dnp") and hasattr(k,"FP_DNP"):
        fp.SetAttributes(fp.GetAttributes() | k.FP_DNP)
    fp.Value().SetVisible(False)
    if c["ref"].startswith("H"):
        px,py=c["pcb"]
        fp.Reference().SetPosition(vec(px,py+(4 if py<125 else -4)))
    elif c["ref"] in ["J1","J2","J5"]:
        px,py=c["pcb"]
        fp.Reference().SetPosition(vec(px,py+7))
    for pad in fp.Pads():
        num = pad.GetNumber()
        if num and int(num) <= len(c["pins"]): pad.SetNet(nets[c["pins"][int(num)-1]])
    b.Add(fp)

def line(x1,y1,x2,y2,layer,width=.1):
    shape = k.PCB_SHAPE(); shape.SetShape(k.SHAPE_T_SEGMENT); shape.SetStart(vec(x1,y1)); shape.SetEnd(vec(x2,y2)); shape.SetLayer(layer); shape.SetWidth(k.FromMM(width)); b.Add(shape)

def board_text(t,x,y,size,layer=k.F_SilkS):
    obj = k.PCB_TEXT(b); obj.SetText(t); obj.SetPosition(vec(x,y)); obj.SetTextSize(vec(size,size)); obj.SetTextThickness(k.FromMM(size*.15)); obj.SetLayer(layer); b.Add(obj)

right,bottom=100+pcb["largo"],100+pcb["ancho"]
for points in [(100,100,right,100),(right,100,right,bottom),(right,bottom,100,bottom),(100,bottom,100,100)]: line(*points,k.Edge_Cuts,.05)
for points in [(110,109,150,109),(150,109,150,129),(150,129,110,129),(110,129,110,109)]: line(*points,k.Dwgs_User,.15)
board_text("RESERVA RADIO NODE",130,116,1.0,k.Dwgs_User)
board_text("40 x 20 - MEDIR",130,120,1.0,k.Dwgs_User)
board_text("SISCOM v0.1",140,104,1.3)
board_text("SIN RUTEAR / NO FABRICAR",140,146,1.0)
board_text("BAT",110,131,1.0); board_text("SW",122,131,1.0); board_text("BAT NODO",134,131,1.0)
board_text("BUS NODO",160,107,1.0); board_text("SENSOR",170,124,1.0)
board_text(f'{pcb["largo"]} x {pcb["ancho"]} mm / M3 {pcb["largo"]-2*fix} x {pcb["ancho"]-2*fix}',140,bottom+4,1.0,k.Dwgs_User)
k.SaveBoard(str(OUT/f"{NAME}.kicad_pcb"),b)

with (OUT/"BOM.csv").open("w",newline="",encoding="utf-8-sig") as f:
    writer=csv.writer(f); writer.writerow(["Referencia","Valor_funcion","Huella_provisional","Montaje","Estado"])
    for c in components: writer.writerow([c["ref"],c["value"],c["footprint"],"DNP" if c.get("dnp") else "PREVISTO","ANTEPROYECTO"])
with (OUT/"CONEXIONES.csv").open("w",newline="",encoding="utf-8-sig") as f:
    writer=csv.writer(f); writer.writerow(["Referencia","Pin_PCB_nueva","Red"])
    for c in components:
        for i,net in enumerate(c["pins"],1): writer.writerow([c["ref"],i,net])
(OUT/"conectividad_esperada.json").write_text(json.dumps({c["ref"]:{str(i):net for i,net in enumerate(c["pins"],1)} for c in components},indent=2),encoding="utf-8")
print(f"Generados esquema, PCB sin pistas, biblioteca local y tablas en {OUT}")
