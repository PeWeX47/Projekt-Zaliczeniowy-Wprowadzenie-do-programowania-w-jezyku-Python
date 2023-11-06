# Wprowadzenie do Programowania w Pythonie - Projekt

## Stworzenie własnego modelu do generowania tekstów piosenek opartego na GPT-2

## Wprowadzenie

### Cel projektu

Celem naszego projektu było wykorzystanie modelu GPT-2 w celu generowania tekstów piosenek. Źródłem danych tekstowych, wykorzystanych do trenowania modelu była strona internetowa "*tekstowo.pl*", która zawiera obszerną kolekcję tekstów piosenek różnych wykonawców. Przeanalizowaliśmy tę stronę i zdecydowaliśmy się na wykorzystanie technik data scrapingu do pozyskania potrzebnych danych.

### Realizacja

Realizacja projektu podzielona została na dwie części:

- Stworzenie aplikacji okienkowej pozwalającej na zescrapowanie tekstów piosenek dowolnych artystów

- Dotrenowanie modelu GPT-2 w środowisku Google Colab oraz stworzenie interfejsu webowego umożliwiającego użytkownikowi łatwiejsze wykorzystanie modelu

### Wykorzystane narzędzia

W projekcie wykorzystane zostały następujące narzędzia:

- Środowisko Google Colab wykorzystane do dostrojenia modelu GPT-2
- Python w wersji 3.9.10
- Biblioteki języka dostępne w repozytoriach pakietów Pythona, ich listing wraz z wersjami znajduje się w pliku '*requirements.txt*'
- Python Virtual Environment pozwalający na separację zależności pakietów pomiędzy różnymi projektami
- System kontroli wersji Git

Instalację wymaganych bibliotek Pythona wykonać można korzystając z polecenia:

```
pip install -r requirements.txt
```

## Aplikacja okienkowa "*tekstowo.pl lyrics scraper*"

Aplikacja korzysta z interfejsu graficznego *tkinter* oraz jego rozszerzenia *customtkinter* oraz współpracuje z bazą danych *SQLite*. Umożliwia użytkownikom wyszukiwanie artystów, wybieranie konkretnych wykonawców oraz zbieranie tekstów piosenek ze strony tekstowo.pl. 

### Kod źródłowy

#### Pozyskanie nazw wszystkich wykonawców dostępnych na *tekstowo.pl* oraz odnośników prowadzących do ich profili na stronie

``` python

# Ramka danych slużąca do przechowywania informacji o zescrapowanych danych
df = pd.DataFrame(
    
    {
        "Artysta":[],
        "Link":[]
    }
)

# Generowanie wszystkich liter alfabetu
alfabet = [chr(i) for i in range(65, 91)]

# Podstawowy adres strony tekstowo.pl
part_url = "https://www.tekstowo.pl"

# Petla iterowana po każdej literze alfabetu
for letter in alfabet:
    # Tworzenie linku adresu strony zaczynającej się na kolejną iterowaną litere w alfabecie
    basic_url = f"https://www.tekstowo.pl/artysci_na,{letter},strona,1.html"
    page = requests.get(basic_url)

    soup = BeautifulSoup(page.text, "lxml")
    try:
        # Zebranie informacji dotyczącej ilości stron artystów zaczynających się na daną litere
        max_num_page = soup.find_all("a", class_="page-link")[-2].text
        max_num_page = int(max_num_page)
    except:
        max_num_page = 1

    # Petla iterująca po każdej stronie artystów zaczynających sie na konkretną litere
    for num_page in range(1, max_num_page + 1):
        container = soup.find("div", class_="content")
        boxes = container.find_all("div", class_="box-przeboje")
        
        # Petla iterująca po każdym artyście na kolejnych stronach
        for box in boxes:
            artist = box.find("a", class_="title").text
            elements = artist.split()
            artist = ' '.join(elements[:-2])
            
            url_artist = box.find("a", class_="title").get("href")
            path = part_url+url_artist
            new_path = path.replace(".html",",strona1.html")

            # Dodanie informacji o artyście i adresie URL do jego utworó do ramki danych
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "Artysta":[artist],
                            "Link":[new_path]
                        }
                    ),
                ],
                ignore_index = True,
            )

        # Pobranie adresu URL kolejnej strony z artystami zaczynającymi się na kolejną litere w alfabecie
        next_number_page = num_page + 1
        next_page = f"https://www.tekstowo.pl/artysci_na,{letter},strona,{next_number_page}.html"
        page = requests.get(next_page)
        soup = BeautifulSoup(page.text, "lxml")

```

