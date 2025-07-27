"""Test the simplified window title checking logic"""

# Test window titles based on actual SSMS behavior
test_titles = [
    # Loading state
    "Microsoft SQL Server Management Studio",
    
    # Ready states - Script View As (no "sqlquery")
    "AXIOM_ILS_4dm0ansk.sql - AXIOM.ILS (AXIOM\\blake (68)) - AXIOM_ILS_4dm0ansk.sql - AXIOM.ILS (AXIOM\\blake (68)) - Microsoft SQL Server Management Studio",
    "usp_Test.sql - AXIOM.ILS (AXIOM\\blake (68)) - Microsoft SQL Server Management Studio",
    "vw_CustomerData.sql* - AXIOM.DBA (AXIOM\\blake (68)) - Microsoft SQL Server Management Studio",
    
    # Ready states - Normal New Query (contains "sqlquery")
    "SQLQuery1.sql - AXIOM.ILS (AXIOM\\blake (68)) - Microsoft SQL Server Management Studio",
    "SQLQuery2.sql* - AXIOM.DBA (AXIOM\\blake (68)) - Microsoft SQL Server Management Studio",
    
    # Other windows
    "Some other application",
    "Notepad",
]

def check_title_status(title):
    """Test the simplified title checking logic"""
    
    # Loading state: just "Microsoft SQL Server Management Studio"
    if title.strip() == "Microsoft SQL Server Management Studio":
        return "LOADING", False
    
    # Ready state: contains filename and server info
    if "Microsoft SQL Server Management Studio" in title and " - " in title:
        # Script View As windows don't have "sqlquery" in the filename part
        is_script_view_as = "sqlquery" not in title.lower()
        workflow = "Script View As" if is_script_view_as else "Normal Query"
        return "READY", workflow
    
    return "UNKNOWN", "Unknown"

print("Testing simplified window title detection:")
for title in test_titles:
    status, workflow = check_title_status(title)
    print(f"Status: {status:8} | Workflow: {workflow:15} | Title: '{title[:60]}{'...' if len(title) > 60 else ''}'")
