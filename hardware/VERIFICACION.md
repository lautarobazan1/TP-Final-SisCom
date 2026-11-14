# Verificación del anteproyecto v0.1

25/10/2026. Comprobaciones ejecutadas sobre archivos, sin ensayos de placas físicas.

| Comprobación | Resultado |
| --- | --- |
| KiCad 10.0.5: lectura y exportación de esquema y PCB | Correctas |
| ERC del esquema | 0 infracciones |
| Conectividad exportada frente al diseño previsto y la PCB | Coinciden: 11 componentes eléctricos, 27 pines y 7 redes |
| Correspondencia esquema/PCB | 0 problemas de paridad |
| DRC de geometría y serigrafía | 0 infracciones en las comprobaciones ejecutadas |
| Conexiones de PCB pendientes | **20 conexiones sin rutear; 0 pistas** |
| Contorno y espesor PCB | 80 x 50 mm, 1,6 mm; 4 fijaciones |
| FreeCAD 1.1.4: reapertura del FCStd generado | Correcta; 10 objetos con geometría válida |
| Bandeja STEP | Válida, 1 sólido; volumen exterior 88 x 58 x 9 mm |
| Bandeja STL | Malla cerrada; 1372 caras |
| Interferencia batería/bandeja de referencia | 0 mm³ |
| Interferencia cápsula/protector de referencia | 0 mm³ |
| Vista funcional y exportaciones de esquema/PCB | Inspeccionadas visualmente |

**La PCB no está lista para fabricar.** La ausencia de infracciones geométricas no compensa las conexiones pendientes. El ERC usa interfaces pasivas y no comprueba por sí solo tensiones, polaridades de los módulos reales, corriente admisible, protección de batería ni adecuación del diseño a IPC.

Las comprobaciones CAD se limitan a las geometrías provisionales. Faltan el modelo comercial del gabinete, huellas y medidas reales de los módulos, soporte del cabezal, sellos y accesorios. Las reservas geométricas no prueban el ajuste de esas piezas reales ni su IP.

Pendientes: ruteo completo, revisión de alimentación durante descarga, consumo y autonomía de 35 días, lectura ambiental, enlace, selección de productos certificados y ensayo IP del conjunto.

## Reproducción

Los generadores sobrescriben sus archivos de salida. Guardar las ediciones manuales antes de ejecutarlos. Las rutas siguientes corresponden a las herramientas instaladas en esta computadora; ejecutar desde la raíz del proyecto en PowerShell.

```powershell
& 'C:/Program Files/KiCad/10.0/bin/python.exe' hardware/scripts/generar_pcb.py
& 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' sch export netlist --format kicadxml --output hardware/pcb/conectividad_exportada.xml hardware/pcb/NodoIntegrador.kicad_sch
& 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' sch erc --format json --output hardware/pcb/ERC.json hardware/pcb/NodoIntegrador.kicad_sch
& 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' pcb drc --format json --schematic-parity --output hardware/pcb/DRC.json hardware/pcb/NodoIntegrador.kicad_pcb
& 'C:/Program Files/KiCad/10.0/bin/python.exe' hardware/scripts/verificar_conectividad.py
& 'C:/Program Files/FreeCAD 1.1/bin/python.exe' hardware/scripts/generar_mecanica.py
```

KiCad CLI emitió avisos por no poder escribir su clave de configuración de usuario de Windows en este entorno. Las exportaciones y los informes se generaron y se reabrieron correctamente; no se cambió el registro del usuario.

Los resultados numéricos también están en `pcb/verificacion_conectividad.json`, `pcb/ERC.json`, `pcb/DRC.json` y `mecanica/geometria_verificada.json`.
