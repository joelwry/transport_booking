#from django.test import TestCase

# Create your tests here.
password1 = 'r95'
password2 = 'r95'
if not password1 or not password2 or password1 != password2:
    raise Exception("Passwords do not match.")
print("All okay")    

print('08023459340'.isdigit())