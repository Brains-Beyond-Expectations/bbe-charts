# bbe-auth

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

Single sign-on for the BBE cluster's apps, with Keycloak, its PostgreSQL database and oauth2-proxy

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://codecentric.github.io/helm-charts | keycloakx | 7.3.2 |
| https://oauth2-proxy.github.io/manifests | oauth2-proxy | 10.7.1 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bbe.auth.admin.email | string | `nil` | The first admin's email address |
| bbe.auth.admin.username | string | `nil` | The username of the first admin, who can manage everyone else in Keycloak's console. Their first password is generated into the `bbe-auth-admin` secret |
| bbe.auth.clients | list | `[]` | Apps signing people in with Keycloak themselves, rather than behind oauth2-proxy. Each is a client in the realm, with a secret generated into the `bbe-auth-clients` secret. `clientId` names it, `host` is the app's name under the domain, and `redirectPath` where Keycloak sends people back to. None of bbe's apps do yet: Jellyfin's SSO plugin and Seerr's sign-in can't, so they keep their own logins |
| bbe.auth.users | list | `[]` | The users bbe adds to Keycloak, with `bbe configure bbe-auth`. Each has a `username`, an `email`, an optional `firstName` and `lastName`, `groups` (`users` or `admins`), and `secretFields.password`, the key of their first password in the `bbe-auth-users` secret. People added in Keycloak's console aren't listed here |
| bbe.postgres.image.repository | string | `"postgres"` | The PostgreSQL image, the official one |
| bbe.postgres.image.tag | string | `"18.6"` | The PostgreSQL version. A new major version needs the database dumped and restored, which an upgrade doesn't |
| bbe.postgres.resources.limits.memory | string | `"512Mi"` | The memory to limit PostgreSQL to |
| bbe.postgres.resources.requests.cpu | string | `"50m"` | The CPU to request for PostgreSQL |
| bbe.postgres.resources.requests.memory | string | `"128Mi"` | The memory to request for PostgreSQL |
| bbe.postgres.size | string | `"2Gi"` | The size of Keycloak's database |
| bbe.setup.backoffLimit | int | `5` | How many times the setup is retried when Keycloak couldn't be set up |
| bbe.setup.image.repository | string | `"python"` | The image to run the setup with, which only needs Python |
| bbe.setup.image.tag | string | `"3.13-alpine"` | The tag of the setup image |
| bbe.setup.readyTimeout | int | `900` | How long the setup waits for Keycloak to start, in seconds |
| bbe.setup.resources.limits.memory | string | `"128Mi"` | The amount of memory to limit the setup pod to |
| bbe.setup.resources.requests.cpu | string | `"50m"` | The amount of CPU to request for the setup pod |
| bbe.setup.resources.requests.memory | string | `"64Mi"` | The amount of memory to request for the setup pod |
| global.bbe.domain | string | `"bbe.home.arpa"` | The domain the cluster's apps are named under, which bbe-networking answers for. Keycloak signs people in at auth.<domain> |
| keycloakx.args[0] | string | `"start"` |  |
| keycloakx.command[0] | string | `"/opt/keycloak/bin/kc.sh"` |  |
| keycloakx.database.database | string | `"keycloak"` |  |
| keycloakx.database.existingSecret | string | `"bbe-auth-postgres"` |  |
| keycloakx.database.existingSecretKey | string | `"password"` |  |
| keycloakx.database.hostname | string | `"bbe-auth-postgres"` |  |
| keycloakx.database.port | int | `5432` |  |
| keycloakx.database.username | string | `"keycloak"` |  |
| keycloakx.database.vendor | string | `"postgres"` |  |
| keycloakx.dbchecker.enabled | bool | `true` |  |
| keycloakx.extraEnv | string | `"- name: KC_HOSTNAME\n  value: https://auth.{{ .Values.global.bbe.domain }}\n- name: KC_HOSTNAME_BACKCHANNEL_DYNAMIC\n  value: \"true\"\n- name: KC_BOOTSTRAP_ADMIN_CLIENT_ID\n  valueFrom:\n    secretKeyRef:\n      name: bbe-auth-keycloak\n      key: setup-client-id\n- name: KC_BOOTSTRAP_ADMIN_CLIENT_SECRET\n  valueFrom:\n    secretKeyRef:\n      name: bbe-auth-keycloak\n      key: setup-client-secret\n- name: KC_BOOTSTRAP_ADMIN_USERNAME\n  valueFrom:\n    secretKeyRef:\n      name: bbe-auth-keycloak\n      key: admin-username\n- name: KC_BOOTSTRAP_ADMIN_PASSWORD\n  valueFrom:\n    secretKeyRef:\n      name: bbe-auth-keycloak\n      key: admin-password\n"` |  |
| keycloakx.extraVolumeMounts | string | `"- name: theme\n  mountPath: /opt/keycloak/themes/bbe\n  readOnly: true\n"` |  |
| keycloakx.extraVolumes | string | `"- name: theme\n  configMap:\n    name: bbe-auth-theme\n    items:\n      - key: theme.properties\n        path: login/theme.properties\n      - key: bbe.css\n        path: login/resources/css/bbe.css\n      - key: brain.webp\n        path: login/resources/img/brain.webp\n      - key: background.webp\n        path: login/resources/img/background.webp\n"` |  |
| keycloakx.fullnameOverride | string | `"bbe-auth-keycloak"` |  |
| keycloakx.http.relativePath | string | `"/"` |  |
| keycloakx.image.tag | string | `"26.7.5"` |  |
| keycloakx.proxy.mode | string | `"xforwarded"` |  |
| keycloakx.resources.limits.memory | string | `"1Gi"` |  |
| keycloakx.resources.requests.cpu | string | `"100m"` |  |
| keycloakx.resources.requests.memory | string | `"512Mi"` |  |
| keycloakx.securityContext.allowPrivilegeEscalation | bool | `false` |  |
| keycloakx.securityContext.capabilities.drop[0] | string | `"ALL"` |  |
| keycloakx.securityContext.runAsNonRoot | bool | `true` |  |
| keycloakx.securityContext.runAsUser | int | `1000` |  |
| keycloakx.securityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| oauth2-proxy.config.cookieName | string | `"_bbe_sso"` |  |
| oauth2-proxy.config.emailDomains[0] | string | `"*"` |  |
| oauth2-proxy.config.existingSecret | string | `"bbe-auth-oauth2-proxy"` |  |
| oauth2-proxy.config.upstreams[0] | string | `"static://202"` |  |
| oauth2-proxy.extraArgs.allowed-group | string | `"admins"` |  |
| oauth2-proxy.extraArgs.code-challenge-method | string | `"S256"` |  |
| oauth2-proxy.extraArgs.cookie-domain | string | `".{{ .Values.global.bbe.domain }}"` |  |
| oauth2-proxy.extraArgs.cookie-secure | string | `"true"` |  |
| oauth2-proxy.extraArgs.login-url | string | `"https://auth.{{ .Values.global.bbe.domain }}/realms/bbe/protocol/openid-connect/auth"` |  |
| oauth2-proxy.extraArgs.oidc-issuer-url | string | `"https://auth.{{ .Values.global.bbe.domain }}/realms/bbe"` |  |
| oauth2-proxy.extraArgs.oidc-jwks-url | string | `"http://bbe-auth-keycloak-http.{{ .Release.Namespace }}.svc/realms/bbe/protocol/openid-connect/certs"` |  |
| oauth2-proxy.extraArgs.provider | string | `"keycloak-oidc"` |  |
| oauth2-proxy.extraArgs.redeem-url | string | `"http://bbe-auth-keycloak-http.{{ .Release.Namespace }}.svc/realms/bbe/protocol/openid-connect/token"` |  |
| oauth2-proxy.extraArgs.redirect-url | string | `"https://auth.{{ .Values.global.bbe.domain }}/oauth2/callback"` |  |
| oauth2-proxy.extraArgs.reverse-proxy | string | `"true"` |  |
| oauth2-proxy.extraArgs.scope | string | `"openid email profile groups"` |  |
| oauth2-proxy.extraArgs.set-xauthrequest | string | `"true"` |  |
| oauth2-proxy.extraArgs.skip-oidc-discovery | bool | `true` |  |
| oauth2-proxy.extraArgs.skip-provider-button | string | `"true"` |  |
| oauth2-proxy.extraArgs.whitelist-domain | string | `".{{ .Values.global.bbe.domain }}"` |  |
| oauth2-proxy.fullnameOverride | string | `"bbe-auth-oauth2-proxy"` |  |
| oauth2-proxy.resources.limits.memory | string | `"128Mi"` |  |
| oauth2-proxy.resources.requests.cpu | string | `"10m"` |  |
| oauth2-proxy.resources.requests.memory | string | `"32Mi"` |  |
| oauth2-proxy.securityContext.allowPrivilegeEscalation | bool | `false` |  |
| oauth2-proxy.securityContext.capabilities.drop[0] | string | `"ALL"` |  |
| oauth2-proxy.securityContext.enabled | bool | `true` |  |
| oauth2-proxy.securityContext.readOnlyRootFilesystem | bool | `true` |  |
| oauth2-proxy.securityContext.runAsGroup | int | `2000` |  |
| oauth2-proxy.securityContext.runAsNonRoot | bool | `true` |  |
| oauth2-proxy.securityContext.runAsUser | int | `2000` |  |
| oauth2-proxy.securityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
