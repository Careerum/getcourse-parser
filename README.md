# getcourse-parser
Позволяет парсить HTML-вывод геткурса.

API:
- Инициализация
  - Метод инициализация центрального объекта GetCourse происходит любым из двух способов: через куку либо через пару логин-пароль (обязательно указывать либо логин/пароль, либо куку. Если указано и то и другое, используется только кука).
    * username/password - Логин и пароль к GetCourse
    * url - ссылка на тенант Getcourse, по умолчанию - "https://school.careerum.ru"
    * cookie - кука PHPSESSID_SUB, взятая из браузера

    - Через куку (урл необязателен, но кука должна быть на то же имя сервера)
    ```python
    from getcourse import *
    gc = GetCourse(url="https://school.careerum.ru", cookie="07f3d96b13b8b33112345638d39ea485")
    ```
    - Через пару логин-пароль
    ```python
    from getcourse import *
    gc = GetCourse(url="https://school.careerum.ru", username='is@careerum.com', password='S3cr37')
    ```     
- Работа с задачами
  - Метод MissionTasks возвращает список задач в указанном процессе
    * processId - ID процесса
    ```python
    gc.MissionTasks(processId=12345)
    ```
    Пример вывода:
    ```python
    [
      {'id': '2216872626', 'client': ('64348545', 'Наталия Маньковская'), 'subject': ('user', '64348545'), 'status': 'Отложена'},
      {'id': '2217509003', 'client': ('45953922', 'Мария Хабахпашева'), 'subject': ('user', '45953922'), 'status': 'Отложена'}
    ]
    ```
  - Метод missionTask возвращает информацию о шагах, выполненых в рамках конкретной задачи
    * taskId - ID задачи
    ```python
    gc.MissionTask(taskId=12345)
    ```
    Пример вывода:
    ```javascript
    [
      {'order': 1, 'resultData': None, 'resultSummary': 'Выполнено', 'stepAction': 'Начало скрипта', 'stepId': 85102200676, 'stepTemplateId': 14646448, 'stepTitle': '"Начало работы"', 'subprocess': '', 'who': ''},
      {'order': 2, 'resultData': None, 'resultSummary': '', 'stepAction': 'Завершение процесса', 'stepId': 85102274162, 'stepTemplateId': 7993476, 'stepTitle': '"Завершение процесса"', 'subprocess': '522600', 'who': ''}
    ]
    ```
- Работа с LMS
  - Метод Streams возвращает вложенные курсы для указанного курса (stream)
    * stream - ID родительского stream, по умолчанию None (т.е. возвращается вся библиотека)
    ```python
    gc.Streams(stream=635684464)
    ```
    Пример вывода:
    ```python
    [
      {
        'children': [
          {'children': None, 'id': '635684601', 'title': '1 сессия. Запрос на курс и карьерные установки'},
          {'children': None, 'id': '635684602', 'title': '2 сессия. Таланты и ценности'}
        ],
        'id': '635684600',
        'title': 'Программа «Real Me: как найти себя в работе и жизни»'
      }
    ]
    ```
  - Метод Lessons возвращает список ID уроков указанного курса (stream)
    * stream - ID курса
    ```python
    gc.Lessons(stream=635684464)
    ```
    Пример вывода:
    ```python
    ['253768811', '253768812', '253768813']
    ```
  - Метод Lesson возвращает информацию об уроке
    * lesson - ID урока
    Возвращается кортеж из:
    * Названия урока
    * Списка URL из iframe'ов
    ```python
    gc.Lesson(lesson=253768811)
    ```
    Пример вывода:
    ```python
    ('Урок 1. Ваш запрос на курс', ['https://video.dreamcatchme.ru/cRkmQf4A'])
    ```      
