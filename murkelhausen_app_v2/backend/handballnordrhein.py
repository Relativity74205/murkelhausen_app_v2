from dataclasses import dataclass
from datetime import datetime, date

import requests
from babel.dates import format_date
from bs4 import BeautifulSoup

TEAM = "1993128"


@dataclass
class HandballGame:
    game_date: date
    game_date_formatted: str
    time: str
    time_original: str | None
    home_team: str
    away_team: str
    location: str
    result: str
    link_to_spielbericht: str | None
    spielbericht_genehmigt: bool | None


def parse_games(html_content: str) -> list[HandballGame]:
    soup = BeautifulSoup(html_content, "html.parser")
    content2_div = soup.find("div", {"id": "content-row2"})
    body = content2_div.find("table", {"class": "result-set"})
    next_row = body.findNext("tr")

    games = []
    while (next_row := next_row.findNext("tr")) is not None:
        parts = next_row.find_all("td")
        game_date = parts[1].text.strip()
        time = parts[2].text.strip().split(" ")[0].strip()
        if "alt" in parts[2].attrs:
            time_original = parts[2]["alt"]
        else:
            time_original = None
        halle = parts[3].text.strip()
        home_team = parts[5].text.strip()
        away_team = parts[6].text.strip()
        result = parts[7].text.strip()
        if parts[7].find("a") is not None:
            link_to_spielbericht = parts[7].find("a")["href"]
            spielbericht_genehmigt = parts[9].find("img") is not None
        else:
            link_to_spielbericht = None
            spielbericht_genehmigt = None

        game_date = datetime.strptime(game_date, "%d.%m.%Y").date()

        game = HandballGame(
            game_date=game_date,
            game_date_formatted=format_date(
                game_date, format="EEE, d.M.yyyy", locale="de_DE"
            ),
            time=time,
            time_original=time_original,
            home_team=home_team,
            away_team=away_team,
            location=halle,
            result=result,
            link_to_spielbericht=link_to_spielbericht,
            spielbericht_genehmigt=spielbericht_genehmigt,
        )
        games.append(game)

    return games


def get_djk_saarn_d_jugend() -> list[HandballGame]:
    r = requests.get(
        "https://hnr-handball.liga.nu/cgi-bin/WebObjects/nuLigaHBDE.woa/wa/teamPortrait",
        params={"teamtable": TEAM},
    )

    return parse_games(r.text)