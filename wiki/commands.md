# GameChanger Commands Reference

GameChanger is a DCS Configuration Manager that provides backup, restore, and Windows services optimization functionality.

## Installation & Setup

### Prerequisites
- Python 3.8+ (for source)
- Windows 10/11
- Administrator privileges (for services commands)

### Running GameChanger

#### Option 1: Pre-built Executable
```cmd
# CMD
cd /d "C:\Projects\GameChanger\dist"
GameChanger.exe --help

# PowerShell
Set-Location "C:\Projects\GameChanger\dist"
.\GameChanger.exe --help
```

#### Option 2: Python Source
```cmd
# CMD
cd /d "C:\Projects\GameChanger"
python src\game_changer.py --help

# PowerShell
Set-Location "C:\Projects\GameChanger"
python src\game_changer.py --help
```

## Global Options

All commands support these global options:

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable detailed logging |
| `-c, --config <path>` | Custom config file path |
| `-d, --dry-run` | Test run without making changes |
| `-f, --force` | Override warnings |
| `-h, --help` | Show help message |

## Main Commands

### 1. Backup Command
Creates a backup of DCS configuration files.

**Syntax:**
```
GameChanger.exe backup [--name <backup_name>]
```

**Options:**
- `--name <backup_name>`: Custom backup name (optional)

**Examples:**

**CMD:**
```cmd
# Basic backup
GameChanger.exe backup

# Backup with custom name
GameChanger.exe backup --name "pre-update-backup"

# Verbose backup with dry-run
GameChanger.exe backup --verbose --dry-run

# Full path execution
"C:\Projects\GameChanger\dist\GameChanger.exe" backup --name "test-backup"
```

**PowerShell:**
```powershell
# Basic backup
.\GameChanger.exe backup

# Backup with custom name
.\GameChanger.exe backup --name "pre-update-backup"

# Verbose backup with dry-run
.\GameChanger.exe backup --verbose --dry-run

# Full path execution
& "C:\Projects\GameChanger\dist\GameChanger.exe" backup --name "test-backup"
```

### 2. Restore Command
Restores DCS configuration files from a backup.

**Syntax:**
```
GameChanger.exe restore --backup-folder <path>
```

**Required Options:**
- `--backup-folder <path>`: Path to backup folder to restore from

**Examples:**

**CMD:**
```cmd
# Restore from specific backup
GameChanger.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-22_14-30-00"

# Dry-run restore
GameChanger.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-22_14-30-00" --dry-run

# Verbose restore
GameChanger.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-22_14-30-00" --verbose
```

**PowerShell:**
```powershell
# Restore from specific backup
.\GameChanger.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-22_14-30-00"

# Dry-run restore
.\GameChanger.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-22_14-30-00" --dry-run

# Verbose restore
.\GameChanger.exe restore --backup-folder "D:\GameChanger\Backup\2025-10-22_14-30-00" --verbose
```

### 3. Services Commands
Manages Windows services for DCS optimization.

#### 3.1 Services Scan
Scans current Windows services state.

**Syntax:**
```
GameChanger.exe services scan
```

**Examples:**

**CMD:**
```cmd
# Scan services
GameChanger.exe services scan

# Verbose scan
GameChanger.exe services scan --verbose
```

**PowerShell:**
```powershell
# Scan services
.\GameChanger.exe services scan

# Verbose scan
.\GameChanger.exe services scan --verbose
```

#### 3.2 Services Backup
Backs up current Windows services configuration.

**Syntax:**
```
GameChanger.exe services backup [--backup-folder <path>]
```

**Options:**
- `--backup-folder <path>`: Custom backup folder (optional)

**Examples:**

**CMD:**
```cmd
# Backup services to default location
GameChanger.exe services backup

# Backup to custom folder
GameChanger.exe services backup --backup-folder "D:\MyBackups\Services"

# Dry-run services backup
GameChanger.exe services backup --dry-run
```

**PowerShell:**
```powershell
# Backup services to default location
.\GameChanger.exe services backup

# Backup to custom folder
.\GameChanger.exe services backup --backup-folder "D:\MyBackups\Services"

# Dry-run services backup
.\GameChanger.exe services backup --dry-run
```

#### 3.3 Services List Backups
Lists available service backup files.

**Syntax:**
```
GameChanger.exe services list-backups
```

**Examples:**

**CMD:**
```cmd
# List available service backups
GameChanger.exe services list-backups
```

**PowerShell:**
```powershell
# List available service backups
.\GameChanger.exe services list-backups
```

#### 3.4 Services Optimize
Optimizes Windows services for gaming performance.

**Syntax:**
```
GameChanger.exe services optimize [--backup-folder <path>]
```

**Options:**
- `--backup-folder <path>`: Custom backup folder before optimization (optional)

