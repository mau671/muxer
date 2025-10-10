import re
from typing import Any

# Language mapping for regional variants
LANGUAGE_MAPPING = {
    # Spanish variants
    "es-ES": "Spanish (ES)",
    "es-419": "Spanish (Latin America)",
    "es-MX": "Spanish (MX)",
    "es-AR": "Spanish (AR)",
    "es-CL": "Spanish (CL)",
    "es-CO": "Spanish (CO)",
    "es-PE": "Spanish (PE)",
    "es-VE": "Spanish (VE)",
    "es-UY": "Spanish (UY)",
    "es-PY": "Spanish (PY)",
    "es-BO": "Spanish (BO)",
    "es-EC": "Spanish (EC)",
    "es-CR": "Spanish (CR)",
    "es-PA": "Spanish (PA)",
    "es-GT": "Spanish (GT)",
    "es-HN": "Spanish (HN)",
    "es-SV": "Spanish (SV)",
    "es-NI": "Spanish (NI)",
    "es-DO": "Spanish (DO)",
    "es-CU": "Spanish (CU)",
    "es-PR": "Spanish (PR)",
    # English variants
    "en-US": "English (US)",
    "en-GB": "English (GB)",
    "en-AU": "English (AU)",
    "en-CA": "English (CA)",
    "en-IE": "English (IE)",
    "en-NZ": "English (NZ)",
    "en-ZA": "English (ZA)",
    "en-IN": "English (IN)",
    # Chinese variants
    "zh-CN": "Chinese (CN)",
    "zh-TW": "Chinese (TW)",
    "zh-HK": "Chinese (HK)",
    "zh-SG": "Chinese (SG)",
    "zh-MO": "Chinese (MO)",
    # Portuguese variants
    "pt-BR": "Portuguese (BR)",
    "pt-PT": "Portuguese (PT)",
    "pt-AO": "Portuguese (AO)",
    "pt-MZ": "Portuguese (MZ)",
    # French variants
    "fr-FR": "French (FR)",
    "fr-CA": "French (CA)",
    "fr-BE": "French (BE)",
    "fr-CH": "French (CH)",
    # Arabic variants
    "ar-SA": "Arabic (SA)",
    "ar-AE": "Arabic (AE)",
    "ar-EG": "Arabic (EG)",
    "ar-MA": "Arabic (MA)",
    "ar-DZ": "Arabic (DZ)",
    "ar-TN": "Arabic (TN)",
    "ar-LB": "Arabic (LB)",
    "ar-SY": "Arabic (SY)",
    "ar-JO": "Arabic (JO)",
    "ar-IQ": "Arabic (IQ)",
    "ar-KW": "Arabic (KW)",
    "ar-QA": "Arabic (QA)",
    "ar-BH": "Arabic (BH)",
    "ar-OM": "Arabic (OM)",
    "ar-YE": "Arabic (YE)",
    # German variants
    "de-DE": "German (DE)",
    "de-AT": "German (AT)",
    "de-CH": "German (CH)",
    # Italian variants
    "it-IT": "Italian (IT)",
    "it-CH": "Italian (CH)",
    # Korean variants
    "ko-KR": "Korean (KR)",
    "ko-KP": "Korean (KP)",
    # Japanese (typically only one variant)
    "ja-JP": "Japanese (JP)",
    # Norwegian variants
    "nb-NO": "Norwegian Bokmal (NO)",
    "nn-NO": "Norwegian Nynorsk (NO)",
    # Dutch variants
    "nl-NL": "Dutch (NL)",
    "nl-BE": "Dutch (BE)",
}

