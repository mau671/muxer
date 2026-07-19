package config

import (
	"os"
	"path/filepath"
	"runtime"
)

// AppName is the name used for cache directories.
const AppName = "muxer"

// GetCacheDir returns the directory where the mkvmerge binary should be cached.
func GetCacheDir() (string, error) {
	cacheDir, err := os.UserCacheDir()
	if err != nil {
		// Fallback to home dir if UserCacheDir is not available
		homeDir, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		if runtime.GOOS == "windows" {
			cacheDir = filepath.Join(homeDir, "AppData", "Local")
		} else {
			cacheDir = filepath.Join(homeDir, ".cache")
		}
	}
	
	appCacheDir := filepath.Join(cacheDir, AppName, "bin")
	if err := os.MkdirAll(appCacheDir, 0755); err != nil {
		return "", err
	}
	return appCacheDir, nil
}

// GetMkvmergePath returns the expected path to the cached mkvmerge binary.
func GetMkvmergePath() (string, error) {
	dir, err := GetCacheDir()
	if err != nil {
		return "", err
	}
	
	binName := "mkvmerge"
	if runtime.GOOS == "windows" {
		binName += ".exe"
	}
	
	return filepath.Join(dir, binName), nil
}
