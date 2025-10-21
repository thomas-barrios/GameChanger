# GameChanger

**GameChanger** is a free, open-source Python app designed to optimize game performance for competitive players, initially focused on *Digital Combat Simulator (DCS)* but expandable to other titles. Built with a PyQt6 UI, it monitors, compares, and backs up configs (Game, VR, Nvidia, Windows), correlating changes to frame times for stutter-free gameplay. Inspired by tools like CapFrameX and Tacview, it's crafted for performance-driven players like those in TACT, SATAL, or JustDogFights servers. As a proud member of HARPIA (3x DCS global champs), I've poured 30 years of optimization expertise into this solo-dev prototype.

## Features Current
- **Config Backup and Restoration**: Configuration backup of relevant DCS files to a backup folder each login

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Quick Install
1. Download and install Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Download GameChanger:
   ```bash
   git clone https://github.com/[YourUsername]/GameChanger.git
   cd GameChanger
   ```
3. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
1. Create or edit `src/config.txt`:
   ```ini
   # Root directory for backups
   BackupRoot=D:\GameChanger\Backup
   
   # Saved Games location
   SavedGamesPath=D:\Users\%USERNAME%\Saved Games
   ```

### Schedule Automatic Backups
1. Open Command Prompt as Administrator
2. Run:
   ```batch
   schtasks /Create /TN "\GameChanger\DCS Config Backup" /TR "\"C:\Projects\GameChanger\venv\Scripts\python.exe\" \"C:\Projects\GameChanger\venv\src\backup.py\"" /SC ONLOGON /RU "%USERNAME%" /RL HIGHEST /F
   ```

### Manual Operation
Run backup manually:
```bash
python src/backup.py
```

## Future Features 
- **Config Management**: Configuration backup, monitoring, and comparison. Backup game configs, VR, Nvidia, and Windows settings.
- **Performance Tracking**: Correlate config changes to frame times for minimal stutters.
- **Keybind & Preset Management**: Save, share, and switch profiles effortlessly.
- **Skin Sharing**: Share and download community-created skins.
- **Community Rankings**: Hardware and performance benchmarks driven by users.
- **Scalable**: Built for DCS, with plans to support other games.

## Requirements
- Python 3.8+
- Additional dependencies in `requirements.txt`

## Contributing
We welcome contributions! Fork the repo, create a branch, and submit a pull request. Check `CONTRIBUTING.md` for guidelines. Join us to revolutionize game optimization!

## License
MIT License - see [LICENSE](LICENSE) for details.

## Roadmap
- Phase 1: Prototype Core Config
- Phase 2: Enhance Config & Basic Manage 
- Phase 3: Performance Integration
- Phase 4: Advanced Manage & Ranking
- Phase 5: Polish & Expand
- Add support for more games (IL-2, MSFS, etc.).
- Integrate advanced analytics for VRAM/CPU usage.
- Build sponsorship, ads or other model for monetization, and project self sustainability.

## Acknowledgments
Inspired by CapFrameX, Tacview, and the DCS competitive community. Built for players chasing the smoothest frames in high-stakes gaming sessions.