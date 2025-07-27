# SSMS Plus

Automatically organizes your SQL Server Management Studio files and colors tabs by server/database.

## What It Does

**File Organization**: Saves your SQL files in organized folders:
```
Save Directory/
├── PROD-SQL01/
│   ├── CustomerDB/
│   │   ├── query1.sql
│   │   └── query2.sql
│   └── OrdersDB/
│       └── report.sql
└── TEST-SQL01/
    └── TestDB/
        └── debug.sql
```

**Tab Coloring**: Groups and colors SSMS tabs for easy identification.

## Setup

### 1. Enable SSMS Tab Coloring (Required)
In SSMS: **Tools** → **Options** → **Environment** → **Tabs and Windows** → Check **"Color tabs by regular expression"**

### 2. Configure SSMS Plus
- Run the app (appears in system tray)
- **Left-click** the tray icon to open settings
- Set your **Temp Directory** (click "Auto" for default)
- Set your **Save Directory** (where organized files go)
- Choose tab grouping mode
- Click **Save**

## Tab Grouping Modes

**Server Only**: All tabs for same server get same color
```
PROD-SQL01 (Blue)    TEST-SQL01 (Green)
├── CustomerDB       ├── CustomerDB
├── OrdersDB         └── TestDB
└── ReportsDB
```

**Server + Database**: Each server+database combo gets unique color
```
PROD-SQL01\CustomerDB (Blue)
PROD-SQL01\OrdersDB (Red)  
PROD-SQL01\ReportsDB (Yellow)
TEST-SQL01\CustomerDB (Green)
TEST-SQL01\TestDB (Purple)
```

## Usage

Just use SSMS normally! SSMS Plus runs in the background and automatically:
- Organizes new SQL files into server/database folders
- Updates ssms regex file based on your grouping preference

## Troubleshooting

**Colors not working?** Check that "Color tabs by regular expression" is enabled in SSMS Options.

**Colors not saving?** SSMS does not save tab colors between sessions, so if you close SSMS, tab colors will be lost.

**Files not saving?** Verify temp directory matches where SSMS creates files (right-click any SSMS tab → "Open Containing Folder").
