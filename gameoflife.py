#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Game of Life
от Дойчин Атанасов - VI 2008
"""

import os
import time
from Tkinter import *
import tkMessageBox
import gameoflife_patterns as patterns
re = patterns.re
#import copy

LIFEFORMS_RGEX = patterns.LIFE_FORMS_REGEXES
GAME_TITLE = "Game of Life"
BUTTON_START_GAME_TEXT = "Пусни"
BUTTON_END_GAME_TEXT = "Спри"
BUTTON_CLEAR_TEXT = "Изчисти"

SIZE_RESTRICTIONS = {
	'cellsize_lowest' : 5,
	'cellsize_highest' : 15,
	'canvsize_lowest' : 20,
	'canvsize_highest' : 100,
	}

DEFAULTS = {
	'advance_speed' : 150, #ms
	'world_width' : 50, #for the console play
	'world_height' : 30, #for the console play
	'cell_size' : 12,
	'canvas_width' : 30,
	'canvas_height' : 30,
	'movement_buttons_step' : 5,
	}


Point = patterns.Point

#
#	Not used
#
#def onMouseButtonHold( button, func ):
	#"""
	#Тъй като няма събитие <buttonHold-1> или подобно
	#button - бутона, който да се сложи onHold събитието
	#func - функцията, която да се изпълнява при задържане или клик
	#"""
	#button['state'] = ACTIVE
	#def output( event=None, *args, **kwargs ):
		#if button['state'] == ACTIVE:
			#func(event)
			#button.after( 200, output, event, *args, **kwargs )
		#else:
			#button['state'] = ACTIVE
	
	#def release(event):
		#button['state'] = NORMAL
	
	#def command():
		#if button['state'] == ACTIVE:
			#func(None)
	
	#button.bind( "<ButtonRelease-1>", release )
	#button['command'] = command
	#return output

# true - the cell is to be alive in the next generation
# false - you guess
def ruleDefaultAlive( nbrs ):
	"""	Всяка клетка с един или нула съседи умира от самота.
	Всяка клетка с четири или повече съседи умира от пренаселеност.
	Всяка клетка с два или три съседа остава жива."""
	return nbrs == 2 or nbrs == 3

def ruleDefaultDead( nbrs ):
	"""	Всяка клетка с три съседа оживява."""
	return nbrs == 3


