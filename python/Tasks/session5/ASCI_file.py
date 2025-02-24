'''
 Python program to get the ASCII value of a 
character.
'''

def ascii_value(x):
    value = ord(x)
    return value


ascii=input("Enter your charactere: ")
print(f"Hello, ASCII value of '{ascii}' character -->" , ascii_value(ascii))