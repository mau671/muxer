package processor

// Metadata represents the JSON output from mkvmerge -J
type Metadata struct {
	Tracks []Track `json:"tracks"`
}

// Track represents a single track from the MKV file
type Track struct {
	ID         int             `json:"id"`
	Type       string          `json:"type"`
	Properties TrackProperties `json:"properties"`
}

// TrackProperties holds the metadata properties of a track
type TrackProperties struct {
	TrackName       string `json:"track_name,omitempty"`
	Language        string `json:"language,omitempty"`
	LanguageIETF    string `json:"language_ietf,omitempty"`
	DefaultTrack    bool   `json:"default_track,omitempty"`
	ForcedTrack     bool   `json:"forced_track,omitempty"`
	OriginalTrack   bool   `json:"original_track,omitempty"`
	HearingImpaired bool   `json:"hearing_impaired,omitempty"`
	VisualImpaired  bool   `json:"visual_impaired,omitempty"`
}
