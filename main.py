#!/usr/bin/python3

import time
import random

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

class MorseTrainer():
  def __init__(self, wordsPerMin, filename = None):
    self.processor = MorseProcessor(wordsPerMin)

    self.inputMethod = "random"
    self.fileData = None
    self.fileIndex = 0
    if filename != None:
      self.inputMethod = "file"
      with open(filename) as file:
        self.fileData = ""
        for line in file:
          self.fileData += line.replace("\n", " ")
      self.fileData = self.fileData.strip()

  def train(self, blockLength, blockCount):
    data = []
    if self.inputMethod == "file":
      for dataIndex in range(blockCount):
        newIndex = self.fileIndex + blockLength
        data.append(self.fileData[self.fileIndex:newIndex])
        self.fileIndex = newIndex
    else:
      #Generate blockCount blocks of random data
      for dataIndex in range(blockCount):
        symbols = list(characterTable.keys())
        dataBlock = ""
        for symbolCount in range(blockLength):
          dataBlock += symbols[random.randint(0, len(symbols) - 1)]
        data.append(dataBlock)

    #Play the data
    firstBlock = True
    for block in data:
      if not firstBlock:
        time.sleep(self.processor.player.wordWaitLength)
      self.processor.readString(block)
      firstBlock = False

    #Take response and check accuracy
    response = input("Enter response:\n")
    self.validate(response, data, blockCount)

  def validate(self, response, data, blockCount):
    #Calculate percentage accuracy of response
    totalCharacters = 0
    incorrectCharacters = 0
    responseBlockIndex = 0
    for i in range(blockCount):
      correctBlock = data[i]

      #Fetch user block of text, update index
      newResponseIndex = responseBlockIndex + len(correctBlock)
      responseBlock = response[responseBlockIndex:newResponseIndex]
      responseBlockIndex = newResponseIndex

      #Compare the blocks
      totalCharacters += len(correctBlock)
      for charIndex in range(len(correctBlock)):
        correctChar = correctBlock[charIndex]
        responseChar = ""
        if len(responseBlock) - 1 >= charIndex:
          responseChar = responseBlock[charIndex]
        else:
          incorrectCharacters += 1
          continue

        if correctChar != responseChar:
          incorrectCharacters += 1

    print(f"\nCorrect response: {data}")
    print(f"Accuracy: {((totalCharacters - incorrectCharacters) / totalCharacters) * 100}%")

  def resetFilePosition():
    self.fileIndex = 0

#TODO process args
#TODO ask for target speed

trainer = MorseTrainer(15)
trainer.train(5, 4)

#TODO loop training (have defaults)
# - ask about level
# - ask about block count
# - if in file mode, ask to reset
