"""Renderiza exportaciones KiCad con Qt, sin abrir ventanas.
Ejecutar con el Python de FreeCAD, que incluye PySide6.
"""
import os
os.environ["QT_QPA_PLATFORM"]="offscreen"
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QImage,QPainter
from PySide6.QtCore import Qt

ROOT=Path(__file__).resolve().parents[2]
app=QApplication([])
sources=[(ROOT/"tmp/diseno/esquema/NodoIntegrador.svg","esquema.png",2200),
         (ROOT/"tmp/diseno/pcb.svg","pcb.png",1800)]
for source,name,width in sources:
    renderer=QSvgRenderer(str(source))
    if not renderer.isValid(): raise RuntimeError(str(source))
    view=renderer.viewBoxF()
    height=round(width*view.height()/view.width())
    img=QImage(width,height,QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.white)
    painter=QPainter(img)
    renderer.render(painter)
    painter.end()
    output=ROOT/"tmp/diseno"/name
    if not img.save(str(output)): raise RuntimeError(str(output))
    print(str(output))
