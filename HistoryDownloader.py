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
# The version directories will be as similar as possible to the directories created by FancyDownloader

