import re as Regex
import collections
import xml.etree.ElementTree as ET
import os
import pathlib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Program to download the complete history of a Wikidot wiki and maintain a local copy.
# The downloads are incremental and restartable.

# The site history data will be kept in the directory Site History
# The structure is a bit complex:
# Top level contains management files plus directories A-Z plus Misc
# Each of those directories contains directories A-Z plus Misc.
#   This arrangement is to prevent there from being too main directories in any drectory, since some Windows tools don't handle thousands of directories well
#   And Fancy 3 has nearly 26,000 pages already.
#   The complete history of individual pages will be contain in directories named the same as the page and stored in the directory hierarchy according to its first two characters
# The complete history of a page xyz will this be stored in directory X/Y/xyz
# xyz will contain numbered directories, each storing a single version.  I.e., xyz/2 will contain the details of version 2 of page xyz.
# The program will guarantee that all version directories will be complete: If a directory exists, it is complete
#   For this reason, it will be possible to prevent HistoryDownloader from attempting to download a specfic version by creating an empty version directory
# The version directories will be similar to what is created by FancyDownloader:
#   source.txt -- contains the source of that version of the page
#   metadata.xml -- and xml file containing the metadata
#           <updated_by> (name of used who did the update)
#           <updated_at> (date and time of update)
#           <tags> (a comma-separated list of tags)
#           <type>  (the kind of update: new, edit, changetags, newfile, removefile, deletepage)
#           <comment> (the update comment, if any)
#           <title>  (the page's title)
#           <files_deleted>  (if a file was deleted, its name)
#           <file_list>  (a list of the files attached to thie version of this page
#   tags -- Tags are not saved as part of the hitsory, but the versions when the tags arec hanged (added or deleted) is documented in the version comments
#   files  -- Files don't seem to be kept as part of history.  The only files we have access to are those that are in the current version.
#             These files will be saved at the top level.
#             The history of *when* they were added exists in the comments for file add versions.

# Our overall strategy will be to work in two phases.
#   In the first phase -- initial creation of the local site history -- we will run through the pages from least-recently-updated to most-recently-updated
#       We will keep a local list (stored in the root of the site history structure) of all the pages we have completed.
#       The list will be in order, beginning with the oldest. We will use this list and the corresponding list from Wikidot to determine what to do next.
#       (Going along the list from Wikidot and comparing it with the list stored locally, the first page found on the wikidot list that isn't stored locally is the next to be downloaded.
#   The second phase is maintenance of a complete initial download
#       In this phase we compare recently updated pages with their local copies and down load whatever increments are new

# The process of getting a historical page is complex and requires parsing a lot of HTML in a pseudo-browser.
#   (The history pages are the result of javascript running and not html, so we can't use Beautiful Soup. We will try to use Selenium, which essentially contains its
#     own internal web browser.)

# Read and save the history of one page.
# Directory is root of all history
def CreatePageHistory(browser, pageName, directory):

    # Open the Fancy 3 page
    browser.get("http://fancyclopedia.org/"+pageName)
    # Find the history button and press it
    elem=browser.find_element_by_id('history-button')
    elem.send_keys(Keys.RETURN)
    # Wait until the history list has loaded
    wait=WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'revision-list')))
    # Get the history list
    div=browser.find_element_by_xpath('//*[@id="revision-list"]/table/tbody')
    historyElements=div.find_elements_by_xpath("tr")[1:]  # The first row is column headers, so skip them.
    # Note that the history list is from newest to oldest
    # The structure of a line is
    #       The revision number followed by a "."
    #       A series of single letters (these letters label buttons)
    #       The name of the person who updated it
    #       The date
    #       An optional comment
    # This calls for a Regex
    rec=Regex.compile("^"  # Start at the beginning
                      "(\d+). "  # Look for a number at least one digit long followed by a period and space
                      "([A-Z])"  # Look for a single capital letter
                      "( V S R | V S )"  # Look for either ' V S ' or ' V S R '
                      "(.*)"  # Look for a name
                      "(\d+ [A-Za-z]{3,3} 2\d{3,3})"  # Look for a date in the 2000s of the form 'dd mmm yyyy'
                      "(.*)$")  # Look for an optional comment

    for el in historyElements:
        id=el.get_attribute("id").replace("revision-row-", "")
        t=el.text
        m=rec.match(t)
        gps=m.groups()

        # The greedy capture of the user name captures the 1st digit of 2-digit dates.  This shows up as the user name ending in a space followed by a single digit.
        # Fix this if necessary
        user=gps[3]
        date=gps[4]
        if user[-2:-1]==" " and user[-1:].isdigit():
            date=user[-1:]+gps[4]
            user=user[:-2]

        # Click on the view source button for this row
        el.find_elements_by_tag_name("td")[3].find_elements_by_tag_name("a")[1].click()
        source=div.find_element_by_xpath('//*[@id="history-subarea"]/div').text     # TODO: Make sure that we don't have to put a wait before this

        # Write out the xml data
        root=ET.Element("data")
        el=ET.SubElement(root, "number")
        number=str(gps[0])
        el.text=number
        el=ET.SubElement(root, "ID")
        el.text=str(id)
        el=ET.SubElement(root, "type")
        el.text=str(gps[1])
        el=ET.SubElement(root, "name")
        el.text=str(user)
        el=ET.SubElement(root, "date")
        el.text=str(date)
        el=ET.SubElement(root, "comment")
        el.text=str(gps[5])
        # And write the xml out to file <localName>.xml.
        tree=ET.ElementTree(root)

        # OK, we have everything.  Start writing it out.
        d1=pageName[0]
        d2=d1
        if len(pageName) > 1:
            d2=pageName[1]

        # Make sure the target directory exists
        seq=("0000"+number)[-4:]
        dir=os.path.join(directory, d1, d2, pageName, "V"+seq)
        pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

        # Write the directory contents
        tree.write(os.path.join(dir, "metadata.xml"))
        with open(os.path.join(dir, "source.txt"), 'a') as file:
            file.write(source)

        i=0


browser=webdriver.Firefox()
CreatePageHistory(browser, "test", ".")
i=0