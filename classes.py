# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 22:34:40 2019

@author: dteno
"""

#classes to help organize all of the information
class Vote:
    """
    represents the information of interest for a single vote. 
    multiple votes can occur on the same bill (and potentially on the same day), 
    so the .link attribute is the only guaranteed unique piece of information
    """
    def __init__(self):
        self.date = ""
        self.name = ""
        self.desc = ""
        self.result = ""
        self.link = ""
        
    def __repr__(self):
        return repr([self.link,self.name,self.desc,self.result,self.date])
        

class Councillor:
    """
    represents the votes taken by an individual councillor, along with information
    about that councillor
    """
    def __init__(self, name="", votes = {}, district = "", years_active = set()):
        self.name = name
        self.votes = votes #key = vote link, value = vote (Pass/Fail/Excused)
        self.district = district
        self.years_active = years_active
        
    def __repr__(self):
        return repr([self.name,self.votes])
