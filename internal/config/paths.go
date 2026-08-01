package config

import (
	"io"
	"os"
	"path/filepath"
	"runtime"
)

// AppName is the name used for data directories.
const AppName = "muxer"

// GetDataDir returns the XDG data directory for muxer (~/.local/share/muxer on Linux/macOS,
// %LOCALAPPDATA%\muxer on Windows). This is the canonical location for all persistent app
// data: downloaded binaries, TMDB cache, etc.
func GetDataDir() (string, error) {
	var base string

	// Respect XDG_DATA_HOME if explicitly set
	if xdg := os.Getenv("XDG_DATA_HOME"); xdg != "" {
		base = xdg
	} else {
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		if runtime.GOOS == "windows" {
			// Use LOCALAPPDATA if available, fall back to AppData\Local
			if local := os.Getenv("LOCALAPPDATA"); local != "" {
				base = local
			} else {
				base = filepath.Join(home, "AppData", "Local")
			}
		} else {
			base = filepath.Join(home, ".local", "share")
		}
	}

	dir := filepath.Join(base, AppName)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return "", err
	}
	return dir, nil
}

// GetBinDir returns the directory where muxer stores downloaded binaries
// (~/.local/share/muxer/bin on Linux/macOS).
func GetBinDir() (string, error) {
	data, err := GetDataDir()
	if err != nil {
		return "", err
	}
	dir := filepath.Join(data, "bin")
	if err := os.MkdirAll(dir, 0755); err != nil {
		return "", err
	}
	return dir, nil
}

// GetMkvmergePath returns the expected path to the mkvmerge binary managed by muxer.
func GetMkvmergePath() (string, error) {
	dir, err := GetBinDir()
	if err != nil {
		return "", err
	}
	binName := "mkvmerge"
	if runtime.GOOS == "windows" {
		binName += ".exe"
	}
	return filepath.Join(dir, binName), nil
}

// legacyBinDir returns the old cache directory used before the XDG reorganization
// (~/.cache/muxer/bin). Used exclusively for migration.
func legacyBinDir() (string, error) {
	cacheDir, err := os.UserCacheDir()
	if err != nil {
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		if runtime.GOOS == "windows" {
			cacheDir = filepath.Join(home, "AppData", "Local")
		} else {
			cacheDir = filepath.Join(home, ".cache")
		}
	}
	return filepath.Join(cacheDir, AppName, "bin"), nil
}

// Migrate moves files from the legacy ~/.cache/muxer/bin/ layout to the new
// ~/.local/share/muxer/ layout. It is safe to call on every startup — it
// only acts when old files exist and the new location is not already populated.
// After migration it attempts to remove the now-empty legacy directories.
func Migrate() {
	oldDir, err := legacyBinDir()
	if err != nil {
		return
	}

	binName := "mkvmerge"
	if runtime.GOOS == "windows" {
		binName += ".exe"
	}

	// ── mkvmerge binary ──────────────────────────────────────────────────────
	oldBin := filepath.Join(oldDir, binName)
	if _, err := os.Stat(oldBin); err == nil {
		if newBin, err := GetMkvmergePath(); err == nil {
			if _, err := os.Stat(newBin); os.IsNotExist(err) {
				// Best-effort: try rename first (same filesystem), then copy+delete
				if os.Rename(oldBin, newBin) != nil {
					copyFile(oldBin, newBin)
					os.Remove(oldBin)
				}
			}
		}
	}

	// ── api_cache.json → tmdb_cache.json ─────────────────────────────────────
	oldCache := filepath.Join(oldDir, "api_cache.json")
	if _, err := os.Stat(oldCache); err == nil {
		if dataDir, err := GetDataDir(); err == nil {
			newCache := filepath.Join(dataDir, "tmdb_cache.json")
			if _, err := os.Stat(newCache); os.IsNotExist(err) {
				if os.Rename(oldCache, newCache) != nil {
					copyFile(oldCache, newCache)
					os.Remove(oldCache)
				}
			}
		}
	}

	// ── Clean up empty legacy directories (no-op if still populated) ─────────
	os.Remove(oldDir)                    // ~/.cache/muxer/bin  — only if empty
	os.Remove(filepath.Dir(oldDir))      // ~/.cache/muxer      — only if empty
}

// copyFile copies src to dst. Used as a fallback when os.Rename fails across
// filesystem boundaries (e.g. /home and /tmp on different mounts).
func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()

	info, err := in.Stat()
	if err != nil {
		return err
	}

	out, err := os.OpenFile(dst, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, info.Mode())
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, in)
	return err
}
