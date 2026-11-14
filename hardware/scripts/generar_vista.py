"""Vista funcional del anteproyecto. Dibujo propio, sin escala."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"diagramas"
OUT.mkdir(parents=True,exist_ok=True)
im=Image.new("RGB",(1680,1100),"#f3f6f8")
d=ImageDraw.Draw(im)
INK="#172e40"; MUTED="#536c7b"; TEAL="#168b96"; BLUE="#26619b"; AMBER="#a46b17"

def font(n,bold=False): return ImageFont.truetype("C:/Windows/Fonts/"+("segoeuib.ttf" if bold else "segoeui.ttf"),n)
def text(x,y,t,n=25,fill=INK,bold=False): d.text((x,y),t,font=font(n,bold),fill=fill)
def rect(bounds,fill,outline=None,width=2,radius=15): d.rounded_rectangle(bounds,radius,fill=fill,outline=outline,width=width)
def arrow(points,color,width=5):
    d.line(points,fill=color,width=width,joint="curve")
    x,y=points[-1]; px,py=points[-2]; a=math.atan2(y-py,x-px)
    d.polygon([(x,y),(x-17*math.cos(a-.45),y-17*math.sin(a-.45)),(x-17*math.cos(a+.45),y-17*math.sin(a+.45))],fill=color)

rect((35,32,1645,155),"#172e40",radius=18)
text(65,48,"PCB + gabinete para el nodo remoto",40,"white",True)
text(66,105,"Anteproyecto v0.1  ·  Radio Node + BME280  ·  25/10/2026",23,"#bdd5df")
rect((1320,63,1615,119),"#f2cd80",radius=10)
text(1339,75,"COTAS PROVISIONALES",20,INK,True)

text(62,186,"01  Electrónica protegida",30,INK,True)
text(920,186,"02  Cabezal de medición separado",30,INK,True)

# Caja principal y junta perimetral.
rect((62,242,756,646),"#dce4e9","#758c9b",4,22)
rect((80,260,738,628),"#ffffff","#bdcbd4",3,16)
rect((115,302,491,515),"#d9efdf","#387d59",3,12)
text(137,322,"PCB integradora",28,"#245a3d",True)
rect((138,376,467,440),"#274b60",radius=8)
text(158,390,"Radio Node actual",26,"white",True)
text(137,464,"80 × 50 mm · sin rutear",21,"#245a3d")
rect((523,302,699,515),"#f6e5bd","#b78736",3,12)
text(544,327,"Li-ion 1S",25,AMBER,True)
text(544,370,"3,7 V",24,AMBER)
text(544,409,"Capacidad",20,AMBER)
text(544,440,"pendiente",20,AMBER)
text(116,549,"Bandeja y separadores interiores",24,MUTED)
text(116,589,"Gabinete comercial certificado IP65/IP66",24,INK,True)
# Entrada estanca y cable conceptual.
rect((730,369,778,407),"#879da8","#526c7b",2,5)
d.line([(778,388),(841,388),(841,435),(946,435),(946,392),(1014,392)],fill=INK,width=8,joint="curve")
text(786,470,"Arnés corto",22,INK,True)
text(786,504,"3V3 · GND",20,MUTED)
text(786,536,"SDA · SCL",20,MUTED)
text(786,575,"Pasacables",20,MUTED)
text(786,603,"estancos",20,MUTED)

# Protector de sol/lluvia, cápsula en corte y membrana.
for y in [260,315,370,425,480,535]:
    rect((965,y,1510,y+18),"#e3e8eb","#a7b7c1",2,9)
rect((1010,299,1395,514),"#e6edf1","#708998",3,18)
rect((1027,316,1378,497),"#ffffff",radius=9)
text(1055,331,"Cámara pequeña",27,INK,True)
text(1055,373,"sin electrónica caliente",21,MUTED)
rect((1110,417,1285,455),"#d2e9e9","#297e85",2,5)
text(1132,419,"BME280",25,TEAL,True)
# Ventana sustituye un tramo de pared, como barrera permeable.
d.rectangle((1118,495,1278,517),fill="#f3f6f8")
rect((1118,494,1278,507),"#64bec7",TEAL,2,3)
rect((993,374,1034,411),"#879da8","#526c7b",2,5)
arrow([(1197,650),(1197,566),(1197,512)],TEAL,6)
text(1271,590,"Aire y vapor",24,TEAL,True)
text(1271,625,"atraviesan la membrana",20,TEAL)
text(1012,673,"Membrana + sellos: elegir y ensayar el IP del conjunto",22,INK,True)
text(1058,230,"Protector solar / lluvia adicional",22,MUTED)

rect((62,729,1618,806),"#e3eef4",radius=12)
text(86,744,"La barrera estanca está en los gabinetes y la membrana.",27,INK,True)
text(86,780,"El protector exterior deja circular aire. El sensor queda próximo a la ventana y separado del calor.",21,MUTED)

cards=[(62,830,556,1030),(580,830,1074,1030),(1098,830,1618,1030)]
for card in cards: rect(card,"white","#d5e0e7",2,13)
text(84,847,"PCB propia",25,INK,True)
text(84,890,"Esquema y posición inicial en KiCad",22,MUTED)
text(84,930,"Divisor: 150 kΩ + 150 kΩ, 100 nF",22,MUTED)
text(84,970,"Módulos por arnés; cotas por medir",22,MUTED)
text(602,847,"35 días = 840 horas",25,INK,True)
text(602,890,"I media ≤ capacidad útil / 840 h",22,MUTED)
text(602,930,"Medir consumo y capacidad real",22,MUTED)
text(602,970,"Autonomía todavía sin demostrar",22,MUTED)
text(1120,847,"Antes de fabricar",25,INK,True)
text(1120,890,"Medir módulos y batería con soporte",22,MUTED)
text(1120,930,"Elegir gabinete, membrana y antena",22,MUTED)
text(1120,970,"Ajustar mecánica, rutear y ensayar",22,MUTED)
text(63,1054,"SECCIÓN FUNCIONAL SIN ESCALA  ·  Los dibujos no representan productos certificados ya seleccionados.",20,MUTED)
im.save(OUT/"arquitectura.png")
print(str(OUT/"arquitectura.png"))
