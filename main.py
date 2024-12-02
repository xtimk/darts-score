from machine import Pin, I2C
from sh1106 import SH1106_I2C
from tm1637 import TM1637
from keypad import Keypad  # Import the keypad library
from time import sleep

# Constants
PLAYER_1 = 0
PLAYER_2 = 1
DEBOUNCE_DELAY = 0.15

# Debounce delay in seconds

# Initialize 7-segment displays
tm1 = TM1637(clk=Pin(2), dio=Pin(3))  # Adjust pins as needed
tm2 = TM1637(clk=Pin(4), dio=Pin(5))  # Adjust pins as needed

# Initialize OLED using the provided SH1106 library
i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)  # Updated pins and I2C bus number
oled = SH1106_I2C(128, 64, i2c, addr=0x3c)

# Initialize keypad
row_pins = [Pin(6), Pin(7), Pin(8), Pin(9)]
col_pins = [Pin(10), Pin(11), Pin(12), Pin(13)]
keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]
keypad = Keypad(row_pins, col_pins, keys)

# Initialize scores and state
scores = [501, 501]
current_player = PLAYER_1
history = []  # List to track score changes for undo functionality
player_1_first = False  # Tracks which player goes first

# Helper function to display scores on 7-segment displays
def update_7seg():
    tm1.show("{:04d}".format(scores[PLAYER_1]))
    tm2.show("{:04d}".format(scores[PLAYER_2]))

# Helper function to display info on OLED
def update_oled():
    oled.fill(0)
    oled.text(f"Player 1: {scores[PLAYER_1]}", 0, 0)
    oled.text(f"Player 2: {scores[PLAYER_2]}", 0, 16)
    oled.text(f"Turn: Player {current_player + 1}", 0, 32)
    oled.show()

# Function to process input from keypad with debounce
def get_keypad_input():
    last_key = None
    while True:
        key = keypad.read_keypad()
        if key is not None and key != last_key:  # Check for change in key state
            sleep(DEBOUNCE_DELAY)  # Add debounce delay
            if key == keypad.read_keypad():  # Confirm key is still pressed
                last_key = key
                return key
        elif key is None:
            last_key = None  # Reset when no key is pressed
        sleep(0.01)  # Small delay to prevent CPU overload

# Function to restart the game
def restart_game():
    global scores, current_player, history, player_1_first
    scores = [501, 501]
    history = []
    player_1_first = not player_1_first  # Alternate starting player
    current_player = PLAYER_1 if player_1_first else PLAYER_2
    update_7seg()
    update_oled()

# Function to undo the last score input
def undo_last_input():
    global scores, current_player
    if history:
        last_player, last_score = history.pop()
        scores[last_player] += last_score
        current_player = last_player
        update_7seg()
        update_oled()
    else:
        oled.fill(0)
        oled.text("No moves to undo!", 0, 16)
        oled.show()
        sleep(2)

# Function to end the game and wait for next action
def end_game(winning_player):
    oled.fill(0)
    oled.text(f"Player {winning_player + 1} Wins!", 0, 16)
    oled.text("Press B to play again", 0, 32)
    oled.show()

    while True:
        key = get_keypad_input()
        if key == 'B':  # Continue to next game
            restart_game()
            break

# Main game loop
restart_game()

while True:
    oled.fill(0)
    oled.text(f"Player {current_player + 1} Turn:", 0, 0)
    oled.text("Enter score:", 0, 16)
    oled.show()
    
    # Read score from keypad
    score_str = ""
    while True:
        key = get_keypad_input()
        print(f"got {key}")
        if key == '#':  # Confirm entry
            break
        elif key == '*':  # Cancel/reset entry
            score_str = ""
            oled.fill_rect(0, 32, 128, 8, 0)  # Clear input line
            oled.show()
        elif key == 'A':  # Abort and restart game
            print("got A")
            restart_game()
            break
        elif key == 'D':  # Undo last input
            print("got D")
            undo_last_input()
            break
        elif key.isdigit():
            score_str += key
            oled.fill_rect(0, 32, 128, 8, 0)  # Clear input line
            oled.text(score_str, 0, 32)
            oled.show()
    
    if key in ['A', 'D']:
        continue  # Skip further processing for these keys

    if score_str.isdigit():
        score = int(score_str)
        if 0 <= score <= scores[current_player]:
            history.append((current_player, score))  # Save move for undo
            scores[current_player] -= score
            current_player = 1 - current_player  # Switch player
        else:
            oled.fill(0)
            oled.text("Invalid score!", 0, 0)
            oled.show()
            sleep(2)

    # Update displays
    update_7seg()
    update_oled()

    # Check for a winner
    if scores[PLAYER_1] == 0:
        end_game(PLAYER_1)
    elif scores[PLAYER_2] == 0:
        end_game(PLAYER_2)

