package main

import (
	"fmt"
	"os"
	"sort"

	"github.com/blang/semver"
	v1 "github.com/spf13/viper"
	v2 "github.com/spf13/viper"
	"gopkg.in/yaml.v2"
)

// required-versions.yaml

type Chart struct {
	Name          string         `mapstructure:"name"`
	MinBbeCli     string         `mapstructure:"min-bbe-cli"`
	ExternalChart *ExternalChart `mapstructure:"external-chart,omitempty"`
}

type ExternalChart struct {
	Version        string `mapstructure:"version"`
	RepositoryUrl  string `mapstructure:"repositoryUrl"`
	RepositoryName string `mapstructure:"repositoryName"`
}

type RequiredVersions struct {
	Charts []Chart `mapstructure:"charts"`
}

// library.yaml

type Library struct {
	Library []LibraryEntry `mapstructure:"library"`
}

type LibraryEntry struct {
	MinBbeCli    string       `mapstructure:"min-bbe-cli" yaml:"min-bbe-cli"`
	ListRevision int          `mapstructure:"list-revision" yaml:"list-revision"`
	Charts       []ChartEntry `mapstructure:"charts" yaml:"charts"`
}

type ChartEntry struct {
	Name           string `mapstructure:"name" yaml:"name"`
	Version        string `mapstructure:"version" yaml:"version"`
	RepositoryUrl  string `mapstructure:"repositoryUrl" yaml:"repositoryUrl"`
	RepositoryName string `mapstructure:"repositoryName" yaml:"repositoryName"`
}

func main() {
	requiredVersions := loadRequiredVersions()
	library := loadLibrary()

	library = processChanges(requiredVersions, library)

	writeLibrary(library)
}

func loadRequiredVersions() RequiredVersions {
	v := v1.New()
	v.SetConfigName("required-versions")
	v.SetConfigType("yaml")
	v.AddConfigPath("./..")
	err := v.ReadInConfig()
	if err != nil {
		panic(err)
	}

	var requiredVersions RequiredVersions
	err = v.Unmarshal(&requiredVersions)
	if err != nil {
		panic(err)
	}

	return requiredVersions
}

func loadLibrary() Library {
	v := v2.New()
	v.SetConfigName("library")
	v.SetConfigType("yaml")
	v.AddConfigPath("./..")
	err := v.ReadInConfig()
	if err != nil {
		panic(err)
	}

	var library Library
	err = v.Unmarshal(&library)
	if err != nil {
		panic(err)
	}

	return library
}

func processChanges(requiredVersions RequiredVersions, library Library) Library {
	// Process each required chart
	for _, requiredVersionsChart := range requiredVersions.Charts {
		seenBbeVersions := make(map[string]bool)

		if requiredVersionsChart.ExternalChart == nil {
			requiredVersionsChart.ExternalChart = loadBbeChartValues(requiredVersionsChart.Name)
		}

		fmt.Printf("\nChecking chart %s (chart version %s for cli version %s):\n", requiredVersionsChart.Name, requiredVersionsChart.ExternalChart.Version, requiredVersionsChart.MinBbeCli)

		found := false
		// Find all compatible CLI versions that need updating
		for _, libraryEntry := range library.Library {
			if seenBbeVersions[libraryEntry.MinBbeCli] {
				continue
			}
			seenBbeVersions[libraryEntry.MinBbeCli] = true

			fmt.Println("Checkling compatibility with library entry cli version", libraryEntry.MinBbeCli)

			// Check if the current chart can be used on this version of bbe
			if semver.MustParse(libraryEntry.MinBbeCli).GTE(semver.MustParse(requiredVersionsChart.MinBbeCli)) {
				found = true
				for _, chartEntry := range libraryEntry.Charts {
					if chartEntry.Name == requiredVersionsChart.Name {
						if semver.MustParse(chartEntry.Version).LT(semver.MustParse(requiredVersionsChart.ExternalChart.Version)) {
							fmt.Println("Creating new revision", chartEntry.Name, "from", chartEntry.Version, "to", requiredVersionsChart.ExternalChart.Version, "for bbe cli version", libraryEntry.MinBbeCli)
							newLibraryEntry := LibraryEntry{
								MinBbeCli:    libraryEntry.MinBbeCli,
								ListRevision: libraryEntry.ListRevision,
								Charts:       append([]ChartEntry{}, libraryEntry.Charts...),
							}
							for i := range newLibraryEntry.Charts {
								if newLibraryEntry.Charts[i].Name == chartEntry.Name {
									newLibraryEntry.Charts[i].Version = requiredVersionsChart.ExternalChart.Version
									newLibraryEntry.Charts[i].RepositoryUrl = requiredVersionsChart.ExternalChart.RepositoryUrl
									newLibraryEntry.Charts[i].RepositoryName = requiredVersionsChart.ExternalChart.RepositoryName
								}
							}
							newLibraryEntry.ListRevision++
							library.Library = append(library.Library, newLibraryEntry)
						}
					}
				}
			}
		}

		if !found {
			fmt.Println("Creating new library entry for cli version", requiredVersionsChart.MinBbeCli)

			allCharts := []ChartEntry{}
			for _, chart := range requiredVersions.Charts {
				if chart.ExternalChart == nil {
					chart.ExternalChart = loadBbeChartValues(chart.Name)
				}
				allCharts = append(allCharts, ChartEntry{
					Name:           chart.Name,
					Version:        chart.ExternalChart.Version,
					RepositoryUrl:  chart.ExternalChart.RepositoryUrl,
					RepositoryName: chart.ExternalChart.RepositoryName,
				})
			}

			newLibraryEntry := LibraryEntry{
				MinBbeCli:    requiredVersionsChart.MinBbeCli,
				ListRevision: 1,
				Charts:       allCharts,
			}
			library.Library = append(library.Library, newLibraryEntry)
		}
	}

	return sortLibrary(library)
}

func sortLibrary(library Library) Library {
	// Sort library entries by MinBbeCli and ListRevision
	sort.Slice(library.Library, func(i, j int) bool {
		if library.Library[i].MinBbeCli != library.Library[j].MinBbeCli {
			return library.Library[i].MinBbeCli > library.Library[j].MinBbeCli
		}
		return library.Library[i].ListRevision > library.Library[j].ListRevision
	})
	return library
}

func writeLibrary(library Library) {
	yamlFile, err := yaml.Marshal(library)
	if err != nil {
		panic(err)
	}

	finalText := []byte("# AUTOGENERATED FILE, DO NOT EDIT!!!\n")
	finalText = append(finalText, yamlFile...)

	err = os.WriteFile("./../library.yaml", finalText, 0644)
	if err != nil {
		panic(err)
	}
}

func loadBbeChartValues(name string) *ExternalChart {
	contents, err := os.ReadFile("./../charts/" + name + "/Chart.yaml")
	if err != nil {
		panic(err)
	}

	var chartYaml struct {
		Version string `yaml:"version"`
	}

	err = yaml.Unmarshal(contents, &chartYaml)
	if err != nil {
		panic(err)
	}

	return &ExternalChart{
		Version:        chartYaml.Version,
		RepositoryUrl:  "https://brains-beyond-expectations.github.io/bbe-charts",
		RepositoryName: "bbe",
	}
}
