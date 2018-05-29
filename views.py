#!/usr/bin/python2

from models import Base, CatalogItem, Catalog
from flask import Flask
from flask import jsonify, url_for, abort, g, render_template
from flask import make_response, request, redirect
from flask import session as login_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, join
from sqlalchemy import create_engine
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
import json


# Creating SQLAlchemy engine and session for SQLLite DB "Catalog"
engine = create_engine("sqlite:///catalog.db")

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

# Load Client ID from file
CLIENT_ID = json.loads(
    open("client_secrets.json", "r").read())["web"]["client_id"]


# Home Page
@app.route("/")
def home():

    # Searching for top 10 items added recently, sorted by earliest date first
    latest_items = session.query(CatalogItem).join(Catalog).add_columns(CatalogItem.title, Catalog.name, CatalogItem.date_added).order_by(CatalogItem.date_added.desc()).limit(10).all()  # noqa

    name = ""
    if "name" in login_session:
        name = login_session["name"]

    return render_template("latest.html", items=latest_items, name=name)


# List of items within a certain category
@app.route("/catalog/<category>/items")
def load_items(category):

    # Searching for all items within a particular category specified in URL
    category_items = session.query(CatalogItem).join(Catalog).add_columns(CatalogItem.title, Catalog.name).filter_by(name=category).all()   # noqa

    name = ""
    if "name" in login_session:
        name = login_session["name"]

    return render_template(
        "itemlist.html", items=category_items,
        category=category, name=name
    )


# Viewing the details of a certain item
@app.route("/catalog/<category>/<item>")
def view_item(category, item):

    # Searching for a specific item and joining with category info
    certain_item = session.query(CatalogItem).filter_by(title=item).join(Catalog).add_columns(CatalogItem.title, CatalogItem.description, Catalog.name).filter_by(name=category).one()  # noqa

    name = ""
    if "name" in login_session:
        name = login_session["name"]

    return render_template("itempage.html", item=certain_item, name=name)


# Adding a new item
@app.route("/catalog/add", methods=["GET", "POST"])
def add_item():

    # Checks if user is logged in
    if "name" in login_session:
        if request.method == "POST":
            # Searching for a category
            new_category = session.query(Catalog).filter_by(name=request.form["category"]).one()    # noqa

            # Creating new catalog item object
            new_item = CatalogItem(
                title=request.form["title"],
                description=request.form["description"],
                cat_id=new_category.id,
                creator_email=login_session["email"]
            )

            session.add(new_item)
            session.commit()

            # Redirect to new item added
            return redirect(url_for(
                "view_item", category=request.form["category"],
                item=request.form["title"]
            ))
        else:
            categories = session.query(Catalog).all()
            return render_template("additem.html", categories=categories)
    else:
        return "Login required!"


# Editing a certain item
@app.route("/catalog/<item>/edit", methods=["GET", "POST"])
def edit_item(item):

    # Checks if user is logged in
    if "name" in login_session:
        if request.method == "POST":
            # Searching for a certain item
            edited_item = session.query(CatalogItem).filter_by(title=item).one()    # noqa
            edited_item.title = request.form["title"]
            edited_item.description = request.form["description"]

            # Searching for a category
            new_category = session.query(Catalog).filter_by(name=request.form["category"]).one()    # noqa

            edited_item.cat_id = new_category.id
            session.add(edited_item)
            session.commit()

            # Redirect to item edited
            return redirect(url_for(
                "view_item", category=request.form["category"],
                item=request.form["title"]
            ))
        else:
            # Searching for a certain item and joining with category info
            certain_item = session.query(CatalogItem).filter_by(title=item).join(Catalog).add_columns(CatalogItem.title, CatalogItem.description, Catalog.name, CatalogItem.creator_email).one()    # noqa

            categories = session.query(Catalog).all()
            return render_template(
                "edititem.html", item=certain_item,
                categories=categories, email=login_session["email"]
            )
    else:
        return "Login required!"


# Deleting an item
@app.route("/catalog/<item>/delete", methods=["GET", "POST"])
def delete_item(item):

    # Checks if user is logged in
    if "name" in login_session:
        if request.method == "POST":

            # Searching for the item to delete
            deletion_item = session.query(CatalogItem).filter_by(title=item).one()  # noqa

            session.delete(deletion_item)
            session.commit()

            return redirect(url_for("home"))
        else:
            # Searching for item to delete
            certain_item = session.query(CatalogItem).filter_by(title=item).join(Catalog).add_columns(CatalogItem.title, CatalogItem.description, Catalog.name, CatalogItem.creator_email).one()    # noqa

            return render_template(
                "deleteitem.html", item=certain_item,
                email=login_session["email"]
            )
    else:
        return "Login required!"


# JSON Endpoint
@app.route("/catalog.json")
def catalog_to_json():

    # Searching for all categories
    categories = session.query(Catalog).all()
    combined_json = []

    # Creating dictionary to jsonify
    for i in categories:
        json_dict = i.serialize
        items = session.query(CatalogItem).filter_by(cat_id=json_dict["id"]).all()  # noqa
        json_dict["item"] = [j.serialize for j in items]
        combined_json.append(json_dict)

    return jsonify(category=combined_json)


# OAuth Signout
@app.route("/signout")
def signout():

    # Popping all current session variables before logout
    login_session.pop("name", None)
    login_session.pop("picture", None)
    login_session.pop("email", None)

    return "success"


# OAuth Signin
@app.route("/oauth/<provider>", methods=["POST"])
def login(provider):

    # Receving the auth code
    auth_code = request.data

    # Exchanging auth code for a token
    if provider == "google":
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(
                "client_secrets.json", scope=""
            )
            oauth_flow.redirect_uri = "postmessage"
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(
                json.dumps("Failed to upgrade the authorization code."), 401
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s" % access_token)     # noqa
        h = httplib2.Http()
        result = json.loads(h.request(url, "GET")[1])

        # If there was an error in the access token info, abort.
        if result.get("error") is not None:
            response = make_response(json.dumps(result.get("error")), 500)
            response.headers["Content-Type"] = "application/json"

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token["sub"]
        if result["user_id"] != gplus_id:
            response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)   # noqa
            response.headers["Content-Type"] = "application/json"
            return response

        # Verify that the access token is valid for this app.
        if result["issued_to"] != CLIENT_ID:
            response = make_response(json.dumps("Token's client ID does not match app's."), 401)    # noqa
            response.headers["Content-Type"] = "application/json"
            return response

        print("Step 2 Complete! Access Token : %s " % credentials.access_token)

        # Get user info
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": credentials.access_token, "alt": "json"}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session["name"] = data["name"]
        login_session["picture"] = data["picture"]
        login_session["email"] = data["email"]

        return jsonify({"token": credentials.access_token})
    else:
        return "Unrecoginized Provider"


if __name__ == "__main__":
    app.debug = True
    app.secret_key = "super_secret_key"
    app.run(host="0.0.0.0", port=5000)
