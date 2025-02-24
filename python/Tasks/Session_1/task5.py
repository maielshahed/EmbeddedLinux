#Print the calendar of a given month and year
# Program to display calendar of the given month and year

# importing calendar module
import calendar

# To take month and year input from the user
year = int(input("Enter year: "))
manth = int(input("Enter month: "))

# display the calendar
print(calendar.month(year, manth))