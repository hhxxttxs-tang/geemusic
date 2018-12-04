#!/bin/bash
target_dir=/geemusic_my_fork
#file_list=$(git status -s|grep -w M|cut -d' ' -f3)
file_list=$(git status -s|grep -E -w 'A|M|MM'|awk '{print $NF}')


#echo $file_list
for i in $file_list
do
    if [ "$i" != "Dockerfile" ]; then
        echo "UPLOADING file to docker:" $i
        #echo "target_file=" $target_dir/$i
        docker cp $i test_gee_portmapping:$target_dir/$i
	fi
done
