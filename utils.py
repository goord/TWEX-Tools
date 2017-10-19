boxes = { "westcoast" : [59.616826,61.474623,4.836320,7.560929],
          "svalbard"  : [77.778678,79.228149,13.90967,18.68607]}

def getbox(loc):
    if(len(loc) == 1):
        locstring = str(loc[0]).lower()
        return boxes[locstring]
    elif(len(loc) == 2):
        box = [float(loc[0]),float(loc[1])]
    elif(len(loc) == 4):
        box = [float(loc[0]),float(loc[1]),float(loc[2]),float(loc[3])]
    else:
        raise Exception("Unsupported location specification " + str(loc))

