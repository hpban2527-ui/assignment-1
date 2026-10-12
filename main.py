def isPrime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

print("hello, world")
input_str = input("Enter a list of numbers separated by space: ")

numbers = [int(num) for num in input_str.split()]
print("The list of numbers is:", numbers)
num_to_check = 7
if isPrime(num_to_check):
    print(f"{num_to_check} is a prime number.")
else:
    print(f"{num_to_check} is not a prime number.")
