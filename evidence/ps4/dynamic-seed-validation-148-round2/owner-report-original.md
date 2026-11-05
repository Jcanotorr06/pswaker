# Baseline performance report

Build ID: 6e885683f47a49a119ae
Version: 01.23
SHA-256: 107e13f80423e89324aabb3aca453f46f2a0ea13569e0be6a509588fc9835a3d
Model: PS4 Slim
Firmware: 9.00
Goldhen: v2.4b18

## Pause menu reported numbers

Cold:
30.00 FPS, p95 33.40, p99 50.05, max 50.059s

Warm
30.00 FPS, p95 33.40, p99 33.45, max 50.14ms

## Logs and Analysis

Cold: ./cold
Warm: ./warm

Each folder contains an `analysis` folder with the output of `frame-pacing.py` and a seed folder with the output of `complete-package.py`

# Observation

Closing the game using the menu's `Quit game` option caused the error code `ce-34878-0`
