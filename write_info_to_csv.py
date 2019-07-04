# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 22:20:30 2019

@author: dteno
"""
import csv 

def write_out_votes(c_list, v_list, fname = None):
    """
    takes in a list of Councillor objects, c_list
    and a list of Vote objects, v_list
    
    the optional input fname can specify where to save the output
    """
    
    
    if not fname:
        fname = 'votes_2017_to_2019.csv'
    
    with open(fname, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        
        rows = []
        #set up the indices for readability
        for _ in range(14):
            rows.append([])
        
        rows[0].append('link')
        rows[1].append('name')
        rows[2].append('desc')
        rows[3].append('date')
        rows[4].append('result')
        rows[5].append('clr1')
        rows[6].append('clr2')
        rows[7].append('clr3')
        rows[8].append('clr4')
        rows[9].append('clr5')
        rows[10].append('clr6')
        rows[11].append('clr7')
        rows[12].append('clr8')
        rows[13].append('clr9')
        
        #go through each Vote object, get the information we need
        for curr_vote in v_list:
            rows[0].append(curr_vote.link)
            rows[1].append(curr_vote.name)
            rows[2].append(curr_vote.desc)
            rows[3].append(curr_vote.date)
            rows[4].append(curr_vote.result)
            
            curr_i = 5
            #go through each councillor
            for c in c_list:
                #find the vote information by that councillor
                if curr_vote.link in c.votes: 
                    name = c.name
                    #account for the enye in one councillor's name
                    if '\u5358' in name:
                       name = 'Klarissa J. Pena'
                    rows[curr_i].append(name + '|' +  c.votes[curr_vote.link])
                    curr_i += 1
            #for votes with less than 9 councillors present, add a filler value
            while curr_i < 14:
                rows[curr_i].append('N/A')
                curr_i += 1
                 
        writer.writerows(rows)
                
        
    writeFile.close()
    
def write_out_councillors(c_list,v_list, fname = None):
    if not fname:
        fname= 'councillors_2017_to_2019.csv'
    with open(fname, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        output = []
        curr_col = 1
        for i,c in enumerate(c_list):
            #accounting for the enye
            if 'Klarissa' in c.name:
                       c.name = 'Klarissa J. Pena'
            #the first column should contain titles for readability
            if i == 0:
                output.append(['Name',c.name])
                output.append(['District',c.district])
                output.append(['Years_Active',c.years_active])
                
                for key in c.votes:
                    output.append(['',c.name + '|' + key + '|' + c.votes[key]])
                
            #the rest of the columns can just contain the information
            else:
                output[0].append(c.name)
                output[1].append(c.district)
                output[2].append(c.years_active)
                
                curr_i = 3
                
                for key in c.votes:
                    while curr_i >= len(output):
                        output.append(['']*curr_col)
                    output[curr_i].append(c.name + '|' + key + '|' + c.votes[key])
                    curr_i += 1
                while curr_i < len(output):
                    output[curr_i].append('')
                    curr_i += 1
                
            curr_col += 1
            
        writer.writerows(output)
    writeFile.close()
    