class World(object):
	def __init__(self, aliveCellRule = ruleDefaultAlive, deadCellRule = ruleDefaultDead, width=DEFAULTS['world_width'], height=DEFAULTS['world_height']):
		"""
		width and height needed for the console output
		aliveCellRule and deadCellRule defines if cell lives or dies in the
		next generation
		"""
		self._genRed = set()
		self._genBlue = set()
		self.gens = ( self._genRed, self._genBlue )
		self.genNum = 0
		self._width = width
		self._height = height
		self._aliveRule = aliveCellRule
		self._deadRule = deadCellRule
	
	@property
	def width(self):
		return self._width
	
	@property
	def height(self):
		return self._height
	
	@property
	def aliveCellsRuleDescr(self):
		return self._aliveRule.__doc__[:]
	
	@property
	def deadCellsRuleDescr(self):
		return self._deadRule.__doc__[:]
	
	def _seed(self, seed):
		self.genNum = 0
		gen = self.getGenerations()[0]
		gen.clear()
		gen.update(set( seed ))
	
	def nextGen(self):
		initStart = time.time() #########
		times = {} #########
		oldgen, newgen = self.getGenerations()
		newgen.clear()
		# INIT TIMER
		times['Func Init'] = time.time() - initStart #########
		alivePoints = time.time() #########
		for point in oldgen:
			if self._aliveRule( self.countNbrs(point, oldgen) ):
				newgen.add(point)
		# ALIVE POINTS TIMER
		times['Alive Points Loop'] = time.time() - alivePoints #########
		deadPoints = time.time() #########
		for point in self.getSetNeighbours( oldgen ):
			if self._deadRule( self.countNbrs(point, oldgen) ):
				newgen.add(point)
		# DEAD POINTS TIMER
		times['Dead Points Loop'] = time.time() - deadPoints #########
		self.genNum += 1
		return times
		
	def getSetNeighbours(self, points):
		res = set()
		for point in points:
			nbrs = point.neighbours()
			for nbr in nbrs:
				if nbr not in points: res.add( nbr )
		return res
		
	def Print(self, times):
		printStart = time.time()
		oldgen = self.getGenerations()[0]
		os.system(['clear','cls'][os.name == 'nt'])
		for y in range( self.height ):
			print ""
			for x in range( self.width ):
				print "o" if Point(x,y) in oldgen else "-" + "",
		printStr = "\ngeneration: %d, generation size: %d, print time: %f"
		printLst = [ self.genNum , len(oldgen), time.time()-printStart ]
		for key, value in times.items():
			printStr += "\n" + str(key) + ": %f"
			printLst.append( value )
		print printStr % tuple(printLst)
	

	def ConsolePlay( self, breakpoint=-1 ):
		"""
		Пуска играта като изобразява поколенията в конзолата - monospaced фонд е препоръчителен.
		breakpoint - колко нови поколения ще бъдат показани. При breakpoint == -1 продължава докато
		не бъде спряна.
		"""
		times = { 'nextGen()' : 0, "0.05 barrier" : 0 }
		while breakpoint != self.genNum:
			self.Print(times)
			start = time.time()
			times.update( self.nextGen() )
			times['nextGen()'] = time.time() - start
			times['gen_size/time coef'] = self.genNum / (100*times['nextGen()'])
			if times['nextGen()'] > 0.05 and times['0.05 barrier'] == 0:
				times['0.05 barrier'] = len( self.getGenerations()[0] )
			if times['nextGen()'] < 0.05 and times['0.05 barrier'] != 0:
				times['0.05 barrier'] = 0
		
	def getGenerations(self):
		"""
		returns tuple ( the old generation, the one to be computed )
		"""
		current = self.genNum % 2
		next = abs( current-1 )
		current = self.gens[current]
		next = self.gens[next]
		return current, next
	
	def countNbrs(self, cell, generation):
		"""
		Basically does the same as some_set.intersection( other_set ) but faster
		"""
		nbrs = cell.neighbours()
		count = 0
		for nbr in nbrs:
			if nbr in generation:
				count += 1
		return count


