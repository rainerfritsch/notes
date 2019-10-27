from subprocess import call
from datetime import datetime

import argparse,os, configparser

configFilePath = r'./nf.ini'
configParser = configparser.RawConfigParser()
config=configParser.read(configFilePath)
switch = configParser.get('switch', 'repository')
notepath = configParser.get('repository', switch)
noteapp=configParser.get('general', 'editor')
defaultFolder=configParser.get('general', 'defaultFolder')

parser = argparse.ArgumentParser()
parser.add_argument('-lp','--listProjects', action='store_true', help='Projekte anzeigen')
parser.add_argument('-sp','--switchProject', help='Switch Repository')
parser.add_argument('-e','--edit', nargs = '*', help='Notiz im Ordner anlegen oder bearbeiten')
parser.add_argument('-l','--list', help='Notizen in Ordner anzeigen')
parser.add_argument('-s','--search', help='Notiz finden')
parser.add_argument('-tags',  help='search tag')
parser.add_argument('-today', action='store_true', help='show overdue notes')
parser.add_argument('-lf','--listFolder', action='store_true', help='Ordner anzeigen')
parser.add_argument('-fi','--folderIndex', help='Index Files für Ordner erzeugen -fi all für alle Ordner')
parser.add_argument('-ps','--push', action='store_true', help='Push Github')
parser.add_argument('-pl','--pull', action='store_true', help='Pull Github')

args = parser.parse_args()


def searchToday():
    indexFiles("all")
    printHeader("Overdue notes")
    now = datetime.now()
    filelist= os.listdir(notepath)
    for file in filelist:
        if file.endswith(".nf"):
            path=os.path.join(notepath,file)
            with open(path,"r") as f:
                lines=f.readlines()
                for l in lines:
                    l=l.strip()
                    fields=l.split(",")
                    if len(fields[3])==8:
                        datetime_object = datetime.strptime(fields[3], '%d.%m.%y')
                        dayDiff=(now-datetime_object).days
                        if dayDiff>=0:
                            print(rchop(str(file),".nf")+"\t"+fields[0]+" -> "+rchop(fields[1],".md")+"\t"+str(dayDiff)+" day(s) overdue")
    print("\n\n")


def searchNote(note):
    indexFiles("all")
    #printHeader("Searching note " + note)

    treffer=[]

    filelist= os.listdir(notepath)
    for file in filelist:
        if file.endswith(".nf"):
            #print(file)
            path=os.path.join(notepath,file)
            with open(path,"r") as f:
                lines=f.readlines()
                for l in lines:
                    l=l.strip()
                    fields=l.split(",")
                    if note in fields[1]:
                        item=rchop(file,".nf") +"\t"+fields[0]+"->"+rchop(fields[1],".md")
                        if len(fields[2])>0:
                            item = item + "\t TAGS:"+fields[2]
                        if len(fields[3])>0:
                            item = item + "\t DATE: "+fields[3]
                        treffer.append(item)
    if len(treffer)>0:
        printHeader (note + " gefunden")
        for t in treffer:
            print(t)
        print("\n\n")
    else:
        printHeader (note + " nicht gefunden")
        print("\n\n")


# its a new file
def addFileToIndex(note,folder):
    print ("Datei wird dem Register hinzugefügt: "+folder+"/"+note)
    indexFile=os.path.join(notepath,folder+".nf")

    with open(indexFile,"r") as f:
        lines=f.readlines()
        if(len(lines)>0):
            nextIndex=int(lines[-1].split(",")[0])+1
            with open(indexFile,"a") as f:
                f.write(str(nextIndex)+","+note+",,\n")
        else:
            print("Start der Liste")
            with open(indexFile,"a") as f:
                f.write("1,"+note+",,\n")


def createNote(note, folder):
    if note.isdigit():
        indexFile=os.path.join(notepath,folder+".nf")
        lines=[]
        with open(indexFile,"r") as f:
            lines=f.readlines()
        for l in lines:
            fields=l.split(",")
            if fields[0]==note:
                createNewNote(fields[1].split(".")[0],folder)
    else:
        createNewNote(note, folder)

