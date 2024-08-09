
def calculateNumbersOfPassegers(number_of_adults, number_of_children):
    if number_of_children <= 1 :
        number_of_children = 0 
    elif number_of_children == 2 :
        number_of_children = 1
    return number_of_adults + number_of_children
