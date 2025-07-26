#!/usr/bin/env python3
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("Starting Quiz Master Application...")
    print("Access the application at: http://localhost:5000")
    print("Admin login: admin@quizmaster.com / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)
