from PIL import Image
from realesrgan import RealESRGAN
import torch

# Load your image
image_path = 'input.jpg'  # Change to your image path
image = Image.open(image_path).convert('RGB')

# Initialize the Real-ESRGAN model (x4 scale)
model = RealESRGAN(torch.device('cuda' if torch.cuda.is_available() else 'cpu'), scale=4)
model.load_weights('RealESRGAN_x4plus.pth', download=True)

# Upscale the image
upscaled = model.predict(image)

# Save the result
upscaled.save('upscaled_output.jpg')

print("✅ Image upscaled and saved as 'upscaled_output.jpg'")
