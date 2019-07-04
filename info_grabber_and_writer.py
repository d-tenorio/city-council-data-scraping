# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import collections
import re
import requests
from bs4 import BeautifulSoup
from write_info_to_csv import *
from classes import *

def get_bill_links(years_of_interest, browser=None,quitBrowser=True):
    #initialize web crawler if needed
    if not browser:
        browser = webdriver.Firefox()
    #intialize output, a set of the links of different bills we seek to get vote info from
    bill_links = set()
    
    CITY_LEGISLATION_LINK = 'https://cabq.legistar.com/Legislation.aspx'
    for year_to_search in years_of_interest:
        
        #start at the city legislation website
        browser.get(CITY_LEGISLATION_LINK)
        
        #go to the advanced search
        adv_search = browser.find_element_by_id("ctl00_ContentPlaceHolder1_btnSwitch")
        adv_search.click()
        
        #set the number of results to all, so we have access to every result from the chosen year
        results = browser.find_element_by_id("ctl00_ContentPlaceHolder1_lstMax_Input")
        results.click()
        results_selector = "#ctl00_ContentPlaceHolder1_lstMax_DropDown > div > ul > li"
        num_results = browser.find_elements_by_css_selector(results_selector)
        for n in num_results:
            if n.text == "All":
                n.click()
                
        #set the year in the search parameters
        year = browser.find_element_by_id("ctl00_ContentPlaceHolder1_lstYearsAdvanced_Input")
        year.click()
        
        years_selector = "#ctl00_ContentPlaceHolder1_lstYearsAdvanced_DropDown > div > ul > li"
        years = browser.find_elements_by_css_selector(years_selector)
        for y in years:
            if y.text == year_to_search:
                y.click()
                
        #execute the search
        search_btn = browser.find_element_by_id("visibleSearchButton2")
        search_btn.click()
        
        bills = browser.find_elements_by_css_selector("tbody > tr > td > a")
        
        #find the actual links for each bill
        for bill in bills:
            #check to make sure we aren't adding None and that we are adding a unique URL
            link = bill.get_attribute("href")
            if link and len(link) > 43:
                bill_links.add(link)
            
        #if we do have more than one page of bills to go through, we'll need to cycle through each page
        other_pages_selector = "#ctl00_ContentPlaceHolder1_gridMain_ctl00 > thead > tr > td > table > tbody > tr > td > div > a"
        pages = collections.deque(browser.find_elements_by_css_selector(other_pages_selector))
        
        #keep track of the pages we've already visited
        visited = set("1")
        
        #while we still have a page to visit, keep looking for more pages and adding more links
        while pages:
            url = pages.popleft()
            try: 
                url.click()
                visited.add(url.text)
                bills = browser.find_elements_by_css_selector("tbody > tr > td > a")
                for bill in bills:
                    link = bill.get_attribute("href")
                    if link and len(link) > 43:
                        bill_links.add(link)
            #if we fail our search, we need to update our links and try again
            except: 
                newElements = browser.find_elements_by_css_selector(other_pages_selector)
                pages.clear()
                for e in newElements:
                    if e.text not in visited:
                        pages.append(e)
    if quitBrowser:
        browser.quit()
    return bill_links
              

