"""
Assessment 1 - Maths Quiz Application
Developed by: Zersha Muzamal

---LEARNING RESOURCES ---
1. Tkinter Basics (W3Schools): https://www.w3schools.com/python/python_gui_tkinter.asp
2. Python Random Module (W3Schools): https://www.w3schools.com/python/module_random.asp
3. Python Functions (Google for Developers): https://developers.google.com/edu/python/introduction
4. Pillow (PIL) Documentation: https://pillow.readthedocs.io/en/stable/
5. YouTube Tutorial on Tkinter Frames: https://www.youtube.com/watch?v=yQSEXcf6s2I
"""

import tkinter as tk  # We use Tkinter to build the window, buttons, and labels.
from tkinter import messagebox  # This lets us pop up alerts (like "Game Over").
import random  # Needed to generate random numbers and pick + or - operators.
from PIL import Image, ImageTk  # Using Pillow to handle the animated GIF background.

# --- 1. Configuration: Making it look good ---
# I chose a dark theme because it's easier on the eyes and looks modern.
BG_COLOR = "#202020"
TITLE_BLOCK_COLOR = "#DCDCDC"
TEXT_COLOR = "white"
ACCENT_BLUE = "#4A90E2"
ACCENT_RED = "#FF4141"
ACCENT_GREEN = "#7ED321"

BUTTON_BASE_COLOR = "#393D46"
BUTTON_HOVER_COLOR = "#50555F"

TRANSPARENT_FRAME_BG = "#1a1a1a"

# Setting up fonts so the text is big and readable.
TITLE_FONT = ("Impact", 60)
SUBTITLE_FONT = ("Impact", 28)
BUTTON_FONT = ("Arial", 18, "bold")
RULES_FONT = ("Arial", 16, "bold")
QUESTION_FONT = ("Arial", 56, "bold")
ANSWER_ENTRY_FONT = ("Arial", 48, "bold")
SMALL_FONT = ("Arial", 12)
STATUS_FONT = ("Arial", 16, "bold")

BUTTON_WIDTH = 18
RULE_BLOCK_WIDTH = 500
RULE_BLOCK_HEIGHT = 50
EMOJI_FONT_SIZE = 40
NUM_EMOJIS = 8

# --- 2. Game State: Remembering what's happening ---
# This dictionary acts like the game's "memory". It stores the score, level, and current question.
game_state = {
    'level': None,
    'question_num': 0,
    'score': 0,
    'current_attempt': 1,  # We need to know if it's the 1st or 2nd try to give points correctly.
    'skips_used': 0,
    'num1': 0,
    'num2': 0,
    'operator': '',
    'ans': 0,
    'entry': None,
    'current_page_frame': None,
    'bg_animation_label': None,
    'attempt_label': None
}

# --- 3. Background Animation Setup ---
gif_path = "Assessment 1 - Skills Portfolio/A1 - Resources/quizz_bg.gif"
frames = []
current_frame = 0

# --- 4. Main Window Setup ---
root = tk.Tk()  # This creates the main window container.
root.geometry("1000x750")  # Setting the size to 1000x750 pixels.
root.title("MY MATHS QUIZ APP")
root.resizable(False, False)  # Locking the size so the layout doesn't break.
root.config(bg=BG_COLOR)

# --- 5. Loading the GIF ---
def load_gif_frames():
    """
    This function breaks the GIF into individual pictures (frames) so Tkinter can play them.
    Ref: https://pillow.readthedocs.io/en/stable/reference/Image.html
    """
    global frames
    try:
        gif = Image.open(gif_path)
        frame_list = []
        try:
            while True:
                frame = gif.copy()
                frame = frame.resize((1000, 750))  # Stretch image to fit window
                frame_list.append(ImageTk.PhotoImage(frame))
                gif.seek(len(frame_list))  # Go to next frame
        except EOFError:
            frames = frame_list
            print(f"Success: Loaded {len(frames)} frames for background.")
    except Exception as e:
        print(f"Warning: Could not load GIF. The background will be static color. ({e})")

load_gif_frames()

# --- 6. Animation & Visual Effects ---
def animate_bg(label):
    """
    This loops through the frames to make the background move.
    It calls itself every 80 milliseconds.
    """
    if not frames:
        return

    global current_frame
    if label.winfo_exists():
        label.config(image=frames[current_frame])
        current_frame = (current_frame + 1) % len(frames)
        label.after(80, lambda: animate_bg(label))