def createNewNote(note, folder):
    path=os.path.join(notepath,folder)
    note=note+".md"
    file=os.path.join(path,note)
    indexFile=os.path.join(notepath,folder+".nf")
    if not os.path.exists(path):
        os.makedirs(path)
        with open(indexFile, 'w'): pass
    if not os.path.exists(file):
        addFileToIndex(note, folder)
        with open(file, 'w'): pass
    call([noteapp,file])


def listFiles(folder):
    indexFiles(folder)
    printHeader("Files in folder " + folder)
    indexFile=os.path.join(notepath,folder+".nf")
    if os.path.exists(indexFile):
        with open(indexFile,"r") as f:
            lines=f.readlines()
            for l in lines:
                l=l.strip()
                fields=l.split(",")
                output=fields[0]+" -> "+ rchop(fields[1],".md")
                if len(fields[2])>0:
                    output = output + "\t TAGS:"+fields[2]
                if len(fields[3])>0:
                    output = output + "\t DATE: "+fields[3]
                print(output)
        print("\n\n")
    else:
        print("Dieser Ordner existiert noch nicht")

def listProjects():
    printHeader ("List of existing projects")

    for key in configParser.items("repository"):
        print (key[0])
    print ("\n\n\n")

    #print(configParser.items("repository"))

def indexFiles(folder):
    if folder=="all":
        dirlist= os.listdir(notepath)
        dirlist.sort()
        for d in dirlist:
            if not os.path.isfile(d) and not d.startswith(".") and not d.endswith(".nf"):
                indexFilesSingle(d)
    else:
        indexFilesSingle(folder)


def indexFilesSingle(folder):
    print("Index für den Ordner "+folder+" neu erstellen.")
    path=os.path.join(notepath,folder)
    indexFile=os.path.join(notepath,folder+".nf")
    if os.path.exists(path):
        dirlist= os.listdir(path)
        dirlist.sort()
        index=0
        with open(indexFile,"w") as fi:
            for f in dirlist:
                if not f.startswith("."):
                    filePath = os.path.join(path,f)
                    tags=findTags(filePath)
                    index=index+1
                    #print(os.path.basename(f))
                    fi.write(str(index) + "," + os.path.basename(f) + ","+str(tags[0])+","+str(tags[1])+"\n")







def listFolders():
    printHeader ("Liste der vorhanden Ordner")
    dirlist= os.listdir(notepath)
    dirlist.sort()
    for d in dirlist:
        #getrickst
        if not os.path.isfile(d) and not d.startswith(".") and not d.endswith(".nf"):
                print (d)
    print("\n\n")

def pushNotes():
    printHeader ("Push notes")
    os.chdir(notepath)
    call(["git","add","*"])
    call(["git", "commit", "-m", "neue Notiz"])
    call(["git", "push", "origin", "master"])

def pullNotes():
    printHeader ("Pull notes")
    os.chdir(notepath)
    call(["git", "pull", "origin", "master"])

def switchRepository(repository):
    configParser.set("switch","repository", repository)
    with open(configFilePath, 'w') as configfile:    # save
        configParser.write(configfile)




# general helping functions
def printHeader(header):
    cls()
    print(header)
    print("="*len(header))
    print("\n")


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def rchop(s, sub):
    return s[:-len(sub)] if s.endswith(sub) else s

def lchop(s, sub):
    return s[len(sub):] if s.startswith(sub) else s






def findTags(file):
    # if line startswith ! or @ safe in indexFiles
    with open(file,"r") as f:
        lines=f.readlines()
        tags=[]
        date=""
        for l in lines:
            l=l.strip()
            if l.startswith("!"):
                tags.append(lchop(l,"!"))
            if l.startswith("@"):
                date=lchop(l,"@")


        return (" ").join(tags), date












if __name__ == "__main__":
    if args.edit is not None:
        if len(args.edit)<2:
            folder=defaultFolder
        else:
            folder=args.edit[1]

        createNote(args.edit[0],folder)

    if args.list is not None:
        listFiles(args.list)

    if args.listProjects:
        listProjects()

    if args.folderIndex is not None:
        indexFiles(args.folderIndex)

    if args.search is not None:
        searchNote(args.search)

    if args.tags is not None:
        print("not yet implemented")

    if args.listFolder:
        listFolders()

    if args.push:
        pushNotes()

    if args.pull:
        pullNotes()

    if args.today:
        searchToday()

    if args.switchProject is not None:
        switchRepository(args.switchProject)
