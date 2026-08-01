package mkv

import (
	"bufio"
	"bytes"
	"fmt"
	"os/exec"
	"regexp"
	"strconv"
	"strings"

	"github.com/mau671/muxer/internal/processor"
)

var progressRegex = regexp.MustCompile(`Progress:\s*(\d+)%`)

// BuildCommand generates the arguments for mkvmerge.
func BuildCommand(inputPath, outputPath string, tracks []processor.Track) []string {
	args := []string{
		"--priority", "highest",
		"--ui-language", "en_US",
		"-v",
		"-o", outputPath,
	}

	var trackOrder []string
	var audioTracks []string
	var subtitleTracks []string

	for _, track := range tracks {
		trackID := fmt.Sprintf("%d", track.ID)
		
		lang := track.Properties.LanguageIETF
		if lang == "" {
			lang = track.Properties.Language
		}
		if lang == "" {
			lang = "und"
		}

		defaultFlag := "no"
		if track.Properties.DefaultTrack {
			defaultFlag = "yes"
		}

		if track.Type == "subtitles" {
			subtitleTracks = append(subtitleTracks, trackID)
		}
		if track.Type == "audio" {
			audioTracks = append(audioTracks, trackID)
		}

		args = append(args, "--language", trackID+":"+lang)
		args = append(args, "--default-track", trackID+":"+defaultFlag)

		if track.Type == "subtitles" {
			forcedFlag := "no"
			if track.Properties.ForcedTrack {
				forcedFlag = "yes"
			}
			args = append(args, "--forced-track", trackID+":"+forcedFlag)
		}

		args = append(args, "--track-name", trackID+":"+track.Properties.TrackName)

		if track.Properties.OriginalTrack {
			args = append(args, "--original-flag", trackID+":yes")
		}
		if track.Properties.HearingImpaired {
			args = append(args, "--hearing-impaired-flag", trackID+":yes")
		}
		if track.Properties.VisualImpaired {
			args = append(args, "--visual-impaired-flag", trackID+":yes")
		}

		trackOrder = append(trackOrder, "0:"+trackID)
	}

	if len(audioTracks) > 0 {
		args = append(args, "--audio-tracks", strings.Join(audioTracks, ","))
	}
	if len(subtitleTracks) > 0 {
		args = append(args, "--subtitle-tracks", strings.Join(subtitleTracks, ","))
	}

	args = append(args, "--title", "")
	args = append(args, "--track-order", strings.Join(trackOrder, ","))
	args = append(args, inputPath)

	return args
}

// RunMuxer executes mkvmerge and reports progress through a channel
func RunMuxer(binPath string, args []string, progressChan chan<- int, msgChan chan<- string) error {
	cmd := exec.Command(binPath, args...)
	
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}
	
	cmd.Stderr = cmd.Stdout // Merge stderr to stdout
	
	if err := cmd.Start(); err != nil {
		return err
	}
	
	var lastLines []string

	scanner := bufio.NewScanner(stdout)
	scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
		if atEOF && len(data) == 0 {
			return 0, nil, nil
		}
		if i := bytes.IndexAny(data, "\r\n"); i >= 0 {
			return i + 1, data[0:i], nil
		}
		if atEOF {
			return len(data), data, nil
		}
		return 0, nil, nil
	})

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}

		if len(lastLines) > 5 {
			lastLines = lastLines[1:]
		}
		lastLines = append(lastLines, line)

		if match := progressRegex.FindStringSubmatch(line); match != nil {
			percent, _ := strconv.Atoi(match[1])
			progressChan <- percent
		} else if strings.Contains(line, "has been opened for writing") {
			msgChan <- "Output file opened for writing"
		} else if strings.Contains(line, "The cue entries") {
			msgChan <- "Writing cue records (index)..."
		} else if strings.Contains(line, "Multiplexing took") {
			msgChan <- line
		}
	}
	
	err = cmd.Wait()
	if err != nil {
		if len(lastLines) > 0 {
			return fmt.Errorf("mkvmerge failed: %s", strings.Join(lastLines, " | "))
		}
		return err
	}
	return nil
}
