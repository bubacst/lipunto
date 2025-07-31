# lipunto

Correct mistyping keyboard layout

Для правильной работы необходимо установить ydotool, qdbus.
Установка ydotool:  pacman -S ydotool
По умолчанию ydotoold работает в arch linux от имени пользователя, необходимо перенастроить для работы от root. Для этого создайте файл /etc/systemd/system/ydotool.service с содержимым:
[Unit]
Description=Starts ydotoold service

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/ydotoold
ExecReload=/usr/bin/kill -HUP $MAINPID
KillMode=process
TimeoutSec=180

[Install]
WantedBy=default.target

Затем:
systemctl daemon-reload
systemctl enable ydotool.service
systemctl start ydotool.service
systemctl status ydotool.service

Убедится в наличии сокета: /tmp/.ydotool_socket и установить ему права: chmod go+rw /tmp/.ydotool_socket

Установка qdbus:  pacman -S install qt5-tools

Затем необходимо привязать клавиши на вызов скрипта для коррекции последнего слова перед кусором либо выделенного текста. Привер в файле lipunto.kksrc
