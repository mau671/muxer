package mkv

import (
	"os"
	"os/exec"

	"github.com/mau671/muxer/internal/config"
	"github.com/mau671/muxer/internal/downloader"
)

// FindMkvmerge looks for mkvmerge in PATH first, then in cache. If not found, it downloads it.
func FindMkvmerge() (string, error) {
	path, err := exec.LookPath("mkvmerge")
	if err == nil {
		return path, nil
	}

	cachedPath, err := config.GetMkvmergePath()
	if err != nil {
		return "", err
	}

	if _, err := os.Stat(cachedPath); err == nil {
		return cachedPath, nil
	}

	// Auto-download since it's not found
	err = downloader.DownloadMkvmerge()
	if err != nil {
		return "", err
	}

	return cachedPath, nil
}
