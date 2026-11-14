# Validación de la primera etapa

Fecha local: 15 de octubre de 2026. Se verificó el código en esta computadora; todavía no se cargó ni se ensayó en las placas físicas.

| Comprobación | Resultado |
| --- | --- |
| Nodo, batería deshabilitada | Compila para `arduino:avr:pro:cpu=8MHzatmega328`. Flash: 15.970 / 30.720 bytes (51 %). RAM global: 586 / 2.048 bytes (28 %). |
| Nodo, batería habilitada | Compila la misma fuente con `BATTERY_CONNECTED = true` en una copia temporal. Flash: 16.546 / 30.720 bytes (53 %). RAM global: 620 / 2.048 bytes (30 %). |
| Heltec Wireless Tracker | Compila para `esp32:esp32:heltec_wireless_tracker`. Flash: 373.993 / 3.342.336 bytes (11 %). RAM global: 25.168 / 327.680 bytes (7 %). |
| Formato de telemetría | Pruebas C++ aprobadas: trama binaria conocida, temperatura negativa, límites, longitud, versión, banderas, rangos y porcentaje monotónico acotado de 0 a 100. |
| Consistencia | Las dos copias de `Telemetria.h` tienen el mismo SHA-256. |

Versiones de dependencias: Arduino AVR 1.8.8; LoRa 0.8.0; Adafruit BME280 2.3.0; Adafruit BusIO 1.17.4; Adafruit Unified Sensor 1.1.15; ESP32 de Espressif 3.3.12; RadioLib 7.7.1; Adafruit GFX 1.12.6; Adafruit ST7735 and ST7789 1.11.0.

La compilación de la Tracker emite un aviso de RadioLib sobre USB CDC y suspensión. Este firmware no usa suspensión del ESP32; el aviso no impidió compilar.

Comandos para reproducir desde la carpeta del proyecto, con Arduino CLI y g++ disponibles en PATH:

```powershell
arduino-cli compile --fqbn arduino:avr:pro:cpu=8MHzatmega328 --build-path build/node firmware/LoRaNodeV1
arduino-cli compile --fqbn esp32:esp32:heltec_wireless_tracker --build-path build/tracker firmware/HeltecWirelessTracker
g++ -std=c++11 -Wall -Wextra -Werror tests/telemetria_test.cpp -o build/telemetria_test.exe
.\build\telemetria_test.exe
```

Pendiente en hardware: comprobar lectura real del BME280, enlace SX1276/SX1262 y presentación TFT; montar el divisor, habilitar y calibrar batería; comprobar aviso de ausencia de paquetes y recuperación. No se midieron consumo, alcance ni autonomía.
