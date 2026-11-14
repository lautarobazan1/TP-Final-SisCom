#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../firmware/LoRaNodeV1/Telemetria.h"

int main() {
  using namespace Telemetria;
  Sample sent = {1, SENSOR_VALID | BATTERY_VALID, 0x12345678,
                 -1234, 5678, 101325, 3850};
  uint8_t bytes[PACKET_SIZE];
  encode(sent, bytes);
  const uint8_t golden[] = {
      0x53, 0x43, 0x01, 0x01, 0x03, 0x78, 0x56, 0x34, 0x12,
      0x2E, 0xFB, 0x2E, 0x16, 0xCD, 0x8B, 0x01, 0x00, 0x0A, 0x0F};
  assert(sizeof(golden) == PACKET_SIZE);
  assert(memcmp(bytes, golden, PACKET_SIZE) == 0);
  Sample received = {};
  assert(decode(golden, sizeof(golden), received));
  assert(received.temperatureCentiC == -1234);
  assert(received.humidityCentiPct == 5678);
  assert(received.pressurePa == 101325);
  assert(received.batteryMv == 3850);
  assert(received.sequence == 0x12345678);
  for (size_t i = 0; i < PACKET_SIZE; ++i) assert(!decode(bytes, i, received));
  assert(!decode(bytes, PACKET_SIZE + 1, received));
  for (int field = 0; field < 3; ++field) {
    bytes[field] ^= 0x01;
    assert(!decode(bytes, sizeof(bytes), received));
    bytes[field] ^= 0x01;
  }
  bytes[3] = 0; assert(!decode(bytes, sizeof(bytes), received)); bytes[3] = 1;
  bytes[4] = 0x80; assert(!decode(bytes, sizeof(bytes), received));
  encode(sent, bytes);
  write16(bytes + 11, 10001); assert(!decode(bytes, sizeof(bytes), received));
  encode(sent, bytes);
  write32(bytes + 13, 110001); assert(!decode(bytes, sizeof(bytes), received));
  encode(sent, bytes);
  write16(bytes + 17, 4501); assert(!decode(bytes, sizeof(bytes), received));
  sent.temperatureCentiC = -4000;
  sent.humidityCentiPct = 0;
  sent.pressurePa = 30000;
  sent.batteryMv = 2000;
  sent.sequence = 0xFFFFFFFF;
  encode(sent, bytes); assert(decode(bytes, sizeof(bytes), received));
  assert(received.temperatureCentiC == -4000 && received.sequence == 0xFFFFFFFF);
  sent.temperatureCentiC = 8500;
  sent.humidityCentiPct = 10000;
  sent.pressurePa = 110000;
  sent.batteryMv = 4500;
  encode(sent, bytes); assert(decode(bytes, sizeof(bytes), received));
  sent.temperatureCentiC = 8501;
  encode(sent, bytes); assert(!decode(bytes, sizeof(bytes), received));
  sent = {1, 0, 1, 0, 0, 0, 0};
  encode(sent, bytes); assert(decode(bytes, sizeof(bytes), received));
  assert(received.flags == 0);  // Error de sensor y bateria ausente son estados validos.
  assert(batteryPercent(3000) == 0 && batteryPercent(3300) == 0);
  assert(batteryPercent(3850) == 50 && batteryPercent(4200) == 100);
  uint8_t previous = 0;
  for (uint16_t mv = 2000; mv <= 4500; ++mv) {
    const uint8_t pct = batteryPercent(mv);
    assert(pct >= previous && pct <= 100);
    previous = pct;
  }
  puts("OK: trama conocida, negativos, limites, campos invalidos y curva de bateria.");
}
