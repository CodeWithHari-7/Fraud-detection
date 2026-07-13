import sys
import os

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.dashboards.server import app

# Vercel serverless function entrypoint
handler = app
