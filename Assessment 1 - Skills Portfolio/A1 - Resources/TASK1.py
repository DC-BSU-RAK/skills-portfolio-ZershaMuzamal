"""
Assessment 1 - Maths Quiz Application
Student Name: [Your Name Here]

--- 📚 MY LEARNING RESOURCES ---
1. Tkinter Basics (W3Schools): 
   https://www.w3schools.com/python/python_gui_tkinter.asp
   -> This helped me understand how to make the window and buttons.

2. Python Random Module (W3Schools): 
   https://www.w3schools.com/python/module_random.asp
   -> I used this to pick random numbers for the questions.

3. Python Functions (Google for Developers): 
   https://developers.google.com/edu/python/introduction
   -> Helped me organize my code into blocks like 'check_answer' and 'next_question'.

4. Pillow (PIL) Documentation: 
   https://pillow.readthedocs.io/en/stable/
   -> I used this to load the GIF frames for the background animation.
"""

import tkinter as tk  # Importing Tkinter to create the graphical interface (GUI).
from tkinter import messagebox  # Importing messagebox to show pop-ups like "Correct!" or "Game Over".
import random  # Importing random to generate the math numbers and pick operators (+ or -).
from PIL import Image, ImageTk  # Importing Pillow to handle the animated background image (GIF).

# --- 1. CONFIGURATION: Setting up the look and feel ---
# I decided to use a dark theme because it looks more modern and is easier on the eyes.
BG_COLOR = "#202020" 
TITLE_BLOCK_COLOR = "#DCDCDC" 
TEXT_COLOR = "white" 
ACCENT_BLUE = "#4A90E2"  # Blue for primary actions
ACCENT_RED = "#FF4141"   # Red for errors or subtraction
ACCENT_GREEN = "#7ED321" # Green for correct answers

BUTTON_BASE_COLOR = "#393D46" 
BUTTON_HOVER_COLOR = "#50555F" 

TRANSPARENT_FRAME_BG = "#1a1a1a" 

# Defining my fonts here so I can change them easily in one place later.
TITLE_FONT = ("Impact", 60)
SUBTITLE_FONT = ("Impact", 28)
BUTTON_FONT = ("Arial", 18, "bold")
RULES_FONT = ("Arial", 16, "bold")
QUESTION_FONT = ("Arial", 56, "bold") 
ANSWER_ENTRY_FONT = ("Arial", 48, "bold") 
SMALL_FONT = ("Arial", 12)
STATUS_FONT = ("Arial", 16, "bold") 

# Constants for layout sizes
BUTTON_WIDTH = 18
RULE_BLOCK_WIDTH = 500
RULE_BLOCK_HEIGHT = 50
EMOJI_FONT_SIZE = 40 
NUM_EMOJIS = 8      

# --- 2. GAME STATE: The brain of the app ---
# This dictionary keeps track of everything happening in the game.
# It's better than using many separate global variables.
game_state = {
    'level': None, 
    'question_num': 0, 
    'score': 0, 
    'current_attempt': 1, # Tracks if it is the 1st or 2nd attempt.
    'skips_used': 0, 
    'num1': 0, 
    'num2': 0, 
    'operator': '', 
    'ans': 0, 
    'entry': None, 
    'current_page_frame': None, 
    'bg_animation_label': None,
    'attempt_label': None # Reference to update attempt label dynamically
}

# --- 3. BACKGROUND ANIMATION SETUP ---
# I need to store the path to my GIF here.
gif_path = "Assessment 1 - Skills Portfolio/A1 - Resources/quizz_bg.gif" 
frames = [] # This list will hold the individual pictures of the GIF.
current_frame = 0 

# --- 4. MAIN WINDOW SETUP ---
root = tk.Tk() # Creating the main window.
root.geometry("1000x750") # Setting the size to 1000 pixels wide, 750 pixels tall.
root.title("MY MATHS QUIZ APP") 
root.resizable(False, False) # Making sure the window size is fixed so my layout doesn't break.
root.config(bg=BG_COLOR) 

