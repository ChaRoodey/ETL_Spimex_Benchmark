## SPIMEX ETL Parser

ETL-пайплайн для загрузки и обработки бюллетеней торгов биржи SPIMEX с сохранением данных в PostgreSQL.

## Возможности

- Асинхронная загрузка файлов (httpx, asyncio)  
- Поддержка PDF и Excel бюллетеней  
- Парсинг таблиц с единицей измерения «Метрическая тонна»  
- Фильтрация записей с количеством договоров > 0  
- Сохранение результатов в PostgreSQL через SQLAlchemy  
- Логирование и обработка ошибок  
- Ограничение RPS для обхода rate limiting  

## Стек технологий

- Python 3.14  
- uv  
- asyncio  
- httpx  
- pandas  
- pdfplumber  
- SQLAlchemy  
- PostgreSQL  

## Установка

Создайте и настройте базу данных PostgreSQL.

Параметры подключения к БД задаются в файле:

```bash
src/db/async_session.py
```

⚠️ В текущей версии параметры подключения захардкожены и при необходимости должны быть изменены вручную.

Установка зависимостей:

```bash
uv sync
```

## Запуск

Запуск производится из корня проекта:
```bash
uv run python src/main.py
```

## Результат выполнения задания

Загружены и обработаны данные SPIMEX начиная с 2023 года.

ETL finished:
- Time: 578.92 sec
- PDF files processed: 119
- Excel files processed: 728
- Failed to download: 0
- Rows inserted: 176725
