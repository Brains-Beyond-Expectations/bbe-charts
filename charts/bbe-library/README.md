# bbe-library

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A book library for the BBE cluster, with Calibre-Web-Automated to read and manage it and Shelfmark to find books

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bbe.admin.username | string | `"library-admin"` | The library's own admin username. It must not be someone's username in authentik, whose password would win |
| bbe.ingress.enabled | bool | `true` | Whether to serve the apps at calibre.<domain> and shelfmark.<domain> through bbe-networking's Traefik |
| bbe.library.calibre.configSize | string | `"2Gi"` | The size of its config volume, with its users, settings and the books it's converting |
| bbe.library.calibre.image.repository | string | `"crocodilestick/calibre-web-automated"` | The Calibre-Web-Automated image |
| bbe.library.calibre.image.tag | string | `"v4.0.8"` | The Calibre-Web-Automated version |
| bbe.library.calibre.resources.limits.memory | string | `"2Gi"` | The memory to limit Calibre-Web-Automated to. Converting a book runs Calibre next to it |
| bbe.library.calibre.resources.requests.cpu | string | `"100m"` | The CPU to request for Calibre-Web-Automated |
| bbe.library.calibre.resources.requests.memory | string | `"512Mi"` | The memory to request for Calibre-Web-Automated |
| bbe.library.nfs.mountOptions | list | `["nfsvers=4"]` | Mount options for the NFS share. NFSv4 needs no lock daemon, which Talos nodes don't run, and `nfsvers=4` uses the newest NFSv4 version the server offers |
| bbe.library.nfs.path | string | `""` | The exported path holding the books on the NFS server. It can be bbe-media's share, as the books get folders of their own |
| bbe.library.nfs.server | string | `""` | The NFS server holding the books, as a hostname or IP address. It can be bbe-media's |
| bbe.library.shelfmark.configSize | string | `"1Gi"` | The size of its config volume, with its settings, users and cover cache |
| bbe.library.shelfmark.directDownload.annasArchive | list | `[]` | Anna's Archive mirrors, such as `https://<mirror>` |
| bbe.library.shelfmark.directDownload.annasArchiveDonatorKey | string | `""` | Anna's Archive donator key, for its fast downloads |
| bbe.library.shelfmark.directDownload.libgen | list | `[]` | Library Genesis mirrors |
| bbe.library.shelfmark.directDownload.welib | list | `[]` | Welib mirrors |
| bbe.library.shelfmark.directDownload.zlibrary | list | `[]` | Z-Library mirrors |
| bbe.library.shelfmark.env | object | `{}` | More of Shelfmark's settings, as environment variables. See its docs/environment-variables.md |
| bbe.library.shelfmark.hardcoverApiKey | string | `""` | A Hardcover API key, for Hardcover's book details rather than Open Library's. Open Library needs no key |
| bbe.library.shelfmark.image.repository | string | `"ghcr.io/calibrain/shelfmark-lite"` | The Shelfmark image. The lite one has no browser of its own, and gets past Cloudflare with bbe-media's FlareSolverr |
| bbe.library.shelfmark.image.tag | string | `"v1.3.0"` | The Shelfmark version. It's maintenance-only since May 2026 |
| bbe.library.shelfmark.irc.channel | string | `""` | The channel, such as `#ebooks` |
| bbe.library.shelfmark.irc.nick | string | `""` | The nickname to use |
| bbe.library.shelfmark.irc.port | int | `6697` | The IRC server's TLS port |
| bbe.library.shelfmark.irc.searchBot | string | `""` | The search bot to ask, such as `search` |
| bbe.library.shelfmark.irc.server | string | `""` | The IRC server, such as `irc.example.net` |
| bbe.library.shelfmark.requests | bool | `false` | Whether people ask for books for an admin to approve, rather than downloading them. Admins always download |
| bbe.library.shelfmark.resources.limits.memory | string | `"512Mi"` | The memory to limit Shelfmark to |
| bbe.library.shelfmark.resources.requests.cpu | string | `"20m"` | The CPU to request for Shelfmark |
| bbe.library.shelfmark.resources.requests.memory | string | `"128Mi"` | The memory to request for Shelfmark |
| bbe.library.size | string | `"100Gi"` | The size of the share. NFS doesn't enforce it, but Kubernetes needs one |
| bbe.library.user.gid | string | `nil` | The group ID of the NAS user |
| bbe.library.user.uid | string | `nil` | The user ID of the NAS user |
| bbe.networkPolicy.enabled | bool | `true` | Whether only Traefik and the library's own pods may reach the library and Shelfmark. The cluster's network has to enforce NetworkPolicies, which `bbe setup` turns on for the clusters it creates |
| bbe.setup.backoffLimit | int | `5` | How many times the setup is retried when the library couldn't be set up |
| bbe.setup.enabled | bool | `true` | Whether to run the Job connecting the library to authentik after every install and upgrade |
| bbe.setup.peopleSchedule | string | `"*/10 * * * *"` | When the setup gives the people Calibre-Web created on their first sign-in their admin rights and Send to eReader address, as a cron schedule |
| bbe.setup.readyTimeout | int | `900` | How long the setup waits for the library to start, in seconds |
| bbe.setup.resources.limits.memory | string | `"256Mi"` | The amount of memory to limit the setup pod to |
| bbe.setup.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the setup pod |
| bbe.setup.resources.requests.memory | string | `"64Mi"` | The amount of memory to request for the setup pod |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the cluster's apps are named under, which bbe-networking answers for. The library is at calibre.<domain>, and Shelfmark at shelfmark.<domain> |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
