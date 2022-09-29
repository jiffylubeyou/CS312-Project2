from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)
	

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert (type(points) == list and type(points[0]) == QPointF)

		# # erase this (test for the upper and lower tangent finders)
		# L = [QPointF(-.75,0), QPointF(-.5,-.5)]
		# R = [QPointF(.25,0), QPointF(.6,.5)]
		# checkMe = self.FindLowerTangent(L,R)
		# return
		# # erase this ^

		t1 = time.time()
		# create my linked list in ascending x value order here
		xToPointDictionary = {}
		sortedPoints = []
		numbers = []
		for point in points:
			xToPointDictionary.update({point.x(): point})
			numbers.append(point.x())

		numbers.sort()
		for number in numbers:
			sortedPoints.append(xToPointDictionary.get(number))

		points = self.recurser(sortedPoints)

		last = QPointF
		polygon = []
		for point in points:
			if point == points[0]:
				last = point
				continue
			else:
				polygon.append(QLineF(last, point))
			last = point


		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		# polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# point1 = QPointF(upperTangentTuple[0], upperTangentTuple[1])
		# point2 = QPointF(upperTangentTuple[2], upperTangentTuple[3])
		# line = QLineF(point1, point2)
		# self.showTangent([line], RED)
		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		# self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def recurser(self,points):

		if len(points) < 3:
			return points
		# delete this
		self.showTangent([QLineF(points[0], points[1])], GREEN)
		# delete this ^


		leftHalf = points[:len(points) // 2]
		rightHalf = points[len(points) // 2:]
		# after this point, they should begin to be clockwise
		leftHalf = self.recurser(leftHalf)
		rightHalf = self.recurser(rightHalf)

		# this combined should be the clockwise order of things
		combined = []
		upperTangentTuple = self.FindUpperTangent(leftHalf, rightHalf)
		lowerTangentTuple = self.FindLowerTangent(leftHalf, rightHalf)

		# This is 9 - 12 on clock
		for point in leftHalf:
			combined.append(point)
			if point.x() == upperTangentTuple[0]:
				break

		# this is 12 to 6 in clock
		begin = False
		for point in rightHalf:
			if point.x() == upperTangentTuple[2]:
				begin = True
			if begin:
				combined.append(point)
			if point.x() == lowerTangentTuple[2]:
				break

		# this is 6 to 9 on clock
		begin = False
		for point in leftHalf:
			if point.x() == lowerTangentTuple[0]:
				begin = True
			if begin:
				combined.append(point)

		return combined



	# takes in two arrays, both of which are an array of points, and returns a line object
	def FindUpperTangent(self, L, R):
		pStuff = self.findRightMostPoint(L)
		qStuff = self.findLeftMostPoint(R)
		p = pStuff[0]
		i = pStuff[1]
		if i == 0:
			i = len(L) - 1
		else:
			i = i - 1
		q = qStuff[0]
		j = qStuff[1]
		if j == len(R) - 1:
			j = 0
		else:
			j = j + 1
		temp = (p.x(), p.y(), q.x(), q.y())
		done = 0
		while done == 0:
			done = 1
			slope1 = self.findSlope(temp)
			slope2 = self.findSlope((L[i].x(), L[i].y(), q.x(), q.y()))
			point = (L[i].x(), L[i].y())
			point2 = (q.x(), q.y())
			while self.findSlope(temp) > self.findSlope((L[i].x(), L[i].y(), q.x(), q.y())):
				p = L[i]
				temp = (p.x(), p.y(), q.x(), q.y())
				if i == 0:
					i = len(L) - 1
				else:
					i = i - 1
				done = 0
			while self.findSlope(temp) < self.findSlope((p.x(), p.y(), R[j].x(), R[j].y())):
				q = R[j]
				temp = (p.x(), p.y(), q.x(), q.y())
				if j == len(R) - 1:
					j = 0
				else:
					j = j + 1
				done = 0
		return temp


	def FindLowerTangent(self, L, R):
		pStuff = self.findRightMostPoint(L)
		qStuff = self.findLeftMostPoint(R)
		p = pStuff[0]
		i = pStuff[1]
		if i == len(L) - 1:
			i = 0
		else:
			i = i + 1
		q = qStuff[0]
		j = qStuff[1]
		if j == 0:
			j = len(R) - 1
		else:
			j = j - 1
		temp = (p.x(), p.y(), q.x(), q.y())
		done = 0
		while done == 0:
			done = 1
			# erase this
			number = self.findSlope(temp)
			otherNumber = self.findSlope((L[i].x(), L[i].y(), q.x(), q.y()))
			# erase this ^
			while self.findSlope(temp) < self.findSlope((L[i].x(), L[i].y(), q.x(), q.y())):
				p = L[i]
				temp = (p.x(), p.y(), q.x(), q.y())
				if i == len(L) - 1:
					i = 0
				else:
					i = i + 1
				done = 0
			while self.findSlope(temp) > self.findSlope((p.x(), p.y(), R[j].x(), R[j].y())):
				q = R[j]
				temp = (p.x(), p.y(), q.x(), q.y())
				if j == 0:
					j = len(R) - 1
				else:
					j = j - 1
				done = 0
		return temp

	# takes in a QLineF line object
	def findSlope(self, myLine):
		return ((myLine[1] - myLine[3]) / (myLine[0] - myLine[2]))

	# give list of points, returns a point object and index on where that point was
	def findRightMostPoint(self, myPointList):
		xToPointDictionary = {}
		sortedPoints = []
		numbers = []
		for point in myPointList:
			xToPointDictionary.update({point.x(): point})
			numbers.append(point.x())

		numbers.sort()
		for number in numbers:
			sortedPoints.append(xToPointDictionary.get(number))

		return [sortedPoints[-1], myPointList.index(sortedPoints[-1])]

	def findLeftMostPoint(self, myPointList):
		xToPointDictionary = {}
		sortedPoints = []
		numbers = []
		for point in myPointList:
			xToPointDictionary.update({point.x(): point})
			numbers.append(point.x())

		numbers.sort()
		for number in numbers:
			sortedPoints.append(xToPointDictionary.get(number))

		return [sortedPoints[0], myPointList.index(sortedPoints[0])]
