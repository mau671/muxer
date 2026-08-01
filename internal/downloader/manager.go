package downloader

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"runtime"

	"github.com/mau671/muxer/internal/config"
	"github.com/mholt/archiver/v3"
)

// DownloadMkvmerge downloads and extracts the static binary
func DownloadMkvmerge() error {
	var url string

	var ext string
	if runtime.GOOS == "windows" {
		if runtime.GOARCH == "arm64" {
			return fmt.Errorf("auto-download not supported for Windows ARM64. Please install MKVToolNix manually")
		}
		url = "https://github.com/Jesseatgao/MKVToolNix-static-builds/releases/download/v58.0.0-mingw-w64-posixv1.8el9/mkvtoolnix-x86_64-win.zip"
		ext = "*.zip"
	} else if runtime.GOOS == "linux" {
		if runtime.GOARCH == "arm64" || runtime.GOARCH == "aarch64" {
			return fmt.Errorf("auto-download not supported for Linux ARM64 (like Oracle Cloud). Please run: sudo apt install mkvtoolnix")
		}
		url = "https://github.com/Jesseatgao/MKVToolNix-static-builds/releases/download/v58.0.0-mingw-w64-posixv1.8el9/mkvtoolnix-x86_64-linux.tar.xz"
		ext = "*.tar.xz"
	} else {
		return fmt.Errorf("auto-download not supported for %s %s. Please install MKVToolNix manually", runtime.GOOS, runtime.GOARCH)
	}

	binDir, err := config.GetBinDir()
	if err != nil {
		return err
	}

	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return fmt.Errorf("bad status: %s", resp.Status)
	}

	tmpFile, err := os.CreateTemp(binDir, "mkvtoolnix-"+ext)
	if err != nil {
		return err
	}
	defer os.Remove(tmpFile.Name())

	_, err = io.Copy(tmpFile, resp.Body)
	tmpFile.Close()
	if err != nil {
		return err
	}

	binPath, _ := config.GetMkvmergePath()
	err = extractBinary(tmpFile.Name(), binPath)
	if err != nil {
		return err
	}

	return os.Chmod(binPath, 0755)
}

func extractBinary(archivePath, targetBinPath string) error {
	targetName := "mkvmerge"
	if runtime.GOOS == "windows" {
		targetName = "mkvmerge.exe"
	}

	var found bool

	err := archiver.Walk(archivePath, func(f archiver.File) error {
		if found {
			return nil
		}

		if !f.IsDir() && filepath.Base(f.Name()) == targetName {
			found = true

			outFile, err := os.Create(targetBinPath)
			if err != nil {
				return err
			}
			defer outFile.Close()

			_, err = io.Copy(outFile, f)
			if err != nil {
				return err
			}
		}
		return nil
	})

	if err != nil {
		return err
	}

	if !found {
		return fmt.Errorf("binary %s not found in archive", targetName)
	}

	return nil
}
