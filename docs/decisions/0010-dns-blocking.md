# 0010: The house's DNS blocks ads and threats out of the box

**Status:** proposed, 2026-10-24

## Context

Blocky is the house's DNS ([0002](0002-single-sign-on.md), decision 6), but it was only just running:
- **One ad list,** StevenBlack's hosts.
- **Plain DNS** to Cloudflare and Google, which the ISP and anyone on the way can read.
- **Config keys Blocky has since renamed** (`upstream`, `port`, `blackLists`).
- **Nothing to change in `bbe.yaml`,** short of rewriting Blocky's whole config.

The goal is for a new cluster's DNS to protect the house from the start, with good defaults applied and every choice changeable in `bbe.yaml`.

Things that shaped what follows, checked on 2026-10-24 against Blocky 0.35.0, run locally with the rendered config:
- **Plain domains only match themselves.** A list entry covers subdomains only when it's written `*.example.com`. HaGeZi publishes its lists in that format for Blocky.
- **Lists are held in memory.** With the defaults below, about 390,000 domains, Blocky used about 105MB, and 165MB after refreshing them. Its pods were limited to 128Mi.
- **Allowlists beat denylists across all of a device's groups.** But a device whose groups only allow is blocked from everything else.
- **Helm doesn't pass `null` through to a subchart's globals,** so a group can't be removed by setting it to `null` in `bbe.yaml`.

## Decisions

### 1. HaGeZi's lists, two groups for every device

| Group | List | Domains | Used by default |
|---|---|---|---|
| `ads` | HaGeZi's Multi Normal: ads, tracking, telemetry and the worst of malware | 172,000 | Yes |
| `security` | HaGeZi's Threat Intelligence Feeds mini: malware, phishing, scams, cryptojacking | 214,000 | Yes |
| `adult` | HaGeZi's NSFW | 91,000 | No, for the devices given it |

**Why HaGeZi:**
- Its lists are updated several times a day.
- It's made for DNS blockers, and documents its compatibility with Blocky.
- Multi Normal is its "set and forget" level: it rarely blocks what it shouldn't, which suits a household without someone on hand to unblock things.

**Only the groups some device gets are downloaded,** so `adult` costs nothing until it's used. Turning a group off is taking it out of `groups`.

**A group nobody has lists for fails the install,** naming the groups there are, so a typo in `bbe.yaml` doesn't quietly leave a device unblocked.

Rejected:
- **HaGeZi's Pro.** It blocks more, but HaGeZi says it works best with an admin nearby to unblock things.
- **OISD Big.** It's similar, but HaGeZi also has the threat feeds, in the same format.
- **StevenBlack's hosts.** Multi Normal covers it.
- **URLhaus's hostfile.** It's been withdrawn (HTTP 410).
- **HaGeZi's TIF medium, and its gambling list.** They're 620,000 and 610,000 domains, too much memory for the gain.

### 2. Encrypted DNS to Quad9 and Cloudflare

Blocky asks `https://dns.quad9.net/dns-query` and `https://cloudflare-dns.com/dns-query`, over DNS-over-HTTPS, and answers with the faster (`parallel_best`).
- **Quad9** also refuses names it knows to be malicious, a second layer behind `security`.
- **Finding them:** both are listed with their IP addresses (`bootstrapDns`). Blocky finds them, and the lists' hosts, without asking anything in plain text.

### 3. DNS keeps answering, whatever the lists do

- **Startup:** lists and upstreams load with Blocky's `fast` strategy. Blocky answers straight away and blocks once the lists are in, so a restart or an unreachable list never takes the house's DNS down.
- **Refresh:** lists are downloaded again every 6 hours (`refreshPeriod`), HaGeZi's own update interval.
- **Blocked names** get `0.0.0.0` for 1 minute (`blockTTL`), so unblocking one works within a minute. Blocky also tells the device why, with an Extended DNS Error naming the list.
- **Memory:** each pod requests 160Mi and is limited to 384Mi.

### 4. Private by default

- **No query log** (`queryLog: none`): who looked up what isn't written anywhere. `console` sends it to Blocky's output, and so into Loki with bbe-observability ([0006](0006-observability.md)).
- **DNS rebinding protection:** an answer from the upstreams pointing at a private address is refused, so a website can't reach the house's network through a browser. Domains that do this on purpose can be let through (`allowedDomains`). The cluster's own domain, and names in `records` and `forward`, aren't affected.

### 5. Everything is in bbe.yaml, with the defaults written in

The settings are `global.bbe.dns`, which Blocky's config template reads (`templates/_blocky.tpl`), as Blocky's chart only sees the parent's globals. bbe records them in `bbe.yaml` with their defaults (`bbe/recorded-values`), so they're there to read and change:

| Setting | What it changes |
|---|---|
| `upstreams`, `bootstrap` | Where Blocky asks, and how it finds them |
| `blocking.lists` | The lists, by group |
| `blocking.groups` | The groups every device gets |
| `blocking.clients` | Other groups for some devices, by IP, subnet or name. `[]` blocks nothing for one |
| `blocking.allowed` | Domains never blocked, each with everything under it, or `/regexes/` |
| `blocking.refreshPeriod`, `blocking.blockTTL` | How often lists are fetched, and how long a block is remembered |
| `records` | More names Blocky answers itself |
| `forward` | Domains asked of another DNS server, such as the router's |
| `rebindingProtection` | Whether to refuse rebinding answers, and the exceptions |
| `queryLog` | `none` or `console` |

Allowed domains are added to every group that blocks. One allowlist would do, but a device given only that group would be blocked from everything else.

## Consequences

- **The defaults are written into `bbe.yaml` once.** Later changes to bbe's defaults, such as a new list, don't reach a cluster that already recorded them, until its `global.bbe.dns` is changed or removed.
- **Some sites may break**, though Multi Normal rarely does that. The answer names the list that blocked a name, and `blocking.allowed` unblocks it.
- **Devices that pick their own DNS** aren't protected: phones with Private DNS, browsers with DNS-over-HTTPS on, and some smart TVs. Blocky only sees what's asked of it.
- **Blocky downloads about 8MB of lists** every 6 hours per pod, with its two replicas.
- **What's verified:**
  - **Blocky 0.35.0 validated** the configs rendered from the defaults, every setting changed, no groups, a device with `adult`, and an unknown group. It accepts unknown groups, which is why the template refuses them.
  - **Run locally** with the defaults and every setting changed:
    - listed domains and their subdomains got `0.0.0.0`, with the blocking list in the Extended DNS Error;
    - allowed domains resolved;
    - other names resolved over DNS-over-HTTPS through Quad9 and Cloudflare;
    - the cluster's domain, `records` and their subdomains got their addresses;
    - the metrics counted each group's lists.
  - **Unit tests** cover the config, the notes and the memory.
  - **Not run on a cluster yet.**
