import requests
import re
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
from typing import List, Dict, Union, Tuple, Any
import click
import urllib.parse
from bs4 import BeautifulSoup


class GetCourse:
    """
    Центральный объект, через который ведется взаимодействие с GC
    """

    def __init__(self, cookie=None, username=None, password=None, url="https://school.careerum.ru", verbose=False):
        """
        Инициализация объекта GetCourse
        * username/password - Логин и пароль к GetCourse
        * url - ссылка на тенант Getcourse, по умолчанию - "https://school.careerum.ru"
        * cookie - кука PHPSESSID_SUB, взятая из браузера
        Обязательно указывать либо логин/пароль, либо куку. Если указано и то и другое, используется только кука.
        """
        self._session = requests.Session()
        self._url = url
        if cookie:
            self._session.cookies = requests.cookies.RequestsCookieJar()
            self._session.cookies.set("PHPSESSID_SUB", cookie)
            r = self._session.get(self._url+'/user/my/profile')
            userinfo = BeautifulSoup(
                r.text, 'html5lib').find('div', class_='row')
            if userinfo:
                self._username = userinfo.get_text().strip().split()[1]
            else:
                raise Exception(
                    "Ошибка инициализации: неверная кука.")
        elif not username or not password:
            raise Exception(
                "Ошибка инициализации: не указана ни кука, ни пара логин-пароль")
        else:
            r = self._session.post(
                self._url+'/cms/system/login?required=true',
                data=urllib.parse.urlencode({
                    'action': 'processXdget',
                    'xdgetId': '99945_1_1_1_1_1_1_1_1',
                    'params[action]': 'login',
                    'params[email]': username,
                    'params[password]': password,
                }),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            try:
                self._username = json.loads(r.text)["email"]
            except (ValueError, KeyError) as e:
                raise Exception(
                    "Ошибка инициализации: неверная комбинация логина и пароля")

    def __repr__(self):
        return f'GetCourse(username="{self._username}", cookie="{self._session.cookies["PHPSESSID_SUB"]}")'

    def MissionTasks(self, processId, page=1, bar=None) -> List[int]:
        """
        Метод возвращает список задач в указанном процесса
        * processId - ID процесса
        """
        url = f'{self._url}/pl/tasks/mission/tasks?id={processId}&page={page}'
        r = self._session.get(url)
        response = BeautifulSoup(r.text, 'html5lib')
        summary = re.search(
            r'Показано (\d+)-(\d+) из (\d+)  всего',
            response.find('div', class_='summary').text.replace('\xa0', '')
        )
        if not summary:
            raise Exception(
                f"Absent summary block in MissionTasks output for {url}")
        _, rec_end, rec_total = map(lambda x: int(
            x.replace(" ", "")), summary.groups())
        if not bar:
            bar = click.progressbar(
                length=rec_total, label='Getting MissionTasks', show_pos=True)
            bar.__enter__()
        found = re.findall(
            r"""<tr data-key=\"(\d+)\"><td data-col-seq=\"0\"><a href=\"/pl/tasks/task/view\?id=\1\">\1</a></td><td [^<]*? data-col-seq=\"1\">.*?<a .*? data-user-id=\\?'(\d+)\\?' .*? href=\\?'/user/control/user/update/id/\2\\?'[^>]*><span[^>]*>.*?(.+?)</span>.*?</td><td .*? data-col-seq=\"2\"><a href=\".*/(\w+)/update/id/(\d+)\">.*</a></td><td data-col-seq=\"3\">.*?</td><td data-col-seq=\"4\">.*?</td><td data-col-seq=\"5\"><span[^>]*>(.*?)</div></td><td data-col-seq=\"6\">.*?</td></tr>""", r.text)
        result = list(map(lambda x: {"id": x[0], "client": (
            x[1], x[2]), "subject": (x[3], x[4]), "status": x[5]}, found))
        bar.update(len(result))
        if rec_end < rec_total:
            # Ответ неполный, дозапрашиваем оставшиеся страницы
            result += self.MissionTasks(processId, page+1, bar)
        else:
            bar.__exit__(None, None, None)
        return result

    def Users(self, filter: Dict, page=1) -> List[int]:
        """
        Метод возвращает список ID пользователей по указанному фильтру
        * filter - словарь в формате uc[rule_string] запроса https://school.dreamcatchme.ru/pl/user/user/index?uc[rule_string]={...}
        """
        if type(filter) != dict:
            raise Exception("Filter must be a dict")
        url = f'{self._url}/pl/user/user/index?uc[rule_string]={json.dumps(filter)}&page={page}'
        r = self._session.get(url, cookies=self._cookies)
        summary = re.search(
            r"<div class=\"summary\">Показано ([0-9 ]+)-([0-9 ]+) из ([0-9 ]+)  всего.\s+</div>", r.text)
        if not summary:
            raise Exception(f"Absent summary block in Users output for {url}")
        _, rec_end, rec_total = map(lambda x: int(
            x.replace(" ", "")), summary.groups())
        result = list(
            map(int, re.findall(r'<tr class="gc-user-link" data-user-id="(\d+)"', r.text)))
        if rec_end < rec_total:
            # Ответ неполный, дозапрашиваем оставшиеся страницы
            result += self.Users(filter, page+1)
        return result

    IntStr = Union[int, str, None]
    StreamType = Tuple[IntStr, str]
    # StreamDict = Dict[StreamType,StreamDict] -- mypy doesn't support recursive typing
    StreamDict = Dict[StreamType, Any]

    def Streams(self, stream: IntStr = None, recursive: bool = True) -> Union[List[StreamType], StreamDict]:
        """
        Метод возвращает содержимое указанного курса (stream)
        * stream - ID родительского stream, по умолчанию None (т.е. глобальный поиск)
        * recursive - указывает, что возвращать
            - True: курсы, являющиеся рекурсивно вложенными в указанный stream (по умолчанию), в формате словаря
                - Ключ: кортеж из ID курса и его имени
                - Значение: словарь со вложенными в него курсами в том же формате
            - False: список кортежей из ID курсов и их названий, являющиеся вложенными в указанный stream
        """
        url = f'{self._url}/teach/control/stream'
        if stream:
            url += f'/view/id/{stream}'
        r = self._session.get(url, cookies=self._cookies)
        try:
            title = re.search(r"<h1>(.*)</h1>", r.text).group(1)
        except:
            title = None
        found_streams = set(re.findall(
            r"<a href='/teach/control/stream/view/id/(\d*)'>\s*<span class=\"stream-title\">(.*?)</span>", r.text))
        if recursive:
            return {(stream, title): [self.Streams(s[0]) for s in found_streams]}
        else:
            return found_streams

    def Lessons(self, stream=None) -> List[IntStr]:
        """
        Метод возвращает список ID уроков указанного курса (stream)
        * stream - ID родительского stream, по умолчанию None (т.е. возвращаются вообще все уроки всех курсов)
        """
        url = f'{self._url}/teach/control/stream'
        if stream:
            url += f'/view/id/{stream}'
        r = self._session.get(url, cookies=self._cookies)
        lessons = []
        found_streams = re.findall(
            r"<a href='/teach/control/stream/view/id/(\d*)'>\s*<span class=\"stream-title\">(.*?)</span>", r.text)
        found_lessons = re.findall(
            r"<div class=\"link title\" href=\"/teach/control/lesson/view/id/(\d+)\">(.*?)</div>", r.text)
        processed_streams = set()
        for s in found_streams:
            if not s[0] in processed_streams:
                lessons += self.Lessons(s[0])
                processed_streams.add(s[0])
        for l in found_lessons:
            if not l in lessons:
                lessons.append(l)
        return lessons

    def Lesson(self, lesson):
        """
        Метод возвращает информацию об уроке
        * lesson - ID урока

        Возвращается кортеж из:
        * Названия урока
        * Списка URL с embed'ами
        """
        url = f'{self._url}/pl/teach/control/lesson/view?id={lesson}'
        r = self._session.get(url, cookies=self._cookies)
        try:
            title = re.search(r"<h1>(.*)</h1>", r.text).group(1)
        except:
            title = None
        embeds = re.findall(
            r"<iframe .*? src=['\"](.*?)['\"].*?></iframe>", r.text)
        return title, embeds

    def userProduct(self, userProduct):
        """
        Метод возвращает информацию о покупке
        * userProduct - ID покупки
        Возвращается кортеж из:
        * Названия покупки
        * Состояния (Активен, Завершен, Не активен, )
        """
        url = f'{self._url}/sales/control/userProduct/update/id/{userProduct}'
        r = self._session.get(url, cookies=self._cookies)
        try:
            title = re.search(r"<h1>(.*)</h1>", r.text).group(1)
        except:
            title = None
        status = re.search(
            r"<tr>\s*<td class=\"key\">\s*Статус\s*</td>\s*<td>\s*<span[^>]+>\s*(Активен)\s*</span>\s*</td>\s*</tr>", r.text).group(1)
        prolong = re.search(
            r'<label\s*>\s*<input [^>]*type=\"checkbox\" name=\"auto_prolongate_enabled\"\s*(checked)?>\s*Продлевать автоматически\s*</label>', r.text).group(1) == "checked"
        return {"title": title, "status": status, "prolong": prolong}

    def missionTask(self, taskId):
        """
        Метод возвращает информацию о задаче
        * taskId - ID задачи
        """
        url = f'{self._url}/pl/tasks/task/task-scripts?id={taskId}'
        r = self._session.get(url)
        reply = json.loads(r.text)
        html = BeautifulSoup(reply["data"]["html"], 'html5lib')
        steps = html.find_all('tr', class_="task-script-row")
        # matches = list(re.finditer(
        #     #            r'<tr class=\"task-script-row \" data-id=\"(\d+)\">',
        #     r'<tr class=\"task-script-row \" data-id=\"(\d+)\">\s*<td class=\"small\" width=\"30\">(\d+)</td>\s*<td class=\"small\" width=\"50\">([^<]*)</td>\s*<td class=\"small\" width=\"50\">([^<]*)</td>\s*<td class=\"small\"\s*>\s*(.*?)\t{5}\s*([^<]*?)\s*\(idS: (\d+)\)\s*</td>\s*<td width=\"200\">\s*<span\s+class=\"small\"\s*>\s*([^<]*?)\s*</span>\s*(?:<span\s+class=\"small\" >)?\s*(?:<span class=\"text-muted\" style=\"margin-left: 5px;\">)?\s*(.*?)(?:</span>\s*)*</td>\s*<td class=\"small\" width=\"100\">\s*(.*?)\s*</td>\s*</tr>',
        #     reply["data"]["html"],
        #     flags=re.DOTALL))

        cal = {"Янв": 1, "Фев": 2, "Мар": 3, "Апр": 4, "Май": 5, "Июн": 6,
               "Июл": 7, "Авг": 8, "Сен": 9, "Окт": 10, "Ноя": 11, "Дек": 12}
        result = []
        #steps = [match.groups() for match in matches]
        for step in steps:
            tds = step.find_all('td')
            """
            try:
                t1=datetime(int(step[2][10:14]),cal[step[2][6:9]],int(step[2][3:5]))
            except:
                t1=datetime(datetime.now().year,cal[step[2][6:9]],int(step[2][3:5]),int(step[2][10:12]),int(step[2][13:15]))
            try:
                t2=datetime(int(step[3][10:14]),cal[step[3][6:9]],int(step[3][3:5]))
            except:
                t2=datetime(datetime.now().year,cal[step[3][6:9]],int(step[3][3:5]),int(step[3][10:12]),int(step[3][13:15]))
            # бывают также "только что", "2 минуты назад", "сегодня ХХ:ХХ" и бог весть что еще
            """
            stepdata = tds[3].text.strip().split('\n')
            result_element=tds[4].find('span', class_="text-muted")
            result.append({
                "stepId": int(step['data-id']),
                "order": int(tds[0].text),  # №
                # "startTime":t1, # Поставлено
                # "finishTime":t2, # Выполнено
                # Название/Действие
                "stepAction": stepdata[0].split('\t\t\t\t\t')[0],
                # Название/Текст
                "stepTitle":  stepdata[0].split('\t\t\t\t\t')[1],
                # Название/ID
                "stepTemplateId": int(stepdata[1].strip()[6:-1]),
                "resultSummary": tds[4].span.text.strip(),  # Результат/Итог
                "resultData": " ".join(result_element.text.split()) if result_element else None,  # Результат/Вывод
                "who": tds[5].text.strip(),  # Кто
                "subprocess": tds[6].text.strip(),  # Подпроцесс
            })
        return sorted(result, key=lambda x: x["order"])

# Удобный сервис для парсинга URL: https://www.freeformatter.com/url-parser-query-string-splitter.html


def gc_user_has_visit_event_created_at(dateStart, dateEnd, inverted=0):
    """
    Субфильтр Пользователь/Имеет посещение/Дата события
    """
    return {
        "type": "event_created_at",
        "inverted": inverted,
        "params": {
            "value": {
                "from": dateStart,
                "to": dateEnd
            },
            "valueMode": None
        }
    }


def gc_user_has_visit(linkedRule, inverted=0, checker="nlt", numval=""):
    """
    Фильтр Пользователь/Имеет посещение
    * linkedRule - как правило, andRule с субфильтрами
    """
    return {
        "type": "user_has_visit",
        "inverted": inverted,
        "params": {
            "linkedRule": linkedRule,
            "countCondition": {"checker": checker, "numval": numval}
        }
    }


def gc_andrule(mode, children, inverted=0):
    """
    Фильтр И/ИЛИ
    * mode - ("and", "or")
    * children - список дочерних фильтров
    """
    return {
        "type": "andrule",
        "inverted": inverted,
        "params": {
            "mode": mode,
            "children": children
        }
    }


def gc_user_typerule(types, inverted=0):
    """
    Фильтр Пользователь/Тип
    * types - список допустимых типов ("user","teacher","admin")
    """
    return {
        "type": "user_typerule",
        "inverted": inverted,
        "params": {
            "value": {"selected_id": types},
            "valueMode": None
        }
    }
