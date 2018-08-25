# -*- coding: utf-8 -*-
"""
Created on Sun Aug 19 10:42:48 2018

@author: Noah
"""

from random import shuffle 
import sys

#0 = no tiles
#1-5 = colored tiles
#6 = first center marker

#constants
FIRST_MARKER = 6
TILES_PER_FACTORY = 4
PLAYERS_TO_FACTORIES = {1:3, 2:5, 3:7, 4:9}
NUM_PLAYERS = 1
'''
TODO
move input verification to public and private board functions
allow combination input (e.g. 1,2,3)

'''
#CLASSES


class tileDrop():
    def __init__(self):
        self.tiles = []
        
    def selectTiles(self, color):
        if color not in self.tiles:
            print('That color is not in that pile, you doofus!')
            return [[],[]]
        else:
            selectedTiles = [t for t in self.tiles if t==color]
            otherTiles = [t for t in self.tiles if t!=color]
            return(selectedTiles, otherTiles)
    
    def addTiles(self, newTiles):
        self.tiles = self.tiles + newTiles

class factory(tileDrop):
    
    def __init__(self):
        super().__init__()
    
    def selectTiles(self, color):
        selectedTiles, otherTiles = super().selectTiles(color)
        if len(selectedTiles) > 0:
            self.tiles = []
        return selectedTiles, otherTiles
        
        
        
class boardCenter(tileDrop):
    
    def __init__(self):
        super().__init__()
        
    def selectTiles(self, color):
        selectedTiles, otherTiles = super().selectTiles(color)
        
        if FIRST_MARKER in self.tiles:
            selectedTiles = selectedTiles + [FIRST_MARKER]
        
        self.tiles = [t for t in self.tiles if t not in selectedTiles]
        
        print(selectedTiles)
        return(selectedTiles)
        
    

        
class publicBoard():
    '''sets up and handles factories, tile bag, and center'''
    
    def __init__(self, numDuplicateTiles, numFactories):
        self.bag = list(range(1,6)) * numDuplicateTiles
        shuffle(self.bag)
        self.factories = [factory() for f in range(numFactories)]
        self.center = boardCenter()
        self.discard = []
        
    def selectTiles(self, tileDropLabel, color):
        if tileDropLabel == 'c':
            selectedTiles = self.center.selectTiles(color)
            
        else:
            tileDropNum = int(tileDropLabel) - 1
            
            try:
                selectedTiles, otherTiles = self.factories[tileDropNum].selectTiles(color)
                self.center.addTiles(otherTiles)
                
            except IndexError:
                print('Wtf this input should already have been validated!')
                selectedTiles = []
                
        return(selectedTiles)
                
                
    def deal(self):
        remainingTiles = len(self.center.tiles) + sum([len(factory.tiles) for factory in self.factories])
        if remainingTiles > 0:
            print("Can't deal until all tiles have been selected!")
        else:
            [factory.addTiles(self.drawFromBag(TILES_PER_FACTORY)) for factory in self.factories]
            self.center.addTiles([FIRST_MARKER])
            
    def drawFromBag(self, numToDraw):
        drawnTiles = []
        for drawIdx in range(numToDraw):
            if len(self.bag) == 0:
                self.bag = self.discard
                shuffle(self.bag)
                self.discard = []
            
            drawnTiles.append(self.bag.pop())
            
        return drawnTiles
    
    def getValidChoices(self):
        #determine which tile drops can be selected to gain tiles
        
        validChoices = [str(fnum + 1) for fnum, fact in enumerate(self.factories) if len(fact.tiles) > 0]
        
        if len([tile for tile in self.center.tiles if tile != FIRST_MARKER]) > 0:
            validChoices.append('c')
        return validChoices
    
    def validatePileChoice(pileChoice, self):
        
        validChoices = [str(fnum + 1) for fnum, fact in enumerate(self.factories) if len(fact.tiles) > 0]
        
        if len([tile for tile in self.center.tiles if tile != FIRST_MARKER]) > 0:
            validChoices.append('c')
            
        if pileChoice in validChoices:
            errorMessage = ''
        else:
            errorMessage = 'Not enough tiles there! Try again.'
        
        return(errorMessage)
        
        
    def validateColorChoice(pileChoice, colorChoice, self):
        validChoices = [str(fnum + 1) for fnum, fact in enumerate(self.factories) if len(fact.tiles) > 0]
        
        if len([tile for tile in self.center.tiles if tile != FIRST_MARKER]) > 0:
            validChoices.append('c')
            
        if pileChoice in validChoices:
            errorMessage = ''
        else:
            errorMessage = 'Not enough tiles there! Try again.'
        
        return(errorMessage)
        
                
    def disp(self):
        print('Board')
        print('Center: {}'.format(self.center.tiles))
        
        for f_i, factory in enumerate(self.factories):
            print('Factory {}: {}'.format(f_i + 1, factory.tiles))
        print('\n')
        
    def checkRoundEnd(self):
        maxFactoryTiles = max([len(p) for p in [f.tiles for f in self.factories]])
        
        if maxFactoryTiles == 0 and len([tile for tile in self.center.tiles if tile != FIRST_MARKER]) == 0:
            return(True)
        else:
            return(False)
        
