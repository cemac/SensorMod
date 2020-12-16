import os
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from adafruit_extended_bus import ExtendedI2C as I2C

# Create library object using our Extended Bus I2C port
os.system('dtoverlay i2c-gpio bus=2 i2c_gpio_sda=22 i2c_gpio_scl=23')
i2c = I2C(2) # use software bus i2c-2

### setup ###
# os.system('i2cdetect -y 2') # to get addr

disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
disp.fill(0)
disp.show()

width = disp.width
height = disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=2)

padding = -2
top = padding
bottom = height - padding
x = 0


IP = os.popen("hostname -I | cut -d' ' -f1").read()


# Load default font.
font = ImageFont.load_default()

def updatedata(date, dct):
        #clear
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        draw.text((x, top + 0), "%20s"%date, font=font, fill=255)
        
        draw.text((x, top + 8), '  | PM1   % .2e | '%(dct[4]), font=font, fill=255)
        draw.text((x, top + 16),'  | PM2.5  %.2e | '%(dct[5]), font=font, fill=255)
        draw.text((x, top + 25), '  | PM10  % .2e | '%(dct[6]), font=font, fill=255)
        
        # Display image.
        disp.image(image)
        disp.show()
        

def otherdata(date, dct):
        #clear
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        draw.text((x, top + 0), " %20s"%date, font=font, fill=255)
        
        draw.text((x, top + 8), '  | TEMP % 4dC | '%(dct[7]), font=font, fill=255)
        draw.text((x, top + 16),'  | RH % 6d | '%(dct[8]), font=font, fill=255)
        draw.text((x, top + 25), '  | X % 7d | '%(dct[10]), font=font, fill=255)
        
        # Display image.
        disp.image(image)
        disp.show()
        
        
## str(datetime.utcnow()).split('.')[0]


def standby():
    ### end on info
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top + 0), "%20s"%'Sensor Monitor v1.0', font=font, fill=255)
    draw.text((x, top + 16), "    IP: %s  "%IP, font=font, fill=255)
    draw.text((x, top + 25), "   -- standing by --   " , font=font, fill=255)
    disp.image(image)
    disp.show()
    
    
def shutdown():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top + 0), "%20s"%'Sensor Monitor v1.0', font=font, fill=255)
    draw.text((x, top + 16),  "    IP: %s  "%IP, font=font, fill=255)
    draw.text((x, top + 25), "    -- shut down --    ", font=font, fill=255)
    disp.image(image)
    disp.show()  
