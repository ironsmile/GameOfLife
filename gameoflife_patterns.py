#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Seed legend:
	'-' means the cell MUST be unpopulated
	'o' means the cell MUST be populated
	'*' wildcard
"""
import re
import copy

class Point(tuple):
	def __new__(cls, x, y):
		return tuple.__new__(cls, (x, y))

	def __getattr__(self, attr):
		if attr == 'x': return self[0]
		elif attr == 'y': return self[1]
		else: return object.__getattr__(self, attr)
	
	@property
	def up(self): return Point(self.x, self.y - 1)
	@property
	def down(self): return Point(self.x, self.y + 1)
	@property
	def left(self): return Point(self.x - 1, self.y)
	@property
	def right(self): return Point(self.x + 1, self.y)
	

	def neighbours(self):
		"""
		Returns list with all the neighbours of the point
		"""# по отиз начин работи по - бързо от колкото с up.left, left... etc
		res = []
		for x in xrange(self.x - 1, self.x + 2):
			res.append( Point( x, self.y+1 ) )
			res.append( Point( x, self.y - 1 ) )
		res.append( Point(self.x -1, self.y) )
		res.append( Point(self.x+1, self.y) )
		return res

pattersf = open('patterns', 'r').readlines()
PATTERNS_MASTER_SEED = reduce( lambda a,b: a+b , pattersf, "" )

def stringToPoints( string, topLeftPoint ):
	"""
	Връща tuple :
		( множество-от-клетки-които-трябва-да-са-живи, такива-които-трябва-да-са-мъртви )
	"""
	x,y = topLeftPoint
	alivePoints = stringToAlivePoints( string, topLeftPoint )
	deadPoints = set()
	for symb in string:
		if symb == "-": deadPoints.add( Point(x,y) )
		elif symb == "\n":
			y += 1
			x = topLeftPoint.x-1
		x += 1
	
	return alivePoints, deadPoints

def stringToAlivePoints( string, topLeftPoint ):
	x,y = topLeftPoint
	alivePoints = set()
	for symb in string:
		if symb == "o": alivePoints.add( Point(x,y) )
		elif symb == "\n":
			y += 1
			x = topLeftPoint.x-1
		x += 1
	return alivePoints


def pointsToSring( aliveSet, deadSet ):
	widthMax, widthMin = maxAttr( deadSet, 'x' ), minAttr( deadSet, 'x' )
	heightMax, heightMin = maxAttr( deadSet, 'y' ), minAttr( deadSet, 'y' )
	
	output = ""
	for y in xrange( heightMin, heightMax+1 ):
		for x in xrange( widthMin, widthMax+1 ):
			thisPoint = Point( x,y )
			if thisPoint in aliveSet: output += "o"
			elif thisPoint in deadSet: output += "-"
			else: output += "*"
		output += "\n"
	
	return output[:-1]

def maxAttr( pointsSet, attr ):
	pointsSet = copy.copy( pointsSet )
	max = getattr( pointsSet.pop(), attr )
	for point in pointsSet:
		if max < getattr( point, attr ):
			max = getattr( point, attr )
	return max

def minAttr( pointsSet, attr ):
	pointsSet = copy.copy( pointsSet )
	min = getattr( pointsSet.pop(), attr )
	for point in pointsSet:
		if min > getattr( point, attr ):
			min = getattr( point, attr )
	return min

def strReverser( string ):
	output = [ symb for symb in string ]
	output.reverse()
	return reduce( lambda x,y: x+y, output )

def mirroredPatter( pattern ):
	"""
	Връща стринг, огледален на pattern
	"""
	return reduce( lambda x,y: x+'\n'+y, map( strReverser, pattern.splitlines() ) )


def rotateRight( pointsSet ):
	return set( map( lambda p: Point( p.y, p.x ), pointsSet ) )

def rotatePattern( pattern ):
	alive, dead = stringToPoints( pattern, Point(0,0) )
	alive, dead = map( rotateRight, (alive, dead) )
	return mirroredPatter( pointsToSring( alive, dead ) )


def patternSeedToDict( patternsStr ):
	result = {}
	patternMatcher = re.compile( r'(?<=<pattern>\n)(?P<rotation>.*\n)(?P<exactStr>(.|\n)*?)(?=\n</pattern>)' )
	matchIter = re.finditer( patternMatcher, patternsStr )
	for match in matchIter:
		groupsDict = match.groupdict()
		result[ groupsDict['exactStr'] ] = groupsDict['rotation']
		mirrored = None
		if "Rotate-none" in groupsDict['rotation']: continue
		elif "-mirror" in groupsDict['rotation']:
			mirrored = mirroredPatter( groupsDict['exactStr'] )
			result[ mirrored ] = groupsDict['rotation']
		
		rotations = groupsDict['rotation'].strip()[-1:]
		try:
			rotations = int( rotations )
		except ValueError: continue
		
		#print rotations
		rotated = groupsDict['exactStr']
		mirRotated = None if mirrored == None else mirroredPatter( groupsDict['exactStr'] )
		for rts in xrange( rotations ):
			rotated = rotatePattern( rotated )
			result[ rotated ] = groupsDict['rotation']
			if mirrored != None:
				mirRotated = rotatePattern( mirRotated )
				result[ mirRotated ] = groupsDict['rotation']
	
	return result

PATTERNS = list( patternSeedToDict( PATTERNS_MASTER_SEED ) )

def getTopLeftPoint( fristAliveCell, pattern ):
	"""
	Добре дошли в С++ света...
	"""
	x,y = 0,0
	
	loop_x = 0
	while pattern[ loop_x ] != "o":
		x += 1
		if pattern[ loop_x ] == "\n":
			y += 1
			x = 0
		
		loop_x += 1
	
	return Point( fristAliveCell.x - x, fristAliveCell.y - y )


LIFE_FORMS_REGEXES = {}