def get_votes(links, browser=None,quitBrowser=True):
    """get_vote-info takes in a set of links to individual bills and
        returns two things: 
        -a list of Councillor objects categorizing each councillor along with 
        their action taken on each bill
        -a list of Vote objects categorizing each vote
    """
    #populate votes first, councillors later
    votes = []
    
    if not browser:
        browser = webdriver.Firefox()

    for i,link in enumerate(links):
        #sprint("link number:", i)
    #for link in ['https://cabq.legistar.com/LegislationDetail.aspx?ID=1263881&GUID=45956378-D021-468E-9459-CD3C23DE55D7&Options=Advanced&Search=']:
        browser.get(link)
        
        #establishing a number of CSS selectors
        rows_selector = "#ctl00_ContentPlaceHolder1_gridLegislation_ctl00 > tbody > tr"
        vote_taken_selector = "td:nth-child(4)"
        vote_details_selector = "td:nth-child(5) > a"
        date_selector =  "td:nth-child(1)"
        name_selector = "#ctl00_ContentPlaceHolder1_lblFile2"
        desc_selector = "#ctl00_ContentPlaceHolder1_lblTitle2"
        
        #get each of the rows containing votes, along with the name and desc of the particular bill
        rows = browser.find_elements_by_css_selector(rows_selector)
        name = browser.find_element_by_css_selector(name_selector)
        desc = browser.find_element_by_css_selector(desc_selector)
        
        for row in rows:
            #initialize a Vote object
            curr = Vote()
            
            #try-except block to catch any pages that have NO action taken
            try:
                vote_taken = row.find_element_by_css_selector(vote_taken_selector)
                date = row.find_element_by_css_selector(date_selector)
            except:
                continue
            
            #find the rows the city council actually took a vote on. 
            #if they did, store all the details of the vote
            if (vote_taken.text in ['Pass','Fail']):
                curr.name = name.text
                curr.desc = desc.text
                curr.result = vote_taken.text
                curr.date = date.text
                
                vote_details_info = row.find_element_by_css_selector(vote_details_selector).get_attribute("onclick")
                
                #make this check to see if the city council actually took a vote
                # (sometimes a vote is only planned, but gets canceled)
                if vote_details_info:
                    #use a regex to find the actual link where the votes are stored
                    #then, do some other formatting to give us a new page to visit
                    votes_link = re.search('\'.+\',', vote_details_info)
                    votes_link = votes_link[0]
                    votes_link = votes_link[1:-2]
                    
                    prefix = r"https://cabq.legistar.com/"
                    votes_link = prefix + votes_link
                    curr.link = votes_link
                    
                    #finally, store the vote
                    votes.append(curr)                                
    print("Stored",len(votes), "votes.")
    if quitBrowser:
        browser.quit()
    return votes


def get_councillor_info(votes):
    
    #now that we have all of the pages containing votes, we need only
    #visit them to find out how each councillor voted on them
    #store these in a dictionary where the key is a string with the name of the councillor
    #and the value is a Councillor object
    councillor_dict = {}
    
    
    for vote in votes:
        link = vote.link
        
        response = requests.get(link)  
        page_content = BeautifulSoup(response.content, "html.parser")
        
        rows_selector = "#ctl00_ContentPlaceHolder1_gridVote_ctl00 > tbody > tr"
        name_selector = "td:nth-child(1) > font > a"
        action_selector = "td:nth-child(2) > font"
        
        rows = page_content.select(rows_selector)
        
        
        #each row should have a councillor's name + the action they took
        for row in rows:
            #try lock to see if the vote is empty (no actions taken)
            try:
                #accounting for the enye
                name = row.select(name_selector)[0].text
                action = row.select(action_selector)[0].text
            except:
                continue
            
            
            if 'Klarissa' in name:
                name = 'Klarissa J. Pena'
            
            #create a new Councillor object if needed
            if name in councillor_dict:
                councillor_dict[name].votes[link] = action
            else:
                councillor_dict[name] = Councillor(name,{},"",[])
                councillor_dict[name].votes[link] = action
                    
    #we only need the objects themselves rather than the full dictionary
    return list(councillor_dict.values())
       
    
           
if __name__ == "__main__":
    years_of_interest = ["2017","2018","2019"] #change this input to reflect the years you wish to obtain data from
    
    #initialize webdriver 
    #browser = webdriver.Firefox()
    
    #gets the links where every single bill from the desired years are stored
    #all_bills = get_bill_links(years_of_interest, browser) 
    #bills_list = list(all_bills) #can turn the links into a list to be able to analyze only a subset to prevent timeouts
    #all_votes = get_votes2(bills_list[:50])
    
    #get a list of hyperlinks for every vote taken on each bill
    #all_votes = get_votes(bills_list[:100],browser)

    #get a list of Councillor objects, containing every single action taken by each councillor on a vote
    councillors = get_councillor_info(all_votes[:50])

    #save information to .csv files...
    
    #...organized by each vote 
    write_out_votes(councillors,all_votes) 
    #...organized by councillor
    write_out_councillors(councillors,all_votes) 

