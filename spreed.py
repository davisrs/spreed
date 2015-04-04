#!/usr/bin/env python

import pygame, sys
import argparse
import math
import pickle
import os
import hashlib

from pygame.locals import *

defaultSpeed = 600 #defaultSpeed 450

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
 
# OpenDingux SDL button mappings
BTN_DPAD_UP = pygame.locals.K_UP
BTN_DPAD_DOWN = pygame.locals.K_DOWN
BTN_DPAD_LEFT = pygame.locals.K_LEFT
BTN_DPAD_RIGHT = pygame.locals.K_RIGHT
BTN_A = pygame.locals.K_LCTRL
BTN_B = pygame.locals.K_LALT
BTN_Y = pygame.locals.K_SPACE
BTN_X = pygame.locals.K_LSHIFT
BTN_START = pygame.locals.K_RETURN
BTN_SELECT = pygame.locals.K_ESCAPE
BTN_LEFT_SHOULDER = pygame.locals.K_TAB
BTN_RIGHT_SHOULDER = pygame.locals.K_BACKSPACE
BTN_HOLD = pygame.locals.K_PAUSE  # NOTE OpenDingux=hold_slide

class Spreed(object):
    def __init__(self):
        # init pygame
        pygame.init()

        if not pygame.font: print('Warning, fonts disabled')
        if not pygame.mixer: print('Warning, sound disabled')

        # init argparser 
        self.argparser = argparse.ArgumentParser(description =
                                                 "A speed reading application")
        self.argparser.add_argument("file", 
                                    help = "The text file you want to spreed.")
        self.argparser.add_argument("-s", "--speed", dest="speed",
                                    help = "Words per minute to spreed.",
                                    type=int, default=defaultSpeed)
        self.argparser.add_argument("-f", "--font-size", dest="font_size",
                                    help="The font size you wish to choose",
                                    type=int, default=30) #72
        
        # parse arguments
        args = self.argparser.parse_args()
        self.file = args.file
        #self.file = "./README.MD"
        self.speed = args.speed 
        self.font_size = args.font_size
            
        # read text
        f = open(self.file, 'r')
        self.raw_text = f.read()
        f.close() # I can't believe this was missing for so long -- ALWAYS close Files when finished with them
        self.words = self.raw_text.split() # words is a list of words split by whitespace
        self.words.append("--- END ---")

        # init state variables
        self.running = True
        self.show_progress = True
        self.show_ambient = True
        self.pause = True 
        self.combo = False # used for start button combos
        self.offset = 0
        self.cfg_rskip_tolerance = 5
        self.save_on_exit = True
        
        self.multiword_length=16 # default value from gutenflash
        self.multimode = True # desirable
        self.numWordsInPhrase = 1 
        self.phraseToRender = ""
        self.phrase_offset = 0 # attempt
 


        # gutenflash porting
        self.chaptertexts = [ # use for determining if a word is a c type
            "CONTENTS",
            "INDEX",
            "FOREWORD", "foreword",
            "PROLOGUE", "Prologue",
            "CHAPTER ", "Chapter", "Ch.", "Ch.1", 
            "PART", "Part",
            "BOOK",
            "SECTION ", "Section",
            "EPILOGUE",
            "GLOSSARY",
            "APPENDIX",
            ]
        self.abbreviations = [ # See these? It isn't the end of a sentence
            "Dr.", "Mr.", "Mrs.", "Ms.", "Ch.", 
            #"A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.",       "J.", "K.",
            #"L.", "M.", "N.", "O.", "P.", "Q.", "R.", "S.", "T.", "U.", "V.",
            #"W.", "X.", "Y.", "Z.",
            ]

        # Load bookmark pickle file
        firstTime = True
        fileName=os.path.splitext(self.file)[0]
        pickleFileName= fileName+".pkl"
        print pickleFileName
        #Check if one exists
        if os.path.isfile(pickleFileName):#This will need to be changed to home eventually prior to release
            pickleFile=open(pickleFileName,'r')#open the pickle file for reading (if it exists)
            lastWord = pickle.load(pickleFile)#unpickle our current word
            if (lastWord<len(self.words)) and (lastWord>-1):#check if lastWord is valid
                print "LastWord bookmark is valid: "+str(lastWord)+" < " + str(len(self.words))
                self.offset = lastWord
            else:
                print "Invalid Bookmark! :"+str(lastWord)+" !< " + str(len(self.words))
                self.offset = 0;
            pickleFile.close()#close
            firstTime=False
        #Create one if it doesn't
        pickleFile=open(pickleFileName,'w')#open (or create) a pickle file for writing
        pickle.dump(self.offset, pickleFile)#pickles our current location
        pickleFile.close()#close the file
        if firstTime:
            print "Created a new bookmark pickle file."

        # assign types to words
        print "assigning types"
        self.t = [" "] * len(self.words) # is a list of letters signifying types
        self.chapterPointerList = [] # for use in eventual go_to_chapter menu?
        for i in range( len(self.words)):
        # Check for chapter headings.
            is_chapter = 0
            is_dot = 0
            #stripline = line.strip()
            #for c in self.chaptertexts:
            #    if self.words[i] == c:
            #        is_chapter = 1
            if self.words[i] in self.chaptertexts:
                is_chapter = 1
            if (self.words[i][-1] in '.!?'): # if the last letter is one of these
                if (self.words[i] not in self.abbreviations): # and it is not an abbreviation
                    is_dot = 1 # it is at the end of a sentence
            #for dotChar in '.?!':
            #    if self.words[i][-1] == dotChar:#if end of word is a . or ! or ? indicative of a sentence ending
            #        is_dot = 1
            if is_chapter:
                #print "Chapter: %s (%s)" % (line, len(self.wordlist))
                self.t[i] = "c"
                self.chapterPointerList.append(i)
                #print i, self.words[i] # for debug purposes
            if is_dot:
                self.t[i] = "."
                #print i, self.words[i] # for debug purposes
        print "types are now assigned"
        
        #print self.t
        
        #print self.chapterPointerList # for debug purposes

        # init pygame display 
        #self.size = pygame.display.list_modes()[0]
        #self.screen = pygame.display.set_mode(self.size, FULLSCREEN)
        self.screen = pygame.display.set_mode((320, 240), pygame.DOUBLEBUF)
        pygame.display.set_caption('spreed')

        # turn off the mouse (pointer)
        pygame.mouse.set_visible(False)

        # init font
        if pygame.font:
            self.font = pygame.font.Font(None, self.font_size)
            self.amb_font = pygame.font.Font(None, self.font_size / 2)
        else:
            print("Error!")
            
        # init clock
        self.clock = pygame.time.Clock()

    def run(self):
        # get initial time
        time = pygame.time.get_ticks() 
        deltaP = 0
        
        #COLORS
        SCHEME=True
        
        #Allow Repeating keys
        delay=100
        interval=50
        pygame.key.set_repeat(delay, interval)

        # main loop
        while self.running:
            # current percentage of reading
            percent = int(len(self.words) / 100)
            #deltaP = (deltaP-10)%100+10
            

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False
                if event.type is KEYUP:#check if modifier is releaased to disable combo
                    if event.key == BTN_START: # "Start + key" combo is finished
                        print "Combo with start is disabled"
                        self.combo = False 
                if event.type is KEYDOWN:
                    if event.key == BTN_SELECT:
                        if self.combo == False: # select by itself
                            print "Will save before exiting"
                            self.save_on_exit = True
                        else: # Start + Select
                            self.save_on_exit = False
                            print "Do not save upon exiting"
                        self.running = False
                    if event.key == BTN_X:
                        self.speed = defaultSpeed
                    if event.key == BTN_Y:
                        if self.combo == False:
                            self.show_progress = not self.show_progress
                            self.show_ambient = not self.show_ambient
                        else:
                            self.multimode = not self.multimode
                            print "As a combo: multiword setting was changed. Multiword mode Enabled = ", self.multimode
                    if event.key == BTN_A:
                        if self.combo == False:
                            self.pause = not self.pause
                            print "is paused: ", self.pause
                        else:
                            print "As a combo: pickle the current location"
                            self.pickle_Bookmark()
                    if event.key == BTN_B:
                        SCHEME = not SCHEME
                        print SCHEME
                    if event.key == BTN_LEFT_SHOULDER:
                        if self.speed <= 70:
                            self.speed =60;
                        else:
                            self.speed -= 10
                        #print self.speed
                    if event.key == BTN_RIGHT_SHOULDER:
                        if self.speed >= 1990:
                            self.speed = 2000
                        else:
                            self.speed += 10
                        #print self.speed
                    if event.key == BTN_DPAD_LEFT:
                        if self.combo == False:
                            self.offset -= 1
                        else:
                            print "As a combo: try to go to previous chapter"
                            self._skip_backward(["c"])
                    if event.key == BTN_DPAD_RIGHT:
                        if self.combo == False:
                            self.offset += 1
                        else:
                            print "As a combo: try to go to next chapter"
                            self._skip_forward(["c"])
                    if event.key == BTN_DPAD_UP:
                        if self.combo == False: # Sentence navigation is now default behavior!
                            print "non-combo: try to go to previous sentence"
                            self._skip_backward(["."]) # This is much easier and better than percent navigation!
                        else:
                            print "As a combo: increment by 1%" # This old function is now a combo because hitting this by accident does bad things
                            deltaP = (deltaP+1)%100 # deltaP doesnt take current location into account and is thus based only on its own previous value
                            self.offset = percent * deltaP # which can make navigation very broken (it's kind of useless actually)
                            #print deltaP # ie it goes in 1% increments of total length of file offset from start not the current location.
                    if event.key == BTN_DPAD_DOWN:
                        if self.combo == False: # Sentence navigation is now default behavior!
                            print "non-combo: try to go to next sentence"
                            self._skip_forward(["."]) # This is much easier and better than percent navigation!
                        else:
                            print "As a combo: decrement by 1%" # This old function is now a combo because hitting this by accident does bad things
                            deltaP = (deltaP-1)%100 # deltaP doesnt take current location into account and is thus based only on its own previous value
                            self.offset = percent * deltaP # which can make navigation very broken (it's kind of useless actually)
                            #print deltaP # ie it goes in 1% increments of total length of file offset from start not the current location.
                    #if event.key == K_0:
                    #    deltaP=0
                    #    self.offset = 0
                    #if event.key == K_1:
                    #    deltaP=10
                    #    self.offset = percent * deltaP 
                    #if event.key == K_2:
                    #    deltaP=20
                    #    self.offset = percent * deltaP
                    #if event.key == K_3:
                    #    deltaP=30
                    #    self.offset = percent * deltaP
                    #if event.key == K_4:
                    #    deltaP=40
                    #    self.offset = percent * deltaP 
                    if event.key == K_5:
                        self.multimode = not self.multimode
                        print "multiword enabled: ", self.multimode
                    if event.key == K_6:
                        print "trying to go to previous sentence"
                        self._skip_backward(["."])
                    if event.key == K_7:
                        print "trying to go to next sentence"
                        self._skip_forward(["."])
                    if event.key == K_8:
                        print "trying to go to previous chapter"
                        self._skip_backward(["c"])
                    if event.key == K_9:
                        print "trying to go to next chapter"
                        self._skip_forward(["c"])
                    if event.key == BTN_START:
                        self.combo = True # "Start + key" combo is possible
                        print "Combo with start is enabled"

            self.offset %= len(self.words) # current word is word modulus len(all)
            #grab 1st chunk here

            #CHOOSE COLOR SCHEME
            if SCHEME:
                BG_COLOR=(0, 0, 0)#default
                FG_COLOR=(255, 255, 255)
                AM_COLOR=(255, 255, 0)
            else:
                FG_COLOR=(0x66, 0x66, 0x66)
                BG_COLOR=(0xCC, 0xCC, 0x9A)
                AM_COLOR=(0x99, 0x99, 0x67)

            # clear screen
            self.screen.fill((BG_COLOR))

            # put words in phraseToRender for buffer
            #if (not self.pause):
            self.get_phraseToRender() # Decide on word[s] to put in buffer

            # render text in buffer
            self.text = self.font.render(self.phraseToRender, 1, 
                (FG_COLOR))
            self.textpos = self.text.get_rect(
                centerx=320 / 2,
                centery=240 / 2)
            self.screen.blit(self.text, self.textpos)

            # wait until ticks per each word has passed and then advance to the next word/phrase chunk
            if (not self.pause) and ((newtime - time) > (self.numWordsInPhrase * 60000 / self.speed)):
                time = pygame.time.get_ticks()
                #self.get_phraseToRender()
                self.offset = self.phrase_offset +1  # regardless of everything else, grab the next word
                # USEFUL for debugging purposes, the below print statement will display some useful but verbose data on each phrase
                #print "numWords:%i \t num letters: %i of 16 \t phrase: %s \t delay: %i ms" % (self.numWordsInPhrase, len(self.phraseToRender), (self.phraseToRender), (self.numWordsInPhrase * 60000 / self.speed))

            # draw progress bar
            if self.show_progress:
                self.draw_progress()

            # draw ambient text symbols
            if self.show_ambient:
                self.ambient_text()

            #update screen with buffer
            pygame.display.flip()

            # get current time
            newtime = pygame.time.get_ticks() # current time
        #end new


        #Before quiting pickle our location
        if self.save_on_exit == True:
            self.pickle_Bookmark()

        #close pygame
        pygame.quit()
            
    def draw_progress(self):
        # current progress
        #ratio = self.offset / len(self.words)
        ratio = float(self.offset) / len(self.words)
        #print float(self.offset) / len(self.words)

        # progress bar coordinates
        bar_x = 320 / 10
        bar_y = 240 - (self.screen.get_height() / 8)
        bar_w = 320 - 2 * bar_x 
        bar_h = bar_w / 30
        
        # progress bar frame
        outer_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        inner_rect = pygame.Rect(bar_x, bar_y, max(bar_w * ratio, 1), bar_h)

        # draw the frame
        pygame.draw.rect(self.screen, pygame.Color("white"), outer_rect, 2)
        pygame.draw.rect(self.screen, pygame.Color("white"), inner_rect)

    def ambient_text(self):#useless
        percent=(float(self.offset) / len(self.words))
        #ratio=str(float(int( (float(self.offset) / len(self.words))*10000))/100.)#Works but formating wrong losing last ie 0 .19,.2,.21
        totalTime=len(self.words)/float(self.speed)*(1-percent)
        totalSec=totalTime*60.0
        hours = int(totalSec)/3600
        minutes=int(totalSec)%3600/60
        seconds=int(totalSec)%3600%60
        ratioStr="{0:.2f}".format(percent*100)
        #timeStr="        Time Remaining: {0:.0f}hr:{1:.0f}:{2:.0f}".format(float(hours),float(minutes),float(seconds))
        #print ratioStr+timeStr
        #print ratio, type(ratio)
        speedStr="Speed: "+str(self.speed)+" WPM" +"        "+ratioStr+"%"+"       Time Remaining: "+str(hours)+"h:"+str(minutes)+"m:"+str(seconds)
        symb = self.amb_font.render(speedStr, 1, (0x99, 0x99, 0x67))
        symb_pos = 2,228
        self.screen.blit(symb, symb_pos)