# --- 5. LOADING THE GIF ---
def load_gif_frames():
    """
    This function splits the GIF file into separate frames so Tkinter can show them one by one.
    """
    global frames
    try:
        gif = Image.open(gif_path)
        frame_list = []
        try:
            while True:
                frame = gif.copy()
                frame = frame.resize((1000, 750)) # Resizing image to fit the window exactly.
                frame_list.append(ImageTk.PhotoImage(frame)) 
                gif.seek(len(frame_list)) # Move to the next frame in the GIF.
        except EOFError:
            frames = frame_list # Save all loaded frames.
            print(f"Loaded {len(frames)} GIF frames successfully.")
    except FileNotFoundError:
        print(f"ERROR: GIF file '{gif_path}' not found. Background animation disabled.")
    except Exception as e:
        print(f"ERROR loading GIF: {e}. Background animation disabled.")
    
load_gif_frames() # Call this immediately to load images before showing the window.


# --- 6. ANIMATION & UI HELPERS ---
def animate_bg(label):
    """
    This function runs in a loop to update the background image every 80ms.
    """
    if not frames:
        return 
        
    global current_frame
    if label.winfo_exists(): # Check if the label still exists before updating.
        label.config(image=frames[current_frame]) 
        current_frame = (current_frame + 1) % len(frames) # Loop back to 0 when we reach the end.
        label.after(80, lambda: animate_bg(label)) # Schedule the next update.

def create_bg_animation(parent_frame):
    """
    Creates the label that holds the background image and starts the animation loop.
    """
    if frames:
        bg_label = tk.Label(parent_frame)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower() # Send to back so it doesn't cover buttons.
        game_state['bg_animation_label'] = bg_label
        animate_bg(bg_label) 
        parent_frame.lift() 

def create_floating_emojis(emoji):
    """
    Fun Feature: Creates random floating emojis when you answer (like confetti).
    """
    if not game_state['current_page_frame']:
        return 

    parent = game_state['current_page_frame']
    emojis = []
    
    win_width = root.winfo_width()
    win_height = root.winfo_height()

    # Create 8 random emojis
    for _ in range(NUM_EMOJIS):
        e_label = tk.Label(parent, text=emoji, font=("Segoe UI Emoji", EMOJI_FONT_SIZE), 
                           bg=parent['bg'], fg='white', bd=0, relief=tk.FLAT)
        
        x = random.randint(100, win_width - 100)
        y = random.randint(100, win_height - 100)
        
        e_label.place(x=x, y=y)
        e_label.lift()
        emojis.append(e_label)

    # Delete them after 2 seconds to clean up.
    def destroy_emojis():
        for label in emojis:
            label.destroy()

    root.after(2000, destroy_emojis) 

def switch_page(target_func):
    """
    This function clears the current screen and loads the new one.
    It's how I navigate between Menu -> Quiz -> Results.
    """
    if game_state['current_page_frame']:
        try:
            game_state['current_page_frame'].destroy() # Destroy old widgets.
        except Exception:
            pass
        game_state['current_page_frame'] = None
    
    game_state['bg_animation_label'] = None 
    target_func() # Run the function to build the new page.

def confirm_exit():
    """Shows a confirmation box before closing the app."""
    ans = messagebox.askyesno("Quit", "Are you sure you want to quit?")
    if ans:
        root.quit()

# --- 7. CORE QUIZ LOGIC (The Maths Part) ---

def randomInt(level):
    """
    Generates random numbers based on the selected difficulty.
    Level 1: Single digits (1-9)
    Level 2: Double digits (10-99)
    Level 3: Four digits (1000-9999) as required.
    """
    if level == 1:
        return random.randint(1, 9), random.randint(1, 9) 
    if level == 2:
        return random.randint(10, 99), random.randint(10, 99) 
    # Level 3 logic
    return random.randint(1000, 9999), random.randint(1000, 9999) 

