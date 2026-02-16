#!/bin/bash
today=$(date +'%Y.%m.%d')
pathtodata="/home/ilofar/Monitor/monitor_dev/data_live/${today}"




curl -F "file=@${pathtodata}/latest_spectrogram.json" "https://lofar.ie/operations-monitor/post_json.php?img=latest_spectrogram.json"   
# ! Deprecated old code

# # Dynamic spectra.... X and Y
# echo "Sending Dynamic Spectra X polarization"
# i=1
# for f in $(ls -r $pathtodata/*X* | grep -v "lightcurve" | head -$n); do
#     echo "File $i-> $f"
#     curl -F file=@$f https://lofar.ie/operations-monitor/post_image.php?img=spectro${i}X.png
#     i=$((i+1))
# done



# echo "Sending Dynamic Spectra Y polarization"
# i=1
# for f in $(ls -r $pathtodata/*Y* | grep -v "lightcurve" | head -$n); do
#     echo "File $i-> $f"
#     curl -F file=@$f https://lofar.ie/operations-monitor/post_image.php?img=spectro${i}Y.png
#     i=$((i+1))
# done


# # Lightcurves ........X and Y
# echo "Sending Lightcurves X polarization"
# i=1
# for f in $(ls -r $pathtodata/*X*lightcurve* | head -$n); do
#     echo "File $i-> $f"
#     curl -F file=@$f https://lofar.ie/operations-monitor/post_image.php?img=lc${i}X.png
#     i=$((i+1))
# done

# echo "Sending Lightcurves Y polarization"
# i=1
# for f in $(ls -r $pathtodata/*Y*lightcurve* | head -$n); do
#     echo "File $i-> $f"
#     curl -F file=@$f https://lofar.ie/operations-monitor/post_image.php?img=lc${i}Y.png
#     i=$((i+1))
# done


