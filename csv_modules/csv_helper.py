import pandas as pd
from backend import parserFuncs


BASE_EVENT_URL = "https://raw.githubusercontent.com/the-blue-alliance/the-blue-alliance-data/master/events/"
AUTHENTICATION_KEY = '3BFWLXdBe4yJUCo73Ky3hiBLdKNwCWHe9Nm1Xwr3JSIv5oOM3S1UNdufyTMKBAVU'


def event_alliances_to_csv(event_name, directory):
    """

    Args:
        event_name (str):
        directory (str):
    """
    filename = event_name + "_alliances.csv"
    alliances_csv = get_event_csv_url(event_name, filename)

    columns = ['captain', 'pick1', 'pick2']
    alliances_df = pd.read_csv(alliances_csv, names=columns)
    alliances_df.insert(0, 'allianceId', range(0, 0 + len(alliances_df)))
    alliances_df.to_csv(f"{directory}/{filename}")


def event_awards_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """
    filename = event_name + "_awards.csv"
    awards_csv = get_event_csv_url(event_name, filename)

    columns = ['eventKey', 'award', 'team', 'awardee']
    awards_df = pd.read_csv(awards_csv, names=columns)
    awards_df.to_csv(f"{directory}/{filename}")


def event_matches_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """
    filename = event_name + "_matches.csv"
    matches_df = parserFuncs.frc_matchData(event_name, AUTHENTICATION_KEY)
    matches_df.to_csv(f"{directory}/{filename}")


def event_rankings_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """

    filename = event_name + "_rankings.csv"
    rankings_csv = get_event_csv_url(event_name, filename)

    matches_df = pd.read_csv(rankings_csv)
    matches_df.to_csv(f"{directory}/{filename}")


def event_teams_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """

    filename = event_name + "_teams.csv"
    teams_csv = get_event_csv_url(event_name, filename)

    teams_df = pd.read_csv(teams_csv, index_col=0, header=None).T
    teams_df.to_csv(f"{directory}/{filename}", header=['team'])


def get_event_csv_url(event_name, filename):
    """

    Args:
        event_name (str):

    Returns:
        str: event_url
    """
    year = event_name[0:4]
    event_url = BASE_EVENT_URL + "/" + year + "/" + event_name + "/"
    csv_url = event_url + filename

    return csv_url