def decideOperation():
    """Randomly picks Addition (+) or Subtraction (-)."""
    return random.choice(['+', '-'])

def isCorrect(user_ans):
    """Checks if the user input matches the calculated answer."""
    return user_ans == game_state['ans']

def displayResults():
    """Moves to the final results screen."""
    switch_page(show_results_page)

def start_new_quiz(level):
    """Initializes a brand new game session."""
    game_state.update({
        'level': level,
        'question_num': 0,
        'score': 0,
        'current_attempt': 1,
        'skips_used': 0 
    })
    next_question()

def next_question():
    """Sets up the variables for the next question."""
    if game_state['question_num'] >= 10:
        displayResults() # If we did 10 questions, finish game.
        return

    game_state['question_num'] += 1
    game_state['current_attempt'] = 1 # Reset attempts for the new question

    game_state['num1'], game_state['num2'] = randomInt(game_state['level'])
    game_state['operator'] = decideOperation()
    
    # Logic to prevent negative answers (swaps numbers if needed).
    if game_state['operator'] == '-':
        if game_state['num1'] < game_state['num2']:
             game_state['num1'], game_state['num2'] = game_state['num2'], game_state['num1']
             
    # Calculate the real answer
    game_state['ans'] = game_state['num1'] + game_state['num2'] if game_state['operator'] == '+' else game_state['num1'] - game_state['num2']

    displayProblem() # Refresh the screen

def check_answer(user_input):
    """
    Validates user input and awards points.
    1st try correct = 10 points.
    2nd try correct = 5 points.
    """
    if user_input == "SKIP_REQUEST":
        handle_skip() 
        return
        
    if not user_input.strip():
        create_floating_emojis('🤔')
        messagebox.showwarning("Invalid Input", "Please enter a valid whole number!")
        return

    try:
        user_ans = int(user_input)
    except ValueError: 
        create_floating_emojis('🤔')
        messagebox.showwarning("Invalid Input", "Please enter a valid whole number!")
        if game_state.get('entry'):
            game_state['entry'].delete(0, tk.END) 
        return

    if isCorrect(user_ans):
        # Correct Answer
        points = 10 if game_state['current_attempt'] == 1 else 5
        game_state['score'] += points
        
        create_floating_emojis('😁')
        messagebox.showinfo("Correct!", f"✅ Correct! +{points} points.")
        next_question()
        
    else:
        # Wrong Answer
        if game_state['current_attempt'] == 1:
            # If it was the first try, let them try again.
            game_state['current_attempt'] = 2
            
            create_floating_emojis('🥹')
            messagebox.showwarning("Incorrect", "❌ Wrong answer! Try again for 5 points.")
            
            # Update the attempt label
            if game_state['attempt_label']:
                game_state['attempt_label'].config(text="ATTEMPT: 2/2", fg=ACCENT_RED)

            if game_state.get('entry'):
                game_state['entry'].delete(0, tk.END)
        else:
            # If it was the second try, show the answer and move on.
            create_floating_emojis('💀')
            messagebox.showerror("Incorrect", f"❌ Wrong answer!\nCorrect answer: {game_state['ans']}")
            next_question()


def handle_skip():
    """Handles the skip logic (max 3 skips)."""
    if game_state['skips_used'] < 3:
        game_state['skips_used'] += 1
        create_floating_emojis('⏩')
        messagebox.showinfo("Skipped", f"⏩ Question skipped. Skips remaining: {3 - game_state['skips_used']}")
        next_question()
    else:
        messagebox.showerror("Skip Limit Reached", "You have used all 3 skips for this quiz!")


# --- 8. GUI PAGE BUILDERS ---

