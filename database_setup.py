#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 17:11:34 2017

@author: markhorvath
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 17:37:23 2017

@author: markhorvath
"""

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurant'
    name = Column(
            String(80), nullable = False)
    
    id = Column(
            Integer, primary_key = True)
    

class MenuItem(Base):
    __tablename__ = 'menu_item'
    
    name = Column(
            String(80), nullable = False)
    
    id = Column(Integer, primary_key = True)
    
    course = Column(String(250))
    
    description = Column(String(250))
    
    price = Column(String(8))
    
    restaurant_id = Column(
            Integer, ForeignKey('restaurant.id'))
    
    restaurant = relationship(Restaurant)
    
    @property
    def serialize(self):
    #returns object data in easily serealizable format
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }

###must be at end of file###

engine = create_engine(
        'sqlite:///restaurantmenu.db')

Base.metadata.create_all(engine)