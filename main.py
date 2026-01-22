from flask import Flask, render_template
import requests
import json
from pathlib import Path

BASE_PATH = Path(__name__).absolute().parent

app = Flask(__name__)


def get_playerdata(stats_dir: str | None = None) -> list[dict]:
    # read files
    if not stats_dir:
        stats_dir = BASE_PATH / "stats"

    result = []
    print(stats_dir, flush=True)
    for stats_file in Path(stats_dir).glob("*.json"):
        # the name of the file contains the uuid
        player_uuid = stats_file.name
        print(player_uuid, flush=True)
        player_name = get_player_name_from_uuid(player_uuid.rstrip(".json"))
        with stats_file.open() as f:
            player_data = json.loads(f.read())
        play_time_ticks = (
            player_data.get("stats", {})
            .get("minecraft:custom", {})
            .get("minecraft:play_time")
        )
        play_time_decimal = play_time_ticks_to_human_time(play_time_ticks)
        play_time_decimal_split = play_time_decimal.split(".")
        play_time_hours, play_time_minutes = (
            play_time_decimal_split[0],
            play_time_decimal_split[1],
        )
        play_time_minutes = int(play_time_minutes) * 0.60
        play_time_minutes = f"{play_time_minutes:.0f}"
        result.append(
            {
                "name": player_name,
                "playtime_ticks": play_time_ticks,
                "playtime_decimal": play_time_decimal,
                "playtime_hours": play_time_hours,
                "playtime_minutes": play_time_minutes,
            }
        )
    return result


def sort_player_list(player_list: list[dict]) -> list[dict]:
    return sorted(player_list, reverse=True, key=lambda x: x.get("playtime_ticks", -1))


def play_time_ticks_to_human_time(playtime_ticks: int) -> str:
    return f"{(playtime_ticks / 20 / 3600):.2f}"


def get_player_name_from_uuid(player_uuid: str) -> str:
    response = requests.get(
        f"https://api.minecraftservices.com/minecraft/profile/lookup/{player_uuid}"
    )
    json_response = json.loads(response.text)
    player_name = json_response.get("name")
    return player_name


@app.route("/")
def root_route():
    persons = get_playerdata()
    persons = sort_player_list(persons)
    return render_template("leaderboard.html", persons=persons)
