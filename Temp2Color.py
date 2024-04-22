from math import log
import tkinter as tk
import re

# https://tannerhelland.com/2012/09/18/convert-temperature-rgb-algorithm-code.html

BACKGROUND = '#202020'
FOREGROUND = '#f8f8f8'
HIGHTLIGHT0 = '#404040'

def main():
    window = tk.Tk()
    window.title("Temp2Color")
    window.minsize(600, 500)
    window['bg'] = BACKGROUND

    info_frame = tk.Frame(window, bg=BACKGROUND)

    main_label = tk.Label(window, fg=FOREGROUND, bg=BACKGROUND, font=("TkDefaultFont", 14), text='Enter a Temperature(k)')

    info_label = tk.Label(info_frame, fg=FOREGROUND, bg=BACKGROUND, font=("TkDefaultFont", 14), justify='left', text=
    '1,700 \t\t=> Match flame, (LPS/SOX)\n' 
    '1,850 \t\t=> Candle flame, sunset/sunrise\n'
    '2,400 \t\t=> Standard incandescent lamp\n'
    '2,550 \t\t=> Soft white incandescent lamp\n'
    '2,700 \t\t=> Soft white compact fluorescent and LED lamp\n'
    '3,000 \t\t=> Warm white compact fluorescent and LED lamp\n'
    '3,200 \t\t=> Studio lamps, photoflood\n'
    '3,350 \t\t=> Studio "CP" light\n'
    '5,000 \t\t=> Horizon daylight\n'
    '5,500-6,000 \t=> Vertical daylight, electronic flash\n'
    '6,200 \t\t=> Xenon short-arc lamp\n'
    '6,500 \t\t=> Daylight, overcast\n'
    '6,500-9,500 \t=> LCD or CRT screen\n'
    '15,000-27,000 \t=> Clear blue poleward sky'
    )

    color_text = tk.Text(window, font=("TkDefaultFont", 14), bg=BACKGROUND, height=2, width=20, relief='flat')
    color_text.configure(state='disabled')

    (temp_entry, temp_str) = createEntry(window)
    gradient = createGradient(window, color_text, temp_entry)

    implEntry(temp_str, color_text, gradient)

    main_label.pack()
    temp_entry.pack()
    gradient.pack()
    color_text.pack()
    info_label.pack()
    info_frame.pack()

    window.mainloop()

######################################################################################
######################################################################################
######################################################################################

def createEntry(window: tk.Tk) -> tuple[tk.Entry, tk.StringVar]:
    def check_num(newval):
        return re.match('^[-+]?[0-9]*\.?[0-9]*$', newval) is not None
    check_num_wrapper = (window.register(check_num), '%P')

    temp_str = tk.StringVar()
    temp_entry = tk.Entry(window, fg=FOREGROUND, bg=HIGHTLIGHT0, insertbackground =FOREGROUND, relief='flat', font=("TkDefaultFont", 14), textvariable=temp_str, validate='key', validatecommand=check_num_wrapper)

    return (temp_entry, temp_str)

def implEntry(temp_str: tk.StringVar, color_label: tk.Text, gradient: tk.Canvas):

    def updated_temp(_a, _b, _c):
        if len(temp_str.get()) != 0 and temp_str.get() != '.':
            temp = float(temp_str.get())
            updateTemperatureDisplay(temp, color_label, gradient)
        else:
            color_label.delete(1.0, 'end')

    temp_str.trace_add("write", updated_temp)

######################################################################################
######################################################################################
######################################################################################

GRADIENT_WIDTH = 300
GRADIENT_HEIGHT = 50
GRADIENT_ARROW_HEIGHT = 16
GRADIENT_ARROW_WIDTH = 16
GRADIENT_ARROW_HALF_WIDTH = GRADIENT_ARROW_WIDTH / 2
GRADIENT_MAX_TEMP = 20_000
GRADIENT_PIXEL2TEMP = GRADIENT_MAX_TEMP / GRADIENT_WIDTH
GRADIENT_TEMP2PIXEL = GRADIENT_WIDTH / GRADIENT_MAX_TEMP
gradient_arrow_id = 0

