#!/usr/bin/env python
"""Convert HEIC images to JPG format for COLMAP compatibility."""
import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    print("ERROR: pillow-heif not installed. Install with: pip install pillow-heif")
    sys.exit(1)


def convert_heic_to_jpg(input_dir: str, output_dir: str = None, quality: int = 95):
    """Convert all HEIC files in input_dir to JPG.
    
    Args:
        input_dir: Directory containing HEIC files
        output_dir: Optional output directory (defaults to input_dir)
        quality: JPG quality (1-100, default 95)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)
    
    heic_files = list(input_path.glob("*.HEIC")) + list(input_path.glob("*.heic"))
    
    if not heic_files:
        print(f"No HEIC files found in {input_dir}")
        return
    
    print(f"Found {len(heic_files)} HEIC files to convert...")
    
    for i, heic_file in enumerate(heic_files, 1):
        jpg_file = output_path / f"{heic_file.stem}.jpg"
        
        if jpg_file.exists():
            print(f"[{i}/{len(heic_files)}] Skipping {heic_file.name} (already converted)")
            continue
        
        try:
            img = Image.open(heic_file)
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(jpg_file, "JPEG", quality=quality)
            print(f"[{i}/{len(heic_files)}] Converted {heic_file.name} -> {jpg_file.name}")
        except Exception as e:
            print(f"[{i}/{len(heic_files)}] ERROR converting {heic_file.name}: {e}")
    
    print(f"\nConversion complete! Converted {len(heic_files)} images to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert HEIC images to JPG")
    parser.add_argument("--input_dir", "-i", required=True, help="Directory containing HEIC files")
    parser.add_argument("--output_dir", "-o", help="Output directory (default: same as input)")
    parser.add_argument("--quality", "-q", type=int, default=95, help="JPG quality 1-100 (default: 95)")
    args = parser.parse_args()
    
    convert_heic_to_jpg(args.input_dir, args.output_dir, args.quality)


if __name__ == "__main__":
    main()
