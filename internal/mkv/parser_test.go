package mkv

import (
	"encoding/json"
	"testing"

	"github.com/mau671/muxer/internal/processor"
)

func TestMetadataParsing(t *testing.T) {
	mockJSON := `{
		"tracks": [
			{
				"id": 0,
				"type": "video",
				"properties": {
					"track_name": "Test Video",
					"language": "und"
				}
			},
			{
				"id": 1,
				"type": "audio",
				"properties": {
					"language": "spa",
					"language_ietf": "es-419",
					"default_track": true
				}
			}
		]
	}`

	var metadata processor.Metadata
	err := json.Unmarshal([]byte(mockJSON), &metadata)
	if err != nil {
		t.Fatalf("Failed to parse JSON: %v", err)
	}

	if len(metadata.Tracks) != 2 {
		t.Fatalf("Expected 2 tracks, got %d", len(metadata.Tracks))
	}

	if metadata.Tracks[1].Properties.LanguageIETF != "es-419" {
		t.Errorf("Expected language_ietf to be es-419")
	}
}
