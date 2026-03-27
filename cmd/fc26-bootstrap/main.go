package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/user"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/charmbracelet/huh"
)

type Config struct {
	DataDir            string   `json:"data_dir"`
	RuntimeDir         string   `json:"runtime_dir"`
	ImportDir          string   `json:"import_dir"`
	ImagesDir          string   `json:"images_dir"`
	DashboardDir       string   `json:"dashboard_dir"`
	SqlitePath         string   `json:"sqlite_path"`
	ManifestPath       string   `json:"manifest_path"`
	StatusJSON         string   `json:"status_json"`
	CSVSources         []string `json:"csv_sources"`
	ProviderPriority   []string `json:"provider_priority"`
	ServerHost         string   `json:"server_host"`
	ServerPort         int      `json:"server_port"`
	BrowserCommand     string   `json:"browser_command"`
	AutoRefreshMinutes int      `json:"auto_refresh_minutes"`
}

func expand(path string) string {
	if strings.HasPrefix(path, "~/") {
		usr, _ := user.Current()
		return filepath.Join(usr.HomeDir, path[2:])
	}
	return path
}

func main() {
	usr, _ := user.Current()
	home := usr.HomeDir
	cfg := Config{
		DataDir:            filepath.Join(home, ".local/share/fc26-clubos"),
		RuntimeDir:         filepath.Join(home, ".local/share/fc26-clubos/runtime"),
		ImportDir:          filepath.Join(home, ".local/share/fc26-clubos/imports"),
		ImagesDir:          filepath.Join(home, ".local/share/fc26-clubos/runtime/images"),
		DashboardDir:       filepath.Join(home, ".local/share/fc26-clubos/runtime/dashboard"),
		SqlitePath:         filepath.Join(home, ".local/share/fc26-clubos/runtime/fc26_clubos.sqlite"),
		ManifestPath:       filepath.Join(home, ".local/share/fc26-clubos/runtime/fc26_image_manifest_v4.json"),
		StatusJSON:         filepath.Join(home, ".local/share/fc26-clubos/runtime/status.json"),
		CSVSources:         []string{},
		ProviderPriority:   []string{"futgg", "futbin"},
		ServerHost:         "127.0.0.1",
		ServerPort:         43826,
		BrowserCommand:     "",
		AutoRefreshMinutes: 120,
	}

	var clubCSV string
	var sbcCSV string
	var browserCmd string
	var refreshMins string = "120"
	var patchWaybar bool = true
	var patchHypr bool = true

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewInput().Title("Club CSV path").Description("Path to club-analyzer.csv").Value(&clubCSV),
			huh.NewInput().Title("SBC CSV path").Description("Path to SBC Storage.csv").Value(&sbcCSV),
			huh.NewInput().Title("Browser command").Description("Optional browser launcher command").Value(&browserCmd),
			huh.NewInput().Title("Auto refresh minutes").Description("Suggested 60 to 180").Value(&refreshMins),
			huh.NewConfirm().Title("Patch Waybar config automatically").Value(&patchWaybar),
			huh.NewConfirm().Title("Patch Hyprland config automatically").Value(&patchHypr),
		),
	)
	_ = form.Run()

	if clubCSV != "" {
		cfg.CSVSources = append(cfg.CSVSources, expand(clubCSV))
	}
	if sbcCSV != "" {
		cfg.CSVSources = append(cfg.CSVSources, expand(sbcCSV))
	}
	cfg.BrowserCommand = browserCmd
	if mins, err := strconv.Atoi(refreshMins); err == nil && mins > 0 {
		cfg.AutoRefreshMinutes = mins
	}

	configDir := filepath.Join(home, ".config/fc26-clubos")
	_ = os.MkdirAll(configDir, 0o755)
	configPath := filepath.Join(configDir, "config.json")
	f, err := os.Create(configPath)
	if err != nil {
		panic(err)
	}
	defer f.Close()
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	if err := enc.Encode(cfg); err != nil {
		panic(err)
	}

	fmt.Println("Saved config to", configPath)
	fmt.Println("Waybar patch:", patchWaybar)
	fmt.Println("Hyprland patch:", patchHypr)
}
