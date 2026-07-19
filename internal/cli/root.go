package cli

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
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

	absInDir, _ := filepath.Abs(inDir)
	absOutDir, _ := filepath.Abs(outDir)

	foundMkv := false
	err := filepath.WalkDir(inDir, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}

		absPath, _ := filepath.Abs(path)

		// Skip the output directory if it's nested inside the input directory (to avoid cyclic processing)
		if d.IsDir() && absPath == absOutDir && absPath != absInDir {
			return filepath.SkipDir
		}

		if !d.IsDir() && strings.HasSuffix(strings.ToLower(d.Name()), ".mkv") {
			// Skip already processed files if processing in-place
			if strings.HasSuffix(strings.ToLower(d.Name()), "_processed.mkv") {
				return nil
			}
			foundMkv = true

			// Create relative path for output
			relPath, err := filepath.Rel(inDir, path)
			if err != nil {
				return err
			}

			outPath := filepath.Join(outDir, strings.TrimSuffix(relPath, ".mkv")+"_processed.mkv")

			// Ensure target directory exists
			if err := os.MkdirAll(filepath.Dir(outPath), 0755); err != nil {
				return err
			}

			processSingleFile(path, outPath)
		}
		return nil
	})

	if err != nil {
		fmt.Printf("Error walking directory: %v\n", err)
		os.Exit(1)
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

			// Extract ID from full path, e.g., [tvdbid-12345] or [tmdbid-67890]
			idRegex := regexp.MustCompile(`\[(tvdbid-[0-9]+|tmdbid-[0-9]+)\]`)
			match := idRegex.FindString(in)
			
			if match != "" {
				// match is like "[tvdbid-12345]"
				idTag := match[1 : len(match)-1] // remove brackets
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
			} else {
				p.Send(ui.InfoMsg("No TMDB/TVDB ID found in path. Skipping original language detection."))
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
