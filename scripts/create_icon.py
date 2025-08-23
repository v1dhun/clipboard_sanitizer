#!/usr/bin/env python3
"""
Icon Creator for Clipboard Sanitizer - PIL Only Version
Creates icons in multiple formats (.ico, .icns, .png) using only PIL/Pillow.
Cross-platform compatible and more efficient.
"""

import sys
from pathlib import Path
from typing import Dict
from PIL import Image, ImageDraw, __version__ as PIL_VERSION


class IconCreator:
    """Creates application icons using only PIL/Pillow."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.output_dir = self.project_root / "assets" / "icons"

        # Icon sizes for different purposes
        self.icon_sizes = {
            'ico': [16, 24, 32, 48, 64, 128, 256],  # Windows .ico
            'icns': [16, 32, 64, 128, 256, 512, 1024],  # macOS .icns
            'png': [16, 24, 32, 48, 64, 128, 256, 512]  # General PNG icons
        }

        # Color scheme
        self.colors = {
            'primary': (52, 152, 219),      # Blue
            'primary_dark': (41, 128, 185), # Darker blue
            'success': (46, 204, 113),      # Green
            'success_dark': (39, 174, 96),  # Darker green
            'white': (255, 255, 255),
            'light_gray': (200, 200, 200),
            'dark_gray': (100, 100, 100),
            'transparent': (0, 0, 0, 0)
        }

    def check_requirements(self) -> bool:
        """Check if PIL/Pillow is available."""
        try:
            print(f"✓ Pillow version: {PIL_VERSION}")
            return True
        except ImportError:
            print("✗ Error: Pillow is not installed.")
            print("Install it with: pip install Pillow")
            return False

    def create_base_icon(self, size: int) -> Image.Image:
        """Create the base icon image with improved design."""
        # Create image with anti-aliasing
        scale_factor = 4  # Render at 4x size for better quality
        render_size = size * scale_factor
        img = Image.new('RGBA', (render_size, render_size), self.colors['transparent'])
        draw = ImageDraw.Draw(img)

        # Calculate dimensions
        padding = render_size // 8
        icon_area = render_size - (padding * 2)

        # Draw background circle with gradient effect
        self._draw_gradient_circle(draw, padding, icon_area, render_size)

        # Draw clipboard
        self._draw_clipboard(draw, padding, icon_area, render_size)

        # Draw sanitization elements
        self._draw_sanitization_symbol(draw, render_size)

        # Resize to target size with high-quality resampling
        if render_size != size:
            img = img.resize((size, size), Image.Resampling.LANCZOS)

        return img

    def _draw_gradient_circle(self, draw, padding: int,
                            icon_area: int, size: int) -> None:
        """Draw a clean gradient background circle."""
        center = size // 2
        max_radius = icon_area // 2

        # Create a smoother gradient with more layers
        layers = 15
        for i in range(layers):
            progress = i / layers
            radius = int(max_radius * (1 - progress * 0.3))  # Don't shrink too much

            # Smooth color interpolation
            r = int(self.colors['primary'][0] * (1 - progress) +
                   self.colors['primary_dark'][0] * progress)
            g = int(self.colors['primary'][1] * (1 - progress) +
                   self.colors['primary_dark'][1] * progress)
            b = int(self.colors['primary'][2] * (1 - progress) +
                   self.colors['primary_dark'][2] * progress)

            # Smooth alpha transition
            alpha = int(255 * (0.9 - progress * 0.1))
            color = (r, g, b, alpha)

            # Draw each layer
            temp_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.ellipse([center - radius, center - radius,
                               center + radius, center + radius], fill=color)

            # Blend with main image
            draw._image.alpha_composite(temp_img)

        # Clean outer border
        border_width = max(2, size // 150)
        draw.ellipse([padding, padding, padding + icon_area, padding + icon_area],
                    outline=self.colors['primary_dark'], width=border_width)

    def _draw_clipboard(self, draw, padding: int,
                       icon_area: int, size: int) -> None:
        """Draw the clipboard with proper proportions and clean design."""
        # Calculate clipboard dimensions with better proportions
        clip_margin = size // 8
        clip_width = size - (clip_margin * 2)
        clip_height = int(clip_width * 0.75)  # Better aspect ratio

        clip_x = clip_margin
        clip_y = padding + (icon_area - clip_height) // 2

        # Ensure clipboard fits within the circle
        max_clip_size = int(icon_area * 0.7)
        if clip_height > max_clip_size:
            scale_factor = max_clip_size / clip_height
            clip_height = int(clip_height * scale_factor)
            clip_width = int(clip_width * scale_factor)
            clip_x = (size - clip_width) // 2
            clip_y = padding + (icon_area - clip_height) // 2

        # Draw subtle shadow
        shadow_offset = max(2, size // 100)
        shadow_blur = max(1, size // 200)

        for i in range(shadow_blur):
            shadow_alpha = int(50 / (i + 1))
            shadow_color = (*self.colors['dark_gray'], shadow_alpha)
            shadow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)

            corner_radius = max(4, size // 50)
            shadow_draw.rounded_rectangle(
                [clip_x + shadow_offset + i, clip_y + shadow_offset + i,
                 clip_x + clip_width + shadow_offset + i,
                 clip_y + clip_height + shadow_offset + i],
                radius=corner_radius,
                fill=shadow_color
            )
            draw._image.alpha_composite(shadow_img)

        # Draw main clipboard body with clean design
        corner_radius = max(4, size // 50)
        draw.rounded_rectangle(
            [clip_x, clip_y, clip_x + clip_width, clip_y + clip_height],
            radius=corner_radius,
            fill=self.colors['white'],
            outline=self.colors['light_gray'],
            width=max(1, size // 100)
        )

        # Draw clipboard clip (more realistic proportions)
        clip_tab_width = int(clip_width * 0.35)
        clip_tab_height = int(clip_height * 0.12)
        clip_tab_x = clip_x + (clip_width - clip_tab_width) // 2
        clip_tab_y = clip_y - clip_tab_height // 2

        # Clip body with metallic appearance
        draw.rounded_rectangle(
            [clip_tab_x, clip_tab_y, clip_tab_x + clip_tab_width,
             clip_tab_y + clip_tab_height],
            radius=corner_radius // 3,
            fill=(240, 240, 240),
            outline=(180, 180, 180),
            width=max(1, size // 150)
        )

        # Small clip detail for realism
        clip_detail_width = clip_tab_width // 3
        clip_detail_x = clip_tab_x + (clip_tab_width - clip_detail_width) // 2
        draw.rectangle(
            [clip_detail_x, clip_tab_y + clip_tab_height // 4,
             clip_detail_x + clip_detail_width, clip_tab_y + 3 * clip_tab_height // 4],
            fill=(200, 200, 200)
        )

        # Draw clean text lines
        self._draw_text_lines(draw, clip_x, clip_y, clip_width, clip_height, size)

    def _draw_text_lines(self, draw, clip_x: int, clip_y: int,
                        clip_width: int, clip_height: int, size: int) -> None:
        """Draw clean, well-proportioned text lines on the clipboard."""
        line_count = 3  # Reduced for cleaner look
        line_margin = int(clip_width * 0.15)  # Proportional margins
        line_spacing = clip_height // (line_count + 2)
        line_height = max(1, size // 100)

        for i in range(line_count):
            line_y = clip_y + int(line_spacing * (i + 1.5))

            # More natural line length variations
            if i == 0:  # Header/title line - longest
                line_length = int((clip_width - (line_margin * 2)) * 0.9)
            elif i == 1:  # Medium line
                line_length = int((clip_width - (line_margin * 2)) * 0.75)
            else:  # Short line
                line_length = int((clip_width - (line_margin * 2)) * 0.6)

            # Clean rounded rectangle for text lines
            line_radius = line_height // 2
            draw.rounded_rectangle(
                [clip_x + line_margin, line_y,
                 clip_x + line_margin + line_length, line_y + line_height],
                radius=line_radius,
                fill=self.colors['dark_gray']
            )

    def _draw_sanitization_symbol(self, draw, size: int) -> None:
        """Draw a clean sanitization symbol (sparkles or clean indicator)."""
        # Position for the sanitization symbol - top right corner
        symbol_size = size // 6
        symbol_x = size - symbol_size - (size // 20)
        symbol_y = size // 20

        # Draw sparkle/clean effect with multiple small shapes
        self._draw_sparkles(draw, symbol_x, symbol_y, symbol_size, size)

    def _draw_sparkles(self, draw, x: int, y: int,
                      area_size: int, total_size: int) -> None:
        """Draw sparkle effects to indicate cleanliness/sanitization."""
        # Main sparkle - larger star shape
        star_size = area_size // 2
        center_x = x + area_size // 2
        center_y = y + area_size // 2

        # Create star points
        star_points = []
        for i in range(8):  # 8-point star
            angle = i * 3.14159 / 4  # 45 degrees each
            if i % 2 == 0:  # Outer points
                radius = star_size // 2
            else:  # Inner points
                radius = star_size // 4

            point_x = center_x + int(radius * __import__('math').cos(angle))
            point_y = center_y + int(radius * __import__('math').sin(angle))
            star_points.append((point_x, point_y))

        # Draw main sparkle with glow effect
        glow_img = Image.new('RGBA', (total_size, total_size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)

        # Create glow by drawing multiple enlarged versions
        for i in range(3):
            scale = 1 + (i * 0.3)
            scaled_points = []
            for px, py in star_points:
                scaled_x = center_x + int((px - center_x) * scale)
                scaled_y = center_y + int((py - center_y) * scale)
                scaled_points.append((scaled_x, scaled_y))

            alpha = int(80 / (i + 1))
            glow_draw.polygon(scaled_points, fill=(*self.colors['success'], alpha))

        draw._image.paste(glow_img, (0, 0), glow_img)

        # Draw main star
        draw.polygon(star_points, fill=self.colors['white'],
                    outline=self.colors['success'], width=max(1, total_size // 256))

        # Add smaller sparkles around
        small_sparkles = [
            (x - area_size // 4, y + area_size // 4),  # Left
            (x + area_size + area_size // 6, y + area_size // 2),  # Right
            (x + area_size // 2, y - area_size // 6),  # Top
        ]

        for sx, sy in small_sparkles:
            if sx >= 0 and sy >= 0 and sx < total_size and sy < total_size:
                small_size = area_size // 8
                # Simple 4-point star
                small_points = [
                    (sx, sy - small_size),  # Top
                    (sx + small_size // 2, sy),  # Right
                    (sx, sy + small_size),  # Bottom
                    (sx - small_size // 2, sy),  # Left
                ]
                draw.polygon(small_points, fill=self.colors['white'],
                           outline=self.colors['success'], width=1)

    def create_icons(self) -> Dict[str, bool]:
        """Create all icon formats."""
        results = {}

        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)

        print(f"Creating icons in: {self.output_dir}")

        # Create individual PNG icons
        results['png'] = self._create_png_icons()

        # Create ICO file (Windows)
        results['ico'] = self._create_ico_file()

        # Create ICNS file (macOS)
        results['icns'] = self._create_icns_file()

        return results

    def _create_png_icons(self) -> bool:
        """Create individual PNG icons."""
        try:
            png_dir = self.output_dir / "png"
            png_dir.mkdir(exist_ok=True)

            for size in self.icon_sizes['png']:
                icon = self.create_base_icon(size)
                icon_path = png_dir / f"icon_{size}x{size}.png"
                icon.save(icon_path, "PNG", optimize=True)
                print(f"✓ Created PNG {size}x{size}")
            # Create a high-quality master PNG
            master_icon = self.create_base_icon(512)
            master_path = self.project_root / "assets" / "icon.png"
            master_icon.save(master_path, "PNG", optimize=True)
            print(f"✓ Created master icon: {master_path}")

            return True
        except Exception as e:
            print(f"✗ Error creating PNG icons: {e}")
            return False

    def _create_ico_file(self) -> bool:
        """Create Windows ICO file."""
        try:
            ico_path = self.output_dir / "icon.ico"
            icons = []

            for size in self.icon_sizes['ico']:
                icon = self.create_base_icon(size)
                icons.append(icon)

            # Save as ICO with multiple sizes
            icons[0].save(ico_path, format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
            print(f"✓ Created ICO file: {ico_path}")
            return True

        except Exception as e:
            print(f"✗ Error creating ICO file: {e}")
            return False

    def _create_icns_file(self) -> bool:
        """Create macOS ICNS file using PIL only."""
        try:
            # PIL doesn't natively support ICNS creation, but we can create
            # the individual PNG files that can be converted to ICNS
            icns_dir = self.project_root / "assets" / "iconset"
            icns_dir.mkdir(exist_ok=True)

            # Create iconset structure
            for size in self.icon_sizes['icns']:
                icon = self.create_base_icon(size)

                if size <= 512:
                    # Regular resolution
                    filename = f"icon_{size}x{size}.png"
                    icon.save(icns_dir / filename, "PNG", optimize=True)

                    # High resolution (@2x) for smaller sizes
                    if size <= 256:
                        hires_icon = self.create_base_icon(size * 2)
                        hires_filename = f"icon_{size}x{size}@2x.png"
                        hires_icon.save(icns_dir / hires_filename, "PNG", optimize=True)

                elif size == 1024:
                    # 1024px is saved as 512@2x
                    filename = "icon_512x512@2x.png"
                    icon.save(icns_dir / filename, "PNG", optimize=True)

            print(f"✓ Created iconset directory: {icns_dir}")
            print("  To create .icns file on macOS, run:")
            print(f"  iconutil -c icns '{icns_dir}' -o '{self.output_dir}/icon.icns'")

            return True

        except Exception as e:
            print(f"✗ Error creating iconset: {e}")
            return False

    def create_all_icons(self) -> bool:
        """Main method to create all icons."""
        print("=" * 60)
        print("🎨 Clipboard Sanitizer Icon Creator (PIL Only)")
        print("=" * 60)

        # Check requirements
        if not self.check_requirements():
            return False

        # Create icons
        results = self.create_icons()

        # Summary
        print("\n" + "=" * 60)
        print("📊 Creation Summary:")
        success_count = sum(results.values())
        total_count = len(results)

        for format_type, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {format_type.upper()} icons")

        if success_count == total_count:
            print("\n🎉 All icons created successfully!")
            print(f"📁 Output directory: {self.output_dir}")
        else:
            print(f"\n⚠️  {success_count}/{total_count} icon formats created successfully")

        print("=" * 60)

        return success_count > 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create icons for Clipboard Sanitizer using PIL only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python icon_creator.py              # Create all icon formats
        """
    )
    parser.add_argument("--version", action="version", version="2.0.0")
    parser.add_argument("--png-only", action="store_true",
                       help="Create only PNG icons")

    args = parser.parse_args()

    creator = IconCreator()

    if args.png_only:
        success = creator._create_png_icons()
    else:
        success = creator.create_all_icons()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
