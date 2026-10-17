# SpotArchive for Windows

Read-only inventory and SHA-256 verified backups of SpotPlayer download folders. **This is not a video player.** It cannot decrypt protected videos or bypass device license restrictions.

## Run
Windows 10/11, Python 3.10+: `python spotarchive.py`

To create an EXE, open the **Actions** tab and run **Build Windows EXE**, or use `pip install pyinstaller` followed by `pyinstaller --onefile --windowed --name SpotArchive spotarchive.py`.

1. Copy the whole `Android/data/spotplayer.ir/files` folder to the PC. Do not delete originals.
2. Select the PC copy as source and click **Scan**.
3. Export a CSV inventory, or copy to another destination with SHA-256 verification.
4. Keep files on the phone until you have confirmed a working playback solution.

Never publish your license data or course downloads on GitHub.