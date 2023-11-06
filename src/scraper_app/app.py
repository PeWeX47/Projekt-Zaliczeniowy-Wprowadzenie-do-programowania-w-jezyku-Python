import tkinter as tk
import customtkinter as ctk
import sqlite3
from tekstowo_scraper import song_scraper
import threading


class TekstowoScraperApp:
    def __init__(self, root):
        # Inicjalizuje interfejs aplikacji oraz niezbędne połączenia z bazą danych.
        self.root = root
        self.root.title("tekstowo.pl lyrics scraper")
        self.root.resizable(False, False)

        self.conn = sqlite3.connect("src/scraper_app/music_artists.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS artists (id INTEGER PRIMARY KEY, artist_name TEXT, url TEXT)"""
        )
        self.top_frame = ctk.CTkFrame(root)
        self.top_frame.pack(side=tk.TOP, pady=10)

        self.left_frame = ctk.CTkFrame(root)
        self.left_frame.pack(side=tk.LEFT, padx=10)
        self.right_frame = ctk.CTkFrame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=10)

        self.search_label = ctk.CTkLabel(self.top_frame, text="Search for an artist:")
        self.search_label.pack()

        self.search_entry = ctk.CTkEntry(self.top_frame)
        self.search_entry.pack(pady=5)

        self.search_button = ctk.CTkButton(
            self.top_frame, text="Search", command=self.search_artists
        )
        self.search_button.pack(pady=5)

        self.scrap_button = ctk.CTkButton(
            self.top_frame, text="Scrap", command=self.scrap
        )
        self.scrap_button.pack(pady=5)

        self.results_label = ctk.CTkLabel(self.left_frame, text="Search results:")
        self.results_label.pack()

        self.results_listbox = tk.Listbox(
            self.left_frame, width=40, background="#242424", foreground="white"
        )
        self.results_listbox.pack()

        self.selected_label = ctk.CTkLabel(self.right_frame, text="Selected artists:")
        self.selected_label.pack()

        self.selected_listbox = tk.Listbox(
            self.right_frame, width=40, background="#242424", foreground="white"
        )
        self.selected_listbox.pack()

        self.add_button = ctk.CTkButton(
            self.left_frame, text="Add", command=self.add_artist
        )
        self.add_button.pack(pady=5)

        self.remove_button = ctk.CTkButton(
            self.right_frame, text="Remove", command=self.remove_artist
        )
        self.remove_button.pack(pady=5)

    def search_artists(self):
        """
        Pobiera i wyświetla nazwy artystów z bazy danych na podstawie wprowadzonego terminu wyszukiwania.
        """
        search_term = self.search_entry.get()
        self.results_listbox.delete(0, tk.END)

        self.cursor.execute(
            "SELECT artist_name, id FROM artists WHERE artist_name LIKE ?",
            (search_term + "%",),
        )
        results = self.cursor.fetchall()

        for row in results:
            self.results_listbox.insert(tk.END, row[0] + " ID: " + str(row[1]))

    def add_artist(self):
        """
        Dodaje wybranego artystę z wyników wyszukiwania do listy wybranych artystów.
        """
        selected_artist = self.results_listbox.get(tk.ACTIVE)
        if selected_artist not in self.selected_listbox.get(0, tk.END):
            self.selected_listbox.insert(tk.END, selected_artist)

    def remove_artist(self):
        """
        Usuwa wybranego artystę z listy wybranych artystów.
        """
        selected_index = self.selected_listbox.curselection()
        if selected_index:
            self.selected_listbox.delete(selected_index[0])

    def run(self):
        """
        Rozpoczyna główną pętlę aplikacji.
        """
        self.root.mainloop()

    def scrap(self):
        """
        Rozpoczyna proces przeszukiwania tekstów piosenek dla wybranych artystów.
        """
        urls = []
        for artist in self.selected_listbox.get(0, tk.END):
            artist_id = int(artist.split()[-1])
            self.cursor.execute(
                "SELECT artist_name, url FROM artists WHERE id = ?", (artist_id,)
            )
            result = self.cursor.fetchone()
            urls.append(result)

        def perform_scraping():
            song_scraper(urls)

        scraping_thread = threading.Thread(target=perform_scraping)
        scraping_thread.start()


if __name__ == "__main__":
    root = ctk.CTk()
    app = TekstowoScraperApp(root)
    app.run()
