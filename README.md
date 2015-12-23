AirbnbKyotoScrape
============

Python Function To Scrape Airbnb Listings in Kyoto

Based on https://github.com/hamelsmu/AirbnbScrape

Special thanks to @hamelsmu


###Table of Contents 
####Scraping
- **KyotoScrape.py:**  this is the code that was used to scrape Airbnb.com  this code is very modular and can be re-used to scrape airbnb data for any location.  

####Analysis 
- **DataCleanAirbnb.py**:  this file contains supporting functions for AirbnbWrapup.ipyb.  Used to clean the dataset and parse/remove features as appropriate.


###How To Use The Scraping Code (KyotoScrape.py):
The main functions are:

1) **IterateMainPage()**  this function takes in a location string, and page limit as a parameter and downloads a list of dictionaries which correspond to all of the distinct listings for that location.  For example, calling IterateMainPage('Cambridge--MA', 10) will scrape all of the distinct listings that appear on pages 1-10 of the page listings for that location.  The output from this function will then be a list of dictionaries with each dictionary item corresponding to one unique listing on each page.  The location string is in the format of 'City--State', as that is how the URL is structured.  

2) **iterateDetail()**  this reads in the output of the function **IterateMainPage()** and visits each specific listing to get mroe detailed information.  If more detailed information is found, then the dictionary is updated to contain more values. 

3) **writeToCSV()**  this function takes care of writing the output to a csv file.  

Example of how to run this code:
```python
    #Iterate Through Main Page To Get Results
    MainResults = IterateMainPage('Cambridge--MA', 1)
    
    #Take The Main Results From Previous Step and Iterate Through Each Listing
    #To add more detail
    DetailResults = iterateDetail(MainResults)
    
    #Write Out Results To CSV File, using function I defined
    writeToCSV(DetailResults, 'CambridgeResults.csv')
```

###Configuration:
In the getStatus(ListingID) function, please set up proper month and year.



Still a lot to get done there is.
I will update both the codes and the document asap.

You know, it's just a first commit!

