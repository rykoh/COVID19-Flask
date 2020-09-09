#Importing packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import pdfplumber
import pandas as pd
from rake_nltk import Rake
import stringdist
from pymongo import MongoClient




# NLP Rake to extract key words from descriptions
r = Rake()
titleOrCoord = []
resultKeyWords = []
linksOrPOC = []
descrip = []
typeOrDep = []
dataSrc = []


drivers = {"Technology and Computer Science": ["technical", "AWS", "software", "development", "cyber", "python", "parameter", "computer", "model", "predictive", "data", "machine", "artificial intelligence", "map"], 
           "Biomedical": ["biology", "ventilator", "lung", "FDA", "hospital", "medicine","tissue", "nasal", "oropharyngeal", "specimen", "oxygen", "placebo", "virus", "antibiotic", "infection", "chronic", "health", "drug", "swab", "blood", "heart", "genome", "clinical"]}
           #"Social Services": ["state", "lockdown", "environment", "community", "social", "low income", "distancing", "pandemic"]}

#Table structure for each of the categories
catTables = {'Technology and Computer Science': [],
              'Biomedical': [],
              'Other': []}

#Making all of the category tables multidimensional
for keys in catTables:
    for i in range(0, 4):
        catTables[keys].append([])

#Method to scrape Stanford data
def stanford():
    #Create a "headless (not opening chrome directly) selenium object"
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get("https://med.stanford.edu/covid19/research.html")

    #Create relevant arrays (each array represents a column in our table)
    title = []
    contacts = []
    desc = []
    keyWords = []
    links = []

    #Grab all of the posts in the site with given class name (all elements in the table)
    posts = driver.find_elements_by_class_name("text.parbase.section")

    #Extract all of the links in the website
    linkVals = driver.find_elements_by_class_name("text.parbase.section [href]")
 
   
    
    #Iterates through each post (or row in table)
    for post in posts:
        #Split the whole text by lines
        entryVals = post.text.split("\n")
        #If all of the content is present
        if(len(entryVals) == 3):
            #Append the title value to titles
            title.append(entryVals[0])
            #Append the contact value to contacts
            contacts.append(entryVals[1])
            #Append the description to descriptions
            desc.append(entryVals[2])
            #Extract all of the key words from the description 
            r.extract_keywords_from_text(entryVals[2])
            #Store the best matching category for that value and eventually append it to the key words list
            keyPhrase = getKeyWord(r.get_ranked_phrases())
            keyWords.append(keyPhrase)
            #Append the title to the specific table which cooresponds to this entries category (tech, bio etc)
            catTables[keyPhrase][0].append(entryVals[0])
            #Append the original source, which in this case will be Stanford
            catTables[keyPhrase][1].append("Stanford")
            #Append the description
            catTables[keyPhrase][3].append(entryVals[2])
            
            #Create a column for the links
            linkTxt = []
            #Grab all of the links in the page
            for relLinks in linkVals:
                textVal = relLinks.text
                if textVal in entryVals[1]:
                    linkTxt.append(str(relLinks.get_attribute('href'))+" ")
            
            #Format the links (turn it into a set for no duplicates)
            linkTxt = list(set(linkTxt))
            linkTxt = [s for s in linkTxt if "stanford" in s]
            #Split by lines for easy readability
            resVal = "\n".join(linkTxt)
            resVal = " "+resVal
            links.append(resVal)
            #Append the links to both the regular and categor table
            catTables[keyPhrase][2].append(resVal)

    #Close the scraper object
    driver.close()

    for a in title:
        titleOrCoord.append(a)

    for a in keyWords:
        resultKeyWords.append(a)       

    for a in links:
        linksOrPOC.append(a)    
    
    for a in desc:
        descrip.append(a)

    for a in desc:
        typeOrDep.append("N/A")

    for a in title:
        dataSrc.append("Stanford")



    
    #Turn the table to a csv and save it
    df = pd.DataFrame(list(zip(title, contacts, desc, links, keyWords)), 
                columns =['Project Title', 'Point of Contact', 'Project Description', 'Relevant Links', 'Key Words']) 

    df.to_csv('StanfordProjects.csv', index = False)

    #Read from mongoDB and place the table into mongodb
    client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/Covid19Data?retryWrites=true&w=majority")
    db = client['Covid19Data']
    name = 'StanfordProjects'
    collection = db[name]
    collection.drop()
    collection = db[name]
    df.reset_index(inplace=True)
    data_dict = df.to_dict("records")
    # Insert collection
    collection.insert_many(data_dict)
    return df
    
