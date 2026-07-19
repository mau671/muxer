package ui

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/progress"
	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/mau671/muxer/internal/processor"
)

type ProgressMsg float64
type InfoMsg string
type ErrorMsg struct{ Err error }
type MetadataMsg struct {
	OutFilename string
	Metadata    processor.Metadata
	Processed   []processor.Track
}
type DoneMsg struct{}
type QuitAfterDelayMsg struct{}

var (
	titleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#00d7ff")).MarginBottom(1)
	infoStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#a8a8a8"))
	errorStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#ff0000")).Bold(true)
	doneStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#00ff00")).Bold(true)
	trackStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#ffff00")).MarginLeft(2)
)

type Model struct {
	filename    string
	outFilename string
	metadata    processor.Metadata
	processed   []processor.Track
	progressBar progress.Model
	spinner     spinner.Model
	progress    float64
	infoMsg     string
	err         error
	done        bool
	isMuxing    bool
}

func NewModel(filename string) Model {
	prog := progress.New(
		progress.WithDefaultGradient(),
		progress.WithWidth(50),
		progress.WithoutPercentage(),
	)

	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("205"))

	return Model{
		filename:    filename,
		progressBar: prog,
		spinner:     s,
		progress:    0,
		infoMsg:     "Initializing...",
		isMuxing:    false,
	}
}

func (m Model) Init() tea.Cmd {
	return m.spinner.Tick
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.String() == "ctrl+c" || msg.String() == "q" {
			return m, tea.Quit
		}
	case tea.WindowSizeMsg:
		m.progressBar.Width = msg.Width - 10
		if m.progressBar.Width > 80 {
			m.progressBar.Width = 80
		}
		return m, nil
	case ProgressMsg:
		m.isMuxing = true
		m.progress = float64(msg)
		cmd := m.progressBar.SetPercent(m.progress)
		return m, cmd
	case MetadataMsg:
		m.outFilename = msg.OutFilename
		m.metadata = msg.Metadata
		m.processed = msg.Processed
		return m, nil
	case InfoMsg:
		m.infoMsg = string(msg)
		return m, nil
	case ErrorMsg:
		m.err = msg.Err
		return m, tea.Quit
	case DoneMsg:
		m.done = true
		m.progress = 1.0
		cmd := m.progressBar.SetPercent(1.0)
		return m, tea.Sequence(cmd, func() tea.Msg {
			time.Sleep(time.Millisecond * 500)
			return QuitAfterDelayMsg{}
		})
	case QuitAfterDelayMsg:
		return m, tea.Quit
	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	case progress.FrameMsg:
		progressModel, cmd := m.progressBar.Update(msg)
		m.progressBar = progressModel.(progress.Model)
		return m, cmd
	}
	return m, nil
}

func (m Model) View() string {
	if m.err != nil {
		return errorStyle.Render(fmt.Sprintf("Error: %v", m.err)) + "\n"
	}

	var s strings.Builder

	s.WriteString(titleStyle.Render(fmt.Sprintf("Processing: %s", m.filename)))
	s.WriteString("\n")
	s.WriteString(infoStyle.Render(fmt.Sprintf("Output: %s", m.outFilename)))
	s.WriteString("\n\n")

	// Print Track Info
	if len(m.processed) > 0 {
		var videos, audios, subs int
		var audioDetails, subDetails []string

		for _, t := range m.processed {
			if t.Type == "video" {
				videos++
			} else if t.Type == "audio" {
				audios++
				tag := t.Properties.TrackName
				if t.Properties.DefaultTrack {
					tag += " (default)"
				}
				audioDetails = append(audioDetails, tag)
			} else if t.Type == "subtitles" {
				subs++
				tag := t.Properties.TrackName
				if t.Properties.DefaultTrack {
					tag += " (default)"
				}
				subDetails = append(subDetails, tag)
			}
		}

		s.WriteString(lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#ff00ff")).Render("Track Summary:"))
		s.WriteString("\n")
		s.WriteString(trackStyle.Render(fmt.Sprintf("Video: %d streams retained", videos)))
		s.WriteString("\n")
		s.WriteString(trackStyle.Render(fmt.Sprintf("Audio: %d streams -> %s", audios, strings.Join(audioDetails, ", "))))
		s.WriteString("\n")
		s.WriteString(trackStyle.Render(fmt.Sprintf("Subs:  %d streams -> %s", subs, strings.Join(subDetails, ", "))))
		s.WriteString("\n\n")
	}

	if m.isMuxing {
		s.WriteString(m.progressBar.View())
		s.WriteString(fmt.Sprintf(" %3.0f%%\n\n", m.progress*100))
	} else if !m.done {
		s.WriteString(fmt.Sprintf("%s Loading...\n\n", m.spinner.View()))
	}

	s.WriteString(infoStyle.Render(m.infoMsg))
	s.WriteString("\n")

	if m.done {
		s.WriteString("\n" + doneStyle.Render("Finished successfully!") + "\n")
	}

	return s.String()
}
