from __future__ import print_function
import random, os, pygame, inflection, collections
from pygame.transform import scale
from pygame.locals import *
from lib import CardShoe, Player, Dealer, CasinoTable
import pdb

# Colors          R    G    B
BLACK        = (  0,   0,   0)
WHITE        = (255, 255, 255)
RED          = (255,   0,   0)
LIME         = (  0, 255,   0)
BLUE         = (  0,   0, 255)
YELLOW       = (255, 255,   0)
AQUAMARINE   = (  0, 255, 255)
MAGENTA      = (255,   0, 255)
SILVER       = (192, 192, 192)
GRAY         = (128, 128, 128)
DIMGRAY      = (105, 105, 105)
MAROON       = (128,   0,   0)
OLIVE        = (128, 128,   0)
GREEN        = (  0, 128,   0)
PURPLE       = (128,   0, 128)
TEAL         = (  0, 128, 128)
NAVY         = (  0,   0, 128)
PERU         = (205, 133,  63)


# Pygame Constants. All of these values are in pixels
FPS = 30
WINDOWWIDTH   = 1024                    # Width of game window
WINDOWHEIGHT  =  768                    # Height of game window
WINCENTERX    = int(WINDOWWIDTH / 2)    # X coordinate of window's center
WINCENTERY    = int(WINDOWHEIGHT / 2)   # Y coordinate of winwow's center
CARDWIDTH     =   30                    # Width of a card image
CARDSPACING   =    4                    # Spacing between cards (both axes)
CARDHEIGHT    =   60                    # Height of a card image
LINESPACING   =   15                    # Spacing between text Rect objects
TABLEWIDTH    =  700                    # width of playing table
TABLEHEIGHT   =  400                    # height of playing table
TABLERIM      =   40                    # width of band around table
STATIONWIDTH  =  250                    # width of dealer's station
STATIONHEIGHT =   60                    # height of dealer's station
MAXPLAYERS    =    3                    # board space limits players to 3
SCOREWIDTH    =  200                    # width of all players' score text

# These four items are the edges of printable area in game window.
LEFTMARGIN    =   10                    
RIGHTMARGIN   = WINDOWWIDTH - LEFTMARGIN
TOPMARGIN     =   10
BOTTOMMARGIN  = WINDOWHEIGHT - TOPMARGIN

# These three constants define the printable area for the players on the casino
# table. A player's regular hand will appear along these margins. The split
# hand will appear above it.
TABLELEFTMARGIN   = WINCENTERX - int(TABLEWIDTH / 2) + (TABLERIM + CARDWIDTH)
TABLEBOTTOMMARGIN = WINCENTERY + int(TABLEHEIGHT / 2) - (TABLERIM + CARDWIDTH)
TABLERIGHTMARGIN  = WINCENTERX + int(TABLEWIDTH / 2) - (TABLERIM + CARDWIDTH)

# This constant adjusts the position of player output in the center of the
# table.
CENTEROUTPUT  =  100

# Y position in front of dealer's where Dealer's cards are dealt. Orignally,
# This was a flat value, but now, it needs to be a formula that adjusts for
# size of the table and the station itself. It is adjusted from the center
# of the table. Half the table height gets it to the edge of the table. Next,
# we adjust for half the height of the station itself.
# These two constants control where the Dealer's station prints and where the
# dealer's cards are printed relative to it. The Y coordinate of the top
# of the station uses a formula of adjustments to get it centered on the edge
# of the table, regardless of shape. The X coordinate of the left edge is
# half the length of the station from the center line of the table.
# DEALERSCARDS is adjusted to a distance of CARDSPACING below the station.
DEALERSTATIONTOP  = WINCENTERY - int(TABLEHEIGHT / 2) - int(STATIONHEIGHT / 2)
DEALERSTATIONLEFT = WINCENTERX - int(STATIONWIDTH / 2)
DEALERSCARDS = DEALERSTATIONTOP + STATIONHEIGHT + CARDSPACING

BGCOLOR   = DIMGRAY
TEXTCOLOR = WHITE

