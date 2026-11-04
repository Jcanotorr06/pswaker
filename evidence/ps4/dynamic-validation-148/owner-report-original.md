# Baseline performance report

Build ID: 6e885683f47a49a119ae
Version: 01.23
SHA-256: 14069c0c7776e330ae9441f81e7537ba95859dfa70bd4b65059d6ec5374b4328
Model: PS4 Slim
Firmware: 9.00
Goldhen: v2.4b18

## Pause menu reported numbers

Cold: 
29.99 FPS, p95 33.40, p99 33.43, max 100.10ms

Warm:
30.00 FPS, p95 33.40, p99 33.44, max 50.06ms

## Logs and Analysis

Cold: ./cold
Warm: ./warm

Each folder contains an `analysis` folder with the output of `frame-pacing.py` and a seed folder with the output of `complete-package.py`

# Observation

Closing the game using the menu's `Quit game` option caused the error code `ce-34878-0`
