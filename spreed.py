#!/usr/bin/env python

import pygame, sys
import argparse
import math
import pickle
import os

from pygame.locals import *

defaultSpeed = 450 #defaultSpeed 300

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

        # init display 
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
            
        # read text
        f = open(self.file, 'r')
        self.raw_text = f.read()
        f.close() # I can't believe this was missing for so long -- ALWAYS close Files when finished with them
        self.words = self.raw_text.split()
        self.words.append("--- END ---")

        # init clock
        self.clock = pygame.time.Clock()

        # init state variables
        self.running = True
        self.show_progress = True
        self.show_ambient = True
        self.pause = True 
        self.word = 0
        
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
                self.word = lastWord
            else:
                print "Invalid Bookmark! :"+str(lastWord)+" !< " + str(len(self.words))
                self.word = 0;
            pickleFile.close()#close
            firstTime=False
        #Create one if it doesn't
        pickleFile=open(pickleFileName,'w')#open (or create) a pickle file for writing
        pickle.dump(self.word,pickleFile)#pickles our current location
        pickleFile.close()#close the file
        if firstTime:
            print "Created a new bookmark pickle file."

    def run(self):
        # get initial time
        time = pygame.time.get_ticks() 
        deltaP =0
        
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
                if event.type is KEYDOWN:
                    if event.key == BTN_SELECT:
                        self.running = False
                    #if event.key == K_q:
                    #    self.running = False
                    if event.key == BTN_Y:
                        self.show_progress = not self.show_progress
                        self.show_ambient = not self.show_ambient
                    if event.key == BTN_A:
                        self.pause = not self.pause
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
                    if event.key == BTN_X:
                        self.speed = defaultSpeed
                    if event.key == BTN_DPAD_LEFT:
                        self.word -= 1
                    if event.key == BTN_DPAD_RIGHT:
                        self.word += 1
                    if event.key == BTN_DPAD_UP:
                        deltaP = (deltaP+10)%100
                        self.word = percent * deltaP
                        #print deltaP
                    if event.key == BTN_DPAD_DOWN:
                        deltaP = (deltaP-10)%100
                        self.word = percent * deltaP
                        #print deltaP
                    if event.key == K_0:
                        deltaP=0
                        self.word = 0
                    if event.key == K_1:
                        deltaP=10
                        self.word = percent * deltaP 
                    if event.key == K_2:
                        deltaP=20
                        self.word = percent * deltaP
                    if event.key == K_3:
                        deltaP=30
                        self.word = percent * deltaP
                    if event.key == K_4:
                        deltaP=40
                        self.word = percent * deltaP 
                    if event.key == K_5:
                        deltaP=50
                        self.word = percent * deltaP
                    if event.key == K_6:
                        deltaP=60
                        self.word = percent * deltaP
                    if event.key == K_7:
                        deltaP=70
                        self.word = percent * deltaP
                    if event.key == K_8:
                        deltaP=80
                        self.word = percent * deltaP
                    if event.key == K_9:
                        deltaP=90
                        self.word = percent * deltaP

            self.word %= len(self.words) # current word is word modulus len(all)

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
            
            # render text
            self.text = self.font.render(self.words[self.word], 1, 
                                         (FG_COLOR))
            self.textpos = self.text.get_rect(
                                centerx=320 / 2,
                                centery=240 / 2)
            self.screen.blit(self.text, self.textpos)

            # draw progress bar
            if self.show_progress:
                self.draw_progress()

            # draw ambient text symbols
            if self.show_ambient:
                self.ambient_text()

            # update screen
            pygame.display.flip()

            # get time
            newtime = pygame.time.get_ticks() 

            if self.word == len(self.words) - 1:
                self.pause = True

            # advance word
            if not self.pause and newtime - time > 1000 / (self.speed / 60):
                time = pygame.time.get_ticks() 
                self.word += 1

        #Before quiting pickle our location
        fileName=os.path.splitext(self.file)[0]
        pickleFileName= fileName+".pkl"
        pickleFile=open(pickleFileName,'w')#open (or create) a pickle file for writing
        pickle.dump(self.word,pickleFile)#pickles our current location
        pickleFile.close()#close the file
        print "Current Location Bookmarked in pkl file"

        #close pygame
        pygame.quit()
        
    def draw_progress(self):
        # current progress
        #ratio = self.word / len(self.words)
        ratio = float(self.word) / len(self.words)
        #print float(self.word) / len(self.words)

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
        percent=(float(self.word) / len(self.words))
        #ratio=str(float(int( (float(self.word) / len(self.words))*10000))/100.)#Works but formating wrong losing last ie 0 .19,.2,.21
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

if __name__ == '__main__':
    spreed = Spreed()
    spreed.run()