class playerBoard():
    
    def __init__(self):
        self.wall = [[0] * 5 for i in range(5)]
        self.wallTemplate = [[(color - row) % 5 + 1 for color in range(1,6)] for row in range(1,6)]
        self.floorLine = [0] * 7
        self.floorPenalties = [-1, -1, -2, -2, -2, -3, -3]      
        self.load = [[0] * row for row in range(1,6)]
        self.score = 0
        
    def disp(self):
        numFloorSpaces = [12, 9, 6, 3, 0]
        dispLoad = [' ' * n + str(e) for e, n in zip(self.load, numFloorSpaces)]
        
        print('  Loading Area        Wall         Template')
        [print('{} {} {}'.format(row[0], row[1], row[2])) for row in zip(dispLoad, self.wall, self.wallTemplate)] #change to letters later?
       
        print('\n')
        print('{} {}'.format('Penalties', self.floorPenalties))
        

        print('{} {} '.format('Floor    ', str(self.floorLine).replace(',', ', ')))
        print('Current Score: {}'.format(self.score))
        
    def roundScore(self, newIndices):
        roundPoints= 0
        
        #get points for placing new tiles
        for newIdx in newIndices:
            curRow, curCol = newIdx
            roundPoints += 1
            
            #check to the left
            for col in range(curCol - 1,-1,-1):
                if self.wall[curRow][col] == 0:
                    break
                else:
                    roundPoints += 1
            #check to the right        
            for col in range(curCol + 1, 5, 1):
                if self.wall[curRow][col] == 0:
                    break
                else:
                    roundPoints += 1
                    
            #check up        
            for row in range(curRow + 1, 5, 1):
                if self.wall[row][curCol] == 0:
                    break
                else:
                    roundPoints += 1
            
            #check down      
            for row in range(curRow - 1, -1, -1):
                if self.wall[row][curCol] == 0:
                    break
                else:
                    roundPoints += 1
                    
        #add floor penalty
        floorPairs = zip([int(tile > 0) for tile in self.floorLine], self.floorPenalties)
        
        penalty = sum(floorPair[0]*floorPair[1] for floorPair in floorPairs)
        roundPoints += penalty
        
        return(roundPoints)
            
        
        
    def roundEnd(self):
        
        #add tiles
        addedIndices = []
        for row in range(5):
            if len([e for e in self.load[row] if e == 0]) == 0:
                newColor = self.load[row][0]
                col = [i for i, e in enumerate(self.wallTemplate[row]) if e == newColor][0]
                self.wall[row][col] = newColor
                addedIndices.append([row, col])
        
        
        #calculate round score
        self.score += self.roundScore(addedIndices)
        
        #remove tiles from load and floor
        loadRowsToClear = [indices[0] for indices in addedIndices]
        discardedTiles = []
        for loadRow in loadRowsToClear:
            discardedTiles.extend([tile for tile in self.load[loadRow] if tile > 0])
            self.load[loadRow] = [0 for tile in self.load[loadRow]]
        
        discardedTiles.extend([tile for tile in self.floorLine if tile > 0 and tile != FIRST_MARKER])
        self.floorLine = [0 for tile in self.floorLine]
    
        return(discardedTiles)

            
        
    def addTiles(self, newTiles, row):
        '''attempts to add tiles to a particular row; returns outcome and remaining tiles'''
        
        if row == 'f':
            if len(newTiles) > len([e for e in self.floorLine if e == 0]):
                message = ('Wow you really screwed up. Theres not enough'
                ' room in your floor! Not even sure what to do...')
            else:
                firstOpenSpot = min(i for i,e in enumerate(self.floorLine) if e == 0)
                self.floorLine[firstOpenSpot:firstOpenSpot+len(newTiles)] = newTiles
                newTiles = []
                message = 'You shouldnt be seeing this message, line 149'
        
        else:
            
            if FIRST_MARKER in newTiles:
                firstOpenSpot = min(i for i,e in enumerate(self.floorLine) if e == 0)
                self.floorLine[firstOpenSpot] = FIRST_MARKER
                newTiles = [t for t in newTiles if t != FIRST_MARKER]
            
            curRowNum = int(row)-1
            curLoadRow = self.load[curRowNum]    
            curWallRow = self.wall[curRowNum]
            if any(tile > 0 and tile not in newTiles for tile in curLoadRow):
                message = 'That loading row already has tiles of a different color! Try again.'               
            elif any(tile == newTiles[0] for tile in curWallRow):
                message = 'That wall row already has that color tile! Try again.'
            else:
                #numSpotsFree = len([s for s in curLoadRow if s == 0])
                #numAddedTiles = min(numSpotsFree, len(newTiles)) #problem w/ this logic, combined w/ indexing below
                freeSpots = reversed([ix for ix, tile in enumerate(curLoadRow) if tile == 0])
                
                
                #curLoadRow[len(curLoadRow) - numAddedTiles:] = [newTiles.pop() for t in range(numAddedTiles)]
                '''
                for tileNum in range(len(newTiles)):
                    try:
                        newTileIdx = freeSpots[tileNum]
                    except IndexError:
                        break
                    curLoadRow[newTileIdx] = newTiles.pop()
                    '''
                    
                for spot in freeSpots:
                    if len(newTiles) == 0:
                        break
                    curLoadRow[spot] = newTiles.pop()
                
                message = 'Where do you want to put your remaining tiles? They are {}'.format(newTiles)
                
            
        return(message, newTiles)
    
    
    def getNumCompleteRows(self):        
        return sum([all([tile > 0 for tile in self.wall[row]]) for row in range(5)])
    
    def getNumCompleteCols(self):
        return sum([all([row[col] > 0 for row in self.wall]) for col in range(5)])

    def getNumCompleteColors(self):
        allTiles=[]
        [allTiles.extend(row) for row in self.wall]
        numEachColor = [sum([tile == color for tile in allTiles]) for color in range(1,6)]
        return sum([count == 5 for count in numEachColor])
    
    def addBonuses(self):
        self.score += self.getNumCompleteRows() * 2
        self.score += self.getNumCompleteCols() * 7
        self.score += self.getNumCompleteColors() * 10
            
        
