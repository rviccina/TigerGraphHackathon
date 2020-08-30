from lxml import html
import requests

from backend import parserFuncs
from csv_modules import csv_helper

AUTHENTICATION_KEY = '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'
BLUE_ALLIANCE_EVENTS_URL = 'https://github.com/the-blue-alliance/the-blue-alliance-data/tree/master/events'


def parse_all_events_to_csv(year, directory):
    """ Parses all FRC events from an entire year and stores them in a CSV file

    Args:
        year (str): year of the competition to be parsed
        directory (str): folder to store csv files
    """

    event_list = __get_events_list(year)

    for event in event_list:
        try:
            parse_single_event_to_csv(event, directory)
        except Exception as e:
            print(f"Exception thrown by event: {event}")
            print(e)


def parse_single_event_to_csv(event_name, directory):
    """ Parses a single FRC match event and stores it in a CSV file

    Args:
        event_name (str): name of the event in the appropriate format
        directory (str): folder to store csv files
    """
    try:
        csv_helper.event_alliances_to_csv(event_name, directory)
        csv_helper.event_awards_to_csv(event_name, directory)
        csv_helper.event_matches_to_csv(event_name, directory)
        csv_helper.event_rankings_to_csv(event_name, directory)
        csv_helper.event_teams_to_csv(event_name, directory)

    except Exception as ex:
        print(f"Exception thrown by event: {event_name} \n"
              f"{ex}")


def __get_events_list(year):
    """ Gets a list of all the event names from the Blue Alliance Github Repository for the specified year

    Args:
        year (str): year of interest

    Returns:
        list: events_list
    """
    event_year_url = BLUE_ALLIANCE_EVENTS_URL + "/" + year
    page = requests.get(event_year_url)
    page_html = html.fromstring(page.content)
    events = page_html.xpath(f"//a[re:match(text(), \'{year}\')]",
                             namespaces={"re": "http://exslt.org/regular-expressions"})
    events_list = list(map(lambda event: event.text, events))
    return events_list