def create_bg_animation(parent_frame):
    """Adds the animated background to a specific page."""
    if frames:
        bg_label = tk.Label(parent_frame)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()  # Send to back so text sits on top
        game_state['bg_animation_label'] = bg_label
        animate_bg(bg_label)
        parent_frame.lift()

def create_floating_emojis(emoji):
    """
    Fun Effect: Creates floating icons when you answer.
    """
    if not game_state['current_page_frame']:
        return

    parent = game_state['current_page_frame']
    emojis = []
    win_width = root.winfo_width()
    win_height = root.winfo_height()

    for _ in range(NUM_EMOJIS):
        e_label = tk.Label(parent, text=emoji, font=("Segoe UI Emoji", EMOJI_FONT_SIZE),
                           bg=parent['bg'], fg='white', bd=0, relief=tk.FLAT)
        
        # Place randomly on screen
        x = random.randint(100, win_width - 100)
        y = random.randint(100, win_height - 100)
        
        e_label.place(x=x, y=y)
        e_label.lift()
        emojis.append(e_label)

    # Remove them after 2 seconds so the screen doesn't get cluttered
    def destroy_emojis():
        for label in emojis:
            label.destroy()

    root.after(2000, destroy_emojis)

def switch_page(target_func):
    """
    This is the Page Manager. It destroys the old page and builds the new one.
    This simulates moving between screens in an app.
    """
    if game_state['current_page_frame']:
        try:
            game_state['current_page_frame'].destroy()
        except Exception:
            pass
        game_state['current_page_frame'] = None
    
    game_state['bg_animation_label'] = None
    target_func()

def confirm_exit():
    """Asks the user nicely if they really want to leave."""
    ans = messagebox.askyesno("Quit", "Are you sure you want to quit?")
    if ans:
        root.quit()

# --- 7. Core Quiz Logic (The Brains of the App) ---

def randomInt(level):
    """
    Requirement: Determines values based on difficulty level.
    Level 1: 1 digit (1-9)
    Level 2: 2 digits (10-99)
    Level 3: 4 digits (1000-9999) - as per Advanced requirement.
    Ref: https://www.w3schools.com/python/ref_random_randint.asp
    """
    if level == 1:
        return random.randint(1, 9), random.randint(1, 9)
    if level == 2:
        return random.randint(10, 99), random.randint(10, 99)
    # Advanced level requires 4 digit numbers
    return random.randint(1000, 9999), random.randint(1000, 9999)

def decideOperation():
    """
    Requirement: Randomly decides if the problem is + or -.
    Returns a character char.
    """
    return random.choice(['+', '-'])

def isCorrect(user_ans):
    """
    Requirement: Checks if user's answer matches the calculated answer.
    Returns True or False.
    """
    return user_ans == game_state['ans']

def displayResults():
    """
    Requirement: Outputs final score and ranks user.
    Redirects to the results page.
    """
    switch_page(show_results_page)

def start_new_quiz(level):
    """Resets everything (score, question count) for a fresh game."""
    game_state.update({
        'level': level,
        'question_num': 0,
        'score': 0,
        'current_attempt': 1,
        'skips_used': 0
    })
    next_question()

def next_question():
    """Sets up the math for the next round."""
    # Check if we have done 10 questions
    if game_state['question_num'] >= 10:
        displayResults()
        return

    game_state['question_num'] += 1
    game_state['current_attempt'] = 1  # Reset attempts for new question

    # Get numbers based on level
    game_state['num1'], game_state['num2'] = randomInt(game_state['level'])
    game_state['operator'] = decideOperation()
    
    # Logic fix: If subtracting, make sure we don't get negative numbers (easier for users)
    if game_state['operator'] == '-':
        if game_state['num1'] < game_state['num2']:
             game_state['num1'], game_state['num2'] = game_state['num2'], game_state['num1']
             
    # Calculate the real answer to check against later
    if game_state['operator'] == '+':
        game_state['ans'] = game_state['num1'] + game_state['num2']
    else:
        game_state['ans'] = game_state['num1'] - game_state['num2']

    displayProblem()  # Show the UI

