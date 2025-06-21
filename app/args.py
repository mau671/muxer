import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="MKV file processor with automatic track naming and language configuration"
    )

    parser.add_argument(
        "-i", "--input", required=True, help="Path to the input file or directory"
    )
    parser.add_argument(
        "-o", "--output", required=False, help="Path to the output file or directory"
    )
    parser.add_argument(
        "--delete-after",
        action="store_true",
        help="Delete the source files after processing",
    )

    return parser.parse_args()
