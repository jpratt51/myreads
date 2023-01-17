"""Generates random colors for use in myreads app."""

from random import choice

def rand_pastel_color():
    """Assign random pastel color to book."""
    colors = ['rgb(172, 236, 174)', 'rgb(246, 237, 179)', 'rgb(176, 227, 234)', 'rgb(203, 185, 254)', 'rgb(253, 194, 235)', '#F8DECB', 'rgb(248, 222, 203)', 'rgb(251, 203, 156)', 'rgb(247, 243, 203)', 'rgb(205, 235, 204)', 'rgb(179, 171, 207)', 'rgb(223, 192, 224)']
    rand_color = choice(colors)
    return rand_color

def rand_primary_color():
    """Assign random primary color to bookshelf."""
    colors = ['#ff0000', '#ffa500', '#ffff00', '#008000', '#0000ff', '#4b0082', '#ee82ee']
    rand_color = choice(colors)
    return rand_color

def rand_dark_color():
    """Assign random dark color to favorite author."""
    colors = ['#161d20', '#36498f', '#2d7c9d', '#a4a29e', '#cccccc']
    rand_color = choice(colors)
    return rand_color

def rand_universe_color():
    """Assign random universe color to favorite subject."""
    colors = ['#05f9fb', '#f9ad7e', '#109fac', '#63949c', '#c9b0b9', '#1c1c34']
    rand_color = choice(colors)
    return rand_color