#--------------------------------------------------------------

#Method to grab the longest length of a string
def longeststring(lst):
    longest = ""
    #In the list if the item is a string and the length is longer than the longest
    for x in lst:
        if isinstance(x, str) and len(x) > len(longest):
            #Set the longest to the current string
            longest = x
    #Return the length of the longest string in the list
    return len(longest)

#This method gets the most relevant category based on the ranked phrases in the description
def getKeyWord(rankedPhrases):
    #Set the initial ratio of the distance to 0
    min_dist_ratio = 1
    driv = ""
    for driver in drivers: 
        indic = drivers.get(driver)
        div =  0
        total_ratio = 0
        for key_val in indic:
            for key_words in rankedPhrases:
                #This gets the levenshtein distance between each word if the row data is not 'None'
                if key_words is not None:
                    dist = stringdist.levenshtein(key_val.lower(), key_words.lower())
                    curr_dist_ratio = (dist/longeststring([key_val, key_words]))
                    total_ratio += curr_dist_ratio
                    div = div+1
        
        total_ratio = total_ratio/div
        if total_ratio <min_dist_ratio:
            min_dist_ratio = total_ratio
            driv = driver
    #The levenshtein distance is computed and the category with the lowest levenshtein distance among all the key words is used for 
    #that specific row. 
    if min_dist_ratio <0.87:
        driv = "Other"
    return driv    


#This method is to scrape Virginia Tech data
def virginiaTech():

    #Create a "headless (not opening chrome directly) selenium object"
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get("https://www.research.vt.edu/covid-19-updates-impacts/opportunities.html")

    #Create relevant arrays (each array represents a column in our table)
    title = []
    typeOfResearch = []
    desc = []
    links = []
    keyWords = []

    #Grab all of the posts in the site with given class name (all elements in the table) (split by even and odd, this is even)
    postsEven = driver.find_elements_by_class_name("rowTop.rowEven")
    #Get all of the links in the site with given class name (all elements in the table) (split by even and odd, this is even)
    linkValsEven = driver.find_elements_by_class_name("rowTop.rowEven [href]")

    #Grab all of the posts in the site with given class name (all elements in the table) (split by even and odd, this is odd)
    postsOdd = driver.find_elements_by_class_name("rowTop.rowOdd")
    #Get all of the links in the site with given class name (all elements in the table) (split by even and odd, this is odd)
    linkValsOdd = driver.find_elements_by_class_name("rowTop.rowOdd [href]")

    #Get all of the descriptions in the site
    descs = driver.find_elements_by_class_name("vt-c-table-noPostProcess")
    
    #Index is set to 0 for all of the even items (this variable is for the descriptions as they all came seperately)
    index = 0

    #Iterates through each even post (or row in table)
    for i in postsEven:
        #Split the whole text by lines
        entryVals = i.text.split("\n")
        #Append the title value to titles
        title.append(entryVals[2])
        #Append the type of research to typesOFResearch
        typeOfResearch.append(entryVals[4])
        #Append the description to descriptions
        desc.append(descs[index].text)
        #Extract all of the key words from the description 
        r.extract_keywords_from_text(descs[index].text)
        #Store the best matching category for that value and eventually append it to the key words list
        keyPhrase = getKeyWord(r.get_ranked_phrases())
        keyWords.append(keyPhrase)
         #Append the title to the specific table which cooresponds to this entries category (tech, bio etc)
        catTables[keyPhrase][0].append(entryVals[2])
        #Append the original source, which in this case will be Virginia Tech
        catTables[keyPhrase][1].append("Virginia Tech")
        #Append the description
        catTables[keyPhrase][3].append(descs[index].text)
        #Increment the index by two for all even items
        index+=2

    #Get the links in the table based on the even links and append them to the link column in the table
    for linksVals in linkValsEven:
        indivLink = str(linksVals.get_attribute('href'))
        links.append(indivLink)
        catTables[keyPhrase][2].append(indivLink)

    #Set index to 1 for odd items
    index = 1
    #Iterates through each odd post (or row in table)
    for i in postsOdd:
        #Split the whole text by lines
        entryVals = i.text.split("\n")
        #Append the title value to titles
        title.append(entryVals[2])
        #Append the type of research to typesOFResearch
        typeOfResearch.append(entryVals[4])
        #Append the description to descriptions
        desc.append(descs[index].text)
        #Extract all of the key words from the description 
        r.extract_keywords_from_text(descs[index].text)
        #Store the best matching category for that value and eventually append it to the key words list
        keyPhrase = getKeyWord(r.get_ranked_phrases())
        keyWords.append(keyPhrase)
        #Append the title to the specific table which cooresponds to this entries category (tech, bio etc)
        catTables[keyPhrase][0].append(entryVals[2])
        #Append the original source, which in this case will be Virginia Tech
        catTables[keyPhrase][1].append("Virginia Tech")
        #Append the description
        catTables[keyPhrase][3].append(descs[index].text)
        #Increment the index by two for all odd items
        index+=2

    #Get the links in the table based on the odd links and append them to the link column in the table
    for linksVals in linkValsOdd:
        indivLink = str(linksVals.get_attribute('href'))
        links.append(indivLink)
        catTables[keyPhrase][2].append(indivLink)

    #Close the scraper object
    driver.close()
    for a in title:
        titleOrCoord.append(a)

    for a in keyWords:
        resultKeyWords.append(a) 

    for a in links:
        linksOrPOC.append(a) 
    
    for a in desc:
        descrip.append(a)

    for a in typeOfResearch:
        typeOrDep.append(a)

    for a in title:
        dataSrc.append("Virginia Tech")
    #Turn the table to a csv and save it
    df = pd.DataFrame(list(zip(title, typeOfResearch, desc, links, keyWords)), 
                    columns =['Project Title', 'Type of Research', 'Project Description', 'Relevant Links', 'Key Words']) 
    df.to_csv('VirginiaTechProjects.csv', index = False)

    #Read from mongoDB and place the table into mongodb
    client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/Covid19Data?retryWrites=true&w=majority")
    db = client['Covid19Data']
    name = 'VirginiaTechProjects'
    collection = db[name]
    collection.drop()
    collection = db[name]
    df.reset_index(inplace=True)
    data_dict = df.to_dict("records")
    # Insert collection
    collection.insert_many(data_dict)
    return df

