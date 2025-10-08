import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import pygame
import os
import random
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import pygame.event

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor MP3 RO5K4")
        self.root.geometry("540x500")
        self.root.configure(bg="#1c1c1c")

        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.shuffle = False
        self.song_length = 0

        self.info_label = tk.Label(root, text="\U0001F3B5 No hay pista cargada", font=("Arial", 12, "bold"),
                                   fg="white", bg="#1c1c1c")
        self.info_label.pack(pady=5)

        control_frame = tk.Frame(root, bg="#1c1c1c")
        control_frame.pack(pady=10)

        btn_style = {"bg": "#2a2a2a", "fg": "white", "activebackground": "#444", "activeforeground": "white"}

        tk.Button(control_frame, text="⏮️", command=self.prev_song, **btn_style).grid(row=0, column=0)
        self.play_button = tk.Button(control_frame, text="▶️", command=self.play_pause, **btn_style)
        self.play_button.grid(row=0, column=1)
        tk.Button(control_frame, text="⏭️", command=self.next_song, **btn_style).grid(row=0, column=2)
        self.shuffle_button = tk.Button(control_frame, text="🔀", command=self.toggle_shuffle, **btn_style)
        self.shuffle_button.grid(row=0, column=3)
        tk.Button(control_frame, text="🗑️", command=self.delete_selected, **btn_style).grid(row=0, column=4)

        self.canvas_progress = tk.Canvas(root, height=20, bg="#2e2e2e", highlightthickness=0)
        self.canvas_progress.pack(fill="x", padx=20, pady=(5, 0))
        self.canvas_progress.bind("<Button-1>", self.seek_canvas)

        self.time_label = tk.Label(root, text="00:00 / 00:00", fg="white", bg="#1c1c1c")
        self.time_label.pack()

        self.volume = tk.DoubleVar(value=0.5)
        pygame.mixer.music.set_volume(self.volume.get())

        volume_frame = tk.Frame(root, bg="#1c1c1c")
        volume_frame.pack(pady=5)
        tk.Label(volume_frame, text="🔉 Volumen", fg="white", bg="#1c1c1c").pack(side="left")
        tk.Scale(volume_frame, from_=0, to=1, resolution=0.01, orient="horizontal",
                 variable=self.volume, command=self.change_volume,
                 troughcolor="#444", bg="#2a2a2a", fg="white", highlightthickness=0).pack(side="left")

        self.song_listbox = tk.Listbox(root, bg="#2a2a2a", fg="white", selectbackground="#555",
                                       selectforeground="white", activestyle="none", height=10,
                                       borderwidth=0, highlightthickness=0)
        self.song_listbox.pack(fill="both", expand=True, padx=20, pady=10)
        self.song_listbox.bind("<<ListboxSelect>>", self.play_selected)

        root.drop_target_register(DND_FILES)
        root.dnd_bind('<<Drop>>', self.drop_songs)

        root.bind('<space>', lambda e: self.play_pause())
        root.bind('<Right>', lambda e: self.next_song())
        root.bind('<Left>', lambda e: self.prev_song())

        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.root.after(100, self.check_music_end)
        self.update_time()

    def add_songs(self):
        files = filedialog.askopenfilenames(filetypes=[("Archivos MP3", "*.mp3")])
        for file in files:
            if file.endswith(".mp3") and file not in self.playlist:
                self.playlist.append(file)
                self.song_listbox.insert("end", os.path.basename(file))

    def drop_songs(self, event):
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.endswith(".mp3") and file not in self.playlist:
                self.playlist.append(file)
                self.song_listbox.insert("end", os.path.basename(file))

    def delete_selected(self):
        selected = self.song_listbox.curselection()
        if selected:
            index = selected[0]
            self.playlist.pop(index)
            self.song_listbox.delete(index)
            if index == self.current_index:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.play_button.config(text="▶️")
            if index < self.current_index:
                self.current_index -= 1

    def play_selected(self, event=None):
        selection = self.song_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.play_song()

    def play_song(self):
        if not self.playlist:
            return
        try:
            song_path = self.playlist[self.current_index]
            pygame.mixer.music.load(song_path)
            audio = MP3(song_path)
            self.song_length = int(audio.info.length)

            try:
                info = EasyID3(song_path)
                title = info.get("title", [os.path.basename(song_path)])[0]
                artist = info.get("artist", [""])[0]
                self.info_label.config(text=f"\U0001F3B5 {title} - {artist}")
            except Exception:
                self.info_label.config(text=f"\U0001F3B5 {os.path.basename(song_path)}")

            pygame.mixer.music.play()
            self.is_playing = True
            self.play_button.config(text="⏸️")

            self.song_listbox.select_clear(0, "end")
            for i in range(len(self.playlist)):
                self.song_listbox.itemconfig(i, {'bg': "#2a2a2a"})
            self.song_listbox.select_set(self.current_index)
            self.song_listbox.itemconfig(self.current_index, {'bg': "#505050"})
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir la canción:\n{str(e)}")

    def play_pause(self):
        if not self.playlist:
            return
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.config(text="▶️")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.play_button.config(text="⏸️")

    def next_song(self):
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_song()

    def prev_song(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_song()

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.shuffle_button.config(bg="#3c6", fg="black")
        else:
            self.shuffle_button.config(bg="#2a2a2a", fg="white")

    def change_volume(self, _=None):
        pygame.mixer.music.set_volume(self.volume.get())

    def seek_canvas(self, event):
        if self.song_length > 0:
            width = self.canvas_progress.winfo_width()
            percentage = event.x / width
            pos = int(percentage * self.song_length)
            pygame.mixer.music.play(start=pos)
            self.is_playing = True
            self.play_button.config(text="⏸️")

    def draw_progress_bar(self, percentage):
        self.canvas_progress.delete("all")
        width = self.canvas_progress.winfo_width()
        fill_width = int(width * (percentage / 100))
        r = int(255 * (percentage / 100))
        g = int(255 * (1 - abs(percentage - 50) / 50))
        b = int(255 * (1 - percentage / 100))
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.canvas_progress.create_rectangle(0, 0, fill_width, 20, fill=color, width=0)

    def update_time(self):
        if self.is_playing and self.song_length > 0:
            pos = pygame.mixer.music.get_pos() // 1000
            if pos >= self.song_length:
                self.next_song()
                return
            percent = (pos / self.song_length) * 100
            self.draw_progress_bar(percent)
            time_text = f"{self.format_time(pos)} / {self.format_time(self.song_length)}"
            self.time_label.config(text=time_text)
        self.root.after(1000, self.update_time)

    def check_music_end(self):
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                self.next_song()
        self.root.after(100, self.check_music_end)

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MP3Player(root)
    root.mainloop()