def main(): # main game function
    global FPSCLOCK, DISPLAYSURF, CARDIMAGES, BLANKCARD, BASICFONT, SCOREFONT, DATAFONT

    # Pygame initialization.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    # The Surface object is stored in DISPLAYSURF, which is returned from
    # pygame.display.set_mode() function calls. This object is not drawn to
    # the screen until pygame.display.update() is called.
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption('Casino Blackjack')
    DISPLAYSURF.fill(BGCOLOR)

    # The next stanza sets the default text font for the game to GNU Free Sans
    # TTF. If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame.
    try:
        BASICFONT = pygame.font.Font('etc/FreeSans.ttf', 12)
    except:
        # FreeSans.ttf could not be found or could not be used.
        BASICFONT = pygame.font.Font('freesansbold.ttf', 12)        

    # The next stanza sets the SCOREFONT for the game to GNU Free Serif TTF.
    # If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame.
    try:
        SCOREFONT = pygame.font.Font('etc/FreeSerif.ttf', 12)
    except:
        # FreeSerif.ttf could not be found or could not be used.
        SCOREFONT = pygame.font.Font('freesansbold.ttf', 12)
    
    # The next stanza sets the DATAFONT for the game to GNU Free Serif TTF.
    # If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame.
    try:
        DATAFONT = pygame.font.Font('etc/FreeMono.ttf', 14)
    except:
        # FreeMono.ttf could not be found or could not be used.
        DATAFONT = pygame.font.Font('freesansbold.ttf', 14)        

    # Next, we need to build the BLANKCARD and CARDIMAGES dictionaries.
    # We need to initialize the dictionaries that store card images and
    # their respecitive surfaces. The first is BLANKCARD, a single layer dict
    # object that contains the mapping as follows:
    # 'image    : loaded graphics file of a blank card
    # 'surface' : a surface object made from the file and scaled to 45x70
    #             pixels
    # 'rect'    : a rect object large enough to display the Surface object
    #
    # CARDIMAGES is a two layer nested ordered dictionary. The first layer maps
    # a card, a tuple of (rank, suit) generated by CardShoe class, to a nested
    # dictionary that maps the following items together with the card:
    # (card) --> {'image'        : loaded graphics file of the tuple (card)
    #             'scaled image' : image scaled to card width/height
    #             'surface'      : a surface object created from the scaled
    #                              scaled image
    #             'rect'         : a rect object large enough to display the
    #                              Surface object}
    # BLANKCARD is the simpler process, but it lays out the steps in building
    # the full nested dictionary, CARDIMAGES.
    BLANKCARD = {}
    BLANKCARD['image']     = pygame.image.load('graphics/Blank.png')
    BLANKCARD['surface']   = BLANKCARD['image'].convert()
    BLANKCARD['rect']      = BLANKCARD['surface'].get_rect()
    BLANKCARD['rect']      = BLANKCARD['rect'].inflate(CARDWIDTH, CARDHEIGHT)
    
    # The first step to import the images and map them to their respective
    # 'cards'. The rest can be done with a iterables. Note: CARDIMAGES is an
    # ordered dict since that makes it easier to test changes. It also puts
    # all of the cards in order for diagnostic printouts

    CARDIMAGES   = collections.OrderedDict()
    CARDIMAGES[( 'A', 'S')] = { 'image' : pygame.image.load('graphics/A-S.png') }
    CARDIMAGES[( '2', 'S')] = { 'image' : pygame.image.load('graphics/2-S.png') }
    CARDIMAGES[( '3', 'S')] = { 'image' : pygame.image.load('graphics/3-S.png') }
    CARDIMAGES[( '4', 'S')] = { 'image' : pygame.image.load('graphics/4-S.png') }
    CARDIMAGES[( '5', 'S')] = { 'image' : pygame.image.load('graphics/5-S.png') }
    CARDIMAGES[( '6', 'S')] = { 'image' : pygame.image.load('graphics/6-S.png') }
    CARDIMAGES[( '7', 'S')] = { 'image' : pygame.image.load('graphics/7-S.png') }
    CARDIMAGES[( '8', 'S')] = { 'image' : pygame.image.load('graphics/8-S.png') }
    CARDIMAGES[( '9', 'S')] = { 'image' : pygame.image.load('graphics/9-S.png') }
    CARDIMAGES[('10', 'S')] = { 'image' : pygame.image.load('graphics/10-S.png') }
    CARDIMAGES[( 'J', 'S')] = { 'image' : pygame.image.load('graphics/J-S.png') }
    CARDIMAGES[( 'Q', 'S')] = { 'image' : pygame.image.load('graphics/Q-S.png') }
    CARDIMAGES[( 'K', 'S')] = { 'image' : pygame.image.load('graphics/K-S.png') }
    CARDIMAGES[( 'A', 'D')] = { 'image' : pygame.image.load('graphics/A-D.png') }
    CARDIMAGES[( '2', 'D')] = { 'image' : pygame.image.load('graphics/2-D.png') }
    CARDIMAGES[( '3', 'D')] = { 'image' : pygame.image.load('graphics/3-D.png') }
    CARDIMAGES[( '4', 'D')] = { 'image' : pygame.image.load('graphics/4-D.png') }
    CARDIMAGES[( '5', 'D')] = { 'image' : pygame.image.load('graphics/5-D.png') }
    CARDIMAGES[( '6', 'D')] = { 'image' : pygame.image.load('graphics/6-D.png') }
    CARDIMAGES[( '7', 'D')] = { 'image' : pygame.image.load('graphics/7-D.png') }
    CARDIMAGES[( '8', 'D')] = { 'image' : pygame.image.load('graphics/8-D.png') }
    CARDIMAGES[( '9', 'D')] = { 'image' : pygame.image.load('graphics/9-D.png') }
    CARDIMAGES[('10', 'D')] = { 'image' : pygame.image.load('graphics/10-D.png') }
    CARDIMAGES[( 'J', 'D')] = { 'image' : pygame.image.load('graphics/J-D.png') }
    CARDIMAGES[( 'Q', 'D')] = { 'image' : pygame.image.load('graphics/Q-D.png') }
    CARDIMAGES[( 'K', 'D')] = { 'image' : pygame.image.load('graphics/K-D.png') }
    CARDIMAGES[( 'A', 'H')] = { 'image' : pygame.image.load('graphics/A-H.png') }
    CARDIMAGES[( '2', 'H')] = { 'image' : pygame.image.load('graphics/2-H.png') }
    CARDIMAGES[( '3', 'H')] = { 'image' : pygame.image.load('graphics/3-H.png') }
    CARDIMAGES[( '4', 'H')] = { 'image' : pygame.image.load('graphics/4-H.png') }
    CARDIMAGES[( '5', 'H')] = { 'image' : pygame.image.load('graphics/5-H.png') }
    CARDIMAGES[( '6', 'H')] = { 'image' : pygame.image.load('graphics/6-H.png') }
    CARDIMAGES[( '7', 'H')] = { 'image' : pygame.image.load('graphics/7-H.png') }
    CARDIMAGES[( '8', 'H')] = { 'image' : pygame.image.load('graphics/8-H.png') }
    CARDIMAGES[( '9', 'H')] = { 'image' : pygame.image.load('graphics/9-H.png') }
    CARDIMAGES[('10', 'H')] = { 'image' : pygame.image.load('graphics/10-H.png') }
    CARDIMAGES[( 'J', 'H')] = { 'image' : pygame.image.load('graphics/J-H.png') }
    CARDIMAGES[( 'Q', 'H')] = { 'image' : pygame.image.load('graphics/Q-H.png') }
    CARDIMAGES[( 'K', 'H')] = { 'image' : pygame.image.load('graphics/K-H.png') }
    CARDIMAGES[( 'A', 'C')] = { 'image' : pygame.image.load('graphics/A-C.png') }
    CARDIMAGES[( '2', 'C')] = { 'image' : pygame.image.load('graphics/2-C.png') }
    CARDIMAGES[( '3', 'C')] = { 'image' : pygame.image.load('graphics/3-C.png') }
    CARDIMAGES[( '4', 'C')] = { 'image' : pygame.image.load('graphics/4-C.png') }
    CARDIMAGES[( '5', 'C')] = { 'image' : pygame.image.load('graphics/5-C.png') }
    CARDIMAGES[( '6', 'C')] = { 'image' : pygame.image.load('graphics/6-C.png') }
    CARDIMAGES[( '7', 'C')] = { 'image' : pygame.image.load('graphics/7-C.png') }
    CARDIMAGES[( '8', 'C')] = { 'image' : pygame.image.load('graphics/8-C.png') }
    CARDIMAGES[( '9', 'C')] = { 'image' : pygame.image.load('graphics/9-C.png') }
    CARDIMAGES[('10', 'C')] = { 'image' : pygame.image.load('graphics/10-C.png') }
    CARDIMAGES[( 'J', 'C')] = { 'image' : pygame.image.load('graphics/J-C.png') }
    CARDIMAGES[( 'Q', 'C')] = { 'image' : pygame.image.load('graphics/Q-C.png') }
    CARDIMAGES[( 'K', 'C')] = { 'image' : pygame.image.load('graphics/K-C.png') }
    # Step two is to iterate through the cards (dict keys) and create the
    # surfaces and rects we need to display the cards on screen. The inflate()
    # method ensures all cards are the same size.
    for card in CARDIMAGES.iterkeys():
        tempSurf = CARDIMAGES[card]['image'].convert()
        CARDIMAGES[card]['scaled image'] = pygame.transform.scale(CARDIMAGES[card]['image'], (CARDWIDTH, CARDHEIGHT))
        CARDIMAGES[card]['surface'] = CARDIMAGES[card]['scaled image'].convert()
        CARDIMAGES[card]['rect']    = CARDIMAGES[card]['surface'].get_rect()
    # Diagnostic print to see if these cards were setup correctly.
    # cardImagesDiagnosticPrint()

    listDealers = generateDealerList()
    
    # Defining the tempDealer for the purpose of testing the printouts.
    # tempDealer = {}
    # tempDealer['name'] = "Fred"
    # tempDealer['bank'] = 100000
    # tempDealer['hand'] = [('A', 'D'), ('J', 'S')]
    # tempDealer['hand'] = [('A', 'D')]
    # tempDealer['hand'] = None
    # tempDealer['soft score'] = 21
    # tempDealer['hard score'] = 11
    # tempDealer['visible card'] = tempDealer['hand'][1]
    # tempDealer['visible card'] = None
    # tempDealer['visible soft score'] = 10
    # tempDealer['visible hard score'] = 10
    # tempDealer['dealer turn'] = None
    # printTableDealer(tempDealer)

    # Defining tempPlayer for the purpose of testing these printouts.
    # tempPlayer = {}
    # tempPlayer['name'] = "Manfred"
    # tempPlayer['bank'] = 25000
    # tempPlayer['hand'] = [('A', 'D'), ('J', 'S')]
    # tempPlayer['hand'] = [('A', 'D')]
    # tempPlayer['hand'] = None
    # tempPlayer['soft score'] = 21
    # tempPlayer['soft score'] = None
    # tempPlayer['hard score'] = 11
    # tempPlayer['hard score'] = None
    # tempPlayer['split hand'] = [('K', 'D'), ('J', 'C')]
    # tempPlayer['split hand'] = [('J', 'C')]
    # tempPlayer['split hand'] = None
    # tempPlayer['soft score split hand'] = 20
    # tempPlayer['soft score split hand'] = 10
    # tempPlayer['soft score split hand'] = None
    # tempPlayer['hard score split hand'] = 20
    # tempPlayer['hard score split hand'] = 10
    # tempPlayer['hard score split hand'] = None
    # tempPlayer['regular bet'] = 100
    # tempPlayer['regular bet'] = None
    # tempPlayer['split hand bet'] = 75
    # tempPlayer['split hand bet'] = None
    # tempPlayer['insurance bet'] = 50
    # tempPlayer['insurance bet'] = None
    # printTablePlayer(tempPlayer, 2, 'diagnostic')
    # printTablePlayer(tempPlayer, 3)
    # Update the screen before recycle.
    pygame.display.update()
    FPSCLOCK.tick()

