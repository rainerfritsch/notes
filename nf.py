from subprocess import call
import argparse,os

parser = argparse.ArgumentParser()
parser.add_argument('-c','--create', nargs = '*', help='Notiz im Ordner anlegen')
parser.add_argument('-l','--list', help='Notizen in Ordner anzeigen')
parser.add_argument('-f','--folder', action='store_true', help='Ordner anzeigen')
parser.add_argument('-ps','--push', action='store_true', help='Push Github')
parser.add_argument('-pl','--pull', action='store_true', help='Pull Github')
args = parser.parse_args()


#config default values
notepath="/Users/rainer/Documents/GitHub/myNotes"
noteapp="atom"
defaultFolder="default"


def createNote(note, folder):
    path=os.path.join(notepath,folder)
    note=note+".md"
    file=os.path.join(path,note)
    print ("Create note " + file)

    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(file):
       with open(file, 'w'): pass

    call([noteapp,file])


def listFiles(folder):
    os.system("clear")
    path=os.path.join(notepath,folder)
    if os.path.exists(path):
        print ("Im Ordner " + folder + " gibt es folgende Notizen:\n")
        dirlist= os.listdir(path)
        dirlist.sort()
        for f in dirlist:
            if not f.startswith("."):
                print (f)
        print("\n\n")
    else:
        print ("Dieser Ordner existiert noch nicht.")

def listFolders():
    os.system("clear")
    print ("Diese Ordner gibt es schon:\n")
    for f in os.listdir(notepath):
        if not f.startswith("."):
            print (f)
    print("\n\n")

def pushNotes():
    print ("Push notes")
    os.chdir(notepath)
    call(["git","add","*"])
    call(["git", "commit", "-m", "neue Notiz"])
    call(["git", "push", "origin", "master"])

def pullNotes():
    print ("Pull notes")
    os.chdir(notepath)
    call(["git", "pull", "origin", "master"])


if __name__ == "__main__":
    if args.create is not None:
        if len(args.create)<2:
            folder=defaultFolder
        else:
            folder=args.create[1]

        createNote(args.create[0],folder)


    if args.list is not None:
        listFiles(args.list)

    if args.folder:
        listFolders()

    if args.push:
        pushNotes()

    if args.pull:
        pullNotes()
