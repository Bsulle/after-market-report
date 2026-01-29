#!/bin/bash
#
# Daily After-Market Report Cron Job Setup
# This script sets up automated daily report generation
#

echo "======================================================"
echo "After-Market Report - Cron Job Setup"
echo "======================================================"

# Get the absolute path to this directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo ""
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"
echo ""

# Ensure dependencies are installed
echo "Checking dependencies..."
$PYTHON_PATH -c "import requests, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Missing dependencies. Installing..."
    pip3 install requests pandas numpy
fi

# Create log directory
mkdir -p "$SCRIPT_DIR/logs"

# Create the cron command
# Runs at 6:00 PM ET every weekday (Monday-Friday)
CRON_TIME="0 18 * * 1-5"  # 6 PM on weekdays
CRON_COMMAND="cd $SCRIPT_DIR && $PYTHON_PATH generate_report.py --date \$(date -d 'yesterday' +\%Y-\%m-\%d) >> logs/cron_\$(date +\%Y-\%m).log 2>&1"

# Full cron entry
CRON_ENTRY="$CRON_TIME $CRON_COMMAND"

echo "Proposed cron job:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$CRON_ENTRY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will run at 6:00 PM ET Monday-Friday"
echo "Reports will be saved to:"
echo "  - After_Market_Report_YYYY-MM-DD.md"
echo "Logs will be saved to:"
echo "  - logs/cron_YYYY-MM.log"
echo ""

# Prompt for confirmation
read -p "Install this cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if cron job already exists
    (crontab -l 2>/dev/null | grep -F "generate_report.py") && {
        echo "⚠ Cron job already exists. Removing old entry..."
        (crontab -l 2>/dev/null | grep -v "generate_report.py") | crontab -
    }

    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

    echo "✓ Cron job installed successfully!"
    echo ""
    echo "To verify:"
    echo "  crontab -l | grep generate_report"
    echo ""
    echo "To remove:"
    echo "  crontab -e"
    echo "  (then delete the line with 'generate_report.py')"
    echo ""
    echo "To test manually:"
    echo "  cd $SCRIPT_DIR && python3 generate_report.py"
else
    echo "❌ Installation cancelled."
    echo ""
    echo "To run manually:"
    echo "  cd $SCRIPT_DIR"
    echo "  python3 generate_report.py --date 2026-01-28"
fi

echo ""
echo "======================================================"
echo "Setup Complete!"
echo "======================================================"
