from flask import Flask, Response, request
import base64
import os
from datetime import datetime
from user_agents import parse as ua_parse
import pytz
from datetime import datetime
import re
import requests
import random

app = Flask(__name__)

# ================== 配置 ==================
# 图片配置
images_config = {
    'img1': {'file': './static/images/1.png', 'x': 156, 'y': -19.7, 'width': 190, 'height': 150},
    'img2': {'file': './static/images/2.png', 'x': 146, 'y': -195.5, 'width': 191, 'height': 500},
    'img3': {'file': './static/images/3.png', 'x': 195, 'y': 1, 'width': 150, 'height': 108},
    'img4': {'file': './static/images/4.png', 'x': 185, 'y': -1.5, 'width': 170, 'height': 110},
    'img5': {'file': './static/images/5.png', 'x': 190, 'y': -9, 'width': 170, 'height': 140},
    'img6': {'file': './static/images/6.png', 'x': 188, 'y': -6.5, 'width': 170, 'height': 115},
    'img7': {'file': './static/images/7.png', 'x': 195, 'y': -1.5, 'width': 170, 'height': 110},
    'img8': {'file': './static/images/8.png', 'x': 195, 'y': -1.5, 'width': 170, 'height': 110},
    'img9': {'file': './static/images/9.png', 'x': 200, 'y': -8.5, 'width': 185, 'height': 130},
    'img10': {'file': './static/images/10.png', 'x': 186, 'y': -1.5, 'width': 170, 'height': 110},
    'img11': {'file': './static/images/11.png', 'x': 188, 'y': -1.5, 'width': 170, 'height': 110},
    'img12': {'file': './static/images/12.png', 'x': 194, 'y': -1.5, 'width': 170, 'height': 110},
    'img13': {'file': './static/images/13.png', 'x': 192.5, 'y': -1.5, 'width': 170, 'height': 110},
    'img14': {'file': './static/images/14.png', 'x': 189, 'y': 1.5, 'width': 170, 'height': 107},
    'img15': {'file': './static/images/15.png', 'x': 185, 'y': -1.5, 'width': 170, 'height': 110},
    'img16': {'file': './static/images/16.png', 'x': 188, 'y': 0.5, 'width': 180, 'height': 115},
    'img17': {'file': './static/images/17.png', 'x': 197, 'y': -1.5, 'width': 180, 'height': 120},
    'img18': {'file': './static/images/18.png', 'x': 172.5, 'y': 3, 'width': 180, 'height': 110},
    'img19': {'file': './static/images/19.png', 'x': 168, 'y': 3.5, 'width': 180, 'height': 110},
    'img20': {'file': './static/images/20.png', 'x': 193.5, 'y': 3.5, 'width': 175, 'height': 105},
    'img21': {'file': './static/images/21.png', 'x': 178.5, 'y': -10.5, 'width': 210, 'height': 120}
}

# SVG输出 配置
svg_config = {
    'width': 315,           # SVG 画布的宽度
    'height': 110,          # SVG 画布的高度
    'font_size': 12,        # 默认文字大小
    'text_color': 'black',  # 文本颜色
    'bg_color': '#ffffff',  # 背景颜色
    'radius': 5,            # 圆角半径，用于矩形边框和背景
    'border_color': 'black',# 边框颜色
    'border_width': 1,      # 边框宽度
    'left_margin': 5,       # 文本的左边距
    'line_positions': [20, 40, 60, 80, 100]  # 每一行文字的纵坐标位置
}

# ================== 功能函数 ==================
def get_ip():
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr
    return ip

def get_location_by_ip(ip): 
    try:
        url = f"https://api.vore.top/api/IPdata?ip={ip}"
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200:
                ip_line = data.get("ipinfo", {}).get("text", ip)

                adcode = data.get("adcode", {})
                province = adcode.get("p", "")

                if province.endswith("省") or province.endswith("区"):
                    province = province[:-1]

                ipdata = data.get("ipdata", {})
                city = ipdata.get("info2", "")
                district = ipdata.get("info3", "")

                addr_line = " ".join(filter(None, [province, city, district])).strip()
                return ip_line, addr_line if addr_line else "未知地区"
        return ip, "未知地区"
    except Exception:
        return ip, "未知地区"

def parse_ua(ua_string):
    ua = ua_parse(ua_string)
    os_display = f"{ua.os.family} {ua.os.version_string}" if ua.os.version_string else ua.os.family
    if "Windows 10" in os_display:
        os_display = os_display.replace("Windows 10", "Windows 10/11")
    browser_display = f"{ua.browser.family} ({ua.browser.version_string})" if ua.browser.version_string else ua.browser.family
    return os_display, browser_display

# ================== 生成 SVG ==================
def generate_svg(img_key):
    ip = get_ip()
    ip_display, address = get_location_by_ip(ip)

    ua_string = request.headers.get('User-Agent', '')
    os_display, browser_display = parse_ua(ua_string)

    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)

    weekarray = ['一','二','三','四','五','六','日']
    current_date = now.strftime(f"%Y年%m月%d日") + f" 星期{weekarray[now.weekday()]}"

    x = svg_config['left_margin']
    linePos = svg_config['line_positions']
    svg_text = f'''
<text x="{x}" y="{linePos[0]}" font-size="{svg_config['font_size']}" fill="black">🏠 欢迎您来自 <tspan fill="red">{address}</tspan> 的朋友</text>
<text x="{x}" y="{linePos[1]}" font-size="{svg_config['font_size']}" fill="black">📅 今天是 {current_date}</text>
<text x="{x}" y="{linePos[2]}" font-size="{svg_config['font_size']}" fill="black">🛜 您的IP是: <tspan fill="red">{ip_display}</tspan></text>
<text x="{x}" y="{linePos[3]}" font-size="{svg_config['font_size']}" fill="black">💻️️ 您使用的是 {os_display} 操作系统</text>
<text x="{x}" y="{linePos[4]}" font-size="{svg_config['font_size']}" fill="black">🌐 您使用的是 {browser_display} 浏览器</text>
'''

    w = svg_config['width']
    h = svg_config['height']
    rx = svg_config['radius']
    bw = svg_config['border_width']

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet">
  <rect x="0" y="0" width="{w}" height="{h}" rx="{rx}" ry="{rx}" fill="{svg_config['bg_color']}" />
  <rect x="{bw/2}" y="{bw/2}" width="{w-bw}" height="{h-bw}" rx="{rx}" ry="{rx}" fill="none" stroke="{svg_config['border_color']}" stroke-width="{bw}" />'''

    # 背景人物
    img_cfg = images_config.get(img_key)
    if img_cfg and os.path.exists(img_cfg['file']):
        with open(img_cfg['file'], 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        svg += f'\n  <image href="data:image/png;base64,{img_data}" x="{img_cfg["x"]}" y="{img_cfg["y"]}" width="{img_cfg["width"]}" height="{img_cfg["height"]}" preserveAspectRatio="xMidYMid meet" />'

    svg += svg_text
    svg += '\n</svg>'
    return svg

# ================== 路由 ==================
@app.route('/')
def index():
    img_key = random.choice(list(images_config.keys()))
    svg = generate_svg(img_key)
    return Response(svg, mimetype='image/svg+xml')

@app.route('/<img_key>')
def serve_svg(img_key):
    if img_key in images_config:
        svg = generate_svg(img_key)
        return Response(svg, mimetype='image/svg+xml')
    return "Image key not found", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