#################################################

    def _skip_forward(self, look=[".", "\n", "c"]):
        "Skip forward to the next <something>"
        found = 0
        self.offset  = self.offset  + 1
        while not found:
            if self.offset  >= len(self.words):
                self.offset  = len(self.words) - 1
                #word = (self.book.word(self.offset ), self.book.type(self.offset ))
                ##self.show_word(flush=1)
                return

                #word = (self.book.word(self.offset ), self.book.type(self.offset ))

            if self.t[self.offset ] in look:
                found = 1
                self.offset  = self.offset  + 1
                ##self.show_word(flush=1)
                break

            self.offset  = self.offset  + 1

            #word = (self.book.word(self.offset ), self.book.type(self.offset ))
            
            #self.show_word(flush=1)

    def _skip_backward(self, look=[".", "\n", "c"]):
        """Skip back to the previous paragraph.
        ... or to the beginning of the current one."""
        found = 0

        # If in the first few words of the paragraph, skip to previous.
        # Else skip to beginning of current.
        self.offset  = self.offset  - self.cfg_rskip_tolerance
        while not found:
            if self.offset  < 0:
                self.offset  = 0
                return
            if self.t[self.offset ] in look:
                found = 1
                self.offset  = self.offset  + 1
                break
            self.offset  = self.offset  - 1
    
    def get_phraseToRender(self):
        local_offset = self.offset
        if (self.multimode == True): # if we are in multiword mode
            self.numWordsInPhrase = 0 # This should be 0, but to be readable you must take an average with the next phrase's delay and use that value for both... honestly just force num words to be 2, since that is the average for max a length of 16 anyway
            self.phraseToRender = ""
            #local_offset = self.offset
            #nowWord = self.words[ self.offset ]
            # to do:
            #   check if nowWord is greater than multiword_length [over 16 letters in size]
            if len(self.words[ local_offset ]) >= self.multiword_length: 
                # if it is check if it is larger than the screen
                self.phraseToRender = self.words[ local_offset ]    # set phraseToRender to just that single gigantic word
                self.numWordsInPhrase = 4          # set numWords to 4 because we need a big delay for this is a gigantic word
            else:
                flush = False
                while ( flush == False):
                    if local_offset == len(self.words): # pause at the end of the file
                        if (not self.pause):
                            self.pause = True
                            print "Reached end of file", local_offset, len(self.words)
                        flush = True
                    elif (len(self.phraseToRender) + len(self.words[ local_offset ]) + 1) <= self.multiword_length: # if (old phrase + space + newWord) is less than or equal to 16
                        self.phraseToRender = self.phraseToRender + " " + self.words[ local_offset ]
                        self.numWordsInPhrase += 1
                        local_offset += 1 # grab next word
                    else:
                        flush = True # phrase is fully loaded, end while loop
                        local_offset -= 1 # unload the most recent word that pushed us over the maxlength
                #########################################################################################
                #Eventually do the average with the next/previous phrase to make things work perfectly. 
                # Until then a much faster and easier way to make this work is to just force numWordsInPhrase = 2 since that is
                # really really really really really close to the average anyway and gives a good delay.
                if (self.numWordsInPhrase < 4): # if we are not the long word over 16 chars from above
                    self.numWordsInPhrase = 2   # force num words to be 2, since that is the average for max a length of 16 anyway
                #########################################################################################
        else: # else we are in single word mode
            self.phraseToRender = self.words[ self.offset ] # just one word
            self.numWordsInPhrase = 1 # it is one word long delayed and offset
        #self.offset = 1 + local_offset # uncomment if change dont work..., regardless of everything else, grab the next word
        self.phrase_offset = local_offset
        

#################################################
    def pickle_Bookmark(self):
        fileName=os.path.splitext(self.file)[0]
        pickleFileName= fileName+".pkl"
        pickleFile=open(pickleFileName,'w')#open (or create) a pickle file for writing
        pickle.dump(self.offset, pickleFile)#pickles our current location
        pickleFile.close()#close the file
        print "Current Location Bookmarked in pkl file"
#################################################
if __name__ == '__main__':
    spreed = Spreed()
    spreed.run()
