# BBE Charts

The packages [bbe](https://github.com/Brains-Beyond-Expectations/bbe-quest) installs on a BBE cluster: storage,
networking, single sign-on, media, books and music.

**New to bbe?** [Getting started](docs/getting-started.md) takes you from a fresh cluster to every app running, with
one account per person for all of them. Why things are the way they are is in [docs/decisions](docs/decisions).

## Usage

[Helm](https://helm.sh) must be installed to use the charts. Please refer to
Helm's [documentation](https://helm.sh/docs) to get started.

Once Helm has been set up correctly, add the repo as follows:

    helm repo add bbe https://brains-beyond-expectations.github.io/bbe-charts

If you had already added this repo earlier, run `helm repo update` to retrieve
the latest versions of the packages. You can then run `helm search repo bbe` to
see the charts.

To install the <chart-name> chart:

    helm install <chart-name> bbe/<chart-name>

To uninstall the chart:

    helm uninstall my-<chart-name>

## Testing a pull request

Every push to a pull request that changes a chart publishes those charts as a pre-release named
`preview-pr-<number>`, with a library listing them next to the published charts. The pull request gets a comment
with the command to install them:

    bbe install --library https://github.com/Brains-Beyond-Expectations/bbe-charts/releases/download/preview-pr-<number>/library.yaml

To test them with a bbe change that isn't released yet, run `go run . install --library <url>` in the `cli` folder
of that bbe-quest branch. A bbe built from source accepts any library revision.

The preview is a pre-release of the chart's current version, such as `0.3.0-pr153.4`, as the released version is
only set when the pull request merges. It's removed when the pull request closes. Pull requests from forks don't
get a preview.

Charts are compared with `main`, so a pull request stacked on another one includes that one's charts too. When a
chart depends on another chart the pull request changes, like `bbe-media` on `sonarr`, it's packaged with that
chart's preview, so both are tested together before either is released. Only charts that are bbe packages, in
`library.yaml` or `required-versions.yaml`, are listed in the preview library.

For quicker changes, bbe also takes a library file on disk whose charts point at folders, so nothing has to be
pushed:

```yaml
library:
  - min-bbe-cli: 0.0.0
    list-revision: 1
    charts:
      - name: bbe-networking
        version: 0.0.0-local
        repositoryUrl: file://charts/bbe-networking # Relative to the library file
        repositoryName: local
```

    bbe install --library ./local-library.yaml
