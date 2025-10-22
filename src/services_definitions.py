"""
GameChanger Services Definitions
Windows services categorized by gaming impact with detailed rationale
"""

from typing import Dict, List, NamedTuple


class ServiceDefinition(NamedTuple):
    """Service definition with gaming performance rationale"""
    internal_name: str
    display_name: str
    category: str
    gaming_rationale: str
    group: str


# Service definitions organized by impact on gaming performance
SERVICES_DATABASE = [
    # === SAFE TO DISABLE ===
    # Telemetry & Diagnostics
    ServiceDefinition(
        "DiagTrack", 
        "Connected User Experiences and Telemetry",
        "SafeToDisable",
        "Collects usage data; no gaming benefit, reduces CPU/network overhead",
        "Telemetry & Diagnostics"
    ),
    ServiceDefinition(
        "DPS", 
        "Diagnostic Policy Service",
        "SafeToDisable", 
        "Problem detection scanning; resource-intensive during gameplay",
        "Telemetry & Diagnostics"
    ),
    ServiceDefinition(
        "WdiServiceHost", 
        "Diagnostic Service Host",
        "SafeToDisable",
        "Background diagnostics can cause micro-stutters during gaming",
        "Telemetry & Diagnostics"
    ),
    ServiceDefinition(
        "WdiSystemHost", 
        "Diagnostic System Host",
        "SafeToDisable",
        "System diagnostics create unnecessary CPU overhead during gaming",
        "Telemetry & Diagnostics"
    ),
    
    # Cloud & Microsoft Services
    ServiceDefinition(
        "WalletService", 
        "WalletService",
        "SafeToDisable",
        "Payment/wallet management; irrelevant for gaming performance",
        "Cloud & Microsoft Services"
    ),
    ServiceDefinition(
        "AssignedAccessManagerSvc", 
        "AssignedAccessManager Service",
        "SafeToDisable",
        "Kiosk mode support; enterprise feature not needed for gaming",
        "Cloud & Microsoft Services"
    ),
    
    # Fax & Legacy
    ServiceDefinition(
        "Fax", 
        "Fax",
        "SafeToDisable",
        "Obsolete fax services; never used in modern gaming setups",
        "Fax & Legacy"
    ),
    
    # Media & Entertainment
    ServiceDefinition(
        "MapsBroker", 
        "Downloaded Maps Manager",
        "SafeToDisable",
        "Offline maps management; irrelevant for desktop gaming",
        "Media & Entertainment"
    ),
    
    # Hardware Support
    ServiceDefinition(
        "RtkUWPService", 
        "Realtek Audio Universal Service",
        "SafeToDisable",
        "Realtek audio management; can conflict with gaming audio drivers",
        "Hardware Support"
    ),
    ServiceDefinition(
        "TobiiVRService", 
        "Tobii VR4PIMAXP3B Platform Runtime",
        "SafeToDisable",
        "Tobii eye tracking; disable if not using Tobii hardware",
        "Hardware Support"
    ),
    
    # Remote Access
    ServiceDefinition(
        "RemoteRegistry", 
        "Remote Registry",
        "SafeToDisable",
        "Remote registry editing; security risk and unnecessary for local gaming",
        "Remote Access"
    ),
    ServiceDefinition(
        "TermService", 
        "Remote Desktop Services",
        "SafeToDisable",
        "RDP connections; unneeded for local gaming, reduces attack surface",
        "Remote Access"
    ),
    
    # Backup & Sync
    ServiceDefinition(
        "fhsvc", 
        "File History Service",
        "SafeToDisable",
        "File backup creates heavy disk I/O that competes with game loading",
        "Backup & Sync"
    ),
    ServiceDefinition(
        "WorkFolders", 
        "Work Folders",
        "SafeToDisable",
        "Enterprise file sync; unused in gaming, removes sync timers",
        "Backup & Sync"
    ),
    
    # Network Discovery
    ServiceDefinition(
        "SSDPSRV", 
        "SSDP Discovery",
        "SafeToDisable",
        "UPnP/SSDP discovery; cuts broadcast traffic and CPU wakeups",
        "Network Discovery"
    ),
    ServiceDefinition(
        "UPnPHost", 
        "UPnP Device Host",
        "SafeToDisable",
        "Hosts UPnP devices; no UPnP device hosting needed for gaming",
        "Network Discovery"
    ),
    ServiceDefinition(
        "FDResPub", 
        "Function Discovery Provider Host",
        "SafeToDisable",
        "Network discovery providers; no network device discovery required",
        "Network Discovery"
    ),
    
    # Location & Sensors
    ServiceDefinition(
        "lfsvc", 
        "Geolocation Service",
        "SafeToDisable",
        "Location & geofences; not used in gaming, avoids periodic checks",
        "Location & Sensors"
    ),
    ServiceDefinition(
        "SensorService", 
        "Sensor Service",
        "SafeToDisable",
        "Manages sensors; desktops lack sensors, removes polling overhead",
        "Location & Sensors"
    ),
    ServiceDefinition(
        "SensrSvc", 
        "Sensor Monitoring Service",
        "SafeToDisable",
        "Monitors sensors; unnecessary for gaming desktop",
        "Location & Sensors"
    ),
    ServiceDefinition(
        "SensorDataService", 
        "Sensor Data Service",
        "SafeToDisable",
        "Delivers sensor data; no sensors used in gaming setup",
        "Location & Sensors"
    ),
    
    # Xbox Services  
    ServiceDefinition(
        "XblAuthManager", 
        "Xbox Live Auth Manager",
        "SafeToDisable",
        "Xbox Live authentication; not used by most PC games",
        "Xbox Services"
    ),
    ServiceDefinition(
        "XblGameSave", 
        "Xbox Live Game Save",
        "SafeToDisable",
        "Cloud saves sync; most PC games don't use Xbox Live saves",
        "Xbox Services"
    ),
    ServiceDefinition(
        "XboxNetApiSvc", 
        "Xbox Live Networking Service",
        "SafeToDisable",
        "Xbox networking API; unused by most PC games, reduces network overhead",
        "Xbox Services"
    ),
    ServiceDefinition(
        "XboxGipSvc", 
        "Xbox Accessory Management Service",
        "SafeToDisable",
        "Manages Xbox accessories; disable if not using Xbox controllers",
        "Xbox Services"
    ),
    
    # Telephony
    ServiceDefinition(
        "PhoneSvc", 
        "Phone Service",
        "SafeToDisable",
        "Telephony state management; desktop without telephony",
        "Telephony"
    ),
    ServiceDefinition(
        "MessagingService_50b27", 
        "MessagingService_50b27",
        "SafeToDisable",
        "Text messaging support; not used in gaming setup",
        "Telephony"
    ),
    
    # Insider Program
    ServiceDefinition(
        "wisvc", 
        "Windows Insider Service",
        "SafeToDisable",
        "Windows Insider Program; not needed for stable gaming rig",
        "Insider Program"
    ),
    
    # WebDAV
    ServiceDefinition(
        "WebClient", 
        "WebClient",
        "SafeToDisable",
        "WebDAV filesystem; avoids WebDAV reconnects and network overhead",
        "WebDAV"
    ),
    
    # Imaging
    ServiceDefinition(
        "stisvc", 
        "Windows Image Acquisition (WIA)",
        "SafeToDisable",
        "Scanner/camera acquisition; no scanning/capturing needed for gaming",
        "Imaging"
    ),
    
    # Third-Party
    ServiceDefinition(
        "GoogleUpdaterService142.0.7416.0", 
        "Google Updater Service",
        "SafeToDisable",
        "Google software updates; not needed for gaming performance",
        "Third-Party"
    ),
    ServiceDefinition(
        "GoogleUpdaterInternalService142.0.7416.0", 
        "Google Updater Internal Service",
        "SafeToDisable",
        "Google software updates; not needed for gaming performance",
        "Third-Party"
    ),
    ServiceDefinition(
        "AsusUpdateCheck", 
        "AsusUpdateCheck",
        "SafeToDisable",
        "ASUS update service; manual updates sufficient for gaming",
        "Third-Party"
    ),
    
    # File Tracking
    ServiceDefinition(
        "TrkWks", 
        "Distributed Link Tracking Client",
        "SafeToDisable",
        "Maintains NTFS links; no benefit for single-user gaming PC",
        "File Tracking"
    ),
    
    # Retail Demo
    ServiceDefinition(
        "RetailDemo", 
        "Retail Demo Service",
        "SafeToDisable",
        "Retail demo behaviors; consumer feature unnecessary for gaming",
        "Retail Demo"
    ),

    # === OPTIONAL TO DISABLE ===
    # Power Management
    ServiceDefinition(
        "power", 
        "Power",
        "OptionalToDisable",
        "CAUTION: Can cause stutters in VR/high-performance gaming due to power state changes",
        "Power Management"
    ),
    
    # Windows Updates
    ServiceDefinition(
        "UsoSvc", 
        "Update Orchestrator Service",
        "OptionalToDisable",
        "Background updates hurt network/CPU during gameplay; user choice",
        "Windows Updates"
    ),
    ServiceDefinition(
        "TrustedInstaller", 
        "Windows Modules Installer",
        "OptionalToDisable",
        "Can trigger during gameplay causing stutters; affects Windows updates",
        "Windows Updates"
    ),
    ServiceDefinition(
        "WaaSMedicSvc", 
        "WaaSMedicSvc",
        "OptionalToDisable",
        "Windows Update repair service; redundant for gaming sessions",
        "Windows Updates"
    ),
    
    # Cloud & Microsoft Services
    ServiceDefinition(
        "wlidsvc", 
        "Microsoft Account Sign-in Assistant",
        "OptionalToDisable",
        "Microsoft account auth; if using local account, unnecessary cloud sync",
        "Cloud & Microsoft Services"
    ),
    
    # Printer Services
    ServiceDefinition(
        "Spooler", 
        "Print Spooler",
        "OptionalToDisable",
        "Print job spooling; disable if no printing needed during gaming",
        "Printer Services"
    ),
    ServiceDefinition(
        "PrintNotify", 
        "Printer Extensions and Notifications",
        "OptionalToDisable",
        "Printer dialogs; unnecessary overhead if no printing",
        "Printer Services"
    ),
    ServiceDefinition(
        "PrintWorkflowUserSvc_50b27", 
        "PrintWorkflow_50b27",
        "OptionalToDisable",
        "Print workflow support; not needed for gaming",
        "Printer Services"
    ),
    
    # Search & Indexing
    ServiceDefinition(
        "WSearch", 
        "Windows Search",
        "OptionalToDisable",
        "File indexing creates heavy disk I/O that competes with game loading",
        "Search & Indexing"
    ),
    
    # Media & Entertainment
    ServiceDefinition(
        "BcastDVRUserService_50b27", 
        "GameDVR and Broadcast User Service_50b27",
        "OptionalToDisable",
        "Game capture/broadcast; can cause frame drops and input lag during gaming",
        "Media & Entertainment"
    ),
    
    # Hardware Support
    ServiceDefinition(
        "AmdPmuService", 
        "AMD 3D V-Cache Performance Optimizer Service",
        "OptionalToDisable",
        "AMD thread optimization; some games use own optimization that may conflict",
        "Hardware Support"
    ),
    ServiceDefinition(
        "AmdAcpSvc", 
        "AMD Application Compatibility Database Service",
        "OptionalToDisable",
        "AMD compatibility database; not needed for most modern games",
        "Hardware Support"
    ),
    ServiceDefinition(
        "AmdPPService", 
        "AMD Provisioning Packages Service",
        "OptionalToDisable",
        "AMD power management; manual game settings often provide better control",
        "Hardware Support"
    ),
    
    # Parental Controls
    ServiceDefinition(
        "WPCSvc", 
        "Parental Controls",
        "OptionalToDisable",
        "Family safety features; not needed for competitive gaming",
        "Parental Controls"
    ),

    # === DO NOT DISABLE ===
    # General System Services
    ServiceDefinition(
        "DCOMLaunch", 
        "DCOM Server Process Launcher",
        "DoNotDisable",
        "CRITICAL: COM/DCOM server launcher - many games crash without it",
        "General System Services"
    ),
    ServiceDefinition(
        "RpcSs", 
        "Remote Procedure Call (RPC)",
        "DoNotDisable",
        "CORE SYSTEM: RPC communication - system fails without it",
        "General System Services"
    ),
    ServiceDefinition(
        "PlugPlay", 
        "Plug and Play",
        "DoNotDisable",
        "REQUIRED: Hardware detection for gaming controllers and peripherals",
        "General System Services"
    ),
    ServiceDefinition(
        "Winmgmt", 
        "Windows Management Instrumentation",
        "DoNotDisable",
        "REQUIRED: System monitoring for game telemetry and system stability",
        "General System Services"
    ),
    ServiceDefinition(
        "Appinfo", 
        "Application Information",
        "DoNotDisable",
        "REQUIRED: Admin privileges for apps - games may require elevated access",
        "General System Services"
    ),
    ServiceDefinition(
        "ProfSvc", 
        "User Profile Service",
        "DoNotDisable",
        "REQUIRED: Loads/unloads user profiles - essential for user login",
        "General System Services"
    ),
    ServiceDefinition(
        "LSM", 
        "Local Session Manager",
        "DoNotDisable",
        "CORE SYSTEM: Manages user sessions - system instability if disabled",
        "General System Services"
    ),
    ServiceDefinition(
        "SENS", 
        "System Event Notification Service",
        "DoNotDisable",
        "REQUIRED: Monitors system events, COM+ event handling for applications",
        "General System Services"
    ),
    ServiceDefinition(
        "Schedule", 
        "Task Scheduler",
        "DoNotDisable",
        "REQUIRED: Schedules system-critical automated tasks",
        "General System Services"
    ),
    ServiceDefinition(
        "SamSs", 
        "Security Accounts Manager",
        "DoNotDisable",
        "CORE SYSTEM: Manages security accounts, login and security",
        "General System Services"
    ),
    
    # Network Services
    ServiceDefinition(
        "Dhcp", 
        "DHCP Client",
        "DoNotDisable",
        "CRITICAL: Assigns IP addresses - essential for online multiplayer",
        "Network Services"
    ),
    ServiceDefinition(
        "Dnscache", 
        "DNS Client",
        "DoNotDisable",
        "CRITICAL: Resolves DNS queries - essential for online multiplayer",
        "Network Services"
    ),
    ServiceDefinition(
        "netprofm", 
        "Network List Service",
        "DoNotDisable",
        "REQUIRED: Identifies network connections for WiFi/Ethernet stability",
        "Network Services"
    ),
    ServiceDefinition(
        "NlaSvc", 
        "Network Location Awareness",
        "DoNotDisable",
        "REQUIRED: Collects network configuration for connectivity",
        "Network Services"
    ),
    ServiceDefinition(
        "nsi", 
        "Network Store Interface Service",
        "DoNotDisable",
        "REQUIRED: Delivers network notifications for connectivity",
        "Network Services"
    ),
    ServiceDefinition(
        "Wlansvc", 
        "WLAN AutoConfig",
        "DoNotDisable",
        "CRITICAL: Configures WiFi connections for multiplayer",
        "Network Services"
    ),
    ServiceDefinition(
        "WinHttpAutoProxySvc", 
        "WinHTTP Web Proxy Auto-Discovery Service",
        "DoNotDisable",
        "REQUIRED: Proxy discovery for network connectivity",
        "Network Services"
    ),
    ServiceDefinition(
        "NcbService", 
        "Network Connection Broker",
        "DoNotDisable",
        "REQUIRED: Brokers app network connections for DCS stability",
        "Network Services"
    ),
    
    # Graphics & Display
    ServiceDefinition(
        "DispSvc", 
        "Display Policy Service",
        "DoNotDisable",
        "REQUIRED: Manages display configurations for multi-monitor and VR setups",
        "Graphics & Display"
    ),
    ServiceDefinition(
        "ShellHWDetection", 
        "Shell Hardware Detection",
        "DoNotDisable",
        "REQUIRED: USB and hardware event detection for controllers and peripherals",
        "Graphics & Display"
    ),
    
    # Audio Services
    ServiceDefinition(
        "AudioSrv", 
        "Windows Audio",
        "DoNotDisable",
        "REQUIRED: Manages audio for headsets and speakers",
        "Audio Services"
    ),
    ServiceDefinition(
        "AudioEndpointBuilder", 
        "Windows Audio Endpoint Builder",
        "DoNotDisable",
        "REQUIRED: Manages audio devices for audio stability",
        "Audio Services"
    ),
    
    # USB & Device Services
    ServiceDefinition(
        "hidserv", 
        "Human Interface Device Service",
        "DoNotDisable",
        "REQUIRED: Supports HID devices like gaming controllers and keyboards",
        "USB & Device Services"
    ),
    ServiceDefinition(
        "DeviceAssociationService", 
        "Device Association Service",
        "DoNotDisable",
        "REQUIRED: Device pairing for USB devices and wireless peripherals",
        "USB & Device Services"
    ),
    ServiceDefinition(
        "DeviceInstall", 
        "Device Install Service",
        "DoNotDisable",
        "REQUIRED: Installs device drivers for controller and peripheral stability",
        "USB & Device Services"
    ),
    
    # Time & Sync
    ServiceDefinition(
        "W32Time", 
        "Windows Time",
        "DoNotDisable",
        "REQUIRED: Time synchronization for multiplayer server sync",
        "Time & Sync"
    ),
    
    # Security
    ServiceDefinition(
        "WinDefend", 
        "Windows Defender Antivirus Service",
        "DoNotDisable",
        "SECURITY: Essential malware protection for system safety",
        "Security"
    ),
    ServiceDefinition(
        "MpsSvc", 
        "Windows Defender Firewall",
        "DoNotDisable",
        "SECURITY: Network firewall protection for online gaming security",
        "Security"
    ),
    
    # Microsoft Store
    ServiceDefinition(
        "ClipSVC", 
        "Client License Service",
        "DoNotDisable",
        "REQUIRED: Microsoft Store licensing if using Store apps",
        "Microsoft Store"
    ),
]


def get_services_by_category() -> Dict[str, List[ServiceDefinition]]:
    """Group services by category"""
    categories = {
        "SafeToDisable": [],
        "OptionalToDisable": [],
        "DoNotDisable": []
    }
    
    for service in SERVICES_DATABASE:
        categories[service.category].append(service)
    
    return categories


def get_service_by_internal_name(internal_name: str) -> ServiceDefinition:
    """Get service definition by internal name"""
    for service in SERVICES_DATABASE:
        if service.internal_name.lower() == internal_name.lower():
            return service
    return None


def get_services_by_group() -> Dict[str, List[ServiceDefinition]]:
    """Group services by functional group"""
    groups = {}
    for service in SERVICES_DATABASE:
        if service.group not in groups:
            groups[service.group] = []
        groups[service.group].append(service)
    
    return groups