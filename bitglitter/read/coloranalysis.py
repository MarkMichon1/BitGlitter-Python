import math

def colorSnap(rawFrameRGB, paletteColorList):

    closestMatch = None
    closestDistance = 500
    for color in paletteColorList:

        activeDistance = math.sqrt(((rawFrameRGB[0] - color[0]) ** 2) + ((rawFrameRGB[1] - color[1])** 2)
                                   + ((rawFrameRGB[2] - color[2]) ** 2))
        if activeDistance < closestDistance:
            closestMatch = color
            closestDistance = activeDistance
    return closestMatch


def returnDistance(rawFrameRGB, expectedValue):
    return math.sqrt(((rawFrameRGB[0] - expectedValue[0]) ** 2) + ((rawFrameRGB[1] - expectedValue[1]) ** 2) +
              ((rawFrameRGB[2] - expectedValue[2]) ** 2))