def check_answer(user_input):
    """
    Validates input and calculates score based on attempts.
    """
    if user_input == "SKIP_REQUEST":
        handle_skip()
        return
        
    # Validation: Check if empty
    if not user_input.strip():
        create_floating_emojis('🧐') # New Emoji: Thinking face
        messagebox.showwarning("Invalid Input", "Please enter a valid whole number!")
        return

    # Validation: Check if it's a number
    try:
        user_ans = int(user_input)
    except ValueError:
        create_floating_emojis('🧐')
        messagebox.showwarning("Invalid Input", "Please enter a valid whole number!")
        if game_state.get('entry'):
            game_state['entry'].delete(0, tk.END)
        return

    if isCorrect(user_ans):
        # --- CORRECT SCENARIO ---
        # 10 points for 1st try, 5 points for 2nd try
        points = 10 if game_state['current_attempt'] == 1 else 5
        game_state['score'] += points
        
        create_floating_emojis('🌟') # New Emoji: Star/Sparkles for correct
        messagebox.showinfo("Correct!", f"✅ Correct! +{points} points.")
        next_question()
        
    else:
        # --- WRONG SCENARIO ---
        if game_state['current_attempt'] == 1:
            # First wrong answer: Give a second chance
            game_state['current_attempt'] = 2
            
            create_floating_emojis('🛡️') # New Emoji: Shield (Defense/Try again)
            messagebox.showwarning("Incorrect", "❌ Wrong answer! Try again for 5 points.")
            
            # Update the text on screen to show 2/2 attempts
            if game_state['attempt_label']:
                game_state['attempt_label'].config(text="ATTEMPT: 2/2", fg=ACCENT_RED)

            # Clear the entry box for them
            if game_state.get('entry'):
                game_state['entry'].delete(0, tk.END)
        else:
            # Second wrong answer: Move on
            create_floating_emojis('💥') # New Emoji: Explosion/Game Over
            messagebox.showerror("Incorrect", f"❌ Wrong answer!\nCorrect answer: {game_state['ans']}")
            next_question()

def handle_skip():
    """Handles the 'Skip' button logic."""
    if game_state['skips_used'] < 3:
        game_state['skips_used'] += 1
        create_floating_emojis('⏭️') # New Emoji: Next track/Skip
        messagebox.showinfo("Skipped", f"⏩ Question skipped. Skips remaining: {3 - game_state['skips_used']}")
        next_question()
    else:
        messagebox.showerror("Skip Limit Reached", "You have used all 3 skips for this quiz!")

# --- 8. GUI Builders (The Functions that draw the screens) ---

def show_welcome_page():
    """Draws the first screen you see."""
    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame)

    # Title Block
    title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, 
                           highlightbackground=ACCENT_BLUE, highlightthickness=3)
    title_block.place(relx=0.5, rely=0.35, anchor="center")

    tk.Label(title_block, text="WELCOME TO\nMY MATH QUIZ", font=TITLE_FONT, 
             fg='white', bg=TRANSPARENT_FRAME_BG, padx=40, pady=20, justify=tk.CENTER).pack()

    # Button Container
    button_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, 
                            highlightbackground='white', highlightthickness=1)
    button_frame.place(relx=0.5, rely=0.75, anchor="center")
    
    # Hover effects for buttons
    def btn_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR
    def btn_leave(e): e.widget['background'] = BUTTON_BASE_COLOR

    # Start Button -> Goes to Menu
    start_button = tk.Button(button_frame, text="START", font=BUTTON_FONT, width=BUTTON_WIDTH, 
                             bg=BUTTON_BASE_COLOR, fg='white', bd=0, relief=tk.FLAT, cursor="hand2",
                             command=lambda: switch_page(displayMenu), padx=10, pady=5)
    start_button.pack(side=tk.LEFT, padx=20, pady=10)
    start_button.bind("<Enter>", btn_enter)
    start_button.bind("<Leave>", btn_leave)

    # Rules Button
    rules_button = tk.Button(button_frame, text="RULES", font=BUTTON_FONT, width=BUTTON_WIDTH, 
                             bg=BUTTON_BASE_COLOR, fg='white', bd=0, relief=tk.FLAT, cursor="hand2",
                             command=lambda: switch_page(show_rules_page), padx=10, pady=5)
    rules_button.pack(side=tk.LEFT, padx=20, pady=10)
    rules_button.bind("<Enter>", btn_enter)
    rules_button.bind("<Leave>", btn_leave)

