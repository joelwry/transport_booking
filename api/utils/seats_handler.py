
def calculateNumbersOfPassegers(number_of_adults, number_of_children) -> int:
    '''
        helps to return the total number of people based on a counting form . 1 child below 10 counts as 0 , while 2 childs counts as 1 otherwise normal counting applies for children ranging from 3 upwards 
    '''
    if number_of_children <= 1 :
        number_of_children = 0 
    elif number_of_children == 2 :
        number_of_children = 1
    return number_of_adults + number_of_children
