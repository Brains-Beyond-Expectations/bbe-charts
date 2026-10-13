package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/blang/semver"
	"gopkg.in/yaml.v2"
)

// A preview library lists a pull request's charts alongside the published ones, so its changes can be installed
// with `bbe --library <url>` before they're merged. Only charts that are bbe packages are listed, those published
// in the library or in required-versions.yaml. The rest, like the apps bbe-media bundles, are only dependencies
func previewLibrary(library Library, requiredVersions RequiredVersions, previews []ChartEntry) (Library, error) {
	base := LibraryEntry{MinBbeCli: "0.0.0"}
	if len(library.Library) > 0 {
		base = library.Library[0]
	}

	entry := LibraryEntry{
		MinBbeCli:    base.MinBbeCli,
		ListRevision: base.ListRevision + 1,
		Charts:       append([]ChartEntry{}, base.Charts...),
	}

	for _, preview := range previews {
		if !isPackage(preview.Name, base, requiredVersions) {
			continue
		}

		replaced := false
		for i := range entry.Charts {
			if entry.Charts[i].Name == preview.Name {
				entry.Charts[i] = preview
				replaced = true
			}
		}
		if !replaced {
			entry.Charts = append(entry.Charts, preview)
		}

		// A preview can need a newer bbe than the published charts, like a chart setting a new annotation
		for _, chart := range requiredVersions.Charts {
			if chart.Name != preview.Name {
				continue
			}

			required, err := semver.Parse(chart.MinBbeCli)
			if err != nil {
				return Library{}, fmt.Errorf("min-bbe-cli `%s` of chart `%s` isn't a version: %w", chart.MinBbeCli, chart.Name, err)
			}
			current, err := semver.Parse(entry.MinBbeCli)
			if err != nil {
				return Library{}, fmt.Errorf("min-bbe-cli `%s` of the library isn't a version: %w", entry.MinBbeCli, err)
			}
			if required.GT(current) {
				entry.MinBbeCli = chart.MinBbeCli
			}
		}
	}

	return Library{Library: []LibraryEntry{entry}}, nil
}

func isPackage(name string, base LibraryEntry, requiredVersions RequiredVersions) bool {
	for _, chart := range base.Charts {
		if chart.Name == name {
			return true
		}
	}
	for _, chart := range requiredVersions.Charts {
		if chart.Name == name {
			return true
		}
	}

	return false
}

// Parses `name=version` arguments into the charts of a preview, all served from the same repository
func parsePreviewCharts(args []string, repositoryUrl string, repositoryName string) ([]ChartEntry, error) {
	if len(args) == 0 {
		return nil, errors.New("no charts to preview, pass them as name=version")
	}

	charts := []ChartEntry{}
	for _, arg := range args {
		name, version, found := strings.Cut(arg, "=")
		if !found || name == "" || version == "" {
			return nil, fmt.Errorf("`%s` isn't name=version", arg)
		}
		if _, err := semver.Parse(version); err != nil {
			return nil, fmt.Errorf("`%s` of chart `%s` isn't a version: %w", version, name, err)
		}

		charts = append(charts, ChartEntry{Name: name, Version: version, RepositoryUrl: repositoryUrl, RepositoryName: repositoryName})
	}

	return charts, nil
}

// go run . preview -repository-url URL -repository-name NAME -output FILE name=version...
func runPreview(args []string) error {
	flags := flag.NewFlagSet("preview", flag.ContinueOnError)
	repositoryUrl := flags.String("repository-url", "", "the helm repository serving the preview charts")
	repositoryName := flags.String("repository-name", "", "the name bbe adds that helm repository under")
	output := flags.String("output", "", "where to write the preview library")
	if err := flags.Parse(args); err != nil {
		return err
	}
	if *repositoryUrl == "" || *repositoryName == "" || *output == "" {
		return errors.New("-repository-url, -repository-name and -output are required")
	}

	previews, err := parsePreviewCharts(flags.Args(), *repositoryUrl, *repositoryName)
	if err != nil {
		return err
	}

	library, err := previewLibrary(loadLibrary(), loadRequiredVersions(), previews)
	if err != nil {
		return err
	}

	content, err := yaml.Marshal(library)
	if err != nil {
		return err
	}

	return os.WriteFile(*output, append([]byte("# Preview of a pull request, not a release\n"), content...), 0644)
}
