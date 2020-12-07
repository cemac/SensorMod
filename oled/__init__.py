from board import SCL, SDA
import busio,os
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


### setup ###
# os.system('i2cdetect -y 1') # to get addr
i2c = busio.I2C(SCL, SDA)
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
        
        draw.text((x, top + 8), 'PM1   % .2e| TEMP % 4dC'%(dct[4],dct[7]), font=font, fill=255)
        draw.text((x, top + 16),'PM2.5 %.2e| RH % 6d'%(dct[5],dct[8]), font=font, fill=255)
        draw.text((x, top + 25), 'PM10  % .2e| X % 7d'%(dct[6],dct[10]), font=font, fill=255)
        
        # Display image.
        disp.image(image)
        disp.show()
        
        
## str(datetime.utcnow()).split('.')[0]


def standby():
    ### end on info
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top + 0), "%20s"%'Sensor Monitor v1.0', font=font, fill=255)
    draw.text((x, top + 16), "     IP: " + IP, font=font, fill=255)
    draw.text((x, top + 25), "   -- standing by --   " , font=font, fill=255)
    disp.image(image)
    disp.show()
    
    
def shutdown():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top + 0), "%20s"%'Sensor Monitor v1.0', font=font, fill=255)
    draw.text((x, top + 16), "     IP: " + IP, font=font, fill=255)
    draw.text((x, top + 25), "    -- shut down --    ", font=font, fill=255)
    disp.image(image)
    disp.show()  