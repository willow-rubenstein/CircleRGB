from urllib.request import urlopen
# remember to change this and the one in version.txt everytime you update
version = "v6.1"
def checkForUpdates():
    try:
        r = urlopen("https://raw.githubusercontent.com/MaleVTuber/CircleRGB/master/version.txt")
    except:
        r = urlopen("https://raw.githubusercontent.com/cfgexe/CircleRGB/master/version.txt")
                                     
    for line in r:
        if line != version:
            print("Please update your CircleRGB!")
            exit()
        else:
            return
