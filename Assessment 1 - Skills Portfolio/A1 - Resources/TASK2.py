"""
Assessment 1 - Joke Assistant Application
Student Name: [Your Name Here]
Date: November 2025

-------------------------------------------------------------------------
ACADEMIC REFERENCES & RESOURCES USED
-------------------------------------------------------------------------
1. Python File Input/Output:
   - Source: W3Schools
   - Concept: Reading text files and handling strings.
   - Link: https://www.w3schools.com/python/python_file_open.asp

2. Tkinter GUI Development:
   - Source: GeeksForGeeks / Official Documentation
   - Concept: Understanding Widgets, Frames, and Geometry Managers (pack/grid).
   - Link: https://www.geeksforgeeks.org/python-gui-tkinter/

3. Text-to-Speech Implementation:
   - Source: YouTube Tutorial ("Python Text to Speech using pyttsx3")
   - Concept: Initializing the pyttsx3 engine to convert string data to audio.
   - Search Query: "python pyttsx3 tutorial"

4. Concurrency with Threading:
   - Source: W3Schools / StackOverflow
   - Concept: Running the speech engine on a separate thread to prevent the 
     Graphical User Interface (GUI) from freezing during playback.
   - Link: https://www.w3schools.com/python/python_threading.asp
-------------------------------------------------------------------------
"""

# Importing the necessary libraries for the application
import tkinter as tk                # Primary library for creating the GUI window
from tkinter import messagebox      # Module for displaying pop-up alert dialogs
import random                       # Library for selecting random elements from lists
import pyttsx3                      # Library for Text-to-Speech (TTS) functionality
import threading                    # Module to allow background execution (prevents UI freezing)
import winsound                     # Native Windows library for playing .wav sound files
import string                       # Module provides string constants (used for removing punctuation)

# --- THEME CONFIGURATION ---
# Defining a dictionary to store color codes for consistent theming across the application.
# This makes it easier to change the color scheme later by modifying values in one place.
COLORS = {
    "bg_main": "#222831",       # Dark Grey Background for the main window
    "bg_dark": "#393E46",       # Slightly lighter grey for headers and content cards
    "card_bg": "#393E46",       # Specific background color for joke cards
    "accent_teal": "#00ADB5",   # Primary accent color for main action buttons
    "accent_pink": "#FF2E63",   # Secondary accent color for other interactive elements
    "accent_gold": "#FFD369",   # Highlighting color for warnings or specific emphasis
    "text_light": "#EEEEEE",    # Light text color for readability on dark backgrounds
    "text_dark": "#222831",     # Dark text color for contrast on bright buttons
    # List of colors used to randomize the visualizer bars
    "visualizer": ["#00ADB5", "#FF2E63", "#FFD369", "#71C9CE", "#CBF1F5"] 
}

# Defining a dictionary for font configurations to ensure typography consistency.
FONTS = {
    "huge": ("Segoe UI", 32, "bold"),       # Font for the main emoji icon
    "title": ("Segoe UI", 24, "bold"),      # Font for main page titles
    "subtitle": ("Segoe UI", 16),           # Font for subtitles
    "body": ("Segoe UI", 12),               # Font for general body text
    "button": ("Segoe UI", 11, "bold"),     # Font specifically for clickable buttons
    "input": ("Segoe UI", 12)               # Font for the user input entry field
}

# --------------------------
# DATA LOADING SECTION
# --------------------------
jokes = [] # Initializing an empty list to hold the joke tuples

def load_jokes_from_file():
    """
    Function to read joke data from an external text file.
    It parses the file by splitting lines at the '?' delimiter.
    """
    global jokes
    try:
        # Using a context manager 'with' to safely open and close the file
        with open("randomJokes.txt", "r", encoding="utf-8") as file:
            lines = file.readlines() # Reading all lines into a list
            for line in lines:
                # Validating that the line contains the delimiter '?'
                if "?" in line:
                    # Splitting the string into exactly two parts: setup and punchline
                    parts = line.strip().split("?", 1)
                    if len(parts) == 2:
                        # Re-appending the question mark to the setup for grammatical correctness
                        setup = parts[0] + "?"
                        punchline = parts[1]
                        # Appending the tuple (setup, punchline) to the main jokes list
                        jokes.append((setup, punchline))
        # Logging success to the console for debugging purposes
        print(f"Loaded {len(jokes)} jokes.")
        
    except FileNotFoundError:
        # Error Handling: If the file is missing, load a backup dataset to prevent crashing
        print("File not found. Using backup data.")
        jokes = [
            ("Why did the chicken cross the road?", "To get to the other side."),
            ("What happens if you boil a clown?", "You get a laughing stock."),
            ("Why did the car get a flat tire?", "Because there was a fork in the road!")
        ]

