from flask import Flask, request, render_template
import pandas as pd
import difflib
from pathlib import Path
import numpy as np

app = Flask(__name__)  

@app.route('/', methods =["GET", "POST"])
def indexingchanges():
    if request.method == "POST":
        MESHFilter = request.form.get("MESHFilter")
        PMIDFilter = request.form.get("PMIDFilter")
        IndexingFilter = request.form.get("IndexingFilter")
        changeddf = pd.read_csv('meshchanges.csv.gz', dtype=str, usecols=['PMID','IndexingMethod_x','DateRevised_x','MESH_x','IndexingMethod_y','DateRevised_y','MESH_y'])
        if MESHFilter is not None and MESHFilter !="":
            filtereddf = changeddf.query("MESH_x.str.contains(@MESHFilter, case=False) or MESH_y.str.contains(@MESHFilter, case=False)")
        else:
            filtereddf = changeddf
        if PMIDFilter is not None and PMIDFilter != "":
            filtereddf = filtereddf.query("PMID == @PMIDFilter")
        else:
            filtereddf = filtereddf
        if IndexingFilter is not None and IndexingFilter !="":
            filtereddf = filtereddf.query("IndexingMethod_y.str.contains(@IndexingFilter, case=False)")
        else:
            filtereddf = filtereddf
        changeddict = filtereddf[['PMID', 'IndexingMethod_x', 'DateRevised_x', 'MESH_x', 'IndexingMethod_y', 'DateRevised_y', 'MESH_y']].to_dict(orient='records')
        HTMLTables = []
        addedtotal = []
        removedtotal = []
        unchangedtotal = []
        meshremoved = 0
        totalrecords = len(changeddict)
        
        for obj in changeddict[:5000]:
            PMIDrow = obj["PMID"]
            PMIDrow = str(PMIDrow)
            OGMESH = obj["MESH_x"]
            OGMESH = OGMESH.replace("Physicians'","Physicians")
            OGMESH = OGMESH.replace('"','$')
            OGMESH = OGMESH.replace("$","'")
            OGMESH = OGMESH.replace('",',"'")
            OGMESH = OGMESH.replace(", '",";")
            OGMESH = OGMESH.replace("'","")
            OGMESH = OGMESH.replace("[","")
            OGMESH = OGMESH.replace("]","")
            GMESH = OGMESH.replace('"',"")
            OGMESH = OGMESH.split(";")
            NewMESH = obj["MESH_y"]
            NewMESH = NewMESH.replace("Physicians'","Physicians")
            NewMESH = NewMESH.replace('"','$')
            NewMESH = NewMESH.replace('$',"'")
            NewMESH = NewMESH.replace(", '",";")
            NewMESH = NewMESH.replace("'","")
            NewMESH = NewMESH.replace('"[',"")
            NewMESH = NewMESH.replace(']"',"")
            NewMESH = NewMESH.replace("[","")
            NewMESH = NewMESH.replace("]","")
            NewMESH = NewMESH.replace('"',"")
            NewMESH = NewMESH.split(";")
            OGIndexing = obj["IndexingMethod_x"]
            NewIndexing = obj["IndexingMethod_y"]
            FirstDateRevised = obj["DateRevised_x"]
            SecondDateRevised = obj["DateRevised_y"]
            #might need to split on ', and possibly reformat
            PMURI = "https://pubmed.ncbi.nlm.nih.gov/" + PMIDrow
            #Might want to play around with sorting and unsorting when you have the actual data. Looking at reordering of headings might also be interesting
            #NLM suggests Mesh are ordered in order of importance https://www.nlm.nih.gov/tsd/cataloging/trainingcourses/mesh/mod3_170.html, however, they do seem arranged alphabetically in Pubmed. Need to check XML files
            OGMESH = sorted(OGMESH)
            NewMESH = sorted(NewMESH)
            if OGMESH != NewMESH:
                OGIndexing = str(OGIndexing)
                NewIndexing = str(NewIndexing)
                FirstDateRevised = str(FirstDateRevised)
                SecondDateRevised = str(SecondDateRevised)
                OGDesc = "Original (" + OGIndexing + ") " + FirstDateRevised + ""
                NewDesc = "Revised (" + NewIndexing + ") " + SecondDateRevised + ""
                htmldiff = difflib.HtmlDiff().make_table(OGMESH, NewMESH, fromdesc=OGDesc, todesc=NewDesc)
                meshremovedcheck = '"diffs_ub">' + MESHFilter
                print(meshremovedcheck)
                print(htmldiff)
                if meshremovedcheck in htmldiff:
                    print(matchremoved)
                    meshremoved +=1
                diffnumbers = list(difflib.ndiff(OGMESH, NewMESH))
                added = str(sum(1 for line in diffnumbers if line.startswith('+ ')))
                addedtotal.append(added)
                removed = str(sum(1 for line in diffnumbers if line.startswith('- ')))
                removedtotal.append(removed)
                unchanged = str(sum(1 for line in diffnumbers if line.startswith('  ')))
                unchangedtotal.append(unchanged)
                htmldiff = "<div style='display:inline' id='MESHTable'><h3><a href='" + PMURI + "'>PMID " + PMIDrow + "</a></h3><div style='display:inline-flex'><div style='display:inline'>" + htmldiff + "</div>" + "<div style='display:inline; font-family:courier; margin-left:15px;'><table id='diffcalculations'><tr><td id='addedlabel'>Added:</td><td id='addedvalue'>" + added + "</td><tr><td id='removedlabel'>Removed:</td><td id='removedvalue'>" + removed + "</td></tr><tr><td id='unchangedlabel'>Unchanged:</td><td id='unchangedvalue'>" + unchanged + "</td></tr></table></div></div></div>"
                HTMLTables.append(htmldiff)

        DiffHTML = "".join(HTMLTables) 
        addedtotal = list(map(int, addedtotal))
        removedtotal = list(map(int, removedtotal))
        unchangedtotal = list(map(int, unchangedtotal))
        addedtotal = sum(addedtotal)
        removedtotal = sum(removedtotal)
        unchangedtotal = sum(unchangedtotal)
    
    else:
        MESHFilter = ""
        DiffHTML = ""
        PMIDFilter = ""
        IndexingFilter = ""
        addedtotal = ""
        removedtotal = ""
        unchangedtotal = ""
        meshremoved = ""
        totalrecords = ""
        
    return render_template("form.html", totalrecords = totalrecords, MESHFilter = MESHFilter, DiffHTML = DiffHTML, PMIDFilter = PMIDFilter, IndexingFilter = IndexingFilter, addedtotal = addedtotal, removedtotal = removedtotal, unchangedtotal = unchangedtotal, meshremoved = meshremoved)

if __name__=='__main__':
   app.run()
