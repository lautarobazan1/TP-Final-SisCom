# BME280 y batería por LoRa

Primera etapa: **LoRa Radio Node v1.0 (ATmega328P) → Heltec Wireless Tracker (ESP32-S3 + SX1262)**. La Tracker muestra temperatura, humedad, presión y la batería **del nodo remoto**.

Anteproyecto de hardware: [PCB integradora, gabinete y cabezal de medición](hardware/ANTEPROYECTO.md). Incluye archivos KiCad y FreeCAD provisionales; faltan medidas físicas, selección de gabinete y ruteo.

Los programas parten de `Radio Node.txt` y `Heltec Wireless Tracker.txt`. Los dos originales se conservan. Se mantienen sus pines, la inicialización TFT y los parámetros del enlace: **915 MHz, SF7, BW 125 kHz, CR 4/5, sync word 0x12**, potencia de 14 dBm y preámbulo de 8 símbolos. Se habilitó CRC en ambos extremos.

## Archivos para cargar

- `firmware/LoRaNodeV1/LoRaNodeV1.ino`: lee el BME280 y transmite cada 5 segundos.
- `firmware/HeltecWirelessTracker/HeltecWirelessTracker.ino`: recibe y muestra los datos en la TFT ST7735 de 160×80.
- Cada carpeta contiene `Config.h` y `Telemetria.h`; conservarlos junto a su `.ino`. Arduino IDE los abre como pestañas. Las dos copias de `Telemetria.h` deben mantenerse idénticas.

## Conexión del BME280 al nodo

| BME280 | LoRa Radio Node v1.0 |
| --- | --- |
| VCC/VIN | 3V3 |
| GND | GND |
| SDA | A4 / SDA |
| SCL | A5 / SCL |

Se prueban automáticamente las direcciones `0x76` y `0x77`. En módulos con CS/CSB y SDO expuestos, CS debe quedar alto para I2C y SDO determina la dirección; seguir el pinout de tu módulo. Un **BMP280** no mide humedad y este código requiere **BME280**.

## Conexión y configuración de la batería

El `Config.h` actual tiene `BATTERY_CONNECTED = true`, resistencias de **150 kΩ + 150 kΩ** y `ADC_REFERENCE_MV = 3226`. Esto describe la configuración del firmware; hay que verificar que coincida con el divisor y la alimentación físicos. Si el divisor no está montado, poner `BATTERY_CONNECTED = false`; la pantalla mostrará **`Bat: -- (sin medicion)`**.

Para una **Li-ion de una celda, nominal 3,7 V, máximo 4,2 V**, conectar:

```text
BAT+ antes del regulador --- R1 150 kohm ---+--- R2 150 kohm --- GND
                                          |
                                          +--- A0 del nodo
                                          |
                                          +--- C1 100 nF ----- GND

BAT- ------------------------------------------ GND del nodo
```

1. Montar el divisor y compartir GND. C1 ayuda a estabilizar la entrada por el valor alto de las resistencias. Esperar al menos 50 ms desde la alimentación antes de medir; el arranque del programa ya supera ese tiempo.
2. Verificar con multímetro que A0 esté aproximadamente a **la mitad de la tensión de batería**: 2,10 V si la batería está a 4,20 V. **No conectar BAT+ directamente a A0**.
3. En `firmware/LoRaNodeV1/Config.h`, dejar `BATTERY_CONNECTED = true` solamente si el divisor está montado y comprobado. Cargar el nodo después de cualquier cambio.
4. Medir 3V3 respecto de GND y ajustar `ADC_REFERENCE_MV` a ese valor en milivoltios. La referencia del ADC es VCC, no la tensión nominal de la batería. Si queda una diferencia con el multímetro, ajustar `BATTERY_CALIBRATION = tension_real / tension_mostrada` partiendo de 1,0.

El código promedia 32 muestras antes de transmitir. La fórmula es `VBAT = ADC × VREF / 1023 × (R1 + R2) / R2`. Recalibrar si cambia la alimentación de 3V3. Cuando la batería baja tanto que el regulador pierde regulación, VCC deja de ser constante y la lectura requiere corregir la referencia.

La pantalla muestra voltios y **porcentaje aproximado** (`~`) mediante una curva orientativa para Li-ion de una celda. No equivale a medir capacidad restante y no sustituye la protección de la batería. El divisor de 150 kΩ + 150 kΩ toma unos 14 µA a 4,2 V. Esta etapa no implementa sueño del ATmega ni demuestra todavía la autonomía del proyecto.

