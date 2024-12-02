# Darts Score System
A dart score tracker written in micropython.

Is intended to be installed in a microcontroller like the raspberry pico.

## Basic information

There are 2 digits displays, tracking points of each player, then a oled display (sh1106) connected via i2c where are shown the informations about turn and feedback when users input scores.
There is also a 4x4 keypad that users use to input scores.

In each turn a user can:

 - input scores: input a number then press # to confirm or * to undo
 - press D to undo the last inserted score. This can be done until the 2 players returns to 501 (the initial state)
 - press A to abort current leg and start a new one. You can press A multiple times to switch players turn.
 - when a leg ends (a player reachs 0) the oled displays information about the winner. By pressing B another leg is started and the players automatically switch turns.

## Pins customization

At the beginning of main.py you can find settings of pin used, that can be modified (ToDo: a easier way to configure pins outside main)