class Drwaing(Frame):
	def __init__(self, world, root, size = DEFAULTS['cell_size'], width = DEFAULTS['canvas_width'], height = DEFAULTS['canvas_height']):
		Frame.__init__(self, root)
		self.parent = root
		self.world = world
		self.SIZE = size
		self._viewStartPoint = Point(0,0)
		self._canvasSizes = [ width, height ]
		self.aliveCellsColours = {
		'fill': 'yellow',
		'outline' : '#415670',
		}
		self.gridColour = "#3C5F6F"
		self.draw = self.drawPatternless
		self.__withPatterns = False
		self.refreshCanvas()
		self.go_flag = False
		self.advanceSpeed = DEFAULTS['advance_speed']
	
	def toggleDrawMethod(self):
		#self.draw = self.drawPatterns if self.draw is self.drawPatternless else self.drawPatternless
		self.__withPatterns = not self.__withPatterns
		self.draw = self.drawPatterns if self.__withPatterns else self.drawPatternless
		if not self.go_flag: self.draw()
		
	
	def userClick(self, event):
		"""
		Destributor. Decides wheather it should trigger DrawPoints or ErasePoints
		"""
		sp = self._viewStartPoint
		point = Point( event.x/self.SIZE + sp.x , event.y/self.SIZE + sp.y )
		gen = self.world.getGenerations()[0]
		if point in gen:
			self.canvas.bind( "<B1-Motion>", self.userErasePoints )
			self.userErasePoints(event)
		else:
			self.canvas.bind( "<B1-Motion>", self.userDrawPoints )
			self.userDrawPoints(event)
	
	def userDrawPoints(self, event):
		sp = self._viewStartPoint
		point = Point( event.x/self.SIZE + sp.x , event.y/self.SIZE + sp.y )
		gen = self.world.getGenerations()[0]
		if point in gen: return
		gen.add( point )
		self.putCell( point.x-sp.x, point.y-sp.y, **self.aliveCellsColours  )
	
	def userErasePoints(self, event):
		sp = self._viewStartPoint
		point = Point( event.x/self.SIZE + sp.x , event.y/self.SIZE + sp.y )
		gen = self.world.getGenerations()[0]
		if point not in gen: return
		gen.remove( point )
		targetedItem = self.canvas.find('closest',event.x,event.y)[0]
		if 'cell' not in self.canvas.gettags( targetedItem ): return
		self.canvas.delete( targetedItem )
	
	def refreshCanvas(self):
		width, height = self._canvasSizes
		if hasattr( self, 'canvas' ):
			for child in self.canvas.find_all(): self.canvas.delete(child)
			self.canvas.grid_forget()
			self.canvas.destroy()
		self.canvas = Canvas(self.parent, width = width * self.SIZE, height = height * self.SIZE, bg='#000000')
		self.canvas.bind( "<Button-1>", self.userClick )
		self.canvas.grid(column=2,row=1, columnspan=10, pady=10, padx=10)
		
		for line in xrange( height ):
			self.canvas.create_line( 0, line*self.SIZE, width*self.SIZE, line*self.SIZE, fill = self.gridColour, width=2, tag="grid_line" )
		
		for row in xrange( width ):
			self.canvas.create_line( row*self.SIZE, 0, row*self.SIZE, width*self.SIZE, fill = self.gridColour, width=2, tag="grid_line" )
		
		self.draw()

		
	def clear(self):
		for child in self.canvas.find_withtag('cell'): self.canvas.delete(child)
	
	def putCell(self, x, y, **kwargs ):
		x,y = self.SIZE * x, self.SIZE * y
		self.canvas.create_rectangle( x,y , x+self.SIZE - 1, y + self.SIZE - 1, tag='cell', **kwargs )
	
	def drawPatterns(self):
		self.clear()
		gen = self.world.getGenerations()[0]
		nullPoint = self._viewStartPoint
		width, height = self._canvasSizes
		endPoint = Point( nullPoint.x + width, nullPoint.y + height )
		
		def inDrawArea(point):
			return point.x >= nullPoint.x and point.x < endPoint.x and point.y >= nullPoint.y and point.y < endPoint.y
		
		pointsToDraw = set( filter( inDrawArea, gen ) )
		drawnPoints = set()
		
		for point in pointsToDraw:
			if point in drawnPoints: continue
			for pattern in patterns.PATTERNS:
				topLeftPoint = patterns.getTopLeftPoint( point, pattern )
				alive, dead = patterns.stringToPoints( pattern, topLeftPoint )
				if pointsToDraw.issuperset( alive ) and pointsToDraw.intersection( dead ) == set():
					for drawpoint in alive:
						self.putCell( drawpoint.x - nullPoint.x, drawpoint.y - nullPoint.y, fill="red" )
						drawnPoints.add( drawpoint )
			if point in drawnPoints: continue
			self.putCell( point.x - nullPoint.x, point.y - nullPoint.y, **self.aliveCellsColours )

	#def drawPatterns(self):
		#self.clear()
		#gen = self.world.getGenerations()[0]
		#nullPoint = self._viewStartPoint
		#width, height = self._canvasSizes
		#endPoint = Point( nullPoint.x + width, nullPoint.y + height )
		
		#def inDrawArea(point):
			#return point.x >= nullPoint.x and point.x < endPoint.x and point.y >= nullPoint.y and point.y < endPoint.y
		
		#pointsToDraw = set( filter( inDrawArea, gen ) )
		#drawnPoints = set()
		
		#if not LIFEFORMS_RGEX.has_key( width ):
			#LIFEFORMS_RGEX[ width ] = {}
			#for form in patterns.PATTERNS:
				#dotsCount = width + 1 - len( form.splitlines()[0] )
				#LIFEFORMS_RGEX[ width ][ form.replace('*', '.').replace( '\n', r'(.|\n){%d,%d}' % ( dotsCount, dotsCount ) )  ] = form
		
		#boardStr = ""
		#for y in xrange( nullPoint.y, nullPoint.y + width + 1 ):
			#for x in xrange( nullPoint.x, nullPoint.x + height + 1 ):
				#point = Point(x,y)
				#boardStr += "o" if point in pointsToDraw else "-"
			#boardStr += "\n"
		
		#os.system(['clear','cls'][os.name == 'nt'])
		#print boardStr
		
		
		#for regEx in LIFEFORMS_RGEX[ width ]:
			#for match in re.finditer( regEx, boardStr ):
				#start = match.start()
				#y = 0 + boardStr[:start].count('\n')
				#x = 0
				#start -= 2
				#while boardStr[start] != '\n' and start != 0:
					#x += 1
					#start -= 1
				
				#topLeft = Point(x,y)
				#points = patterns.stringToAlivePoints( LIFEFORMS_RGEX[ width ][ regEx ], topLeft )
				#for point in points:
					#self.putCell( point.x - nullPoint.x, point.y - nullPoint.y, fill="red" )
					#pointsToDraw.remove( point )
				
		#for point in pointsToDraw:
			#self.putCell( point.x - nullPoint.x, point.y - nullPoint.y, **self.aliveCellsColours )
		
		


	def drawPatternless(self):
		self.clear()
		gen = self.world.getGenerations()[0]
		nullPoint = self._viewStartPoint
		width, height = self._canvasSizes
		endPoint = Point( nullPoint.x + width, nullPoint.y + height )
		
		def inDrawArea(point):
			return point.x >= nullPoint.x and point.x < endPoint.x and point.y >= nullPoint.y and point.y < endPoint.y
		
		pointsToDraw = filter( inDrawArea, gen )
		
		for point in pointsToDraw:
			self.putCell( point.x - nullPoint.x, point.y - nullPoint.y, **self.aliveCellsColours )
	
	def advance(self):
		if not self.go_flag: return
		timer = time.time()
		self.world.nextGen()
		#print time.time() - timer ###########
		#drawTimer = time.time() ###########
		self.draw()
		#print time.time() - drawTimer ###########
		timer = (int)(100*(time.time()-timer))
		difference = 1 if self.advanceSpeed == 0 else ( (self.advanceSpeed - timer) if timer < self.advanceSpeed else 10 )
		self.after( difference  , self.advance )
	
	def changeGoFlag(self):
		self.go_flag = not self.go_flag
		if self.go_flag: self.after( 100, self.advance )
		return self.go_flag