def show_rules_page():
    """Displays the instructions."""
    page_frame = tk.Frame(root)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame

    create_bg_animation(page_frame)
    
    # Back button to return to home
    back_button = tk.Button(page_frame, text="◀", font=("Arial", 24, "bold"), width=2, bg=TRANSPARENT_FRAME_BG, fg='white', bd=0, relief=tk.FLAT, cursor="hand2", command=lambda: switch_page(show_welcome_page))
    back_button.place(relx=0.08, rely=0.08, anchor="center")
    
    rule_title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=3, width=RULE_BLOCK_WIDTH, height=RULE_BLOCK_HEIGHT)
    rule_title_block.place(relx=0.5, rely=0.12, anchor="center")
    rule_title_block.pack_propagate(False)
    tk.Label(rule_title_block, text="Maths Quiz Rules", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).pack(expand=True)

    rules = [
        "1. 10 Maths questions per round.",
        "2. Correct on 1st Attempt = 10 Points.",
        "3. Correct on 2nd Attempt = 5 Points.",
        "4. You have TWO attempts per question.",
        "5. Difficulty determines number of digits.",
        "6. Max 3 skips allowed."
    ]

    rely = 0.28
    for r in rules:
        block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, highlightbackground='white', highlightthickness=1, width=RULE_BLOCK_WIDTH, height=RULE_BLOCK_HEIGHT)
        block.place(relx=0.5, rely=rely, anchor="center")
        block.pack_propagate(False)
        tk.Label(block, text=r, font=RULES_FONT, fg='white', bg=TRANSPARENT_FRAME_BG, anchor="w", padx=20).pack(fill="both", expand=True)
        rely += 0.12

    back_to_welcome_btn = tk.Button(page_frame, text="Back to Welcome", command=lambda: switch_page(show_welcome_page), 
                                    bg=BUTTON_BASE_COLOR, fg='white', bd=0, relief=tk.FLAT, cursor="hand2", padx=15, pady=8)
    back_to_welcome_btn.place(relx=0.5, rely=0.92, anchor="center")
    
    def back_btn_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR 
    def back_btn_leave(e): e.widget['background'] = BUTTON_BASE_COLOR
    back_to_welcome_btn.bind("<Enter>", back_btn_enter)
    back_to_welcome_btn.bind("<Leave>", back_btn_leave)

def displayMenu():
    """
    Requirement: A function that displays the difficulty level menu.
    """
    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame)

    # Simple back button
    back_button = tk.Button(page_frame, text="◀", font=("Arial", 24, "bold"), width=2, bg=TRANSPARENT_FRAME_BG, fg='white', bd=0, relief=tk.FLAT, cursor="hand2",
                             command=lambda: switch_page(show_welcome_page))
    back_button.place(relx=0.08, rely=0.08, anchor="center")

    # Menu Title
    title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=3, padx=20, pady=10)
    title_block.place(relx=0.5, rely=0.2, anchor="center")
    tk.Label(title_block, text="SELECT THE INTENSITY LEVEL", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).pack()

    buttons = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, highlightbackground='white', highlightthickness=1)
    buttons.place(relx=0.5, rely=0.55, anchor="center")
    
    # Common style for level buttons
    btn_style = {'font': BUTTON_FONT, 'width': 22, 'bg': BUTTON_BASE_COLOR, 'fg': 'white', 'bd': 0, 'relief': tk.FLAT, 'cursor': "hand2", 'padx':10, 'pady':5}

    # Creating buttons that pass the level (1, 2, or 3) to the start function
    tk.Button(buttons, text="LEVEL 1 (EASY)", command=lambda: start_new_quiz(1), **btn_style).pack(pady=10)
    tk.Button(buttons, text="LEVEL 2 (MODERATE)", command=lambda: start_new_quiz(2), **btn_style).pack(pady=10)
    tk.Button(buttons, text="LEVEL 3 (ADVANCED)", command=lambda: start_new_quiz(3), **btn_style).pack(pady=10)

    def level_btn_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR 
    def level_btn_leave(e): e.widget['background'] = BUTTON_BASE_COLOR
    
    for widget in buttons.winfo_children():
        if isinstance(widget, tk.Button):
            widget.bind("<Enter>", level_btn_enter)
            widget.bind("<Leave>", level_btn_leave)

