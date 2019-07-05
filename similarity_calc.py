# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 21:29:20 2019

@author: dteno
"""

import pandas as pd
import collections
import seaborn as sns
import numpy as np
from matplotlib import pyplot

def clr_dict_getter(df):
    """
    takes in a pandas DataFrame containing vote information
    and returns a nested dictionary of the following format:
        
    {
    CLR_NAME-1: { VOTE-1-URL:ACTION-TAKEN-1
                VOTE-2-URL:ACTION-TAKEN-2
                ...
                }
    CLR_NAME-2: { VOTE-1-URL:ACTION-TAKEN-1
                VOTE-2-URL:ACTION-TAKEN-2
                ...
                }
    ...
    }
    """    
    rows = df.shape[0]
    cols = df.shape[1] #number of unique votes taken
    
    #nested dictionary to hold relations between each councilor
    clr_dict = collections.defaultdict(dict)
    
    #sets to determine other statistics
    unanimous = set()
    passed = set()
    
    for col in range(1,cols):
        #holds the number of unique acitons, to determine if the vote is unanimous
        uniq_actions = set()
        
        #storing all hte different pieces of information
        link = df.iloc[0,col]
        name = df.iloc[1,col]
        desc = df.iloc[2,col]
        date = df.iloc[3,col]
        result = df.iloc[4,col]
        
        #store number of votes that have been passed
        if result == 'Pass':
            passed.add(link)
        
        #now, get the action from each councilor who voted on a particular bill
        for row in range(5,rows):
            cell_info_raw = df.iloc[row,col]
            
            #need to pass over N/A values, for votes with a subset of the full council
            try:
                cell_info = cell_info_raw.split("|")
            except:
                continue
            
            clr_name = cell_info[0]
            #the enye can be stored weirdly, so we have to account for that
            if "Klarissa" in clr_name:
                clr_name = "Klarissa J. Pena"
           
            action = cell_info[1]
            
            #store the action this councilor took on this bill
            clr_dict[clr_name][link] = action
            
  
            uniq_actions.add(action)
        
        
        
        if len(uniq_actions) == 1:
            unanimous.add(link)
            
    #percentage of unanimous votes
    unanimous_pct = len(unanimous) / cols 
    #percentage of votes that passed
    passed_pct = len(passed) / cols
    
    
    return clr_dict, unanimous


def sim_calc(clr_dict,unan_set):
    """
    takes in a nested dictionary of Councilor names + votes + action taken
    on each vote
    
    and calculates the percentage of votes in common between each pair of
    councilors
    
    sim_calc returns a dictionary holding that score for each pair of 
    councilors
    
    """
    
    
    names = clr_dict.keys()
    sim_dict = collections.defaultdict(dict)
    
    #subscript 1 for the original councilor 
    #subscript 2 for the councilor being compared
    for name_1 in names:
        links_1 = clr_dict[name_1].keys()
        for name_2 in names:
            if name_1 == name_2:
                continue
            #if we've already calculated the sim_score for this pairing, skip it
            try:
                val = sim_dict[name_1][name_2]
                continue
            except KeyError:
                total_votes_in_common = 0
                actions_in_common = 0
                for url in links_1:
                    #make sure both councilors voted on this vote
                    #and omit unanimous votes
                    if url in clr_dict[name_2] and (url not in unan_set):
                        total_votes_in_common += 1
                        
                        action_1 = clr_dict[name_1][url]
                        action_2 = clr_dict[name_2][url]
                        
                        #"excused" shouldn't count as a vote for our purposes
                        if "Excused" in [action_1,action_2]:
                             total_votes_in_common -= 1
                             continue
                        
                        #these two councilors voted together on this vote
                        if action_1 == action_2:
                            actions_in_common += 1
                            
                #calculate the number of actions in common as a percentage,
                #making sure to not divide by 0
                try:
                    sim_score = round(100*(actions_in_common/total_votes_in_common), 2)
                except ZeroDivisionError:
                    sim_score = np.NaN
                    
                #store the scores
                sim_dict[name_1][name_2] = sim_score
                sim_dict[name_2][name_1] = sim_score
                
    return sim_dict

def get_heatmap(sim_dict):
    
    names = sim_dict.keys()    
    
    #district info to help sort the dataframe
    districts = {
             'Ken Sanchez': 1, 
             'Isaac Benton': 2,
             'Klarissa J. Pena': 3, 
             'Brad Winter': 4, 
             'Cynthia D. Borrego':5, 
             'Dan Lewis': 5, 
             'Patrick Davis': 6, 
             'Diane G. Gibson' : 7, 
             'Trudy E. Jones': 8,
             'Don Harris': 9
            }
    
    #making a heat map
    
    #sort the Dataframe by district
    Cols = sorted(names, key = lambda x:districts.get(x))
    
    dfObj = pd.DataFrame.from_dict(sim_dict, orient = "index", columns = Cols)
    dfObj = dfObj.loc[Cols]
    
    #restore the enye!
    dfObj = dfObj.rename({'Klarissa J. Pena': 'Klarissa J. Peña'},axis = 'columns')
    dfObj = dfObj.rename({'Klarissa J. Pena': 'Klarissa J. Peña'},axis = 'index')
    
    #create a mask to avoid mapping redundant values
    dropSelf = np.zeros_like(dfObj)
    dropSelf[np.triu_indices_from(dropSelf)] = True
    
    a4_dims = (11.7, 12.27)
    fig, ax = pyplot.subplots(figsize=a4_dims)
    #go from blue to red, for visual clarity
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    heatmap = sns.heatmap(dfObj, annot=True, cmap=cmap,linecolor="Black", mask=dropSelf)
    heatmap.set_title('ABQ City Clr % of Votes in Common, 2017 - Now')
    
    return heatmap


if __name__ == "__main__":
    sim_dict = {}

    votes_link = "votes_total.csv"
    #read the csv file into a pandas DataFrame
    df = pd.read_csv(votes_link,encoding = "ISO-8859-1",header=None)
    
    clr_dict,unan_set = clr_dict_getter(df)
    #calculate similarity scores
    sim_dict = sim_calc(clr_dict,unan_set)
    #graph the similarity sscores using a heat map
    heatmap = get_heatmap(sim_dict)
    
    #save that heatmap locally
    fig = heatmap.get_figure()
    fig.savefig("heatmap.png", dpi=400, bbox_inches='tight',pad_inches=0.1)