#### Moduł wykorzystany do scrapowania tekstów piosenek

``` python

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np


def song_scraper(artist_data: list) -> None:
    """
    Scrapuje teksty piosenek określoncyh artystów z 'tekstowo.pl'.

    Args:
        artist_data (list): Lista zawierająca krotki with z nazwami artystów oraz odnośnikami do ich profili na 'tekstowo.pl'.

    Zescrapowane dane zapisywane są do pliku 'scraper-result.csv'.
    """
    dfs = []
    df_text = pd.DataFrame(
        data={"Author": [], "Title": [], "Polish": [], "English": []}
    )

    base_url = "https://www.tekstowo.pl"

    for artist_name, artist_url in artist_data:
        artist_page = requests.get(artist_url)
        soup = BeautifulSoup(artist_page.text, "lxml")

        try:
            max_num_page = soup.find_all("a", class_="page-link")[-2].text
            max_num_page = int(max_num_page)

        except:
            max_num_page = 1

        for num_page in range(1, max_num_page + 1):
            boxes = soup.find_all("div", class_="flex-group")
            songs_urls = {"Url": []}

            for box in boxes:
                try:
                    url = box.find("a", class_="title").get("href")
                    song_url = base_url + url

                    songs_urls["Url"].append(song_url)
                except:
                    pass

            df = pd.DataFrame(songs_urls)
            dfs.append(df)

            next_number_page = num_page + 1
            splitted = artist_url.split("strona")
            before_strona = splitted[0]

            next_page = f"{before_strona}strona{next_number_page}.html"

            page = requests.get(next_page)
            soup = BeautifulSoup(page.text, "lxml")

    df_songs = pd.concat(dfs, ignore_index=True)

    for _, row in df_songs.iterrows():
        try:
            song_page = requests.get(row[0])

            soup = BeautifulSoup(song_page.text, "lxml")

            original = soup.find_all("div", class_="inner-text")[0].text
            translated = soup.find_all("div", class_="inner-text")[1].text
            translated = np.nan if translated == "" else translated
            song_title = (
                re.findall(r",[^,]+,([^\.]+)\.", row[0])[0]
                .replace("_", " ")
                .strip()
                .title()
            )

            if re.search(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", original):
                df_text = pd.concat(
                    [
                        df_text,
                        pd.DataFrame(
                            {
                                "Author": artist_name,
                                "Title": song_title,
                                "Polish": [original],
                                "English": [translated],
                            }
                        ),
                    ],
                    ignore_index=True,
                )

            else:
                df_text = pd.concat(
                    [
                        df_text,
                        pd.DataFrame(
                            {
                                "Author": artist_name,
                                "Title": song_title,
                                "Polish": [translated],
                                "English": [original],
                            }
                        ),
                    ],
                    ignore_index=True,
                )
        except:
            print(f"Unable to download lyrics from {row[0]}")

    df_text.to_csv("src/scraper-result.csv", index=None)

```

#### Interfejs graficzny umożliwający wybranie artstów oraz pozyskanie tekstów piosenek

``` python

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

        self.conn = sqlite3.connect("src/music_artists.db")
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
```

## Dostrojenie modelu GPT-2 w celu generowania tekstów piosenek

### Kod źrodłowy z notatnika Google Colab

#### Import potrzebnych bibliotek

``` python
!pip install -q gpt-2-simple
import gpt_2_simple as gpt2
from datetime import datetime
from google.colab import files
import pandas as pd
import re
```

#### Pobranie **"surowego"** modelu GPT2 124M

``` python
gpt2.download_gpt2(model_name="124M")
```

#### Import wcześniej zescrapowanych danych z pliku .csv, oraz usunięcie rekordów zawierających puste wartości w kolumnie **English** (kolumna która zostanie wykorzystana do operacji dostrojenia modelu)

``` python
dataset = pd.read_csv("/content/Merged.csv", index_col = None)
dataset = dataset[dataset['English'].notna()]
```

#### Oczyszczenie zbioru danych ze znaków, które uznaliśmy za niepotrzebne w trenowaniu modelu

``` python
# do zbioru usuwanych znaków należą:
# -   *
# -   ^
# -   /

def clearing(x, column):

  for index, row in x.iterrows():
    row[column] = re.sub(r'[*^=/]', '', row[column])

  return x

clear_data = clearing(dataset, "English")
```

#### Zapisanie oczyszczonych danych do pliku o nazwie songs z rozszerzeniem .txt, dane z tego pliku bezpośrednio posłużą do treningu modelu

``` python
filename = "songs.txt"

with open(filename, 'w') as file:
    clear_data['English'].to_csv(file, header=False, index=False)
```

