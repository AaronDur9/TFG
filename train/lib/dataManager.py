# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 11:35:48 2016

@author: slide22
"""

def generateCsv(startDate, endDate, zipDestinationPath, csvDestinationPath, verbose = True):
    downloadData(startDate, endDate, zipDestinationPath, True)
    uncompressData(zipDestinationPath, csvDestinationPath, True)
    correctCharacters(csvDestinationPath, True)

"""
This function download the hourly csv between the years specified at the 
parameters.

Return:
    1. Error while request: status code - The url is invalid or the server 
       is down
    2. Failed fetching data: year - The year url in innaccesible
    3. 0 - Everything is ok. The data have been downloaded in the path 
       specified
"""
def downloadData(startDate, endDate, pathName, verbose = True):
    
    import os
    from bs4 import BeautifulSoup
    import requests
    from urllib2 import urlopen, URLError, HTTPError
    
    #get year from startDate
    startYear = startDate / 10000
    endYear = endDate / 10000
    print "\nStartYear: " + str(startYear)
    print "EndYear: " + str(endYear) + "\n"
    years = range(startYear, endYear + 1)
    
    url = "http://ftp.itacyl.es/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios/"

    # making the request to InfoRiego
    req = requests.get(url)
    
    statusCode = req.status_code
    # if succesfully
    if statusCode == 200:
        
        if verbose:
            print 'Succesfully request InfoRiego\n'
            
        # getting the html of the webpage
        # and the year links
        html = BeautifulSoup(req.text, "lxml")
        links = html.find_all('a')
        
        # making the list of the years
        yearsLinks = list()
        for link in links:
            
            if link.get('href')[:-1].isdigit() and \
                int(link.get('href')[:-1]) in years:
                   
                yearsLinks.append(link.get('href')[:-1])
                
        if verbose:
            print 'Years found: ' + str(len(yearsLinks)) + '\n'
            
        # create the directory if doesn't exist
        if not os.path.exists(pathName):
            
            if verbose:
                print pathName + " not found. Creating it.\n"

            os.makedirs(pathName)
            
        # requesting the years pages
        for year in yearsLinks:

            url2 = url+'/'+year+'/'
            req = requests.get(url2)
            statCode = req.status_code
            
            # if succesfully
            if statCode == 200:
                
                if verbose:
                    print 'Succesfully request year ' + year + '\n'
                
                html = BeautifulSoup(req.text, "lxml")
                links = html.find_all('a')
                
                for link in links:
                    if link.get('href').endswith('.zip'):
                        # only zip files
                        links = [link for link in links \
                                if link.get('href').endswith('.zip') \
                                and int(link.get('href')[0:8]) >= startDate \
                                and int(link.get('href')[0:8]) <= endDate]
                
                #print len(links)
                # getting the .zip links
                i = 0
                for link in links:
                        
                    zipUrl = url2 + link.get('href')
                    auxPath = os.path.join(pathName, link.get_text())

                    if os.path.isfile(auxPath):
                        print "File found. Not downloading: " + auxPath

                    else:
                        #downloading zip file
                        try:
                            
                            # open url
                            zipFile = urlopen(zipUrl)
                            
                            if verbose:
                                print 'Downloading ' + link.get_text()
                            
                            # save the file in local file
                            
                            with open(auxPath, "wb") as localFile:
                                localFile.write(zipFile.read())
                            
                        #handle errors
                        except HTTPError, e:
                            return 'Failed downloading zip file: ' + link.get('href'), e.code, url
                        except URLError, e:
                            return 'Failed downloading zip file: ' + link.get('href'), e.reason, url
                        
                        if verbose:
                            i+=1
                            print 'Successfuly download ' + str(i) + '/' + str(len(links)) + ' in year ' + year
                                
                        
            else:
                return 'Failed on fetching data (' + year + ')'
                
        return 0
    else:
        return 'Error while request: '+ statusCode

"""
This function uncompress the source zip files into a destination path  
"""
def uncompressData(sourcePath, destinationPath, verbose = True):
    
    import os
    from os import listdir
    from os.path import isfile, join
    import zipfile
    
    # check if source path exists
    d = os.path.dirname(sourcePath)
    if not os.path.exists(d):
        return 'Source path not found'
        
    # check if destination path exists and creating if doesn't
    d = os.path.dirname(sourcePath)
    if not os.path.exists(d):
       os.makedirs(d)
       
    zipFiles = [f for f in listdir(sourcePath) if isfile(join(sourcePath, f)) and zipfile.is_zipfile(join(sourcePath, f))] 
    
    if verbose:
        print '\nstarting uncommpression\n'
        
    i = 0
    for zFile in zipFiles:
        
        with zipfile.ZipFile(sourcePath + '/' + zFile, "r") as z:
            z.extractall(destinationPath)
            
        i += 1
        
        if verbose:
            print str(i) + '/' + str(len(zipFiles)) + ' | ' + zFile + ' uncompressed'
            
def deleteTildes(s):
    import unicodedata
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
             
            
def correctCharacters(csvFolder, verbose = True):

    from os import listdir

    if verbose:
        print "\nStarting correcting characters\n"
    
    
    csvFiles = [f for f in listdir(csvFolder) if f.endswith('.csv')]
    
    for f in csvFiles:
        
        filedata = None
        
        with open(csvFolder + '/' + f) as file :
          filedata = file.read()
        
        filedata = filedata.decode('unicode_escape')
        filedata = filedata.replace(u'á', 'a')
        filedata = filedata.replace(u'é', 'e')
        filedata = filedata.replace(u'í', 'i')
        filedata = filedata.replace(u'ó', 'o')
        filedata = filedata.replace(u'ú', 'u')
        filedata = filedata.replace(u'º', 'o')
        filedata = filedata.replace(u'ó', 'o')
        filedata = filedata.encode("utf-8")
        
        # Write the file out again
        with open(csvFolder + '/' + f, 'w') as file:
          file.write(filedata)
          
        if verbose:
            print 'Correcting characters in ' + f

if __name__ == "__main__":
    
    startDate = 20150101
    endDate = 20150131

    downloadData(startDate, endDate, '../data/zipFiles', verbose = True)
    uncompressData('../data/zipFiles', '../data/csvFiles')
    correctCharacters('../data/csvFiles')
