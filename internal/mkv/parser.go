package mkv

import (
	"encoding/json"
	"fmt"
	"os/exec"

	"github.com/mau671/muxer/internal/processor"
)

// GetMetadata runs mkvmerge -J on the file and parses the result
func GetMetadata(binPath, filePath string) (processor.Metadata, error) {
	cmd := exec.Command(binPath, "--identify", filePath, "--identification-format", "json")
	output, err := cmd.Output()
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			return processor.Metadata{}, fmt.Errorf("mkvmerge failed (exit %d): %s", exitErr.ExitCode(), string(exitErr.Stderr))
		}
		return processor.Metadata{}, err
	}

	var metadata processor.Metadata
	err = json.Unmarshal(output, &metadata)
	if err != nil {
		return processor.Metadata{}, err
	}

	return metadata, nil
}
