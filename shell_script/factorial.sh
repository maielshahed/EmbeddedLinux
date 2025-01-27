
#. Write a function in a shell script that calculates the factorial of a given number.
#!/bin/bash

factorial(){
num=$1   
fact=1

for (( i=1; i<=$num; i++ ))
do
fact=$(( fact * i ))
done
echo "The factorial of $num is: $fact"
}
read -p "Enter a number: " num

factorial $num