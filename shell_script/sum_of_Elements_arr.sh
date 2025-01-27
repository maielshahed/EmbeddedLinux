#Write a script to calculate the sum of Elements in an Array

#!/bin/bash
echo "Enter an array of numbers (separated by space):"

read -a arr
sum=0
#tot=0
for i in  ${arr[@]}; do

sum=$((sum+i))
#Another way to calculate the sum of numbers in a array
#let tot+=$i
done
echo "Total: $sum"
#echo "Total: $tot"