from django import template

register = template.Library()

@register.filter(name='seat_state')
def seat_state(position, booked_seats):
    if position in booked_seats:
        return "bg-danger"
    else:
        return "bg-black"
