#!/bin/bash
set -e

echo "🚀 Deploying Nobi Trade..."

cd /home/ubuntu/nobi-trade

# Pull latest code
git pull origin master

# Activate venv & install any new deps
source venv/bin/activate
pip install -r requirements.txt --quiet

# Restart services
sudo systemctl restart nobi-trade
sudo systemctl restart nobi-trade-streamlit

echo "✅ Deploy complete!"
