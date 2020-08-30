from csv_modules import event_parser


def main():
    event = "2015azch"
    csv_files_directory = "/path/to/your/directory"

    event_parser.parse_single_event_to_csv(event, csv_files_directory)


main()