class Game(object):
	def __init__(self):
		"""
		Създава обект-игра с Tkinter GUI.
		За да се 'запали' - използвайте метода run( self )
		"""
		self.tk = Tk()
		self.tk.title(GAME_TITLE)
		self.tk.geometry("+200+200")
		self.tk.bind( "<Return>" , lambda e: self.changeGoState() )
		self.tk.bind( "<Up>", lambda e: self.pressDirectionButton( "up" ) )
		self.tk.bind( "<Down>", lambda e: self.pressDirectionButton( "down" ) )
		self.tk.bind( "<Left>", lambda e: self.pressDirectionButton( "left" ) )
		self.tk.bind( "<Right>", lambda e: self.pressDirectionButton( "right" ) )
		self.world = World()
		self.board = Drwaing( self.world, self.tk )
		self.stateButton = Button( self.tk, command = self.changeGoState, width=6, text = BUTTON_START_GAME_TEXT )
		self.stateButton.grid( column=2, row=3, pady=10, padx=10 )
		
		self.clearButton = Button( self.tk, command = self.clearGame, text = BUTTON_CLEAR_TEXT )
		self.clearButton.grid( column=3, row=3, pady=10, padx=10 )
		
		self.informationLabel = Label( self.tk, justify=LEFT, width = 20 )
		self.informationLabel.grid( column=4, row=3, pady=2, padx=2, sticky=W )
		
		self.state = False
		self.refreshInfo()
		
		self.renderMenu()
		self.moveButtonsStep = DEFAULTS['movement_buttons_step']

	
	def run(self):
		"""
		Пуска играта. Приятно забавление ;)
		"""
		self.tk.mainloop()
		
	
	def refreshInfo(self):
		self.informationLabel['text'] = "Поколение: %d\nБрой клетки: %d" % ( self.world.genNum, len( self.world.getGenerations()[0] ) )
		if self.state: self.tk.after( 100, self.refreshInfo )
	
	
	def pressDirectionButton(self, evalStr ):
		for x in xrange( self.moveButtonsStep ):
			self.board._viewStartPoint = eval( "self.board._viewStartPoint."+evalStr )
		if not self.state: self.board.draw()
	
	def clearGame(self):
		self.board.clear()
		self.board._viewStartPoint = Point(0,0)
		self.world._seed( [] )
		self.refreshInfo()
		if self.state: self.changeGoState()
	
	def changeGoState(self):
		self.state = self.board.changeGoFlag()
		self.refreshInfo()
		self.stateButton['text'] = BUTTON_END_GAME_TEXT if self.state else BUTTON_START_GAME_TEXT
	
	def renderMenu(self):
		menu = Menu(self.tk)
		game = Menu(menu)
		game.add_command( label = "Нова игра", command = self.clearGame )
		game.add_command( label = "Изход", command = self.quit )
		
		menu.add_cascade(label = "Игра", menu = game)
		
		prefs = Menu(menu)
		prefs.add_command( label = "Размери", command = lambda: options_changeSizes( self ) )
		prefs.add_command( label = "Правила", command = lambda: options_changeRules( self ) )
		prefs.add_command( label = "Скорост", command = lambda: options_changeSpeed( self ) )
		prefs.add_command( label = "Оцветяване", command = self.board.toggleDrawMethod )
		menu.add_cascade( label = "Настройки", menu = prefs )
		
		about = Menu(menu)
		about.add_command( label = "Правила", command = lambda: tkMessageBox.showinfo("Правила",
			"* За клетка, която е жива:\n\n%s\n\n* За клетка, която е мъртва:\n\n%s" % 
						( self.world.aliveCellsRuleDescr, self.world.deadCellsRuleDescr ))
			)
		menu.add_cascade( label = "За Играта", menu = about )
		
		self.tk['menu'] = menu
	
	def quit(self):
		self.board.grid_forget()
		self.board.destroy()
		self.tk.quit()
		self.tk.state('withdrawn')


