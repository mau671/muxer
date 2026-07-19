package cli

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/spf13/cobra"
	"github.com/mau671/muxer/internal/mkv"
	"github.com/mau671/muxer/internal/processor"
	"github.com/mau671/muxer/internal/ui"
)

var rootCmd = &cobra.Command{
	Use:   "muxer",
	Short: "An MKV file processor with automatic track naming",
	Run:   runMuxer,
}

var (
	inputPath   string
	outputPath  string
	deleteAfter bool
)

func init() {
	rootCmd.Flags().StringVarP(&inputPath, "input", "i", "", "Input file or directory (required)")
	rootCmd.Flags().StringVarP(&outputPath, "output", "o", "", "Output file or directory (optional)")
	rootCmd.Flags().BoolVar(&deleteAfter, "delete-after", false, "Delete source files after processing")
	rootCmd.MarkFlagRequired("input")
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func runMuxer(cmd *cobra.Command, args []string) {
	info, err := os.Stat(inputPath)
	if err != nil {
		fmt.Printf("Error: Input path does not exist: %v\n", err)
		os.Exit(1)
	}

	if info.IsDir() {
		fmt.Println("Directory processing is not fully implemented yet, processing single file...")
	} else {
		processSingleFile(inputPath, outputPath)
	}
}

func processSingleFile(in, out string) {
	if out == "" {
		ext := filepath.Ext(in)
		base := strings.TrimSuffix(in, ext)
		out = base + "_processed" + ext
	}

	p := tea.NewProgram(ui.NewModel(filepath.Base(in)))

	go func() {
		p.Send(ui.InfoMsg("Looking for mkvmerge..."))
		binPath, err := mkv.FindMkvmerge()
		if err != nil {
			p.Send(ui.ErrorMsg{Err: fmt.Errorf("mkvmerge not found and failed to download: %v", err)})
			return
		}

		p.Send(ui.InfoMsg("Reading metadata..."))
		metadata, err := mkv.GetMetadata(binPath, in)
		if err != nil {
			p.Send(ui.ErrorMsg{Err: fmt.Errorf("error reading metadata: %v", err)})
			return
		}

		processedTracks := processor.ProcessTracks(metadata)
		mkvArgs := mkv.BuildCommand(in, out, processedTracks)

		progressChan := make(chan int)
		msgChan := make(chan string)

		go func() {
			for {
				select {
				case prog, ok := <-progressChan:
					if !ok {
						progressChan = nil
					} else {
						p.Send(ui.ProgressMsg(float64(prog) / 100.0))
					}
				case msg, ok := <-msgChan:
					if !ok {
						msgChan = nil
					} else {
						p.Send(ui.InfoMsg(msg))
					}
				}
				if progressChan == nil && msgChan == nil {
					break
				}
			}
		}()

		err = mkv.RunMuxer(binPath, mkvArgs, progressChan, msgChan)
		close(progressChan)
		close(msgChan)

		if err != nil {
			p.Send(ui.ErrorMsg{Err: err})
			return
		}

		p.Send(ui.DoneMsg{})
	}()

	if _, err := p.Run(); err != nil {
		fmt.Printf("UI Error: %v\n", err)
		os.Exit(1)
	}

	if deleteAfter {
		os.Remove(in)
	}
}
