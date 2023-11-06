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

    df_text.to_csv("src/scraper_app/scraper-result.csv", index=None)
