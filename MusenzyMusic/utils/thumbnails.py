import os
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
import config
from MusenzyMusic.utils.queue import Track

class ThumbnailManager:
    def __init__(self):
        self.output_dir = config.CACHE_DIR
        # We'll use default fonts if possible, or try to find some
        self.font_path = None # Will attempt to use default

    async def generate(self, track: Track) -> str:
        output_path = os.path.join(self.output_dir, f"{hash(track.url)}.png")
        if os.path.exists(output_path):
            return output_path

        async with aiohttp.ClientSession() as session:
            async with session.get(track.thumb) as resp:
                if resp.status == 200:
                    with open(f"temp_thumb.jpg", "wb") as f:
                        f.write(await resp.read())
                else:
                    # Use default
                    return config.DEFAULT_THUMB

        try:
            img = Image.open("temp_thumb.jpg")
            img = img.convert("RGB").resize((1280, 720))
            
            # Blur background
            blur = img.filter(ImageFilter.GaussianBlur(20))
            darken = ImageEnhance.Brightness(blur).enhance(0.5)
            
            # Rounded rect for original thumb
            thumb = ImageOps.fit(img, (600, 600), Image.LANCZOS)
            mask = Image.new("L", (600, 600), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle((0, 0, 600, 600), radius=30, fill=255)
            thumb.putalpha(mask)
            
            darken.paste(thumb, (50, 60), thumb)
            
            # Text
            draw = ImageDraw.Draw(darken)
            # Try to load a font, otherwise use default
            try:
                font_title = ImageFont.truetype("arial.ttf", 60)
                font_brand = ImageFont.truetype("arial.ttf", 40)
            except:
                font_title = ImageFont.load_default()
                font_brand = ImageFont.load_default()

            draw.text((700, 100), track.title[:30] + "...", fill="white", font=font_title)
            draw.text((700, 200), f"Duration: {track.duration}", fill="white", font=font_brand)
            draw.text((700, 600), config.BRANDING_TEXT, fill="cyan", font=font_brand)
            
            darken.save(output_path)
            return output_path
        except Exception as e:
            print(f"Thumbnail error: {e}")
            return config.DEFAULT_THUMB

thumb_manager = ThumbnailManager()
