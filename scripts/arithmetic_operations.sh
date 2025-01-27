
#How can you use arithmetic operations within a shell script?
#!/bin/bash
 
read -p "Enter a number:" num1
read -p "Enter a smaller number:" num2
read -p "Enter an operand:" op


if [[ $op == "+" ]]
then
    result=$(( num1 + num2 ))
    echo "Addition: $num1 + $num2 =" $result
elif [[ $op == "-"  ]]
then
    result=$(( num1 - num2 ))
    echo "Subtraction: $num1 - $num2 =" $result
elif [[  $op == "*" ]]
then 
    result=$(( num1 * num2 ))
    echo "Multiplication: $num1 * $num2 =" $result 
elif [[  $op == "/" ]]
then 
    result=$(( num1 / num2 ))
    echo "Divisio: $num1 / $num2 =" $result 
elif [[  $op == "%" ]]
then 
    
    result=$(( num1 % num2 ))
    echo "Modulus: $num1 % $num2 =" $result     
   
else
    echo "Invalid operator."
fi

