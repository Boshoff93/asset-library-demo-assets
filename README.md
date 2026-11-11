# Asset Library demo assets

Sample files for trying the Creator Hub Asset Library, which lists a GitHub repo's files and imports them as Roblox assets.

| Folder | Files | Imports as |
| --- | --- | --- |
| `decals/` | 4 PNG textures, 512 × 512 | Decal |
| `models/` | 3 GLB meshes: crate, pyramid, gem | Model |
| `audio/` | 3 WAV clips: coin pickup, button click, ambient hum | Audio |
| `scripts/` | 1 Luau script | Script |

## License

`tools/generate_assets.py` generates every file here, so all of it is original work. It's dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

To regenerate the files:

```sh
python3 tools/generate_assets.py
```
