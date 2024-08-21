
from random import randint, choices
from string import ascii_uppercase

def generateBookingId():
  """Generates a unique string ID starting with 'BK-' followed by a 7-digit number divisible by 6 with alternating even/odd digits.

  Returns:
      str: The unique string ID.
  """
  while True:
    # Generate a random 7-digit number
    number = randint(1000000, 9999999)

    # Check if divisible by 6
    if number % 6 == 0:
      # Extract digits as a string
      digits = str(number)

      # Check for alternating even/odd pattern
      is_even_start = int(digits[0]) % 2 == 0
      is_valid = True
      for i in range(1, len(digits)):
        if (is_even_start and int(digits[i]) % 2 == 0) or (not is_even_start and int(digits[i]) % 2 != 0):
          is_valid = False
          break
      
      if is_valid:
        alphabet = choices(ascii_uppercase,k=3)
        return f"BK-{number}{alphabet[0]+alphabet[2]+alphabet[1]}"
      

def generateGuestBookingId():
  """Generates a unique string ID starting with 'GST-' followed by a 7-digit number divisible by 6 with alternating even/odd digits and end with BK.

  Returns:
      str: The unique string ID.
  """
  while True:
    # Generate a random 7-digit number
    number = randint(1000000, 9999999)

    # Check if divisible by 6
    if number % 6 == 0:
      # Extract digits as a string
      digits = str(number)

      # Check for alternating even/odd pattern
      is_even_start = int(digits[0]) % 2 == 0
      is_valid = True
      for i in range(1, len(digits)):
        if (is_even_start and int(digits[i]) % 2 == 0) or (not is_even_start and int(digits[i]) % 2 != 0):
          is_valid = False
          break
      
      if is_valid:
        alphabet = choices(ascii_uppercase,k=3)
        return f"GST-{number}{alphabet[0]+alphabet[2]+alphabet[1]}-BK"
      
