from csv_modules import event_parser


def main(default_dir="../../"):
    """ This script will output all vertex and edges csv files for the selected event to the same
    directory under which the repository is located.

    Args:
        default_dir (str): Specify your own directory path or use default
    """
    event_year = "2015"
    event_parser.parse_all_events_to_csv(event_year, default_dir)


main()
