#!/bin/bash

: << 'COMMENT'
 ILOFAR MONITOR

  SUPPORTS
  357 Solar Observations
  357 w/ REALTA Solar Observations

  Uses a data buffer folder to get the data from the LCU. Every 10 mins it syncs using rsync.
  If it cant sync means observation isnt on or station is in international mode and will wait 30 mins.

  USES lofar_monitor.py to generate Dynamic spectra which is then sent to a webserver(done inside python)
  Generates logs from CPU status and station status and sends them  to webserver.

  RUN this using tmux.
  to run tmux:

  # NEW Tmux session
    tmux new -s monitor
  # in tmux ... run script
    ./monitor.sh
  # use ctrl+b d  to dettach
  # to reattach to the session
    tmux attach -t monitor


  NEEDS:
  lofar_monitor.py
  lofar_bst.py
  authors: Alberto Canizares  - canizares (at) cp.dias.ie
           Jeremy Rigney - jeremy.rigney (at) dias.ie
COMMENT

set -x

day="0"

# this is a test
while true
do
	#source activate monitor_env

	daynow=$(date +%e | sed 's/ //g')
	if ((day !=  daynow))
		echo day
	then
		echo "new day"

		# ! Old code
		#curl -F file=@/home/ilofar/Monitor/NoData/LC_NO_DATA.png https://lofar.ie/operations-monitor/post_image.php?img=lc${i}X.png
		#curl -F file=@/home/ilofar/Monitor/NoData/LC_NO_DATA.png https://lofar.ie/operations-monitor/post_image.php?img=lc${i}Y.png

		#curl -F file=@/home/ilofar/Monitor/NoData/SPEC_NO_DATA.png https://lofar.ie/operations-monitor/post_image.php?img=spectro${i}X.png
		#curl -F file=@/home/ilofar/Monitor/NoData/SPEC_NO_DATA.png https://lofar.ie/operations-monitor/post_image.php?img=spectro${i}Y.png

		curl -v -F "file=@latest_spectrogram.json" "https://lofar.ie/operations-monitor/post_json.php?img=latest_spectrogram_test.json"  
		rm -rf ~/Monitor/monitor_dev/data_buff/
		
	fi

	today=$(date +'%Y.%m.%d')
	day=$(date +%d)
	
	mkdir -p  ~/Monitor/monitor_dev/data_buff/$today

	# # # # # # # # # #
	# Directories     #
	# # # # # # # # # #
	og_data_source="lcu:/data/home/user1/data/kbt/rcu357_1beam/${today}/*00?.dat"
	realta_data_source="lcu:/data/home/user1/data/kbt/rcu357_1beam_datastream*/${today}/*00?.dat"
	monitor_temp_data=~/"Monitor/monitor_dev/data_buff/${today}"
	python_dir=~/"Scripts/Python/MonitorRealtime_dev/"
	test_dir=~/"Monitor/monitor_dev/data_live/${today}"
	YYYY=$(date +'%Y')
	MM=$(date +'%m')
	DD=$(date +'%d')
	echo $today
	ls -ld ~/Scripts/Python/MonitorRealtime
	ls -l  ~/Scripts/Python/MonitorRealtime/main.py
	ls -ld "${monitor_temp_data}/datastream/"
	ls -ld "${test_dir}"

	echo " "
	echo $(date)
	# ! This code is important for the current functionality of the calendar used for archived data
	# populates folders in Data folder with javascript files for the calendar to know the names of the figures that will be used. 	
	#python3 addtoscript.py
	curl -F file=@/home/ilofar/Data/IE613/monitor/dates_calendar.js https://lofar.ie/operations-monitor/post_log.php?js=dates_calendar

		# ? confirm whether status code is actually working properly
       # python3 update_antenna_status.py #/home/ilofar/Monitor/
       # curl -F file=@HBA_numbers.txt https://lofar.ie/operations-monitor/post_log.php?txt=HBA_numbers
       # curl -F file=@LBA_numbers.txt https://lofar.ie/operations-monitor/post_log.php?txt=LBA_numbers	

        
        if rsync -ahP $og_data_source $monitor_temp_data | grep -q '.dat'; then
		echo "Upload succeeded"
      		newestfile=$(ls -Art ${monitor_temp_data}/ | tail -n 1)
		/home/ilofar/.local/bin/uv run /home/ilofar/Scripts/Python/MonitorRealtime_dev/MonitorRealtime/main.py ${monitor_temp_data} ${test_dir}/$today
                

		# ? confirm whether status code is actually working properly
		
		# # # # # # # # # #
		# STATUS REPORT   #
		# # # # # # # # # #		  
		# LGC   
		echo 'LGC STATUS' > status_lgc.txt
		date >> status_lgc.txt
		sensors >> status_lgc.txt
		# #LCU
		echo 'LCU STATUS' > status_lcu.txt
		date >> status_lcu.txt
		ssh lcu 'rspctl --status' >> status_lcu.txt
	
        echo "lofar monitor generated a preview."
        echo ""
		./sendtomonitor.sh

	elif rsync -ahP $realta_data_source $monitor_temp_data/datastream | grep -q '.dat'; then
		echo "Upload succeeded. Realta is working."
		newestfile=$(ls -Art ${monitor_temp_data}/datastream/ | tail -n 1)
       	       uv run --project ~/Scripts/Python/MonitorRealtime_dev/MonitorRealtime python ~/Scripts/Python/MonitorRealtime_dev/MonitorRealtime/main.py ~/Monitor/monitor_dev/data_buff/${today}/datastream/ ~/Monitor/monitor_dev/data_live/${today}/

		
		# # # # # # # # # #
		# STATUS REPORT   #
		# # # # # # # # # #		  
		# LGC   
		echo 'LGC STATUS' > status_lgc.txt
		date >> status_lgc.txt
		sensors >> status_lgc.txt
		#LCU
		echo 'LCU STATUS' > status_lcu.txt
		date >> status_lcu.txt
		ssh lcu 'rspctl --status' >> status_lcu.txt

		echo "lofar monitor generated a preview."
		./sendtomonitor.sh
        echo ""
	else
		# # # # # # # # # #
		# STATUS REPORT   #
		# # # # # # # # # #		  
		# LGC   
		echo 'LGC STATUS' > status_lgc.txt
		date >> status_lgc.txt
		sensors >> status_lgc.txt
		#LCU
		echo 'LCU STATUS' > status_lcu.txt
		date >> status_lcu.txt
		echo "LCU IN INTERNATIONAL MODE" >> status_lcu.txt

    		#echo "Upload failed. Try in half an hour"
		#sleep 1200
	fi


	# send logs
	echo "sending logs to webserver"
	curl -F file=@status_lcu.txt https://lofar.ie/operations-monitor/post_log.php?txt=status_lcu
	curl -F file=@status_lgc.txt https://lofar.ie/operations-monitor/post_log.php?txt=status_lgc
	echo "logs sent correctly"
        
        echo " sleep 1 mins"
	#wait 10 mins
	sleep 60

set +x
	
done