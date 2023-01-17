"""Handles requests to and responses from OpenLibrary API."""

import requests
from colors import rand_pastel_color

API_BASE_URL = 'http://openlibrary.org/search.json'

def book_search(book_title, author):
    """Handle search form submission and return results to mylibrary view function in app.py.
    
    Results format:
    [
        {
            "author_name": author,
            "first_publish_year": year,
            "number_of_pages_median": pages,
            "subject": subject,
            "title": title,
            "color": color
        }, 
        ... 
    ]
    """
    # pass user inputs to search_entry function to handle different submissions: author only, title only, and author and title.
    response = search_entry(book_title, author)
   
    books = []

    # Format API response into list of dictionaries containing information on each book
    # Handle errors for when certain information is lacking from a search result.
    i = 0
    # grab results for first 50 books
    while i <= 50 :
        book = {}
        # Handling index and key errors for search results. 
        try:
            t = response.json()['docs'][i]['title']
        except (IndexError, KeyError):
            # Break loop when there's no more titles in API response (less than 50 books found)
            break
        try:
            # List the first 5 subjects listed for each book in API
            nums = [0,1,2,3,4]
            s = []
            for num in nums :
                subject = response.json()['docs'][i]['subject'][num]
                s.append(subject)
        except (IndexError, KeyError):
            # Not every book has 5 subjects, so pass if they run out
            pass
        try:
            n = str(response.json()['docs'][i]['number_of_pages_median'])
        except (IndexError, KeyError):
            n = "Not Found"
        try:
            a = response.json()['docs'][i]['author_name'][0]
        except (IndexError, KeyError):
            a = "Not Found"
        try:
            p = str(response.json()['docs'][i]['first_publish_year'])
        except (IndexError, KeyError):
            p = "Not Found"
        if bool(s) == False:
            s = "Not Found"

        color = rand_pastel_color()

        # create book dictionary from search results
        book["title"] = t
        book["author_name"] = a
        book["first_publish_year"] = p
        book["number_of_pages_median"] = n
        book["subject"] = s
        book["color"] = color
        print(book)
        books.append(book)
        i+=1
    return books

def search_entry(book_title, author):
    """Parse search entry submission and get response from API."""

    # search for book by title and author
    if len(book_title) > 0 and len(author) > 0:
        response = requests.get(API_BASE_URL, 
            params={'title': book_title, 'author': author})

    # search for book by title only
    elif len(book_title) > 0 and len(author) == 0:
        response = requests.get(API_BASE_URL, 
            params={'title': book_title})

    # search for book by author only
    elif len(book_title) == 0 and len(author) > 0:
        response = requests.get(API_BASE_URL,
            params={'author': author})

    return response