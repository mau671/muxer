import subprocess
import json
import sys
import os
from args import parse_arguments
from typing import List, Dict, Any

args = parse_arguments()


def get_mkv_metadata(input_file):
    """
    Retrieves metadata from an MKV file using the mkvmerge tool.

    Args:
        input_file (str): The path to the MKV file from which to retrieve metadata.

    Returns:
        dict: A dictionary containing the metadata of the MKV file in JSON format.

    Raises:
        SystemExit: If the mkvmerge command fails, the program will exit with an error message.
    """
    command = ["mkvmerge", "--identify", input_file, "--identification-format", "json"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing mkvmerge: {result.stderr}")
        sys.exit(1)
    metadata = json.loads(result.stdout)
    return metadata


def process_video_tracks(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts and processes video tracks from the metadata.

    Args:
        metadata (Dict[str, Any]): Metadata containing track information.

    Returns:
        List[Dict[str, Any]]: A list of video track dictionaries.
    """
    return [track for track in metadata["tracks"] if track["type"] == "video"]


def process_audio_tracks(audio_tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processes audio tracks, setting appropriate properties like language, track name, and default status.

    Args:
        audio_tracks (List[Dict[str, Any]]): A list of audio track dictionaries.

    Returns:
        List[Dict[str, Any]]: A list of processed audio track dictionaries.
    """
    processed_audio_tracks = []
    default_spa_audio_set = False
    default_audio_set = False

    for track in audio_tracks:
        lang = track["properties"].get(
            "language_ietf", track["properties"].get("language")
        )
        title = track["properties"].get("track_name", "").lower()

        if lang == "es-419" or "lat" in title:
            # Set Spanish (Latin America) as the default track
            track["properties"].update(
                {
                    "track_name": "Spanish (Latin America)",
                    "language_ietf": "es-419",
                    "default_track": True,
                }
            )
            processed_audio_tracks.append(track)
            default_spa_audio_set = True
            break

    if not default_spa_audio_set:
        for track in audio_tracks:
            lang = track["properties"].get("language")
            title = track["properties"].get("track_name", "").lower()
            lang_code = track["properties"].get(
                "language_ietf", track["properties"].get("language")
            )

            if lang == "spa":
                if "lat" in title or lang_code == "es-419":
                    # Set Spanish (Latin America)
                    track["properties"].update(
                        {
                            "track_name": "Spanish (Latin America)",
                            "language_ietf": "es-419",
                        }
                    )
                elif lang_code in ["es-ES", "es-724"] or "europ" in title:
                    # Set Spanish (Spain)
                    track["properties"].update(
                        {"track_name": "Spanish (Spain)", "language_ietf": "es-ES"}
                    )
                else:
                    track["properties"]["track_name"] = "Spanish"

                track["properties"]["default_track"] = True
                processed_audio_tracks.append(track)
                default_spa_audio_set = True
                break

    for track in audio_tracks:
        lang = track["properties"].get("language")
        if lang in ["jpn", "chi", "kor", "eng"]:
            # Map language codes to readable track names
            lang_mappings = {
                "jpn": "Japanese",
                "chi": "Chinese",
                "kor": "Korean",
                "eng": "English",
            }
            track["properties"]["track_name"] = lang_mappings[lang]

            if lang == "chi":
                track["properties"]["language_ietf"] = "zh-CN"

            track["properties"]["default_track"] = (
                not default_spa_audio_set and not default_audio_set
            )

            if track["properties"]["default_track"]:
                default_audio_set = True

            processed_audio_tracks.append(track)

    return processed_audio_tracks


def process_subtitle_tracks(
    subtitle_tracks: List[Dict[str, Any]], default_spa_audio_set: bool
) -> List[Dict[str, Any]]:
    """
    Processes subtitle tracks, setting properties like language, track name, and default status.

    Args:
        subtitle_tracks (List[Dict[str, Any]]): A list of subtitle track dictionaries.
        default_spa_audio_set (bool): Whether a default Spanish audio track is set.

    Returns:
        List[Dict[str, Any]]: A list of processed subtitle track dictionaries.
    """
    processed_subtitle_tracks = []
    default_subtitle_set = False
    found_forced_subtitle = False

    for track in subtitle_tracks:
        lang = track["properties"].get(
            "language_ietf", track["properties"].get("language")
        )
        title = track["properties"].get("track_name", "").lower()
        forced = track["properties"].get("forced_track", False)

        if (lang == "es-419" or "lat" in title) and lang != "hi-Latn":
            if "forced" in title or forced:
                # Set Spanish (Latin America) forced subtitle
                track["properties"].update(
                    {
                        "track_name": "Spanish (Latin America) [Forced]",
                        "forced_track": True,
                        "default_track": True,
                        "language_ietf": "es-419",
                    }
                )
                default_subtitle_set = True
                found_forced_subtitle = True
            else:
                # Set Spanish (Latin America) subtitle
                track["properties"].update(
                    {"track_name": "Spanish (Latin America)", "language_ietf": "es-419"}
                )

                track["properties"]["default_track"] = (
                    not found_forced_subtitle and not default_spa_audio_set
                )
                default_subtitle_set = track["properties"]["default_track"]

            processed_subtitle_tracks.append(track)

    if not default_subtitle_set:
        for track in subtitle_tracks:
            lang = track["properties"].get("language")
            title = track["properties"].get("track_name", "").lower()

            if lang == "spa":
                # Set default Spanish subtitle if none exists
                track["properties"]["track_name"] = "Spanish"
                track["properties"]["default_track"] = (
                    not found_forced_subtitle or not default_spa_audio_set
                )
                default_subtitle_set = track["properties"]["default_track"]
                processed_subtitle_tracks.append(track)
                break

    for track in subtitle_tracks:
        lang = track["properties"].get("language")
        title = track["properties"].get("track_name", "").lower()
        forced = track["properties"].get("forced_track", False)

        if lang == "eng":
            if "forced" in title or forced:
                # Set English forced subtitle
                track["properties"]["track_name"] = "English [Forced]"
                track["properties"]["forced_track"] = True
            else:
                track["properties"]["track_name"] = "English"

            track["properties"]["default_track"] = not default_subtitle_set
            processed_subtitle_tracks.append(track)

    return processed_subtitle_tracks


def process_tracks(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Processes metadata to extract and process video, audio, and subtitle tracks.

    Args:
        metadata (Dict[str, Any]): Metadata containing track information.

    Returns:
        List[Dict[str, Any]]: A list of processed track dictionaries.
    """
    video_tracks = process_video_tracks(metadata)
    audio_tracks = [track for track in metadata["tracks"] if track["type"] == "audio"]
    subtitle_tracks = [
        track for track in metadata["tracks"] if track["type"] == "subtitles"
    ]

    processed_audio_tracks = process_audio_tracks(audio_tracks)
    processed_subtitle_tracks = process_subtitle_tracks(
        subtitle_tracks,
        any(
            track["properties"].get("default_track") for track in processed_audio_tracks
        ),
    )

    return video_tracks + processed_audio_tracks + processed_subtitle_tracks


def mux_files(input_file: str, output_file: str, tracks: List[Dict[str, Any]]) -> None:
    """
    Combines and processes multimedia tracks using mkvmerge.

    Args:
        input_file (str): Path to the input MKV file.
        output_file (str): Path to save the output MKV file.
        tracks (List[Dict[str, Any]]): List of track metadata to process.

    Raises:
        SystemExit: If mkvmerge fails to execute.
    """
    command = ["mkvmerge", "-o", output_file]
    track_order = []
    subtitle_tracks = []
    audio_tracks = []

    for track in tracks:
        track_id = track["id"]
        lang = track["properties"].get(
            "language_ietf", track["properties"].get("language", "und")
        )
        title = track["properties"].get("track_name", "")
        default = "yes" if track["properties"].get("default_track", False) else "no"

        if track["type"] == "subtitles":
            subtitle_tracks.append(str(track_id))

        if track["type"] == "audio":
            audio_tracks.append(str(track_id))

        command.extend(["--language", f"{track_id}:{lang}"])
        command.extend(["--default-track", f"{track_id}:{default}"])

        if title:
            command.extend(["--track-name", f"{track_id}:{title}"])

        track_order.append(f"0:{track_id}")

    if audio_tracks:
        command.extend(["--audio-tracks", ",".join(audio_tracks)])

    if subtitle_tracks:
        command.extend(["--subtitle-tracks", ",".join(subtitle_tracks)])

    command.extend(["--title", ""])
    command.extend(["--track-order", ",".join(track_order)])
    command.append(input_file)

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing mkvmerge: {result.stdout}")
        sys.exit(1)

    print(f"Muxed file saved to {output_file}")


if __name__ == "__main__":
    input_path = args.input
    output_path = args.output if args.output else input_path

    if os.path.isdir(input_path):
        files = [f for f in os.listdir(input_path) if f.endswith(".mkv")]
        files.sort()

        for file in files:
            input_file = os.path.join(input_path, file)
            output_file = os.path.join(
                output_path, f"{os.path.splitext(file)[0]}_muxed.mkv"
            )

            metadata = get_mkv_metadata(input_file)
            processed_tracks = process_tracks(metadata)

            mux_files(input_file, output_file, processed_tracks)

            if args.delete_after:
                os.remove(input_file)
    else:
        metadata = get_mkv_metadata(input_path)
        processed_tracks = process_tracks(metadata)

        mux_files(input_path, output_path, processed_tracks)
