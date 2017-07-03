#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 14:38:37 2017

@author: markhorvath
"""
#import Flask class from flask
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
#create an instance of FLask class with the name of the running application as the argument
#anytime we run an application in python, a special variable called 'name' gets defined for the
#application and all the imports it uses

#the application run by the python interpreter gets a name variable set to '__main__'
#whereas all the other imported python files get a '__name__' variable set to the
#actual name of the python file
app = Flask(__name__)

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#making an API endpoint (GET request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = 
            restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def oneMenuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItem=[item.serialize])
#the @ indicated a 'decorator', essentially wraps our function inside the app.route function that 
#flask has already created, so if either of the two following 'routes' (ie '/' or '/hello') get sent
#from the browser the function below would get called
@app.route('/')
@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant = restaurant, items = items)

@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = MenuItem(name = request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash(request.form['name'] + ' added to Restaurants!')
        return redirect(url_for('restaurants'))
    else:
        return render_template('newrestaurant.html')

# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash(request.form['name'] + ' added to the menu!')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash('Menu item succesfully edited!')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id,
            item=editedItem)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', 
           methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item deleted from the menu!')
        #flash(itemname + ' deleted from the menu!')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template(
                'deletemenuitem.html', restaurant_id=restaurant_id, menu_id=
                menu_id, item=itemToDelete)

#the if statement here makes sure the server runs only if the script is executed directly form the python interpreter,
#and not used as an imported module, so basically if you execute this from the python interpreter then run the server,
#but if youre importing it then dont
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    #runs the local server with our application
    app.run(host = '0.0.0.0', port = 5000)
    
