package processor

import (
	"strings"
)

// ISO 639-1 (TMDB) to ISO 639-2 (MKV) mapping
var isoMap = map[string]string{
	"en": "eng", "ja": "jpn", "ko": "kor", "zh": "chi", "es": "spa",
	"fr": "fre", "de": "ger", "it": "ita", "pt": "por", "ru": "rus",
}

// matchLanguage checks if the track matches the TMDB original language
func matchLanguage(track Track, tmdbLang string) bool {
	if tmdbLang == "" {
		return false
	}
	
	// Check IETF (usually 2 letters like "ja" or "es-419")
	if strings.HasPrefix(strings.ToLower(track.Properties.LanguageIETF), tmdbLang) {
		return true
	}
	
	// Check 3-letter MKV legacy code
	if mkvLang, ok := isoMap[tmdbLang]; ok {
		if track.Properties.Language == mkvLang {
			return true
		}
	}
	return false
}

// ProcessTracks processes the tracks according to business rules.
func ProcessTracks(metadata Metadata, originalOnly bool, originalLanguage string) []Track {
	var videoTracks []Track
	var audioTracks []Track
	var subtitleTracks []Track

	for _, track := range metadata.Tracks {
		if track.Type == "video" {
			track.Properties.TrackName = "" // Remove video track title
			videoTracks = append(videoTracks, track)
		} else if track.Type == "audio" {
			audioTracks = append(audioTracks, track)
		} else if track.Type == "subtitles" {
			subtitleTracks = append(subtitleTracks, track)
		}
	}

	var processedAudioTracks []Track
	defaultSpaAudioSet := false
	defaultAudioSet := false

	// If originalOnly is active and we have an original language, pre-filter non-Spanish and non-original tracks
	var filteredAudioTracks []Track
	if originalOnly && originalLanguage != "" {
		for _, track := range audioTracks {
			lang := track.Properties.Language
			langIETF := track.Properties.LanguageIETF
			if langIETF == "" {
				langIETF = lang
			}

			// Keep if it's Spanish (any variant) OR if it matches original language
			if strings.HasPrefix(langIETF, "es") || lang == "spa" || matchLanguage(track, originalLanguage) {
				filteredAudioTracks = append(filteredAudioTracks, track)
			}
		}
		audioTracks = filteredAudioTracks

		var filteredSubtitleTracks []Track
		for _, track := range subtitleTracks {
			lang := track.Properties.Language
			langIETF := track.Properties.LanguageIETF
			if langIETF == "" {
				langIETF = lang
			}

			// Keep if it's Spanish (any variant) OR if it matches original language OR if it's English (as a safe fallback for subs)
			if strings.HasPrefix(langIETF, "es") || lang == "spa" || lang == "eng" || strings.HasPrefix(langIETF, "en") || matchLanguage(track, originalLanguage) {
				filteredSubtitleTracks = append(filteredSubtitleTracks, track)
			}
		}
		subtitleTracks = filteredSubtitleTracks
	}

	// First pass for audio: Latin American Spanish
	for _, track := range audioTracks {
		lang := track.Properties.LanguageIETF
		if lang == "" {
			lang = track.Properties.Language
		}
		title := strings.ToLower(track.Properties.TrackName)

		if lang == "es-419" || (strings.Contains(title, "lat") && lang != "hi-Latn" && lang != "sr-Latn") {
			track.Properties.TrackName = "Spanish (Latin America)"
			track.Properties.LanguageIETF = "es-419"
			track.Properties.DefaultTrack = true
			processedAudioTracks = append(processedAudioTracks, track)
			defaultSpaAudioSet = true
			break
		}
	}

	// Second pass for audio: Spain Spanish or generic Spanish
	if !defaultSpaAudioSet {
		for _, track := range audioTracks {
			lang := track.Properties.Language
			langIETF := track.Properties.LanguageIETF
			if langIETF == "" {
				langIETF = lang
			}
			title := strings.ToLower(track.Properties.TrackName)

			if lang == "spa" {
				if strings.Contains(title, "lat") || langIETF == "es-419" {
					track.Properties.TrackName = "Spanish (Latin America)"
					track.Properties.LanguageIETF = "es-419"
				} else {
					if langIETF == "es-ES" || langIETF == "es-724" || strings.Contains(title, "europ") {
						track.Properties.TrackName = "Spanish (Spain)"
						track.Properties.LanguageIETF = "es-ES"
					} else {
						track.Properties.TrackName = "Spanish"
					}
				}
				track.Properties.DefaultTrack = true
				processedAudioTracks = append(processedAudioTracks, track)
				defaultSpaAudioSet = true
				break
			}
		}
	}

	// Third pass for audio: Other languages
	for _, track := range audioTracks {
		lang := track.Properties.Language
		switch lang {
		case "jpn":
			track.Properties.TrackName = "Japanese"
			if !defaultSpaAudioSet {
				track.Properties.DefaultTrack = true
				defaultAudioSet = true
			} else {
				track.Properties.DefaultTrack = false
			}
			processedAudioTracks = append(processedAudioTracks, track)
		case "chi":
			track.Properties.LanguageIETF = "zh-CN"
			track.Properties.TrackName = "Chinese"
			if !defaultAudioSet && !defaultSpaAudioSet {
				track.Properties.DefaultTrack = true
				defaultAudioSet = true
			} else {
				track.Properties.DefaultTrack = false
			}
			processedAudioTracks = append(processedAudioTracks, track)
		case "kor":
			track.Properties.TrackName = "Korean"
			if !defaultSpaAudioSet && !defaultAudioSet {
				track.Properties.DefaultTrack = true
				defaultAudioSet = true
			} else {
				track.Properties.DefaultTrack = false
			}
			processedAudioTracks = append(processedAudioTracks, track)
		case "eng":
			track.Properties.TrackName = "English"
			if !defaultSpaAudioSet && !defaultAudioSet {
				track.Properties.DefaultTrack = true
				defaultAudioSet = true
			} else {
				track.Properties.DefaultTrack = false
			}
			processedAudioTracks = append(processedAudioTracks, track)
		}
	}

	var processedSubtitleTracks []Track
	foundForcedSubtitle := false
	foundLatinSubtitles := false

	// Subtitles pass 1: Latin American
	for _, track := range subtitleTracks {
		lang := track.Properties.LanguageIETF
		if lang == "" {
			lang = track.Properties.Language
		}
		title := strings.ToLower(track.Properties.TrackName)
		forced := track.Properties.ForcedTrack

		isLatinSubtitle := (lang == "es-419" || lang == "es-MX" || strings.Contains(title, "lat") || strings.Contains(title, "latin american")) && (lang != "hi-Latn" && lang != "sr-Latn")

		if isLatinSubtitle {
			foundLatinSubtitles = true
			if strings.Contains(title, "forced") || strings.Contains(title, "forzad") || strings.Contains(title, "signs") || forced {
				track.Properties.TrackName = "Spanish (Latin America) [Forced]"
				track.Properties.ForcedTrack = true
				track.Properties.DefaultTrack = true
				track.Properties.LanguageIETF = "es-419"
				if strings.Contains(title, "ao") {
					track.Properties.TrackName += " [AO]"
				}
				// Prepend
				processedSubtitleTracks = append([]Track{track}, processedSubtitleTracks...)
				foundForcedSubtitle = true
			} else {
				track.Properties.TrackName = "Spanish (Latin America)"
				track.Properties.LanguageIETF = "es-419"
				track.Properties.DefaultTrack = !defaultSpaAudioSet
				if strings.Contains(title, "ao") {
					track.Properties.TrackName += " [AO]"
				}
				if strings.Contains(title, "sdh") {
					track.Properties.TrackName += " [SDH]"
				}
				if strings.Contains(title, "cc") {
					track.Properties.TrackName += " [CC]"
				}
				if strings.Contains(title, "dub") {
					track.Properties.TrackName += " [Dubtitle]"
				}
				processedSubtitleTracks = append(processedSubtitleTracks, track)
			}
		}
	}

	// Subtitles pass 2: Spain/European and generic
	if !foundLatinSubtitles {
		for _, track := range subtitleTracks {
			lang := track.Properties.Language
			langIETF := track.Properties.LanguageIETF
			if langIETF == "" {
				langIETF = lang
			}
			title := strings.ToLower(track.Properties.TrackName)
			forced := track.Properties.ForcedTrack

			isLatinSubtitle := (langIETF == "es-419" || langIETF == "es-MX" || strings.Contains(title, "lat") || strings.Contains(title, "latin american")) && (lang != "hi-Latn" && lang != "sr-Latn")

			if lang == "spa" && !isLatinSubtitle {
				if langIETF == "es-ES" || langIETF == "es-724" || strings.Contains(title, "europ") {
					track.Properties.TrackName = "Spanish (Spain)"
					track.Properties.LanguageIETF = "es-ES"
				} else {
					track.Properties.TrackName = "Spanish"
				}
				track.Properties.DefaultTrack = false

				if strings.Contains(title, "forced") || strings.Contains(title, "forzad") || strings.Contains(title, "signs") || forced {
					track.Properties.TrackName += " [Forced]"
					track.Properties.ForcedTrack = true
				}
				if strings.Contains(title, "sdh") {
					track.Properties.TrackName += " [SDH]"
				}
				if strings.Contains(title, "cc") {
					track.Properties.TrackName += " [CC]"
				}
				if strings.Contains(title, "dub") {
					track.Properties.TrackName += " [Dubtitle]"
				}
				processedSubtitleTracks = append(processedSubtitleTracks, track)
			}
		}
	}

	// Subtitles pass 3: English
	for _, track := range subtitleTracks {
		lang := track.Properties.Language
		forced := track.Properties.ForcedTrack
		title := strings.ToLower(track.Properties.TrackName)

		if lang == "eng" {
			if strings.Contains(title, "forced") || strings.Contains(title, "forzad") || strings.Contains(title, "signs") || forced {
				track.Properties.TrackName = "English [Forced]"
				track.Properties.ForcedTrack = true
			} else {
				track.Properties.TrackName = "English"
			}

			if !foundForcedSubtitle && !defaultSpaAudioSet && !foundLatinSubtitles {
				track.Properties.DefaultTrack = true
			} else {
				track.Properties.DefaultTrack = false
			}

			if strings.Contains(title, "sdh") {
				track.Properties.TrackName += " [SDH]"
			}
			if strings.Contains(title, "cc") {
				track.Properties.TrackName += " [CC]"
			}
			if strings.Contains(title, "dub") {
				track.Properties.TrackName += " [Dubtitle]"
			}
			processedSubtitleTracks = append(processedSubtitleTracks, track)
		}
	}

	result := append(videoTracks, processedAudioTracks...)
	result = append(result, processedSubtitleTracks...)
	return result
}
