"""
ACE Artifact Persistence for GitHub Actions

This module handles downloading and restoring ACE system artifacts
(playbook, trade logs, reflections) across GitHub Actions runs.
"""

import json
import os
import requests
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone


def is_running_in_github_actions() -> bool:
    """Check if code is running in GitHub Actions environment."""
    return os.environ.get('GITHUB_ACTIONS') == 'true'


def get_github_api_headers() -> Dict[str, str]:
    """Get headers for GitHub API requests."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment")
    
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }


def get_latest_artifact(repo: str, artifact_name_prefix: str = "ace-session") -> Optional[Dict[str, Any]]:
    """
    Get the latest ACE session artifact from GitHub Actions.
    
    Args:
        repo: Repository in format "owner/repo"
        artifact_name_prefix: Prefix to filter artifacts
        
    Returns:
        Artifact metadata dict or None if not found
    """
    try:
        url = f"https://api.github.com/repos/{repo}/actions/artifacts"
        headers = get_github_api_headers()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        artifacts = response.json().get('artifacts', [])
        
        # Filter for ACE session artifacts
        ace_artifacts = [
            a for a in artifacts 
            if a['name'].startswith(artifact_name_prefix) and not a['expired']
        ]
        
        if not ace_artifacts:
            print(f"⚠️  No {artifact_name_prefix} artifacts found")
            return None
        
        # Sort by created_at and get most recent
        ace_artifacts.sort(key=lambda x: x['created_at'], reverse=True)
        latest = ace_artifacts[0]
        
        print(f"✅ Found latest artifact: {latest['name']} (created {latest['created_at']})")
        return latest
        
    except Exception as e:
        print(f"❌ Error fetching artifacts: {e}")
        return None


def download_artifact(artifact: Dict[str, Any], download_dir: Path = Path(".")):
    """
    Download and extract a GitHub Actions artifact.
    
    Args:
        artifact: Artifact metadata from GitHub API
        download_dir: Directory to extract artifact to
    """
    try:
        # Get download URL
        download_url = artifact['archive_download_url']
        headers = get_github_api_headers()
        
        print(f"📥 Downloading artifact: {artifact['name']}...")
        
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Save zip file
        zip_path = download_dir / "artifact.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"📦 Extracting artifact...")
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        
        # Clean up zip file
        zip_path.unlink()
        
        print(f"✅ Artifact extracted to {download_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading artifact: {e}")
        return False


def restore_playbook(source_path: Path = Path("data/playbook.json")) -> bool:
    """
    Restore playbook from downloaded artifact.
    
    Args:
        source_path: Path to playbook in downloaded artifact
        
    Returns:
        True if restored successfully
    """
    try:
        if not source_path.exists():
            print(f"⚠️  Playbook not found at {source_path}")
            return False
        
        # Ensure data directory exists
        Path("data").mkdir(exist_ok=True)
        
        # Load playbook to validate it
        with open(source_path) as f:
            playbook = json.load(f)
        
        # Verify structure
        if "metadata" not in playbook or "sections" not in playbook:
            print("❌ Invalid playbook structure")
            return False
        
        version = playbook["metadata"].get("version", "unknown")
        bullets = playbook["metadata"].get("total_bullets", 0)
        
        print(f"✅ Playbook restored: v{version}, {bullets} bullets")
        return True
        
    except Exception as e:
        print(f"❌ Error restoring playbook: {e}")
        return False


def restore_trading_sessions(source_dir: Path = Path("trading_session")) -> int:
    """
    Count and validate restored trading sessions.
    
    Args:
        source_dir: Path to trading_session directory in artifact
        
    Returns:
        Number of sessions restored
    """
    try:
        if not source_dir.exists():
            print(f"⚠️  No trading sessions found")
            return 0
        
        # Count session directories
        sessions = [d for d in source_dir.iterdir() if d.is_dir()]
        count = len(sessions)
        
        if count > 0:
            print(f"✅ {count} trading session(s) restored")
            # Show most recent 3
            recent = sorted(sessions, key=lambda x: x.name, reverse=True)[:3]
            for session in recent:
                print(f"   - {session.name}")
        
        return count
        
    except Exception as e:
        print(f"❌ Error restoring sessions: {e}")
        return 0


def restore_weekly_reflections(source_dir: Path = Path("weekly_reflections")) -> int:
    """
    Count and validate restored weekly reflections.
    
    Args:
        source_dir: Path to weekly_reflections directory in artifact
        
    Returns:
        Number of reflections restored
    """
    try:
        if not source_dir.exists():
            print(f"⚠️  No weekly reflections found")
            return 0
        
        # Ensure directory exists
        source_dir.mkdir(exist_ok=True, parents=True)
        
        # Count reflection files
        reflections = list(source_dir.glob("*.json"))
        count = len(reflections)
        
        if count > 0:
            print(f"✅ {count} weekly reflection(s) restored")
            # Show most recent 3
            recent = sorted(reflections, reverse=True)[:3]
            for ref in recent:
                print(f"   - {ref.name}")
        
        return count
        
    except Exception as e:
        print(f"❌ Error restoring reflections: {e}")
        return 0


def download_and_restore_ace_artifacts() -> bool:
    """
    Main function to download and restore all ACE artifacts.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("ACE ARTIFACT RESTORATION")
    print("="*60 + "\n")
    
    if not is_running_in_github_actions():
        print("ℹ️  Not running in GitHub Actions - skipping artifact download")
        print("   (Using local files if they exist)")
        return True
    
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        print("❌ GITHUB_REPOSITORY not found in environment")
        return False
    
    print(f"📦 Repository: {repo}")
    
    # Get latest artifact
    artifact = get_latest_artifact(repo)
    if not artifact:
        print("⚠️  No previous artifacts found - starting fresh")
        print("   Playbook will be initialized on first run")
        return True
    
    # Download artifact
    download_dir = Path(".")
    if not download_artifact(artifact, download_dir):
        print("⚠️  Failed to download artifact - starting fresh")
        return True
    
    # Restore components
    print("\n📂 Restoring ACE components...")
    
    playbook_ok = restore_playbook()
    sessions_count = restore_trading_sessions()
    reflections_count = restore_weekly_reflections()
    
    # Summary
    print("\n" + "="*60)
    print("RESTORATION SUMMARY")
    print("="*60)
    print(f"Playbook:           {'✅ Restored' if playbook_ok else '⚠️  Not found'}")
    print(f"Trading Sessions:   {sessions_count} restored")
    print(f"Weekly Reflections: {reflections_count} restored")
    print("="*60 + "\n")
    
    return True


