from urllib.request import urlopen
version = "v6.1"
def checkForUpdates():
    r = urlopen("https://raw.githubusercontent.com/MaleVTuber/CircleRGB/master/version.txt")
                                     
    for line in r:
        if line != version:
            print("Please update your CircleRGB!")
            exit()
        else:
            return
