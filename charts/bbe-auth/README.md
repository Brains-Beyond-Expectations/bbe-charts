# bbe-auth

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

Single sign-on for the BBE cluster's apps with authentik, its PostgreSQL database, and LDAP for Jellyfin

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://charts.goauthentik.io | authentik | 2026.8.4 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| authentik.authentik.postgresql.host | string | `"bbe-auth-postgres"` |  |
| authentik.authentik.postgresql.name | string | `"authentik"` |  |
| authentik.authentik.postgresql.user | string | `"authentik"` |  |
| authentik.blueprints.configMaps[0] | string | `"bbe-auth-blueprints"` |  |
| authentik.fullnameOverride | string | `"bbe-auth"` |  |
| authentik.global.envFrom[0].secretRef.name | string | `"bbe-auth-authentik"` |  |
| authentik.global.securityContext.runAsNonRoot | bool | `true` |  |
| authentik.global.securityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| authentik.postgresql.enabled | bool | `false` |  |
| authentik.server.containerSecurityContext.allowPrivilegeEscalation | bool | `false` |  |
| authentik.server.containerSecurityContext.capabilities.drop[0] | string | `"ALL"` |  |
| authentik.server.resources.limits.memory | string | `"1Gi"` |  |
| authentik.server.resources.requests.cpu | string | `"100m"` |  |
| authentik.server.resources.requests.memory | string | `"512Mi"` |  |
| authentik.server.volumeMounts[0].mountPath | string | `"/media/public/branding"` |  |
| authentik.server.volumeMounts[0].name | string | `"branding"` |  |
| authentik.server.volumeMounts[0].readOnly | bool | `true` |  |
| authentik.server.volumes[0].configMap.name | string | `"bbe-auth-branding"` |  |
| authentik.server.volumes[0].name | string | `"branding"` |  |
| authentik.serviceAccount.create | bool | `false` |  |
| authentik.worker.automountServiceAccountToken | bool | `false` |  |
| authentik.worker.containerSecurityContext.allowPrivilegeEscalation | bool | `false` |  |
| authentik.worker.containerSecurityContext.capabilities.drop[0] | string | `"ALL"` |  |
| authentik.worker.resources.limits.memory | string | `"1Gi"` |  |
| authentik.worker.resources.requests.cpu | string | `"100m"` |  |
| authentik.worker.resources.requests.memory | string | `"384Mi"` |  |
| bbe.auth.admin.email | string | `nil` | The first admin's email address |
| bbe.auth.admin.username | string | `nil` | The username of the first admin, who can manage everyone else in authentik. Their first password is generated into the `bbe-auth-admin` secret |
| bbe.auth.users | list | `[]` | The users bbe adds to authentik, with `bbe configure bbe-auth`. Each has a `username`, an `email`, an optional `firstName` and `lastName`, `groups` (`users` or `admins`), and `secretFields.password`, the key of their first password in the `bbe-auth-users` secret. People added in authentik's admin interface aren't listed here |
| bbe.ldap.image.repository | string | `"ghcr.io/goauthentik/ldap"` | authentik's LDAP outpost, which Jellyfin signs people in with. Its version is authentik's |
| bbe.ldap.image.tag | string | `"2026.8.4"` | The LDAP outpost's version, the same as authentik's |
| bbe.ldap.resources.limits.memory | string | `"128Mi"` | The memory to limit the LDAP outpost to |
| bbe.ldap.resources.requests.cpu | string | `"10m"` | The CPU to request for the LDAP outpost |
| bbe.ldap.resources.requests.memory | string | `"64Mi"` | The memory to request for the LDAP outpost |
| bbe.postgres.image.repository | string | `"postgres"` | The PostgreSQL image, the official one |
| bbe.postgres.image.tag | string | `"18.6"` | The PostgreSQL version. A new major version needs the database dumped and restored, which an upgrade doesn't |
| bbe.postgres.resources.limits.memory | string | `"512Mi"` | The memory to limit PostgreSQL to |
| bbe.postgres.resources.requests.cpu | string | `"50m"` | The CPU to request for PostgreSQL |
| bbe.postgres.resources.requests.memory | string | `"128Mi"` | The memory to request for PostgreSQL |
| bbe.postgres.size | string | `"2Gi"` | The size of authentik's database |
| bbe.setup.backoffLimit | int | `5` | How many times the setup is retried when authentik couldn't be set up |
| bbe.setup.image.repository | string | `"python"` | The image to run the setup with, which only needs Python |
| bbe.setup.image.tag | string | `"3.13-alpine"` | The tag of the setup image |
| bbe.setup.readyTimeout | int | `900` | How long the setup waits for authentik to start and apply bbe's blueprint, in seconds |
| bbe.setup.resources.limits.memory | string | `"128Mi"` | The amount of memory to limit the setup pod to |
| bbe.setup.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the setup pod |
| bbe.setup.resources.requests.memory | string | `"64Mi"` | The amount of memory to request for the setup pod |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the cluster's apps are named under, which bbe-networking answers for. authentik signs people in at auth.<domain> |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
