# Prunus
arduino-cli monitor -p /dev/ttyACM0 -b arduino:avr:uno
arduino-cli compile -b arduino:renesas_uno:minima
arduino-cli board list
arduino-cli upload -b arduino:renesas_uno:minima
arduino-cli monitor -p /dev/ttyACM0 -b arduino:renesas_uno:minima
arduino-cli monitor -p /dev/ttyACM1 -b arduino:renesas_uno:minima
arduino-cli lib list