## Carga en Arduino IDE

Bibliotecas del Gestor de bibliotecas:

| Placa | Bibliotecas |
| --- | --- |
| Nodo | **LoRa** de Sandeep Mistry; **Adafruit BME280 Library** y sus dependencias **Adafruit Unified Sensor** y **Adafruit BusIO** |
| Tracker | **RadioLib** de Jan Gromes; **Adafruit GFX Library**; **Adafruit ST7735 and ST7789 Library**, con sus dependencias |

1. Abrir `LoRaNodeV1.ino`. Seleccionar **Arduino Pro or Pro Mini → ATmega328P (3.3V, 8 MHz)**. Usar un adaptador USB-serie con **lógica de 3,3 V** según el pinout de la placa. Monitor serie: **9600 baud**. No seleccionar la variante de 16 MHz.
2. Abrir `HeltecWirelessTracker.ino`. Seleccionar **Heltec Wireless Tracker**, usando el paquete ESP32 que ya tenés instalado. Monitor serie: **115200 baud**. Mantener las opciones de carga/USB que ya funcionaban con tu ejemplo.
3. Conectar las antenas de 915 MHz antes de encender y cargar los dos programas. El nuevo formato de datos requiere ambos firmwares; el receptor nuevo descarta el antiguo mensaje `Hola Heltec!`.

## Qué debe verse

```text
BME280 + BATERIA NODO
Nodo 1  RSSI -72 dBm
Temp: 23.45 C
Hum:  56.78 %
Pres: 1013.2 hPa
Bat: 3.85 V ~50%
Edad 0s  #12
```

Los números anteriores son solo un ejemplo. Sin divisor, la fila de batería indica que no hay medición. Al arrancar la Tracker espera el primer paquete. Si pasan **20 segundos sin un paquete válido del nodo 1**, muestra **`SIN DATOS RECIENTES`** y conserva los últimos valores en amarillo, con su antigüedad. Si el nodo informa un fallo del BME280, muestra el error sin inventar lecturas; el nodo reintenta detectar el sensor en el siguiente ciclo.

Para probar: comprobar cambios del sensor, desconectar el BME280 y comprobar el mensaje de error, apagar el nodo durante más de 20 segundos y comprobar el estado de datos antiguos, luego reconectarlo y comprobar recuperación. Después de montar el divisor, comparar batería con multímetro. No desconectar cables de alimentación provocando cortocircuitos.

## Formato del paquete

19 bytes, enteros little-endian; no se transmite directamente una estructura C ni valores `float`.

| Bytes | Contenido |
| --- | --- |
| 0–2 | `S`, `C`, versión `1` |
| 3 | ID de nodo, inicialmente `1` |
| 4 | bit 0: BME280 válido; bit 1: batería válida |
| 5–8 | contador de envíos (`uint32_t`, reinicia al arrancar) |
| 9–10 | temperatura en centésimas de °C (`int16_t`) |
| 11–12 | humedad en centésimas de % (`uint16_t`) |
| 13–16 | presión en Pa (`uint32_t`) |
| 17–18 | batería en mV (`uint16_t`) |

Los campos cuya bandera no está activa no se muestran como mediciones. La Tracker valida longitud, identificador, versión, banderas, ID del nodo y rangos; la radio comprueba el CRC LoRa. Es un enlace local de un solo nodo, sin confirmación de entrega ni cifrado.

## Verificación y referencias

Las versiones locales usadas para compilar se registran en `VALIDACION.md`. `tests/telemetria_test.cpp` comprueba bytes conocidos, temperaturas negativas, extremos y rechazo de paquetes inválidos. La compilación no sustituye la prueba con las placas físicas.

- [LoRa Radio Node v1.0: esquema del fabricante IOT-MCU](https://github.com/IOT-MCU/LoRa-Radio-Node-v1.0). Confirma SPI D10/D9/D2, I2C A4/A5 y reloj de 8 MHz; este esquema no incluye un divisor de batería al ADC.
- [Heltec Wireless Tracker](https://heltec.org/project/wireless-tracker/): modelo ESP32-S3 + SX1262 y pantalla TFT.
- [API de Arduino LoRa](https://github.com/sandeepmistry/arduino-LoRa/blob/master/API.md) y [configuración de RadioLib](https://github.com/jgromes/RadioLib/wiki/Default-configuration).