class OptionsWindow(object):
	"""
	Родител на всички прозорци с настройки
	"""
	def __init__(self, parent, titleTxt):
		self.parent = parent
		self.tk = Toplevel()
		self.tk.geometry("+250+250")
		self.tk.title( GAME_TITLE + " | %s" % titleTxt )
		self.tk.bind( "<Escape>", lambda e: self.quit() )
		self.tk.bind( "<Return>", lambda e: self.okButton.invoke() )
		
		self.frame = Frame(self.tk)
		self.frame.grid(column=0, row=0, pady=35, padx=35 )
		self.okButton = Button( self.frame, width=5, text="OK" )
		self.cancelButton = Button( self.frame, width=5, text="Cancel", command = self.quit )
		self.applyButton = Button( self.frame, width=5, text="Apply" )
		
	def quit(self):
		self.tk.destroy()
		#self.tk.state('withdrawn')

class options_changeSizes(OptionsWindow):
	def __init__(self, parent):
		OptionsWindow.__init__(self, parent, "Размери")
		
		self.sizeLabel = Label( self.frame, text="Големина на клетката в пиксели (%d-%d):" % (SIZE_RESTRICTIONS['cellsize_lowest'], SIZE_RESTRICTIONS['cellsize_highest']) )
		self.sizeLabel.grid( column=0, row=0, columnspan=2, pady=2, padx=2 )

		self.sizeEntry = Entry( self.frame, width=3, background="#FFFFFF" )
		self.sizeEntry.insert( 0, self.parent.board.SIZE )
		self.sizeEntry.grid( column=2, row=0, pady=2, padx=2 )
		
		width, height = self.parent.board._canvasSizes[:]
		
		self.canvasSizesLabel = Label( self.frame, text="Големина на полето в клетки (%d-%d)" % (SIZE_RESTRICTIONS['canvsize_lowest'], SIZE_RESTRICTIONS['canvsize_highest']) )
		self.canvasSizesLabel.grid( column=0, row=1, columnspan=3, pady=10, padx=2 )
		
		self.widthLabel = Label( self.frame, text="width:" )
		self.widthLabel.grid( column=0, row=2, pady=10, padx=2, sticky=E )
		
		self.heightLabel = Label( self.frame, text="height:" )
		self.heightLabel.grid( column=0, row=3, pady=10, padx=2, sticky=E )
		
		self.widthEntry = Entry( self.frame, width=3, background="#FFFFFF" )
		self.widthEntry.insert( 0, width )
		self.widthEntry.grid( column=1, row=2, pady=2, padx=2, sticky=W )
		
		self.heightEntry = Entry( self.frame, width=3, background="#FFFFFF" )
		self.heightEntry.insert( 0, height )
		self.heightEntry.grid( column=1, row=3, pady=2, padx=2, sticky=W )
		
		self.okButton['command'] = self.triggerOkButton
		self.okButton.grid( column=0, row=4, pady=2, padx=2 )
		
		#self.cancelButton['command'] = self.quit
		self.cancelButton.grid( column=1, row=4, pady=2, padx=2 )
		
		self.applyButton['command'] = self.triggerApplyButton
		self.applyButton.grid( column=2, row=4, pady=2, padx=2 )
	
	def triggerOkButton(self):
		self.triggerApplyButton()
		self.quit()
	
	
	def _valueValidator(self, value, keyStr ):
		"""
		Хвърля ValueError при неуспешно валидиране
		"""
		if value < SIZE_RESTRICTIONS[ keyStr+"_lowest" ] or value > SIZE_RESTRICTIONS[ keyStr+"_highest" ]: raise ValueError
	
	def triggerApplyButton(self):
		try:
			size = int( self.sizeEntry.get() )
			width = int( self.widthEntry.get() )
			height = int( self.heightEntry.get() )
			self._valueValidator( size, "cellsize" )
			self._valueValidator( height, "canvsize" )
			self._valueValidator( width, "canvsize" )
		except ValueError:
			tkMessageBox.showinfo("Искам си числата!", "size, width и height трябва да са числа в обозначените граници!")
			return
		else:
			self.parent.board.SIZE = size
			self.parent.board._canvasSizes = [width, height][:]
			self.parent.board.refreshCanvas()


