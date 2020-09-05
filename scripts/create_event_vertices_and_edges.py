from csv_modules import event_parser


def main(default_dir="../../"):
    """ This script will output all vertex and edges csv files for the selected event to the same
    directory under which the repository is located.

    Args:
        default_dir (str): Specify your own directory path or use default
    """
    event = "2015azch"
    event_parser.parse_single_event_to_csv(event, default_dir)


main()
