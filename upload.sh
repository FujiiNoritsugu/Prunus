#!/bin/bash

# Arduino CLIのパスを設定（必要に応じて修正）
ARDUINO_CLI="/home/fujii/Prunus/bin/arduino-cli"

# ArduinoボードのFQBN（Fully Qualified Board Name）を設定
BOARD_FQBN="arduino:avr:uno"

# シリアルポートの設定（必要に応じて修正）
SERIAL_PORT="/dev/ttyACM0"

# スケッチのディレクトリを設定
SKETCH_DIR="/home/fujii/Prunus/test_sketch"

# スケッチのコンパイル
$ARDUINO_CLI compile --fqbn $BOARD_FQBN $SKETCH_DIR

# ボードへのアップロード
$ARDUINO_CLI upload -p $SERIAL_PORT --fqbn $BOARD_FQBN $SKETCH_DIR
