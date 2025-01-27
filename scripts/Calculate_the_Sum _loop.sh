

#!/bin/bash

#Write a shell script that calculates the sum of integers from 1 to N using a loop.


read -p "Enter a number: " num
sum=0
for (( x=1 ; x  <= num ; x++))
do
echo $sum + $x = $(( sum + x ))
sum=$(( sum + x ))

done
echo "Calculate the sum of integers from 1 to N=$num ="$sum
chmod +x Calculate_the_Sum _loop.sh