# Executing the data loading function upon application startup
load_jokes_from_file()

# --- GLOBAL VARIABLES ---
# Initializing variables to track the application state
current_joke = None             # Stores the currently selected joke tuple
is_speaking = False             # Boolean flag to track if the TTS engine is currently active
available_voices_data = []      # List to store available system voices
default_voice_index = 0         # Index to track user preference (0 for Male, 1 for Female)
DEFAULT_VOLUME = 0.9            # Setting the default volume level (0.0 to 1.0)

# Declaring UI widget references as None; these will be assigned when frames are built
joke_label = None
punchline_label = None
guess_entry = None
feedback_label = None
visualizer_canvas = None
btn_male = None
btn_female = None

# --- AUDIO & TTS LOGIC ---

def setup_tts_data():
    """
    Function to initialize the pyttsx3 engine temporarily to retrieve system voices.
    """
    global available_voices_data
    try:
        temp_engine = pyttsx3.init()
        voices = temp_engine.getProperty('voices')
        # Iterating through system voices to extract ID and Name properties
        for v in voices:
            available_voices_data.append({'id': v.id, 'name': v.name})
        del temp_engine # Deleting the temporary engine instance to free resources
    except Exception:
        pass # Silently fail if TTS initialization encounters an error

def play_sound_effect(effect_type):
    """
    Function to play specific .wav sound effects based on user interaction.
    """
    try:
        # Playing sounds asynchronously so the UI does not hang while audio plays
        if effect_type == "correct":
            winsound.PlaySound("clapping.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif effect_type == "wrong":
            winsound.PlaySound("boo.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif effect_type == "huh":
            winsound.PlaySound("huh.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass # Ignoring errors if sound files are missing

def set_voice(index):
    """
    Updates the global voice index based on user selection (Male/Female).
    """
    global default_voice_index
    if 0 <= index < len(available_voices_data):
        default_voice_index = index
        update_voice_buttons() # Refreshing the button styles to reflect the new selection

def update_voice_buttons():
    """
    Updates the visual appearance (relief style) of the voice toggle buttons.
    """
    if btn_male and btn_female:
        if default_voice_index == 0:
            # Setting 'Male' button to sunken to indicate it is active
            btn_male.config(relief=tk.SUNKEN, bg=COLORS["accent_teal"], fg=COLORS["text_light"])
            btn_female.config(relief=tk.RAISED, bg=COLORS["bg_dark"], fg=COLORS["text_light"])
        else:
            # Setting 'Female' button to sunken to indicate it is active
            btn_male.config(relief=tk.RAISED, bg=COLORS["bg_dark"], fg=COLORS["text_light"])
            btn_female.config(relief=tk.SUNKEN, bg=COLORS["accent_teal"], fg=COLORS["text_light"])

# --- VISUALIZER ANIMATION LOGIC ---

def draw_bar(canvas, x, bar_height):
    """
    Helper function to draw a single vertical bar on the visualizer canvas.
    """
    bar_width = 15
    if not canvas: return
    canvas_height = canvas.winfo_height()
    
    # Calculating Y coordinates to center the bar vertically
    y1 = (canvas_height / 2) - (bar_height / 2)
    y2 = (canvas_height / 2) + (bar_height / 2)
    
    # Selecting a random color from the defined palette for visual variety
    color = random.choice(COLORS["visualizer"])
    canvas.create_rectangle(x, y1, x + bar_width, y2, fill=color, outline="", width=0)

def animate_visualizer():
    """
    Recursive function that redraws the visualizer bars while speech is active.
    """
    global is_speaking
    # Check if speech is active and the canvas exists
    if is_speaking and visualizer_canvas:
        try:
            visualizer_canvas.delete("all") # Clearing the canvas for the next frame
            canvas_width = visualizer_canvas.winfo_width()
            num_bars = 12
            spacing = canvas_width // num_bars
            
            # Looping to draw multiple bars with random heights
            for i in range(num_bars):
                bar_height = random.randint(10, 50) # Randomizing height to simulate sound waves
                draw_bar(visualizer_canvas, i * spacing + 10, bar_height)
            
            # Scheduling this function to run again after 80ms
            visualizer_canvas.after(80, animate_visualizer)
        except Exception:
            pass
    elif visualizer_canvas:
        visualizer_canvas.delete("all") # Ensuring canvas is clean if not speaking

def stop_speaking_ui_update():
    """
    Callback function to reset the speaking flag and clear the visualizer.
    """
    global is_speaking
    is_speaking = False
    if visualizer_canvas:
        visualizer_canvas.delete("all")

def tts_thread_target(text_to_speak, voice_id):
    """
    The target function for the background thread. Handles the blocking TTS calls.
    """
    try:
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 150)
        local_engine.setProperty('volume', DEFAULT_VOLUME)
        if voice_id:
            local_engine.setProperty('voice', voice_id)
        local_engine.say(text_to_speak)
        local_engine.runAndWait() # This blocks execution, hence the need for threading
        local_engine.stop()
    except Exception:
        pass
    finally:
        # Triggering UI cleanup on the main thread after speech concludes
        root.after(0, stop_speaking_ui_update)

def speak_and_animate(text_to_speak):
    """
    Main function to initiate speech and start the visualizer animation.
    """
    global is_speaking
    if is_speaking: return # preventing overlapping speech commands
    
    is_speaking = True
    animate_visualizer() # Starting the animation loop
    
    # Launching the TTS process in a separate thread to keep the UI responsive
    if available_voices_data:
        current_voice_id = available_voices_data[default_voice_index]['id']
        tts_thread = threading.Thread(target=tts_thread_target, args=(text_to_speak, current_voice_id))
        tts_thread.start()
    else:
        # Fallback logic if no voices are detected (simulate duration)
        root.after(len(text_to_speak) * 100, stop_speaking_ui_update)

def speak_current_display():
    """
    Determines what text needs to be spoken based on the current UI state.
    """
    if not current_joke:
        return
    # If punchline is revealed, read the full joke; otherwise, just the setup
    if punchline_label and punchline_label.cget("text"):
        text = f"{current_joke[0]} ... {current_joke[1]}"
    else:
        text = current_joke[0]
    speak_and_animate(text)

# --- CORE GAMEPLAY LOGIC ---

def tell_joke():
    """
    Selects a random joke from the list and updates the UI labels.
    """
    global current_joke
    if not joke_label: return
    
    # Resetting UI elements for the new round
    punchline_label.config(text="")
    guess_entry.delete(0, tk.END)
    feedback_label.config(text="")
    
    # Picking a random joke tuple from the loaded data
    current_joke = random.choice(jokes)
    joke_label.config(text=current_joke[0])

def show_punchline():
    """
    Reveals the punchline label when the user clicks the button.
    """
    if current_joke and punchline_label:
        punchline_label.config(text=current_joke[1])
    elif punchline_label:
        punchline_label.config(text="Start a joke first! 😜")

def check_answer():
    """
    Validates the user's guess against the actual punchline.
    """
    if not current_joke:
        messagebox.showinfo("Wait!", "Press 'New Joke' first!")
        return

    # Normalizing inputs by stripping whitespace and converting to lowercase
    user_guess = guess_entry.get().strip().lower()
    correct_answer = current_joke[1].lower()

    # Basic validation to ensure the user actually typed something
    if not user_guess or len(user_guess) < 2:
        play_sound_effect("huh")
        feedback_label.config(text="Huh? Say that again?", fg=COLORS["accent_gold"])
        return

    # Removing punctuation for a more forgiving comparison (e.g., "side." == "side")
    translator = str.maketrans('', '', string.punctuation)
    clean_guess = user_guess.translate(translator)
    clean_answer = correct_answer.translate(translator)

    # Checking if the key terms match
    if clean_answer in clean_guess or clean_guess in clean_answer:
        play_sound_effect("correct")
        feedback_label.config(text="NAILED IT!! 🎉", fg=COLORS["accent_teal"])
        show_punchline() # Auto-reveal the answer on success
    else:
        play_sound_effect("wrong")
        feedback_label.config(text="NOPE! Try again.", fg=COLORS["accent_pink"])

# --- UI CONSTRUCTION AND NAVIGATION ---

def clear_content_frame():
    """
    Utility function to remove all widgets from the main frame before switching pages.
    """
    for widget in content_frame.winfo_children():
        widget.destroy()

def show_welcome_page():
    """
    Constructs and displays the Landing/Home page widgets.
    """
    clear_content_frame()
    
    # Using a central frame to center content vertically and horizontally
    center_frame = tk.Frame(content_frame, bg=COLORS["bg_main"])
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Displaying the main logo emoji and titles
    tk.Label(center_frame, text="🤖", font=("Segoe UI Emoji", 80), bg=COLORS["bg_main"], fg="white").pack()
    tk.Label(center_frame, text="JOKE ASSISTANT", font=FONTS["huge"], bg=COLORS["bg_main"], fg=COLORS["accent_teal"]).pack(pady=10)
    tk.Label(center_frame, text="Assessment 1 Project", font=FONTS["subtitle"], bg=COLORS["bg_main"], fg="white").pack(pady=(0, 30))

    # Adding navigation buttons with specific styling
    tk.Button(center_frame, text="🚀 LAUNCH APP", font=FONTS["button"], bg=COLORS["accent_teal"], fg=COLORS["text_light"], 
              width=25, bd=0, padx=10, pady=10, command=show_game_page, cursor="hand2").pack(pady=10)
    
    tk.Button(center_frame, text="📜 INSTRUCTIONS", font=FONTS["button"], bg=COLORS["accent_gold"], fg=COLORS["text_dark"], 
              width=25, bd=0, padx=10, pady=10, command=show_rules_page, cursor="hand2").pack(pady=10)

def show_rules_page():
    """
    Constructs and displays the Instructions page.
    """
    clear_content_frame()
    
    rules_frame = tk.Frame(content_frame, bg=COLORS["bg_main"])
    rules_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(rules_frame, text="HOW TO USE", font=FONTS["title"], bg=COLORS["bg_main"], fg="white").pack(pady=20)

    # Defining the instructional text block
    rules_text = (
        "1. Click 'New Joke' to get a setup.\n"
        "2. Type your guess in the box (Optional).\n"
        "3. Click 'Check It' to see if you're right.\n"
        "4. Click 'Show Me' to reveal the punchline.\n"
        "5. Use the Audio controls to read jokes out loud!"
    )
    
    lbl_rules = tk.Label(rules_frame, text=rules_text, font=FONTS["body"], bg=COLORS["bg_dark"], fg="white",
                         justify=tk.LEFT, padx=30, pady=30, relief=tk.FLAT)
    lbl_rules.pack(pady=20)

    # Navigation button to return to the welcome screen
    tk.Button(rules_frame, text="BACK TO MENU", font=FONTS["button"], bg=COLORS["accent_pink"], fg="white", 
              width=20, bd=0, pady=8, command=show_welcome_page, cursor="hand2").pack(pady=20)

def show_game_page():
    """
    Constructs and displays the Main Game page with all interactive elements.
    """
    global joke_label, punchline_label, guess_entry, feedback_label, visualizer_canvas, btn_male, btn_female
    clear_content_frame()
    
    # --- HEADER SECTION ---
    # Creating a header frame for the title and voice controls
    header_frame = tk.Frame(content_frame, bg=COLORS["bg_dark"], pady=15)
    header_frame.pack(fill=tk.X)

    tk.Label(header_frame, text="  JOKE BOT 3000", font=("Segoe UI", 14, "bold"), bg=COLORS["bg_dark"], fg=COLORS["accent_teal"]).pack(side=tk.LEFT, padx=20)

    # Creating a sub-frame for grouping audio buttons
    voice_group = tk.Frame(header_frame, bg=COLORS["bg_dark"])
    voice_group.pack(side=tk.RIGHT, padx=20)

    # Male Voice Toggle
    btn_male = tk.Button(voice_group, text="Male", font=("Segoe UI", 10), width=8, bd=1,
                         bg=COLORS["bg_dark"], fg="white", command=lambda: set_voice(0), cursor="hand2")
    btn_male.pack(side=tk.LEFT, padx=2)

    # Read Aloud Button
    tk.Button(voice_group, text="🔊 READ", font=("Segoe UI", 10, "bold"), width=8, bd=1,
              bg=COLORS["accent_pink"], fg="white", command=speak_current_display, cursor="hand2").pack(side=tk.LEFT, padx=10)

    # Female Voice Toggle
    btn_female = tk.Button(voice_group, text="Female", font=("Segoe UI", 10), width=8, bd=1,
                           bg=COLORS["bg_dark"], fg="white", command=lambda: set_voice(1), cursor="hand2")
    btn_female.pack(side=tk.LEFT, padx=2)
    
    update_voice_buttons() # Setting initial button states

    # --- AUDIO VISUALIZER ---
    # Creating a canvas element to draw the animated bars
    visualizer_canvas = tk.Canvas(content_frame, bg="#111", height=60, highlightthickness=0)
    visualizer_canvas.pack(fill=tk.X, pady=(0, 20))

    # --- MAIN GAME AREA ---
    # Creating a container for the joke setup, input, and punchline
    game_area = tk.Frame(content_frame, bg=COLORS["bg_main"])
    game_area.pack(fill=tk.BOTH, expand=True, padx=50)

    # 1. Joke Setup Card (LabelFrame)
    setup_card = tk.LabelFrame(game_area, text=" THE SETUP ", font=("Segoe UI", 10, "bold"), 
                               bg=COLORS["card_bg"], fg=COLORS["accent_gold"], bd=0, labelanchor="n")
    setup_card.pack(fill=tk.X, pady=10)
    
    joke_label = tk.Label(setup_card, text="Press 'New Joke' to begin!", font=FONTS["body"], 
                          bg=COLORS["card_bg"], fg="white", wraplength=650, pady=20)
    joke_label.pack(fill=tk.X)

    # 2. User Input Section
    input_frame = tk.Frame(game_area, bg=COLORS["bg_main"])
    input_frame.pack(fill=tk.X, pady=15)
    
    tk.Label(input_frame, text="Your Guess:", font=("Segoe UI", 12), bg=COLORS["bg_main"], fg="white").pack(anchor="w")
    guess_entry = tk.Entry(input_frame, font=FONTS["input"], bg="white", fg="#222", relief=tk.FLAT, bd=5)
    guess_entry.pack(fill=tk.X, pady=(5,0))

    # Feedback Label (Correct/Wrong)
    feedback_label = tk.Label(game_area, text="", font=("Segoe UI", 14, "bold"), bg=COLORS["bg_main"], fg="white")
    feedback_label.pack(pady=5)

    # 3. Punchline Card (Initially Hidden)
    punch_card = tk.LabelFrame(game_area, text=" THE PUNCHLINE ", font=("Segoe UI", 10, "bold"), 
                               bg=COLORS["card_bg"], fg=COLORS["accent_pink"], bd=0, labelanchor="n")
    punch_card.pack(fill=tk.X, pady=10)
    
    punchline_label = tk.Label(punch_card, text="...", font=("Segoe UI", 14, "italic"), 
                               bg=COLORS["card_bg"], fg="white", wraplength=650, pady=20)
    punchline_label.pack(fill=tk.X)

    # --- CONTROL BUTTONS ---
    # Creating a grid layout for the main action buttons at the bottom
    ctrl_frame = tk.Frame(game_area, bg=COLORS["bg_main"], pady=30)
    ctrl_frame.pack(fill=tk.X)
    ctrl_frame.columnconfigure(0, weight=1)
    ctrl_frame.columnconfigure(1, weight=1)
    ctrl_frame.columnconfigure(2, weight=1)
    ctrl_frame.columnconfigure(3, weight=1) 

    # 'New Joke' Button
    tk.Button(ctrl_frame, text="New Joke", font=FONTS["button"], bg=COLORS["accent_gold"], fg=COLORS["text_dark"], bd=0, 
              command=tell_joke, width=14, pady=8, cursor="hand2").grid(row=0, column=0, padx=5)
    
    # 'Check Answer' Button
    tk.Button(ctrl_frame, text="Check It", font=FONTS["button"], bg=COLORS["accent_teal"], fg=COLORS["text_light"], bd=0, 
              command=check_answer, width=14, pady=8, cursor="hand2").grid(row=0, column=1, padx=5)
    
    # 'Show Punchline' Button
    tk.Button(ctrl_frame, text="Show Me", font=FONTS["button"], bg=COLORS["accent_pink"], fg=COLORS["text_light"], bd=0, 
              command=show_punchline, width=14, pady=8, cursor="hand2").grid(row=0, column=2, padx=5)

    # 'Exit' Button
    tk.Button(ctrl_frame, text="Exit", font=FONTS["button"], bg="#555", fg="white", bd=0, 
              command=show_welcome_page, width=10, pady=8, cursor="hand2").grid(row=0, column=3, padx=5)


# --- MAIN ENTRY POINT ---
# Initializing the main Tkinter root window
root = tk.Tk()

# Customizing the window icon
# Generating a 16x16 icon filled with our accent color to replace the default feather icon
try:
    icon_img = tk.PhotoImage(width=16, height=16)
    icon_img.put(COLORS["accent_teal"], to=(0, 0, 16, 16))
    root.iconphoto(True, icon_img) 
except Exception:
    pass # If icon generation fails, fall back to default

# Configuring the main window properties
root.title("🤡 Joke Assistant")      # Adding emoji to title as requested
root.geometry("900x850")             # Setting dimensions
root.configure(bg=COLORS["bg_main"]) # Applying background theme

# Creating a main frame to hold all page content
content_frame = tk.Frame(root, bg=COLORS["bg_main"])
content_frame.pack(fill=tk.BOTH, expand=True)

# Loading data and launching the initial view
setup_tts_data()
show_welcome_page() 

# Starting the main event loop to keep the application running
root.mainloop()