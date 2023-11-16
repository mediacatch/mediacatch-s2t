import argparse
import sys

from rich.console import Console
from mediacatch_s2t import uploader


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='mediacatch_s2t',
        usage='%(prog)s [options] api_key file',
        description='Upload a media file and get the transcription from MediaCatch.'
    )
    parser.add_argument("api_key", type=str, help="MediaCatch API key.")
    parser.add_argument("file", type=str, help="A media file.")
    parser.add_argument("--quota", type=str, default='any', help="The main language in the file.")
    args = parser.parse_args()

    console = Console()
    with console.status(
            "[bold green]Uploading file to MediaCatch..."):
        result = uploader.upload_and_get_transcription(args.file, args.api_key, args.quota)
        if result['status'] == 'error':
            sys.exit(
                f"Error occurred:\n{result['message']}. "
                f"Please contact support@mediacatch.io for further information."
            )
        console.print(f"[bold]transcription url: {result['url']}")
        console.print(
            f"[bold]estimated processing time: "
            f"{result['estimated_processing_time']} [not bold]seconds"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
