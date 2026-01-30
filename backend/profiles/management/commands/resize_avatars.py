"""
Resize existing avatar images to reduce file size and improve loading times.

Usage:
  python manage.py resize_avatars                    # Resize all avatars
  python manage.py resize_avatars --user mock_maya   # Resize specific user
  python manage.py resize_avatars --dry-run          # Show what would be resized
"""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image


class Command(BaseCommand):
    help = "Resize existing avatar images to reduce file size"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--user",
            type=str,
            help="Resize avatars for specific user by username (e.g., mock_maya)",
        )
        parser.add_argument(
            "--size",
            type=int,
            default=320,
            help="Target size in pixels (default: 320)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be resized without making changes",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Create backup of original images before resizing",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        base_dir = Path(settings.BASE_DIR) / "static" / "painted_avatars"
        
        if not base_dir.exists():
            self.stdout.write(self.style.WARNING(f"Avatar directory not found: {base_dir}"))
            return
        
        target_size = options.get("size", 512)
        dry_run = options.get("dry_run", False)
        backup = options.get("backup", False)
        specific_user = options.get("user")
        
        # Find all avatar images
        avatar_files = []
        if specific_user:
            user_dir = base_dir / specific_user
            if user_dir.exists():
                avatar_files = list(user_dir.glob("avatar_*.png"))
            else:
                self.stderr.write(self.style.ERROR(f"User directory not found: {user_dir}"))
                return
        else:
            # Find all avatar files in all user directories
            for user_dir in base_dir.iterdir():
                if user_dir.is_dir():
                    avatar_files.extend(user_dir.glob("avatar_*.png"))
        
        if not avatar_files:
            self.stdout.write(self.style.WARNING("No avatar images found"))
            return
        
        self.stdout.write(f"📸 Found {len(avatar_files)} avatar image(s)")
        self.stdout.write(f"   Target size: {target_size}x{target_size} pixels")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n🔍 DRY RUN MODE - No changes will be made\n"))
        
        total_original_size = 0
        total_optimized_size = 0
        processed = 0
        skipped = 0
        errors = 0
        
        for avatar_path in avatar_files:
            try:
                # Get original file size
                original_size = avatar_path.stat().st_size / 1024  # KB
                total_original_size += original_size
                
                # Open and check current dimensions
                with Image.open(avatar_path) as img:
                    current_width, current_height = img.size
                    
                    # Skip if already smaller than target
                    if current_width <= target_size and current_height <= target_size:
                        self.stdout.write(
                            f"   ⏭️  {avatar_path.name}: Already {current_width}x{current_height} "
                            f"({original_size:.1f}KB) - skipping"
                        )
                        skipped += 1
                        continue
                    
                    if dry_run:
                        self.stdout.write(
                            f"   📝 {avatar_path.name}: Would resize from "
                            f"{current_width}x{current_height} ({original_size:.1f}KB) "
                            f"to {target_size}x{target_size}"
                        )
                        continue
                    
                    # Create backup if requested
                    if backup:
                        backup_path = avatar_path.with_suffix('.png.backup')
                        if not backup_path.exists():
                            import shutil
                            shutil.copy2(avatar_path, backup_path)
                            self.stdout.write(f"   💾 Backed up: {backup_path.name}")
                    
                    # Resize image with crop focusing on upper portion (face area)
                    # Calculate aspect ratio
                    aspect_ratio = current_width / current_height
                    
                    if aspect_ratio < 1.0:  # Portrait (taller than wide)
                        # Resize to fit width, then crop height from bottom to focus on face
                        new_width = target_size
                        new_height = int(current_height * (target_size / current_width))
                        img_temp = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        # Crop from top, cutting off bottom portion
                        img_resized = img_temp.crop((0, 0, target_size, target_size))
                    elif aspect_ratio > 1.0:  # Landscape (wider than tall)
                        # Crop to square focusing on upper-center portion
                        crop_size = min(current_width, current_height)
                        left = (current_width - crop_size) // 2
                        # Shift crop upward to focus on face (top 30% of image)
                        top = max(0, int((current_height - crop_size) * 0.3))
                        right = left + crop_size
                        bottom = top + crop_size
                        img_cropped = img.crop((left, top, right, bottom))
                        img_resized = img_cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
                    else:  # Square
                        # Resize normally for square images
                        img_resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                    
                    # Save with compression
                    output = BytesIO()
                    img_resized.save(output, format='PNG', optimize=True, compress_level=6)
                    optimized_bytes = output.getvalue()
                    optimized_size = len(optimized_bytes) / 1024  # KB
                    total_optimized_size += optimized_size
                    
                    # Write optimized image
                    avatar_path.write_bytes(optimized_bytes)
                    
                    # Calculate reduction
                    reduction = ((original_size - optimized_size) / original_size) * 100
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   ✅ {avatar_path.name}: "
                            f"{current_width}x{current_height} ({original_size:.1f}KB) → "
                            f"{target_size}x{target_size} ({optimized_size:.1f}KB) "
                            f"({reduction:.0f}% reduction)"
                        )
                    )
                    processed += 1
                    
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"   ❌ Error processing {avatar_path.name}: {e}")
                )
                errors += 1
        
        # Summary
        if not dry_run:
            total_reduction = ((total_original_size - total_optimized_size) / total_original_size * 100) if total_original_size > 0 else 0
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Done! Processed: {processed}, Skipped: {skipped}, Errors: {errors}"
                )
            )
            if processed > 0:
                self.stdout.write(
                    f"   Total size: {total_original_size:.1f}KB → {total_optimized_size:.1f}KB "
                    f"({total_reduction:.0f}% reduction)"
                )
        else:
            self.stdout.write(
                self.style.WARNING(f"\n🔍 Would process {len(avatar_files) - skipped} image(s)")
            )
