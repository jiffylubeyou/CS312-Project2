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

		if len(sortedPoints) == 1:
			return sortedPoints

		leftHalf = sortedPoints[:len(sortedPoints)//2]
		rightHalf = sortedPoints[len(sortedPoints)//2:]
		# after this point, they should begin to be clockwise
		leftHalf = self.compute_hull(leftHalf, pause, view)
		rightHalf = self.compute_hull(rightHalf, pause, view)

		# this combined should be the clockwise order of things
		combined = []
		upperTangentTuple = self.FindUpperTangent(leftHalf, rightHalf)

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



		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		upperTangentTuple = self.FindUpperTangent(leftHalf,rightHalf)
		point1 = QPointF(upperTangentTuple[0], upperTangentTuple[1])
		point2 = QPointF(upperTangentTuple[2], upperTangentTuple[3])
		line = QLineF(point1, point2)
		self.showTangent([line], RED)


		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))


	# takes in two arrays, both of which are an array of points, and returns a line object
	def FindUpperTangent(self, L, R):
		pStuff = self.findRightMostPoint(L)[0]
		qStuff = self.findLeftMostPoint(R)[0]
		p = pStuff[0]
		i = pStuff[1]
		q = qStuff[0]
		j = qStuff[1]
		temp = (p.x(), p.y(), q.x(), q.y())
		done = 0
		while done == 0:
			done = 1
			while self.findSlope(temp) > self.findSlope((L[i].x(), L[i].y(), q.x(), q.y())):
				p = L[i]
				temp = (p.x(), p.y(), q.x(), q.y())
				i = i - 1
				done = 0
			while self.findSlope(temp) < self.findSlope((p.x(), p.y(), R[j].x(), R[j].y())):
				q = R[j]
				temp = (p.x(), p.y(), q.x(), q.y())
				j = j + 1
				done = 0
		return temp


	def FindLowerTangent(self, L, R):
		p = L[-1]
		q = R[0]
		temp = (p.x(), p.y(), q.x(), q.y())
		done = 0
		i = -2
		j = 1
		while done == 0:
			done = 1
			while self.findSlope(temp) > self.findSlope((L[i].x(), L[i].y(), q.x(), q.y())):
				p = L[i]
				temp = (p.x(), p.y(), q.x(), q.y())
				i = i - 1
				done = 0
			while self.findSlope(temp) < self.findSlope((p.x(), p.y(), R[j].x(), R[j].y())):
				q = R[j]
				temp = (p.x(), p.y(), q.x(), q.y())
				j = j + 1
				done = 0
		return temp

	# takes in a QLineF line object
	def findSlope(self, myLine):
		return (myLine[1] - myLine[3] / (myLine[0] - myLine[2]))

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
