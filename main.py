#!/usr/bin/python3

import time

import numpy as np
import simpleaudio as sa

from morseTable import *

class MorsePlayer():
  def __init__(self, wordsPerMin):
    self.sampleRate = 44100
    self.frequency = 300

    self.unitLength = 60 / (50 * wordsPerMin)
    self.symbolWaitLength = self.unitLength * 1
    self.letterWaitLength = self.unitLength * 3
    self.wordWaitLength = self.unitLength * 7

    #Generate audio buffers
    self.dotBuffer = [None]
    self.dashBuffer = [None]
    self._genBuffer(self.dotBuffer, 1)
    self._genBuffer(self.dashBuffer, 3)

  def _genBuffer(self, target, length):
    soundLength = self.unitLength * length
    steps = np.linspace(0, soundLength, int(soundLength * self.sampleRate), False)
    wave = np.sin(self.frequency * steps * 2 * np.pi)
    #Compress to 16-bit
    wave = wave * (2**15 - 1) / np.max(np.abs(wave))

    target[0] = wave.astype(np.int16)

  def _playSound(self, buffer):
    play_obj = sa.play_buffer(buffer[0], 1, 2, self.sampleRate)
    play_obj.wait_done()

  def playDot(self):
    self._playSound(self.dotBuffer)

  def playDash(self):
    self._playSound(self.dashBuffer)

class MorseProcessor():
  def __init__(self, wordsPerMin):
    self.player = MorsePlayer(wordsPerMin)

  def readString(self, inputString):
    for char in inputString:
      #Wait between words
      if char == " ":
        time.sleep(self.player.wordWaitLength)
        continue

      symbolList = characterTable[char.lower()]
      isFirstSound = True
      for symbol in symbolList:
        if symbol == 0:
          self.player.playDot()
        else:
          self.player.playDash()

        #Wait between symbols
        time.sleep(self.player.letterWaitLength - self.player.symbolWaitLength)

      #Wait between letters
      time.sleep(self.player.letterWaitLength)

reader = MorseProcessor(10)
reader.readString("PARIS")
