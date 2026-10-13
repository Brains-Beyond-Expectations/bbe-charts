package main

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
)

var published = Library{
	Library: []LibraryEntry{
		{
			MinBbeCli:    "1.4.0",
			ListRevision: 7,
			Charts: []ChartEntry{
				{Name: "bbe-media", Version: "0.2.0", RepositoryUrl: "https://bbe.example", RepositoryName: "bbe"},
				{Name: "bbe-networking", Version: "0.3.0", RepositoryUrl: "https://bbe.example", RepositoryName: "bbe"},
			},
		},
		{
			MinBbeCli:    "0.6.0",
			ListRevision: 6,
			Charts:       []ChartEntry{{Name: "bbe-media", Version: "0.1.0", RepositoryUrl: "https://bbe.example", RepositoryName: "bbe"}},
		},
	},
}

func Test_previewLibrary_Succeeds_ReplacingAndAddingCharts(t *testing.T) {
	previews := []ChartEntry{
		{Name: "bbe-networking", Version: "0.3.0-pr153.4", RepositoryUrl: "https://preview.example", RepositoryName: "bbe-pr-153"},
		{Name: "bbe-storage", Version: "0.1.0-pr153.4", RepositoryUrl: "https://preview.example", RepositoryName: "bbe-pr-153"},
	}

	result, err := previewLibrary(published, RequiredVersions{}, previews)

	assert.NoError(t, err)
	assert.Equal(t, Library{Library: []LibraryEntry{{
		MinBbeCli:    "1.4.0",
		ListRevision: 8,
		Charts: []ChartEntry{
			{Name: "bbe-media", Version: "0.2.0", RepositoryUrl: "https://bbe.example", RepositoryName: "bbe"},
			previews[0],
			previews[1],
		},
	}}}, result)
	// The published library is left as it is
	assert.Equal(t, "0.3.0", published.Library[0].Charts[1].Version)
}

func Test_previewLibrary_Succeeds_RaisingTheMinimumBbeVersion(t *testing.T) {
	requiredVersions := RequiredVersions{Charts: []Chart{
		{Name: "bbe-media", MinBbeCli: "2.0.0"},
		{Name: "bbe-networking", MinBbeCli: "1.5.0"},
		{Name: "bbe-storage", MinBbeCli: "1.0.0"},
	}}
	previews := []ChartEntry{{Name: "bbe-networking"}, {Name: "bbe-storage"}}

	result, err := previewLibrary(published, requiredVersions, previews)

	assert.NoError(t, err)
	assert.Equal(t, "1.5.0", result.Library[0].MinBbeCli)
}

func Test_previewLibrary_Succeeds_WithoutAPublishedLibrary(t *testing.T) {
	previews := []ChartEntry{{Name: "bbe-storage", Version: "0.1.0-pr152.1"}}

	result, err := previewLibrary(Library{}, RequiredVersions{}, previews)

	assert.NoError(t, err)
	assert.Equal(t, Library{Library: []LibraryEntry{{MinBbeCli: "0.0.0", ListRevision: 1, Charts: previews}}}, result)
}

func Test_previewLibrary_Fails_WithAnInvalidMinimumBbeVersion(t *testing.T) {
	requiredVersions := RequiredVersions{Charts: []Chart{{Name: "bbe-networking", MinBbeCli: "soon"}}}

	_, err := previewLibrary(published, requiredVersions, []ChartEntry{{Name: "bbe-networking"}})

	assert.ErrorContains(t, err, "min-bbe-cli `soon` of chart `bbe-networking` isn't a version")
}

func Test_previewLibrary_Fails_WithAnInvalidLibraryVersion(t *testing.T) {
	library := Library{Library: []LibraryEntry{{MinBbeCli: "latest"}}}
	requiredVersions := RequiredVersions{Charts: []Chart{{Name: "bbe-networking", MinBbeCli: "1.5.0"}}}

	_, err := previewLibrary(library, requiredVersions, []ChartEntry{{Name: "bbe-networking"}})

	assert.ErrorContains(t, err, "min-bbe-cli `latest` of the library isn't a version")
}

func Test_parsePreviewCharts_Succeeds(t *testing.T) {
	charts, err := parsePreviewCharts([]string{"bbe-networking=0.3.0-pr153.4"}, "https://preview.example", "bbe-pr-153")

	assert.NoError(t, err)
	assert.Equal(t, []ChartEntry{{Name: "bbe-networking", Version: "0.3.0-pr153.4", RepositoryUrl: "https://preview.example", RepositoryName: "bbe-pr-153"}}, charts)
}

func Test_parsePreviewCharts_Fails(t *testing.T) {
	cases := map[string][]string{
		"no charts to preview":                             {},
		"`bbe-networking` isn't name=version":              {"bbe-networking"},
		"`=1.0.0` isn't name=version":                      {"=1.0.0"},
		"`next` of chart `bbe-networking` isn't a version": {"bbe-networking=next"},
	}

	for expected, args := range cases {
		_, err := parsePreviewCharts(args, "https://preview.example", "bbe-pr-153")

		assert.ErrorContains(t, err, expected, args)
	}
}

func Test_runPreview_Succeeds_WritingTheLibrary(t *testing.T) {
	output := filepath.Join(t.TempDir(), "library.yaml")

	err := runPreview([]string{"-repository-url", "https://preview.example", "-repository-name", "bbe-pr-153", "-output", output, "bbe-networking=0.3.0-pr153.4"})

	assert.NoError(t, err)
	content, _ := os.ReadFile(output)
	assert.Contains(t, string(content), "# Preview of a pull request, not a release\nlibrary:\n")
	assert.Contains(t, string(content), "  - name: bbe-networking\n    version: 0.3.0-pr153.4\n    repositoryUrl: https://preview.example\n    repositoryName: bbe-pr-153\n")
}

func Test_runPreview_Fails(t *testing.T) {
	cases := map[string][]string{
		"flag provided but not defined":                              {"-unknown"},
		"-repository-url, -repository-name and -output are required": {"bbe-networking=0.3.0"},
		"no charts to preview":                                       {"-repository-url", "u", "-repository-name", "n", "-output", "o"},
	}

	for expected, args := range cases {
		assert.ErrorContains(t, runPreview(args), expected, args)
	}
}
