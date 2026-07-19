package processor

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

var httpClient = &http.Client{Timeout: 10 * time.Second}

type TMDBClient struct {
	apiKey string
	cache  *APICache
}

func NewTMDBClient(apiKey string) (*TMDBClient, error) {
	cache, err := NewAPICache()
	if err != nil {
		return nil, err
	}
	return &TMDBClient{
		apiKey: apiKey,
		cache:  cache,
	}, nil
}

// GetOriginalLanguage takes an identifier like "tvdbid-12345" or "tmdbid-6789"
// and returns the 2-letter ISO 639-1 language code (e.g., "en", "ja", "ko").
func (c *TMDBClient) GetOriginalLanguage(identifier string) (string, error) {
	if c.apiKey == "" {
		return "", fmt.Errorf("TMDB_API_KEY is not set. Cannot fetch metadata")
	}

	// Check cache
	if lang, found := c.cache.Get(identifier); found {
		return lang, nil
	}

	var lang string
	var err error

	// Parse identifier
	var source string
	var id string
	if len(identifier) > 7 && identifier[:7] == "tvdbid-" {
		source = "tvdb_id"
		id = identifier[7:]
	} else if len(identifier) > 7 && identifier[:7] == "tmdbid-" {
		source = "tmdb"
		id = identifier[7:]
	} else {
		return "", fmt.Errorf("unknown identifier format: %s", identifier)
	}

	if source == "tvdb_id" {
		lang, err = c.findLanguageByExternalID(id, source)
	} else {
		// Native TMDB ID: We don't know if it's TV or Movie, so we try TV first, then Movie
		lang, err = c.getLanguageByType(id, "tv")
		if err != nil {
			lang, err = c.getLanguageByType(id, "movie")
		}
	}

	if err != nil {
		return "", err
	}
	if lang == "" {
		return "", fmt.Errorf("original_language not found in TMDB response")
	}

	// Save to cache
	c.cache.Set(identifier, lang)
	return lang, nil
}

func (c *TMDBClient) findLanguageByExternalID(id, source string) (string, error) {
	url := fmt.Sprintf("https://api.themoviedb.org/3/find/%s?external_source=%s", id, source)
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Add("Authorization", "Bearer "+c.apiKey)
	req.Header.Add("accept", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("TMDB API error: status %d", resp.StatusCode)
	}

	var result struct {
		MovieResults []struct {
			OriginalLanguage string `json:"original_language"`
		} `json:"movie_results"`
		TvResults []struct {
			OriginalLanguage string `json:"original_language"`
		} `json:"tv_results"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	if len(result.TvResults) > 0 {
		return result.TvResults[0].OriginalLanguage, nil
	}
	if len(result.MovieResults) > 0 {
		return result.MovieResults[0].OriginalLanguage, nil
	}

	return "", fmt.Errorf("no results found for external ID %s", id)
}

func (c *TMDBClient) getLanguageByType(id, mediaType string) (string, error) {
	url := fmt.Sprintf("https://api.themoviedb.org/3/%s/%s", mediaType, id)
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Add("Authorization", "Bearer "+c.apiKey)
	req.Header.Add("accept", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("TMDB API error: status %d", resp.StatusCode)
	}

	var result struct {
		OriginalLanguage string `json:"original_language"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	return result.OriginalLanguage, nil
}
