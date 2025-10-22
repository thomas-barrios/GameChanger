# GameChanger Wiki

Welcome to the GameChanger documentation hub! This wiki contains comprehensive guides, references, and resources for GameChanger - the DCS Configuration Manager.

## 📚 Documentation Index

### Quick Start
- **[Commands Reference](commands.md)** - Complete list of all GameChanger commands with examples
- [Installation Guide](#installation-guide) - Get GameChanger up and running
- [Configuration](#configuration) - Customize GameChanger settings
- [Troubleshooting](#troubleshooting) - Common issues and solutions

### Core Features
- [DCS Config Backup & Restore](#dcs-config-backup--restore) - Protect your DCS configurations
- [Windows Services Optimization](#windows-services-optimization) - Optimize system for gaming performance
- [Scheduled Backups](#scheduled-backups) - Automate your backup workflow

### Advanced Topics
- [Command-Line Interface](#command-line-interface) - Power user commands and scripting
- [Configuration Files](#configuration-files) - Deep dive into config options
- [Logging & Debugging](#logging--debugging) - Troubleshoot issues effectively

---

## 🚀 Installation Guide

### Prerequisites
- **Windows 10/11** - Required operating system
- **Python 3.8+** - For running from source (optional if using executable)
- **Administrator privileges** - Required for Windows services management

### Option 1: Pre-built Executable (Recommended)
1. Download GameChanger from the releases page
2. Extract to your preferred location (e.g., `C:\Programs\GameChanger\`)
3. Run from Command Prompt or PowerShell:
   ```powershell
   cd "C:\Programs\GameChanger\dist"
   .\GameChanger.exe --help
   ```

### Option 2: From Source
1. Clone the repository:
   ```powershell
   git clone https://github.com/thomas-barrios/GameChanger.git
   cd GameChanger
   ```

2. Create virtual environment:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Run GameChanger:
   ```powershell
   python src\game_changer.py --help
   ```

---

## ⚙️ Configuration

GameChanger uses `config.ini` for settings. The configuration file is automatically created on first run.

### Default Configuration Locations
- **Executable**: `dist\config.ini`
- **Source**: `src\config.ini`

### Configuration Options

```ini
[DEFAULT]
# Root directory for all backups
backup_root = D:\GameChanger\Backup

# DCS Saved Games location  
saved_games_path = D:\Users\%USERNAME%\Saved Games

# Maximum number of backups to keep (0 = unlimited)
max_backups = 10

# Enable backup compression (not implemented yet)
compress_backups = false

# Logging level (DEBUG, INFO, WARNING, ERROR)
log_level = INFO
```

### Customizing Paths
Edit the configuration to match your system:

1. **Backup Location**: Set `backup_root` to your preferred backup drive
2. **DCS Location**: Update `saved_games_path` if DCS is installed elsewhere
3. **Backup Retention**: Adjust `max_backups` based on available disk space

---

## 💾 DCS Config Backup & Restore

GameChanger automatically backs up critical DCS configuration files including:

- **DCS Settings**: Graphics, controls, gameplay options
- **Module Configurations**: Aircraft-specific settings
- **Input Bindings**: Joystick, keyboard, and HOTAS mappings
- **VR Settings**: Virtual reality configurations
- **Saved Games Data**: Campaigns, missions, logbooks

### Backup Strategy
- **Manual Backups**: Create before major updates or configuration changes
- **Scheduled Backups**: Automatic backups on system login (planned feature)
- **Named Backups**: Tag important configurations with descriptive names

### Restore Options
- **Full Restore**: Complete configuration restoration
- **Selective Restore**: Choose specific files to restore (planned feature)
- **Backup Verification**: Dry-run mode to preview changes

---

## 🔧 Windows Services Optimization

GameChanger includes intelligent Windows services management to optimize system performance for DCS World and other flight simulators.

### Service Categories
- **Safe to Disable**: Services that can be safely stopped for gaming
- **Gaming Optimized**: Services optimized for better performance
- **Keep Running**: Critical services that should remain active
- **VR Specific**: Services important for VR headset functionality

### Optimization Process
1. **Scan**: Analyze current service states
2. **Backup**: Create service configuration backup
3. **Optimize**: Apply gaming-optimized service settings
4. **Monitor**: Track performance impact
5. **Restore**: Revert to original settings if needed

### Safety Features
- **Automatic Backups**: Always backup before optimization
- **Dry-Run Mode**: Preview changes without applying them
- **One-Click Restore**: Quickly revert to previous state
- **Admin Validation**: Ensures proper permissions before changes

---

## 📅 Scheduled Backups

*Note: This feature is planned for a future release.*

Automate your backup workflow with scheduled backups:

- **Login Backups**: Automatic backup when logging into Windows
- **Daily Backups**: Scheduled at specific times
- **Weekly Backups**: Long-term backup retention
- **Pre-Update Backups**: Triggered before DCS updates

---

## 💻 Command-Line Interface

GameChanger provides a powerful command-line interface for advanced users and automation.

### Quick Command Reference
```powershell
# Basic backup
.\GameChanger.exe backup

# Restore from specific backup
.\GameChanger.exe restore --backup-folder "path\to\backup"

# Optimize Windows services
.\GameChanger.exe services optimize

# Scan current services state
.\GameChanger.exe services scan
```

📖 **[Full Commands Reference](commands.md)** - Complete documentation with examples

---

## 📋 Configuration Files

### config.ini Structure
GameChanger uses INI format for configuration with the following sections:

- **[DEFAULT]**: Core application settings
- **[BACKUP]**: Backup-specific options (planned)
- **[SERVICES]**: Service optimization settings (planned)
- **[LOGGING]**: Advanced logging configuration (planned)

### Custom Configuration
You can specify a custom config file:
```powershell
.\GameChanger.exe --config "path\to\custom\config.ini" backup
```

---

## 🐛 Logging & Debugging

### Log Files
GameChanger creates detailed logs for troubleshooting:

- **Location**: `backup_root\logs\`
- **Format**: `gamechanger_YYYY-MM-DD.log`
- **Retention**: 30 days (configurable)

### Debug Mode
Enable verbose logging for detailed troubleshooting:
```powershell
.\GameChanger.exe --verbose backup
```

### Common Debug Scenarios
- **Permission Issues**: Run as Administrator for services commands
- **Path Problems**: Verify configuration file paths
- **DCS Not Found**: Check `saved_games_path` setting
- **Backup Failures**: Ensure sufficient disk space

---

## 🆘 Troubleshooting

### Quick Solutions

**Problem**: "Administrative privileges required"
- **Solution**: Right-click CMD/PowerShell → "Run as administrator"

**Problem**: "Backup folder not found"
- **Solution**: Check `config.ini` backup_root path exists

**Problem**: "Python not found"
- **Solution**: Use pre-built executable or install Python 3.8+

**Problem**: DCS configurations not backed up
- **Solution**: Verify `saved_games_path` in configuration

**Problem**: Services optimization failed
- **Solution**: Ensure no antivirus blocking, run as Administrator

### Getting Help

1. **Check Logs**: Review log files in backup directory
2. **Run with --verbose**: Get detailed operation information  
3. **Use --dry-run**: Preview changes without applying them
4. **GitHub Issues**: Report bugs or request features
5. **Community**: Join DCS communities for user support

---

## 🔗 Additional Resources

- **[GitHub Repository](https://github.com/thomas-barrios/GameChanger)** - Source code and releases
- **[Issue Tracker](https://github.com/thomas-barrios/GameChanger/issues)** - Bug reports and feature requests
- **[Changelog](../README.md)** - Version history and updates
- **[License](../LICENSE)** - Open source license information

---

## 📖 Documentation Navigation

- **[← Back to Main README](../README.md)**
- **[Commands Reference →](commands.md)**

---

*Last Updated: October 22, 2025*