def create_artifact_summary() -> Dict[str, Any]:
    """
    Create a summary of current ACE artifacts for reporting.
    
    Returns:
        Dict with artifact summary
    """
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "playbook": None,
        "trading_sessions": [],
        "weekly_reflections": []
    }
    
    # Playbook info
    playbook_path = Path("data/playbook.json")
    if playbook_path.exists():
        try:
            with open(playbook_path) as f:
                playbook = json.load(f)
            summary["playbook"] = {
                "version": playbook["metadata"].get("version"),
                "total_bullets": playbook["metadata"].get("total_bullets"),
                "last_updated": playbook["metadata"].get("last_updated")
            }
        except Exception as e:
            summary["playbook"] = {"error": str(e)}
    
    # Trading sessions
    session_dir = Path("trading_session")
    if session_dir.exists():
        sessions = sorted([d.name for d in session_dir.iterdir() if d.is_dir()])
        summary["trading_sessions"] = sessions[-10:]  # Last 10 sessions
    
    # Weekly reflections
    reflection_dir = Path("weekly_reflections")
    if reflection_dir.exists():
        reflections = sorted([f.name for f in reflection_dir.glob("*.json")])
        summary["weekly_reflections"] = reflections[-5:]  # Last 5 reflections
    
    return summary


def save_artifact_summary():
    """Save artifact summary to file for inclusion in uploads."""
    summary = create_artifact_summary()
    
    summary_path = Path("artifact_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📊 Artifact summary saved to {summary_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("CURRENT ACE STATE")
    print("="*60)
    if summary["playbook"]:
        p = summary["playbook"]
        if "error" not in p:
            print(f"Playbook:     v{p['version']} ({p['total_bullets']} bullets)")
        else:
            print(f"Playbook:     Error - {p['error']}")
    else:
        print("Playbook:     Not initialized")
    
    print(f"Sessions:     {len(summary['trading_sessions'])} total")
    print(f"Reflections:  {len(summary['weekly_reflections'])} total")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Can be run standalone to test
    download_and_restore_ace_artifacts()
    save_artifact_summary()
