from subprocess import call
import argparse,os
import configparser

configFilePath = r'./nf.ini'
configParser = configparser.RawConfigParser()
config=configParser.read(configFilePath)
switch = configParser.get('switch', 'repository')
notepath = configParser.get('repository', switch)


parser = argparse.ArgumentParser()
parser.add_argument('-c','--create', nargs = '*', help='Notiz im Ordner anlegen')
parser.add_argument('-l','--list', help='Notizen in Ordner anzeigen')
parser.add_argument('-fi','--folderIndex', help='Index Files für Ordner erzeugen -fi all für alle Ordner')
parser.add_argument('-s','--search', help='Notiz finden')
parser.add_argument('-f','--folder', action='store_true', help='Ordner anzeigen')
parser.add_argument('-ps','--push', action='store_true', help='Push Github')
parser.add_argument('-pl','--pull', action='store_true', help='Pull Github')
parser.add_argument('-sw','--switch', help='Switch Repository')
args = parser.parse_args()


noteapp="atom"
defaultFolder="default"

def searchNote(note):
    os.system("clear")

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
                        treffer.append(file +"\n"+fields[0]+"->"+fields[1])
                        #print (note + " gefunden in "+ file +"\n"+fields[0]+"->"+fields[1])
    if len(treffer)>0:
        print (note + " gefunden")
        print ("=" *len(note + " gefunden"))
        print ("\n")
        for t in treffer:
            print(t)
        print("\n\n")
    else:
        print (note + " nicht gefunden")
        print ("=" *len(note + " nicht gefunden"))
        print("\n\n")



def addFileToIndex(note,folder):
    print ("Datei wird dem Register hinzugefügt: "+folder+"/"+note)
    indexFile=os.path.join(notepath,folder+".nf")
    with open(indexFile,"r") as f:
        lines=f.readlines()
        if(len(lines)>0):
            nextIndex=int(lines[-1].split(",")[0])+1
            with open(indexFile,"a") as f:
                f.write(str(nextIndex)+","+note+"\n")
        else:
            print("Start der Liste")
            with open(indexFile,"a") as f:
                f.write("1,"+note+"\n")


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
        print("Notiz existiert nicht")
    else:
        createNewNote(note, folder)

def createNewNote(note, folder):
    path=os.path.join(notepath,folder)
    note=note+".md"
    file=os.path.join(path,note)
    #print ("Create note " + file)
    indexFile=os.path.join(notepath,folder+".nf")
    if not os.path.exists(path):
        os.makedirs(path)
        with open(indexFile, 'w'): pass
    if not os.path.exists(file):
        addFileToIndex(note, folder)
        with open(file, 'w'): pass

    call([noteapp,file])


def listFiles(folder):
    os.system("clear")
    indexFile=os.path.join(notepath,folder+".nf")
    if os.path.exists(indexFile):
        with open(indexFile,"r") as f:
            lines=f.readlines()
            for l in lines:
                l=l.strip()
                fields=l.split(",")
                print(fields[0]+"->"+fields[1])
        print("\n\n")
    else:
        print("Dieser Ordner existiert noch nicht")


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
                index=index+1
                #print(os.path.basename(f))
                fi.write(str(index) + "," + os.path.basename(f) + "\n")







def listFolders():
    os.system("clear")
    print ("Diese Ordner gibt es schon:\n")
    dirlist= os.listdir(notepath)
    dirlist.sort()
    for d in dirlist:
        #getrickst
        if not os.path.isfile(d) and not d.startswith(".") and not d.endswith(".nf"):
                print (d)
    print("\n\n")

def pushNotes():
    os.system("clear")
    print ("Push notes")
    os.chdir(notepath)
    call(["git","add","*"])
    call(["git", "commit", "-m", "neue Notiz"])
    call(["git", "push", "origin", "master"])

def pullNotes():
    os.system("clear")
    print ("Pull notes")
    os.chdir(notepath)
    call(["git", "pull", "origin", "master"])

def switchRepository(repository):
    configParser.set("switch","repository", repository)
    with open(configFilePath, 'w') as configfile:    # save
        configParser.write(configfile)


if __name__ == "__main__":
    if args.create is not None:
        if len(args.create)<2:
            folder=defaultFolder
        else:
            folder=args.create[1]

        createNote(args.create[0],folder)

    if args.list is not None:
        listFiles(args.list)

    if args.folderIndex is not None:
        indexFiles(args.folderIndex)

    if args.search is not None:
        searchNote(args.search)

    if args.folder:
        listFolders()

    if args.push:
        pushNotes()

    if args.pull:
        pullNotes()

    if args.switch is not None:
        switchRepository(args.switch)
