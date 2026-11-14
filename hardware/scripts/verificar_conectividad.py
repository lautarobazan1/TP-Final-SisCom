"""Compara las redes exportadas por KiCad con el esquema previsto y la PCB.
Ejecutar con el Python de KiCad, después de exportar conectividad_exportada.xml.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import pcbnew as k

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"pcb"
expected=json.loads((OUT/"conectividad_esperada.json").read_text(encoding="utf-8"))
expected_electrical={ref:pins for ref,pins in expected.items() if pins}
netlist=ET.parse(OUT/"conectividad_exportada.xml").getroot()
schematic={ref:{} for ref in expected_electrical}
for net in netlist.findall("nets/net"):
    name=net.attrib["name"].lstrip("/")
    for pin in net.findall("node"):
        schematic.setdefault(pin.attrib["ref"],{})[pin.attrib["pin"]]=name
assert schematic==expected_electrical,(schematic,expected_electrical)
board=k.LoadBoard(str(OUT/"NodoIntegrador.kicad_pcb"))
actual={}
for fp in board.GetFootprints():
    pins={pad.GetNumber():pad.GetNetname().lstrip("/") for pad in fp.Pads() if pad.GetNumber()}
    actual[fp.GetReference()]=pins
assert actual==expected,(actual,expected)
assert len(list(board.GetTracks()))==0,"Esta version debe identificarse como no ruteada"
param=json.loads((ROOT/"parametros.json").read_text(encoding="utf-8"))["pcb_mm"]
outline=board.GetBoardEdgesBoundingBox()
assert abs(k.ToMM(outline.GetWidth())-param["largo"])<.1
assert abs(k.ToMM(outline.GetHeight())-param["ancho"])<.1
assert abs(k.ToMM(board.GetDesignSettings().GetBoardThickness())-param["espesor"])<.001
erc=json.loads((OUT/"ERC.json").read_text(encoding="utf-8"))
assert sum(len(sheet["violations"]) for sheet in erc["sheets"])==0
drc=json.loads((OUT/"DRC.json").read_text(encoding="utf-8"))
assert not drc["violations"],drc["violations"]
assert not drc["schematic_parity"],drc["schematic_parity"]
assert len(drc["unconnected_items"])==20,"Actualizar informe si cambia el alcance de esta version"
report={"componentes_electricos":len(expected_electrical),"fijaciones":4,"pines_conectados":sum(len(pins) for pins in expected_electrical.values()),"redes":len(netlist.findall("nets/net")),"conectividad_esquema_pcb_coincide":True,"pistas":0,"ERC_infracciones":0,"DRC_violaciones_geometricas":0,"DRC_problemas_paridad":0,"DRC_conexiones_sin_rutear":20,"fabricacion_habilitada":False}
(OUT/"verificacion_conectividad.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report))
