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

    # Parse Vertex
    vertex_filename = event_name + "_alliances_vertex.csv"
    columns = ['captain', 'pick1', 'pick2']
    alliances_vertex_df = pd.read_csv(alliances_csv, names=columns)
    alliances_vertex_df.insert(0, 'allianceId', range(1, 1 + len(alliances_vertex_df)))
    alliances_vertex_df.to_csv(f"{directory}/{vertex_filename}")

    # Parse Edges
    edges = list()
    for alliance_role in columns:
        team_col = alliances_vertex_df[alliance_role]
        alliance_id_col = alliances_vertex_df['allianceId']

        new_df = pd.DataFrame({"fr_team": team_col})
        new_df["alliance"] = alliance_id_col
        new_df["state_city"] = event_name[4::]

        edges.append(new_df)

    edge_filename = event_name + "_alliances_edge.csv"
    alliances_edges_df = pd.concat(edges, ignore_index=True)
    alliances_edges_df.to_csv(f"{directory}/{edge_filename}")


def event_awards_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """
    filename = event_name + "_awards.csv"
    awards_csv = get_event_csv_url(event_name, filename)

    # Parse Vertex
    vertex_filename = event_name + "_awards_vertex.csv"
    columns = ['eventKey', 'award', 'team', 'awardee']
    awards_vertex_df = pd.read_csv(awards_csv, names=columns)

    new_awardee_values_list = list()
    for val in awards_vertex_df['awardee']:
        if type(val) is float:
            new_awardee_values_list.append("n/a")
        else:
            new_awardee_values_list.append(val)

    awards_vertex_df.update({'awardee': new_awardee_values_list})
    awards_vertex_df.to_csv(f"{directory}/{vertex_filename}")

    # Parse Edge
    edge_filename = event_name + "_awards_edge.csv"
    awards_edge_df = pd.DataFrame({"fr_team": awards_vertex_df['team'],
                                   "award": awards_vertex_df['award']})
    awards_edge_df["state_city"] = event_name[4::]
    awards_edge_df.to_csv(f"{directory}/{edge_filename}")


def event_matches_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """
    # Parse Vertex
    vertex_filename = event_name + "_matches_vertex.csv"
    matches_vertex_df = parserFuncs.frc_matchData(event_name, AUTHENTICATION_KEY)
    matches_vertex_df.to_csv(f"{directory}/{vertex_filename}")

    # Parse Edge
    edge_filename = event_name + "_matches_edge.csv"
    teams = ['red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']
    total_score_blue = matches_vertex_df['blue.total_points']
    total_score_red = matches_vertex_df['red.total_points']
    edges = list()

    for team in teams:
        team_col = matches_vertex_df[team]

        if 'blue' in team:
            total_score = total_score_blue
        else:
            total_score = total_score_red

        new_df = pd.DataFrame({"fr_team": team_col, "color_team_score": total_score})
        new_df["color_team"] = team

        edges.append(new_df)

    matches_edges_df = pd.concat(edges, ignore_index=True)
    matches_edges_df.to_csv(f"{directory}/{edge_filename}")


def event_rankings_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """
    filename = event_name + "_rankings.csv"
    rankings_csv = get_event_csv_url(event_name, filename)

    # Parse Vertex
    vertex_filename = event_name + "_rankings_vertex.csv"
    rankings_vertex_df = pd.read_csv(rankings_csv)
    rankings_vertex_df.to_csv(f"{directory}/{vertex_filename}")

    # Parse Edges
    edge_filename = event_name + "_rankings_edge.csv"
    rankings_edges_df = pd.DataFrame({"fr_team": rankings_vertex_df["Team"],
                                      "rank": rankings_vertex_df["Rank"]})
    rankings_edges_df["state_city"] = event_name[4::]
    rankings_edges_df.to_csv(f"{directory}/{edge_filename}")


def event_teams_to_csv(event_name, directory):
    """
    Args:
        event_name (str):
        directory (str):
    """

    filename = event_name + "_teams.csv"
    teams_csv = get_event_csv_url(event_name, filename)

    teams_vertex_df = pd.read_csv(teams_csv, index_col=0, header=None).T
    teams_vertex_df.to_csv(f"{directory}/{filename}", header=['team'])


def get_event_csv_url(event_name, filename):
    """

    Args:
        event_name (str):
        filename (str):

    Returns:
        str: event_url
    """
    year = event_name[0:4]
    event_url = BASE_EVENT_URL + "/" + year + "/" + event_name + "/"
    csv_url = event_url + filename
    return csv_url
