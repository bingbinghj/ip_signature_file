# IP签名档

修改自[xhboke/IP: IP签名档显示IP、地址、日期······](https://github.com/xhboke/IP)

## 演示效果

![images](https://youke1.picui.cn/s1/2025/09/26/68d63639357c8.png)

## 修改说明

1.PHP改为Python，使用 Flask 提供 Web 服务，输出 SVG 格式，并支持叠加 PNG 图片作为装饰。

2.删除天气及温度

3.API调用修改为 `https://api.vore.top/api/IPdata?ip=`

4.以及其他小修改

## 部署

#### 1.安装Python 和 pip

```
apt update -y && apt install python3 python3-venv python3-pip -y
```

#### 2.创建项目

```
git clone https://github.com/bingbinghj/ip_signature_file.git
cd ip_signature_file
```

#### 3.创建虚拟环境(可选)

```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

#### 4.安装依赖

```
pip install -r requirements.txt
```

#### 5.测试运行

```
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 6.配置Systemd 开机自启

Ctrl + C 停止项目，创建一个systemd 服务文件

```
nano /etc/systemd/system/ip_signature_file.service
```

内容示例：

```
[Unit]
Description=ip_signature_file
After=network.target

[Service]
User=root
WorkingDirectory=/root/ip_signature_file
Environment="PATH=/root/ip_signature_file/venv/bin"
ExecStart=/root/ip_signature_file/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ctrl + X 输入 y 回车保存

#### 重新加载 systemd 配置

```
systemctl daemon-reload
```

#### 启动服务

```
systemctl start ip_signature_file
```

#### 查看状态

```
systemctl status ip_signature_file
```

#### 设置开机自启

```
systemctl enable ip_signature_file
```

或者使用更简单的Docker

```
docker run -d \
--restart always \
--name ip \
-p 5000:5000 \
bingbing123a1/ip_signature_file:latest
```

#### 7.使用Nginx反向代理(可选)

配置文件示例：

```
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name abc.com;

    ssl_certificate     /etc/ssl/IP/fullchain.cer;
    ssl_certificate_key /etc/ssl/IP/private.key;

    # 如果通过 Cloudflare，需要加 CF IP 解析
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 131.0.72.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;

    real_ip_header CF-Connecting-IP;
    real_ip_recursive on;

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:5000;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

部署完成后可通过**IP**或**IP:端口**访问，**127.0.0.1**是随机背景图片，**127.0.0.1/imgXX**是固定背景图片