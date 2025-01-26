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


def process_tracks(metadata):
    """
    Processes the tracks from the given metadata, categorizing them into video, audio, and subtitle tracks.
    It also sets default tracks based on specific language and title criteria.
    Args:
        metadata (dict): A dictionary containing track metadata. The dictionary should have a 'tracks' key,
                         which is a list of track dictionaries. Each track dictionary should have a 'type' key
                         (indicating 'video', 'audio', or 'subtitles') and a 'properties' key containing track properties.
    Returns:
        list: A list of processed tracks with updated properties.
    Track Properties:
        - type (str): The type of the track ('video', 'audio', 'subtitles').
        - properties (dict): A dictionary containing track properties such as:
            - language (str): The language code of the track.
            - language_ietf (str): The IETF language tag of the track.
            - track_name (str): The name of the track.
            - default_track (bool): Indicates if the track is the default track.
            - forced_track (bool): Indicates if the track is a forced track.
    Processing Details:
        - Video tracks are collected as-is.
        - Audio tracks are processed to set default tracks based on language and title criteria.
            - Spanish (Latin America) is prioritized and set as default if found.
            - Spanish (Spain) is set if no Latin American Spanish is found.
            - Japanese, Chinese, Korean, and English tracks are also processed and default tracks are set accordingly.
        - Subtitle tracks are processed to set default and forced tracks based on language and title criteria.
            - Spanish (Latin America) forced subtitles are prioritized and set as default if found.
            - Spanish (Spain) subtitles are set if no Latin American Spanish subtitles are found.
            - English subtitles are processed and default tracks are set accordingly.
    """
    video_tracks = []
    audio_tracks = []
    subtitle_tracks = []

    for track in metadata['tracks']:
        if track['type'] == 'video':
            video_tracks.append(track)
        elif track['type'] == 'audio':
            audio_tracks.append(track)
        elif track['type'] == 'subtitles':
            subtitle_tracks.append(track)

    processed_audio_tracks = []
    default_spa_audio_set = False
    default_audio_set = False

    for track in audio_tracks:
        lang = track['properties'].get('language_ietf', track['properties'].get('language'))
        title = track['properties'].get('track_name', '').lower()
        if lang == 'es-419' or 'lat' in title:
            track['properties']['track_name'] = 'Spanish (Latin America)'
            track['properties']['language_ietf'] = 'es-419'
            track['properties']['default_track'] = True
            processed_audio_tracks.append(track)
            default_spa_audio_set = True
            break

    if not default_spa_audio_set:
        for track in audio_tracks:
            lang = track['properties'].get('language')
            title = track['properties'].get('track_name', '').lower()
            lang_code = track['properties'].get('language_ietf', track['properties'].get('language'))
            if lang == 'spa':
                if 'lat' in title or lang_code == 'es-419':
                    track['properties']['track_name'] = 'Spanish (Latin America)'
                    track['properties']['language_ietf'] = 'es-419'
                else:
                    # If it has "European" in the name or the code is es-ES or es-724, change to "Spanish (Spain)" and the language to es-ES
                    if lang_code in ['es-ES', 'es-724'] or 'europ' in title:
                        track['properties']['track_name'] = 'Spanish (Spain)'
                        track['properties']['language_ietf'] = 'es-ES'
                    else:
                        track['properties']['track_name'] = 'Spanish'
                track['properties']['default_track'] = True
                processed_audio_tracks.append(track)
                default_spa_audio_set = True
                break

    for track in audio_tracks:
        lang = track['properties'].get('language')
        if lang == 'jpn':
            track['properties']['track_name'] = 'Japanese'
            if not default_spa_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False

            processed_audio_tracks.append(track)
        elif lang == 'chi':
            track['properties']['language_ietf'] = 'zh-CN'
            track['properties']['track_name'] = 'Chinese'
            if not default_audio_set or not default_spa_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False
            processed_audio_tracks.append(track)
        elif lang == 'kor':
            track['properties']['track_name'] = 'Korean'
            if not default_spa_audio_set or not default_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False
            processed_audio_tracks.append(track)
        elif lang == 'eng':
            track['properties']['track_name'] = 'English'
            processed_audio_tracks.append(track)
            if not default_spa_audio_set and not default_audio_set:
                track['properties']['default_track'] = True
                default_audio_set = True
            else:
                track['properties']['default_track'] = False

    processed_subtitle_tracks = []
    default_subtitle_set = False
    found_forced_subtitle = False

    for track in subtitle_tracks:
        lang = track['properties'].get('language_ietf', track['properties'].get('language'))
        title = track['properties'].get('track_name', '').lower()
        forced = track['properties'].get('forced_track', False)
        if (lang in ['es-419','es-MX'] or 'lat' in title) and lang != 'hi-Latn':
            if 'forced' in title or forced:
                track['properties']['track_name'] = 'Spanish (Latin America) [Forced]'
                track['properties']['forced_track'] = True
                track['properties']['default_track'] = True
                track['properties']['language_ietf'] = 'es-419'
                if 'ao' in title:
                    track['properties']['track_name'] += ' [AO]'
                processed_subtitle_tracks.insert(0, track)
                default_subtitle_set = True
                found_forced_subtitle = True
            else:
                track['properties']['track_name'] = 'Spanish (Latin America)'
                track['properties']['language_ietf'] = 'es-419'
                if not found_forced_subtitle:
                    if not default_spa_audio_set:
                        track['properties']['default_track'] = True
                        default_subtitle_set = True
                    else:
                        track['properties']['default_track'] = False
                else:
                    track['properties']['default_track'] = False
                if 'ao' in title:
                    track['properties']['track_name'] += ' [AO]'
                if 'sdh' in title:
                    track['properties']['track_name'] += ' [SDH]'
                if 'cc' in title:
                    track['properties']['track_name'] += ' [CC]'
                if 'dub' in title:
                    track['properties']['track_name'] += ' [Dubtitle]'
                processed_subtitle_tracks.append(track)
        
    if not default_subtitle_set:
        for track in subtitle_tracks:
            lang = track['properties'].get('language')
            title = track['properties'].get('track_name', '').lower()
            lang_code = track['properties'].get('language_ietf', track['properties'].get('language'))
            if lang == 'spa' and not default_subtitle_set:
                if lang_code in ['es-ES', 'es-724'] or 'europ' in title:
                    track['properties']['track_name'] = 'Spanish (Spain)'
                    track['properties']['language_ietf'] = 'es-ES'
                else:
                    track['properties']['track_name'] = 'Spanish'
                # Should be True if no forced subtitle is found or if there is no Spanish audio
                track['properties']['default_track'] = not found_forced_subtitle or not default_spa_audio_set
                default_subtitle_set = track['properties']['default_track']
                if 'sdh' in title:
                    track['properties']['track_name'] += ' [SDH]'
                if 'cc' in title:
                    track['properties']['track_name'] += ' [CC]'
                if 'dub' in title:
                    track['properties']['track_name'] += ' [Dubtitle]'
                processed_subtitle_tracks.append(track)
                break

    for track in subtitle_tracks:
        lang = track['properties'].get('language')
        forced = track['properties'].get('forced_track', False)
        title = track['properties'].get('track_name', '').lower()
        if lang == 'eng':
            if 'forced' in title or forced:
                track['properties']['track_name'] = 'English [Forced]'
                track['properties']['forced_track'] = True
            else:
                track['properties']['track_name'] = 'English'
            if not default_subtitle_set:
                track['properties']['default_track'] = True
            else:
                track['properties']['default_track'] = False
            if 'sdh' in title:
                track['properties']['track_name'] += ' [SDH]'
            if 'cc' in title:
                track['properties']['track_name'] += ' [CC]'
            if 'dub' in title:
                track['properties']['track_name'] += ' [Dubtitle]'
            processed_subtitle_tracks.append(track)

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
