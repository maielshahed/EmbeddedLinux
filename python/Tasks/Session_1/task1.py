#Write a Python program to count the number 4 in a given list
four=[1,4,3,4,7,8]
print(4 in four)
count=0

for num in four:
    if num == 4:
        count = count + 1
        
        
print(count)