# Title patterns to extract regional information
TITLE_PATTERNS = {
    # Spanish regional patterns
    r"latin\s*american?|lat(?:ino)?(?:america)?": "es-419",
    r"european?|spain|castilian|peninsular": "es-ES",
    r"mexican?|mexico": "es-MX",
    r"argentin[ae]|argentina": "es-AR",
    r"chile|chilean": "es-CL",
    r"colombia|colombian": "es-CO",
    r"peru|peruvian": "es-PE",
    r"venezuela|venezuelan": "es-VE",
    # English regional patterns
    r"american?|usa?|us": "en-US",
    r"british|uk|britain|england": "en-GB",
    r"australian?|australia": "en-AU",
    r"canadian?|canada": "en-CA",
    # Chinese regional patterns
    r"simplified|china|mainland": "zh-CN",
    r"traditional|taiwan|hong\s*kong|hk": "zh-TW",
    r"hong\s*kong|hk": "zh-HK",
    # Portuguese regional patterns
    r"brazilian?|brazil": "pt-BR",
    r"european?|portugal": "pt-PT",
    # French regional patterns
    r"canadian?|canada|quebec": "fr-CA",
    r"french|france|european?": "fr-FR",
    # Arabic regional patterns
    r"saudi\s*arabia|saudi": "ar-SA",
    r"egypt|egyptian": "ar-EG",
    r"morocco|moroccan": "ar-MA",
}

# Special markers to preserve
SPECIAL_MARKERS = ["MTL", "CC", "SDH", "AO", "Dubtitle", "Forced"]


