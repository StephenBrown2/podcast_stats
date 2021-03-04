import click
import pendulum
from rich.color import Color
from rich.console import Console
from rich.style import Style
from rich.table import Table

from podcast_stats import get_parsed_feed, weekday_distribution


@click.command()
@click.option("--feed-url", prompt=True, multiple=True)
def run(feed_url):
    """
    Pull a podcast rss feed from a given url and print a table
    with all episodes sorted by time between episodes

    :raises ValueError:
        If the feed does not have all of the required data
    """
    console = Console(width=150)
    # get the feed and parse it
    parsed_feed = []
    for url in feed_url:
        parsed_feed.extend(get_parsed_feed(url))

    # Draw weekday distribution
    heatmap = Table(title="Weekday Heatmap")
    heat = {
        0: Style(bgcolor=Color.from_rgb(red=153, green=0, blue=13)),
        1: Style(bgcolor=Color.from_rgb(red=203, green=24, blue=29)),
        2: Style(bgcolor=Color.from_rgb(red=239, green=59, blue=44)),
        3: Style(bgcolor=Color.from_rgb(red=251, green=106, blue=74), color="black"),
        4: Style(bgcolor=Color.from_rgb(red=252, green=146, blue=114), color="black"),
        5: Style(bgcolor=Color.from_rgb(red=252, green=187, blue=161), color="black"),
        6: Style(bgcolor=Color.from_rgb(red=254, green=229, blue=217), color="black"),
    }

    count = weekday_distribution(parsed_feed)
    result = {}
    for i, item in enumerate(count.most_common()):
        result[item[0]] = {"value": str(item[1]), "style": heat[i]}

    row = []
    for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        day = result.get(d, {"value": "0", "style": ""})
        heatmap.add_column(d, style=day["style"], justify="center")
        row.append(day["value"])

    heatmap.add_row(*row)

    console.print(heatmap)

    table = Table(
        "Podcast",
        "Title",
        "Date published",
        "Days since last",
        title="Episodes",
    )
    for episode in sorted(
        parsed_feed, key=lambda x: x["published_datetime"], reverse=True
    ):
        table.add_row(
            episode["podcast"],
            " ".join(episode["title"].split()),
            episode["published_datetime"]
            .in_timezone(pendulum.local_timezone())
            .to_day_datetime_string(),
            str(episode["time_since_last"].days),
        )

    console.print(table)
