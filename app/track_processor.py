from typing import Any


def process_tracks(metadata: dict[str, Any]) -> list[dict[str, Any]]:
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

    for track in metadata["tracks"]:
        if track["type"] == "video":
            video_tracks.append(track)
        elif track["type"] == "audio":
            audio_tracks.append(track)
        elif track["type"] == "subtitles":
            subtitle_tracks.append(track)

    processed_audio_tracks = []
    default_spa_audio_set = False
    default_audio_set = False

    for track in audio_tracks:
        lang = track["properties"].get(
            "language_ietf", track["properties"].get("language")
        )
        title = track["properties"].get("track_name", "").lower()
        if lang == "es-419" or ("lat" in title and lang not in ["hi-Latn", "sr-Latn"]):
            track["properties"]["track_name"] = "Spanish (Latin America)"
            track["properties"]["language_ietf"] = "es-419"
            track["properties"]["default_track"] = True
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
                    track["properties"]["track_name"] = "Spanish (Latin America)"
                    track["properties"]["language_ietf"] = "es-419"
                else:
                    # If it has "European" in the name or the code is es-ES or es-724, change to "Spanish (Spain)" and the language to es-ES
                    if lang_code in ["es-ES", "es-724"] or "europ" in title:
                        track["properties"]["track_name"] = "Spanish (Spain)"
                        track["properties"]["language_ietf"] = "es-ES"
                    else:
                        track["properties"]["track_name"] = "Spanish"
                track["properties"]["default_track"] = True
                processed_audio_tracks.append(track)
                default_spa_audio_set = True
                break

    for track in audio_tracks:
        lang = track["properties"].get("language")
        if lang == "jpn":
            track["properties"]["track_name"] = "Japanese"
            if not default_spa_audio_set:
                track["properties"]["default_track"] = True
                default_audio_set = True
            else:
                track["properties"]["default_track"] = False

            processed_audio_tracks.append(track)
        elif lang == "chi":
            track["properties"]["language_ietf"] = "zh-CN"
            track["properties"]["track_name"] = "Chinese"
            if not default_audio_set and not default_spa_audio_set:
                track["properties"]["default_track"] = True
                default_audio_set = True
            else:
                track["properties"]["default_track"] = False
            processed_audio_tracks.append(track)
        elif lang == "kor":
            track["properties"]["track_name"] = "Korean"
            if not default_spa_audio_set and not default_audio_set:
                track["properties"]["default_track"] = True
                default_audio_set = True
            else:
                track["properties"]["default_track"] = False
            processed_audio_tracks.append(track)
        elif lang == "eng":
            track["properties"]["track_name"] = "English"
            processed_audio_tracks.append(track)
            if not default_spa_audio_set and not default_audio_set:
                track["properties"]["default_track"] = True
                default_audio_set = True
            else:
                track["properties"]["default_track"] = False

    processed_subtitle_tracks = []
    found_forced_subtitle = False
    found_latin_subtitles = False

    # First pass: Process Latin American subtitles (both forced and complete)
    for track in subtitle_tracks:
        lang = track["properties"].get(
            "language_ietf", track["properties"].get("language")
        )
        title = track["properties"].get("track_name", "").lower()
        forced = track["properties"].get("forced_track", False)

        # Check if this is a Latin American Spanish subtitle
        is_latin_subtitle = (
            lang in ["es-419", "es-MX"] or "lat" in title or "latin american" in title
        ) and lang not in ["hi-Latn", "sr-Latn"]

        if is_latin_subtitle:
            found_latin_subtitles = True
            if "forced" in title or forced:
                track["properties"]["track_name"] = "Spanish (Latin America) [Forced]"
                track["properties"]["forced_track"] = True
                track["properties"]["default_track"] = True
                track["properties"]["language_ietf"] = "es-419"
                if "ao" in title:
                    track["properties"]["track_name"] += " [AO]"
                processed_subtitle_tracks.insert(0, track)
                found_forced_subtitle = True
            else:
                # Complete Latin American subtitles
                track["properties"]["track_name"] = "Spanish (Latin America)"
                track["properties"]["language_ietf"] = "es-419"
                # Set as default if there's no Spanish audio (prioritize over English)
                track["properties"]["default_track"] = not default_spa_audio_set
                if "ao" in title:
                    track["properties"]["track_name"] += " [AO]"
                if "sdh" in title:
                    track["properties"]["track_name"] += " [SDH]"
                if "cc" in title:
                    track["properties"]["track_name"] += " [CC]"
                if "dub" in title:
                    track["properties"]["track_name"] += " [Dubtitle]"
                processed_subtitle_tracks.append(track)

    # Second pass: Process other Spanish subtitles (Spain/European and generic)
    # Only include Spain/European subtitles if NO Latin American subtitles were found
    if not found_latin_subtitles:
        for track in subtitle_tracks:
            lang = track["properties"].get("language")
            title = track["properties"].get("track_name", "").lower()
            lang_code = track["properties"].get(
                "language_ietf", track["properties"].get("language")
            )
            forced = track["properties"].get("forced_track", False)

            # Skip if already processed as Latin American
            is_latin_subtitle = (
                lang_code in ["es-419", "es-MX"]
                or "lat" in title
                or "latin american" in title
            ) and lang not in ["hi-Latn", "sr-Latn"]

            if lang == "spa" and not is_latin_subtitle:
                # Determine if this is Spain Spanish or generic Spanish
                if lang_code in ["es-ES", "es-724"] or "europ" in title:
                    track["properties"]["track_name"] = "Spanish (Spain)"
                    track["properties"]["language_ietf"] = "es-ES"
                else:
                    track["properties"]["track_name"] = "Spanish"

                # Don't set as default if there's already Spanish audio (any variant)
                track["properties"]["default_track"] = False

                if "forced" in title or forced:
                    track["properties"]["track_name"] += " [Forced]"
                    track["properties"]["forced_track"] = True
                if "sdh" in title:
                    track["properties"]["track_name"] += " [SDH]"
                if "cc" in title:
                    track["properties"]["track_name"] += " [CC]"
                if "dub" in title:
                    track["properties"]["track_name"] += " [Dubtitle]"
                processed_subtitle_tracks.append(track)

    # Third pass: Process English subtitles
    for track in subtitle_tracks:
        lang = track["properties"].get("language")
        forced = track["properties"].get("forced_track", False)
        title = track["properties"].get("track_name", "").lower()
        if lang == "eng":
            if "forced" in title or forced:
                track["properties"]["track_name"] = "English [Forced]"
                track["properties"]["forced_track"] = True
            else:
                track["properties"]["track_name"] = "English"

            # Only set English as default if:
            # 1. No forced subtitles were found AND
            # 2. No Spanish audio is present (any variant) AND
            # 3. No Latin American subtitles were found
            if (
                not found_forced_subtitle
                and not default_spa_audio_set
                and not found_latin_subtitles
            ):
                track["properties"]["default_track"] = True
            else:
                track["properties"]["default_track"] = False

            if "sdh" in title:
                track["properties"]["track_name"] += " [SDH]"
            if "cc" in title:
                track["properties"]["track_name"] += " [CC]"
            if "dub" in title:
                track["properties"]["track_name"] += " [Dubtitle]"
            processed_subtitle_tracks.append(track)

    return video_tracks + processed_audio_tracks + processed_subtitle_tracks
