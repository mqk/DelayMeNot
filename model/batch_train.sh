#!/bin/bash

while read -r destination Nflights;
do
     if [ ${destination:0:1} == '#' ]
     then
         continue
     fi

     echo "Training Random Forest model on Destination=$destination"

     python run_model_RandomForest_destination.py $destination --min_Nflights=0

     echo
     echo

done < destination_list.txt

# for origin in $(cat origin_list.txt)
# do
#     if [ ${origin:0:1} == '#' ]
#     then
#         continue
#     fi

#     echo "Training Random Forest model on Origin=$origin"

#     python run_model_RandomForest.py $origin --min_Nflights=0

#     echo
#     echo
# done