def cardImagesDiagnosticPrint(adjX=0, adjY=0):
    """
    This function prints out all 52 cards to verify spacing and apperance.
    INPUT: optional posX and posY adjustments, defaults are 30 (LINESPACING)
    OUTPUT: None
    """
    DISPLAYSURF.fill(BGCOLOR)
    posX = int(3 * (CARDSPACING + CARDWIDTH) / 2) + adjX
    posY = CARDHEIGHT + CARDSPACING + adjY
    for card in CARDIMAGES.iterkeys():
        rank, suit = card
        if rank == 'A':
            posX  = int(3 * (CARDSPACING + CARDWIDTH) / 2) + adjX
            posY += CARDHEIGHT + CARDSPACING + adjY
        CARDIMAGES[card]['rect'].center = (posX, posY)
        DISPLAYSURF.blit(CARDIMAGES[card]['surface'], CARDIMAGES[card]['rect'])
        posX += CARDWIDTH + CARDSPACING
        pygame.display.update()
        FPSCLOCK.tick()

def diagnosticPrint(output = ''):
    """
    This function checks for and prints out the following objects classes:
        CasinoTable
        CardShoe
        Player(s)
        Dealer
    It also prints out the game information on the following local objects:
        listPlayers : stores names of players and their current bank
        blackjack_multiplier : multiplier for the casino (can be overridden
            by the table multiplier, if better)
        listDealers : list of the Dealers in the casino and the type of table
            they deal at (normal, special event, high rollar, beginner)
    When player(s) pick a table to play at, a tableObject is created. Before
    that, it does not exist. The tableObject has a Dealer object and up to
    five player objects that manage their hands, banks, and betting options.
    Since this is partly a diagnostic function, we cannot assume that any of
    these objects exist.
    INPUT: option 'v' or 'verbose' argument (all other strings are ignored)
    OUTPUT: A quick visual printout of the contents of the active objects in
        the current game. If the verbose option is requested, it will also
        issue the dianostic_print() methods for the classes CasinoTable,
        Player, Dealer, and CardShoe. The latter outputs should go to the
        terminal output.
    """
    # First, clear the screen.
    DISPLAYSURF.fill(BGCOLOR)
    posY = LINESPACING
    
    # See if a table object exists.
    if tableObject and type(tableObject) == 'CasinoTable':
        tableObjectInfoSurf = BASICFONT.render('A CasinoTable object exists', True, TEXTCOLOR)
        tableObjectInfoRect = tableObjectInfoSurf.get_rect()
        tableObjectInfoRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(tableObjectInfoSurf, tableObjectInfoRect)
        posY += LINESPACING
        if output == 'v' or output == 'verbose':
            tableObject.diagnostic_print()
        if tableObject.tableDealer and type(tableObject.tableDealer) == 'Dealer':
            tableObjectInfoSurf = BASICFONT.render('A Dealer object was found inside the CasinoTable', True, TEXTCOLOR)
            tableObjectInfoRect = tableObjectInfoSurf.get_rect()
            tableObjectInfoRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(tableObjectInfoSurf, tableObjectInfoRect)
            posY += LINESPACING
            tableDealer = print(tableObject.tableDealer)
            printTableDealer(tableDealer, 'diagnostic')

        if tableObject.players:
            numOfPlayers = len(tableObject.players)
            tableObjectInfoSurf = BASICFONT.render('%s players have been found inside the CasinoTable' % (numOfPlayers), True, TEXTCOLOR)
            for i in xrange(1, numOfPlayers + 1):
                playerObj = print(tableObject.players[i])
                printTablePlayer(playerObj, i, 'diagnostic')
            

    else: # tableObject is not defined.
        tableObjectInfoSurf = BASICFONT.render('No CasinoTable object found', True, TEXTCOLOR)
        tableObjectInfoRect = tableObjectInfoSurf.get_rect()
        tableObjectInfoRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(tableObjectInfoSurf, tableObjectInfoRect)
        posY += LINESPACING


