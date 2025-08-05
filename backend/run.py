#!/usr/bin/env python3
"""
Simple startup script for the backend application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Get port from environment or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 Starting backend server...")
    print(f"📝 Server will run on port {port}")
    print("⚡ Server will be ready for basic operations immediately")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    ) 