class options_changeRules(OptionsWindow):
	def __init__(self, parent):
		OptionsWindow.__init__(self, parent, "Правила")
		
		maxNbrs = len( Point(42,42).neighbours() )
		
		Label( self.frame, text="* За живите клетки:" ).grid( column=0, row=0, columnspan=4, pady=2, padx=2, sticky=W )
		Label( self.frame, text="* За мъртвите клетки:" ).grid( column=0, row=2, columnspan=4, pady=2, padx=2, sticky=W )
		
		Label( self.frame, text="\tНеобходим брой съседи за да остане жива:" ).grid( column=0, row=1, columnspan=3, pady=2, sticky=E )
		Label( self.frame, text="\tНеобходим брой съседи за да оживее:" ).grid( column=0, row=3, columnspan=3, pady=2, sticky=E )
		
		self.aliveCellsEntry = Entry( self.frame, width=10, background="#FFFFFF" )
		self.aliveCellsEntry.grid( column=4, row=1, pady=2, sticky=W )
		
		self.deadCellsEntry = Entry( self.frame, width=10, background="#FFFFFF" )
		self.deadCellsEntry.grid( column=4, row=3, pady=2, sticky=W )
		
		aliveEntryStr = ""
		deadCellsEntryStr = ""
		for nbrsCount in xrange(maxNbrs+1):
			if self.parent.world._aliveRule( nbrsCount ):
				aliveEntryStr += "," if len(aliveEntryStr) > 0 else ""
				aliveEntryStr += str(nbrsCount)
			if self.parent.world._deadRule( nbrsCount ):
				deadCellsEntryStr += "," if len(deadCellsEntryStr) > 0 else ""
				deadCellsEntryStr += str(nbrsCount)
		
		self.aliveCellsEntry.insert( 0, aliveEntryStr )
		self.deadCellsEntry.insert( 0, deadCellsEntryStr )
		
		self.cancelButton.grid( column=1, row=4, pady=2, padx=2 )
		self.okButton.grid( column=0, row=4, pady=2, padx=2 )
		self.applyButton.grid( column=2, row=4, pady=2, padx=2 )
		
		self.applyButton['command'] = self.triggerApplyButton
		self.okButton['command'] = self.triggerOkButton
	
	def triggerApplyButton(self):
		maxNbrs = len( Point(42,42).neighbours() )
		
		try:
			aliveNbrs = map( int, self.aliveCellsEntry.get().split(',') )
			deadNbrs = map( int, self.deadCellsEntry.get().split(',') )
			for value in aliveNbrs + deadNbrs:
				if value < 0 or value > maxNbrs: raise ValueError
		except ValueError:
			tkMessageBox.showinfo("Грешчица!", 
						"Въведете разумни стойности, моля!")
			return
		else:
			self.parent.world._deadRule = lambda nbrs : nbrs in deadNbrs
			self.parent.world._deadRule.__doc__ = "Мъртва клетка със %s брой съседи оживява." % str( deadNbrs )
			
			self.parent.world._aliveRule = lambda nbrs: nbrs in aliveNbrs
			self.parent.world._aliveRule.__doc__ = "Жива клетка със %s брой съседи остава жива." % str( aliveNbrs )
	
	def triggerOkButton(self):
		self.triggerApplyButton()
		self.quit()

