# GameChanger

## Mission Statement
In the high-stakes world of DCS World competitive play where every frame counts, a single stutter can lose a match in TACT, SATAL, or JustDogFights. Yet, optimizing DCS is a nightmare: configs sprawl across DCS folders, VR headsets, Nvidia Control Panel, and Windows settings. Tweaking one risks breaking another, and tracking what works is a manual slog.

GameChanger is the solution: a free, open-source tool to streamline config management, boost performance, and unite the community around shared knowledge—no more guesswork, just precision.

## Current Features
- **Config Backup and Restoration**: Automatic backup of DCS configuration files
- **Performance Impact Analysis**: Detailed analysis of configuration changes and their gaming performance impact
- **Windows Services Optimization**: Gaming-focused Windows services management
- **Performance Correlation Framework**: Track and correlate configuration changes with performance metrics

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Installation
1. Download and install Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Clone GameChanger:
   ```powershell
   git clone https://github.com/[YourUsername]/GameChanger.git
   cd GameChanger
   ```
3. Create virtual environment:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Configuration
1. Create or edit `src/config.ini`:
   ```ini
   [DEFAULT]
   backup_root = D:\GameChanger\Backup
   saved_games_path = D:\Users\%USERNAME%\Saved Games
   max_backups = 10
   compress_backups = false
   log_level = INFO
   ```

### Usage
#### Basic Commands
```powershell
# Create backup
python src/game_changer.py backup

# Analyze performance impact between backups
python src/game_changer.py compare --latest

# Optimize Windows services for gaming
python src/game_changer.py services optimize
"C:\Projects\GameChanger\venv\Scripts\python.exe" "C:\Projects\GameChanger\venv\src\backup.py"
```

### Automatic Backups
Set up automatic backups on login:
```powershell
# Run as Administrator
schtasks /Create /TN "\GameChanger\DCS Config Backup" /TR "\"C:\Projects\GameChanger\venv\Scripts\python.exe\" \"C:\Projects\GameChanger\venv\src\backup.py\"" /SC ONLOGON /RU "%USERNAME%" /RL HIGHEST /F
```

## Roadmap

### Phase 1 (Current)
- ✓ CLI prototype for config backup/restore
- CLI installation
- ⧖ Change monitoring
- ⧖ Basic diff UI

### Phase 2
- PyQt6 UI for Config tab
- Keybind/preset import/export
- JSON bundle support

### Phase 3
- Performance correlation
- Hardware ranking
- Frame time analysis

### Phase 4
- Skin sharing
- Player rankings
- Tacview integration

### Phase 5
- Multi-game support
- Community features
- Optional cloud sync

## Future Features

### Performance
- VR Auto-Tuning
- Real-Time Overlays
- Hardware Benchmark DB

### Community
- Cloud Config Sync
- AI-Powered Suggestions
- Forum Integration

### Advanced Features
- Mod Management
- Tacview Analytics
- Multi-Game Support

## Contributing
We welcome contributions! Fork the repo, create a branch, and submit a pull request. Check `CONTRIBUTING.md` for guidelines. Join us to revolutionize game optimization!

## License
MIT License - See [LICENSE](LICENSE) for details

## CLI Reference

### Basic Usage
```powershell
game-changer.exe [global-options] command [command-options]
```

### Global Options
```
-v, --verbose        Enable detailed logging
-c, --config PATH    Use alternative config file
-d, --dry-run       Test run without making changes
-f, --force         Override warnings
-h, --help          Show help message
```

### Commands

#### Backup
Create new backup
```powershell
game-changer.exe backup [--name NAME]

Examples:
  game-changer.exe backup
  game-changer.exe backup --name "pre-update"
  game-changer.exe -v backup  # Verbose mode
```

#### Restore
Restore from backup
```powershell
game-changer.exe restore --backup-folder PATH

Examples:
  game-changer.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-21-backup"
  game-changer.exe -f restore --backup-folder "path"  # Force restore
```

#### Schedule
Configure scheduled backups
```powershell
game-changer.exe schedule --preset PRESET [--time HH:MM]

Presets:
  atlogon    Run at user login (default)
  daily      Run daily at 12:00
  weekly     Run weekly on Sunday at 12:00

Examples:
  game-changer.exe schedule --preset atlogon
  game-changer.exe schedule --preset daily --time 23:00
```

#### Configure
Edit configuration
```powershell
game-changer.exe configure [options]

Options:
  --backup-root PATH     Set backup root directory
  --saved-games PATH    Set saved games directory

Examples:
  game-changer.exe configure --backup-root "D:\Backups"
  game-changer.exe -d configure  # Test configuration
```

### Configuration File Format

#### Location
The configuration file is located at:
- Default: `src/config.txt`
- Custom: Specify with `--config PATH`

#### Format
```ini
# GameChanger Configuration File
# Lines starting with # are comments
# Use Windows-style paths with forward or backslashes
# Environment variables like %USERNAME% are supported

# Required Settings
BackupRoot=D:\GameChanger\Backup        # Root folder for all backups
SavedGamesPath=D:\Users\%USERNAME%\Saved Games    # DCS saved games location

# Optional Settings
LogLevel=INFO          # DEBUG, INFO, WARNING, ERROR
MaxBackups=10         # Maximum number of backups to keep
CompressBackups=false # Enable backup compression
```

#### Environment Variables
The following environment variables are supported:
- `%USERNAME%` - Current Windows username
- `%USERPROFILE%` - User's home directory
- `%PROGRAMDATA%` - Windows ProgramData folder
- `%LOCALAPPDATA%` - User's local app data

#### Examples
```ini
# Minimal configuration
BackupRoot=D:\GameChanger\Backup
SavedGamesPath=D:\Users\%USERNAME%\Saved Games

# Full configuration with all options
BackupRoot=D:\GameChanger\Backup
SavedGamesPath=D:\Users\%USERNAME%\Saved Games
LogLevel=DEBUG
MaxBackups=20
CompressBackups=true
```

#### Validation
- Paths must be absolute
- Directories must be writable
- Invalid settings will fall back to defaults
- Use `--dry-run` to test configuration

### Exit Codes
```
0   Success
1   General error
2   Configuration error
3   Permission error
4   File system error
```

## Building from Source

### Prerequisites
- Python 3.8 or higher
- Windows 10/11
- Git (optional)

### Build Steps
1. Clone or download the repository:
   ```powershell
   git clone https://github.com/[YourUsername]/GameChanger.git
   cd GameChanger
   ```

2. Run the build script:
   ```powershell
   cd scripts
   .\build.bat
   ```

3. Find the executable in `dist\game-changer.exe`

### Testing the Build
```powershell
# Test backup
.\dist\game-changer.exe backup --dry-run

# Test restore
.\dist\game-changer.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-21-backup" --dry-run

# Show help
.\dist\game-changer.exe --help
```