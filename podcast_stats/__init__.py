"""podcast_stats - A script to pull the rss feed for a podcast and run some analysis on it."""
from collections import Counter

import feedparser
from pendulum import constants, duration, from_format, now, timezone

__version__ = "0.1.0"
__author__ = "Niklas Meinzer <github@niklas-meinzer.de>"
__all__ = []


def get_parsed_feed(feed_url):
    """
    Pull a podcast rss feed from a given url and calculate
    time between episodes.

    :raises ValueError:
        If the feed does not have all of the required data
    """

    parsed_feed = feedparser.parse(feed_url)
    if parsed_feed is None:
        raise ValueError("No feed could be found")
    last_datetime = None

    episodes = []

    for index, entry in enumerate(reversed(parsed_feed["entries"])):
        try:
            published_datetime = from_format(entry.published, constants.RSS)
        except ValueError:
            naive, _, tz_abbr = entry.published.rpartition(" ")
            tz_abbr = tz_abbr.replace("PST", "US/Pacific").replace("PDT", "US/Pacific")
            published_datetime = from_format(
                naive,
                constants.RSS.removesuffix(" ZZ"),
                tz=timezone(tz_abbr),
            )

        if index == 0:
            # use an empty Duration for the first episode
            time_since_last = duration()
        else:
            time_since_last = published_datetime - last_datetime

        episodes.append(
            {
                "podcast": parsed_feed.feed.title,
                "title": entry.title,
                "published_datetime": published_datetime,
                "time_since_last": time_since_last,
                "published": True,
            }
        )
        last_datetime = published_datetime

    average = sum([e["time_since_last"].days for e in episodes]) / len(
        list(filter(lambda e: e["time_since_last"].days > 0, episodes))
    )
    # Add a dummy episode to measure the time from the last episode until the next
    episodes.append(
        {
            "podcast": parsed_feed.feed.title,
            "title": "[Next unpublished episode]",
            "published_datetime": last_datetime + duration(days=average),
            "time_since_last": now() - (last_datetime + duration(days=average)),
            "published": False,
        }
    )

    return episodes


def weekday_distribution(feed):
    result = Counter()

    for entry in feed:
        if entry["published"]:
            result[entry["published_datetime"].format("ddd")] += 1

    return result
