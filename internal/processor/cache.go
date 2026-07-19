package processor

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sync"

	"github.com/mau671/muxer/internal/config"
)

type APICache struct {
	mu    sync.RWMutex
	path  string
	Data  map[string]string `json:"data"` // maps "tvdbid-12345" or "tmdbid-67890" to "ja" (original language)
}

func NewAPICache() (*APICache, error) {
	cacheDir, err := config.GetCacheDir()
	if err != nil {
		return nil, err
	}

	cacheFile := filepath.Join(cacheDir, "api_cache.json")
	
	cache := &APICache{
		path: cacheFile,
		Data: make(map[string]string),
	}

	cache.load()
	return cache, nil
}

func (c *APICache) load() {
	c.mu.Lock()
	defer c.mu.Unlock()

	b, err := os.ReadFile(c.path)
	if err == nil {
		json.Unmarshal(b, &c.Data)
	}
}

func (c *APICache) save() error {
	b, err := json.MarshalIndent(c.Data, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(c.path, b, 0644)
}

func (c *APICache) Get(key string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	val, ok := c.Data[key]
	return val, ok
}

func (c *APICache) Set(key, value string) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.Data[key] = value
	return c.save()
}