- Работа с покупками
  - Метод userProduct возвращает информацию о покупке
    * userProduct - ID покупки
        Возвращается объект:
        * title - Название покупки
        * status - Состояние покупки (Активен, Завершен, Не активен, )
        * prolong - состояние автопродления (True/False)
        * number - номер покупки
        * client - ID клиента
        * product - ID продукта
        * orders - список ID заказов
    ```python
    gc.userProduct(userProduct=151336186)
    ```
    Пример вывода:
    ```python
    {
      'client': 232034086,
      'number': 20444,
      'orders': [200203221, 191334515, 182847122],
      'product': 1581756,
      'prolong': True,
      'status': 'Завершена',
      'title': 'Покупка #20444. Карьерум.Клуб: базовое членство в клубе'
    }
    ```      
- Работа с пользователями
  - Метод Users возвращает список ID пользователей по указанному фильтру
        * filter - словарь в формате uc\[rule_string\] запроса https://school.dreamcatchme.ru/pl/user/user/index?uc\[rule_string\]=\{...\}
    ```python
    gc.Users(
      filter={
        'type': 'andrule',
        'inverted': 0,
        'params': {
          'mode': 'or',
          'children': [
            {
              'type': 'idsrule',
              'inverted': 0,
              'params': {
                  'value': '23135576',
                  'valueMode': None
              }
            },
            {
              'type': 'user_email_like',
              'inverted': 0,
              'params': {
                  'value': 'solntsev@innokentiy.ru',
                  'valueMode': None
              }
            }
          ]
        }
      }
    )
    ```
    Пример вывода:
    ```python
    [23135576]
    ```      
    Для получения фильтров удобно использовать сервис парсинга URL https://www.freeformatter.com/url-parser-query-string-splitter.html:
    | Оригинальный URL | Распаршенный Query String |
    | --- | --- |
    | [https://school.careerum.ru/pl/user/user/index?uc%5Bsegment_id%5D=0&uc%5Brule_string%5D=%7B%22type%22%3A%22(...)innokentiy.ru](https://school.careerum.ru/pl/user/user/index?uc%5Bsegment_id%5D=0&uc%5Brule_string%5D=%7B%22type%22%3A%22andrule%22%2C%22inverted%22%3A0%2C%22params%22%3A%7B%22mode%22%3A%22or%22%2C%22children%22%3A%5B%7B%22type%22%3A%22idsrule%22%2C%22inverted%22%3A0%2C%22params%22%3A%7B%22value%22%3A%2223135576%22%2C%22valueMode%22%3Anull%7D%7D%2C%7B%22type%22%3A%22user_email_like%22%2C%22inverted%22%3A0%2C%22params%22%3A%7B%22value%22%3A%22solntsev%40innokentiy.ru%22%2C%22valueMode%22%3Anull%7D%7D%5D%7D%2C%22maxSize%22%3A%22%22%7D&r63=23135576&r2545=solntsev%40innokentiy.ru) | `'uc[rule_string]'`: `{"type":"andrule","inverted":0,"params":{"mode":"or","children":[{"type":"idsrule","inverted":0,"params":{"value":"23135576","valueMode":null}},{"type":"user_email_like","inverted":0,"params":{"value":"solntsev@innokentiy.ru","valueMode":null}}]},"maxSize":""}` |

  - Для удобства работы наиболее популярные фильтры уже собраны в пресеты
    - gc_andrule(mode, children, inverted=0) - Фильтр И/ИЛИ
      * mode - ("and", "or")
      * children - список дочерних фильтров
    - gc_user_typerule(types, inverted=0)- Фильтр Пользователь/Тип
      * types - список допустимых типов ("user","teacher","admin")
    - gc_user_has_visit(linkedRule, inverted=0, checker="nlt", numval="")- Фильтр Пользователь/Имеет посещение
      * linkedRule - как правило, gc_andrule со вложенными субфильтрами (event_ref, event_loc, event_created_at и т.д.)
      * checker/numval - правило "не менее/больше/равно и т.д.", необязательны
      - gc_user_has_visit_event_created_at(dateStart, dateEnd, inverted=0) - Субфильтр Пользователь/Имеет посещение/Дата события
        * dateStart/dateEnd - даты начала/конца периода, в течение которого должно произойти событие

