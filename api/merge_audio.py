# Audio Chunk Merger for Audiobook
import os
import glob
from pydub import AudioSegment
import sys
sys.stdout.reconfigure(encoding='utf-8')
def merge_audio_chunks():
    """Merge all audio chunks into a single audiobook file."""
    
    AUDIO_DIR = "audio_chunks"
    OUTPUT_FILE = "my_voice_audiobook.wav"
    
    # Check if audio chunks directory exists
    if not os.path.exists(AUDIO_DIR):
        print(f"❌ Error: {AUDIO_DIR} directory not found!")
        print("💡 Run convet_to_myVoice.py first to generate audio chunks")
        return False
    
    # Get all WAV files in the audio chunks directory
    chunk_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "chunk_*.wav")))
    
    if not chunk_files:
        print(f"❌ No audio chunks found in {AUDIO_DIR}/")
        return False
    
    print(f"🔗 Found {len(chunk_files)} audio chunks to merge...")
    
    try:
        # Load the first chunk
        combined_audio = AudioSegment.from_wav(chunk_files[0])
        print(f"✅ Loaded: {os.path.basename(chunk_files[0])}")
        
        # Add each subsequent chunk
        for i, chunk_file in enumerate(chunk_files[1:], 1):
            try:
                chunk = AudioSegment.from_wav(chunk_file)
                combined_audio += chunk
                print(f"✅ Added: {os.path.basename(chunk_file)} ({i+1}/{len(chunk_files)})")
            except Exception as e:
                print(f"⚠️  Warning: Could not load {chunk_file}: {e}")
                continue
        
        # Export the final audiobook
        print(f"\n💾 Saving final audiobook as {OUTPUT_FILE}...")
        combined_audio.export(OUTPUT_FILE, format="wav")
        
        # Calculate duration
        duration_seconds = len(combined_audio) / 1000
        duration_minutes = duration_seconds / 60
        
        print(f"\n🎉 Audiobook created successfully!")
        print(f"📁 File: {OUTPUT_FILE}")
        print(f"⏱️  Duration: {duration_minutes:.1f} minutes ({duration_seconds:.0f} seconds)")
        print(f"📊 File size: {os.path.getsize(OUTPUT_FILE) / (1024*1024):.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error merging audio: {e}")
        print("💡 Make sure pydub is installed: pip install pydub")
        return False

def merge_with_ffmpeg():
    """Alternative method using ffmpeg (if pydub is not available)."""
    
    AUDIO_DIR = "audio_chunks"
    OUTPUT_FILE = "my_voice_audiobook.wav"
    
    # Check if audio chunks directory exists
    if not os.path.exists(AUDIO_DIR):
        print(f"❌ Error: {AUDIO_DIR} directory not found!")
        return False
    
    # Get all WAV files
    chunk_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "chunk_*.wav")))
    
    if not chunk_files:
        print(f"❌ No audio chunks found in {AUDIO_DIR}/")
        return False
    
    # Create file list for ffmpeg
    filelist_path = "chunk_list.txt"
    with open(filelist_path, 'w') as f:
        for chunk_file in chunk_files:
            f.write(f"file '{chunk_file}'\n")
    
    # Use ffmpeg to concatenate
    ffmpeg_cmd = f'ffmpeg -f concat -safe 0 -i {filelist_path} -c copy {OUTPUT_FILE}'
    print(f"🔧 Running: {ffmpeg_cmd}")
    
    result = os.system(ffmpeg_cmd)
    
    # Clean up
    os.remove(filelist_path)
    
    if result == 0:
        print(f"🎉 Audiobook created successfully: {OUTPUT_FILE}")
        return True
    else:
        print("❌ ffmpeg merge failed")
        return False

if __name__ == "__main__":
    print("🎵 Audio Chunk Merger")
    print("=" * 30)
    
    # Try pydub first, fallback to ffmpeg
    try:
        from pydub import AudioSegment
        print("📦 Using pydub for merging...")
        success = merge_audio_chunks()
    except ImportError:
        print("📦 pydub not found, trying ffmpeg...")
        success = merge_with_ffmpeg()
    
    if not success:
        print("\n💡 Installation tips:")
        print("   For pydub: pip install pydub")
        print("   For ffmpeg: Download from https://ffmpeg.org/")
