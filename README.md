### Тестовое задание: Реализовать web приложение, для сбора и отслеживания изменений курса валют.

## Деплой готового проекта

 Протестировать развернутый проект можно [по этой ссылке](http://193.233.23.68:8082/swagger)
#### 1. Клонировать проект на локальный компьютер или удаленный сервер:

    git clone https://github.com/ead3471/currency_monitor.git

#### 2. Установить Docker и docker-compose если необходимо
#### 3. Изменить (при необходимости) файл .env в корне проекта:

    cd currency_monitor/infra
    nano .env

#### 4. Запустить проект:

    docker-compose up -d

#### 5. Выполнить создание таблиц баз данных:

    docker-compose exec api sh
    python manage.py migrate

#### 6. Описание API станет доступно по адресу:

    http://127.0.0.1:8082/swagger


## Задание 
Для получения курсов используй https://coinlayer.com/, получать данные можно по апи или же в результате парсинга.

#### UC:
1. Пользователь должен иметь возможность обратиться к api-нашего приложения и запустить фоновую задачу, по сбору данных о валютах (если данная задача активирована). Результат которого запишется в таблицу. 

2. Пользователь должен иметь возможность обратиться к api-нашего приложения и запустить фоновую задачу, по сбору данных о конкретной валюте, к примеру $.

3. Пользователь должен иметь возможность обратиться к api-нашего приложения и ВКЛЮЧИТЬ/ВЫКЛЮЧИТЬ фоновую задачу, по сбору данных о валюте/ах.

4. Пользователь должен иметь возможность обратиться к api-нашего приложения и получить ВСЮ историю, указанной в запросе валюты.
5. Пользователь должен иметь возможность обратиться к api-нашего приложения и получить разницу двух курсов для конкретной валюты (последней полученной и последней исторической).

#### 1. Для реализации НЕОБХОДИМО использовать Django (любой версии), DRF, Celery, django-simple-history

django-simple-history – использовать для отслеживания изменения валют, где ключом будет валюта.

#### 2. Frontend для данного задания не нужен, но опционально можно будет реализовать описание апи за счет swagger.

#### 3. Опциональный функционал:
 - Иметь возможность создавать задачи по рассписанию и управлять этим расписанием.
 - base session authentication


#### 4. 


