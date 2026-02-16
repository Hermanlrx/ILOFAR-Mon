from radiospectra.spectrogram import Spectrogram 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import gridspec
from matplotlib.colors import PowerNorm, LogNorm
import json
from pathlib import Path
import os
import sys
import datetime


def get_mtime(path):
    return path.stat().st_mtime


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
    specs.plot()
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
    print(f" File size: {file_size_mb:.2f} MB")
    
    return json_data



if __name__ == "__main__":

    
    debugg = 1
    t_start =datetime.datetime.now()

    if len(sys.argv) >= 2:
        filename = sys.argv[1]  # path to data file
    else:
        filename = "data/20200602_071428_bst_00X.dat"  # this is for testing
    
    NEWOBS = Path(filename)
    

    x_dat_files = sorted(
        NEWOBS.glob("*00X.dat"),
        key=get_mtime,
        reverse=True   
    )

    x_dat_file = x_dat_files[0]
    
    # Default output directory is ./monitor/YYYY.MM.DD
    # otherwise manually add output directory
    if len(sys.argv) <= 2:
        # Get date from file to create directory
        specs = Spectrogram._read_file(x_dat_file)
        _, meta = specs[0]
        t0 = meta['start_time']
        output_dir = os.getcwd() + '/monitor/' + str(t0.datetime.year) + '.' + str(t0.datetime.month).zfill(2) + '.' + str(t0.datetime.day).zfill(2)
    else:
        output_dir = sys.argv[2]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Convert to JSON
    output_json = os.path.join(output_dir, 'latest_spectrogram.json')
    bst_to_json(x_dat_file, output_json)


    t_end = datetime.datetime.now()

    if debugg == 1:
        print("lofar monitor: ")
        print("Start:  " +str(t_start))
        print("End:    " +str(t_end))
        print("Time elapsed:  " +str(t_end-t_start))