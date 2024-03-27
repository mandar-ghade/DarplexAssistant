The DarplexAssistant package provides utility and mobility for your Plex-server Redis data.
Note that this package is incomplete and unstable, so usage is very limited.

# Usage:
...

# Installation:
...



### `config.toml` configuration:

The `traditional-db-config` setting in `config.toml`:

When set to `True`:
#### Traditional:
Traditional `database-config.dat`:
```
ACCOUNT 127.0.0.1:3306/account root password
PLAYER_STATS 127.0.0.1:3306/PLAYER_STATUS root password
(...)
```
When set to `False`:
#### Custom:
(With custom DBPool)
```
ACCOUNT 127.0.0.1:3306 root password
PLAYER_STATS 127.0.0.1:3306 root password
(...)
```
