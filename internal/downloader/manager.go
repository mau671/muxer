package downloader

import (
	"archive/zip"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/mau671/muxer/internal/config"
)

// DownloadMkvmerge downloads and extracts the static binary
func DownloadMkvmerge() error {
	var url string
	var isZip bool

	// Using the static builds from Jesseatgao for demonstration
	if runtime.GOOS == "windows" {
		url = "https://github.com/Jesseatgao/MKVToolNix-static-builds/releases/download/v58.0.0-mingw-w64-posixv1.8el9/mkvtoolnix-x86_64-win.zip"
		isZip = true
	} else if runtime.GOOS == "linux" {
		url = "https://github.com/Jesseatgao/MKVToolNix-static-builds/releases/download/v58.0.0-mingw-w64-posixv1.8el9/mkvtoolnix-x86_64-linux.tar.xz"
		isZip = false
	} else {
		return fmt.Errorf("auto-download not supported for %s", runtime.GOOS)
	}

	cacheDir, err := config.GetCacheDir()
	if err != nil {
		return err
	}

	fmt.Printf("📥 Downloading mkvmerge for %s...\n", runtime.GOOS)
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return fmt.Errorf("bad status: %s", resp.Status)
	}

	tmpFile, err := os.CreateTemp(cacheDir, "mkvtoolnix-*")
	if err != nil {
		return err
	}
	defer os.Remove(tmpFile.Name())

	_, err = io.Copy(tmpFile, resp.Body)
	tmpFile.Close()
	if err != nil {
		return err
	}

	fmt.Println("📦 Extracting binary...")
	binPath, _ := config.GetMkvmergePath()

	if isZip {
		err = extractZip(tmpFile.Name(), cacheDir, binPath)
	} else {
		err = extractTarXz(tmpFile.Name(), cacheDir, binPath)
	}

	if err != nil {
		return err
	}

	return os.Chmod(binPath, 0755)
}

func extractZip(zipPath, destDir, targetBinPath string) error {
	r, err := zip.OpenReader(zipPath)
	if err != nil {
		return err
	}
	defer r.Close()

	for _, f := range r.File {
		if strings.HasSuffix(f.Name, "mkvmerge.exe") {
			rc, err := f.Open()
			if err != nil {
				return err
			}
			defer rc.Close()

			outFile, err := os.Create(targetBinPath)
			if err != nil {
				return err
			}
			defer outFile.Close()

			_, err = io.Copy(outFile, rc)
			return err
		}
	}
	return fmt.Errorf("mkvmerge.exe not found in zip")
}

func extractTarXz(tarPath, destDir, targetBinPath string) error {
	// Use system tar for .xz as Go stdlib doesn't support LZMA/XZ
	cmd := exec.Command("tar", "-xf", tarPath, "-C", destDir)
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("tar extraction failed: %w", err)
	}
	
	// Find mkvmerge in the extracted directory
	var foundPath string
	filepath.Walk(destDir, func(path string, info os.FileInfo, err error) error {
		if !info.IsDir() && filepath.Base(path) == "mkvmerge" {
			foundPath = path
		}
		return nil
	})

	if foundPath == "" {
		return fmt.Errorf("mkvmerge not found after extraction")
	}

	// Move to target path
	if foundPath != targetBinPath {
		if err := os.Rename(foundPath, targetBinPath); err != nil {
			return err
		}
	}
	return nil
}
