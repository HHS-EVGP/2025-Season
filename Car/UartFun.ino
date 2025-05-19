#include <Wire.h>

#define I2C_SLAVE_ADDR 0x42
#define UART_RX_PIN 16
#define UART_TX_PIN 17
#define BUFFER_SIZE 256
#define I2C_CHUNK_SIZE 32  // Maximum bytes per I2C transmission

char fullSentence[BUFFER_SIZE];
char tempBuffer[BUFFER_SIZE];
char tempBuffer2[BUFFER_SIZE];
volatile bool hasFullSentence = false;
int tempIndex = 0;
int currentChunkIndex = 0;  // Track current position in sentence
int remainingBytes = 0;     // Track remaining bytes to send

HardwareSerial UART(2);

void setup() {
  Serial.begin(9600);
  UART.begin(9600, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  Wire.begin(I2C_SLAVE_ADDR);
  Wire.onRequest(onI2CRequest);
  Serial.println("ESP32 UART to I2C - Waiting for GPS...");
}

void loop() {
  while (UART.available()) {
    char c = UART.read();

    if (tempIndex < BUFFER_SIZE - 1) {
      tempBuffer[tempIndex++] = c;
      tempBuffer[tempIndex] = '\0';

      if (c == '\n') {
        strncpy(tempBuffer2, tempBuffer, BUFFER_SIZE);
        memset(tempBuffer, 0, BUFFER_SIZE);

        if (strncmp(tempBuffer2, "$GNRMC", 6) == 0) {
          strncpy(fullSentence, tempBuffer2, BUFFER_SIZE);
          hasFullSentence = true;
          currentChunkIndex = 0;  // Reset chunk index for new sentence
          remainingBytes = strlen(fullSentence);
        } else {
          memset(tempBuffer2, 0, BUFFER_SIZE);
        }

        tempIndex = 0;
      }
    } else {
      // Overflow protection
      tempIndex = 0;
      memset(tempBuffer, 0, BUFFER_SIZE);
      memset(tempBuffer2, 0, BUFFER_SIZE);
      memset(fullSentence, 0, BUFFER_SIZE);
    }
  }

  delay(10);
}

void onI2CRequest() {
  if (hasFullSentence && remainingBytes > 0) {
    // Calculate how many bytes to send in this chunk
    int chunkSize = min(I2C_CHUNK_SIZE, remainingBytes);
    
    // Send the chunk
    Wire.write((const uint8_t*)fullSentence + currentChunkIndex, chunkSize);
    
    // Also send to Serial for debugging
    Serial.write((const uint8_t*)fullSentence + currentChunkIndex, chunkSize);
    
    // Update positions
    currentChunkIndex += chunkSize;
    remainingBytes -= chunkSize;
    
    // If we've sent the entire sentence, reset flags
    if (remainingBytes <= 0) {
      hasFullSentence = false;
      memset(fullSentence, 0, BUFFER_SIZE);
    }
  } else {
    // No data to send or transmission complete
    Wire.write('\0');
  }
}