# ILOFAR Mode 357 Spectrogram Viewer

Interactive web viewer for dynamic solar radio spectrograms from the Irish LOFAR station (ILOFAR).

This single-page application visualizes high-resolution spectrogram data across three observing modes (Mode 3, Mode 5, Mode 7) in a stacked layout.

<img width="1443" height="657" alt="LofarScreen" src="https://github.com/user-attachments/assets/ab776eb3-059f-4201-bb15-492ebcf89c49" />


## What it does

- Loads the most recent `.dat` file converted to JSON (`latest_spectrogram.json`)
- Displays a **stacked dynamic spectrogram**
- Shared time axis (UTC) with readable HH:MM ticks
- Real-time controls to explore the data:

  | Control         | Function                                      |
  |-----------------|-----------------------------------------------|
  | Start Time      | Slide to choose where in the observation to begin (minutes) |
  | Duration        | Select how many minutes to display (Observation start - Observation end) |
  | Colormap        | Switch between Viridis, Plasma, Inferno, Hot, Jet |
  | Gamma           | Adjust contrast / dynamic range (power-law normalization) |
  | Reset View      | Return to full-duration view at t=0           |

- Intensity is shown after:
  - Log10 scaling
  - Per-frequency background (median) subtraction
  - Global percentile-based clipping + gamma correction
- Hover shows precise frequency, time, and normalized intensity values



