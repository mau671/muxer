package ui

import (
	"fmt"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type ProgressMsg int
type InfoMsg string
type ErrorMsg struct{ Err error }
type DoneMsg struct{}

var (
	titleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#00ff00")).MarginBottom(1)
	infoStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#00d7ff"))
	barStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("#ff00d7"))
)

type Model struct {
	filename string
	progress int
	infoMsg  string
	err      error
	done     bool
}

func NewModel(filename string) Model {
	return Model{
		filename: filename,
		progress: 0,
		infoMsg:  "Starting...",
	}
}

func (m Model) Init() tea.Cmd {
	return nil
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.String() == "ctrl+c" || msg.String() == "q" {
			return m, tea.Quit
		}
	case ProgressMsg:
		m.progress = int(msg)
	case InfoMsg:
		m.infoMsg = string(msg)
	case ErrorMsg:
		m.err = msg.Err
		return m, tea.Quit
	case DoneMsg:
		m.done = true
		m.progress = 100
		return m, tea.Quit
	}
	return m, nil
}

func (m Model) View() string {
	if m.err != nil {
		return fmt.Sprintf("❌ Error: %v\n", m.err)
	}

	s := titleStyle.Render(fmt.Sprintf("🎬 Processing: %s", m.filename)) + "\n"

	// Progress bar
	width := 40
	filled := int((float64(m.progress) / 100.0) * float64(width))
	empty := width - filled

	bar := barStyle.Render(strings.Repeat("█", filled)) + strings.Repeat("░", empty)
	s += fmt.Sprintf("%s %3d%%\n\n", bar, m.progress)

	s += infoStyle.Render(fmt.Sprintf("ℹ️  %s", m.infoMsg)) + "\n"

	if m.done {
		s += "\n✅ Finished successfully!\n"
	} else {
		s += "\n(press q to quit)\n"
	}

	return s
}
