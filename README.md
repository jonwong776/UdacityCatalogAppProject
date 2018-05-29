# Catalog App Project

The Udacity Catalog App Project for the Full Stack Web Developer Nanodegree. This program at run time will start up a Flask webserver and serve up a website that can be visited. This website acts as a catalog system where a user can browse various item categories and items and if logged in via Google, can also edit, add, and delete items. 

## Description of Files

1. views.py
    - Main file container the web server and Flask framework
2. models.py
    - File container the SQLAlchemy ORM for the Catalog and CatalogItem tables.
3. catalog.db
    - SQLLite database containing sample data.
4. client_secrets.json
    - JSON file containing necessary details for Google OAuth.
5. templates (Folder)
    - Folder containing all the Jinja HTML templates for Flask.
    - Contains the files:
        - main.html
            - HTML file containing the reusable portions of every webpage.
        - latest.html
            - HTML file containing the home page showing the latest items.
        - deleteitem.html
            - HTML file containing the delete item confirmation page.
        - itempage.html
            - HTML file containing the details of a specific item.
        - additem.html
            - HTML file containing the add item page.
        - edititem.html
            - HTML file containing the edit item page.
        - itemlist.html
            - HTML file containing the list of items within a category.
6. static (Folder)
    - Folder containing the CSS file for all the HTML files in the templates folder.
    - Contains the files:
        - main.css
            - CSS file that provides the styling for the HTML files in the templates folder.

## Prerequisites/Installation

1. Ensure that you have all the files listed in the above section placed in a folder accessible by the Udacity fullstack-nanodegree-vm Vagrant VM.
2. Power up the Udacity fullstack-nanodegree-vm Vagrant VM and SSH in.

## Running the Program

1. In the commandline of the Udacity fullstack-nanodegree-vm Vagrant VM, type in `python2 views.py` to start the Flask server.
2. Visit the website at http://localhost:5000.
