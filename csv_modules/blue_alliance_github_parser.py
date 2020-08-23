from lxml import html
import requests

from backend import parserFuncs

AUTHENTICATION_KEY = '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'
BLUE_ALLIANCE_EVENTS_URL = 'https://github.com/the-blue-alliance/the-blue-alliance-data/tree/master/events'
CSV_DIRECTORY = "/Users/renzo/Desktop/BlueAllianceCSV/"


def parse_events_to_csv(year):
    """ Parses FRC events from an entire year and stores them in a CSV file

    Args:
        year (str): year of the competition to be parsed
    """

    event_year_url = BLUE_ALLIANCE_EVENTS_URL + "/" + year
    page = requests.get(event_year_url)
    tree = html.fromstring(page.content)
    events = tree.xpath(f"//a[re:match(text(), \'{year}\')]",
                             namespaces={"re": "http://exslt.org/regular-expressions"})
    events = list(map(lambda event: event.text, events))

    for event in events:
        try:
            event_df = parserFuncs.frc_matchData(event, AUTHENTICATION_KEY)
            event_df.to_csv(f"{CSV_DIRECTORY + event}.csv")
        except Exception:
            print(f"Exception thrown by event: {event}")
