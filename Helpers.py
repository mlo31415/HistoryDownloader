import datetime
import urllib.request

#-----------------------------------------
# Find text bracketed by <b>...</b>
# Input is of the form <b stuff>stuff</b>stuff
# Return the contents of the first pair of brackets found, the remainder of the input string up to </b>, and anything leftover afterwards (the three stuffs)
def FindBracketedText(s, b):
    strlower=s.lower()
    # Find <b ...>
    l1=strlower.find("<"+b.lower()) # Look for <b
    if l1 == -1:
        return "", "", s
    l2=strlower.find(">", l1)       # Look for following >
    if l2 == -1:
        print("***Error: no terminating '>' found in "+strlower+"'")
        return None
    s1=s[l1+len(b)+2:l2]

    # Find text between <b ...> and </b>
    l3=strlower.find("</"+b.lower()+">", l2+1)
    if l3 == -1:
        return None

    return s1, s[l2+len(b):l3], s[l3+len(b)+3:]

#-------------------------------------
# Function to pull and hfref and accompanying text from a Tag
# The structure is "<a href='URL'>LINKTEXT</a>
# We want to extract the URL and LINKTEXT
def GetHrefAndTextFromString(s):
    s=FindBracketedText(s, "a")
    if s[0] == "":
        return None, None

    # Remove the 'href="' from trailing '"' from the string
    return s[0][6:-1], s[1]


#-------------------------------------
def DecodeDatetime(dtstring):
    if dtstring == None:
        return datetime.datetime(1950, 1, 1, 1, 1, 1)    # If there's no datetime, return something early
    if not dtstring.endswith("+00:00"):
        raise ValueError("Could not decode datetime: '")+dtstring+"'"
    return datetime.datetime.strptime(dtstring[:-6], '%Y-%m-%dT%H:%M:%S')


#-----------------------------------------
# Copy the contents of a file from a given URL to a local file.
def Download(url, filepath):

    webFile = urllib.urlopen(url)
    localFile = open(filepath)
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()
    return