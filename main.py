from radiospectra.spectrogram import Spectrogram 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import gridspec
from matplotlib.colors import PowerNorm, LogNorm
import json
from pathlib import Path
import os

NEWOBS = Path(r"./ldb/data_buff/2026.01.20/datastream/")

def get_mtime(path):
    return path.stat().st_mtime


x_dat_files = sorted(
    NEWOBS.glob("*X.dat"),
    key=get_mtime,
    reverse=True   
)


x_dat_file = x_dat_files[0]

def bst_to_json(bst_file, output_json):
    """
    Convert BST file to JSON format for web plotting.
    No compression - preserves all data fidelity.
    
    Parameters
    ----------
    bst_file : str
        Path to .dat file
    output_json : str
        Output JSON path
    """
    specs = Spectrogram._read_file(bst_file)
    
    data3, meta3 = specs[0]
    data5, meta5 = specs[1]
    data7, meta7 = specs[2]
    
    # Optional downsampling (set to 1 to keep all data)
    
    times = meta3['times']
    
    # Convert to ISO format timestamps
    timestamps = [t.datetime.isoformat() for t in times]
    
    # Prepare JSON structure - all data preserved as-is
    json_data = {
        'metadata': {
            'start_time': meta3['start_time'].datetime.isoformat(),
            'end_time': times[-1].datetime.isoformat(),
            'duration_seconds': float((times[-1] - meta3['start_time']).sec),
            'time_resolution': 1.0,  # seconds
            'num_time_samples': len(timestamps),
            'original_file': os.path.basename(bst_file)
        },
        'bands': [
            {
                'name': 'mode3',
                'frequencies': meta3['freqs'].to_value('MHz').tolist(),
                'freq_unit': 'MHz',
                'freq_range': [
                    float(meta3['freqs'].to_value('MHz').min()),
                    float(meta3['freqs'].to_value('MHz').max())
                ],
                'num_channels': len(meta3['freqs']),
                'data': data3.tolist()  # [freq, time] - full precision
            },
            {
                'name': 'mode5',
                'frequencies': meta5['freqs'].to_value('MHz').tolist(),
                'freq_unit': 'MHz',
                'freq_range': [
                    float(meta5['freqs'].to_value('MHz').min()),
                    float(meta5['freqs'].to_value('MHz').max())
                ],
                'num_channels': len(meta5['freqs']),
                'data': data5.tolist()
            },
            {
                'name': 'mode7',
                'frequencies': meta7['freqs'].to_value('MHz').tolist(),
                'freq_unit': 'MHz',
                'freq_range': [
                    float(meta7['freqs'].to_value('MHz').min()),
                    float(meta7['freqs'].to_value('MHz').max())
                ],
                'num_channels': len(meta7['freqs']),
                'data': data7.tolist()
            }
        ],
        'timestamps': timestamps
    }
    
    with open(output_json, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    file_size_mb = os.path.getsize(output_json) / 1024 / 1024
    print(f" Saved to {output_json}")
    print(f" File size: {file_size_mb:.2f} MB")
    print(f" Time samples: {len(timestamps)}")
    print(f" Frequency channels: {data3.shape[0]} + {data5.shape[0]} + {data7.shape[0]}")
    
    return json_data

bst_to_json(x_dat_file, 'latest_spectrogram.json')

def plot_357_minimal(specs, start_min=0):
    """
    ILOFAR solar radio spectra plotting function using sunpy/radiospectra
    
    Parameters
    ----------
    specs : Spectogram 
        This is class created by Spectrogram factory containing observations and metadata
    start_min : int
        This was initially used along with a duration variable to plot chunks of spectra but functionality has changed since
    """
    if len(specs) != 3:
        raise ValueError("Need 3 bands")
    
    data3, meta3 = specs[0]
    data5, meta5 = specs[1]
    data7, meta7 = specs[2]
    
    
    endtime = (meta3['end_time']-meta3['start_time']).sec
    print(endtime)
    duration_min = endtime
    
    # Get time indices
    t = (meta7['times'] - meta3['start_time']).sec
    i0 = np.searchsorted(t, start_min * 60)
    i1 = np.searchsorted(t, (start_min + duration_min) * 60)
    
    # Slice data (shape: [freq, time])
    m3 = data3[:, i0:i1]
    m5 = data5[:, i0:i1]
    m7 = data7[:, i0:i1]

    
    
    # Apply log scaling FIRST (matching original)
    log_m3 = np.log10(np.maximum(m3, 1e-10))
    log_m5 = np.log10(np.maximum(m5, 1e-10))
    log_m7 = np.log10(np.maximum(m7, 1e-10))
    
    # Replace -inf with 0
    log_m3[np.isneginf(log_m3)] = 0
    log_m5[np.isneginf(log_m5)] = 0
    log_m7[np.isneginf(log_m7)] = 0
    
    # Flatten: compute median along TIME axis (axis=1) for each frequency channel
    bg3 = np.median(log_m3, axis=1, keepdims=True)
    bg5 = np.median(log_m5, axis=1, keepdims=True)
    bg7 = np.median(log_m7, axis=1, keepdims=True)
    
    # Avoid division by zero
    bg3[bg3 == 0] = 1.0
    bg5[bg5 == 0] = 1.0
    bg7[bg7 == 0] = 1.0
    
    # Divide each frequency channel by its background
    c_m3 = log_m3 / bg3
    c_m5 = log_m5 / bg5
    c_m7 = log_m7 / bg7

    vmin = np.percentile(c_m3, 0) 
    vmax = np.percentile(c_m3, 99.9)  
    
    # Time axis setup
    t0 = mdates.date2num(meta3['times'][i0].datetime)
    t1 = mdates.date2num(meta3['times'][i1-1].datetime)
    
    # Frequency arrays
    f3 = meta3['freqs'].to_value('MHz')
    f5 = meta5['freqs'].to_value('MHz')
    f7 = meta7['freqs'].to_value('MHz')
    
    
    ratios = [
        abs(f3.max() - f3.min()),
        abs(f5.max() - f5.min()),
        abs(f7.max() - f7.min())
    ]
    ratios = [r / sum(ratios) for r in ratios]
    
    
    norm = PowerNorm(gamma=0.9,vmin= vmin,vmax=vmax)
    

    fig = plt.figure(figsize=(10, 7))
    gs = gridspec.GridSpec(3, 2, width_ratios=[20, 1], height_ratios=ratios,
                          wspace=0.05, hspace=0.3)
    
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[2, 0])
    cax = fig.add_subplot(gs[:, 1])
    
    # Plot
    ax1.imshow(c_m3, norm=norm, origin='upper', aspect='auto',
              extent=[t0, t1, f3[-1], f3[0]])
    ax2.imshow(c_m5, norm=norm, origin='upper', aspect='auto',
              extent=[t0, t1, f5[-1], f5[0]])
    im = ax3.imshow(c_m7, norm=norm, origin='upper', aspect='auto',
                   extent=[t0, t1, f7[-1], f7[0]])
    
    # Colorbar
    cb = fig.colorbar(im, cax=cax)
    cb.set_label('Intensity', rotation=270, labelpad=15)
    
    # Format axes
    ax1.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    ax2.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    
    ax3.xaxis_date()
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    for ax in (ax1, ax2, ax3):
        ax.set_ylabel('Frequency (MHz)')
    
    fig.text(0.5, 0.04, 'Time (UTC)', ha='center', fontsize=11)
    fig.suptitle(f'ILOFAR Mode 357', fontsize=13)
    
    plt.tight_layout(rect=[0.03, 0.05, 0.95, 0.97])
    plt.show()

specs = Spectrogram._read_file(x_dat_file)
#plot_357_minimal(specs)

