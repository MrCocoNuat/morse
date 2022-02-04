import random, time, sys
from colorama import init, Fore, Back, Style
import pyaudio
from math import sin

#replace ALSA lib's error handler with one that trashes messages

from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    ...
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def suppressALSA():
    asound = cdll.LoadLibrary("libasound.so")
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

#Merci, https://stackoverflow.com/a/17673011 - Nils Werner


''' table of morse code patterns '''
morse = {'A':".-",
         'B':"-...",
         'C':"-.-.",
         'D':"-..",
         'E':".",
         'F':"..-.",
         'G':"--.",
         'H':"....",
         'I':"..",
         'J':".---",
         'K':"-.-",
         'L':".-..",
         'M':"--",
         'N':"-.",
         'O':"---",
         'P':".--.",
         'Q':"--.-",
         'R':".-.",
         'S':"...",
         'T':"-",
         'U':"..-",
         'V':"...-",
         'W':".--",
         'X':"-..-",
         'Y':"-.--",
         'Z':"--.."}


''' returns a list of indices *** IN s1 *** of matching characters '''
''' and only returns one of the solutions, don't need every one anyways '''
''' specifically the lcs with all characters closest to the end '''
''' so, use a trick, reverse the strings and outputs, to get the substring '''
''' with all characters closest to the beginning '''
def lcs(s1, s2):
    s1, s2 = s1[::-1], s2[::-1] #reverse strings
    #use the matrix method with linear space
    prev_row = []
    for row_number in range(len(s1)+1):
        row = []
        for col_number in range(len(s2)+1):
            if row_number*col_number == 0:
                row.append((0,[])) #insert 0 pads for ease of algorithm 
                continue
            if s1[row_number-1] == s2[col_number-1]: #match, use immediately
                prior_entry = prev_row[col_number-1]
                new_index = row_number-1 #of s1
                row.append((prior_entry[0]+1, prior_entry[1]+[new_index]))
            else: #no match
                prior_A = row[col_number-1]
                prior_B = prev_row[col_number]
                row.append(prior_A if prior_A[0] >= prior_B[0] else prior_B)
        prev_row = row
    return [len(s1)-1-n for n in row[-1][1]] #unreverse outputs


''' simple transform from [-1,1] to [0,255] '''
amplitude = 32
def sin_byte(n):
    return int(sin(n)*amplitude + 127)

''' generate a unsigned 8-bit sine wave ".wav" file '''
''' called by a pyaudio stream '''
theta = 0
def callback(in_data, frame_count, time_info, status):
    global theta
    data = bytes([sin_byte(theta+i) for i in range(frame_count)])
    #ensure progressive generation
    theta += frame_count
    return (data, pyaudio.paContinue)



class Trainer:
    
    def __init__(self,
                 wpm=24,
                 farnsworth=False,
                 visual=False,
                 audio=True):
        
        assert visual or audio, "Cannot create trainer with visuals and audio off!"

        self.wait_time = 1.2/wpm
        #seconds that one . takes, this is pretty slow
        #wpm = 1.2/wait_time in standard timing with farnsworth off

        self.do_farnsworth = farnsworth
        self.do_visual = visual
        self.do_audio = audio

        #start up the audio stream manager
        #suppress warning messages that probably don't impact usage anyways
        with suppressALSA():
            p = pyaudio.PyAudio()

        self.stream = p.open(format=pyaudio.paUInt8, #single byte .wav file
                        channels=1, #monochannel is just fine
                        rate=4800, #adjust this if you like different freq.
                        frames_per_buffer=24, #whole buffers cannot be divided, keep this small
                        output=True,
                        stream_callback=callback)
        #immediately pause audio stream
        self.stream.stop_stream()

        self.words = self.load_list_of_words()

        print("New trainer set to",round(1.2/self.wait_time),"wpm")
        if farnsworth:
            print(" Farnsworth timing activated")
        print()
        time.sleep(0.25)

    ''' returns a big list of uppercase words '''
    def load_list_of_words(self):
        #on linux, pull words from /etc/dictionaries-common/words
        with open("/etc/dictionaries-common/words","r") as fh:
            words = fh.readlines()

        def valid(word): #no accented letters, apostrophes, ...
            for c in word.upper():        
                if c not in morse:
                    return False
            return True
            
        #remember to strip newline
        return [word.strip().upper() for word in words if valid(word.strip())]

    ''' play audio / show visual of a single character '''
    def play_char(self,char):
        if char not in morse:
            return #do nothing
        
        pattern = morse[char]
        for d in pattern:
            if d == ".":
                delay = self.wait_time
            if d == "-":
                delay = 3*self.wait_time

            if self.do_audio:
                self.stream.start_stream()
            if self.do_visual:
                print(d,end="",flush=True)
        
            #time of ./-
            time.sleep(delay)
            if self.do_audio:
                self.stream.stop_stream()
            
            #time between ./-
            time.sleep(self.wait_time)

    ''' play audio / show visual of a single word '''
    def play_word(self,word):
        for char in word:
            self.play_char(char)
        
            if self.do_visual:
                print(" ",end="",flush=True)
            time.sleep(3*self.wait_time)
            
            #farnsworth timing, inter-character pauses are double length
            if self.do_farnsworth:
                time.sleep(3*self.wait_time)

    ''' play audio / show visual of a single string '''
    def play_string(self, string):
        for word in string.split():
            self.play_word(word)

            if self.do_visual:
                #a slash separates words
                print("/ ",end="",flush=True)
            time.sleep(7*self.wait_time)
            
            #farnsworth timing, inter-character pauses are double length
            if self.do_farnsworth:
                time.sleep(7*self.wait_time)
        
            
    ''' User translates morse code to english, one word '''
    def train(self):
        word = random.choice(self.words)
     
        self.play_word(word)
        #single word only for now
        if self.do_visual:
            print()
        
        #accepts input from before input() too since buffer not flushed
        guess = input().upper()
        
        #better matching mode,
        #longest common subsequence
        #I knew Basic Algorithms would be useful for something!
        
        lcs_indices = lcs(word,guess)
    
        missed_chars = set()
        for i in range(len(word)):
            #Cyan and red are distinguishable by almost everybody,
            #much more than green and red
            if i not in lcs_indices:
                print(Fore.RED,end="")
                missed_chars.add(word[i])
            else:
                print(Fore.CYAN,end="")
            print(word[i],end="")
        
        if len(missed_chars) == 0:
            #good job!
            print(Fore.GREEN+" - Nice!",end="")
        print(Style.RESET_ALL)
    
        #remind user of codes
        for c in missed_chars:
            print("{}: {}  ".format(c,morse[c]),end="")
        if len(missed_chars) > 0:
            print()
    
        time.sleep(1)


    ''' User inputs a string to output in morse code '''
    def translate(self):
        string = input().upper()

        self.play_string(string)
        print()
