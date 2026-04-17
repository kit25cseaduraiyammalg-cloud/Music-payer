import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import vlc
import os
import json
import requests
import sys
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL
from io import BytesIO

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------- GLOBAL ----------------
songs = []
filtered_songs = []
favorites = []
current_index = 0
current_song = ""
is_dragging = False
# ---------------- APP ----------------
app = ctk.CTk()
app.geometry("1100x650")
app.title("Mini Spotify PRO 🎧")

# ---------------- SIDEBAR ----------------
sidebar = ctk.CTkFrame(app, width=240, fg_color="#140a24")
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="🎧 Mini Spotify", font=("Arial", 22, "bold")).pack(pady=25)

playlist_box = tk.Listbox(sidebar, bg="#1E0721", fg="white")
playlist_box.pack(fill="both", expand=True, padx=15, pady=15)

# ---------------- MAIN ----------------
main = ctk.CTkFrame(app, fg_color="#2c0b2c")
main.pack(side="right", fill="both", expand=True)

# TOP
top = ctk.CTkFrame(main)
top.pack(fill="x", pady=5)

search_entry = ctk.CTkEntry(top, placeholder_text="Search songs...", width=350)
search_entry.pack(side="left", padx=20)

# ---------------- BOTTOM (FIXED) ----------------
bottom = ctk.CTkFrame(main, fg_color="#1a0f2a", height=120)
bottom.pack(side="bottom", fill="x")

# ---------------- CENTER ----------------
center = ctk.CTkFrame(main, fg_color="transparent")
center.pack(fill="both", expand=True)

# ---------------- VIDEO ----------------
video_frame = ctk.CTkFrame(center, width=500, height=300)
video_frame.pack(pady=15)

video_frame.update()
video_id = video_frame.winfo_id()

player = vlc.MediaPlayer()

if sys.platform == "win32":
    player.set_hwnd(video_id)
elif sys.platform == "linux":
    player.set_xwindow(video_id)

player.audio_set_volume(70)

# ---------------- IMAGE ----------------
album_label = ctk.CTkLabel(center, text="")
album_label.pack(pady=5)

def set_default_image():
    global album_photo
    img = Image.new("RGB", (200, 200), "#35093B")
    album_photo = ImageTk.PhotoImage(img)
    album_label.configure(image=album_photo)
    album_label.image = album_photo

set_default_image()

# ---------------- LABELS ----------------
song_label = ctk.CTkLabel(center, text="No song playing", font=("Arial", 24, "bold"))
song_label.pack()

status_label = ctk.CTkLabel(center, text="🎶 Enjoy your music", text_color="gray")
status_label.pack()

# ---------------- SEEK ----------------
def seek_to_position(event):
    try:
        val = progress.get()
        length = player.get_length()
        new_time = (val / 100) * length
        player.set_time(int(new_time))
    except:
        pass

def on_slider_press(event):
    global is_dragging
    is_dragging = True

def on_slider_release(event):
    global is_dragging
    is_dragging = False

progress = ctk.CTkSlider(center, from_=0, to=100)
progress.pack(fill="x", padx=100, pady=10)

# 🔥 AFTER CREATE dhaan bind
progress.bind("<ButtonRelease-1>", seek_to_position)
progress.bind("<Button-1>", on_slider_press)
progress.bind("<ButtonRelease-1>", on_slider_release)

progress = ctk.CTkSlider(center, from_=0, to=100)
progress.pack(fill="x", padx=100, pady=10)

# ---------------- FUNCTIONS ----------------
def update_playlist():
    playlist_box.delete(0, "end")
    for s in filtered_songs:
        if isinstance(s, dict):
            playlist_box.insert("end", s["title"])
        else:
            playlist_box.insert("end", os.path.basename(s))

def load_songs():
    global songs, filtered_songs
    songs = list(filedialog.askopenfilenames(filetypes=[("MP3", "*.mp3")]))
    filtered_songs = songs.copy()
    update_playlist()

def load_thumbnail(url):
    global album_photo
    try:
        img_data = requests.get(url).content
        img = Image.open(BytesIO(img_data)).resize((200, 200))
        album_photo = ImageTk.PhotoImage(img)
        album_label.configure(image=album_photo)
        album_label.image = album_photo
    except:
        set_default_image()

def play_song():
    global current_song
    if not filtered_songs:
        return

    item = filtered_songs[current_index]

    if isinstance(item, dict):
        player.stop()
        player.set_media(vlc.Media(item["url"]))
        player.play()

        current_song = item["url"]
        song_label.configure(text=item["title"])
        load_thumbnail(item["thumb"])
    else:
        player.stop()
        player.set_media(vlc.Media(item))
        player.play()

        current_song = item
        song_label.configure(text=os.path.basename(item))
        set_default_image()

def play_selected(event):
    global current_index
    if playlist_box.curselection():
        current_index = playlist_box.curselection()[0]
        play_song()

playlist_box.bind("<<ListboxSelect>>", play_selected)

def search_movie_songs(query):
    global filtered_songs
    filtered_songs = []

    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(f"ytsearch10:{query} songs", download=False)

        for entry in info['entries']:
            filtered_songs.append({
                "url": entry['url'],
                "thumb": entry.get("thumbnail"),
                "title": entry['title']
            })

    update_playlist()

ctk.CTkButton(top, text="🌐 Play",
              command=lambda: search_movie_songs(search_entry.get())
).pack(side="left")

# ---------------- CONTROLS ----------------
btn_frame = ctk.CTkFrame(bottom, fg_color="transparent")
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="⏮", command=lambda: change_song(-1)).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="▶", command=play_song).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="⏸", command=lambda: player.pause()).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="⏭", command=lambda: change_song(1)).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="❤️", command=lambda: favorites.append(current_song)).pack(side="left", padx=10)

def change_song(step):
    global current_index
    if filtered_songs:
        current_index = (current_index + step) % len(filtered_songs)
        play_song()

# ---------------- VOLUME ----------------
volume = ctk.CTkSlider(bottom, from_=0, to=100,
                       command=lambda v: player.audio_set_volume(int(v)))
volume.set(70)
volume.pack()

# ---------------- PROGRESS ----------------
def update_progress():
    global is_dragging

    try:
        if player.is_playing():
            current = player.get_time()
            total = player.get_length()

            if total > 0:
                percent = (current / total) * 100

                # 🔥 IMPORTANT
                if not is_dragging:
                    progress.set(percent)
    except:
        pass

    app.after(500, update_progress)

# ---------------- SIDEBAR BUTTONS ----------------
ctk.CTkButton(sidebar, text="📂 Load Songs", command=load_songs).pack(pady=5, padx=15, fill="x")

# INIT
update_progress()
app.mainloop()
