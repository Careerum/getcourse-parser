# getcourse-parser
Позволяет парсить HTML-вывод геткурса.

API:
- Инициализация
  - Метод инициализация центрального объекта GetCourse происходит любым из двух способов: через куку либо через пару логин-пароль (обязательно указывать либо логин/пароль, либо куку. Если указано и то и другое, используется только кука).
    * username/password - Логин и пароль к GetCourse
    * url - ссылка на тенант Getcourse, по умолчанию - "https://school.careerum.ru"
    * cookie - кука PHPSESSID_SUB, взятая из браузера

    - Через куку (урл необязателен, но кука должна быть на то же имя сервера)
    ```
    from getcourse import *
    gc = GetCourse(url="https://school.careerum.ru", cookie="07f3d96b13b8b33112345638d39ea485")
    ```
    - Через пару логин-пароль
    ```
    from getcourse import *
    gc = GetCourse(url="https://school.careerum.ru", username='is@careerum.com', password='S3cr37')
    ```     
