from getcourse import *
import datetime

gc = GetCourse()

ConsultingVideos = [
    ['66844116', '169425744', '169425746', '169425749', '169425752',
        '146470753', '169427055', '169427056', '169427057', '169427058'],
    ['68381428', '169426032', '169426066', '169426067', '169426068',
        '146470754', '169427063', '169427064', '169427065', '169427066'],
    ['68995081', '169426665', '169426666', '169426667', '169426669',
        '146470755', '169427069', '169427070', '169427071', '169427072'],
    ['71822973', '169426804', '169426816',
        '146470760', '169427084', '169427085'],
]
DreamTeamVideos = [
    ['146546429', '107503606', '172340101', '172340103', '172340105',
        '172340107', '172346813', '172346814', '172346815', '172346816'],
    ['146546440', '110983412', '172340570', '172340575', '172340577',
        '172340579', '172346825', '172346826', '172346827', '172346828'],
    ['146546445', '113274079', '172346041', '172346043',
        '172346045', '172346829', '172346830', '172346831'],
    ['146546454', '117184652', '172346112', '172346117',
        '172346118', '172346834', '172346835', '172346836'],
]



def gc_filter_new(videoIdsList, dateStart, dateEnd):
    return gc_andrule("and", [
        gc_user_has_visit(
            gc_andrule(
                "and",
                [
                    gc_andrule("or", [{"type": "event_loc", "params": {
                        "value": video}} for video in videoIdsList]),
                    gc_user_has_visit_event_created_at(
                        dateStart,
                        dateEnd
                    )
                ]
            )
        ),
        gc_user_typerule(["user"])
    ])

# totals1={}
# totals2={}
i=0

today = datetime.date.today()
first = today.replace(day=1)
lastMonth = first - datetime.timedelta(days=1)

# month=10
month=int(lastMonth.strftime("%m"))

startDate = datetime.datetime(2022, month, 1).strftime("%d.%m.%Y")
endDate = (datetime.datetime(2022, month, 1) + relativedelta(months=+
                                                    1) + relativedelta(days=-1)).strftime("%d.%m.%Y")
print(f"{startDate} - {endDate}")
users1_total = 0
users1_total_str=[]
for video in ConsultingVideos:
    i+=1
    Users = gc.Users(gc_filter_new(video, startDate, endDate))
    print(f"{i} видео - {len(Users)}")
    users1_total += len(Users)
    users1_total_str.append(str(len(Users)))
print(f"({'+'.join(users1_total_str)})={users1_total}")
print(f"{users1_total}×500₽={users1_total*500}₽")
print("")
users2_total = 0
users2_total_str = []
i=0
for video in DreamTeamVideos:
    i+=1
    Users = gc.Users(gc_filter_new(video, startDate, endDate))
    print(f"{i} видео - {len(Users)}")
    users2_total += len(Users)
    users2_total_str.append(str(len(Users)))
print(f"({'+'.join(users2_total_str)})={users2_total}")
print(f"{users2_total}×230₽={users2_total*230}₽")
