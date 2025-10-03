import streamlit as st
import random
import time
import pandas as pd

# 🎨 Colors (using Streamlit's color support via HTML)
def color_cell(text, color):
    if color == "red":
        return f'<span style="color:red">{text}</span>'
    elif color == "green":
        return f'<span style="color:green">{text}</span>'
    elif color == "blue":
        return f'<span style="color:blue">{text}</span>'
    elif color == "yellow":
        return f'<span style="color:orange">{text}</span>'
    return text

# Define snakes and ladders
snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

# Initialize session state
if "positions" not in st.session_state:
    st.session_state.positions = {"P1": 1, "P2": 1}
if "current_player" not in st.session_state:
    st.session_state.current_player = "P1"
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "turn_completed" not in st.session_state:
    st.session_state.turn_completed = False
if "move_messages" not in st.session_state:
    st.session_state.move_messages = []

# 🎲 Dice roll simulation
def roll_dice():
    return random.randint(1, 6)

# Build the board DataFrame
def build_board():
    board_data = []
    for row in range(10, 0, -1):
        row_data = []
        start = (row - 1) * 10 + 1
        end = row * 10
        if row % 2 == 0:
            rng = range(start, end + 1)
        else:
            rng = range(end, start - 1, -1)
        for square in rng:
            cell = str(square).rjust(3)
            if square in snakes:
                cell = color_cell("S↓", "red")
            elif square in ladders:
                cell = color_cell("L↑", "green")
            for player, pos in st.session_state.positions.items():
                if pos == square:
                    cell = color_cell(player, "blue")
            row_data.append(cell)
        board_data.append(row_data)
    return pd.DataFrame(board_data)

# Display board as styled table
def display_board():
    df = build_board()
    st.markdown(df.style.to_html(), unsafe_allow_html=True)
    st.markdown("---")

# Snake/ladder move with progress
def handle_snake_ladder(player, start, end):
    if start == end:  # No movement needed
        return
    st.session_state.move_messages.append(f"{player} moving from {start} to {end}...")
    with st.spinner(f"{player} moving from {start} to {end}..."):
        step = 1 if end > start else -1
        steps = abs(end - start) + 1
        progress_bar = st.progress(0)
        for i, pos in enumerate(range(start, end + step, step)):
            st.session_state.positions[player] = pos
            # Cap progress to [0.0, 1.0]
            progress = min((i + 1) / steps, 1.0)
            progress_bar.progress(progress)
            time.sleep(0.05)  # Quick animation
        progress_bar.empty()

# Main app
st.title("🐍🪜 Snakes and Ladders - Human vs. Computer")
st.write("**P1 (You)**: Click to roll. **P2 (Computer)**: Auto-rolls after you click 'Continue'.")

if st.session_state.game_over:
    st.balloons()
    if st.button("Play Again?"):
        st.session_state.positions = {"P1": 1, "P2": 1}
        st.session_state.current_player = "P1"
        st.session_state.game_over = False
        st.session_state.turn_completed = False
        st.session_state.move_messages = []
        st.rerun()
    st.stop()

# Display move messages
for msg in st.session_state.move_messages:
    st.write(msg)

display_board()

player = st.session_state.current_player
if player == "P1":
    if not st.session_state.turn_completed:
        if st.button("Roll Dice (P1's Turn) 🎲", use_container_width=True):
            roll = roll_dice()
            st.session_state.move_messages.append(f"You rolled a {roll}!")
            st.session_state.positions[player] += roll
            if st.session_state.positions[player] > 100:
                st.session_state.positions[player] -= roll
                st.session_state.move_messages.append(f"Overshot! Need {100 - st.session_state.positions[player]} more.")
            else:
                if st.session_state.positions[player] in ladders:
                    new_pos = ladders[st.session_state.positions[player]]
                    st.session_state.move_messages.append("Ladder! Climb up! 🎉")
                    handle_snake_ladder(player, st.session_state.positions[player], new_pos)
                    st.session_state.positions[player] = new_pos
                elif st.session_state.positions[player] in snakes:
                    new_pos = snakes[st.session_state.positions[player]]
                    st.session_state.move_messages.append("Snake! Slide down! 🐍")
                    handle_snake_ladder(player, st.session_state.positions[player], new_pos)
                    st.session_state.positions[player] = new_pos
            st.session_state.turn_completed = True
            if st.session_state.positions[player] == 100:
                st.session_state.game_over = True
                st.session_state.move_messages.append(f"{player} Wins! 🏆🎉")
            st.rerun()
    else:
        if st.button("Continue to P2's Turn"):
            st.session_state.current_player = "P2"
            st.session_state.turn_completed = False
            st.session_state.move_messages = []
            st.rerun()
else:  # P2 (Computer)
    if not st.session_state.turn_completed:
        st.info("Computer's turn... Thinking 🤖")
        time.sleep(1)  # Pause
        roll = roll_dice()
        st.session_state.move_messages.append(f"Computer rolled a {roll}!")
        st.session_state.positions[player] += roll
        if st.session_state.positions[player] > 100:
            st.session_state.positions[player] -= roll
            st.session_state.move_messages.append(f"Computer overshot! Needs {100 - st.session_state.positions[player]} more.")
        else:
            if st.session_state.positions[player] in ladders:
                new_pos = ladders[st.session_state.positions[player]]
                st.session_state.move_messages.append("Computer climbs ladder! 🎉")
                handle_snake_ladder(player, st.session_state.positions[player], new_pos)
                st.session_state.positions[player] = new_pos
            elif st.session_state.positions[player] in snakes:
                new_pos = snakes[st.session_state.positions[player]]
                st.session_state.move_messages.append("Computer slides down snake! 🐍")
                handle_snake_ladder(player, st.session_state.positions[player], new_pos)
                st.session_state.positions[player] = new_pos
        st.session_state.turn_completed = True
        if st.session_state.positions[player] == 100:
            st.session_state.game_over = True
            st.session_state.move_messages.append(f"{player} Wins! 🏆🎉")
        st.rerun()
    else:
        if st.button("Continue to P1's Turn"):
            st.session_state.current_player = "P1"
            st.session_state.turn_completed = False
            st.session_state.move_messages = []
            st.rerun()
