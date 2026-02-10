# Jobs Web Manager

Simple web interface to manage `_jobs.json` for clip-pipes.

## Usage

1. Start the web server:
   ```bash
   cd web-manager
   python3 server.py
   ```

2. Open your browser to:
   ```
   http://localhost:8080
   ```

3. Use the interface to:
   - Add/remove job slots
   - Edit job dates and times
   - Add/remove items within jobs
   - Configure video settings (URL, timestamps, position, account, etc.)
   - Save changes to `_jobs.json`

## Features

- **Load/Save**: Reads and writes to `../data/_jobs.json`
- **Validation**: Checks required fields and time formats
- **Backup**: Creates `.json.bak` backup before saving
- **Real-time Preview**: Shows JSON output as you edit
- **Simple Interface**: No glamor, just functional job management

## File Structure

```
web-manager/
├── index.html          # Web interface
├── server.py          # HTTP server with file access
└── README.md          # This file

../data/
└── _jobs.json         # Jobs data file
```

## Security Note

The server only allows access to the `_jobs.json` file in the data directory.
It runs on localhost only by default.