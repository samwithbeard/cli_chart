import math
import time
from typing import List

# Create a test array of 100 numbers that form a sine wave
def sine_samples(n: int = 100, cycles: float = 2.0) -> List[float]:
    return [math.sin(2 * math.pi * cycles * i / n) for i in range(n)]

# Map a value in [-1, 1] to one of the block symbols
SYMBOLS = ['▁', '▂', '▃', '▄', '▅', '█']  # using the block characters provided (arranged low->high)

r = '255'
g = '200'
b = '0'
CUSTOM = '\033[38;2;255;100;0m'
CUSTOM1 = '\033[38;2;100;100;0m'
CUSTOM2 = '\033[38;2;50;100;0m'
RGB = '\033[38;2;' + str(r) + ';' + str(g) + ';' + str(b) + 'm'
RESET = '\033[0m'  # Resets color to default


def value_to_symbol(value: float, symbols: List[str] = SYMBOLS) -> str:
    # clamp value to [-1, 1]
    v = max(-1.0, min(1.0, value))
    # normalize to index range 0..len(symbols)-1
    idx = int(round((v + 1) / 2 * (len(symbols) - 1)))
    return symbols[idx]

# Create a loop which outputs one symbol after another (streaming)
def stream_plot(values: List[float], delay: float = 0.03):
    for v in values:
        print(value_to_symbol(v), end='', flush=True)
        time.sleep(delay)
    print()  # newline at end

# Create a function that returns a horizontal "plot" string for a list of values
def line_plot(values: List[float], symbols: List[str] = SYMBOLS, label="", length: int = 100) -> str:
    # optionally downsample to requested length, then map values to symbols
    if length and len(values) > length:
        step = len(values) / length
        indices = [min(int(i * step), len(values) - 1) for i in range(length)]
        sampled = [values[i] for i in indices]
    else:
        sampled = values
    chart = ''.join(value_to_symbol(v, symbols) for v in sampled) + (length - len(sampled)) * ' '
    return f"{chart} {label}" if label else chart

# Create a one-line heatmap using 24-bit ANSI colors
def heat_map(values: List[float], length: int = 100, min_value: float = None, max_value: float = None, label: str = "", rainbow=False) -> str:
    if length and len(values) > length:
        step = len(values) / length
        indices = [min(int(i * step), len(values) - 1) for i in range(length)]
        sampled = [values[i] for i in indices]
    else:
        sampled = list(values)

    if not sampled:
        return ""

    if min_value is None:
        min_value = min(sampled)
    if max_value is None:
        max_value = max(sampled)
    if max_value == min_value:
        max_value = min_value + 1e-9

    # convert HSV (h in degrees, s/v 0..1) to RGB 0..255
    def hsv_to_rgb(h: float, s: float, v: float):
        h = h % 360
        c = v * s
        x = c * (1 - abs(((h / 60) % 2) - 1))
        m = v - c
        if h < 60:
            rp, gp, bp = c, x, 0
        elif h < 120:
            rp, gp, bp = x, c, 0
        elif h < 180:
            rp, gp, bp = 0, c, x
        elif h < 240:
            rp, gp, bp = 0, x, c
        elif h < 300:
            rp, gp, bp = x, 0, c
        else:
            rp, gp, bp = c, 0, x
        return int((rp + m) * 255), int((gp + m) * 255), int((bp + m) * 255)

    blocks = []
    for v in sampled:
        ratio = (v - min_value) / (max_value - min_value)
        ratio = max(0.0, min(1.0, ratio))
        # map ratio to hue: 240 (blue) -> 0 (red)
        hue = (1.0 - ratio) * 240.0
        if rainbow:
            r_, g_, b_ = hsv_to_rgb(hue, 1.0, ratio) #für regenbogen
        else:
            r_, g_, b_ = hsv_to_rgb(200, 1.0 , ratio) #einfarbig blau
        blocks.append(f'\033[38;2;{r_};{g_};{b_}m█')
    chart = ''.join(blocks) + RESET
    return f"{chart} {label}" if label else chart



# Print colored text
print(CUSTOM + "█" + CUSTOM1 + "█" + CUSTOM2 + "█" + RESET)

def gauge_plot(value: float, min_value: float, max_value: float, label="", length: int = 100) -> str:
    # Normalize value to [0, 1]
    ratio = (value - min_value) / (max_value - min_value)
    ratio = max(0.0, min(1.0, ratio))  # Clamp to [0, 1]
    filled_length = int(length * ratio)    
    bar = '█' * filled_length + '░' * (length - filled_length)+" "+str(value)+" "+str(label)
    #print(bar)
    return f'{bar}'


def pie_chart(values: float, label="",length: int = 100) -> str:
    vals = list(values)
    total = sum(vals)
    #print("")  # sum of all values
    if total <= 0 or not vals:
        return ""
    # block/shade symbols to differentiate slices
    symbols = ['█','░','▓', '▒',  '▌', '▐']
    # compute raw lengths and integer lengths
    raw_lengths = [v / total * length for v in vals]
    int_lengths = [int(r) for r in raw_lengths]
    # distribute any remaining characters by largest fractional parts
    remainder = length - sum(int_lengths)
    if remainder > 0:
        frac_idx = sorted(range(len(raw_lengths)), key=lambda i: raw_lengths[i] - int_lengths[i], reverse=True)
        for i in range(remainder):
            int_lengths[frac_idx[i % len(frac_idx)]] += 1
    # build chart string
    chart = ''.join(symbols[i % len(symbols)] * int_lengths[i] for i in range(len(vals)))
    # create a simple legend with raw values and percentages
    legend = " ".join(f"{vals[i]}({vals[i]/total*100:.1f}%)" for i in range(len(vals)))
    return f"{chart} total={total} {legend} {label}"

def show_examples():
    pie=pie_chart([10,20,70], "pie-label",length=100)
    gauge=gauge_plot(75, 0, 100, "[km/h] test", length=100)
    sinewave = sine_samples(100, cycles=3)  # 2 cycles across 100 points
    print("Pie chart:")
    print(pie)
    print("Gauge plot:")
    print(gauge)
    print("Line plot:")
    print(line_plot(sinewave))
    print("heatmap:")
    print(heat_map(sinewave))
    print(heat_map([1,1,1,1,2,2,2,3,3,3,4,4,4]))
    print("rainbow heatmap:")
    print(heat_map(sinewave, rainbow=True))


if __name__ == "__main__":
    show_examples()
    
    # Example: stream the symbols one after another
    #print("Streaming plot:")
    #stream_plot(data, delay=0.02)










