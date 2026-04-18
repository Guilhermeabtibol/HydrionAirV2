#include "DHT.h"
#include <MQUnifiedsensor.h>

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define Board ("Arduino UNO")
#define MQ7Pin (A0)
#define Type ("MQ-7")
#define Voltage_Resolution (5)
#define ADC_Bit_Resolution (10)
#define RatioMQ7CleanAir (27.0f)

MQUnifiedsensor MQ7(Board, Voltage_Resolution, ADC_Bit_Resolution, MQ7Pin, Type);

void setup() {
  Serial.begin(9600);
  dht.begin();

  MQ7.setRegressionMethod(1);
  MQ7.setA(99.042);
  MQ7.setB(-1.518);
  MQ7.setR0(10.0);
  MQ7.init();                     // <--- adicionado
  MQ7.calibrate(RatioMQ7CleanAir);
}

void loop() {
  delay(2000);
  
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  MQ7.update();
  float ppm = MQ7.readSensor();
  
  if (isnan(h) || isnan(t) || ppm < 0) {
    Serial.println("{\"erro\": \"leitura invalida\"}");
    return;
  }
  
  Serial.print("{\"temperatura\":");
  Serial.print(t);
  Serial.print(",\"umidade\":");
  Serial.print(h);
  Serial.print(",\"co_ppm\":");
  Serial.print(ppm);
  Serial.println("}");
}