def printTableDealer(tableDealer, output = 'player turn'):
    '''
    This method requires a dealer object produced by the Dealer.__str__()
    method. The dictionary with all of the Dealer's data has the  structure:
        'name'               : dealer's name (aka "Dealer")
        'bank'               : dealer's bank
	'hand'               : dealer's hand or None (a list)
	'soft score'         : soft score for dealer's hand or None
	'hard score'         : hard score for dealer's hand or None
	'visible card'       : a tuple of the hand[0] or None
	'visible soft score  : soft score of the visible card
	'visible hard score  : hard score of the visible card
	'dealer turn'        : set to None (normal) or True (dealer's turn)
    To avoid too much code duplication, this method uses an argument to
    determine what kind of output to produce. See below for an explanation:
    INPUT: tableDealer (a dict object with the data above),
           optional output argument that determines printout content
               valid options are:
               'player turn'    : keep dealer's hold card and actual scores
                                  hidden, default value
               'dealer turn'    : print out real hands and score, skipping any
                                  marked 'visible', can be triggered by the
                                  'dealer turn' key existing
               'diagnostic'     : print everything in the dealer's dictionary
    OUTPUT: There is output to the screen, but no return value
    '''
    # We need a starting position for this data above the dealer. All the
    # remaining lines of output will print relative to the staring position.
    # Dealer's name and bank always print out regardless of the mode in this
    # function call.
    posY = 2 * LINESPACING
    if output == 'dealer turn':
        outputTypeSurf = DATAFONT.render("Dealer's Turn", True, TEXTCOLOR)
    elif output == 'diagnostic':
        outputTypeSurf = DATAFONT.render("Diagnostic Printout", True, TEXTCOLOR)
    else: # Default behavior as 'player turn'.
        outputTypeSurf = DATAFONT.render("Players' Turn", True, TEXTCOLOR)
    outputTypeRect = outputTypeSurf.get_rect()
    outputTypeRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(outputTypeSurf, outputTypeRect)
    posY += 2 * LINESPACING
    dealerNameSurf = BASICFONT.render("Dealer's Name: %s" % (tableDealer['name']), True, TEXTCOLOR)
    dealerNameRect = dealerNameSurf.get_rect()
    dealerNameRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(dealerNameSurf, dealerNameRect)
    posY += LINESPACING
    dealerBankSurf = BASICFONT.render("Dealer's Bank: %s" % (tableDealer['bank']), True, TEXTCOLOR)
    dealerBankRect = dealerBankSurf.get_rect()
    dealerBankRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(dealerBankSurf, dealerBankRect)
    posY += LINESPACING

    # The cover color for the hold card will be SILVER. The alpha for its
    # overlay is 50% for diagnostic printouts, 100% during player's turns,
    # and unused in the Dealer's turn. Opaque = 255. These cards stay in front
    # of the Dealer's station until the Dealer's turn. The code for the
    # Dealer's turn skips the use of the overlay.
    if output == 'diagnostic':
        alpha = 128
    else:
        alpha = 255
    dealerHoldCardOverlaySurf = pygame.Surface((CARDWIDTH, CARDHEIGHT))
    dealerHoldCardOverlaySurf.fill(SILVER)
    dealerHoldCardOverlaySurf.convert_alpha()
    dealerHoldCardOverlayRect = dealerHoldCardOverlaySurf.get_rect()

    # Now, we need to know how many cards are in the Dealer's hand or if it
    # it exists at all.
    if tableDealer['hand']:
        sizeOfHand = len(tableDealer['hand'])
    else:
        sizeOfHand = 0
    
    # If the Dealer's hand does not exist, normally, all output associated
    # the Dealer's hand is skipped. For diagnostic printouts, we need a notice
    # that the hand is missing.
    if not tableDealer['hand'] and output == 'diagnostic':
        dealerHandSurf = BASICFONT.render("Dealer's hand does not exist", True, TEXTCOLOR)
        dealerHandRect = dealerHandSurf.get_rect()
        dealerHandRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerHandSurf, dealerHandRect)
        posY += LINESPACING

    # During the Dealer's turn and in diagnostic mode, we need a full view of
    # the Dealer's hand and the actual cards present. The hand is also placed
    # in the middle of the table as the Dealer plays its hand.
    # Remember, we can send a printout of 'dealer turn' to indicate it is the
    # Dealer's turn. The Dealer.dealer_print() method will set the 'dealer turn'
    # flag in the dictionary it returns to True.
    if (tableDealer['dealer turn'] or output == 'dealer turn' or output == 'diagnostic') and tableDealer['hand']:
        dealerHardScoreSurf = SCOREFONT.render("Dealer's hard score: %s" % (tableDealer['hard score']), True, TEXTCOLOR)
        dealerHardScoreRect = dealerHardScoreSurf.get_rect()
        dealerHardScoreRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerHardScoreSurf, dealerHardScoreRect)
        posY += LINESPACING
        dealerSoftScoreSurf = SCOREFONT.render("Dealer's soft score: %s" % (tableDealer['soft score']), True, TEXTCOLOR)
        dealerSoftScoreRect = dealerSoftScoreSurf.get_rect()
        dealerSoftScoreRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerSoftScoreSurf, dealerSoftScoreRect)
        posY += LINESPACING
        # Now, we need print the hand in the middle of the table. The cards
        # are played in the center of the table. The first two cards will be
        # to the left of center. Any additional cards the Dealer must accept
        # during its turn will be to the right of the center.
        for i in xrange(0, sizeOfHand):
            card = tableDealer['hand'][i]
            cardY = WINCENTERY
            cardX = WINCENTERX - (2 - i) * (CARDWIDTH + CARDSPACING) + (int((CARDSPACING + CARDWIDTH)/ 2))
            cardRect = CARDIMAGES[card]['rect']
            cardRect.center = (cardX, cardY)
            DISPLAYSURF.blit(CARDIMAGES[card]['surface'], cardRect)

    # In a diagnostic run, we want messages indicating that the game is aware
    # that the Dealer has no hand when one does not exist. During regular
    # game play, these messages would be skipped. This message has to do with
    # visible card not existing with a hand that does exist.
    if not tableDealer['visible card'] and sizeOfHand == 1 and output == 'diagnostic':
        # As above, in diagnostic mode, we need to see that there is no
        # visible card in a message on screen. On the Player's turn
        # and Dealer's turn, this code would be skipped.
        dealerVisibleCardSurf = BASICFONT.render("Dealer's visible card does not exist", True, TEXTCOLOR)
        dealerVisibleCardRect = dealerVisibleCardSurf.get_rect()
        dealerVisibleCardRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerVisibleCardSurf, dealerVisibleCardRect)
        posY += LINESPACING
    
    # On the players' turn (the turn in which all of the players play their
    # hands, the Dealer's hold card is kept confidential and the hand scores
    # change to scoring around the visible card. The Dealer's hand is also
    # kept in front of the Dealer's station at the top of the table (black
    # rectangle). The hold card is covered in an opaque mask that is reduced
    # to 50% alpha in diagnostic mode (see code block above.
    if (output == 'player turn' and not tableDealer['dealer turn']) or output == 'diagnostic':

        # As before, we print any scores that are valid, but this time only
        # on the visible card. It is possible to get this far, and still not
        # have a dealer's hand (and therefore no visible card either).
        # There could also be only the hold card dealt.

        # Now, we need to print the hold card, if the hand exists. This code
        # block is still inside the test for player's turn or diagnostics.
        if tableDealer['hand']:
            posXHoldCard = WINCENTERX - (int((CARDSPACING + CARDWIDTH)/ 2))
            posYHoldCard = DEALERSCARDS
            holdCard = tableDealer['hand'][0]
            dealerHoldCardSurf = CARDIMAGES[holdCard]['surface']
            dealerHoldCardRect = CARDIMAGES[holdCard]['rect']
            dealerHoldCardRect.topleft = (posXHoldCard, posYHoldCard)
            DISPLAYSURF.blit(dealerHoldCardSurf, dealerHoldCardRect)
            dealerHoldCardOverlaySurf.set_alpha(alpha)
            dealerHoldCardOverlayRect.topleft = (posXHoldCard, posYHoldCard)
            DISPLAYSURF.blit(dealerHoldCardOverlaySurf, dealerHoldCardOverlayRect)

        # We need to print the "visisble card" if it exists. Again, we are
        # still in the player's turn code block.
        if tableDealer['hand'] and sizeOfHand > 1:
            posXVisCard = WINCENTERX + (int((CARDSPACING + CARDWIDTH)/ 2))
            posYVisCard = DEALERSCARDS
            visCard = tableDealer['visible card']
            dealerVisCardSurf = CARDIMAGES[visCard]['surface']
            dealerVisCardRect = CARDIMAGES[visCard]['rect']
            dealerVisCardRect.topleft = (posXVisCard, posYVisCard)
            DISPLAYSURF.blit(dealerVisCardSurf, dealerVisCardRect)
            dealerVisHardScoreSurf = SCOREFONT.render("Dealer is showing a hard score: %s" % (tableDealer['visible hard score']), True, TEXTCOLOR)
            dealerVisHardScoreRect = dealerVisHardScoreSurf.get_rect()
            dealerVisHardScoreRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(dealerVisHardScoreSurf, dealerVisHardScoreRect)
            posY += LINESPACING
            dealerVisSoftScoreSurf = SCOREFONT.render("Dealer is showing a soft score: %s" % (tableDealer['visible soft score']), True, TEXTCOLOR)
            dealerVisSoftScoreRect = dealerVisSoftScoreSurf.get_rect()
            dealerVisSoftScoreRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(dealerVisSoftScoreSurf, dealerVisSoftScoreRect)
            posY += LINESPACING
                
    pygame.display.update()
    FPSCLOCK.tick()
    return # printTableDealer

