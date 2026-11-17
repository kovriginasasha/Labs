# FitLife — ЛР №3: подключение базы данных (SQLite + SQLModel)

Те же два сервиса и те же действия, что в ЛР №2, но данные хранятся в БД и не пропадают
при перезапуске. У каждого сервиса своя база (микросервисный подход):

| Сервис | Порт | Файл БД | Таблицы |
|---|---|---|---|
| subscriptions_service | 8001 | subscriptions.db | tariff, subscription, payment |
| booking_service | 8002 | booking.db | fitclass, booking |

Файлы .db создаются автоматически при первом запуске: функция conn() (database/connection.py)
вызывается при старте приложения и выполняет SQLModel.metadata.create_all(engine).
echo=True: в терминале видны SQL-команды (CREATE TABLE, INSERT, SELECT).

CRUD-операции: тарифы (сервис 8001) и занятия (сервис 8002) — create/read/update/delete.
Готовые команды curl: COMMANDS.md (два набора).

    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt

Терминал 1:  cd subscriptions_service && python main.py
Терминал 2:  cd booking_service && python main.py

Swagger: http://127.0.0.1:8001/docs  и  http://127.0.0.1:8002/docs
Номер клиента (client_id) указывается в теле запроса или параметром адреса; в Swagger уже подставлен 1.

## Проверка
1. :8002 POST /bookings/ {"client_id":1,"class_id":1} -> 403 (нет абонемента)
2. :8001 POST /subscriptions/buy {"client_id":1,"tariff_id":1,"card_token":"declined"} -> 402
3. :8001 POST /subscriptions/buy {"client_id":1,"tariff_id":1,"card_token":"tok_visa_4242"} -> 201
4. :8002 POST /bookings/ {"client_id":1,"class_id":1} -> 201
5. Остановите оба сервиса (Ctrl+C) и запустите снова: GET /bookings/my?client_id=1 и GET /subscriptions/my?client_id=1
   по-прежнему показывают данные — они хранятся в БД.
6. Просрочка: client_id = 99 -> :8001 GET /subscriptions/active даёт 404,
   :8002 POST /bookings/ даёт 403, POST /subscriptions/expire переводит абонемент в expired.

## Просмотр базы
    cd subscriptions_service
    sqlite3 subscriptions.db
    .tables
    SELECT * FROM subscription;
    SELECT * FROM payment;
    .quit

Сброс данных: остановить сервис, удалить файл .db, запустить снова.
