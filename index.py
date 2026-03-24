import os
import sys

# Ensure Vercel reads from the root project directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resumeAnalyzer.resumeAnalyzer.settings")

# Vercel's @vercel/python looks for 'app' or 'application'
from resumeAnalyzer.resumeAnalyzer.wsgi import application
app = application
