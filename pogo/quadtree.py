"""
A simple quadtree that we'll use to solve the TSP in a suboptimal but efficient way
"""
import logging
class Tree(object):
    def __init__(self, rect, level):
        #logging.info(rect)
        self.rect = rect
        self.level = level
        self.objects = []
        if level > 0:
            nextLevel = level - 1
            self.nodes = {
                    "NW": Tree(Rect(rect.left, rect.top, rect.midpoint[0], rect.midpoint[1]), nextLevel), 
                    "SW": Tree(Rect(rect.left, rect.midpoint[1], rect.midpoint[0], rect.bottom), nextLevel), 
                    "NE": Tree(Rect(rect.midpoint[0], rect.top, rect.right, rect.midpoint[1]), nextLevel),
                    "SE": Tree(Rect(rect.midpoint[0], rect.midpoint[1], rect.right, rect.bottom), nextLevel)
            }
        else: 
            self.nodes = None
        
    def getObjects(self):
        if self.nodes is None:
            return self.objects
        return self.nodes['NW'].getObjects() + self.nodes['NE'].getObjects() + self.nodes['SW'].getObjects() + self.nodes['SE'].getObjects()
        
                
    def addObject(self, x, y, obj):
        if self.nodes is None:
            self.objects.append(obj)
        else:
            h = "W"
            v = "N"
            if x > self.rect.midpoint[0]:
                h = "E"
            if y > self.rect.midpoint[1]:
                v = "S"

            key = "%s%s" % (v, h)

            self.nodes[key].addObject(x, y, obj)

class Rect(object):
    def __init__(self, x1, y1, x2, y2):
        self.left = x1
        self.top = y1
        self.right = x2
        self.bottom = y2

        self.width = abs(x2-x1)
        self.height = abs(y2-y1)
        self.midpoint = (x1+self.width/2, y1+self.height/2)

    def __str__(self):
        return "Recatangle: (%f, %f) (%f, %f)  %fX%f" %(self.left,self.top,self.right,self.bottom,self.width, self.height)