# Save the wiki page's metadata to an xml file
def SaveMetadata(localName, pageData):
    root = ET.Element("data")
    wikiUpdatedTime = None
    for itemName in pageData:
        if itemName == "content" or itemName == "html":  # Skip: We've already dealt with this
            continue
        # Page tags get handled specially
        if itemName == "tags":
            tags = pageData["tags"]
            if len(tags) > 0:
                tagsElement = ET.SubElement(root, "tags")
                for tag in tags:
                    tagElement = ET.SubElement(tagsElement, "tag")
                    tagElement.text = tag
            continue
        if itemName == "updated_at":  # Save the updated time
            wikiUpdatedTime = pageData[itemName]
        # For all other pieces of metadata, create a subelement in the xml
        if pageData[itemName] != None and pageData[itemName] != "None":
            element = ET.SubElement(root, itemName)
            element.text = str(pageData[itemName])

    # And write the xml out to file <localName>.xml.
    tree = ET.ElementTree(root)
    tree.write(localName + ".xml")
    return wikiUpdatedTime