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
      print(gc.MissionTasks(processId=12345))
      ```
      Пример вывода:
      ```python
      [
        {'id': '2216872626', 'client': ('64348545', 'Наталия Маньковская'), 'subject': ('user', '64348545'), 'status': 'Отложена'},
        {'id': '2217509003', 'client': ('45953922', 'Мария Хабахпашева'), 'subject': ('user', '45953922'), 'status': 'Отложена'}
      ]
      ```
    - Метод missionTask возвращает информацию о конкретной задаче
      * taskId - ID задачи
      ```python
      print(gc.MissionTask(taskId=12345))
      ```
      Пример вывода:
      ```javascript
      [{'order': 1, 'resultData': None, 'resultSummary': 'Выполнено', 'stepAction': 'Начало скрипта', 'stepId': 85102200676, 'stepTemplateId': 14646448, 'stepTitle': '"Начало работы"', 'subprocess': '', 'who': ''},
      {'order': 2, 'resultData': None, 'resultSummary': '', 'stepAction': 'Завершение процесса', 'stepId': 85102274162, 'stepTemplateId': 7993476, 'stepTitle': '"Завершение процесса"', 'subprocess': '522600', 'who': ''}]
      ```