def displayProblem():
    """
    Requirement: Displays the question to the user and accepts answer.
    """
    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame)

    # --- Top Status Bar (Score, Attempts, Question Count) ---
    status_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=20, pady=10)
    status_frame.pack(fill=tk.X, pady=(10, 5)) 

    # Using Grid to space things out evenly
    status_frame.grid_columnconfigure(0, weight=1)
    status_frame.grid_columnconfigure(1, weight=1)
    status_frame.grid_columnconfigure(2, weight=1)

    # Left: Back button & Question number
    left_status_frame = tk.Frame(status_frame, bg=TRANSPARENT_FRAME_BG)
    left_status_frame.grid(row=0, column=0, sticky="w")
    
    tk.Button(left_status_frame, text="◀", font=("Impact", 18), bg=TRANSPARENT_FRAME_BG, fg=TITLE_BLOCK_COLOR, bd=0, relief=tk.FLAT, cursor="hand2",
                command=lambda: switch_page(displayMenu)).pack(side=tk.LEFT, padx=(0, 10))

    tk.Label(left_status_frame, text=f"Q {game_state['question_num']} OUT OF 10", font=STATUS_FONT, fg=TITLE_BLOCK_COLOR, bg=TRANSPARENT_FRAME_BG).pack(side=tk.LEFT)
    
    # Center: Attempt Status (Blue for safe, Red for danger)
    attempt_str = f"ATTEMPT: {game_state['current_attempt']}/2"
    att_color = ACCENT_BLUE if game_state['current_attempt'] == 1 else ACCENT_RED
    
    game_state['attempt_label'] = tk.Label(status_frame, text=attempt_str, font=STATUS_FONT, fg=att_color, bg=TRANSPARENT_FRAME_BG)
    game_state['attempt_label'].grid(row=0, column=1, sticky="nsew")
    
    # Right: Current Score
    tk.Label(status_frame, text=f"SCORE: {game_state['score']}/100", font=STATUS_FONT, fg=ACCENT_BLUE, bg=TRANSPARENT_FRAME_BG).grid(row=0, column=2, sticky="e")


    # --- THE QUESTION BLOCK ---
    main_content_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=30, pady=30, highlightbackground='white', highlightthickness=1)
    main_content_frame.place(relx=0.5, rely=0.5, anchor="center")

    question_block = tk.Frame(main_content_frame, bg='white', padx=30, pady=25, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=2)
    question_block.pack(pady=20)

    # Coloring the operator to make it stand out
    op_col = ACCENT_BLUE if game_state['operator'] == '+' else ACCENT_RED
    
    # Putting the numbers and operator in a row
    tk.Label(question_block, text=f"{game_state['num1']}", font=QUESTION_FONT, fg='#303030', bg='white').pack(side=tk.LEFT, padx=15)
    tk.Label(question_block, text=game_state['operator'], font=QUESTION_FONT, fg=op_col, bg='white').pack(side=tk.LEFT, padx=15)
    tk.Label(question_block, text=f"{game_state['num2']}", font=QUESTION_FONT, fg='#303030', bg='white').pack(side=tk.LEFT, padx=15)
    tk.Label(question_block, text="=", font=QUESTION_FONT, fg='#303030', bg='white').pack(side=tk.LEFT, padx=15)

    # --- ANSWER ENTRY BOX ---
    entry_frame = tk.Frame(main_content_frame, bg='white', bd=3, relief=tk.SOLID, highlightbackground=ACCENT_GREEN, highlightthickness=2)
    entry_frame.pack(pady=25)
    
    game_state['entry'] = tk.Entry(entry_frame, font=ANSWER_ENTRY_FONT, width=8, justify='center', bg='white', fg='#303030', insertbackground='#303030', relief=tk.FLAT, bd=0, highlightthickness=0)
    game_state['entry'].pack(padx=20, pady=10)
    game_state['entry'].focus() # Automatically puts cursor in box
    # Allow pressing "Enter" key to submit
    game_state['entry'].bind('<Return>', lambda event: check_answer(game_state['entry'].get()))

    # --- SUBMIT BUTTON ---
    submit_button = tk.Button(main_content_frame, text="SUBMIT", font=BUTTON_FONT, width=18, bg=BUTTON_BASE_COLOR, fg='white', bd=0, relief=tk.FLAT, cursor="hand2", command=lambda: check_answer(game_state['entry'].get()),
                              padx=20, pady=10)
    submit_button.pack(pady=30)
    
    def on_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR 
    def on_leave(e): e.widget['background'] = BUTTON_BASE_COLOR
    submit_button.bind("<Enter>", on_enter)
    submit_button.bind("<Leave>", on_leave)

    # --- BOTTOM MENU (Restart, Quit, Skip) ---
    action_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=10, pady=10)
    action_frame.place(relx=0.5, rely=0.92, anchor="center")
    
    btn_style_small = {'font': SMALL_FONT, 'width': 10, 'height': 2, 'bg': BUTTON_BASE_COLOR, 'fg': 'white', 'bd': 0, 'relief': tk.FLAT, 'cursor': "hand2", 'padx': 10, 'pady': 5}
    
    restart_btn = tk.Button(action_frame, text="RESTART", command=lambda: switch_page(displayMenu), **btn_style_small)
    restart_btn.pack(side=tk.LEFT, padx=10)
    
    quit_btn = tk.Button(action_frame, text="QUIT", command=confirm_exit, **btn_style_small)
    quit_btn.pack(side=tk.LEFT, padx=10)
    
    skip_btn = tk.Button(action_frame, text=f"SKIP ({3 - game_state['skips_used']})", command=handle_skip, **btn_style_small)
    skip_btn.pack(side=tk.LEFT, padx=10)

    def on_small_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR
    def on_small_leave(e): e.widget['background'] = BUTTON_BASE_COLOR
        
    for btn in [restart_btn, quit_btn, skip_btn]:
        btn.bind("<Enter>", on_small_enter)
        btn.bind("<Leave>", on_small_leave)

