# SSMS Plus

SSMS Plus is a system tray application that automatically organizes and saves your SQL Server Management Studio (SSMS) query files with intelligent folder structure and tab grouping.

## Features

- **Automatic File Organization**: Saves new SQL files to organized folders based on server and database
- **Tab Grouping & Colors**: Groups and colors SSMS tabs by server or server+database combination
- **System Tray Integration**: Runs quietly in the background with easy access to settings
- **Real-time Monitoring**: Watches for new SQL files and processes them automatically

## How It Works

### File Saving
When you create a new SQL file in SSMS, SSMS Plus automatically:
1. Detects the new file creation
2. Identifies which server and database you're connected to
3. Saves the file to: `[Save Directory]\[Server]\[Database]\filename.sql`

**Example**: If you're connected to `PROD-SQL01` server and `CustomerDB` database, your file will be saved to:
```
C:\MyQueries\PROD-SQL01\CustomerDB\NewQuery.sql
```

### Tab Grouping
SSMS Plus can group and color your SSMS tabs in two ways:

#### Server Only Grouping
- Groups tabs by server name only
- All tabs connected to the same server get the same color
- Useful when you work with many servers but fewer databases per server

#### Server + Database Grouping (Default)
- Groups tabs by both server AND database combination
- Each server+database combination gets a unique color
- More granular organization for complex environments

**Important**: 
- Tab grouping only affects **colors and visual organization**
- **File saving always uses the full server/database path** regardless of grouping mode
- Colors are automatically assigned and managed by SSMS Plus

### Custom Colors
If you want to set a custom color for a specific tab:
1. Right-click the tab in SSMS
2. Select "Set Tab Color"
3. Choose your preferred color

**Important Notes about Tab Colors**:
- SSMS Plus will respect your custom colors during the current SSMS session
- However, SSMS **will not remember tab colors** when you close and restart SSMS (believe me, I tried everything!)
- SSMS Plus remembers your server/database combinations and grouping settings permanently

## Setup

### SSMS Configuration (Required)
**Important**: Before SSMS Plus can color your tabs, you must enable this feature in SSMS:

1. Open SQL Server Management Studio
2. Go to **Tools** → **Options**
3. Navigate to **Environment** → **Tabs and Windows**
4. Check the box: **"Color tabs by regular expression"**
5. Click **OK**

Without this setting enabled, SSMS Plus cannot apply tab colors.

### First Time Setup
1. Run SSMS Plus - it will appear in your system tray
2. If directories aren't configured, the settings window will open automatically
3. Configure your directories:
   - **Temp Directory**: Click "Auto" to use your system temp folder, or browse to a custom location
   - **Save Directory**: Browse to where you want your organized SQL files saved
4. Choose your preferred tab grouping mode
5. Click "Save"

### Settings Window
Access settings by:
- **Left-clicking** the SSMS Plus tray icon, or
- **Right-clicking** the tray icon and selecting "Settings"

## Configuration

### Temp Directory
This is where SSMS initially creates temporary files. SSMS Plus monitors this folder for new SQL files.
- **Recommended**: Use the "Auto" button to set your system's temp directory
- **Custom**: Choose a different folder if you've configured SSMS to use a custom temp location

### Save Directory
This is your organized storage location where SSMS Plus will move and organize your SQL files.
- Choose a dedicated folder for your SQL queries
- SSMS Plus will create server and database subfolders automatically

### Tab Grouping Modes

#### Server Only
```
PROD-SQL01 (Blue)
├── CustomerDB tab (Blue)
├── OrdersDB tab (Blue)
└── ReportsDB tab (Blue)

TEST-SQL01 (Green)
├── CustomerDB tab (Green)
└── TestDB tab (Green)
```

#### Server + Database (Default)
```
PROD-SQL01\CustomerDB (Blue)
PROD-SQL01\OrdersDB (Red)
PROD-SQL01\ReportsDB (Yellow)
TEST-SQL01\CustomerDB (Green)
TEST-SQL01\TestDB (Purple)
```

## Troubleshooting

### Colors Not Applying
- **First, check SSMS settings**: Ensure "Color tabs by regular expression" is enabled in Tools → Options → Environment → Tabs and Windows
- Tab grouping only works with files that SSMS Plus has processed
- Custom colors set manually in SSMS will be preserved during the session
- Restart SSMS Plus if colors stop working
- Remember: SSMS doesn't persist tab colors between sessions (that's why you need SSMS Plus!)

### Files Not Being Detected
- Ensure the temp directory matches where SSMS creates temporary files
- Check that SSMS Plus is running (look for the tray icon)
- Verify both temp and save directories exist and are accessible

### Settings Won't Save
- Ensure both directories exist and are accessible
- Check that you have write permissions to the save directory
- Both temp and save directories must be valid folder paths

## System Tray Controls

- **Left Click**: Open settings window
- **Right Click**: Access menu with Settings and Exit options

## Requirements

- Windows operating system
- SQL Server Management Studio (SSMS)
- Python 3.7+ (if running from source)

## Support

For issues, feature requests, or questions, please visit the [GitHub repository](https://github.com/Blake-goofy/ssmsplus).
