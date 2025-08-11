# Руководство пользователя lipunto

## Содержание

1. [Введение](#введение)
2. [Первый запуск](#первый-запуск)
3. [Основное использование](#основное-использование)
4. [Горячие клавиши](#горячие-клавиши)
5. [Настройка](#настройка)
6. [Устранение неполадок](#устранение-неполадок)
7. [Советы и хитрости](#советы-и-хитрости)
8. [Часто задаваемые вопросы](#часто-задаваемые-вопросы)

## Введение

**lipunto** — это умная утилита, которая автоматически исправляет опечатки, вызванные переключением раскладки клавиатуры. Она идеально подходит для тех, кто часто работает с английским и русским языками.

### Как это работает?

Когда вы печатаете текст на неправильной раскладке (например, вместо "привет" получается "ghbdtn"), просто нажмите назначенную горячую клавишу, и lipunto автоматически:

1. Определяет текст для исправления
2. Преобразует его с неправильной раскладки на правильную
3. Заменяет текст в приложении
4. Переключает раскладку клавиатуры
5. Показывает уведомление с результатом

### Для кого это?

- **Программисты**: Часто переключают раскладку при написании кода
- **Переводчики**: Работают с текстами на разных языках
- **Писатели и журналисты**: Пишут статьи на двух языках
- **Студенты**: Учатся и работают с учебными материалами
- **Все пользователи**: Кто просто устал от ручной коррекции опечаток

## Первый запуск

### Шаг 1: Проверка системы

Перед установкой убедитесь, что ваша система соответствует требованиям:

```bash
# Проверка версии Python
python3 --version
# Должно быть Python 3.13 или выше

# Проверка окружения рабочего стола
echo $XDG_CURRENT_DESKTOP
# Должно содержать KDE или Plasma
```

### Шаг 2: Установка зависимостей

#### Для Arch Linux:
```bash
# Установка ydotool
sudo pacman -S ydotool

# Установка qt5-tools (для qdbus и kdialog)
sudo pacman -S qt5-tools

# Настройка systemd сервиса
sudo systemctl daemon-reload
sudo systemctl enable ydotool.service
sudo systemctl start ydotool.service
```

#### Для Ubuntu/Debian:
```bash
# Установка ydotool
sudo apt install ydotool

# Установка qt5-tools
sudo apt install qt5-tools qtbase5-dev-tools

# Настройка systemd сервиса
sudo systemctl daemon-reload
sudo systemctl enable ydotool.service
sudo systemctl start ydotool.service
```

### Шаг 3: Установка lipunto

```bash
# Клонируем репозиторий (если вы не скачали архивом)
git clone https://github.com/yourusername/lipunto.git
cd lipunto

# Создаем виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Копируем скрипты в системные директории
sudo cp switch_layout.py /usr/local/sbin/
sudo cp sw_last.sh /usr/local/sbin/
sudo cp sw_selected.sh /usr/local/sbin/
sudo chmod +x /usr/local/sbin/*

# Настраиваем права на сокет
sudo chmod go+rw /tmp/.ydotool_socket
```

### Шаг 4: Настройка горячих клавиш

#### Способ 1: Автоматическая настройка
```bash
# Импортируем конфигурацию KDE
kwriteconfig5 --file kglobalshortcutsrc < lipunto.kksrc
kbuildsycoca5
```

#### Способ 2: Ручная настройка
1. Откройте `System Settings` → `Shortcuts` → `Custom Shortcuts`
2. Нажмите `Add Custom Shortcut`
3. Создайте две команды:
   - **Имя**: `sw_last`
   - **Команда**: `/usr/local/sbin/sw_last.sh`
   - **Горячая клавиша**: `Pause`

4. Создайте вторую команду:
   - **Имя**: `sw_selected`
   - **Команда**: `/usr/local/sbin/sw_selected.sh`
   - **Горячая клавиша**: `Shift+Pause`

### Шаг 5: Проверка работы

1. Откройте текстовый редактор (например, Kate или KWrite)
2. Напечатайте: `ghbdtn`
3. Нажмите `Pause`
4. Текст должен преобразоваться в: `привет`
5. Должно появиться уведомление

Поздравляем! lipunto установлен и готов к работе!

## Основное использование

### Режим 1: Коррекция последнего слова

**Когда использовать**: Когда вы напечатали одно слово на неправильной раскладке.

**Как использовать**:
1. Напечатайте текст на неправильной раскладке
2. Поставьте курсор в конец слова
3. Нажмите `Pause`

**Пример**:
```
До: ghbdtn| (курсор в конце)
Нажмите: Pause
После: привет| (курсор в конце)
```

### Режим 2: Коррекция выделенного текста

**Когда использовать**: Когда вы выделили несколько слов или фразу на неправильной раскладке.

**Как использовать**:
1. Выделите текст мышью или клавиатурой
2. Нажмите `Shift + Pause`

**Пример**:
```
До: [rfhf crbq] (текст выделен)
Нажмите: Shift + Pause
После: [дом работа] (текст выделен)
```

### Командная строка

Вы также можете использовать lipunto напрямую из командной строки:

```bash
# Коррекция последнего слова
python /usr/local/sbin/switch_layout.py last

# Коррекция выделенного текста
python /usr/local/sbin/switch_layout.py selected

# С включенными уведомлениями
python /usr/local/sbin/switch_layout.py last --show-popup

# С отключенными уведомлениями
python /usr/local/sbin/switch_layout.py last --no-popup

# С указанием времени отображения уведомления
python /usr/local/sbin/switch_layout.py last --popup-timeout 3
```

## Горячие клавиши

| Комбинация | Действие | Описание |
|------------|----------|----------|
| `Pause` | Коррекция последнего слова | Исправляет последнее слово перед курсором |
| `Shift + Pause` | Коррекция выделенного текста | Исправляет выделенный текст |
| `Ctrl + Alt + L` | Переключение раскладки | Стандартное переключение раскладки KDE |

### Настройка горячих клавиш

Если вы хотите изменить назначенные клавиши:

1. Откройте `System Settings` → `Shortcuts` → `Custom Shortcuts`
2. Найдите `sw_last` или `sw_selected`
3. Нажмите на поле с комбинацией клавиш
4. Нажмите новую комбинацию
5. Нажмите `Apply`

**Рекомендуемые комбинации**:
- `Pause` - удобно, так как редко используется
- `Ctrl + Alt + S` - альтернатива для режима "selected"
- `Ctrl + Alt + W` - альтернатива для режима "word"

## Настройка

### Базовая настройка

lipunto можно настроить несколькими способами:

#### 1. Через аргументы командной строки

```bash
# Изменение раскладки по умолчанию
python /usr/local/sbin/switch_layout.py last --layout ru_en

# Изменение задержек
python /usr/local/sbin/switch_layout.py last --delay-text-process 0.3

# Включение уведомлений
python /usr/local/sbin/switch_layout.py last --show-popup

# Изменение времени отображения уведомления
python /usr/local/sbin/switch_layout.py last --popup-timeout 2
```

#### 2. Через переменные окружения

Добавьте в ваш `~/.bashrc` или `~/.zshrc`:

```bash
export LIPUNTO_LAYOUT=ru_en
export LIPUNTO_DELAY_TEXT_PROCESS=0.3
export LIPUNTO_UI_SHOW_POPUP=true
export LIPUNTO_UI_POPUP_TIMEOUT=3
```

#### 3. Через конфигурационный файл

Создайте файл `~/.config/lipunto/config.json`:

```json
{
  "layout": "en_ru",
  "delays": {
    "clipboard_set": 0.05,
    "clipboard_get": 0.1,
    "text_process": 0.2,
    "paste": 0.1
  },
  "logging": {
    "enabled": false,
    "level": "WARNING",
    "file": "/tmp/lipunto.log",
    "console": false,
    "syslog": false
  },
  "ui": {
    "show_popup": true,
    "popup_timeout": 5
  }
}
```

### Расширенная настройка

#### Настройка задержек

Задержки важны для корректной работы lipunto. Вы можете настроить их под вашу систему:

- `clipboard_set`: Задержка при установке текста в буфер обмена (0.05-0.2с)
- `clipboard_get`: Задержка при получении текста из буфера обмена (0.1-0.3с)
- `text_process`: Задержка при обработке текста (0.2-0.5с)
- `paste`: Задержка при вставке текста (0.1-0.2с)

**Совет**: Если у вас быстрая система, уменьшите задержки. Если медленная — увеличьте.

#### Настройка логирования

Для отладки проблем вы можете включить логирование:

```bash
# Включение логирования
python /usr/local/sbin/switch_layout.py last --enable-logging

# Логирование в файл
python /usr/local/sbin/switch_layout.py last --enable-logging --log-file /var/log/lipunto.log

# Логирование с уровнем DEBUG
python /usr/local/sbin/switch_layout.py last --enable-logging --log-level DEBUG
```

#### Настройка уведомлений

lipunto может показывать уведомления о результатах коррекции:

- `--show-popup`: Включить уведомления
- `--no-popup`: Отключить уведомления
- `--popup-timeout`: Время отображения (1-60 секунд)

## Устранение неполадок

### Проблема 1: Горячие клавиши не работают

**Симптомы**: Нажатие Pause или Shift+Pause не вызывает реакции.

**Решения**:

1. **Проверка конфигурации KDE**:
   ```bash
   # Проверка конфигурации
   kwriteconfig5 --file kglobalshortcutsrc | grep sw_

   # Перезагрузка конфигурации
   kbuildsycoca5
   ```

2. **Проверка прав доступа**:
   ```bash
   # Проверка прав на скрипты
   ls -la /usr/local/sbin/sw_*

   # Проверка сокета ydotool
   ls -la /tmp/.ydotool_socket
   ```

3. **Проверка работы скриптов вручную**:
   ```bash
   # Тест работы скрипта
   /usr/local/sbin/sw_last.sh
   ```

### Проблема 2: ydotool не работает

**Симптомы**: Ошибки при работе с буфером обмена или эмуляции ввода.

**Решения**:

1. **Проверка сервиса ydotool**:
   ```bash
   # Проверка статуса сервиса
   systemctl status ydotool.service

   # Перезапуск сервиса
   sudo systemctl restart ydotool.service
   ```

2. **Проверка сокета**:
   ```bash
   # Проверка существования сокета
   ls -la /tmp/.ydotool_socket

   # Установка прав
   sudo chmod go+rw /tmp/.ydotool_socket
   ```

3. **Проверка установки ydotool**:
   ```bash
   # Проверка установки
   which ydotool

   # Проверка версии
   ydotool --version
   ```

### Проблема 3: qdbus не работает

**Симптомы**: Ошибки при работе с буфером обмена.

**Решения**:

1. **Проверка установки qt5-tools**:
   ```bash
   # Проверка установки
   which qdbus

   # Для Arch Linux
   sudo pacman -S qt5-tools

   # Для Ubuntu/Debian
   sudo apt install qt5-tools
   ```

2. **Проверка работы Klipper**:
   ```bash
   # Проверка работы Klipper
   qdbus org.kde.klipper /klipper getClipboardContents
   ```

### Проблема 4: kdialog не работает

**Симптомы**: Уведомления не отображаются.

**Решения**:

1. **Проверка установки kdialog**:
   ```bash
   # Проверка установки
   which kdialog

   # Установка (обычно входит в qt5-tools)
   sudo pacman -S qt5-tools
   ```

2. **Проверка работы KDE**:
   ```bash
   # Проверка работы KDE
   qdbus org.kde.kglobalaccel /component/kglobalaccel org.kde.kglobalaccel.Component.isActive
   ```

### Проблема 5: Преобразование текста не работает

**Симптомы**: Текст не преобразуется или преобразуется неправильно.

**Решения**:

1. **Проверка словарей**:
   ```bash
   # Проверка работы Python скрипта
   python /usr/local/sbin/switch_layout.py last --enable-logging --log-level DEBUG
   ```

2. **Проверка конфигурации**:
   ```bash
   # Проверка конфигурации
   python /usr/local/sbin/switch_layout.py last --layout en_ru
   ```

3. **Проверка прав доступа**:
   ```bash
   # Проверка прав на Python скрипт
   ls -la /usr/local/sbin/switch_layout.py
   ```

### Проблема 6: Конфликты с другими программами

**Симптомы**: lipunto конфликтует с другими утилитами автоматизации.

**Решения**:

1. **Проверка конфликтов с ydotool**:
   ```bash
   # Проверка запущенных процессов
   ps aux | grep ydotool

   # Проверка сокетов
   lsof /tmp/.ydotool_socket
   ```

2. **Изменение конфигурации**:
   ```bash
   # Изменение пути сокета (если нужно)
   export YDOTOOL_SOCKET=/tmp/.ydotool_socket_custom
   ```

## Советы и хитрости

### 1. Оптимизация производительности

```bash
# Для быстрой системы
export LIPUNTO_DELAY_TEXT_PROCESS=0.1
export LIPUNTO_DELAY_CLIPBOARD_GET=0.05

# Для медленной системы
export LIPUNTO_DELAY_TEXT_PROCESS=0.5
export LIPUNTO_DELAY_CLIPBOARD_GET=0.3
```

### 2. Интеграция с другими приложениями

#### VS Code
Добавьте в настройки VS Code:
```json
{
  "terminal.integrated.env.linux": {
    "LIPUNTO_LAYOUT": "en_ru",
    "LIPUNTO_UI_SHOW_POPUP": "true"
  }
}
```

#### Konsole
Добавьте в `~/.config/konsolerc`:
```ini
[General]
Environment=LIPUNTO_LAYOUT=en_ru;LIPUNTO_UI_SHOW_POPUP=true
```

### 3. Создание настольных файлов

Для удобства запуска создайте `.desktop` файлы:

```bash
# Создание файла для режима "last"
cat > ~/.local/share/applications/sw_last.desktop << EOF
[Desktop Entry]
Name=lipunto (last word)
Exec=/usr/local/sbin/sw_last.sh
Icon=preferences-desktop-keyboard
Type=Application
Categories=Utility;
EOF

# Создание файла для режима "selected"
cat > ~/.local/share/applications/sw_selected.desktop << EOF
[Desktop Entry]
Name=lipunto (selected text)
Exec=/usr/local/sbin/sw_selected.sh
Icon=preferences-desktop-keyboard
Type=Application
Categories=Utility;
EOF
``