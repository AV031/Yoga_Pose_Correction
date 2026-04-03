#!/usr/bin/env python3
"""
Installation script for Yoga Pose Estimation System
Checks dependencies and installs required packages
"""

import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        import importlib.util
        if importlib.util.find_spec('pip') is not None:
            print("✅ pip is available")
            return True
        print("❌ pip is not available")
        return False
    except ImportError:
        print("❌ pip is not available")
        return False

def install_requirements():
    """Install packages from requirements.txt"""
    print("\n" + "="*50)
    print("INSTALLING REQUIRED PACKAGES")
    print("="*50)
    
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        print("Installing packages from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ All packages installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def verify_installation():
    """Verify that all packages are installed correctly"""
    print("\n" + "="*50)
    print("VERIFYING INSTALLATION")
    print("="*50)
    
    required_packages = [
        'tensorflow', 'cv2', 'mediapipe', 'numpy', 
        'sklearn', 'matplotlib', 'PIL', 'tqdm', 'pandas'
    ]
    
    failed_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
                print(f"✅ opencv-python ({cv2.__version__})")
            elif package == 'PIL':
                from PIL import Image
                print(f"✅ pillow ({Image.__version__})")
            elif package == 'sklearn':
                import sklearn
                print(f"✅ scikit-learn ({sklearn.__version__})")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {package} ({version})")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Failed to import: {', '.join(failed_packages)}")
        return False
    else:
        print("\n✅ All packages verified successfully!")
        return True

def check_camera():
    """Check if camera is available"""
    print("\n" + "="*50)
    print("CHECKING CAMERA")
    print("="*50)
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera is available")
            cap.release()
            return True
        else:
            print("❌ Camera not found")
            return False
    except Exception as e:
        print(f"❌ Camera check failed: {e}")
        return False

def main():
    """Main installation process"""
    print("🧘 Yoga Pose Estimation System - Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        print("Please install pip first")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️  Installation failed!")
        print("Try installing manually:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Some packages failed to install")
        sys.exit(1)
    
    # Check camera (optional)
    camera_available = check_camera()
    
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)
    
    if camera_available:
        print("✅ Ready to run the yoga pose estimation system")
        print("\nNext steps:")
        print("1. python main.py --mode train  # Train the model")
        print("2. python main.py --mode demo   # Run live demo")
    else:
        print("⚠️  Camera not detected")
        print("You can still train the model, but live demo requires a camera")
        print("\nNext steps:")
        print("1. python main.py --mode train  # Train the model")
        print("2. Check camera connection and run: python main.py --mode demo")
    
    print("\nFor help: python main.py --help")

if __name__ == "__main__":
    main()
