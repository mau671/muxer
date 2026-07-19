package processor

import (
	"testing"
)

func TestProcessTracks_LatinAmericanSpanish(t *testing.T) {
	metadata := Metadata{
		Tracks: []Track{
			{ID: 0, Type: "video", Properties: TrackProperties{TrackName: "Video"}},
			{ID: 1, Type: "audio", Properties: TrackProperties{Language: "spa", LanguageIETF: "es-419"}},
			{ID: 2, Type: "subtitles", Properties: TrackProperties{TrackName: "Forced", LanguageIETF: "es-419", ForcedTrack: true}},
		},
	}
	res := ProcessTracks(metadata)
	
	if res[1].Properties.TrackName != "Spanish (Latin America)" || !res[1].Properties.DefaultTrack {
		t.Errorf("Audio es-419 should be Latin America and default")
	}
	if res[2].Properties.TrackName != "Spanish (Latin America) [Forced]" || !res[2].Properties.ForcedTrack {
		t.Errorf("Subtitle forced logic failed")
	}
}

func TestProcessTracks_SpainSpanishFallback(t *testing.T) {
	metadata := Metadata{
		Tracks: []Track{
			{ID: 1, Type: "audio", Properties: TrackProperties{Language: "spa", LanguageIETF: "es-ES"}},
			{ID: 2, Type: "subtitles", Properties: TrackProperties{Language: "spa", LanguageIETF: "es-ES", ForcedTrack: true}},
		},
	}
	res := ProcessTracks(metadata)
	
	if res[0].Properties.TrackName != "Spanish (Spain)" || !res[0].Properties.DefaultTrack {
		t.Errorf("Audio es-ES should be Spain and default")
	}
	if res[1].Properties.TrackName != "Spanish (Spain) [Forced]" || !res[1].Properties.ForcedTrack {
		t.Errorf("Subtitle es-ES forced logic failed")
	}
}

func TestProcessTracks_EnglishFallback(t *testing.T) {
	metadata := Metadata{
		Tracks: []Track{
			{ID: 1, Type: "audio", Properties: TrackProperties{Language: "eng"}},
			{ID: 2, Type: "subtitles", Properties: TrackProperties{Language: "eng"}},
		},
	}
	res := ProcessTracks(metadata)
	
	if res[0].Properties.TrackName != "English" || !res[0].Properties.DefaultTrack {
		t.Errorf("Audio eng should be default if no spanish")
	}
	if res[1].Properties.TrackName != "English" || !res[1].Properties.DefaultTrack {
		t.Errorf("Subtitle eng should be default if no forced/spanish")
	}
}

func TestProcessTracks_JapaneseAudio(t *testing.T) {
	metadata := Metadata{
		Tracks: []Track{
			{ID: 1, Type: "audio", Properties: TrackProperties{Language: "jpn"}},
			{ID: 2, Type: "subtitles", Properties: TrackProperties{Language: "eng", TrackName: "Signs", ForcedTrack: true}},
		},
	}
	res := ProcessTracks(metadata)
	
	if res[0].Properties.TrackName != "Japanese" || !res[0].Properties.DefaultTrack {
		t.Errorf("Japanese should be default if no spanish")
	}
	if res[1].Properties.TrackName != "English [Forced]" || !res[1].Properties.ForcedTrack {
		t.Errorf("English forced subtitle handling failed")
	}
}

func TestProcessTracks_MultipleAudioPriorities(t *testing.T) {
	metadata := Metadata{
		Tracks: []Track{
			{ID: 1, Type: "audio", Properties: TrackProperties{Language: "jpn"}},
			{ID: 2, Type: "audio", Properties: TrackProperties{Language: "spa", LanguageIETF: "es-419"}},
			{ID: 3, Type: "audio", Properties: TrackProperties{Language: "eng"}},
		},
	}
	res := ProcessTracks(metadata)
	
	// Track 1 should be Latin American (moved to first matched loop)
	if res[0].Properties.TrackName != "Spanish (Latin America)" || !res[0].Properties.DefaultTrack {
		t.Errorf("es-419 should take priority and be default")
	}
	
	// Track 2 is Japanese
	if res[1].Properties.TrackName != "Japanese" || res[1].Properties.DefaultTrack {
		t.Errorf("Japanese should NOT be default when es-419 is present")
	}
	
	// Track 3 is English
	if res[2].Properties.TrackName != "English" || res[2].Properties.DefaultTrack {
		t.Errorf("English should NOT be default when es-419 is present")
	}
}
