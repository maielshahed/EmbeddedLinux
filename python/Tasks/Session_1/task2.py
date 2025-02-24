#write a Python program to test whether a passed letter is a vowel or not

passed_letter=['a','e','i','o','u','A','E','I','O','U']

text=input("Write passed letter:")

letter=text  in passed_letter


if letter:
    print("The letter that passed is  a vowel: " + str (text) )
else:
    print("The letter that passed is not a vowel: " + str (text))