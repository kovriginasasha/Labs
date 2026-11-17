# FitLife — ЛР №2 (данные хранятся в памяти)

Сервис абонементов и оплаты — порт 8001, сервис записи на тренировки — порт 8002.
Структура как в практическом №7: main.py, database, routes, models (+ services для внешних вызовов).
Данные лежат в списках в памяти (database/connection.py) и сбрасываются при перезапуске.

    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt

Терминал 1:  cd subscriptions_service && python main.py
Терминал 2:  cd booking_service && python main.py

Swagger: http://127.0.0.1:8001/docs  и  http://127.0.0.1:8002/docs
Номер клиента (client_id) указывается в теле запроса или параметром адреса; в Swagger уже подставлен 1.

## Основной сценарий
1. :8002 POST /bookings/ {"client_id":1,"class_id":1} -> 403 (нет абонемента)
2. :8001 POST /subscriptions/buy {"client_id":1,"tariff_id":1,"card_token":"declined"} -> 402
3. :8001 POST /subscriptions/buy {"client_id":1,"tariff_id":1,"card_token":"tok_visa_4242"} -> 201
4. :8002 POST /bookings/ {"client_id":1,"class_id":1} -> 201
5. :8002 GET /classes/ (свободных мест стало меньше), GET /bookings/my?client_id=1

## Срок действия абонемента
- Срок = дата покупки + duration_days тарифа (месяц = 30 дней).
- Абонемент проверяется по датам, а не только по статусу: просроченный не сработает,
  даже если статус ещё active.
- Запись проверяет абонемент на ДАТУ ЗАНЯТИЯ: класс 4 (через 60 дней) недоступен
  клиенту с месячным абонементом (403), хотя сегодня абонемент действует.
- Демо-клиент 99: абонемент просрочен 10 дней назад (статус ещё active).
  В Swagger укажите client_id = 99 (в теле запроса или параметре):
  :8001 GET /subscriptions/active -> 404; :8002 POST /bookings/ {"client_id":99,"class_id":1} -> 403
  :8001 GET /subscriptions/my -> видно просроченный; POST /subscriptions/expire -> статус expired
