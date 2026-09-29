# Perfect World — Колесо Фортуны

Windows desktop roulette made with Python + PySide6.

## Запуск
```
pip install -r requirements.txt
python roulette.py
```

## EXE
```
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name PerfectWorldRoulette roulette.py
```

Крутка доступна один раз в 24 часа. Время последней крутки сохраняется локально в state.json.
Призы и их вес меняются в config.json.
