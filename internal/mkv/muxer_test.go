package mkv

import (
	"reflect"
	"testing"

	"github.com/mau671/muxer/internal/processor"
)

func TestBuildCommand(t *testing.T) {
	tracks := []processor.Track{
		{
			ID:   0,
			Type: "video",
			Properties: processor.TrackProperties{
				TrackName:    "",
				Language:     "und",
				LanguageIETF: "",
				DefaultTrack: true,
			},
		},
		{
			ID:   1,
			Type: "audio",
			Properties: processor.TrackProperties{
				TrackName:     "Spanish (Latin America)",
				Language:      "spa",
				LanguageIETF:  "es-419",
				DefaultTrack:  true,
				OriginalTrack: true,
			},
		},
		{
			ID:   2,
			Type: "subtitles",
			Properties: processor.TrackProperties{
				TrackName:       "Spanish (Latin America) [Forced]",
				Language:        "spa",
				LanguageIETF:    "es-419",
				DefaultTrack:    true,
				ForcedTrack:     true,
				HearingImpaired: true,
			},
		},
	}

	expected := []string{
		"--priority", "highest",
		"--ui-language", "en_US",
		"-v",
		"-o", "output.mkv",
		"--language", "0:und", "--default-track", "0:yes", "--track-name", "0:",
		"--language", "1:es-419", "--default-track", "1:yes", "--track-name", "1:Spanish (Latin America)", "--original-flag", "1:yes",
		"--language", "2:es-419", "--default-track", "2:yes", "--forced-track", "2:yes", "--track-name", "2:Spanish (Latin America) [Forced]", "--hearing-impaired-flag", "2:yes",
		"--audio-tracks", "1",
		"--subtitle-tracks", "2",
		"--title", "",
		"--track-order", "0:0,0:1,0:2",
		"input.mkv",
	}

	result := BuildCommand("input.mkv", "output.mkv", tracks)

	if !reflect.DeepEqual(result, expected) {
		t.Errorf("BuildCommand output mismatch.\nExpected:\n%v\nGot:\n%v", expected, result)
	}
}