class game():
    '''class containing public and private boards; handles player input'''
    def __init__(self, tileDuplicates = 20, numPlayers = 2):
        
       
        self.numFactories = PLAYERS_TO_FACTORIES[numPlayers]
        
        self.numPlayers = numPlayers
        self.publicBoard = publicBoard(tileDuplicates, self.numFactories) #
        self.publicBoard.deal()
        self.playerBoards = [playerBoard() for p in range(numPlayers)]
        
   
        
    def mainLoop(self):
        
        quitLoop = False
        while not quitLoop:
            for player in range(self.numPlayers):
                self.displayBoard(player)
                
                #selectedTiles = self.getPlayerTileSelection(player)
                
                #self.getPlayerRowSelection(player, selectedTiles)
                
                self.getPlayerInput(player)
                
                self.checkRoundEnd()
                
                self.checkGameOver()
          
    def checkRoundEnd(self):
        roundIsOver = self.publicBoard.checkRoundEnd()

        if roundIsOver:
            print('\nThe round is over!\n')
            
            discardedTiles = []
            
            #place tiles
            for p in range(self.numPlayers):
                
                #do playerboard round end procedure and return tiles to discard
                playerDiscardedTiles = self.playerBoards[p].roundEnd()
                discardedTiles.extend(playerDiscardedTiles)
                
            
            #dicard tiles
            self.publicBoard.discard.extend(discardedTiles)
            self.publicBoard.deal()

            
    def checkGameOver(self):
        completeRows = [p.getNumCompleteRows() > 0 for p in self.playerBoards]
               
        if any(completeRows):
            [p.addBonuses for p in self.playerBoards]
            scores = [p.score for p in self.playerBoards]       
            verbs = ['won', 'lost', 'was embarrassed', 'utterly failed']
            
            playerScoreOrder =sorted(range(len(scores), key = scores.__getitem__, reverse=True))
            
            for place, playerIdx in enumerate(playerScoreOrder):
                print('Player {} {} with {} points'.format(playerIdx + 1, verbs[place], [scores[playerIdx]]))
            
                
    
    def displayBoard(self, player = -1):
        g.publicBoard.disp()
        if player > -1:
            g.playerBoards[player].disp()
            
    '''        
    def getPlayerRowSelection(self, player=1, selectedTiles=[]):
        #structure definitely needs to be reworked
        remainingTiles = selectedTiles
        inputMessage = 'Which row do you want to put them in?'


        while len(remainingTiles) > 0:
            print(inputMessage)
            targetRow = self.checkInput(validChars=['f'] + list(range(1,6)))              
            [inputMessage, remainingTiles] = self.playerBoards[player].addTiles(remainingTiles, targetRow)
    '''    
        
    
    def getPlayerInput(self, player=1):
        #should this be a method of publicBoard?
        #here the validity checking is done within game,
        #but for load row selection the checkign is done within playerBoard
        #but I guess some checking is also done in public board, e.g. to see
        #if there are any of the right color
        
        selectedTiles = []
        print('\nPlayer {} it is your turn.'.format(player+1))
        
            
        print("Enter the number of the factory you want to select or enter"
          " \n'c' to pick from the center. If you already know the color\n"
          "and row you want, you can enter that now")
        
       
        errorMessage = '_'
        while len(errorMessage) > 0:
            firstInput = self.checkInput(maxLength = 3)
            pileSelection = list(firstInput)[0]         
            errorMessage = self.publicBoard.validatePileChoice(pileSelection)
            print(errorMessage)
            

        if len(firstInput) > 1:
            colorSelection = firstInput[1]     
            errorMessage = self.publicBoard.validateColorChoice(pileSelection, colorSelection)                 
        else:
            errorMessage = '_'

        while len(errorMessage) > 0:               
            print('Ok, what color? ')
            colorSelection = self.checkInput(validChars = range(1,6), maxLength = 1)[0] #add error checking
            errorMessage = self.publicBoard.validateColorChoice(pileSelection, colorSelection)

        

        
        selectedTiles = self.publicBoard.selectTiles(pileSelection, int(colorSelection))
        
        print('You picked {0}'.format(selectedTiles))
    
        
        remainingTiles = selectedTiles
        
        if len(firstInput) > 2:
            targetRow = firstInput[2]
        else:       
            inputMessage = 'Which row do you want to put them in?'
            while len(remainingTiles) > 0:
                print(inputMessage)
                targetRow = self.checkInput(validChars=['f'] + list(range(1,6)))[0]              
                
                
        [inputMessage, remainingTiles] = self.playerBoards[player].addTiles(remainingTiles, targetRow) #add error checking?
        
        
        
        
        
    @staticmethod
    def checkInput(message = '> ', validChars = [], maxLength = 1):
        validChars = [str(char) for char in validChars]
        validChars.append('q')
        
        errorMessage = '_'
        while len(errorMessage) > 0:
            inVals = input(message).split(',')
    
            errorMessage = ''
            if len(inVals) > maxLength:
                errorMessage = 'Too many inputs! Try again.'
            elif len(validChars) > 1 and any([char not in validChars for char in inVals]): #should each one have a separate list of valid chars?
                errorMessage = 'Some characters not valid! Try again.'
        
        
            if inVals[0] == 'q':
                    sys.exit(0)
            print(errorMessage)
            
        return(inVals)
        
    

        
        
        
        
                    
    
#INITIAL SETUP            
#p = publicBoard(4, 4)
#p.deal()
#p.disp()
        
        
#b = playerBoard()
#b.disp()
if __name__ == '__main__':
    g=game(numPlayers = NUM_PLAYERS)
    g.mainLoop()
    #g.checkInput(message='>', validChars = [1,2,3], maxLength=3)
'''
x = g.playerBoards[0]
x.load[0]=[4]
x.load[1]=[2,2]
x.load[2]=[0,5,5]

x.wall[0] = [9 for e in x.wall[0]]
x.wall[1] = [9 for e in x.wall[0]]

x.wall[2][2]=9
x.wall[3][2]=8
x.wall[4][2]=8

x.disp()
#x.roundEnd()
x.disp()
#newTiles=[2,2,2,2,2,2]
#x.addTiles(newTiles, 2)
'''
#GRAVEYARD
'''
def disp(self):
        print('Wall - Template')
        [print('{} {}'.format(row[0], row[1])) for row in zip(self.wall, self.wallTemplate)] #change to letters later?
        print('Loading Area')
        [print(row) for row in self.load]
        print('Floor')
        print(self.floorLine)
        print('Current Score: {}'.format(self.score))
'''