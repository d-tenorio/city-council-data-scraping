# -*- coding: utf-8 -*-
import csv


def csv_combiner(main,others):
    """
    takes in a filename, main
    and a list of filenames, others
    
    and copies the content of each file in others to a file located at main
    """
    
    
    
    headings = ['link','name','desc','date',
                'result','clr1','clr2','clr3','clr4',
                'clr5','clr6','clr7','clr8','clr9']
    headings_set = set(headings)
    
    output = []
    #set up each row in our csv output
    for i,e in enumerate(headings):
        output.append([e])
    
    for fname in others:
        with open(fname, 'r', newline='') as readFile:
            reader = csv.reader(readFile)
            lines = list(reader)
            
            for i,line in enumerate(lines):
                   for e in line:
                       if e not in headings_set:
                           output[i].append(e)
    
        readFile.close()
        
    with open(main, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(output)
    
    writeFile.close()

        

if __name__ == "__main__":
    indices = range(2,4) #change this depending on how many votes.csv files you need to combine
    
    #location to save the output to
    newTitle = "votes_total.csv"
    
    #generate the list of titles of files to combine
    titles = ["votes.csv"]
    for i in indices:
        curr = "votes" + str(i) + ".csv"
        titles.append(curr)

    csv_combiner(newTitle,titles)
    
    
    
    