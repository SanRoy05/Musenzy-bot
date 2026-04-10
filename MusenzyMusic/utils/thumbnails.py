import os
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
import config
from MusenzyMusic.utils.queue import Track

class ThumbnailManager:
    def __init__(self):
        self.output_dir = config.CACHE_DIR
        # Try to find common linux fonts
        self.font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf" # Windows fallback
        ]

    def _get_font(self, size):
        for path in self.font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    async def generate(self, track: Track) -> str:
        # Create unique filename based on URL hash
        output_path = os.path.join(self.output_dir, f"thumb_{abs(hash(track.url))}.png")
        if os.path.exists(output_path):
            return output_path

        # Download thumbnail
        local_thumb = f"cache/temp_{abs(hash(track.url))}.jpg"
        async with aiohttp.ClientSession() as session:
            async with session.get(track.thumb) as resp:
                if resp.status == 200:
                    with open(local_thumb, "wb") as f:
                        f.write(await resp.read())
                else:
                    return config.DEFAULT_THUMB

        try:
            # 1. Background
            main = Image.open(local_thumb).convert("RGB").resize((1280, 720))
            # Blur and darken
            background = main.filter(ImageFilter.GaussianBlur(25))
            background = ImageEnhance.Brightness(background).enhance(0.4)
            
            # 2. Main Square Thumbnail
            thumb = ImageOps.fit(main, (600, 600), Image.LANCZOS)
            # Rounded corners
            mask = Image.new("L", (600, 600), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle((0, 0, 600, 600), radius=40, fill=255)
            thumb.putalpha(mask)
            
            # Add subtle border to main thumb
            border = Image.new("RGBA", (610, 610), (255, 255, 255, 100))
            mask_border = Image.new("L", (610, 610), 0)
            draw_b = ImageDraw.Draw(mask_border)
            draw_b.rounded_rectangle((0, 0, 610, 610), radius=45, fill=255)
            border.putalpha(mask_border)
            
            background.paste(border, (45, 55), border)
            background.paste(thumb, (50, 60), thumb)

            # 3. Text & Branding
            draw = ImageDraw.Draw(background)
            font_title = self._get_font(70)
            font_info = self._get_font(40)
            font_brand = self._get_font(50)

            # Clean title
            title = track.title[:45] + "..." if len(track.title) > 45 else track.title
            
            # Title
            draw.text((700, 150), title, fill=(255, 255, 255), font=font_title)
            
            # Info
            draw.text((700, 300), f"⏱️ Duration: {track.duration}", fill=(200, 200, 200), font=font_info)
            draw.text((700, 380), f"👤 By: {track.user}", fill=(200, 200, 200), font=font_info)
            
            # Branding Footer
            draw.text((700, 580), f"🎵 {config.BRANDING_TEXT}", fill=(0, 255, 255), font=font_brand)
            
            # 4. Save
            background.save(output_path)
            # Cleanup temp
            if os.path.exists(local_thumb): os.remove(local_thumb)
            
            return output_path
        except Exception as e:
            print(f"❌ Thumbnail error: {e}")
            return config.DEFAULT_THUMB

thumb_manager = ThumbnailManager()