#### Połączenie naszego Google Drive z środowiskiem wykonawczym w Google Colab

``` python
gpt2.mount_gdrive()
```

#### Inicjalizacja środowiska Tensorflow, oraz dobór parametrów wykorzystywanych do operacji Fine Tune

- dataset - plik .txt, z którego dane są wykorzystywane do trenowania modelu GPT2
- steps - liczba epok, które bedą służyć do treningu
- restore_from - wartość "fresh" służy do trenowania modelu na nowo dla naszych danych, natomiast "latest" wykorzystujemy do wczytania modelu z ostatniego checkpoint'a
- run_name - nazwa podfolderu wewnątrz folderu checkpoint, gdzie będzie zapisany model
- print_every - liczba określająca co ile epok zostaniemy informowani o postępie uczenia
- sample_every - liczba określająca co ile epok model zwróci nam przykładowe wygenerowane dane
- save_every - liczba epok, co ile model zostaje zapisany do checkpoint'a

Po zakończeniu Fine Tune zapisujemy model w Google Drive

``` python
sess = gpt2.start_tf_sess()

gpt2.finetune(sess,
              dataset=filename,
              model_name='124M',
              steps=8500,
              restore_from='fresh',
              run_name='run1',
              print_every=500,
              sample_every=1000,
              save_every=5000,
              )
gpt2.copy_checkpoint_to_gdrive(run_name='run1')
```

#### Ten zestaw poleceń należy wykonać, jeśli chcemy użyć już gotowego modelu do zadania generowania piosenek, należy pamiętać o poprzednim **zainstalowaniu** odpowiednich bibliotek

``` python
gpt2.mount_gdrive()
gpt2.copy_checkpoint_from_gdrive(run_name='run1')
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, run_name='run1')
```

#### Określenie początkowych wyrazów, od których ma zaczynać się piosenka

``` python
prefix = "Love is"
```

#### Parametry wykorzystane podczas generowania tekstu

- length - liczba tokenów z których ma składać się jeden rekord
- temperature - entropia wyrazów wykorzystanych w nowym utworze (im większa wartość tym mniej standardowych słów będzie się pojawiać)
- prefix - dane wejściowe
- nsamples - liczba zwracanych rekordów danych
- return_as_list - parametr pozwalający na przekazanie wygenerowanego teksu do zmiennej jako listy

``` python
gpt2.generate(sess,
              length=100,
              temperature=0.7,
              prefix=prefix,
              nsamples=5,
            # return_as_list = True
              )
```

#### Przykładowy tekst wygenerowany przez model

``` output
Love is the past, where we can be in the future

[Bridge]
We've been friends for so long
And I'm not even sure I'm okay
I'm a fool
I don't know what it is
But I guess I don't mind

[Outro]
We'll fly out to London
Where we can be in the future
And we'll see
And we'll see
And we'll see
And we'll see
And we'll see
====================
Love is in your heart
And you hear it in your heart,
And I hear it in your heart,

And I write my love down
And I can read your heart-wrenching face on the cover of a magazine
And I can finally see that your eyes are now filled with tears,
...
The freeway is pulsing
I pass the finish line when it starts to fade
I pass the finish line in the car now with
```

## Interfejs webowy zintegrowany z modelem

W celu umożliwienia użytkownikowi łatwego wykorzystania modelu, stworzyliśmy aplikację webową korzystając z biblioteki *Gradio*. Aplikacja hostowana jest poprzez serwis huggingface pod tym [adresem](https://huggingface.co/spaces/PeWeX47/GPT-2-Lyrics-Generator).

### Kod źrodłowy

``` python

import gradio as gr
import gpt_2_simple as gpt2

def pipeline(prompt: str, length: int, temperature: float, top_k: int, top_p: float):

    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess)

    lyrics = gpt2.generate(
        sess,
        return_as_list=True,
        length=length,
        prefix=prompt,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
    )[0]
    return lyrics


length_slider = gr.Slider(
    50, 1000, value = 500, label = "Lyrics length"
)

temperature_slider = gr.Slider(
    0.6, 1.0, value = 0.7, label = "Temperature"
)

top_k_slider = gr.Slider(0, 40, value=0, label="Top k")
top_p_slider = gr.Slider(0.0, 1.0, value=0.9, label="Top p")

app = gr.Interface(
    fn=pipeline,
    inputs=["text", length_slider, temperature_slider, top_k_slider, top_p_slider],
    outputs="text",
    allow_flagging = "manual"
)

if __name__ == "__main__":
    app.launch(debug=True)
```
