print("hello, world")
input_str = input("Enter a list of numbers separated by space: ")

numbers = [int(num) for num in input_str.split()]
print("The list of numbers is:", numbers)