def extract_regional_info(
    title: str, language_ietf: str, language: str
) -> tuple[str, str]:
    """Extract regional language code and display name from title and language codes."""
    if not title:
        title = ""

    title_lower = title.lower()

    # First, check if we have a direct IETF language code that's already regional
    if language_ietf and language_ietf in LANGUAGE_MAPPING:
        return language_ietf, LANGUAGE_MAPPING[language_ietf]

    # Check for mediainfo format like "Spanish (Latin America)", "Chinese (CN)", etc.
    if language_ietf:
        # Handle full region names in parentheses
        if "spanish (latin america)" in language_ietf.lower():
            return "es-419", "Spanish (Latin America)"
        elif (
            "chinese (simplified)" in language_ietf.lower()
            or "chinese (china)" in language_ietf.lower()
        ):
            return "zh-CN", "Chinese (CN)"
        elif (
            "chinese (traditional)" in language_ietf.lower()
            or "chinese (taiwan)" in language_ietf.lower()
        ):
            return "zh-TW", "Chinese (TW)"
        elif (
            "chinese (hk)" in language_ietf.lower()
            or "chinese (hong kong)" in language_ietf.lower()
        ):
            return "zh-HK", "Chinese (HK)"
        elif (
            "portuguese (br)" in language_ietf.lower()
            or "portuguese (brazil)" in language_ietf.lower()
        ):
            return "pt-BR", "Portuguese (BR)"
        elif (
            "portuguese (pt)" in language_ietf.lower()
            or "portuguese (portugal)" in language_ietf.lower()
        ):
            return "pt-PT", "Portuguese (PT)"
        elif (
            "french (ca)" in language_ietf.lower()
            or "french (canada)" in language_ietf.lower()
        ):
            return "fr-CA", "French (CA)"
        elif (
            "french (fr)" in language_ietf.lower()
            or "french (france)" in language_ietf.lower()
        ):
            return "fr-FR", "French (FR)"
        elif (
            "arabic (sa)" in language_ietf.lower()
            or "arabic (saudi arabia)" in language_ietf.lower()
        ):
            return "ar-SA", "Arabic (SA)"
        elif "english (us)" in language_ietf.lower():
            return "en-US", "English (US)"
        elif "english (gb)" in language_ietf.lower():
            return "en-GB", "English (GB)"
        elif "english (au)" in language_ietf.lower():
            return "en-AU", "English (AU)"
        elif "english (ca)" in language_ietf.lower():
            return "en-CA", "English (CA)"
        elif "spanish (es)" in language_ietf.lower():
            return "es-ES", "Spanish (ES)"
        elif "spanish (mx)" in language_ietf.lower():
            return "es-MX", "Spanish (MX)"
        elif "spanish (ar)" in language_ietf.lower():
            return "es-AR", "Spanish (AR)"

        # Extract from short format parentheses like "Spanish (ES)" or "Portuguese (BR)"
        lang_match = re.search(r"(\w+)\s*\(([A-Z]{2,3})\)", language_ietf)
        if lang_match:
            base_lang = lang_match.group(1).lower()
            region = lang_match.group(2)

            # Try to construct IETF code
            constructed_code = None
            if base_lang == "spanish":
                constructed_code = f"es-{region}"
            elif base_lang == "english":
                constructed_code = f"en-{region}"
            elif base_lang == "chinese":
                constructed_code = f"zh-{region}"
            elif base_lang == "portuguese":
                constructed_code = f"pt-{region}"
            elif base_lang == "french":
                constructed_code = f"fr-{region}"
            elif base_lang == "arabic":
                constructed_code = f"ar-{region}"
            elif base_lang == "german":
                constructed_code = f"de-{region}"
            elif base_lang == "italian":
                constructed_code = f"it-{region}"
            elif base_lang == "korean":
                constructed_code = f"ko-{region}"
            elif base_lang == "japanese":
                constructed_code = f"ja-{region}"

            if constructed_code and constructed_code in LANGUAGE_MAPPING:
                return constructed_code, LANGUAGE_MAPPING[constructed_code]

    # Try to extract from title patterns
    for pattern, lang_code in TITLE_PATTERNS.items():
        if re.search(pattern, title_lower):
            if lang_code in LANGUAGE_MAPPING:
                return lang_code, LANGUAGE_MAPPING[lang_code]

    # Check for specific Chinese variants in title
    if "chinese" in title_lower:
        if (
            "simplified" in title_lower
            or "china" in title_lower
            or "mainland" in title_lower
        ):
            return "zh-CN", "Chinese (CN)"
        elif "traditional" in title_lower or "taiwan" in title_lower:
            return "zh-TW", "Chinese (TW)"
        elif (
            "hong kong" in title_lower
            or " hk " in title_lower
            or title_lower.endswith("hk")
        ):
            return "zh-HK", "Chinese (HK)"

    # Fallback to base language mapping with improved 3-letter code handling
    base_language_map = {
        "spa": "Spanish",
        "eng": "English",
        "jpn": "Japanese",
        "chi": "Chinese",
        "kor": "Korean",
        "fre": "French",
        "ger": "German",
        "ita": "Italian",
        "por": "Portuguese",
        "ara": "Arabic",
        "dut": "Dutch",
        "rus": "Russian",
        "pol": "Polish",
        "cze": "Czech",
        "hun": "Hungarian",
        "fin": "Finnish",
        "swe": "Swedish",
        "nor": "Norwegian",
        "dan": "Danish",
        "tha": "Thai",
        "vie": "Vietnamese",
        "ind": "Indonesian",
        "may": "Malay",
        "tur": "Turkish",
        "hin": "Hindi",
        "bul": "Bulgarian",
        "cro": "Croatian",
        "slv": "Slovenian",
        "mac": "Macedonian",
        "rom": "Romanian",
        "gre": "Greek",
        "ukr": "Ukrainian",
        "est": "Estonian",
        "lav": "Latvian",
        "lit": "Lithuanian",
        "slo": "Slovak",
        "ser": "Serbian",
    }

    if language in base_language_map:
        return language, base_language_map[language]

    # Final fallback
    return language_ietf or language or "und", title or "Unknown"


def extract_special_markers(title: str) -> list[str]:
    """Extract special markers from title."""
    if not title:
        return []

    markers = []
    title_upper = title.upper()

    for marker in SPECIAL_MARKERS:
        if marker.upper() in title_upper:
            markers.append(marker)

    return markers


