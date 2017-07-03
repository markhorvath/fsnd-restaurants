#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 11:59:03 2017

@author: markhorvath
"""
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from sqlalchemy import func

from sqlalchemy import Sequence

from database_setup import Base, Restaurant, MenuItem
import datetime

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#common gateway interface
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')

DBSession = sessionmaker(bind=engine)

session = DBSession()

def get_restaurants():
    results = session.query(Restaurant.name, Restaurant.id).order_by(Restaurant.id).all()
    return results

def add_restaurant(new):
    restaurant1 = Restaurant(name = new)
    session.add(restaurant1)
    session.commit()
    
#handler section indicates what code to execute based on type of HTTP request sent to server (ie GET, POST, PUT, DELETE, etc)
#defines webserverHandler class called in HTTPserver, extends from class BaseHTTPRequestHandler
class webserverHandler(BaseHTTPRequestHandler):
    #Handles all GET requests our server receives
    def do_GET(self):
        #uses simple pattern-matching to look for ending of URL PATH
        try:
            #path is a variable of BaseHTTPRequestHandler that contains string of URL, endswith is a method
            if self.path.endswith("/restaurant"):
                #send response code of 200 indicated successful request
                self.send_response(200)
                #indicates that server will be replying with text in the form of html
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                #data that gets sent back
                output = ""
                output += "<html><body>"
                output += "<h2>Restaurants</h2>"
                results = get_restaurants()
                for restaurant in results:
                    output += "<h4 style='margin:1'>" + restaurant[0] + "</h4>"
                    output += "<a href=' /restaurant/%s/edit' >Edit</a><br>" % restaurant.id
                    output += "<a href=' /restaurant/%s/delete' >Delete</a><br>" % restaurant.id
                    
                output += "<h2><a href='/new'>Add a New Restaurant Here</a></h2>"
                output += "</body</html>"
                #wfile is an instance variable containing the output string to be sent back to the clien
                #while .write() is what writes the data to the wfile (i think), in this case its the value of output
                self.wfile.write(output)
                return
                
            if self.path.endswith("/new"):
                #send response code of 200 indicated successful request
                self.send_response(200)
                #indicates that server will be replying with text in the form of html
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                #data that gets sent back
                output = ""
                output += "<html><body>"
                output += "<h2>Make A New Restaurant</h2>"
                output += "<form method='POST' enctype='multipart/form-data' action='/new'><h4>Enter the \
                name of your new restaurant: </h4><input name='new-restaurant' type='text'><input type='submit' \
                value='Submit' > </form>"
                output += "</body</html>"
                #wfile is an instance variable containing the output string to be sent back to the clien
                #while .write() is what writes the data to the wfile (i think), in this case its the value of output
                self.wfile.write(output)
                return
            
            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
                #send response code of 200 indicated successful request
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>" + myRestaurantQuery.name + "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data'\
                    action='/restaurants/%s/edit' >" % restaurantIDPath
                    output += "<input name = 'new-restaurant' type='text' \
                    placeholder = '%s' >" % myRestaurantQuery.name
                    output += "<input type= 'submit' value='rename'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)
            
            if self.path.endswith('/delete'):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    output = ""
                    output += "<html><body>"
                    output += "<h2>Are you sure you want to delete %s?</h2>" % myRestaurantQuery.name
                    output += "<form method='POST' enctype='multipart/form-data' action='restaurant/%s/delete'>" \
                    % restaurantIDPath
                    "<input type='submit' value='Delete' ></form>"
                    output += "</body</html>"
                    self.wfile.write(output)

        #https://docs.python.org/2/library/exceptions.html#exceptions.IOError
        except IOError:
            self.send_error(404, "File not found %s" % self.path)
    
    def do_POST(self):
        try:
            if self.path.endswith('/new'):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                #check if this is form data being received
                if ctype == 'multipart/form-data':
                    
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('new-restaurant')
                    print messagecontent
                    #now that POST request received, tell client what to do with info received
                    add_restaurant(messagecontent[0])
    
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurant')
                    self.end_headers()
            
            if self.path.endswith('/edit'):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                #check if this is form data being received
                if ctype == 'multipart/form-data':
                    
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('new-restaurant')
                    restaurantIDPath = self.path.split("/")[2]
                    myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurant')
                        self.end_headers()
                    
            if self.path.endswith('/delete'):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
                if myRestaurantQuery != []:
                        session.delete(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurant')
                        self.end_headers()
        except:
            pass
        
#main method instantiates the server and tells what port to listen on
def main():
    try:
        port = 8080
        #('',port) is a tuple that contains host and port number for server
        #https://docs.python.org/2/library/basehttpserver.html#module-BaseHTTPServer for more info
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        #runs the server until close()
        server.serve_forever()
        
    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        #https://docs.python.org/2/library/socket.html
        server.socket.close()
        
#placed at end to immediately run the main method when python interpreter executes script
if __name__ == '__main__':
    main()