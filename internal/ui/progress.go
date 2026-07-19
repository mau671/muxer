package ui

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/progress"
	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type ProgressMsg float64
type InfoMsg string
type ErrorMsg struct{ Err error }
type DoneMsg struct{}

var (
	titleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#00d7ff")).MarginBottom(1)
	infoStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#a8a8a8"))
	errorStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#ff0000")).Bold(true)
	doneStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#00ff00")).Bold(true)
)

type Model struct {
	filename    string
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
		return m, tea.Sequence(cmd, tea.Tick(time.Millisecond*500, func(t time.Time) tea.Msg { return tea.Quit }))
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
	s.WriteString("\n\n")

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
	} else {
		s.WriteString(lipgloss.NewStyle().Foreground(lipgloss.Color("#555555")).Render("\n(press q to quit)\n"))
	}

	return s.String()
}