def createGradient(window: tk.Tk, color_label: tk.Text, entry: tk.Entry) -> tk.Canvas:
    global gradient_arrow_id

    height = GRADIENT_HEIGHT + GRADIENT_ARROW_HEIGHT
    width = GRADIENT_WIDTH + GRADIENT_ARROW_WIDTH
    gradient = tk.Canvas(window, width=width, height=height, background=BACKGROUND, highlightthickness=0, relief='ridge')

    gradient_arrow_id = gradient.create_polygon(0, 0, GRADIENT_ARROW_HALF_WIDTH, GRADIENT_ARROW_HEIGHT, GRADIENT_ARROW_WIDTH, 0, fill='white', outline='black')

    for i in range(GRADIENT_WIDTH):
        temp = i * GRADIENT_PIXEL2TEMP
        col = rgb2hex(calculateColor(temp))
        gradient.create_rectangle(i + GRADIENT_ARROW_HALF_WIDTH, GRADIENT_ARROW_HEIGHT, i + GRADIENT_ARROW_HALF_WIDTH, height, outline='#' + col)

    def selectTemp(event):
        pixel_pos = event.x - GRADIENT_ARROW_HALF_WIDTH
        temp = min(max(int(GRADIENT_PIXEL2TEMP * pixel_pos), 0), GRADIENT_MAX_TEMP)

        entry.delete(0, "end")
        entry.insert(0, temp);
        updateTemperatureDisplay(temp, color_label, gradient)

    gradient.bind("<Button-1>", selectTemp)
    gradient.bind("<B1-Motion>", selectTemp)

    return gradient

def updateGradientArrow(gradient: tk.Canvas, temp: float):
    temp = min(max(temp, 0), GRADIENT_MAX_TEMP)
    pos = GRADIENT_TEMP2PIXEL * temp
    gradient.coords(gradient_arrow_id, pos, 0, pos + GRADIENT_ARROW_HALF_WIDTH, GRADIENT_ARROW_HEIGHT, pos + GRADIENT_ARROW_WIDTH, 0)

######################################################################################
######################################################################################
######################################################################################

def updateTemperatureDisplay(temp: float, color_label: tk.Text, gradient: tk.Canvas):
    color = calculateColor(temp)
    hex_str = rgb2hex(color)

    color_label.configure(state='normal')
    color_label.delete(1.0, "end")
    color_label.insert(1.0, 'RGB: {} {} {}\nHEX: {}'.format(color[0], color[1], color[2], hex_str));
    color_label.configure(state='disabled')

    color_label.config(fg = '#' + hex_str)
    updateGradientArrow(gradient, temp)

######################################################################################
######################################################################################
######################################################################################

def calculateColor(temp: float) -> tuple[int, int, int]:
    temp = max(temp, 1.0)
    temp = temp / 100.0

    red = 0
    green = 0
    blue = 0

    # calculate red
    if temp <= 66:
        red = 255
    else:
        red = temp - 60
        red = 329.698727446 * red ** -0.1332047592
        if red < 0:
            red = 0
        elif red > 255:
            red = 255

    # calculate green
    if temp <= 66:
        green = temp
        green = 99.4708025861 * log(green) - 161.1195681661
        if green < 0: 
            green = 0
        elif green > 255: 
            green = 255
    else:
        green = temp - 60
        green = 288.1221695283 * green ** -0.075514849
        if green < 0 : green = 0
        if green > 255 : green = 255
    

    # calculate blue
    if temp >= 66:
        blue = 255
    else:

        if temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * log(blue) - 305.0447927307
            if blue < 0 : blue = 0
            if blue > 255 : blue = 255

    return (int(red), int(green), int(blue))

def rgb2hex(rgb: tuple[int, int, int]) -> str:
    return '{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

if __name__ == "__main__":
    main()