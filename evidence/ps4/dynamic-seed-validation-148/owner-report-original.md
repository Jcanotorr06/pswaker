# Baseline performance report

Build ID: 6e885683f47a49a119ae
Version: 01.23
SHA-256: 058bd19c4fc4be1782b631ad4e808dbddea4b31530f0e3a599c38d71b93090e0
Model: PS4 Slim
Firmware: 9.00
Goldhen: v2.4b18

## Pause menu reported numbers

Cold:
30.00 FPS, p95 33.40, p99 33.44, max 50.05ms

Warm
30.00 FPS, p95 33.40, p99 50.00, max 50.12ms

## Logs and Analysis

Cold: ./cold
Warm: ./warm

Each folder contains an `analysis` folder with the output of `frame-pacing.py` and a seed folder with the output of `complete-package.py`

# Observation

Closing the game using the menu's `Quit game` option caused the error code `ce-34878-0`