def printTablePlayer(playerObj, ordinal, output = 'normal'):
    '''
    This method prints on screen the full data for each players. This data
    is pulled from the CasinoTable.players.__str__() method, which returns
    a dictionary of the form below:
        'name'                  : player's name
        'bank'                  : player's bank
        'hand'                  : player's regular hand or None
        'split hand'            : player's split hand or None
        'soft score'            : soft score for player's hand or None
        'hard score'            : hard score for player's hand or None
        'soft score split hand' : soft score for split hand or None
        'hard score split hand' : hard score for split hand or None
        'regular bet'           : bet amount on regular hand or None
        'split hand bet'        : bet amount on split hand or None
        'insurance bet'         : bet amount on dealer blackjack or None
    "hands" are set to None if they do not exist, including split_hand.  The
    split_flag is used to check for the latter. Bets and scores are set to
    None if they are zero in this dictionary.
    Note: This method assumes that player being printed has been found in a
    CasinoTable class object.
    INPUTS: playerObj : dict object, see above
            ordinal   : integer, player number, valid for 1, 2, 3
            output    : string determining the output of this function
                'diagnostic' : prints everything about the player, putting in
                               messages for None items
                'normal'     : prints only what exists for the player. "None"
                               items are skipped.
    '''
    # This function has to calculate where the player's data will be printed.
    # There is only room for MAXPLAYERS. All of this screen output needs  to
    # written from the bottom up. The players will never see teh difference
    # because nothing appears on screen until a pygame.display.update() is
    # called. regHandX and regHandY are the positions of the player's cards.
    # splitHandY are a card height directly above them while splitHandX will
    # the same for the both the regular and split hands. We need all three
    # sets of coordinates for the score data and both hands of cards, as they
    # all printing independently of each other.
    if ordinal == 1:
        # The player is the left one. posX will be on the screen margin,
        # while regHandX and splitHandX will on the left margin of the green
        # area of the table.
        posX       = LEFTMARGIN
        regHandX   = TABLELEFTMARGIN
        splitHandX = regHandX

    elif ordinal == 2:
        # The player is the center one. posX moves the output under the center
        # of the table, but it will be lined up there. Likewise, regHandX moves
        # there as well. We set the pointer to place the first two cards of
        # either hand to the left of the center line of the table. splitHandX
        # does the same.
        posX       = WINCENTERX - CENTEROUTPUT
        regHandX   = WINCENTERX - (2 * (CARDWIDTH + CARDSPACING)) + (int((CARDSPACING + CARDWIDTH)/ 2))
        splitHandX = regHandX

    elif ordinal == 3:
        # The player is the right one. posX will be on the screen margin, with
        # an adjustment width of the score data rectangle. regHandX will on the
        # left margin of the green area of the table, less the width of four
        # cards laid side by side. The same is true of splitHandX,
        posX       = RIGHTMARGIN - SCOREWIDTH
        regHandX   = TABLERIGHTMARGIN - (4 * (CARDWIDTH + CARDSPACING))
        splitHandX = regHandX
    # posY is the same in all cases. It starts half of LINESPACING above the
    # bottom margin. regHandY is at the bottom margin of the table. This is
    # where the split and regular hands differ. The split hand is positioned
    # above the regular hand.
    posY       = BOTTOMMARGIN - int(LINESPACING / 2)
    regHandY   = TABLEBOTTOMMARGIN
    splitHandY = regHandY - (CARDHEIGHT + CARDSPACING)

    if playerObj['insurance bet']:
        insBetSurf = SCOREFONT.render("Insurance Bet: $%s" % (playerObj['insurance bet']), True, TEXTCOLOR)
        insBetRect = insBetSurf.get_rect()
        insBetRect.topleft = (posX, posY)
        DISPLAYSURF.blit(insBetSurf, insBetRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            insBetSurf = SCOREFONT.render("No insurance bet found", True, TEXTCOLOR)
            insBetRect = insBetSurf.get_rect()
            insBetRect.topleft = (posX, posY)
            DISPLAYSURF.blit(insBetSurf, insBetRect)
            posY -= LINESPACING

    if playerObj['split hand bet']:
        splitBetSurf = SCOREFONT.render("Bet on split hand: $%s" % (playerObj['split hand bet']), True, TEXTCOLOR)
        splitBetRect = splitBetSurf.get_rect()
        splitBetRect.topleft = (posX, posY)
        DISPLAYSURF.blit(splitBetSurf, splitBetRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            splitBetSurf = SCOREFONT.render("No split bet found", True, TEXTCOLOR)
            splitBetRect = splitBetSurf.get_rect()
            splitBetRect.topleft = (posX, posY)
            DISPLAYSURF.blit(splitBetSurf, splitBetRect)
            posY -= LINESPACING

    if playerObj['regular bet']:
        regBetSurf = SCOREFONT.render("Bet on regular hand: $%s" % (playerObj['regular bet']), True, TEXTCOLOR)
        regBetRect = regBetSurf.get_rect()
        regBetRect.topleft = (posX, posY)
        DISPLAYSURF.blit(regBetSurf, regBetRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            regBetSurf = SCOREFONT.render("No regular bet found", True, TEXTCOLOR)
            regBetRect = regBetSurf.get_rect()
            regBetRect.topleft = (posX, posY)
            DISPLAYSURF.blit(regBetSurf, regBetRect)
            posY -= LINESPACING

    if playerObj['hard score split hand']:
        hardSplitScoreSurf = SCOREFONT.render("Hard score on split hand: %s" % (playerObj['hard score split hand']), True, TEXTCOLOR)
        hardSplitScoreRect = hardSplitScoreSurf.get_rect()
        hardSplitScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(hardSplitScoreSurf, hardSplitScoreRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            hardSplitScoreSurf = SCOREFONT.render("No hard hand score on split hand was found", True, TEXTCOLOR)
            hardSplitScoreRect = hardSplitScoreSurf.get_rect()
            hardSplitScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(hardSplitScoreSurf, hardSplitScoreRect)
            posY -= LINESPACING

    if playerObj['soft score split hand']:
        softSplitScoreSurf = SCOREFONT.render("Soft score on split hand: %s" % (playerObj['soft score split hand']), True, TEXTCOLOR)
        softSplitScoreRect = softSplitScoreSurf.get_rect()
        softSplitScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(softSplitScoreSurf, softSplitScoreRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            softSplitScoreSurf = SCOREFONT.render("No soft hand score on split hand was found", True, TEXTCOLOR)
            softSplitScoreRect = softSplitScoreSurf.get_rect()
            softSplitScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(softSplitScoreSurf, softSplitScoreRect)
            posY -= LINESPACING

    # This is purely diagnostic message that the split hand has does not exist.
    if not playerObj['hand'] and output == 'diagnostic':
        splitHandDiagSurf = SCOREFONT.render("No split hand was found", True, TEXTCOLOR)
        splitHandDiagRect = splitHandDiagSurf.get_rect()
        splitHandDiagRect.topleft = (posX, posY)
        DISPLAYSURF.blit(splitHandDiagSurf, splitHandDiagRect)
        posY -= LINESPACING

    if playerObj['hard score']:
        hardScoreSurf = SCOREFONT.render("Hard score on regular hand: %s" % (playerObj['hard score']), True, TEXTCOLOR)
        hardScoreRect = hardScoreSurf.get_rect()
        hardScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(hardScoreSurf, hardScoreRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            hardScoreSurf = SCOREFONT.render("No hard hand score was found", True, TEXTCOLOR)
            hardScoreRect = hardScoreSurf.get_rect()
            hardScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(hardScoreSurf, hardScoreRect)
            posY -= LINESPACING

    if playerObj['soft score']:
        softScoreSurf = SCOREFONT.render("Soft score on regular hand: %s" % (playerObj['soft score']), True, TEXTCOLOR)
        softScoreRect = softScoreSurf.get_rect()
        softScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(softScoreSurf, softScoreRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            softScoreSurf = SCOREFONT.render("No soft hand score was found", True, TEXTCOLOR)
            softScoreRect = softScoreSurf.get_rect()
            softScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(softScoreSurf, softScoreRect)
            posY -= LINESPACING

    # This is purely diagnostic message that the regular has does not exist.
    if not playerObj['hand'] and output == 'diagnostic':
        handDiagSurf = SCOREFONT.render("No regular hand was found", True, TEXTCOLOR)
        handDiagRect = handDiagSurf.get_rect()
        handDiagRect.topleft = (posX, posY)
        DISPLAYSURF.blit(handDiagSurf, handDiagRect)
        posY -= LINESPACING

    if playerObj['bank']:
        playerBankSurf = SCOREFONT.render("Bank: $%s" % (playerObj['bank']), True, TEXTCOLOR)
        playerBankRect = playerBankSurf.get_rect()
        playerBankRect.topleft = (posX, posY)
        DISPLAYSURF.blit(playerBankSurf, playerBankRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            playerBankSurf = SCOREFONT.render("No bank for this player was found", True, TEXTCOLOR)
            playerBankRect = playerBankSurf.get_rect()
            playerBankRect.topleft = (posX, posY)
            DISPLAYSURF.blit(playerBankSurf, playerBankRect)
            posY -= LINESPACING

    if playerObj['name']:
        playerNameSurf = SCOREFONT.render("Name: %s" % (playerObj['name']), True, TEXTCOLOR)
        playerNameRect = playerNameSurf.get_rect()
        playerNameRect.topleft = (posX, posY)
        DISPLAYSURF.blit(playerNameSurf, playerNameRect)
        posY -= LINESPACING
    else:
        if output == 'diagnostic':
            playerNameSurf = SCOREFONT.render("No name for the player was found", True, TEXTCOLOR)
            playerNameRect = playerNameSurf.get_rect()
            playerNameRect.topleft = (posX, posY)
            DISPLAYSURF.blit(playerNameSurf, playerNameRect)
            posY -= LINESPACING

    # Diagnostic output should be indicated on each player.
    if output == 'diagnostic':
        outputTypeSurf = DATAFONT.render("Diagnostic Printout", True, TEXTCOLOR)
        outputTypeRect = outputTypeSurf.get_rect()
        outputTypeRect.topleft = (posX, posY)
        DISPLAYSURF.blit(outputTypeSurf, outputTypeRect)
        posY -= LINESPACING

    # Now, we need to print out the cards in any hands the player has,
    # starting with the regular hand. The users cannot see this take place.
    # (regHandX, regHandY) and (splitHandX, splitHandY) have already been
    # intialized at the beginning of this function. All these loops do is
    # increment across horizontally as the cards are laid out. Y coordinates
    # do not change.
    if playerObj['hand']:
        sizeOfHand = len(playerObj['hand'])
        for i in xrange(0, sizeOfHand):
            card = playerObj['hand'][i]
            cardRect = CARDIMAGES[card]['rect']
            cardRect.center = (regHandX, regHandY)
            DISPLAYSURF.blit(CARDIMAGES[card]['surface'], cardRect)
            regHandX += CARDWIDTH + CARDSPACING

    if playerObj['split hand']:
        sizeOfHand = len(playerObj['split hand'])
        for i in xrange(0, sizeOfHand):
            card = playerObj['split hand'][i]
            cardRect = CARDIMAGES[card]['rect']
            cardRect.center = (splitHandX, splitHandY)
            DISPLAYSURF.blit(CARDIMAGES[card]['surface'], cardRect)
            splitHandX += CARDWIDTH + CARDSPACING
        
        
    pygame.display.update()
    FPSCLOCK.tick()

def generateTable(tableColor = OLIVE ):
    """
    This function prints a basic table to the screen. It does not print the
    cards, nor any data on the players or dealers. That is done by other
    methods and functions.
    INPUTS: None
    OUTPUTS: None, other than pygame creation of a blank table.
    """
    # This stanza creates the table surface. It is composed of a brown oval
    # a green oval, a black rectangle (dealer's station), and areas where
    # player cards will be dealt. These Rect objects use the form:
    # pygame.Rect((left, top), (width, height)). The formulas are calculating
    # the X and Y distances to the (left, top) of each rect object from the
    # CENTER of the game window.
    
    tableOuterRectLeft = WINCENTERX - int(TABLEWIDTH / 2)
    tableOuterRectTop  = WINCENTERY - int(TABLEHEIGHT / 2)
    tableOuterRect = pygame.Rect((tableOuterRectLeft, tableOuterRectTop), (TABLEWIDTH, TABLEHEIGHT))

    tableInnerRectLeft = WINCENTERX - int((TABLEWIDTH - TABLERIM) / 2)
    tableInnerRectTop  = WINCENTERY - int((TABLEHEIGHT - TABLERIM) / 2)
    tableInnerRect = pygame.Rect((tableInnerRectLeft, tableInnerRectTop), (TABLEWIDTH - TABLERIM, TABLEHEIGHT - TABLERIM))
    
    dealerStationRectTop  = DEALERSTATIONTOP
    dealerStationRectLeft = DEALERSTATIONLEFT
    dealerStationRect = pygame.Rect((dealerStationRectLeft, dealerStationRectTop), (STATIONWIDTH, STATIONHEIGHT))

    # pygame.draw.ellipse(DISPLAYSURF, OLIVE, tableOuterRect)
    # pygame.draw.ellipse(DISPLAYSURF, LIME,  tableInnerRect)
    pygame.draw.rect(DISPLAYSURF, tableColor, tableOuterRect)
    pygame.draw.rect(DISPLAYSURF, LIME,       tableInnerRect)
    pygame.draw.rect(DISPLAYSURF, BLACK,      dealerStationRect)

    pygame.display.update()
    FPSCLOCK.tick()

def generateDealerList():
    """
    This function creates a list of dictionary objects that feed initial
    settings for creating dealer objects in CasinoTable objects. The structure
    is a list of dictionaries of the form below:
        'name'  : Dealer's name (string)
        'type'  : This is type of CasinoTable that this "dealer" normally works
                    'high'    : only works high roller tables, banks over $1m
                    'starter' : best for new players, bank under $100k
                    'normal'  : banks 100-250k
                    'special' : dealer only works special events
                    
    For the early versions of the pygame implementation, this list will be
    hardcoded, but the intention is to migrate this data to a much more
    complete database, such as a postgres or sql-lite database.
    INPUTS: None
    OUTPUTS: list of dictionaries with the following additions
        'bank' : A value calculated from a base determined by table type
                 and adjusted by a random amount
        'blackjack_multiplier : A value chosen randomly from a set of ratios
                 controlled by the table type
        'table color' : This the color of the felt of the table. The rim is
                 always leather.
        'table bets'  : Tuple storing the min and max bets that table allows

    Each table type has formulas, complete with random choices to create
    variety during play. All die rolls have a max value of whatever the die
    itself can produce (d6+2 still maxes at 6, but a d6-2 maxes at 4). All die
    rolls have a min of 0 (no negative values). The function, dieRoll(),
    produces these "weighted" die results.
        'starter': Starter tables
            'bank': $50k + [(d30 - 5) * $1k]
                This produces a range 50-75k with most banks being 50k
            'table color' : OLIVE
            'blackjack multiplier' : d6 choice from the following options:
                1) 7:3, 2.33
                2) 9:4, 2.25
                3) 2:1, 2.00
                4) 7:4, 1.75
                5) 5:3, 1.67
                6) 3:2, 1.50
            'table bets' : (tableMin = 50, tableMax = 100)
            
        'high' : High Roller Tables
            'bank': $1m + (d100 * $25k)
                This produces a range of $1-3.5m (uniform)
            'table color' : PURPLE
            'blackjack multiplier' : d6 choice from the following options:
                1) 11:4, 2.75
                2) 8:3, 2.67
                3) 5:2, 2.50
                4) 7:3, 2.33
                5) 9:4, 2.25
                6) 2:1, 2.00
            'table bets' : (tableMin = 500, tableMax = 100k)

        'special' : Special Event Tables
            'bank': $250k + (d100 * 5k)
                This produces a range of $250-750k (uniform)
            'table color' : AQUAMARINE
            'blackjack multiplier' : d4 choice from the following options:
                1) 3:1, 3.00
                2) 5:2, 2.50
                3) 2:1, 2.00
                4) 3:2, 1.50
            'table bets' : (tableMin = 250, tableMax = 1000)        

        'normal' : Regular Tables
            'bank': $100k + [(d100 - 25) * 2k]
                This produces a range of $100-250k, weighted to 25% of banks
                being $100k
            'table color' : BLUE
            'blackjack multiplier' : d8 choice from the following options:
                1) 2:1, 2.00
                2) 9:5, 1.80
                3) 7:4, 1.75
                4) 8:5, 1.60
                5) 5:3, 1.67
                6) 7:5, 1.40
                7) 4:3, 1.33
                8) 6:5, 1.20
            'table bets' : (tableMin = 50, tableMax = 200)
            
    Note: All players start with the starter tables while they learn to play
    this game. It helps to reinforce that the game is partly about having fun,
    but it is also about beating the bank.
    """
    listDealers = []
    listDealers.append({'name' : 'Frank',   'type' : 'starter'})
    listDealers.append({'name' : 'Hannah',  'type' : 'normal'})
    listDealers.append({'name' : 'Mike',    'type' : 'normal'})
    listDealers.append({'name' : 'Rayden',  'type' : 'special'})
    listDealers.append({'name' : 'Charlie', 'type' : 'special'})
    listDealers.append({'name' : 'Freddie', 'type' : 'high'})
    listDealers.append({'name' : 'James',   'type' : 'high'})
    listDealers.append({'name' : 'Angela',  'type' : 'high'})
    print(listDealers)

    numOfDealers = len(listDealers)
    # As mentioned in the main comment block, we need to calculate the banks
    # for each dealer, their current table blackjack_multiplier, and the color
    # of the felt on their table. These are determined by formulas that depend
    # on the type of table the dealer works at.
    for i in range(0, numOfDealers):
        if listDealers[i]['type'] == 'starter':
            listDealers[i]['table color'] = OLIVE
            listDealers[i]['bank'] = 50000 + (1000 * dieRoll(30, 0, 25, -5))
            multiplierChoice = dieRoll(6, 1, 6)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('7:3', 2.33)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('9:4', 2.25)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('7:4', 1.75)
            elif  multiplierChoice == 5:
                listDealers[i]['blackjack multiplier'] = ('5:3', 1.67)
            elif  multiplierChoice == 6:
                listDealers[i]['blackjack multiplier'] = ('3:2', 1.50)
            listDealers[i]['table bets'] = (25, 100)
            
        elif listDealers[i]['type'] == 'normal':
            listDealers[i]['table color'] = BLUE
            listDealers[i]['bank'] = 100000 + (2000 * dieRoll(100, 0, 75, -25))
            multiplierChoice = dieRoll(8, 1, 8)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('9:5', 1.80)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('7:4', 1.75)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('8:5', 1.60)
            elif  multiplierChoice == 5:
                listDealers[i]['blackjack multiplier'] = ('3:2', 1.50)
            elif  multiplierChoice == 6:
                listDealers[i]['blackjack multiplier'] = ('7:5', 1.40)
            elif  multiplierChoice == 7:
                listDealers[i]['blackjack multiplier'] = ('4:3', 1.33)
            elif  multiplierChoice == 8:
                listDealers[i]['blackjack multiplier'] = ('6:5', 1.20)
            listDealers[i]['table bets'] = (50, 200)

        elif listDealers[i]['type'] == 'special':
            listDealers[i]['table color'] = AQUAMARINE
            listDealers[i]['bank'] = 250000 + (5000 * dieRoll(100, 1, 100))
            multiplierChoice = dieRoll(4, 1, 4)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('3:1', 3.00)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('5:2', 2.50)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('3:2', 1.50)
            listDealers[i]['table bets'] = (250, 1000)

        elif listDealers[i]['type'] == 'high':
            listDealers[i]['table color'] = PURPLE
            listDealers[i]['bank'] = 1000000 + (25000 * dieRoll(100, 1, 100))
            multiplierChoice = dieRoll(6, 1, 6)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('11:4', 2.75)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('8:3', 2.67)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('5:2', 2.50)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('7:3', 2.33)
            elif  multiplierChoice == 5:
                listDealers[i]['blackjack multiplier'] = ('9:4', 2.25)
            elif  multiplierChoice == 6:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            listDealers[i]['table bets'] = (500, 1000000)

    return listDealers

def dieRoll(die, minNum, maxNum, adj=0):
    """
    This function generates random numbers for sequences with floor or ceiling
    values. For example, suppose you need to have a roll weighted to be zero
    more often than one possible value, such as d6-2 with a 0 minimum value.
    The sequence of numbers would be [0, 0, 1, 2, 3, 4]. Or suppose you want
    a d12+3 with max of 12. That sequence would be [4, 5, 6, 7, 8, 9 ,10, 11
    12, 12, 12, 12]. In this version, it cannot do a sequence like [1, 1, 2, 2].
    """
    numList = []
    for i in range(1, die + 1):
        currentNum = i + adj
        if not (minNum <= currentNum <= maxNum):
            if currentNum < minNum:
                currentNum = minNum
            elif currentNum > maxNum:
                currentNum = maxNum
        numList.append(currentNum)
    random.shuffle(numList)
    output = random.randint(0, die - 1)
    return numList[output]


if __name__ == '__main__':
    main()