def show_welcome_page():
    """Builds the main Welcome Screen."""
    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame) 

    # Title block
    title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, 
                           highlightbackground=ACCENT_BLUE, highlightthickness=3) 
    title_block.place(relx=0.5, rely=0.35, anchor="center")

    tk.Label(title_block, text="WELCOME TO\nMY MATH QUIZ", font=TITLE_FONT, 
             fg='white', bg=TRANSPARENT_FRAME_BG, padx=40, pady=20, justify=tk.CENTER).pack() 

    # Buttons
    button_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, 
                            highlightbackground='white', highlightthickness=1) 
    button_frame.place(relx=0.5, rely=0.75, anchor="center")
    
    def btn_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR 
    def btn_leave(e): e.widget['background'] = BUTTON_BASE_COLOR 

    # START Button
    start_button = tk.Button(button_frame, text="START", font=BUTTON_FONT, width=BUTTON_WIDTH, 
                             bg=BUTTON_BASE_COLOR, fg='white', bd=0, relief=tk.FLAT, cursor="hand2",
                             command=lambda: switch_page(displayMenu), padx=10, pady=5) 
    start_button.pack(side=tk.LEFT, padx=20, pady=10)
    start_button.bind("<Enter>", btn_enter)
    start_button.bind("<Leave>", btn_leave)

    # RULES Button
    rules_button = tk.Button(button_frame, text="RULES", font=BUTTON_FONT, width=BUTTON_WIDTH, 
                             bg=BUTTON_BASE_COLOR, fg='white', bd=0, relief=tk.FLAT, cursor="hand2",
                             command=lambda: switch_page(show_rules_page), padx=10, pady=5)
    rules_button.pack(side=tk.LEFT, padx=20, pady=10)
    rules_button.bind("<Enter>", btn_enter)
    rules_button.bind("<Leave>", btn_leave)


def show_rules_page():
    """Displays the Rules Screen."""
    page_frame = tk.Frame(root)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame

    create_bg_animation(page_frame)
    
    # Back button (Arrow at top left) - Keeps navigation easy.
    back_button = tk.Button(page_frame, text="◀", font=("Arial", 24, "bold"), width=2, bg=TRANSPARENT_FRAME_BG, fg='white', bd=0, relief=tk.FLAT, cursor="hand2", command=lambda: switch_page(show_welcome_page))
    back_button.place(relx=0.08, rely=0.08, anchor="center")
    
    rule_title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=3, width=RULE_BLOCK_WIDTH, height=RULE_BLOCK_HEIGHT)
    rule_title_block.place(relx=0.5, rely=0.12, anchor="center")
    rule_title_block.pack_propagate(False)
    tk.Label(rule_title_block, text="Maths Quiz Rules", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).pack(expand=True)

    # List of rules
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

    # NOTE: I removed the bottom "Back to Welcome" button as requested.
    # Users can use the arrow button at the top left.


