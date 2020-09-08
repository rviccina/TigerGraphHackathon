from lxml import html
import requests

import pandas as pd
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

    alliance_vertex_dfs = list()
    alliance_edges_dfs = list()

    awards_vertex_dfs = list()
    awards_edges_dfs = list()

    matches_vertex_dfs = list()
    matches_edges_dfs = list()

    rankings_vertex_dfs = list()
    rankings_edges_dfs = list()

    teams_vertex_dfs = list()

    for event in event_list:
        try:
            df_dict = parse_single_event_to_csv(event, directory)
            assert len(df_dict) > 0

            alliance_vertex_dfs.append(df_dict["alliance"][0])
            alliance_edges_dfs.append(df_dict["alliance"][1])

            awards_vertex_dfs.append(df_dict["awards"][0])
            awards_edges_dfs.append(df_dict["awards"][1])

            matches_vertex_dfs.append(df_dict["matches"][0])
            matches_edges_dfs.append(df_dict["matches"][1])

            rankings_vertex_dfs.append(df_dict["rankings"][0])
            rankings_edges_dfs.append(df_dict["rankings"][1])

            teams_vertex_dfs.append(df_dict["teams"])

        except Exception as e:
            print(f"Exception thrown by event: {event}")
            print(e)

    alliance_vertex_dataframe = pd.concat(alliance_vertex_dfs, ignore_index=True)
    alliance_edge_dataframe = pd.concat(alliance_edges_dfs, ignore_index=True)

    awards_vertex_dataframe = pd.concat(awards_vertex_dfs, ignore_index=True)
    awards_edge_dataframe = pd.concat(awards_edges_dfs, ignore_index=True)

    matches_vertex_dataframe = pd.concat(matches_vertex_dfs, ignore_index=True)
    matches_edge_dataframe = pd.concat(matches_edges_dfs, ignore_index=True)

    rankings_vertex_dataframe = pd.concat(rankings_vertex_dfs, ignore_index=True)
    rankings_edge_dataframe = pd.concat(rankings_edges_dfs, ignore_index=True)

    teams_vertex_dataframe = pd.concat(teams_vertex_dfs, ignore_index=True)

    alliance_vertex_dataframe.to_csv(f"{directory}/{year}_alliance_vertex.csv")
    alliance_edge_dataframe.to_csv(f"{directory}/{year}_alliance_edge.csv")

    awards_vertex_dataframe.to_csv(f"{directory}/{year}_awards_vertex.csv")
    awards_edge_dataframe.to_csv(f"{directory}/{year}_awards_edge.csv")

    matches_vertex_dataframe.to_csv(f"{directory}/{year}_matches_vertex.csv")
    matches_edge_dataframe.to_csv(f"{directory}/{year}_matches_edge.csv")

    rankings_vertex_dataframe.to_csv(f"{directory}/{year}_rankings_vertex.csv")
    rankings_edge_dataframe.to_csv(f"{directory}/{year}_rankings_edge.csv")

    teams_vertex_dataframe = teams_vertex_dataframe.drop_duplicates()
    teams_vertex_dataframe.to_csv(f"{directory}/{year}_teams.csv")


def parse_single_event_to_csv(event_name, directory):
    """ Parses a single FRC match event and stores it in a CSV file

    Args:
        event_name (str): name of the event in the appropriate format
        directory (str): folder to store csv files
    """
    df_dict = dict()
    try:
        alliance_vertex_df, alliance_edge_df = csv_helper.event_alliances_to_csv(event_name, directory)
        award_vertex_df, award_edge_df = csv_helper.event_awards_to_csv(event_name, directory)
        matches_vertex_df, matches_edge_df = csv_helper.event_matches_to_csv(event_name, directory)
        rankings_vertex_df, rankings_edge_df = csv_helper.event_rankings_to_csv(event_name, directory)
        teams_vertex_df = csv_helper.event_teams_to_csv(event_name, directory)

        df_dict["alliance"] = (alliance_vertex_df, alliance_edge_df)
        df_dict["awards"] = (award_vertex_df, award_edge_df)
        df_dict["matches"] = (matches_vertex_df, matches_edge_df)
        df_dict["rankings"] = (rankings_vertex_df, rankings_edge_df)
        df_dict["teams"] = teams_vertex_df

    except Exception as ex:
        print(f"Exception thrown by event: {event_name} \n"
              f"{ex}")

    return df_dict


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
