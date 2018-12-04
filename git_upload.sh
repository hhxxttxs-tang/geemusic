#!/bin/bash
target_dir=/geemusic
file_list=$(git status -s|grep -w M|cut -d' ' -f3)
#echo $file_list
for i in $file_list
do
    if [ "$i" != "Dockerfile" ]; then
        echo "UPLOADING file to docker:" $i
        #echo "target_file=" $target_dir/$i
        docker cp $i f596b2628559:$target_dir/$i
	fi
done