#This method is to scrape UT Austin data
def utAustin():

    #Open up the PDF using pdf plumber
    pathToFile = "/Users/siddh1/Documents/Covid19Opps/scraping/UT COVID-19 Researchers_active projs only_2020-05-19.pdf"
    pdf = pdfplumber.open(pathToFile)
    #Get the relavant pages
    pages = pdf.pages[1:-1]

    #Create relevant arrays (each array represents a column in our table)
    names = []
    departments = []
    description = []
    contacts = []
    keyWords = []

    #Iterates through each page in the pdf
    for page in pages:
        #Split the whole page by lines
        pageVal = page.extract_text().split("\n")
        #If all of the content is present
        if(len(pageVal)>1):
            #Append the name value to names
            names.append(pageVal[0])
            #Append the department value to departments
            departments.append(pageVal[1])
            #Append the contact value to contacts
            contact = pageVal[-1]
            #Split the description by lines
            descVal = "\n".join(pageVal[2:-1])
            #Split the contact by lines
            contact = contact.split(" ")
            eduIn = False
            #Point of contact
            poc = ""
            #Loop through the contacts and if it was found, we set eduIn to true
            for x in contact:
                if ".edu" in x or ".com" in x:
                    eduIn = True
                    break
            #If the contact was found we isolate it and set it 
            if eduIn == True:
                poc = contact[0]
                contacts.append(contact[0])
                #Then we append the remaining value to the description
                if (len(contact) > 1):
                    contact = " ".join(contact[1:])
                    descVal = descVal + contact
            #If the contact was not found, we move to the previous element to find the contact
            if eduIn == False:
                #we isolate it and set it
                contact = pageVal[-2].split(" ")
                poc = contact[0]
                contacts.append(contact[0])
                descVal = "\n".join(pageVal[2:-2])
                #Then we append the remaining value to the description
                if (len(contact) > 1):
                    contact = " ".join(contact[1:])
                    descVal = descVal + contact
                descVal = descVal + (" ".join(pageVal[-1]))

            #Append the description to descriptions
            description.append(descVal)
            #Extract all of the key words from the description 
            r.extract_keywords_from_text(descVal)
            #Store the best matching category for that value and eventually append it to the key words list
            keyPhrase = getKeyWord(r.get_ranked_phrases())
            keyWords.append(keyPhrase)
            #Append the title to the specific table which cooresponds to this entries category (tech, bio etc)
            catTables[keyPhrase][0].append(pageVal[0])
             #Append the original source, which in this case will be UT Austin
            catTables[keyPhrase][1].append("UT Austin")
            #Append the point of contact
            linkVal = "No links but here is the point of contact: "+poc
            catTables[keyPhrase][2].append(linkVal)
            #Append the description
            catTables[keyPhrase][3].append(descVal)

    for a in names:
        titleOrCoord.append(a)

    for a in keyWords:
        resultKeyWords.append(a) 

    for a in contacts:
        linksOrPOC.append(a) 

    for a in description:
        descrip.append(a)

    for a in departments:
        typeOrDep.append(a)

    for a in names:
        dataSrc.append("UT Austin")

    #Turn the table to a csv and save it
    df = pd.DataFrame(list(zip(names, departments, description, contacts, keyWords)), 
                    columns =['Person Name', 'Department', 'Project Description', 'Point of Contact', 'Key Words']) 

    df.to_csv('UTAustinProjects.csv', index = False)

    #Read from mongoDB and place the table into mongodb
    client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/Covid19Data?retryWrites=true&w=majority")
    db = client['Covid19Data']
    name = 'UTAustinProjects'
    collection = db[name]
    collection.drop()
    collection = db[name]
    df.reset_index(inplace=True)
    data_dict = df.to_dict("records")
    # Insert collection
    collection.insert_many(data_dict)
    return df




