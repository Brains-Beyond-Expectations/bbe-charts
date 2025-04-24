package main

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_ProcessChanges_CanAddNewEntries(t *testing.T) {
	requiredVersions := &RequiredVersions{
		Charts: []Chart{
			{
				Name:      "first-chart",
				MinBbeCli: "1.0.0",
				ExternalChart: &ExternalChart{
					Version:        "1.0.0",
					RepositoryUrl:  "https://first.com",
					RepositoryName: "first",
				},
			},
		},
	}
	library := Library{
		Library: []LibraryEntry{},
	}

	result := processChanges(*requiredVersions, library)

	assert.Len(t, result.Library, 1)
	// New entry
	assert.Equal(t, "1.0.0", result.Library[0].MinBbeCli)
	assert.Equal(t, 1, result.Library[0].ListRevision)
	assert.Equal(t, "first-chart", result.Library[0].Charts[0].Name)
	assert.Equal(t, "1.0.0", result.Library[0].Charts[0].Version)
	assert.Equal(t, "https://first.com", result.Library[0].Charts[0].RepositoryUrl)
	assert.Equal(t, "first", result.Library[0].Charts[0].RepositoryName)
}

func Test_ProcessChanges_CanAddNewRevisions(t *testing.T) {
	requiredVersions := &RequiredVersions{
		Charts: []Chart{
			{
				Name:      "first-chart",
				MinBbeCli: "1.0.0",
				ExternalChart: &ExternalChart{
					Version:        "1.0.1",
					RepositoryUrl:  "https://first.com",
					RepositoryName: "first",
				},
			},
		},
	}
	library := Library{
		Library: []LibraryEntry{
			{
				MinBbeCli:    "1.0.0",
				ListRevision: 1,
				Charts: []ChartEntry{
					{
						Name:           "first-chart",
						Version:        "1.0.0",
						RepositoryUrl:  "https://first.com",
						RepositoryName: "first",
					},
				},
			},
		},
	}

	result := processChanges(*requiredVersions, library)

	assert.Len(t, result.Library, 2)
	// New entry
	assert.Equal(t, "1.0.0", result.Library[0].MinBbeCli)
	assert.Equal(t, 2, result.Library[0].ListRevision)
	assert.Equal(t, "first-chart", result.Library[0].Charts[0].Name)
	assert.Equal(t, "1.0.1", result.Library[0].Charts[0].Version)
	assert.Equal(t, "https://first.com", result.Library[0].Charts[0].RepositoryUrl)
	assert.Equal(t, "first", result.Library[0].Charts[0].RepositoryName)
	// Original entry
	assert.Equal(t, "1.0.0", result.Library[1].MinBbeCli)
	assert.Equal(t, 1, result.Library[1].ListRevision)
	assert.Equal(t, "first-chart", result.Library[1].Charts[0].Name)
	assert.Equal(t, "1.0.0", result.Library[1].Charts[0].Version)
	assert.Equal(t, "https://first.com", result.Library[1].Charts[0].RepositoryUrl)
	assert.Equal(t, "first", result.Library[1].Charts[0].RepositoryName)
}