class options_changeSpeed(OptionsWindow):
	def __init__(self, parent):
		OptionsWindow.__init__(self, parent, "Скорост")
		
		self.worldLabel = Label( self.frame, text="Скорост на развитие на света в ms,\nнула за максимална:" )
		self.worldLabel.grid( column=0, row=0, columnspan=3, pady=2, padx=2 )
		
		self.btnsLabel = Label( self.frame, text="Стъпка на бутоните за движение (1+):" )
		self.btnsLabel.grid( column=0, row=1, columnspan=3, pady=2, padx=2 )
		
		self.worldSpeedEntry = Entry( self.frame, width=5, background="#FFFFFF" )
		self.worldSpeedEntry.insert( 0, self.parent.board.advanceSpeed )
		self.worldSpeedEntry.grid( column=3, row=0, pady=2, padx=2 )
		self.worldSpeedEntry.focus()
		
		self.btnsSpeedEntry = Entry( self.frame, width=5, background="#FFFFFF" )
		self.btnsSpeedEntry.insert( 0, self.parent.moveButtonsStep )
		self.btnsSpeedEntry.grid( column=3, row=1, pady=2, padx=2 )
		
		self.okButton['command'] = self.triggerOkButton
		self.okButton.grid( column=1, row=2, pady=2, padx=2 )
		
		self.cancelButton.grid( column=2, row=2, pady=2, padx=2 )
	
	def triggerOkButton(self):
		try:
			speed = int( self.worldSpeedEntry.get() )
			btnOffset = int( self.btnsSpeedEntry.get() )
			if speed < 0 or btnOffset < 1: raise ValueError
		except ValueError:
			tkMessageBox.showinfo("Искам число!", 
						"Времето и отместването трябва да бъдат положителни числа!")
			return
		else:
			self.parent.board.advanceSpeed = speed
			self.parent.moveButtonsStep = btnOffset
			self.quit()
		

if __name__ == '__main__':
	game = Game()
	game.run()