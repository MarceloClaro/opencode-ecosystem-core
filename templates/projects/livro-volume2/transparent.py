import sys
try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image

def make_transparent(input_path, output_path):
    img = Image.open(input_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    # threshold for what is considered "black"
    # if r, g, b are all less than 50, make it transparent, but preserve glowing parts
    for item in datas:
        # Calculate luminance
        lum = 0.299*item[0] + 0.587*item[1] + 0.114*item[2]
        if lum < 30: # strict threshold
            newData.append((0, 0, 0, 0))
        else:
            # Map luminance to alpha for smooth edge blending
            alpha = int(min(255, max(0, (lum - 30) * 5)))
            newData.append((item[0], item[1], item[2], alpha))

    img.putdata(newData)
    img.save(output_path, "PNG")
    print(f"Saved transparent image to {output_path}")

input_img = r"C:\Users\marce\.gemini\antigravity-cli\brain\255293ea-a76a-49ae-9ced-20c7fcf8659c\holographic_tooth_1781947196117.jpg"
output_img = r"C:\Users\marce\Documents\OpenCode_Ecosystem\livro_gemeos_odontologia\images\capa_logo_transparent.png"
make_transparent(input_img, output_img)