def process_tracks(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Processes the tracks from the given metadata, categorizing them into video, audio, and subtitle tracks.
    It also sets default tracks based on specific language and title criteria.
    Now supports regional language variants and preserves special markers.
    Special handling for Chinese anime audio tracks.

    Args:
        metadata (dict): A dictionary containing track metadata. The dictionary should have a 'tracks' key,
                         which is a list of track dictionaries. Each track dictionary should have a 'type' key
                         (indicating 'video', 'audio', or 'subtitles') and a 'properties' key containing track properties.
    Returns:
        list: A list of processed tracks with updated properties.
    """
    video_tracks = []
    audio_tracks = []
    subtitle_tracks = []

    for track in metadata["tracks"]:
        if track["type"] == "video":
            # Remove video track title
            track["properties"]["track_name"] = ""
            video_tracks.append(track)
        elif track["type"] == "audio":
            audio_tracks.append(track)
        elif track["type"] == "subtitles":
            subtitle_tracks.append(track)

    processed_audio_tracks = []
    default_spa_audio_set = False
    default_audio_set = False

    # Check if this is a Chinese anime (only Chinese audio tracks)
    is_chinese_anime = False
    chinese_audio_count = 0
    total_audio_count = len(audio_tracks)

    for track in audio_tracks:
        lang = track["properties"].get("language", "")
        language_ietf = track["properties"].get("language_ietf", "")
        lang_code, _ = extract_regional_info(
            track["properties"].get("track_name", ""), language_ietf, lang
        )

        if lang == "chi" or lang_code.startswith("zh-"):
            chinese_audio_count += 1

    # If all audio tracks are Chinese, it's a Chinese anime
    if total_audio_count > 0 and chinese_audio_count == total_audio_count:
        is_chinese_anime = True

    # Process audio tracks with regional support and Chinese anime handling
    spanish_latin_found = False
    spanish_other_found = False
    chinese_default_set = False

    # First pass: Find and prioritize Spanish Latin America audio
    for track in audio_tracks:
        lang = track["properties"].get("language", "")
        language_ietf = track["properties"].get("language_ietf", "")
        title = track["properties"].get("track_name", "")

        # Extract regional info and special markers
        lang_code, display_name = extract_regional_info(title, language_ietf, lang)
        special_markers = extract_special_markers(title)

        # Check if this is Spanish Latin America
        is_spanish_latin = lang_code in [
            "es-419",
            "es-MX",
            "es-AR",
            "es-CL",
            "es-CO",
            "es-PE",
            "es-VE",
            "es-UY",
            "es-PY",
            "es-BO",
            "es-EC",
            "es-CR",
            "es-PA",
            "es-GT",
            "es-HN",
            "es-SV",
            "es-NI",
            "es-DO",
            "es-CU",
            "es-PR",
        ]

        if is_spanish_latin and not spanish_latin_found:
            # Update track properties
            track["properties"]["language_ietf"] = lang_code
            track["properties"]["track_name"] = display_name
            track["properties"]["default_track"] = True

            # Add special markers to track name
            for marker in special_markers:
                if marker.upper() not in track["properties"]["track_name"].upper():
                    track["properties"]["track_name"] += f" [{marker}]"

            processed_audio_tracks.append(track)
            default_spa_audio_set = True
            spanish_latin_found = True
            break

    # Second pass: Process other Spanish audio if no Latin America found
    if not spanish_latin_found:
        for track in audio_tracks:
            lang = track["properties"].get("language", "")
            language_ietf = track["properties"].get("language_ietf", "")
            title = track["properties"].get("track_name", "")

            # Extract regional info and special markers
            lang_code, display_name = extract_regional_info(title, language_ietf, lang)
            special_markers = extract_special_markers(title)

            # Check if this is Spanish (any variant)
            is_spanish = lang == "spa" or lang_code.startswith("es-")

            if is_spanish and not spanish_other_found:
                # Update track properties
                track["properties"]["language_ietf"] = lang_code
                track["properties"]["track_name"] = display_name
                track["properties"]["default_track"] = True

                # Add special markers to track name
                for marker in special_markers:
                    if marker.upper() not in track["properties"]["track_name"].upper():
                        track["properties"]["track_name"] += f" [{marker}]"

                processed_audio_tracks.append(track)
                default_spa_audio_set = True
                spanish_other_found = True
                break

    # Third pass: Process all other audio tracks (including Chinese anime handling)
    for track in audio_tracks:
        lang = track["properties"].get("language", "")
        language_ietf = track["properties"].get("language_ietf", "")
        title = track["properties"].get("track_name", "")

        # Extract regional info and special markers
        lang_code, display_name = extract_regional_info(title, language_ietf, lang)
        special_markers = extract_special_markers(title)

        # Skip if already processed as Spanish
        is_spanish = lang == "spa" or lang_code.startswith("es-")
        if is_spanish and (spanish_latin_found or spanish_other_found):
            continue

        # Update track properties
        track["properties"]["language_ietf"] = lang_code
        track["properties"]["track_name"] = display_name

        # Add special markers to track name
        for marker in special_markers:
            if marker.upper() not in track["properties"]["track_name"].upper():
                track["properties"]["track_name"] += f" [{marker}]"

        # Set default track based on language priority
        is_japanese = lang == "jpn" or lang_code == "ja-JP"
        is_chinese = lang == "chi" or lang_code.startswith("zh-")
        is_korean = lang == "kor" or lang_code == "ko-KR"
        is_english = lang == "eng" or lang_code.startswith("en-")

        # Special handling for Chinese anime - preserve all Chinese variants and set first as default
        if is_chinese_anime and is_chinese:
            if not chinese_default_set and not default_spa_audio_set:
                track["properties"]["default_track"] = True
                chinese_default_set = True
                default_audio_set = True
            else:
                track["properties"]["default_track"] = False
            processed_audio_tracks.append(track)
        # Regular priority: Japanese > Chinese > Korean > English > Others
        elif is_japanese and not default_spa_audio_set and not default_audio_set:
            track["properties"]["default_track"] = True
            default_audio_set = True
            processed_audio_tracks.append(track)
        elif (
            is_chinese
            and not default_spa_audio_set
            and not default_audio_set
            and not is_chinese_anime
        ):
            track["properties"]["default_track"] = True
            default_audio_set = True
            processed_audio_tracks.append(track)
        elif is_korean and not default_spa_audio_set and not default_audio_set:
            track["properties"]["default_track"] = True
            default_audio_set = True
            processed_audio_tracks.append(track)
        elif is_english and not default_spa_audio_set and not default_audio_set:
            track["properties"]["default_track"] = True
            default_audio_set = True
            processed_audio_tracks.append(track)
        else:
            track["properties"]["default_track"] = False
            processed_audio_tracks.append(track)

    # Process subtitle tracks with regional support
    processed_subtitle_tracks = []
    found_forced_subtitle = False
    found_latin_subtitles = False

    # First pass: Process all Spanish subtitles (prioritizing Latin American)
    for track in subtitle_tracks:
        lang = track["properties"].get("language", "")
        language_ietf = track["properties"].get("language_ietf", "")
        title = track["properties"].get("track_name", "")
        forced = track["properties"].get("forced_track", False)

        # Extract regional info and special markers
        lang_code, display_name = extract_regional_info(title, language_ietf, lang)
        special_markers = extract_special_markers(title)

        # Check if this is Spanish
        is_spanish = lang == "spa" or lang_code.startswith("es-")
        is_spanish_latin = lang_code in [
            "es-419",
            "es-MX",
            "es-AR",
            "es-CL",
            "es-CO",
            "es-PE",
            "es-VE",
            "es-UY",
            "es-PY",
            "es-BO",
            "es-EC",
            "es-CR",
            "es-PA",
            "es-GT",
            "es-HN",
            "es-SV",
            "es-NI",
            "es-DO",
            "es-CU",
            "es-PR",
        ]
        is_forced = (
            "forced" in title.lower()
            or "forzad" in title.lower()
            or forced
            or "Forced" in special_markers
            or title.strip().lower().endswith("signs")
        )

        if is_spanish:
            if is_spanish_latin:
                found_latin_subtitles = True

            # Update track properties
            track["properties"]["language_ietf"] = lang_code
            track["properties"]["track_name"] = display_name

            # Handle forced subtitles
            if is_forced:
                track["properties"]["track_name"] += " [Forced]"
                track["properties"]["forced_track"] = True
                if is_spanish_latin:
                    track["properties"]["default_track"] = True
                    found_forced_subtitle = True
                    processed_subtitle_tracks.insert(0, track)
                else:
                    track["properties"]["default_track"] = False
                    processed_subtitle_tracks.append(track)
            else:
                # Complete subtitles
                if is_spanish_latin:
                    # Set as default if there's no Spanish audio
                    track["properties"]["default_track"] = not default_spa_audio_set
                else:
                    # Don't set Spain Spanish as default if there's any Spanish audio
                    track["properties"]["default_track"] = False
                processed_subtitle_tracks.append(track)

            # Add other special markers
            for marker in special_markers:
                if (
                    marker != "Forced"
                    and marker.upper() not in track["properties"]["track_name"].upper()
                ):
                    track["properties"]["track_name"] += f" [{marker}]"

    # Second pass: Process English subtitles (preserve all regional variants)
    for track in subtitle_tracks:
        lang = track["properties"].get("language", "")
        language_ietf = track["properties"].get("language_ietf", "")
        title = track["properties"].get("track_name", "")
        forced = track["properties"].get("forced_track", False)

        # Extract regional info and special markers
        lang_code, display_name = extract_regional_info(title, language_ietf, lang)
        special_markers = extract_special_markers(title)

        # Check if this is English
        is_english = lang == "eng" or lang_code.startswith("en-")
        is_forced = (
            "forced" in title.lower()
            or "forzad" in title.lower()
            or forced
            or "Forced" in special_markers
            or title.strip().lower().endswith("signs")
        )

        if is_english:
            # Update track properties
            track["properties"]["language_ietf"] = lang_code
            track["properties"]["track_name"] = display_name

            # Handle forced subtitles
            if is_forced:
                track["properties"]["track_name"] += " [Forced]"
                track["properties"]["forced_track"] = True

            # Set as default only if no forced subtitles found, no Spanish audio, and no Latin American subtitles
            if (
                not found_forced_subtitle
                and not default_spa_audio_set
                and not found_latin_subtitles
            ):
                track["properties"]["default_track"] = True
            else:
                track["properties"]["default_track"] = False

            # Add special markers
            for marker in special_markers:
                if (
                    marker != "Forced"
                    and marker.upper() not in track["properties"]["track_name"].upper()
                ):
                    track["properties"]["track_name"] += f" [{marker}]"

            processed_subtitle_tracks.append(track)

    # Third pass: Process other language subtitles (remove non-Spanish/English subtitles)
    for track in subtitle_tracks:
        lang = track["properties"].get("language", "")
        language_ietf = track["properties"].get("language_ietf", "")
        title = track["properties"].get("track_name", "")
        forced = track["properties"].get("forced_track", False)

        # Extract regional info and special markers
        lang_code, display_name = extract_regional_info(title, language_ietf, lang)
        special_markers = extract_special_markers(title)

        # Skip if already processed (Spanish or English)
        is_spanish = lang == "spa" or lang_code.startswith("es-")
        is_english = lang == "eng" or lang_code.startswith("en-")

        # Only process non-Spanish and non-English subtitles to remove them
        # (keeping the original behavior of filtering out other languages)
        if not is_spanish and not is_english:
            # These tracks are effectively removed by not being added to processed_subtitle_tracks
            continue

    return video_tracks + processed_audio_tracks + processed_subtitle_tracks