def displayMenu():
    """Allows the user to select difficulty."""
    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame)

    back_button = tk.Button(page_frame, text="◀", font=("Arial", 24, "bold"), width=2, bg=TRANSPARENT_FRAME_BG, fg='white', bd=0, relief=tk.FLAT, cursor="hand2",
                             command=lambda: switch_page(show_welcome_page))
    back_button.place(relx=0.08, rely=0.08, anchor="center")

    title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=3, padx=20, pady=10)
    title_block.place(relx=0.5, rely=0.2, anchor="center")
    tk.Label(title_block, text="SELECT THE INTENSITY LEVEL", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).pack()

    buttons = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, highlightbackground='white', highlightthickness=1)
    buttons.place(relx=0.5, rely=0.55, anchor="center")
    
    btn_style = {'font': BUTTON_FONT, 'width': 22, 'bg': BUTTON_BASE_COLOR, 'fg': 'white', 'bd': 0, 'relief': tk.FLAT, 'cursor': "hand2", 'padx':10, 'pady':5}

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
    """Displays the Question Screen."""
    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame)

    # --- Top Status Bar ---
    status_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=20, pady=10)
    status_frame.pack(fill=tk.X, pady=(10, 5)) 

    status_frame.grid_columnconfigure(0, weight=1) 
    status_frame.grid_columnconfigure(1, weight=1) 
    status_frame.grid_columnconfigure(2, weight=1) 

    # Left status frame
    left_status_frame = tk.Frame(status_frame, bg=TRANSPARENT_FRAME_BG)
    left_status_frame.grid(row=0, column=0, sticky="w")
    
    tk.Button(left_status_frame, text="◀", font=("Impact", 18), bg=TRANSPARENT_FRAME_BG, fg=TITLE_BLOCK_COLOR, bd=0, relief=tk.FLAT, cursor="hand2",
                command=lambda: switch_page(displayMenu)).pack(side=tk.LEFT, padx=(0, 10))

    tk.Label(left_status_frame, text=f"Q {game_state['question_num']} OUT OF 10", font=STATUS_FONT, fg=TITLE_BLOCK_COLOR, bg=TRANSPARENT_FRAME_BG).pack(side=tk.LEFT)
    
    # Center - ATTEMPT logic
    attempt_str = f"ATTEMPT: {game_state['current_attempt']}/2"
    att_color = ACCENT_BLUE if game_state['current_attempt'] == 1 else ACCENT_RED
    
    game_state['attempt_label'] = tk.Label(status_frame, text=attempt_str, font=STATUS_FONT, fg=att_color, bg=TRANSPARENT_FRAME_BG)
    game_state['attempt_label'].grid(row=0, column=1, sticky="nsew")
    
    # Right Score
    tk.Label(status_frame, text=f"SCORE: {game_state['score']}/100", font=STATUS_FONT, fg=ACCENT_BLUE, bg=TRANSPARENT_FRAME_BG).grid(row=0, column=2, sticky="e")


    # --- MAIN CONTENT BLOCK ---
    main_content_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=30, pady=30, highlightbackground='white', highlightthickness=1)
    main_content_frame.place(relx=0.5, rely=0.5, anchor="center") 

    # --- Question Display ---
    question_block = tk.Frame(main_content_frame, bg='white', padx=30, pady=25, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=2)
    question_block.pack(pady=20) 

    op_col = ACCENT_BLUE if game_state['operator'] == '+' else ACCENT_RED
    tk.Label(question_block, text=f"{game_state['num1']}", font=QUESTION_FONT, fg='#303030', bg='white').pack(side=tk.LEFT, padx=15)
    tk.Label(question_block, text=game_state['operator'], font=QUESTION_FONT, fg=op_col, bg='white').pack(side=tk.LEFT, padx=15)
    tk.Label(question_block, text=f"{game_state['num2']}", font=QUESTION_FONT, fg='#303030', bg='white').pack(side=tk.LEFT, padx=15)
    tk.Label(question_block, text="=", font=QUESTION_FONT, fg='#303030', bg='white').pack(side=tk.LEFT, padx=15)

    # --- Answer Entry ---
    entry_frame = tk.Frame(main_content_frame, bg='white', bd=3, relief=tk.SOLID, highlightbackground=ACCENT_GREEN, highlightthickness=2)
    entry_frame.pack(pady=25)
    game_state['entry'] = tk.Entry(entry_frame, font=ANSWER_ENTRY_FONT, width=8, justify='center', bg='white', fg='#303030', insertbackground='#303030', relief=tk.FLAT, bd=0, highlightthickness=0)
    game_state['entry'].pack(padx=20, pady=10) 
    game_state['entry'].focus()
    game_state['entry'].bind('<Return>', lambda event: check_answer(game_state['entry'].get()))

    # --- Submit Button ---
    submit_button = tk.Button(main_content_frame, text="SUBMIT", font=BUTTON_FONT, width=18, bg=BUTTON_BASE_COLOR, fg='white', bd=0, relief=tk.FLAT, cursor="hand2", command=lambda: check_answer(game_state['entry'].get()),
                              padx=20, pady=10) 
    submit_button.pack(pady=30)
    
    def on_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR 
    def on_leave(e): e.widget['background'] = BUTTON_BASE_COLOR
    submit_button.bind("<Enter>", on_enter)
    submit_button.bind("<Leave>", on_leave)

    # --- Bottom Actions ---
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
    """Calculates marks and shows the final report card."""
    score = game_state['score']
    
    if score >= 90: grade, msgg = "A+", "Phenomenal! You’ve mastered this!"
    elif score >= 80: grade, msgg = "A", "Amazing effort — excellence achieved!"
    elif score >= 70: grade, msgg = "B", "Solid performance! You’re getting stronger!"
    elif score >= 60: grade, msgg = "C", "You’re improving — keep the momentum!"
    else: grade, msgg = "F", "Don’t quit — keep trying!"

    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(x=0, y=0, relwidth=1, relheight=1)
    game_state['current_page_frame'] = page_frame
    
    create_bg_animation(page_frame)
    
    title_block = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, padx=20, pady=10, bd=0, relief=tk.FLAT, highlightbackground=ACCENT_BLUE, highlightthickness=3)
    title_block.place(relx=0.5, rely=0.1, anchor="center")
    tk.Label(title_block, text="QUIZ COMPLETED", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).pack()

    card_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=40, pady=30, highlightbackground='white', highlightthickness=1)
    card_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(card_frame, text="SCORE:", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).grid(row=0, column=0, sticky="w", pady=10, padx=10)
    tk.Label(card_frame, text=f"{score}/100", font=TITLE_FONT, fg="#FFD700", bg=TRANSPARENT_FRAME_BG).grid(row=1, column=0, sticky="w", padx=10)

    tk.Label(card_frame, text="RANK:", font=SUBTITLE_FONT, fg='white', bg=TRANSPARENT_FRAME_BG).grid(row=0, column=1, sticky="w", pady=10, padx=80)
    tk.Label(card_frame, text=grade, font=TITLE_FONT, fg=ACCENT_BLUE, bg=TRANSPARENT_FRAME_BG).grid(row=1, column=1, sticky="w", padx=80)

    tk.Label(card_frame, text=msgg, font=RULES_FONT, fg='white', bg=TRANSPARENT_FRAME_BG, wraplength=400, justify=tk.CENTER).grid(row=2, column=0, columnspan=2, pady=25)

    buttons_frame = tk.Frame(page_frame, bg=TRANSPARENT_FRAME_BG, bd=0, relief=tk.FLAT, padx=10, pady=10)
    buttons_frame.place(relx=0.5, rely=0.85, anchor="center")
    
    btn_style_result = {'font': SMALL_FONT, 'width': 12, 'height': 2, 'bg': BUTTON_BASE_COLOR, 'fg': 'white', 'bd': 0, 'relief': tk.FLAT, 'cursor': "hand2", 'padx': 10, 'pady': 5}

    tk.Button(buttons_frame, text="PLAY AGAIN", command=lambda: switch_page(displayMenu), **btn_style_result).grid(row=0, column=0, padx=15, pady=10)
    tk.Button(buttons_frame, text="EXIT", command=confirm_exit, **btn_style_result).grid(row=0, column=1, padx=15, pady=10)
    
    tk.Button(buttons_frame, text="LEVEL UP", command=lambda: switch_page(displayMenu), **btn_style_result).grid(row=1, column=0, padx=15, pady=10)
    tk.Button(buttons_frame, text="LEVEL DOWN", command=lambda: switch_page(displayMenu), **btn_style_result).grid(row=1, column=1, padx=15, pady=10)
    
    def on_result_btn_enter(e): e.widget['background'] = BUTTON_HOVER_COLOR
    def on_result_btn_leave(e): e.widget['background'] = BUTTON_BASE_COLOR
        
    for widget in buttons_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.bind("<Enter>", on_result_btn_enter)
            widget.bind("<Leave>", on_result_btn_leave)


# --- 9. START APP ---
show_welcome_page()

def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop() # Keep window open.
