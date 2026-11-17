# FitLife — два микросервиса (ЛР №2)

Сервис абонементов и оплаты — порт 8001, сервис записи на тренировки — порт 8002.

    python3 -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
    pip install -r requirements.txt

Терминал 1:  cd subscriptions_service && python main.py
Терминал 2:  cd booking_service && python main.py

Документация Swagger: http://127.0.0.1:8001/docs  и  http://127.0.0.1:8002/docs

## Проверка (curl)

    # тарифы
    curl http://127.0.0.1:8001/tariffs/
    # запись БЕЗ абонемента -> 403
    curl -X POST http://127.0.0.1:8002/bookings/ -H 'Content-Type: application/json' -d '{"client_id":1,"class_id":1}'
    # оплата отклонена -> 402
    curl -X POST http://127.0.0.1:8001/subscriptions/buy -H 'Content-Type: application/json' -d '{"client_id":1,"tariff_id":1,"card_token":"declined"}'
    # оплата успешна -> 201
    curl -X POST http://127.0.0.1:8001/subscriptions/buy -H 'Content-Type: application/json' -d '{"client_id":1,"tariff_id":1,"card_token":"tok_visa_4242"}'
    # запись С абонементом -> 201
    curl -X POST http://127.0.0.1:8002/bookings/ -H 'Content-Type: application/json' -d '{"client_id":1,"class_id":1}'
    # расписание со свободными местами
    curl http://127.0.0.1:8002/classes/
