# Unimon Control 🎛

Unimon Control is port of [ClickOS Control](https://github.com/sysml/clickos-ctl) into Python. This hopes to make life easier for future edits given the amou t of string handling required from this program...

This currently supports all the same features as the original ClickOS Control so can be used as a stand in replacement. This program does **not** depend on `libxenstore`, but does depend on `pyxs`.

See the README for ClickOS Control [here](https://github.com/sysml/clickos-ctl/blob/master/README.md).

## Installation

Install using pip (for python 3):
```bash
pip install --user unimon-ctl
sudo unimon-ctl -h
```
(script should be added to `~/.local/bin` by default)

Or use with Docker:

```bash
docker run --rm -it -v /var/run/xenstored/socket:/var/run/xenstored/socket willfantom/unimon-ctl -h
```

## Re-Implemented ClickOS-Ctl Features

- Use xenstore to communicate with clickos instance ✅
- Install/Remove click configs to clickos domains ✅
  - via `install`/`remove` sub commands
- Start/Stop clickos routers ✅
  - via `start`/`stop` sub commands

## Added Features

- Get list of clickos domain's routers and states ✅
  - via `list` sub command
- Check state of specific router ✅
  - via `state` sub command
- Prints some emoji ✅
- Pythony (can be installed via `pip`) 🐍
- Dockery (can be ran using Docker) 🐳

## Notice

This has been made as part of my PhD work, so will not be maintained beyond the feature set I require.