**Examples:**

**CMD:**
```cmd
# Optimize services (creates backup first)
GameChanger.exe services optimize

# Optimize with custom backup location
GameChanger.exe services optimize --backup-folder "D:\MyBackups\Services"

# Dry-run optimization
GameChanger.exe services optimize --dry-run

# Force optimization (skip warnings)
GameChanger.exe services optimize --force
```

**PowerShell:**
```powershell
# Optimize services (creates backup first)
.\GameChanger.exe services optimize

# Optimize with custom backup location
.\GameChanger.exe services optimize --backup-folder "D:\MyBackups\Services"

# Dry-run optimization
.\GameChanger.exe services optimize --dry-run

# Force optimization (skip warnings)
.\GameChanger.exe services optimize --force
```

#### 3.5 Services Restore
Restores Windows services from a backup file.

**Syntax:**
```
GameChanger.exe services restore --backup-file <path>
```

**Required Options:**
- `--backup-file <path>`: Path to services backup file

**Examples:**

**CMD:**
```cmd
# Restore services from backup
GameChanger.exe services restore --backup-file "D:\GameChanger\Backup\services_backup_2025-10-22_14-30-00.json"

# Dry-run restore
GameChanger.exe services restore --backup-file "D:\GameChanger\Backup\services_backup_2025-10-22_14-30-00.json" --dry-run

# Verbose restore
GameChanger.exe services restore --backup-file "D:\GameChanger\Backup\services_backup_2025-10-22_14-30-00.json" --verbose
```

**PowerShell:**
```powershell
# Restore services from backup
.\GameChanger.exe services restore --backup-file "D:\GameChanger\Backup\services_backup_2025-10-22_14-30-00.json"

# Dry-run restore
.\GameChanger.exe services restore --backup-file "D:\GameChanger\Backup\services_backup_2025-10-22_14-30-00.json" --dry-run

# Verbose restore
.\GameChanger.exe services restore --backup-file "D:\GameChanger\Backup\services_backup_2025-10-22_14-30-00.json" --verbose
```

### 4. Schedule Command
*Note: This command is planned but not yet implemented.*

**Syntax:**
```
GameChanger.exe schedule [--preset <preset>] [--time <time>]
```

**Options:**
- `--preset <preset>`: Schedule preset (atlogon, daily, weekly)
- `--time <time>`: Time for daily/weekly backups (HH:MM format)

## Command Combinations & Workflows

### Typical Backup Workflow
```cmd
# 1. Create a backup before making changes
GameChanger.exe backup --name "before-tweaks"

# 2. Optimize services for gaming
GameChanger.exe services optimize

# 3. If issues occur, restore from backup
GameChanger.exe restore --backup-folder "D:\GameChanger\Backup\before-tweaks_2025-10-22_14-30-00"
```

### Service Management Workflow
```cmd
# 1. Scan current services
GameChanger.exe services scan --verbose

# 2. Backup current service state
GameChanger.exe services backup

# 3. Optimize services
GameChanger.exe services optimize

# 4. If needed, restore services
GameChanger.exe services restore --backup-file "D:\GameChanger\Backup\services_backup_2025-10-22_14-30-00.json"
```

## Administrative Requirements

**Services commands require Administrator privileges:**
- `services scan`
- `services backup`
- `services optimize`
- `services restore`

**To run as Administrator:**

**CMD:**
```cmd
# Right-click Command Prompt → "Run as administrator"
cd /d "C:\Projects\GameChanger\dist"
GameChanger.exe services scan
```

**PowerShell:**
```powershell
# Right-click PowerShell → "Run as administrator"
Set-Location "C:\Projects\GameChanger\dist"
.\GameChanger.exe services scan
```

## Configuration

GameChanger uses `config.ini` for configuration. Default locations:
- Executable: `C:\Projects\GameChanger\dist\config.ini`
- Source: `C:\Projects\GameChanger\src\config.ini`

**Example config.ini:**
```ini
[DEFAULT]
backup_root = D:\GameChanger\Backup
saved_games_path = D:\Users\%USERNAME%\Saved Games
max_backups = 10
compress_backups = false
log_level = INFO
```

## Troubleshooting

### Common Issues

1. **"Administrative privileges required"**
   - Run CMD/PowerShell as Administrator for services commands

2. **"Command not found"**
   - Ensure you're in the correct directory
   - Use full path to executable

3. **Python not found (source version)**
   - Install Python 3.8+ or use the pre-built executable

4. **Backup folder not found**
   - Check config.ini for correct backup paths
   - Ensure backup folder exists

### Debug Mode
Use `--verbose` flag for detailed logging:
```cmd
GameChanger.exe backup --verbose
GameChanger.exe services optimize --verbose --dry-run
```