#--------------------------------------------------------------------------------------

def princeton():
    # Scraping done in a Jupyter Notebook

    # Read CSV as DF
    df = pd.read_csv('PrincetonProjects', index=False)

    #Read from mongoDB and place the table into mongodb
    client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/Covid19Data?retryWrites=true&w=majority")
    db = client['Covid19Data']
    name = 'PrincetonProjects'
    collection = db[name]
    collection.drop()
    collection = db[name]
    df.reset_index(inplace=True)
    data_dict = df.to_dict("records")
    # Insert collection
    collection.insert_many(data_dict)
    return df


#--------------------------------------------------------------------------------------

def ucSanDiego():
    # Scraping done in a Jupyter Notebook

    # Read CSV as DF
    df = pd.read_csv('UCSDSOM', index=False)

    #Read from mongoDB and place the table into mongodb
    client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/Covid19Data?retryWrites=true&w=majority")
    db = client['Covid19Data']
    name = 'UCSanDiegoProjects'
    collection = db[name]
    collection.drop()
    collection = db[name]
    df.reset_index(inplace=True)
    data_dict = df.to_dict("records")
    # Insert collection
    collection.insert_many(data_dict)
    return df

#--------------------------------------------------------------------------------------







#This method turn the category tables into their own seperate files
def turnCatstoFiles():
    #Iterate through all of the categories 
    for keys in catTables:
        #Create a file name for them
        fileName = str(keys)+".csv"
        #Turn the table to a csv and save it
        df = pd.DataFrame(list(zip(catTables[keys][0], catTables[keys][1], catTables[keys][2], catTables[keys][3])), 
                    columns =['Project Title', 'Source', 'Relevant Links', 'Project Description']) 
        df.to_csv(fileName, index = False)

        #Read from mongoDB and place the table into mongodb
        client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/Covid19Data?retryWrites=true&w=majority")
        db = client['Covid19Data']
        collection = db[str(keys)]
        collection.drop()
        collection = db[str(keys)]
        df.reset_index(inplace=True)
        data_dict = df.to_dict("records")
        # Insert collection
        collection.insert_many(data_dict)

def writeLargeToDatabase():



    df = pd.DataFrame(list(zip(dataSrc, titleOrCoord, typeOrDep, descrip, linksOrPOC, resultKeyWords)), 
                    columns =['Data Source', 'Project Title/ Coordinator', 'Type of Research', 'Description' ,'Relevant Links/POC', 'Key Words']) 
    df.to_csv('BigDataSheet.csv', index = False)

    #Read from mongoDB and place the table into mongodb
    client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/FlaskTable?retryWrites=true&w=majority")
    db = client['FlaskTable']
    name = 'AllDataVals'
    collection = db[name]
    collection.drop()
    collection = db[name]
    df.reset_index(inplace=True)
    data_dict = df.to_dict("records")
    # Insert collection
    collection.insert_many(data_dict)


#All method calls (scrape each source and in the end generate the csv's for all the categories)

stanford()
virginiaTech()
utAustin()
turnCatstoFiles()
writeLargeToDatabase()


#Fin