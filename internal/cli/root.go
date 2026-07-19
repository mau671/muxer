package cli

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/joho/godotenv"
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
	originalOnly bool
	Version      = "dev"
)

func init() {
	rootCmd.Flags().StringVarP(&inputPath, "input", "i", "", "Input file or directory (required)")
	rootCmd.Flags().StringVarP(&outputPath, "output", "o", "", "Output file or directory (optional)")
	rootCmd.Flags().BoolVar(&deleteAfter, "delete-after", false, "Delete source files after processing")
	rootCmd.Flags().BoolVar(&originalOnly, "original-only", false, "Keep only original language and Spanish tracks (requires TMDB_API_KEY env var)")
	rootCmd.Version = strings.TrimPrefix(Version, "v") // Remove "v" if present
	rootCmd.SetVersionTemplate("{{printf \"%s\\n\" .Version}}")
	rootCmd.MarkFlagRequired("input")
}

func Execute() {
	// Intentar cargar variables desde .env (opcional)
	_ = godotenv.Load()

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
		processDirectory(inputPath, outputPath)
	} else {
		processSingleFile(inputPath, outputPath)
	}
}

func processDirectory(inDir, outDir string) {
	if outDir == "" {
		outDir = inDir
	}
	
	if err := os.MkdirAll(outDir, 0755); err != nil {
		fmt.Printf("Error creating output directory: %v\n", err)
		os.Exit(1)
	}

	entries, err := os.ReadDir(inDir)
	if err != nil {
		fmt.Printf("Error reading directory: %v\n", err)
		os.Exit(1)
	}

	foundMkv := false
	for _, entry := range entries {
		if !entry.IsDir() && strings.HasSuffix(strings.ToLower(entry.Name()), ".mkv") {
			foundMkv = true
			inPath := filepath.Join(inDir, entry.Name())
			outPath := filepath.Join(outDir, strings.TrimSuffix(entry.Name(), ".mkv")+"_processed.mkv")
			processSingleFile(inPath, outPath)
		}
	}

	if !foundMkv {
		fmt.Println("No MKV files found in directory.")
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

		originalLang := ""
		if originalOnly {
			apiKey := os.Getenv("TMDB_API_KEY")
			if apiKey == "" {
				p.Send(ui.ErrorMsg{Err: fmt.Errorf("TMDB_API_KEY environment variable is missing")})
				return
			}

			// Extract ID from filename, e.g., [tvdbid-12345] or [tmdbid-67890]
			filename := filepath.Base(in)
			startIdx := strings.Index(filename, "[")
			endIdx := strings.Index(filename, "]")
			
			if startIdx != -1 && endIdx != -1 && endIdx > startIdx {
				idTag := filename[startIdx+1 : endIdx]
				if strings.HasPrefix(idTag, "tvdbid-") || strings.HasPrefix(idTag, "tmdbid-") {
					p.Send(ui.InfoMsg(fmt.Sprintf("Querying TMDB for %s...", idTag)))
					
					tmdbClient, err := processor.NewTMDBClient(apiKey)
					if err == nil {
						lang, err := tmdbClient.GetOriginalLanguage(idTag)
						if err == nil {
							originalLang = lang
							p.Send(ui.InfoMsg(fmt.Sprintf("Detected Original Language: %s", lang)))
						} else {
							p.Send(ui.InfoMsg(fmt.Sprintf("Warning: API failed: %v", err)))
						}
					}
				}
			}
		}

		processedTracks := processor.ProcessTracks(metadata, originalOnly, originalLang)
		
		p.Send(ui.MetadataMsg{
			OutFilename: out,
			Metadata:    metadata,
			Processed:   processedTracks,
		})

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
