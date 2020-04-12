<p align="center">
  <img href="#" src="https://github.com/WoodyMKD/Facebook-Group-Post-Scraper/blob/master/logo.png?raw=true">
</p>

##  Упатство: :video_game: 
- *Инсталирајте geckodriver (https://github.com/mozilla/geckodriver/releases/tag/v0.26.0)*
- *Инсталирајте го selenium за python:* ```pip install selenium```
- *Пополнете ги информациите кои се бараат на почетокот од скриптата*:
``` geckodriver_path = "XXX"
geckodriver_log_path = "XXX"
fb_username = "XXX"
fb_pass = "XXX"
postgre_db_username = "XXX"
postgre_db_password = "XXX"
postgre_db_name = "XXX"
postgre_db_host = "XXX"
headlessMode = True
```

Пример за користење на скриптата: ```python scraper.py -g 125093080970970 -d 1```