def show_results_page():
    """
    Requirement: Function that outputs the users final score and ranks.
    """
    score = game_state['score']
    
    # Grading logic
    if score >= 90: grade, msgg = "A+", "Phenomenal! You’ve mastered this!"
    elif score >= 80: grade, msgg = "A", "Amazing effort — excellence achieved!"
    elif score >= 70: grade, msgg = "B", "Solid performance! You’re getting stronger!"
    elif score >= 60: grade, msgg = "C", "You’re improving — keep the momentum!"
    else: grade, msgg = "F", "Don’t quit — keep trying!"

    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame)
    
    # Header
    title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, padx=20, pady=10, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=3)
    title_block.place(relx=0.5, rely=0.1, anchor="center")
    tk.Label(title_block, text="QUIZ COMPLETED", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).pack()

    # Results Card
    card_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=40, pady=30, highlightbackground='white', highlightthickness=1)
    card_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(card_frame, text="SCORE:", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).grid(row=0, column=0, sticky="w", pady=10, padx=10)
    tk.Label(card_frame, text=f"{score}/100", font=TITLE_FONT, fg="#FFD700", bg=TRANSPARENT_FRAME_BG).grid(row=1, column=0, sticky="w", padx=10)

    tk.Label(card_frame, text="RANK:", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).grid(row=0, column=1, sticky="w", pady=10, padx=80)
    tk.Label(card_frame, text=grade, font=TITLE_FONT, fg=ACCENT_BLUE, bg=TRANSPARENT_FRAME_BG).grid(row=1, column=1, sticky="w", padx=80)

    tk.Label(card_frame, text=msgg, font=RULES_FONT, fg='white', bg=TRANSPARENT_FRAME_BG, wraplength=400, justify=tk.CENTER).grid(row=2, column=0, columnspan=2, pady=25)

    # End Game Actions
    buttons_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=10, pady=10)
    buttons_frame.place(relx=0.5, rely=0.85, anchor="center")
    
    btn_style_result = {'font': SMALL_FONT, 'width': 12, 'height': 2, 'bg': BUTTON_BASE_COLOR, 'fg': 'white', 'bd': 0, 'relief': tk.FLAT, 'cursor': "hand2", 'padx': 10, 'pady': 5}

    tk.Button(buttons_frame, text="PLAY AGAIN", command=lambda: switch_page(displayMenu), **btn_style_result).grid(row=0, column=0, padx=15, pady=10)
    tk.Button(buttons_frame, text="EXIT", command=confirm_exit, **btn_style_result).grid(row=0, column=1, padx=15, pady=10)
    
    # Extra feature buttons for future expansion
    tk.Button(buttons_frame, text="LEVEL UP", command=lambda: switch_page(displayMenu), **btn_style_result).grid(row=1, column=0, padx=15, pady=10)
    tk.Button(buttons_frame, text="LEVEL DOWN", command=lambda: switch_page(displayMenu), **btn_style_result).grid(row=1, column=1, padx=15, pady=10)
    
    def on_result_btn_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR
    def on_result_btn_leave(e): e.widget['background'] = BUTTON_BASE_COLOR
        
    for widget in buttons_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.bind("<Enter>", on_result_btn_enter)
            widget.bind("<Leave>", on_result_btn_leave)


# --- 9. Launching the App ---
show_welcome_page()

# Cleanup when closing window
def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop() # This keeps the window open!