func Test_ProcessChanges_CanMaintainMultipleCliVersions(t *testing.T) {
	requiredVersions := &RequiredVersions{
		Charts: []Chart{
			{
				Name:      "first-chart",
				MinBbeCli: "2.0.0",
				ExternalChart: &ExternalChart{
					Version:        "2.0.0",
					RepositoryUrl:  "https://first.com",
					RepositoryName: "first",
				},
			},
			{
				Name:      "second-chart",
				MinBbeCli: "1.0.0",
				ExternalChart: &ExternalChart{
					Version:        "1.0.1",
					RepositoryUrl:  "https://second.com",
					RepositoryName: "second",
				},
			},
		},
	}
	library := Library{
		Library: []LibraryEntry{
			{
				MinBbeCli:    "2.0.0",
				ListRevision: 1,
				Charts: []ChartEntry{
					{
						Name:           "first-chart",
						Version:        "2.0.0",
						RepositoryUrl:  "https://first.com",
						RepositoryName: "first",
					},
					{
						Name:           "second-chart",
						Version:        "1.0.0",
						RepositoryUrl:  "https://second.com",
						RepositoryName: "second",
					},
				},
			},
			{
				MinBbeCli:    "1.0.0",
				ListRevision: 1,
				Charts: []ChartEntry{
					{
						Name:           "first-chart",
						Version:        "1.0.0",
						RepositoryUrl:  "https://first.com",
						RepositoryName: "first",
					},
					{
						Name:           "second-chart",
						Version:        "1.0.0",
						RepositoryUrl:  "https://second.com",
						RepositoryName: "second",
					},
				},
			},
		},
	}

	result := processChanges(*requiredVersions, library)

	assert.Len(t, result.Library, 4)
	// First entry
	assert.Equal(t, "2.0.0", result.Library[0].MinBbeCli)
	assert.Equal(t, 2, result.Library[0].ListRevision)
	assert.Equal(t, "first-chart", result.Library[0].Charts[0].Name)
	assert.Equal(t, "2.0.0", result.Library[0].Charts[0].Version)
	assert.Equal(t, "https://first.com", result.Library[0].Charts[0].RepositoryUrl)
	assert.Equal(t, "first", result.Library[0].Charts[0].RepositoryName)
	assert.Equal(t, "second-chart", result.Library[0].Charts[1].Name)
	assert.Equal(t, "1.0.1", result.Library[0].Charts[1].Version)
	assert.Equal(t, "https://second.com", result.Library[0].Charts[1].RepositoryUrl)
	assert.Equal(t, "second", result.Library[0].Charts[1].RepositoryName)
	// Second entry
	assert.Equal(t, "2.0.0", result.Library[1].MinBbeCli)
	assert.Equal(t, 1, result.Library[1].ListRevision)
	assert.Equal(t, "first-chart", result.Library[1].Charts[0].Name)
	assert.Equal(t, "2.0.0", result.Library[1].Charts[0].Version)
	assert.Equal(t, "https://first.com", result.Library[1].Charts[0].RepositoryUrl)
	assert.Equal(t, "first", result.Library[1].Charts[0].RepositoryName)
	assert.Equal(t, "second-chart", result.Library[1].Charts[1].Name)
	assert.Equal(t, "1.0.0", result.Library[1].Charts[1].Version)
	assert.Equal(t, "https://second.com", result.Library[1].Charts[1].RepositoryUrl)
	assert.Equal(t, "second", result.Library[1].Charts[1].RepositoryName)
	// First entry
	assert.Equal(t, "1.0.0", result.Library[2].MinBbeCli)
	assert.Equal(t, 2, result.Library[2].ListRevision)
	assert.Equal(t, "first-chart", result.Library[2].Charts[0].Name)
	assert.Equal(t, "1.0.0", result.Library[2].Charts[0].Version)
	assert.Equal(t, "https://first.com", result.Library[2].Charts[0].RepositoryUrl)
	assert.Equal(t, "first", result.Library[2].Charts[0].RepositoryName)
	assert.Equal(t, "second-chart", result.Library[2].Charts[1].Name)
	assert.Equal(t, "1.0.1", result.Library[2].Charts[1].Version)
	assert.Equal(t, "https://second.com", result.Library[2].Charts[1].RepositoryUrl)
	assert.Equal(t, "second", result.Library[2].Charts[1].RepositoryName)
	// Second entry
	assert.Equal(t, "1.0.0", result.Library[3].MinBbeCli)
	assert.Equal(t, 1, result.Library[3].ListRevision)
	assert.Equal(t, "first-chart", result.Library[3].Charts[0].Name)
	assert.Equal(t, "1.0.0", result.Library[3].Charts[0].Version)
	assert.Equal(t, "https://first.com", result.Library[3].Charts[0].RepositoryUrl)
	assert.Equal(t, "first", result.Library[3].Charts[0].RepositoryName)
	assert.Equal(t, "second-chart", result.Library[3].Charts[1].Name)
	assert.Equal(t, "1.0.0", result.Library[3].Charts[1].Version)
	assert.Equal(t, "https://second.com", result.Library[3].Charts[1].RepositoryUrl)
	assert.Equal(t, "second", result.Library[3].Charts[1].RepositoryName)
}
