<a href="https://clustta.com">
  <img src="./assets/clustta-logo.svg" alt="Clustta" style="width: 60px; height: 60px;" />
</a>

# Clustta Blender Addon

Blender addon for [Clustta](https://clustta.com) - version control, collaboration and asset management for creative work.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## About

This addon brings Clustta's version control and collaboration features directly into Blender. It is a thin UI shell that communicates with a local **Clustta Agent** over HTTP - all heavy lifting (file chunking, protobuf serialization, zstd compression, keyring access, SQLite) is handled by the agent. The addon only sends and receives JSON.

## Requirements

- **Blender 4.3+** (uses the new Extensions / `blender_manifest.toml` format)
- **Clustta Agent** running on localhost (a Go binary shipped with the Clustta desktop app or installed standalone)

## Installation

1. Open Blender > **Edit > Preferences > Get Extensions**
2. Use **Install from Disk** and select the `clustta-blender-addon` folder (or a packaged `.zip`)
3. Enable the **Clustta** addon

The addon will appear as a **"Clustta"** tab in the 3D Viewport sidebar (`N` panel).

## Features

- **Account & Studio Switching** - Browse and switch between accounts stored in the OS keyring, and select a studio to work with.
- **Project Browser** - View and switch between projects in the active studio.
- **Asset Viewer** - Browse Blender assets assigned to you, with file state indicators (synced, modified, missing, outdated).
- **Checkpoint History** - View the version history of any asset.
- **Create Checkpoints** - Save new versions of your work and push them to the studio server, all from within Blender.
- **Auto-Launch Agent** - The addon automatically starts the Clustta Agent if it isn't already running.

## Roadmap

- Sync directly with server for remote studios
- Integrations with Kitsu/ftrack and other production trackers
- Update asset status from within Blender
- Fetch and browse through asset dependencies
- Link/build scenes based on dependency mapping
- One-click render playblast/image and send to tracker

## Components

This addon is part of the Clustta ecosystem:

1. **[Clustta Studio](https://github.com/eaxum/clustta-studio)** - Studio/team management server
2. **[Clustta Client](https://github.com/eaxum/clustta-client)** - Desktop application & agent
3. **Clustta Blender Addon** (this repository) - Blender integration

## Contributing

There are many ways to contribute, from reporting bugs to submitting code. See the [contributing guide](Contributing.md) for details.

Visit [https://clustta.com](https://clustta.com) for more information about Clustta.

## License

Clustta Blender Addon is released under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## About Authors

Clustta is developed by [Eaxum](https://eaxum.com), a computer animation studio based in Nigeria.

<a href="https://eaxum.com">
  <img src="./assets/eaxum-logo.gif" alt="Eaxum" style="height: 100px" />
</a>
