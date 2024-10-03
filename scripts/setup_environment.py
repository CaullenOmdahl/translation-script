# scripts/setup_environment.py

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SetupEnvironment')

def install_dependencies():
    """
    Installs required Python packages from requirements.txt.
    """
    try:
        logger.info("Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        logger.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        sys.exit(1)

def create_directories():
    """
    Creates necessary directories if they do not exist.
    """
    directories = [
        Path('Videos to Transcode'),
        Path('Output')
    ]
    
    for directory in directories:
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                sys.exit(1)
        else:
            logger.info(f"Directory already exists: {directory}")

def clone_scripts_if_missing():
    """
    Clones the scripts from the GitHub repository if any are missing.
    """
    required_scripts = [
        'download_export_model.py',
        'load_model.py',
        'transcribe_audio.py',
        'translate_text.py',
        'create_subtitles.py'
    ]
    
    missing_scripts = []
    for script in required_scripts:
        script_path = Path('scripts') / script
        if not script_path.exists():
            missing_scripts.append(script)
    
    if missing_scripts:
        logger.info("Some scripts are missing. Cloning from GitHub repository...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 'gitpython'
            ])
            from git import Repo
            repo_url = 'https://github.com/CaullenOmdahl/translation-script.git'
            repo_path = Path('scripts')
            if not repo_path.exists():
                Repo.clone_from(repo_url, repo_path)
                logger.info(f"Cloned scripts from {repo_url} to {repo_path}")
            else:
                logger.info(f"Scripts directory already exists at {repo_path}")
        except Exception as e:
            logger.error(f"Failed to clone scripts: {e}")
            sys.exit(1)
    else:
        logger.info("All required scripts are present.")

def main():
    create_directories()
    install_dependencies()
    clone_scripts_if_missing()
    logger.info("Environment setup completed successfully.")

if __name__ == "__main__":
    main()
