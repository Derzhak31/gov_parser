Для запуска требуется установить виртуальное окружение:
    Если используем poetry: `poetry install`
    Если pip, нужно установить библиотеки: celery[redis], bs4, requests, xmltodict

Далее поднимаем redis в докер контейнере `docker run --name redis -p 6379:6379 -d redis`
    Если нет образа redis `docker pull redis`

Запускаем:
    В первом терминале запускаем планировщик `celery -A tasks beat -l info`
    В следующем терминале запускаем worker `celery -A tasks worker -l info`
    В 3 терминале запускаем скрипт `python tasks.py`

Переходим в терминал worker'а и смотрим лог выполнения. Скрипт работает асинхронно 