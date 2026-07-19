package cli

import (
	"context"
	"fmt"
	"os"
	"strings"

	"github.com/creativeprojects/go-selfupdate"
	"github.com/spf13/cobra"
)

var updateCmd = &cobra.Command{
	Use:   "update",
	Short: "Update the binary to the latest version",
	Run: func(cmd *cobra.Command, args []string) {
		cleanVersion := strings.TrimPrefix(Version, "v")
		if cleanVersion == "dev" {
			fmt.Println("Warning: You are running a development build. Automatic updates may not work accurately.")
		}

		fmt.Printf("Checking for updates for mau671/muxer (current version: %s)...\n", cleanVersion)

		updater, err := selfupdate.NewUpdater(selfupdate.Config{})
		if err != nil {
			fmt.Printf("Error initializing updater: %v\n", err)
			os.Exit(1)
		}

		latest, found, err := updater.DetectLatest(context.Background(), selfupdate.ParseSlug("mau671/muxer"))
		if err != nil {
			fmt.Printf("Error checking for updates: %v\n", err)
			os.Exit(1)
		}
		if !found {
			fmt.Println("No releases were found in the repository.")
			return
		}

		if latest.Version() == cleanVersion {
			fmt.Println("✅ You are already using the latest version!")
			return
		}

		fmt.Printf("🚀 Found new version: %s\n", latest.Version())
		fmt.Println("📥 Downloading and applying update...")

		exe, err := os.Executable()
		if err != nil {
			fmt.Printf("❌ Error locating executable: %v\n", err)
			os.Exit(1)
		}

		err = updater.UpdateTo(context.Background(), latest, exe)
		if err != nil {
			if strings.Contains(strings.ToLower(err.Error()), "permission denied") {
				fmt.Println("❌ Permission denied. The executable is likely located in a protected system directory.")
				fmt.Println("👉 Please try running the command with administrator privileges:")
				fmt.Println("   sudo muxer update")
			} else {
				fmt.Printf("❌ Error updating binary: %v\n", err)
			}
			os.Exit(1)
		}

		fmt.Printf("Successfully updated to %s!\n", latest.Version())
	},
}

func init() {
	rootCmd.AddCommand(updateCmd)
}
