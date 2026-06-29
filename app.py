import streamlit as st
import json
import os
import pandas as pd
from html import escape
from datetime import datetime, timedelta, timezone

# --- CONFIGURACIÓN DE DATOS ---
DATA_FILE = "quiniela_2026_auto.json"
APP_SCHEMA_VERSION = 3
ADMIN_PASSWORD = "EcCampeon26"
PREDICTION_LOCK_DEADLINE = datetime(2026, 6, 10, 12, 0, tzinfo=timezone(timedelta(hours=1), "CET"))
OFFICIAL_BRACKET_LOCK_DEADLINE = datetime(2026, 6, 28, 20, 0, tzinfo=timezone(timedelta(hours=1), "CET"))

GRUPOS_EQUIPOS = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "Chequia"],
    "Grupo B": ["Canadá", "Bosnia y Herzegovina", "Catar", "Suiza"],
    "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "Grupo D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "Grupo E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "Grupo F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "Grupo G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "Grupo H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "Grupo I": ["Francia", "Senegal", "Irak", "Noruega"],
    "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "Grupo K": ["Portugal", "RD Congo", "Uzbekistán", "Colombia"],
    "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
}

PARTIDOS_GRUPOS = {
    "Grupo A": [("México", "Sudáfrica"), ("Corea del Sur", "Chequia"), ("Chequia", "Sudáfrica"), ("México", "Corea del Sur"), ("Chequia", "México"), ("Sudáfrica", "Corea del Sur")],
    "Grupo B": [("Canadá", "Bosnia y Herzegovina"), ("Catar", "Suiza"), ("Suiza", "Bosnia y Herzegovina"), ("Canadá", "Catar"), ("Suiza", "Canadá"), ("Bosnia y Herzegovina", "Catar")],
    "Grupo C": [("Brasil", "Marruecos"), ("Haití", "Escocia"), ("Escocia", "Marruecos"), ("Brasil", "Haití"), ("Escocia", "Brasil"), ("Marruecos", "Haití")],
    "Grupo D": [("Estados Unidos", "Paraguay"), ("Australia", "Turquía"), ("Turquía", "Paraguay"), ("Estados Unidos", "Australia"), ("Turquía", "Estados Unidos"), ("Paraguay", "Australia")],
    "Grupo E": [("Alemania", "Curazao"), ("Costa de Marfil", "Ecuador"), ("Ecuador", "Curazao"), ("Alemania", "Costa de Marfil"), ("Ecuador", "Alemania"), ("Curazao", "Costa de Marfil")],
    "Grupo F": [("Países Bajos", "Japón"), ("Suecia", "Túnez"), ("Túnez", "Japón"), ("Países Bajos", "Suecia"), ("Túnez", "Países Bajos"), ("Japón", "Suecia")],
    "Grupo G": [("Bélgica", "Egipto"), ("Irán", "Nueva Zelanda"), ("Nueva Zelanda", "Egipto"), ("Bélgica", "Irán"), ("Nueva Zelanda", "Bélgica"), ("Egipto", "Irán")],
    "Grupo H": [("España", "Cabo Verde"), ("Arabia Saudita", "Uruguay"), ("Uruguay", "Cabo Verde"), ("España", "Arabia Saudita"), ("Uruguay", "España"), ("Cabo Verde", "Arabia Saudita")],
    "Grupo I": [("Francia", "Senegal"), ("Irak", "Noruega"), ("Noruega", "Senegal"), ("Francia", "Irak"), ("Noruega", "Francia"), ("Senegal", "Irak")],
    "Grupo J": [("Argentina", "Argelia"), ("Austria", "Jordania"), ("Jordania", "Argelia"), ("Argentina", "Austria"), ("Argelia", "Austria"), ("Jordania", "Argentina")],
    "Grupo K": [("Portugal", "RD Congo"), ("Uzbekistán", "Colombia"), ("Colombia", "RD Congo"), ("Portugal", "Uzbekistán"), ("Colombia", "Portugal"), ("RD Congo", "Uzbekistán")],
    "Grupo L": [("Inglaterra", "Croacia"), ("Ghana", "Panamá"), ("Panamá", "Croacia"), ("Inglaterra", "Ghana"), ("Panamá", "Inglaterra"), ("Croacia", "Ghana")]
}

TEAM_FLAGS = {
    "México": "🇲🇽",
    "Sudáfrica": "🇿🇦",
    "Corea del Sur": "🇰🇷",
    "Chequia": "🇨🇿",
    "Canadá": "🇨🇦",
    "Bosnia y Herzegovina": "🇧🇦",
    "Catar": "🇶🇦",
    "Suiza": "🇨🇭",
    "Brasil": "🇧🇷",
    "Marruecos": "🇲🇦",
    "Haití": "🇭🇹",
    "Escocia": "🏴",
    "Estados Unidos": "🇺🇸",
    "Paraguay": "🇵🇾",
    "Australia": "🇦🇺",
    "Turquía": "🇹🇷",
    "Alemania": "🇩🇪",
    "Curazao": "🇨🇼",
    "Costa de Marfil": "🇨🇮",
    "Ecuador": "🇪🇨",
    "Países Bajos": "🇳🇱",
    "Japón": "🇯🇵",
    "Suecia": "🇸🇪",
    "Túnez": "🇹🇳",
    "Bélgica": "🇧🇪",
    "Egipto": "🇪🇬",
    "Irán": "🇮🇷",
    "Nueva Zelanda": "🇳🇿",
    "España": "🇪🇸",
    "Cabo Verde": "🇨🇻",
    "Arabia Saudita": "🇸🇦",
    "Uruguay": "🇺🇾",
    "Francia": "🇫🇷",
    "Senegal": "🇸🇳",
    "Irak": "🇮🇶",
    "Noruega": "🇳🇴",
    "Argentina": "🇦🇷",
    "Argelia": "🇩🇿",
    "Austria": "🇦🇹",
    "Jordania": "🇯🇴",
    "Portugal": "🇵🇹",
    "RD Congo": "🇨🇩",
    "Uzbekistán": "🇺🇿",
    "Colombia": "🇨🇴",
    "Inglaterra": "🏴",
    "Croacia": "🇭🇷",
    "Ghana": "🇬🇭",
    "Panamá": "🇵🇦",
}

FIFA_RANKING_LAST_UPDATE = "2026-06-11"
FIFA_RANKING_BY_TEAM = {
    "México": 14,
    "Sudáfrica": 60,
    "Corea del Sur": 25,
    "Chequia": 40,
    "Canadá": 30,
    "Bosnia y Herzegovina": 64,
    "Catar": 56,
    "Suiza": 19,
    "Brasil": 6,
    "Marruecos": 7,
    "Haití": 83,
    "Escocia": 42,
    "Estados Unidos": 17,
    "Paraguay": 41,
    "Australia": 27,
    "Turquía": 22,
    "Alemania": 10,
    "Curazao": 82,
    "Costa de Marfil": 33,
    "Ecuador": 23,
    "Países Bajos": 8,
    "Japón": 18,
    "Suecia": 38,
    "Túnez": 45,
    "Bélgica": 9,
    "Egipto": 29,
    "Irán": 20,
    "Nueva Zelanda": 85,
    "España": 2,
    "Cabo Verde": 67,
    "Arabia Saudita": 61,
    "Uruguay": 16,
    "Francia": 3,
    "Senegal": 15,
    "Irak": 57,
    "Noruega": 31,
    "Argentina": 1,
    "Argelia": 28,
    "Austria": 24,
    "Jordania": 63,
    "Portugal": 5,
    "RD Congo": 46,
    "Uzbekistán": 50,
    "Colombia": 13,
    "Inglaterra": 4,
    "Croacia": 11,
    "Ghana": 73,
    "Panamá": 34,
}
YELLOW_CARD_CONDUCT_POINTS = -1
RED_CARD_CONDUCT_POINTS = -4

ANNEX_C_THIRD_COLUMNS = ["1A", "1B", "1D", "1E", "1G", "1I", "1K", "1L"]
ANNEX_C_ROWS = """
1:EJIFHGLK
2:HGIDJFLK
3:EJIDHGLK
4:EJIDHFLK
5:EGIDJFLK
6:EGJDHFLK
7:EGIDHFLK
8:EGJDHFLI
9:EGJDHFIK
10:HGICJFLK
11:EJICHGLK
12:EJICHFLK
13:EGICJFLK
14:EGJCHFLK
15:EGICHFLK
16:EGJCHFLI
17:EGJCHFIK
18:HGICJDLK
19:CJIDHFLK
20:CGIDJFLK
21:CGJDHFLK
22:CGIDHFLK
23:CGJDHFLI
24:CGJDHFIK
25:EJICHDLK
26:EGICJDLK
27:EGJCHDLK
28:EGICHDLK
29:EGJCHDLI
30:EGJCHDIK
31:CJEDIFLK
32:CJEDHFLK
33:CEIDHFLK
34:CJEDHFLI
35:CJEDHFIK
36:CGEDJFLK
37:CGEDIFLK
38:CGEDJFLI
39:CGEDJFIK
40:CGEDHFLK
41:CGJDHFLE
42:CGJDHFEK
43:CGEDHFLI
44:CGEDHFIK
45:CGJDHFEI
46:HJBFIGLK
47:EJIBHGLK
48:EJBFIHLK
49:EJBFIGLK
50:EJBFHGLK
51:EGBFIHLK
52:EJBFHGLI
53:EJBFHGIK
54:HJBDIGLK
55:HJBDIFLK
56:IGBDJFLK
57:HGBDJFLK
58:HGBDIFLK
59:HGBDJFLI
60:HGBDJFIK
61:EJBDIHLK
62:EJBDIGLK
63:EJBDHGLK
64:EGBDIHLK
65:EJBDHGLI
66:EJBDHGIK
67:EJBDIFLK
68:EJBDHFLK
69:EIBDHFLK
70:EJBDHFLI
71:EJBDHFIK
72:EGBDJFLK
73:EGBDIFLK
74:EGBDJFLI
75:EGBDJFIK
76:EGBDHFLK
77:HGBDJFLE
78:HGBDJFEK
79:EGBDHFLI
80:EGBDHFIK
81:HGBDJFEI
82:HJBCIGLK
83:HJBCIFLK
84:IGBCJFLK
85:HGBCJFLK
86:HGBCIFLK
87:HGBCJFLI
88:HGBCJFIK
89:EJBCIHLK
90:EJBCIGLK
91:EJBCHGLK
92:EGBCIHLK
93:EJBCHGLI
94:EJBCHGIK
95:EJBCIFLK
96:EJBCHFLK
97:EIBCHFLK
98:EJBCHFLI
99:EJBCHFIK
100:EGBCJFLK
101:EGBCIFLK
102:EGBCJFLI
103:EGBCJFIK
104:EGBCHFLK
105:HGBCJFLE
106:HGBCJFEK
107:EGBCHFLI
108:EGBCHFIK
109:HGBCJFEI
110:HJBCIDLK
111:IGBCJDLK
112:HGBCJDLK
113:HGBCIDLK
114:HGBCJDLI
115:HGBCJDIK
116:CJBDIFLK
117:CJBDHFLK
118:CIBDHFLK
119:CJBDHFLI
120:CJBDHFIK
121:CGBDJFLK
122:CGBDIFLK
123:CGBDJFLI
124:CGBDJFIK
125:CGBDHFLK
126:CGBDHFLJ
127:HGBCJFDK
128:CGBDHFLI
129:CGBDHFIK
130:HGBCJFDI
131:EJBCIDLK
132:EJBCHDLK
133:EIBCHDLK
134:EJBCHDLI
135:EJBCHDIK
136:EGBCJDLK
137:EGBCIDLK
138:EGBCJDLI
139:EGBCJDIK
140:EGBCHDLK
141:HGBCJDLE
142:HGBCJDEK
143:EGBCHDLI
144:EGBCHDIK
145:HGBCJDEI
146:CJBDEFLK
147:CEBDIFLK
148:CJBDEFLI
149:CJBDEFIK
150:CEBDHFLK
151:CJBDHFLE
152:CJBDHFEK
153:CEBDHFLI
154:CEBDHFIK
155:CJBDHFEI
156:CGBDEFLK
157:CGBDJFLE
158:CGBDJFEK
159:CGBDEFLI
160:CGBDEFIK
161:CGBDJFEI
162:CGBDHFLE
163:CGBDHFEK
164:HGBCJFDE
165:CGBDHFEI
166:HJIFAGLK
167:EJIAHGLK
168:EJIFAHLK
169:EJIFAGLK
170:EGJFAHLK
171:EGIFAHLK
172:EGJFAHLI
173:EGJFAHIK
174:HJIDAGLK
175:HJIDAFLK
176:IGJDAFLK
177:HGJDAFLK
178:HGIDAFLK
179:HGJDAFLI
180:HGJDAFIK
181:EJIDAHLK
182:EJIDAGLK
183:EGJDAHLK
184:EGIDAHLK
185:EGJDAHLI
186:EGJDAHIK
187:EJIDAFLK
188:HJEDAFLK
189:HEIDAFLK
190:HJEDAFLI
191:HJEDAFIK
192:EGJDAFLK
193:EGIDAFLK
194:EGJDAFLI
195:EGJDAFIK
196:HGEDAFLK
197:HGJDAFLE
198:HGJDAFEK
199:HGEDAFLI
200:HGEDAFIK
201:HGJDAFEI
202:HJICAGLK
203:HJICAFLK
204:IGJCAFLK
205:HGJCAFLK
206:HGICAFLK
207:HGJCAFLI
208:HGJCAFIK
209:EJICAHLK
210:EJICAGLK
211:EGJCAHLK
212:EGICAHLK
213:EGJCAHLI
214:EGJCAHIK
215:EJICAFLK
216:HJECAFLK
217:HEICAFLK
218:HJECAFLI
219:HJECAFIK
220:EGJCAFLK
221:EGICAFLK
222:EGJCAFLI
223:EGJCAFIK
224:HGECAFLK
225:HGJCAFLE
226:HGJCAFEK
227:HGECAFLI
228:HGECAFIK
229:HGJCAFEI
230:HJICADLK
231:IGJCADLK
232:HGJCADLK
233:HGICADLK
234:HGJCADLI
235:HGJCADIK
236:CJIDAFLK
237:HJFCADLK
238:HFICADLK
239:HJFCADLI
240:HJFCADIK
241:CGJDAFLK
242:CGIDAFLK
243:CGJDAFLI
244:CGJDAFIK
245:HGFCADLK
246:CGJDAFLH
247:HGJCAFDK
248:HGFCADLI
249:HGFCADIK
250:HGJCAFDI
251:EJICADLK
252:HJECADLK
253:HEICADLK
254:HJECADLI
255:HJECADIK
256:EGJCADLK
257:EGICADLK
258:EGJCADLI
259:EGJCADIK
260:HGECADLK
261:HGJCADLE
262:HGJCADEK
263:HGECADLI
264:HGECADIK
265:HGJCADEI
266:CJEDAFLK
267:CEIDAFLK
268:CJEDAFLI
269:CJEDAFIK
270:HEFCADLK
271:HJFCADLE
272:HJECAFDK
273:HEFCADLI
274:HEFCADIK
275:HJECAFDI
276:CGEDAFLK
277:CGJDAFLE
278:CGJDAFEK
279:CGEDAFLI
280:CGEDAFIK
281:CGJDAFEI
282:HGFCADLE
283:HGECAFDK
284:HGJCAFDE
285:HGECAFDI
286:HJBAIGLK
287:HJBAIFLK
288:IJBFAGLK
289:HJBFAGLK
290:HGBAIFLK
291:HJBFAGLI
292:HJBFAGIK
293:EJBAIHLK
294:EJBAIGLK
295:EJBAHGLK
296:EGBAIHLK
297:EJBAHGLI
298:EJBAHGIK
299:EJBAIFLK
300:EJBFAHLK
301:EIBFAHLK
302:EJBFAHLI
303:EJBFAHIK
304:EJBFAGLK
305:EGBAIFLK
306:EJBFAGLI
307:EJBFAGIK
308:EGBFAHLK
309:HJBFAGLE
310:HJBFAGEK
311:EGBFAHLI
312:EGBFAHIK
313:HJBFAGEI
314:IJBDAHLK
315:IJBDAGLK
316:HJBDAGLK
317:IGBDAHLK
318:HJBDAGLI
319:HJBDAGIK
320:IJBDAFLK
321:HJBDAFLK
322:HIBDAFLK
323:HJBDAFLI
324:HJBDAFIK
325:FJBDAGLK
326:IGBDAFLK
327:FJBDAGLI
328:FJBDAGIK
329:HGBDAFLK
330:HGBDAFLJ
331:HGBDAFJK
332:HGBDAFLI
333:HGBDAFIK
334:HGBDAFIJ
335:EJBAIDLK
336:EJBDAHLK
337:EIBDAHLK
338:EJBDAHLI
339:EJBDAHIK
340:EJBDAGLK
341:EGBAIDLK
342:EJBDAGLI
343:EJBDAGIK
344:EGBDAHLK
345:HJBDAGLE
346:HJBDAGEK
347:EGBDAHLI
348:EGBDAHIK
349:HJBDAGEI
350:EJBDAFLK
351:EIBDAFLK
352:EJBDAFLI
353:EJBDAFIK
354:HEBDAFLK
355:HJBDAFLE
356:HJBDAFEK
357:HEBDAFLI
358:HEBDAFIK
359:HJBDAFEI
360:EGBDAFLK
361:EGBDAFLJ
362:EGBDAFJK
363:EGBDAFLI
364:EGBDAFIK
365:EGBDAFIJ
366:HGBDAFLE
367:HGBDAFEK
368:HGBDAFEJ
369:HGBDAFEI
370:IJBCAHLK
371:IJBCAGLK
372:HJBCAGLK
373:IGBCAHLK
374:HJBCAGLI
375:HJBCAGIK
376:IJBCAFLK
377:HJBCAFLK
378:HIBCAFLK
379:HJBCAFLI
380:HJBCAFIK
381:CJBFAGLK
382:IGBCAFLK
383:CJBFAGLI
384:CJBFAGIK
385:HGBCAFLK
386:HGBCAFLJ
387:HGBCAFJK
388:HGBCAFLI
389:HGBCAFIK
390:HGBCAFIJ
391:EJBAICLK
392:EJBCAHLK
393:EIBCAHLK
394:EJBCAHLI
395:EJBCAHIK
396:EJBCAGLK
397:EGBAICLK
398:EJBCAGLI
399:EJBCAGIK
400:EGBCAHLK
401:HJBCAGLE
402:HJBCAGEK
403:EGBCAHLI
404:EGBCAHIK
405:HJBCAGEI
406:EJBCAFLK
407:EIBCAFLK
408:EJBCAFLI
409:EJBCAFIK
410:HEBCAFLK
411:HJBCAFLE
412:HJBCAFEK
413:HEBCAFLI
414:HEBCAFIK
415:HJBCAFEI
416:EGBCAFLK
417:EGBCAFLJ
418:EGBCAFJK
419:EGBCAFLI
420:EGBCAFIK
421:EGBCAFIJ
422:HGBCAFLE
423:HGBCAFEK
424:HGBCAFEJ
425:HGBCAFEI
426:IJBCADLK
427:HJBCADLK
428:HIBCADLK
429:HJBCADLI
430:HJBCADIK
431:CJBDAGLK
432:IGBCADLK
433:CJBDAGLI
434:CJBDAGIK
435:HGBCADLK
436:HGBCADLJ
437:HGBCADJK
438:HGBCADLI
439:HGBCADIK
440:HGBCADIJ
441:CJBDAFLK
442:CIBDAFLK
443:CJBDAFLI
444:CJBDAFIK
445:HFBCADLK
446:CJBDAFLH
447:HJBCAFDK
448:HFBCADLI
449:HFBCADIK
450:HJBCAFDI
451:CGBDAFLK
452:CGBDAFLJ
453:CGBDAFJK
454:CGBDAFLI
455:CGBDAFIK
456:CGBDAFIJ
457:CGBDAFLH
458:HGBCAFDK
459:HGBCAFDJ
460:HGBCAFDI
461:EJBCADLK
462:EIBCADLK
463:EJBCADLI
464:EJBCADIK
465:HEBCADLK
466:HJBCADLE
467:HJBCADEK
468:HEBCADLI
469:HEBCADIK
470:HJBCADEI
471:EGBCADLK
472:EGBCADLJ
473:EGBCADJK
474:EGBCADLI
475:EGBCADIK
476:EGBCADIJ
477:HGBCADLE
478:HGBCADEK
479:HGBCADEJ
480:HGBCADEI
481:CEBDAFLK
482:CJBDAFLE
483:CJBDAFEK
484:CEBDAFLI
485:CEBDAFIK
486:CJBDAFEI
487:HFBCADLE
488:HEBCAFDK
489:HJBCAFDE
490:HEBCAFDI
491:CGBDAFLE
492:CGBDAFEK
493:CGBDAFEJ
494:CGBDAFEI
495:HGBCAFDE
"""

# --- PERSISTENCIA Y ESQUEMA ---
def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

def empty_user_predictions():
    return {"group_predictions": {}, "ko_predictions": {}, "official_bracket_predictions": {}}

def normalize_user_data(user_data):
    user_data.setdefault("group_predictions", {})
    user_data.setdefault("ko_predictions", {})
    user_data.setdefault("official_bracket_predictions", {})
    user_data.pop("advancement_predictions", None)
    return user_data

def reset_all_user_predictions(data):
    for user_name in list(data.get("users", {}).keys()):
        data["users"][user_name] = empty_user_predictions()

def normalize_participant_name(name):
    return " ".join(name.split()).casefold()

def find_duplicate_participant_groups(users):
    grouped_names = {}
    for user_name in users:
        normalized_name = normalize_participant_name(user_name)
        if not normalized_name:
            continue
        grouped_names.setdefault(normalized_name, []).append(user_name)
    return [sorted(names, key=str.casefold) for names in grouped_names.values() if len(names) > 1]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"schema_version": APP_SCHEMA_VERSION, "users": {}, "real_results": {"group_results": {}, "ko_results": {}}}

    data.setdefault("users", {})
    data.setdefault("real_results", {})
    data["real_results"].setdefault("group_results", {})
    data["real_results"].setdefault("ko_results", {})
    data["real_results"].setdefault("official_r32", {})

    stored_schema = data.get("schema_version", 1)
    if stored_schema < APP_SCHEMA_VERSION:
        reset_all_user_predictions(data)
        data["schema_version"] = APP_SCHEMA_VERSION
        save_data(data)
    else:
        data["schema_version"] = APP_SCHEMA_VERSION
        for user_data in data["users"].values():
            normalize_user_data(user_data)
    return data

def load_persisted_real_results():
    if not os.path.exists(DATA_FILE):
        return data.get("real_results", {})
    with open(DATA_FILE, "r") as f:
        persisted_data = json.load(f)
    persisted_real_results = persisted_data.get("real_results", {})
    persisted_real_results.setdefault("group_results", {})
    persisted_real_results.setdefault("ko_results", {})
    persisted_real_results.setdefault("official_r32", {})
    return persisted_real_results

def predictions_are_locked():
    return datetime.now(timezone.utc) >= PREDICTION_LOCK_DEADLINE.astimezone(timezone.utc)

def prediction_lock_message():
    return f"Las predicciones quedaron bloqueadas el {PREDICTION_LOCK_DEADLINE:%d/%m/%Y a las %H:%M} CET."

def official_bracket_predictions_are_locked():
    return datetime.now(timezone.utc) >= OFFICIAL_BRACKET_LOCK_DEADLINE.astimezone(timezone.utc)

def official_bracket_prediction_lock_message():
    return f"Las predicciones del bracket oficial quedaron bloqueadas el {OFFICIAL_BRACKET_LOCK_DEADLINE:%d/%m/%Y a las %H:%M} CET."

def build_annex_c_assignments():
    assignments = {}
    for raw_line in ANNEX_C_ROWS.strip().splitlines():
        option, groups = raw_line.split(":")
        key = "".join(sorted(groups))
        assignments[key] = {
            "option": int(option),
            "slots": dict(zip(ANNEX_C_THIRD_COLUMNS, groups))
        }
    return assignments

ANNEX_C_ASSIGNMENTS = build_annex_c_assignments()

def group_is_complete(resultados_dict, group_name):
    return all(f"{group_name}_{i}" in resultados_dict for i in range(len(PARTIDOS_GRUPOS[group_name])))

def split_by_equal_keys(items, key_fn):
    groups = []
    for item in items:
        key = key_fn(item)
        if groups and groups[-1][0] == key:
            groups[-1][1].append(item)
        else:
            groups.append((key, [item]))
    return groups

def h2h_stats(teams, group_name, resultados_dict):
    stats = {team: {"Pts": 0, "GF": 0, "GC": 0, "GD": 0} for team in teams}
    team_set = set(teams)
    for i, (loc, vis) in enumerate(PARTIDOS_GRUPOS[group_name]):
        if loc not in team_set or vis not in team_set:
            continue
        m_id = f"{group_name}_{i}"
        if m_id not in resultados_dict:
            continue

        l_score = resultados_dict[m_id]["l"]
        v_score = resultados_dict[m_id]["v"]
        stats[loc]["GF"] += l_score
        stats[loc]["GC"] += v_score
        stats[vis]["GF"] += v_score
        stats[vis]["GC"] += l_score
        if l_score > v_score:
            stats[loc]["Pts"] += 3
        elif l_score < v_score:
            stats[vis]["Pts"] += 3
        else:
            stats[loc]["Pts"] += 1
            stats[vis]["Pts"] += 1

    for team in teams:
        stats[team]["GD"] = stats[team]["GF"] - stats[team]["GC"]
    return stats

def card_conduct_score(yellow_cards, red_cards):
    return yellow_cards * YELLOW_CARD_CONDUCT_POINTS + red_cards * RED_CARD_CONDUCT_POINTS

def group_conduct_scores(group_name, resultados_dict):
    scores = {team: 0 for team in GRUPOS_EQUIPOS[group_name]}
    for i, (loc, vis) in enumerate(PARTIDOS_GRUPOS[group_name]):
        result = resultados_dict.get(f"{group_name}_{i}")
        if not result:
            continue

        scores[loc] += card_conduct_score(result.get("l_yellow", 0), result.get("l_red", 0))
        scores[vis] += card_conduct_score(result.get("v_yellow", 0), result.get("v_red", 0))
    return scores

def fifa_ranking_position(team):
    return FIFA_RANKING_BY_TEAM.get(team, 999)

def rank_equal_points_teams(
    teams,
    group_name,
    resultados_dict,
    overall_stats,
    team_order,
    use_fifa_tiebreakers=False,
    conduct_scores=None,
):
    if len(teams) <= 1:
        return teams

    h2h = h2h_stats(teams, group_name, resultados_dict)
    h2h_sorted = sorted(
        teams,
        key=lambda team: (h2h[team]["Pts"], h2h[team]["GD"], h2h[team]["GF"], -team_order[team]),
        reverse=True,
    )
    h2h_groups = split_by_equal_keys(
        h2h_sorted,
        lambda team: (h2h[team]["Pts"], h2h[team]["GD"], h2h[team]["GF"]),
    )

    if len(h2h_groups) > 1:
        ranked = []
        for _, tied_teams in h2h_groups:
            if len(tied_teams) == len(teams):
                break
            ranked.extend(rank_equal_points_teams(
                tied_teams,
                group_name,
                resultados_dict,
                overall_stats,
                team_order,
                use_fifa_tiebreakers=use_fifa_tiebreakers,
                conduct_scores=conduct_scores,
            ))
        if len(ranked) == len(teams):
            return ranked

    if use_fifa_tiebreakers:
        overall_key = lambda team: (
            overall_stats[team]["GD"],
            overall_stats[team]["GF"],
            (conduct_scores or {}).get(team, 0),
            -fifa_ranking_position(team),
            -team_order[team],
        )
    else:
        overall_key = lambda team: (overall_stats[team]["GD"], overall_stats[team]["GF"], -team_order[team])

    overall_sorted = sorted(teams, key=overall_key, reverse=True)
    return overall_sorted

def rank_group_table(group_name, equipos, resultados_dict, use_fifa_tiebreakers=False, conduct_scores=None):
    team_order = {team: idx for idx, team in enumerate(GRUPOS_EQUIPOS[group_name])}
    teams = GRUPOS_EQUIPOS[group_name]
    teams_by_points = sorted(teams, key=lambda team: (equipos[team]["Pts"], -team_order[team]), reverse=True)

    ranked = []
    for _, tied_teams in split_by_equal_keys(teams_by_points, lambda team: equipos[team]["Pts"]):
        ranked.extend(rank_equal_points_teams(
            tied_teams,
            group_name,
            resultados_dict,
            equipos,
            team_order,
            use_fifa_tiebreakers=use_fifa_tiebreakers,
            conduct_scores=conduct_scores,
        ))

    rows = []
    for team in ranked:
        row = {"Equipo": team, **equipos[team]}
        if use_fifa_tiebreakers:
            row["FairPlay"] = (conduct_scores or {}).get(team, 0)
            row["Ranking FIFA"] = fifa_ranking_position(team)
        rows.append(row)

    columns = ["Equipo", "Pts", "PJ", "GF", "GC", "GD"]
    if use_fifa_tiebreakers:
        columns.extend(["FairPlay", "Ranking FIFA"])
    return pd.DataFrame(rows, columns=columns)

# --- PROCESAMIENTO DE MATRICES ---
def get_all_group_tables(resultados_dict, use_fifa_tiebreakers=False):
    tables = {}
    thirds = []
    for g in GRUPOS_EQUIPOS.keys():
        completed = group_is_complete(resultados_dict, g)
        conduct_scores = group_conduct_scores(g, resultados_dict) if use_fifa_tiebreakers else None
        equipos = {e: {"Pts": 0, "PJ": 0, "GF": 0, "GC": 0, "GD": 0} for e in GRUPOS_EQUIPOS[g]}
        for i, (loc, vis) in enumerate(PARTIDOS_GRUPOS[g]):
            m_id = f"{g}_{i}"
            if m_id in resultados_dict:
                l_score = resultados_dict[m_id]["l"]
                v_score = resultados_dict[m_id]["v"]
                equipos[loc]["PJ"] += 1; equipos[vis]["PJ"] += 1
                equipos[loc]["GF"] += l_score; equipos[loc]["GC"] += v_score
                equipos[vis]["GF"] += v_score; equipos[vis]["GC"] += l_score
                if l_score > v_score: equipos[loc]["Pts"] += 3
                elif l_score < v_score: equipos[vis]["Pts"] += 3
                else: equipos[loc]["Pts"] += 1; equipos[vis]["Pts"] += 1
        for e in equipos: equipos[e]["GD"] = equipos[e]["GF"] - equipos[e]["GC"]
        df = rank_group_table(
            g,
            equipos,
            resultados_dict,
            use_fifa_tiebreakers=use_fifa_tiebreakers,
            conduct_scores=conduct_scores,
        ).reset_index(drop=True)
        tables[g] = df
        if len(df) >= 3:
            tercero = df.iloc[2].to_dict()
            tercero["Grupo"] = g
            tercero["Completo"] = completed
            thirds.append(tercero)
	            
    df_thirds = pd.DataFrame(thirds)
    if use_fifa_tiebreakers:
        df_thirds = df_thirds.sort_values(
            by=["Pts", "GD", "GF", "FairPlay", "Ranking FIFA"],
            ascending=[False, False, False, False, True],
            kind="mergesort",
        ).reset_index(drop=True)
    else:
        df_thirds = df_thirds.sort_values(by=["Pts", "GD", "GF"], ascending=False, kind="mergesort").reset_index(drop=True)
    if not df_thirds.empty:
        df_thirds["Qualified"] = False
        complete_third_indexes = df_thirds[df_thirds["Completo"]].head(8).index
        df_thirds.loc[complete_third_indexes, "Qualified"] = True
        df_thirds["Avanza"] = df_thirds.apply(
            lambda row: "✅ Sí" if row["Qualified"] else ("❌ No" if row["Completo"] else "Pendiente"),
            axis=1,
        )
        
    best_thirds_list = df_thirds[df_thirds["Qualified"]]["Equipo"].tolist() if not df_thirds.empty else []
    return tables, best_thirds_list, df_thirds

def get_winner(match_data, team_l, team_v):
    if not match_data: return "Por definir"
    l_score, v_score = match_data.get("l", 0), match_data.get("v", 0)
    if l_score > v_score: return team_l
    elif l_score < v_score: return team_v
    return team_l if match_data.get("avanza", "L") == "L" else team_v

def get_loser(match_data, team_l, team_v):
    if not match_data: return "Por definir"
    l_score, v_score = match_data.get("l", 0), match_data.get("v", 0)
    if l_score > v_score: return team_v
    elif l_score < v_score: return team_l
    return team_v if match_data.get("avanza", "L") == "L" else team_l

def get_all_teams():
    return [team for teams in GRUPOS_EQUIPOS.values() for team in teams]

R16_SLOTS = [(1, 4), (0, 2), (3, 5), (6, 7), (10, 11), (8, 9), (13, 15), (12, 14)]
QF_SLOTS = [(0, 1), (4, 5), (2, 3), (6, 7)]
SF_SLOTS = [(0, 1), (2, 3)]
R32_SLOT_PAIRS = [
    ("2A", "2B"),              # id 0 (M73)
    ("1E", "3rd_from_1E"),     # id 1 (M74)
    ("1F", "2C"),              # id 2 (M75)
    ("1C", "2F"),              # id 3 (M76)
    ("1I", "3rd_from_1I"),     # id 4 (M77)
    ("2E", "2I"),              # id 5 (M78)
    ("1A", "3rd_from_1A"),     # id 6 (M79)
    ("1L", "3rd_from_1L"),     # id 7 (M80)
    ("1D", "3rd_from_1D"),     # id 8 (M81)
    ("1G", "3rd_from_1G"),     # id 9 (M82)
    ("2K", "2L"),              # id 10 (M83)
    ("1H", "2J"),              # id 11 (M84)
    ("1B", "3rd_from_1B"),     # id 12 (M85)
    ("1J", "2H"),              # id 13 (M86)
    ("1K", "3rd_from_1K"),     # id 14 (M87)
    ("2D", "2G")               # id 15 (M88)
]
R32_MATCH_BY_SLOT = {
    slot: 73 + idx
    for idx, pair in enumerate(R32_SLOT_PAIRS)
    for slot in pair
    if slot.startswith("1") or slot.startswith("2")
}

def resolve_bracket_from_r32(r32, ko_data):
    # --- R16: OCTAVOS (M89 al M96) ---
    r16 = [{"id": i, "match_number": 89 + i, "L_team": get_winner(ko_data.get(f"R32_{l}"), r32[l]["L_team"], r32[l]["V_team"]), "V_team": get_winner(ko_data.get(f"R32_{v}"), r32[v]["L_team"], r32[v]["V_team"])} for i, (l, v) in enumerate(R16_SLOTS)]
    
    # --- QF: CUARTOS (M97 al M100) ---
    qf = [{"id": i, "match_number": 97 + i, "L_team": get_winner(ko_data.get(f"R16_{l}"), r16[l]["L_team"], r16[l]["V_team"]), "V_team": get_winner(ko_data.get(f"R16_{v}"), r16[v]["L_team"], r16[v]["V_team"])} for i, (l, v) in enumerate(QF_SLOTS)]
    
    # --- SF: SEMIFINALES (M101 y M102) ---
    sf = [{"id": i, "match_number": 101 + i, "L_team": get_winner(ko_data.get(f"QF_{l}"), qf[l]["L_team"], qf[l]["V_team"]), "V_team": get_winner(ko_data.get(f"QF_{v}"), qf[v]["L_team"], qf[v]["V_team"])} for i, (l, v) in enumerate(SF_SLOTS)]
    
    # --- TERCER PUESTO (M103) ---
    third = [{"id": 0, "match_number": 103, "L_team": get_loser(ko_data.get(f"SF_0"), sf[0]["L_team"], sf[0]["V_team"]), "V_team": get_loser(ko_data.get(f"SF_1"), sf[1]["L_team"], sf[1]["V_team"])}]
    
    # --- FINAL (M104) ---
    final = [{"id": 0, "match_number": 104, "L_team": get_winner(ko_data.get(f"SF_0"), sf[0]["L_team"], sf[0]["V_team"]), "V_team": get_winner(ko_data.get(f"SF_1"), sf[1]["L_team"], sf[1]["V_team"])}]
    
    campeon = get_winner(ko_data.get("Final_0"), final[0]["L_team"], final[0]["V_team"])
    
    return {"R32": r32, "R16": r16, "QF": qf, "SF": sf, "Third": third, "Final": final, "Campeon": campeon}

def build_official_r32(official_r32):
    r32 = []
    for i in range(16):
        m_id = f"R32_{i}"
        match = official_r32.get(m_id, {})
        r32.append({
            "id": i,
            "match_number": 73 + i,
            "L_team": match.get("L_team", f"Por definir (M{73 + i}A)"),
            "V_team": match.get("V_team", f"Por definir (M{73 + i}B)")
        })
    return r32

def official_bracket_is_ready(official_r32):
    teams = []
    for i in range(16):
        match = official_r32.get(f"R32_{i}", {})
        if "L_team" not in match or "V_team" not in match:
            return False
        teams.extend([match["L_team"], match["V_team"]])
    return len(teams) == 32 and len(set(teams)) == 32

def resolve_official_bracket(official_r32, ko_data):
    return resolve_bracket_from_r32(build_official_r32(official_r32), ko_data)

def resolve_real_bracket(real_obj):
    if official_bracket_is_ready(real_obj.get("official_r32", {})):
        return resolve_official_bracket(real_obj.get("official_r32", {}), real_obj.get("ko_results", {}))

    r_tables, _, df_r_thirds = get_all_group_tables(real_obj.get("group_results", {}), use_fifa_tiebreakers=True)
    return resolve_full_bracket(r_tables, df_r_thirds, real_obj.get("ko_results", {}))

def resolve_real_bracket_for_display(real_obj):
    if official_bracket_is_ready(real_obj.get("official_r32", {})):
        return resolve_official_bracket(real_obj.get("official_r32", {}), real_obj.get("ko_results", {}))

    r_tables, _, df_r_thirds = get_all_group_tables(real_obj.get("group_results", {}), use_fifa_tiebreakers=True)
    return resolve_full_bracket(
        r_tables,
        df_r_thirds,
        real_obj.get("ko_results", {}),
        require_complete_groups=False,
        third_place_mode="provisional",
    )
	
def select_third_place_qualifiers(df_thirds, third_place_mode):
    if df_thirds.empty:
        return []
    if third_place_mode == "qualified" and "Qualified" in df_thirds.columns:
        return df_thirds[df_thirds["Qualified"]].head(8).to_dict('records')
    if third_place_mode == "provisional":
        provisional_thirds = df_thirds
        if "PJ" in provisional_thirds.columns:
            provisional_thirds = provisional_thirds[provisional_thirds["PJ"] > 0]
        return provisional_thirds.head(8).to_dict('records')
    return df_thirds.head(8).to_dict('records')

def resolve_full_bracket_from_slots(clasificados, df_thirds, ko_data, third_place_mode="qualified"):
    mejores_8_terceros = select_third_place_qualifiers(df_thirds, third_place_mode)

    # Annex C maps each possible set of eight best third-placed groups to R32 slots.
    asignaciones_terceros = {}
    if len(mejores_8_terceros) == 8:
        terceros_por_grupo = {t["Grupo"][-1]: t["Equipo"] for t in mejores_8_terceros}
        annex_key = "".join(sorted(terceros_por_grupo.keys()))
        annex_assignment = ANNEX_C_ASSIGNMENTS.get(annex_key)
        if annex_assignment:
            asignaciones_terceros = {
                slot: terceros_por_grupo[group_letter]
                for slot, group_letter in annex_assignment["slots"].items()
            }

    def get_team(slot):
        if slot.startswith("1") or slot.startswith("2"): 
            return clasificados.get(slot, f"Por definir ({slot})")
        if slot.startswith("3rd_from_"):
            lider_slot = slot.split("_from_")[1]
            return asignaciones_terceros.get(lider_slot, "Esperando Tercero...")
        return slot

    # --- R32: DIECISEISAVOS (M73 al M88) ---
    r32 = [{"id": i, "match_number": 73 + i, "L_team": get_team(l), "V_team": get_team(v)} for i, (l, v) in enumerate(R32_SLOT_PAIRS)]
    return resolve_bracket_from_r32(r32, ko_data)

def resolve_full_bracket(group_tables, df_thirds, ko_data, require_complete_groups=True, third_place_mode="qualified"):
    clasificados = {}
    for g, tabla in group_tables.items():
        complete = "PJ" in tabla.columns and int(tabla["PJ"].sum()) == len(PARTIDOS_GRUPOS[g]) * 2
        has_results = "PJ" in tabla.columns and int(tabla["PJ"].sum()) > 0
        if len(tabla) >= 2 and (complete or (not require_complete_groups and has_results)):
            clasificados[f"1{g[-1]}"] = tabla.iloc[0]["Equipo"]
            clasificados[f"2{g[-1]}"] = tabla.iloc[1]["Equipo"]

    return resolve_full_bracket_from_slots(clasificados, df_thirds, ko_data, third_place_mode=third_place_mode)

def projected_result_options(local, visitante):
    return [
        (local, visitante, {"l": 1, "v": 0, "l_yellow": 0, "l_red": 0, "v_yellow": 0, "v_red": 0}),
        (local, visitante, {"l": 0, "v": 0, "l_yellow": 0, "l_red": 0, "v_yellow": 0, "v_red": 0}),
        (local, visitante, {"l": 0, "v": 1, "l_yellow": 0, "l_red": 0, "v_yellow": 0, "v_red": 0}),
    ]

def enumerate_group_position_sets(group_name, resultados_dict):
    remaining_matches = [
        (i, local, visitante)
        for i, (local, visitante) in enumerate(PARTIDOS_GRUPOS[group_name])
        if f"{group_name}_{i}" not in resultados_dict
    ]
    position_sets = {team: set() for team in GRUPOS_EQUIPOS[group_name]}

    def visit(match_index, projected_results):
        if match_index == len(remaining_matches):
            table = get_all_group_tables(projected_results, use_fifa_tiebreakers=True)[0][group_name]
            for idx, row in table.reset_index(drop=True).iterrows():
                position_sets[row["Equipo"]].add(idx + 1)
            return

        i, local, visitante = remaining_matches[match_index]
        match_id = f"{group_name}_{i}"
        for _, _, result in projected_result_options(local, visitante):
            projected_results[match_id] = result
            visit(match_index + 1, projected_results)
            projected_results.pop(match_id, None)

    visit(0, dict(resultados_dict))
    return position_sets

def qualification_statuses_from_real_results(resultados_dict):
    statuses = {}
    for group_name in GRUPOS_EQUIPOS.keys():
        group_letter = group_name[-1]
        position_sets = enumerate_group_position_sets(group_name, resultados_dict)
        for team, positions in position_sets.items():
            if not positions:
                continue

            status = None
            best_position = min(positions)
            worst_position = max(positions)
            locked_position = best_position if len(positions) == 1 else None

            if locked_position in (1, 2):
                slot = f"{locked_position}{group_letter}"
                match_number = R32_MATCH_BY_SLOT.get(slot)
                status = {
                    "type": "locked_position",
                    "label": f"{slot} confirmado",
                    "table_label": f"Clasificado ({slot})",
                    "bracket_label": f"{slot} confirmado" + (f" - M{match_number}" if match_number else ""),
                    "slot": slot,
                    "match_number": match_number,
                }
            elif worst_position <= 2:
                status = {
                    "type": "qualified",
                    "label": "Clasificado",
                    "table_label": "Clasificado",
                    "bracket_label": "Clasificado",
                    "slot": None,
                    "match_number": None,
                }
            elif locked_position == 4:
                status = {
                    "type": "eliminated",
                    "label": "Eliminado",
                    "table_label": "Eliminado",
                    "bracket_label": "Eliminado",
                    "slot": None,
                    "match_number": None,
                }

            if status:
                statuses[team] = status
    return statuses

def status_for_team(team, team_statuses):
    if team_is_pending(team):
        return None
    return (team_statuses or {}).get(team)

def add_real_status_columns(table, team_statuses):
    display_table = table.copy()
    display_table["Estado"] = display_table["Equipo"].map(lambda team: (team_statuses.get(team) or {}).get("table_label", ""))
    display_table["R32"] = display_table["Equipo"].map(lambda team: (team_statuses.get(team) or {}).get("bracket_label", ""))
    return display_table

def style_real_status_table(table):
    def row_style(row):
        status = row.get("Estado", "")
        if "Eliminado" in status:
            return ["background-color: #fde8e8; color: #7f1d1d;"] * len(row)
        if "Clasificado" in status:
            return ["background-color: #e9f7ef; color: #14532d; font-weight: 600;"] * len(row)
        return [""] * len(row)

    return table.style.apply(row_style, axis=1)

def UI_real_status_summary(team_statuses):
    locked = [
        f"{team} ({status['bracket_label']})"
        for team, status in team_statuses.items()
        if status["type"] == "locked_position"
    ]
    eliminated = [
        team
        for team, status in team_statuses.items()
        if status["type"] == "eliminated"
    ]
    if locked:
        st.success("Posiciones confirmadas: " + ", ".join(locked))
    if eliminated:
        st.error("Eliminados: " + ", ".join(eliminated))

def build_simulated_group_results(real_group_results):
    simulated_results = dict(real_group_results)
    for group_name, matches in PARTIDOS_GRUPOS.items():
        for i, _ in enumerate(matches):
            match_id = f"{group_name}_{i}"
            if match_id in real_group_results:
                continue
            simulated_results[match_id] = {
                "l": st.session_state.get(f"sim_applied_l_{match_id}", 0),
                "v": st.session_state.get(f"sim_applied_v_{match_id}", 0),
                "l_yellow": 0,
                "l_red": 0,
                "v_yellow": 0,
                "v_red": 0,
            }
    return simulated_results

def reset_simulation_inputs(real_group_results):
    for group_name, matches in PARTIDOS_GRUPOS.items():
        for i, _ in enumerate(matches):
            match_id = f"{group_name}_{i}"
            if match_id in real_group_results:
                continue
            for prefix in ["sim_draft_l", "sim_draft_v", "sim_applied_l", "sim_applied_v"]:
                st.session_state.pop(f"{prefix}_{match_id}", None)
    st.session_state["real_group_simulation_applied"] = False

def apply_simulation_inputs(real_group_results):
    for group_name, matches in PARTIDOS_GRUPOS.items():
        for i, _ in enumerate(matches):
            match_id = f"{group_name}_{i}"
            if match_id in real_group_results:
                continue
            st.session_state[f"sim_applied_l_{match_id}"] = st.session_state.get(f"sim_draft_l_{match_id}", 0)
            st.session_state[f"sim_applied_v_{match_id}"] = st.session_state.get(f"sim_draft_v_{match_id}", 0)
    st.session_state["real_group_simulation_applied"] = True

def UI_real_group_simulator(real_group_results):
    st.subheader("🧪 Simulador de Clasificación")
    pending_count = sum(
        1
        for group_name, matches in PARTIDOS_GRUPOS.items()
        for i, _ in enumerate(matches)
        if f"{group_name}_{i}" not in real_group_results
    )
    st.metric("Partidos pendientes simulables", pending_count)

    if st.button("Reiniciar simulación", key="reset_real_group_simulation"):
        reset_simulation_inputs(real_group_results)
        st.rerun()

    sim_input_tab, sim_table_tab, sim_bracket_tab = st.tabs(["Partidos", "Tablas", "Llave R32"])

    with sim_input_tab:
        with st.form("form_real_group_simulator"):
            for group_name, matches in PARTIDOS_GRUPOS.items():
                finished_count = sum(1 for i, _ in enumerate(matches) if f"{group_name}_{i}" in real_group_results)
                with st.expander(f"{group_name} ({finished_count}/{len(matches)} oficiales)", expanded=finished_count < len(matches)):
                    for i, (local, visitante) in enumerate(matches):
                        match_id = f"{group_name}_{i}"
                        official_result = real_group_results.get(match_id)
                        if official_result:
                            cur_l = official_result.get("l", 0)
                            cur_v = official_result.get("v", 0)
                            disabled = True
                            status_text = "Oficial"
                            l_key = f"sim_official_l_{match_id}"
                            v_key = f"sim_official_v_{match_id}"
                        else:
                            cur_l = st.session_state.get(
                                f"sim_draft_l_{match_id}",
                                st.session_state.get(f"sim_applied_l_{match_id}", 0),
                            )
                            cur_v = st.session_state.get(
                                f"sim_draft_v_{match_id}",
                                st.session_state.get(f"sim_applied_v_{match_id}", 0),
                            )
                            disabled = False
                            status_text = "Pendiente"
                            l_key = f"sim_draft_l_{match_id}"
                            v_key = f"sim_draft_v_{match_id}"

                        c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 0.7, 1, 3, 1.2])
                        c1.write(local)
                        c2.number_input(
                            "",
                            0,
                            20,
                            cur_l,
                            key=l_key,
                            disabled=disabled,
                            label_visibility="collapsed",
                        )
                        c3.write("vs")
                        c4.number_input(
                            "",
                            0,
                            20,
                            cur_v,
                            key=v_key,
                            disabled=disabled,
                            label_visibility="collapsed",
                        )
                        c5.write(visitante)
                        c6.caption(status_text)

            if st.form_submit_button("Aplicar simulación"):
                apply_simulation_inputs(real_group_results)
                st.rerun()

    if not st.session_state.get("real_group_simulation_applied", False):
        with sim_table_tab:
            st.info("Ingresa los resultados pendientes y presiona Aplicar simulación para recalcular tablas.")
        with sim_bracket_tab:
            st.info("La llave simulada aparecerá después de aplicar la simulación.")
        return

    simulated_results = build_simulated_group_results(real_group_results)
    sim_tables, _, sim_thirds = get_all_group_tables(simulated_results, use_fifa_tiebreakers=True)
    sim_statuses = qualification_statuses_from_real_results(simulated_results)

    with sim_table_tab:
        UI_real_status_summary(sim_statuses)
        cx = st.columns(3)
        for idx, group_name in enumerate(PARTIDOS_GRUPOS.keys()):
            with cx[idx % 3]:
                st.write(f"**{group_name}**")
                sim_group_table = add_real_status_columns(sim_tables[group_name], sim_statuses)
                st.dataframe(style_real_status_table(sim_group_table), hide_index=True)

        st.subheader("🥉 Terceros Simulados")
        third_columns = ["Grupo", "Equipo", "Pts", "GD", "GF", "Avanza"]
        if {"FairPlay", "Ranking FIFA"}.issubset(sim_thirds.columns):
            third_columns = ["Grupo", "Equipo", "Pts", "GD", "GF", "FairPlay", "Ranking FIFA", "Avanza"]
        st.dataframe(sim_thirds[third_columns], hide_index=True)

    with sim_bracket_tab:
        sim_bracket = resolve_full_bracket(sim_tables, sim_thirds, {}, require_complete_groups=True)
        UI_arbol_bracket(sim_bracket, {}, team_statuses=sim_statuses)
    
# --- INTERFAZ ---
st.set_page_config(page_title="Quiniela Pro Mundial 2026", layout="wide")
data = load_data()
predictions_locked = predictions_are_locked()
official_bracket_predictions_locked = official_bracket_predictions_are_locked()

st.sidebar.title("🏆 Configuración")
user = st.sidebar.text_input("Tu Nombre de Jugador:")
admin_requested = st.sidebar.toggle("Modo Administrador")
admin_mode = False

if admin_requested:
    admin_password = st.sidebar.text_input("Contraseña de administrador:", type="password", key="admin_password")
    if admin_password == ADMIN_PASSWORD:
        admin_mode = True
        st.sidebar.success("Modo administrador activado.")
    elif admin_password:
        st.sidebar.error("Contraseña incorrecta.")
    else:
        st.sidebar.info("Ingresa la contraseña para acceder al modo administrador.")

if admin_mode:
    st.sidebar.divider()
    st.sidebar.subheader("💾 Backup de Datos")
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"quiniela_backup_{backup_timestamp}.json"

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            backup_data = f.read()
        st.sidebar.caption(f"Archivo actual: {DATA_FILE}")
    else:
        backup_data = json.dumps(data, indent=4, ensure_ascii=False).encode("utf-8")
        st.sidebar.caption(f"{DATA_FILE} todavía no existe. Se descargará el estado actual en memoria.")

    st.sidebar.download_button(
        "Descargar JSON",
        data=backup_data,
        file_name=backup_filename,
        mime="application/json",
    )

if not user:
    st.info("👈 Por favor ingresa tu nombre en la barra lateral para sincronizar tus datos.")
    st.stop()

if user not in data["users"]: data["users"][user] = empty_user_predictions()
normalize_user_data(data["users"][user])

t_pred, t_otros, t_real, t_puntos = st.tabs(["🔮 Mi Predicción", "👥 Otros Jugadores", "🌍 Realidad del Mundial", "🥇 Ranking y Puntuación"])

# --- FUNCION INTERACTIVA PARA BRACKETS ---
def team_is_pending(team):
    return any(token in team for token in ["Por definir", "Mejor", "Esperando"])

def flag_for_team(team):
    return "" if team_is_pending(team) else TEAM_FLAGS.get(team, "🏳️")

def get_match_winner_side(match_data):
    if not match_data:
        return None
    l_score = match_data.get("l", 0)
    v_score = match_data.get("v", 0)
    if l_score > v_score:
        return "L"
    if l_score < v_score:
        return "V"
    return match_data.get("avanza", "L")

def render_tree_team(team, score, side, winner_side, team_statuses=None):
    pending_class = " pending" if team_is_pending(team) else ""
    winner_class = " winner" if winner_side == side else ""
    status = status_for_team(team, team_statuses)
    locked_class = " locked" if status and status["type"] == "locked_position" else ""
    score_html = "" if score is None else f"<span class='tree-score'>{score}</span>"
    status_html = ""
    if status and status["type"] == "locked_position":
        status_html = f"<span class='tree-status'>{escape(status['bracket_label'])}</span>"
    return (
        f"<div class='tree-team{winner_class}{pending_class}{locked_class}'>"
        f"<span class='tree-flag'>{escape(flag_for_team(team))}</span>"
        f"<span class='tree-name'>{escape(team)}{status_html}</span>"
        f"{score_html}"
        "</div>"
    )

def render_tree_match(round_key, match, storage_path, team_statuses=None):
    m_id = f"{round_key}_{match['id']}"
    match_data = storage_path.get(m_id)
    winner_side = get_match_winner_side(match_data)
    l_score = match_data.get("l") if match_data else None
    v_score = match_data.get("v") if match_data else None
    match_number = match.get("match_number")
    label = f"M{match_number}" if match_number else ""
    return (
        "<div class='tree-match-card'>"
        f"<div class='tree-match-label'>{escape(label)}</div>"
        f"{render_tree_team(match['L_team'], l_score, 'L', winner_side, team_statuses)}"
        f"{render_tree_team(match['V_team'], v_score, 'V', winner_side, team_statuses)}"
        "</div>"
    )

def get_tree_r32_leaf_order(round_key="Final", match_id=0):
    if round_key == "R32":
        return [match_id]
    if round_key == "R16":
        return [r32_id for r32_id in R16_SLOTS[match_id]]
    if round_key == "QF":
        return [
            r32_id
            for r16_id in QF_SLOTS[match_id]
            for r32_id in get_tree_r32_leaf_order("R16", r16_id)
        ]
    if round_key == "SF":
        return [
            r32_id
            for qf_id in SF_SLOTS[match_id]
            for r32_id in get_tree_r32_leaf_order("QF", qf_id)
        ]
    if round_key == "Final":
        return [
            r32_id
            for sf_id in (0, 1)
            for r32_id in get_tree_r32_leaf_order("SF", sf_id)
        ]
    return []

def get_tree_match_position(round_key, match_id, r32_row_by_id):
    leaf_ids = get_tree_r32_leaf_order(round_key, match_id)
    rows = [r32_row_by_id[leaf_id] for leaf_id in leaf_ids]
    row_start = min(rows)
    row_span = max(rows) - row_start + 1
    return row_start, row_span

def UI_arbol_bracket(bracket_dict, storage_path, team_statuses=None):
    rounds = [
        ("R32", "Dieciseisavos"),
        ("R16", "Octavos"),
        ("QF", "Cuartos"),
        ("SF", "Semifinales"),
        ("Final", "Final"),
    ]
    headers = "".join(f"<div class='tree-round-title'>{escape(round_name)}</div>" for _, round_name in rounds)
    r32_leaf_order = get_tree_r32_leaf_order()
    r32_row_by_id = {match_id: row_index + 1 for row_index, match_id in enumerate(r32_leaf_order)}
    match_cards = []
    for round_index, (round_key, _) in enumerate(rounds):
        matches = bracket_dict[round_key]
        if round_key == "R32":
            matches = sorted(matches, key=lambda match: r32_row_by_id[match["id"]])
        for match in matches:
            row_start, row_span = get_tree_match_position(round_key, match["id"], r32_row_by_id)
            connect_class = "" if round_key == "Final" else " tree-match-connect"
            match_cards.append(
                f"<div class='tree-match{connect_class}' "
                f"style='grid-column:{round_index + 1}; grid-row:{row_start} / span {row_span};'>"
                f"{render_tree_match(round_key, match, storage_path, team_statuses)}"
                "</div>"
            )

    third_place = render_tree_match("Third", bracket_dict["Third"][0], storage_path, team_statuses)
    champion = bracket_dict.get("Campeon", "Por definir")
    champion_html = (
        "<div class='tree-champion'>"
        "<div class='tree-champion-label'>Campeón</div>"
        f"<div class='tree-champion-team'><span>{escape(flag_for_team(champion))}</span>{escape(champion)}</div>"
        "</div>"
    )

    st.markdown(
        f"""
        <style>
            .bracket-tree-wrap {{
                overflow-x: auto;
                padding: 0.25rem 0 1rem;
            }}
            .bracket-tree {{
                min-width: 1060px;
                color: #172033;
            }}
            .tree-header {{
                display: grid;
                grid-template-columns: repeat(5, minmax(190px, 1fr));
                gap: 1rem;
                margin-bottom: 0.75rem;
            }}
            .tree-round-title {{
                font-size: 0.82rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0;
                color: #4a5568;
            }}
            .tree-grid {{
                display: grid;
                grid-template-columns: repeat(5, minmax(190px, 1fr));
                grid-template-rows: repeat(16, minmax(58px, auto));
                column-gap: 1rem;
                row-gap: 0.45rem;
                align-items: stretch;
            }}
            .tree-match {{
                position: relative;
                display: flex;
                align-items: center;
            }}
            .tree-match-connect::after {{
                content: "";
                position: absolute;
                right: -1rem;
                top: 50%;
                width: 1rem;
                border-top: 2px solid #b8c3d8;
            }}
            .tree-match-card {{
                width: 100%;
                border: 1px solid #d5deed;
                border-left: 4px solid #2f80ed;
                background: #ffffff;
                border-radius: 8px;
                box-shadow: 0 1px 4px rgba(25, 36, 55, 0.08);
                padding: 0.45rem;
            }}
            .tree-match-label {{
                margin-bottom: 0.25rem;
                font-size: 0.72rem;
                font-weight: 700;
                color: #64748b;
            }}
            .tree-team {{
                display: grid;
                grid-template-columns: 1.8rem minmax(0, 1fr) auto;
                align-items: center;
                min-height: 2rem;
                gap: 0.35rem;
                border-radius: 6px;
                padding: 0.25rem 0.35rem;
                font-size: 0.9rem;
                line-height: 1.1;
            }}
            .tree-team + .tree-team {{
                margin-top: 0.2rem;
            }}
            .tree-team.winner {{
                background: #e9f7ef;
                color: #0f5c3a;
                font-weight: 700;
            }}
            .tree-team.locked {{
                outline: 2px solid #22c55e;
                background: #ecfdf3;
            }}
            .tree-team.pending {{
                color: #7a8496;
                background: #f7f9fc;
                font-style: italic;
            }}
            .tree-flag {{
                font-size: 1.2rem;
                text-align: center;
            }}
            .tree-name {{
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            .tree-status {{
                display: block;
                margin-top: 0.12rem;
                font-size: 0.68rem;
                font-weight: 700;
                color: #15803d;
            }}
            .tree-score {{
                min-width: 1.4rem;
                text-align: center;
                border-radius: 999px;
                background: #eef2f7;
                color: #1f2937;
                font-weight: 700;
                padding: 0.1rem 0.35rem;
            }}
            .tree-extras {{
                display: grid;
                grid-template-columns: minmax(240px, 1fr) minmax(240px, 1fr);
                gap: 1rem;
                margin-top: 1rem;
            }}
            .tree-champion {{
                border: 1px solid #d8c47a;
                border-left: 4px solid #d9a441;
                border-radius: 8px;
                background: #fff9e8;
                padding: 0.7rem;
            }}
            .tree-champion-label {{
                font-size: 0.72rem;
                font-weight: 700;
                text-transform: uppercase;
                color: #7a5b14;
                margin-bottom: 0.35rem;
            }}
            .tree-champion-team {{
                display: flex;
                gap: 0.5rem;
                align-items: center;
                font-weight: 800;
                color: #382b0a;
            }}
        </style>
        <div class="bracket-tree-wrap">
            <div class="bracket-tree">
                <div class="tree-header">{headers}</div>
                <div class="tree-grid">{''.join(match_cards)}</div>
                <div class="tree-extras">
                    {champion_html}
                    <div>{third_place}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def UI_fase_eliminatoria(bracket_dict, storage_path, key_prefix, read_only=False, team_statuses=None):
    view_mode = st.radio(
        "Vista del bracket:",
        ["Partidos", "Árbol con banderas"],
        horizontal=True,
        key=f"{key_prefix}_bracket_view",
    )
    if view_mode == "Árbol con banderas":
        UI_arbol_bracket(bracket_dict, storage_path, team_statuses=team_statuses)
        return

    rondas = [
        ("R32", "Dieciseisavos de Final"), 
        ("R16", "Octavos de Final"), 
        ("QF", "Cuartos de Final"), 
        ("SF", "Semifinales"), 
        ("Third", "Partido por el Tercer Puesto"),
        ("Final", "Gran Final")
    ]
    for r_key, r_name in rondas:
        with st.expander(f"➔ {r_name}", expanded=True):
            for match in bracket_dict[r_key]:
                m_id = f"{r_key}_{match['id']}"
                has_pick = m_id in storage_path
                cur = storage_path.get(m_id, {"l": 0, "v": 0, "avanza": "L"})
                match_number = match.get("match_number")
                
                bloqueado = (
                    any(f in match["L_team"] for f in ["Por definir", "Mejor", "Esperando"])
                    or any(f in match["V_team"] for f in ["Por definir", "Mejor", "Esperando"])
                    or read_only
                )
                
                c0, c1, c2, c3, c4, c5, c6 = st.columns([0.9, 3, 1, 1, 1, 3, 2])
                c0.write(f"**M{match_number}**" if match_number else "")
                c1.write(f"**{match['L_team']}**")
                left_status = status_for_team(match["L_team"], team_statuses)
                if left_status and left_status["type"] == "locked_position":
                    c1.caption(left_status["bracket_label"])
                l_in = c2.number_input("", 0, 15, cur["l"], key=f"{key_prefix}_l_{m_id}", disabled=bloqueado, label_visibility="collapsed")
                c3.write("vs")
                v_in = c4.number_input("", 0, 15, cur["v"], key=f"{key_prefix}_v_{m_id}", disabled=bloqueado, label_visibility="collapsed")
                c5.write(f"**{match['V_team']}**")
                right_status = status_for_team(match["V_team"], team_statuses)
                if right_status and right_status["type"] == "locked_position":
                    c5.caption(right_status["bracket_label"])
                
                if read_only:
                    if not has_pick:
                        c6.caption("Sin predicción")
                    elif (
                        any(f in match["L_team"] for f in ["Por definir", "Mejor", "Esperando"])
                        or any(f in match["V_team"] for f in ["Por definir", "Mejor", "Esperando"])
                    ):
                        c6.caption("Esperando cruces...")
                    elif l_in == v_in:
                        ganador_penales = match["L_team"] if cur.get("avanza", "L") == "L" else match["V_team"]
                        c6.caption(f"Pasa: {ganador_penales}")
                    else:
                        c6.caption("Ganador directo")
                elif l_in == v_in and not bloqueado:
                    # Mostrar nombres de equipos reales en vez de "Local" o "Visita"
                    team_options = [match["L_team"], match["V_team"]]
                    current_avanza = cur.get("avanza", "L")
                    idx = 0 if current_avanza == "L" else 1
                    
                    av = c6.selectbox("¿Quién pasa (Penales)?", team_options, index=idx, key=f"{key_prefix}_av_{m_id}")
                    if not read_only: 
                        # Lo seguimos guardando internamente como "L" o "V"
                        storage_path[m_id] = {"l": l_in, "v": v_in, "avanza": "L" if av == match["L_team"] else "V"}
                elif not bloqueado:
                    c6.caption("Ganador directo")
                    if not read_only: storage_path[m_id] = {"l": l_in, "v": v_in, "avanza": "L" if l_in > v_in else "V"}
                else:
                    c6.caption("Esperando cruces...")
            
            if not read_only:
                st.write("") 
                if st.button(f"Actualizar y Avanzar a la siguiente ronda ({r_name})", key=f"btn_save_ko_{key_prefix}_{r_key}"):
                    save_data(data)
                    st.rerun() 

def UI_admin_ko_results(bracket_dict, ko_results):
    st.caption("Marca como finalizado solo el partido que quieres publicar. Los partidos sin marcar no se guardan como resultados oficiales.")
    rondas = [
        ("R32", "Dieciseisavos de Final"),
        ("R16", "Octavos de Final"),
        ("QF", "Cuartos de Final"),
        ("SF", "Semifinales"),
        ("Third", "Partido por el Tercer Puesto"),
        ("Final", "Gran Final"),
    ]
    pending_tokens = ["Por definir", "Mejor", "Esperando"]

    for r_key, r_name in rondas:
        with st.expander(f"➔ {r_name}", expanded=r_key == "R32"):
            with st.form(f"form_admin_ko_{r_key}"):
                for match in bracket_dict[r_key]:
                    m_id = f"{r_key}_{match['id']}"
                    cur = ko_results.get(m_id, {"l": 0, "v": 0, "avanza": "L"})
                    match_number = match.get("match_number")
                    blocked = (
                        any(token in match["L_team"] for token in pending_tokens)
                        or any(token in match["V_team"] for token in pending_tokens)
                    )

                    c0, c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 0.9, 3, 1, 0.7, 1, 3, 2.2])
                    c0.checkbox(
                        "Finalizado",
                        value=m_id in ko_results,
                        key=f"admin_ko_played_{m_id}",
                        disabled=blocked,
                    )
                    c1.write(f"**M{match_number}**" if match_number else "")
                    c2.write(f"**{match['L_team']}**")
                    c3.number_input(
                        "",
                        0,
                        15,
                        cur["l"],
                        key=f"admin_ko_l_{m_id}",
                        disabled=blocked,
                        label_visibility="collapsed",
                    )
                    c4.write("vs")
                    c5.number_input(
                        "",
                        0,
                        15,
                        cur["v"],
                        key=f"admin_ko_v_{m_id}",
                        disabled=blocked,
                        label_visibility="collapsed",
                    )
                    c6.write(f"**{match['V_team']}**")
                    if blocked:
                        c7.caption("Esperando cruces...")
                    else:
                        team_options = [match["L_team"], match["V_team"]]
                        current_avanza = cur.get("avanza", "L")
                        c7.selectbox(
                            "Pasa si empate",
                            team_options,
                            index=0 if current_avanza == "L" else 1,
                            key=f"admin_ko_av_{m_id}",
                        )

                if st.form_submit_button(f"Guardar resultados de {r_name}"):
                    for match in bracket_dict[r_key]:
                        m_id = f"{r_key}_{match['id']}"
                        blocked = (
                            any(token in match["L_team"] for token in pending_tokens)
                            or any(token in match["V_team"] for token in pending_tokens)
                        )
                        if blocked:
                            continue

                        if st.session_state[f"admin_ko_played_{m_id}"]:
                            l_score = st.session_state[f"admin_ko_l_{m_id}"]
                            v_score = st.session_state[f"admin_ko_v_{m_id}"]
                            if l_score > v_score:
                                avanza = "L"
                            elif l_score < v_score:
                                avanza = "V"
                            else:
                                avanza = "L" if st.session_state[f"admin_ko_av_{m_id}"] == match["L_team"] else "V"
                            ko_results[m_id] = {"l": l_score, "v": v_score, "avanza": avanza}
                        else:
                            ko_results.pop(m_id, None)

                    save_data(data)
                    st.success(f"Resultados guardados para {r_name}.")
                    st.rerun()

def UI_prediccion_bracket_oficial(player_data, key_prefix, read_only=False):
    official_r32 = data["real_results"].get("official_r32", {})
    if not official_bracket_is_ready(official_r32):
        st.info("El bracket oficial de dieciseisavos todavía no ha sido cargado por el administrador.")
        return

    player_data.setdefault("official_bracket_predictions", {})
    storage_path = player_data["official_bracket_predictions"]
    official_bracket = resolve_official_bracket(official_r32, storage_path)
    st.metric(label="🏆 CAMPEÓN PREDICHO EN BRACKET OFICIAL", value=official_bracket["Campeon"])
    UI_fase_eliminatoria(official_bracket, storage_path, key_prefix, read_only=read_only)

def official_bracket_prediction_match_ids():
    return (
        [f"R32_{i}" for i in range(16)]
        + [f"R16_{i}" for i in range(8)]
        + [f"QF_{i}" for i in range(4)]
        + [f"SF_{i}" for i in range(2)]
        + ["Third_0", "Final_0"]
    )

def UI_admin_official_prediction_status(official_r32):
    st.subheader("📋 Estado de Predicciones del Bracket Oficial")
    users = data.get("users", {})
    if not users:
        st.info("No hay jugadores registrados todavía.")
        return

    expected_match_ids = set(official_bracket_prediction_match_ids())
    total_expected = len(expected_match_ids)
    rows = []
    submitted_count = 0
    complete_count = 0
    official_ready = official_bracket_is_ready(official_r32)

    for player_name in sorted(users.keys(), key=str.casefold):
        player_data = users[player_name]
        predictions = player_data.get("official_bracket_predictions", {})
        predicted_match_count = len(expected_match_ids.intersection(predictions.keys()))
        has_prediction = predicted_match_count > 0
        is_complete = predicted_match_count == total_expected
        submitted_count += 1 if has_prediction else 0
        complete_count += 1 if is_complete else 0

        champion = "Pendiente"
        if official_ready and has_prediction:
            champion = resolve_official_bracket(official_r32, predictions).get("Campeon", "Por definir")

        if is_complete:
            status = "Completa"
        elif has_prediction:
            status = "Iniciada"
        else:
            status = "Sin predicción"

        rows.append({
            "Jugador": player_name,
            "Estado": status,
            "Partidos guardados": f"{predicted_match_count}/{total_expected}",
            "Campeón predicho": champion,
        })

    c1, c2, c3 = st.columns(3)
    c1.metric("Jugadores con predicción", f"{submitted_count}/{len(users)}")
    c2.metric("Predicciones completas", f"{complete_count}/{len(users)}")
    c3.metric("Partidos requeridos", total_expected)
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

def UI_admin_official_r32():
    st.subheader("🧩 Bracket Oficial de Dieciseisavos")
    options = ["Por definir"] + get_all_teams()
    official_r32 = data["real_results"].get("official_r32", {})

    with st.form("form_official_r32"):
        for i in range(16):
            m_id = f"R32_{i}"
            match = official_r32.get(m_id, {})
            c1, c2, c3 = st.columns([1, 4, 4])
            c1.write(f"**M{73 + i}**")
            current_l = match.get("L_team", "Por definir")
            current_v = match.get("V_team", "Por definir")
            c2.selectbox(
                "Equipo A",
                options,
                index=options.index(current_l) if current_l in options else 0,
                key=f"official_r32_l_{i}",
                label_visibility="collapsed",
            )
            c3.selectbox(
                "Equipo B",
                options,
                index=options.index(current_v) if current_v in options else 0,
                key=f"official_r32_v_{i}",
                label_visibility="collapsed",
            )

        if st.form_submit_button("Guardar Bracket Oficial R32"):
            new_official_r32 = {}
            selected_teams = []
            for i in range(16):
                l_team = st.session_state[f"official_r32_l_{i}"]
                v_team = st.session_state[f"official_r32_v_{i}"]
                if l_team != "Por definir" or v_team != "Por definir":
                    new_official_r32[f"R32_{i}"] = {"L_team": l_team, "V_team": v_team}
                if l_team != "Por definir":
                    selected_teams.append(l_team)
                if v_team != "Por definir":
                    selected_teams.append(v_team)

            duplicates = sorted({team for team in selected_teams if selected_teams.count(team) > 1})
            incomplete_pairs = [
                f"M{73 + i}" for i in range(16)
                if (st.session_state[f"official_r32_l_{i}"] == "Por definir") != (st.session_state[f"official_r32_v_{i}"] == "Por definir")
            ]
            if duplicates:
                st.error(f"Equipos repetidos en el bracket oficial: {', '.join(duplicates)}")
            elif incomplete_pairs:
                st.error(f"Partidos incompletos: {', '.join(incomplete_pairs)}")
            else:
                changed = new_official_r32 != official_r32
                data["real_results"]["official_r32"] = new_official_r32
                if changed:
                    for user_data in data["users"].values():
                        user_data["official_bracket_predictions"] = {}
                save_data(data)
                if official_bracket_is_ready(new_official_r32):
                    if changed:
                        st.success("Bracket oficial completo guardado. Las predicciones del bracket oficial se reiniciaron.")
                    else:
                        st.success("Bracket oficial completo guardado.")
                else:
                    st.warning("Bracket oficial guardado parcialmente.")
                st.rerun()

    st.divider()
    UI_admin_official_prediction_status(official_r32)

def build_group_match_rows(group_name, group_results):
    rows = []
    for i, (local, visitante) in enumerate(PARTIDOS_GRUPOS[group_name]):
        m_id = f"{group_name}_{i}"
        result = group_results.get(m_id)
        if result:
            local_cards = f"{result.get('l_yellow', 0)}A / {result.get('l_red', 0)}R"
            visitante_cards = f"{result.get('v_yellow', 0)}A / {result.get('v_red', 0)}R"
            rows.append({
                "Grupo": group_name,
                "Partido": f"{local} vs {visitante}",
                "Resultado": f"{result['l']} - {result['v']}",
                "Tarjetas": f"{local_cards} - {visitante_cards}",
                "Estado": "Finalizado",
            })
        else:
            rows.append({
                "Grupo": group_name,
                "Partido": f"{local} vs {visitante}",
                "Resultado": "Pendiente",
                "Tarjetas": "Pendiente",
                "Estado": "Pendiente",
            })
    return rows

def UI_real_group_results_view(group_results):
    st.subheader("📌 Resultados Reales de Fase de Grupos")
    total_matches = sum(len(matches) for matches in PARTIDOS_GRUPOS.values())
    played_matches = sum(
        1
        for group_name, matches in PARTIDOS_GRUPOS.items()
        for i, _ in enumerate(matches)
        if f"{group_name}_{i}" in group_results
    )
    st.metric("Partidos con resultado oficial", f"{played_matches}/{total_matches}")

    group_options = ["Todos los grupos"] + list(PARTIDOS_GRUPOS.keys())
    selected_group = st.selectbox("Selecciona una vista:", group_options, key="real_group_results_view")

    if selected_group == "Todos los grupos":
        for group_name in PARTIDOS_GRUPOS.keys():
            rows = build_group_match_rows(group_name, group_results)
            finished_count = sum(1 for row in rows if row["Estado"] == "Finalizado")
            with st.expander(f"{group_name} ({finished_count}/{len(rows)} jugados)", expanded=finished_count > 0):
                st.dataframe(pd.DataFrame(rows)[["Partido", "Resultado", "Tarjetas", "Estado"]], hide_index=True)
    else:
        rows = build_group_match_rows(selected_group, group_results)
        st.dataframe(pd.DataFrame(rows)[["Partido", "Resultado", "Tarjetas", "Estado"]], hide_index=True)

def UI_admin_group_results():
    st.subheader("Resultados Reales de Grupos")
    group_results = data["real_results"]["group_results"]
    g_adm = st.selectbox("Grupo Real:", list(PARTIDOS_GRUPOS.keys()), key="admin_group_results_group")

    with st.form("f_real_grp"):
        for i, (local, visitante) in enumerate(PARTIDOS_GRUPOS[g_adm]):
            m_id = f"{g_adm}_{i}"
            cur = group_results.get(m_id, {"l": 0, "v": 0})
            c0, c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([1.2, 2.4, 0.9, 0.9, 0.9, 0.5, 0.9, 0.9, 0.9, 2.4])
            c0.checkbox("Finalizado", value=m_id in group_results, key=f"r_played_{m_id}")
            c1.write(local)
            c2.number_input("Goles", 0, 20, cur.get("l", 0), key=f"r_l_{m_id}")
            c3.number_input("Amar.", 0, 20, cur.get("l_yellow", 0), key=f"r_l_yellow_{m_id}")
            c4.number_input("Rojas", 0, 20, cur.get("l_red", 0), key=f"r_l_red_{m_id}")
            c5.write("vs")
            c6.number_input("Goles", 0, 20, cur.get("v", 0), key=f"r_v_{m_id}")
            c7.number_input("Amar.", 0, 20, cur.get("v_yellow", 0), key=f"r_v_yellow_{m_id}")
            c8.number_input("Rojas", 0, 20, cur.get("v_red", 0), key=f"r_v_red_{m_id}")
            c9.write(visitante)

        if st.form_submit_button("Publicar Resultados Reales de Grupo"):
            for i, _ in enumerate(PARTIDOS_GRUPOS[g_adm]):
                m_id = f"{g_adm}_{i}"
                if st.session_state[f"r_played_{m_id}"]:
                    group_results[m_id] = {
                        "l": st.session_state[f"r_l_{m_id}"],
                        "v": st.session_state[f"r_v_{m_id}"],
                        "l_yellow": st.session_state[f"r_l_yellow_{m_id}"],
                        "l_red": st.session_state[f"r_l_red_{m_id}"],
                        "v_yellow": st.session_state[f"r_v_yellow_{m_id}"],
                        "v_red": st.session_state[f"r_v_red_{m_id}"],
                    }
                else:
                    group_results.pop(m_id, None)
            save_data(data)
            st.success("Datos oficiales guardados.")
            st.rerun()

def UI_admin_participants(current_user):
    st.subheader("👥 Administración de Participantes")
    users = data.get("users", {})
    participant_names = sorted(users.keys(), key=str.casefold)

    duplicate_groups = find_duplicate_participant_groups(participant_names)
    if duplicate_groups:
        st.warning("Posibles participantes duplicados detectados por nombre:")
        for duplicate_group in duplicate_groups:
            st.write(f"- {', '.join(duplicate_group)}")
    else:
        st.info("No se detectan nombres duplicados ignorando mayúsculas, minúsculas y espacios extra.")

    if not participant_names:
        st.info("No hay participantes para eliminar.")
        return

    selected_participant = st.selectbox(
        "Participante a eliminar:",
        participant_names,
        key="admin_delete_participant",
    )
    selected_data = users.get(selected_participant, {})
    st.caption(
        "Predicciones guardadas: "
        f"{len(selected_data.get('group_predictions', {}))} partidos de grupos, "
        f"{len(selected_data.get('ko_predictions', {}))} partidos de llave, "
        f"{len(selected_data.get('official_bracket_predictions', {}))} partidos de bracket oficial."
    )

    if selected_participant == current_user:
        st.warning("No puedes eliminar el participante activo de esta sesión. Cambia temporalmente tu nombre de jugador y vuelve a intentarlo.")
        return

    with st.form("form_delete_participant"):
        confirmation = st.text_input(
            f'Para confirmar, escribe exactamente: "{selected_participant}"',
            key="delete_participant_confirmation",
        )
        delete_submitted = st.form_submit_button("Eliminar participante")

        if delete_submitted:
            if confirmation != selected_participant:
                st.error("La confirmación no coincide con el participante seleccionado.")
            elif selected_participant not in data["users"]:
                st.error("Ese participante ya no existe en los datos.")
            else:
                del data["users"][selected_participant]
                save_data(data)
                st.success(f"Participante eliminado: {selected_participant}")
                st.rerun()

def score_tendency(result):
    if result["l"] > result["v"]:
        return "L"
    if result["l"] < result["v"]:
        return "V"
    return "D"

def classify_prediction_hit(prediction, real_result):
    if not prediction or not real_result:
        return None
    if prediction["l"] == real_result["l"] and prediction["v"] == real_result["v"]:
        return "exact"
    if score_tendency(prediction) == score_tendency(real_result):
        return "tendency"
    return None

def prediction_hit_label(hit_type):
    if hit_type == "exact":
        return "Marcador exacto"
    if hit_type == "tendency":
        return "Tendencia correcta"
    return ""

def prediction_hit_badge_html(hit_type):
    if hit_type not in {"exact", "tendency"}:
        return "<span class='hit-badge hit-none'>Sin acierto</span>"
    return f"<span class='hit-badge hit-{hit_type}'>{prediction_hit_label(hit_type)}</span>"

def render_prediction_hit_legend():
    st.markdown(
        """
        <style>
            .hit-badge {
                display: inline-flex;
                align-items: center;
                min-height: 1.55rem;
                border-radius: 999px;
                padding: 0.18rem 0.55rem;
                font-size: 0.78rem;
                font-weight: 700;
                line-height: 1;
                white-space: nowrap;
            }
            .hit-exact {
                background: #dcfce7;
                color: #14532d;
                border: 1px solid #86efac;
            }
            .hit-tendency {
                background: #fef3c7;
                color: #78350f;
                border: 1px solid #fbbf24;
            }
            .hit-none {
                background: #f1f5f9;
                color: #64748b;
                border: 1px solid #cbd5e1;
            }
            .prediction-match-card {
                display: grid;
                grid-template-columns: minmax(0, 1fr) auto auto auto minmax(0, 1fr) auto;
                align-items: center;
                gap: 0.55rem;
                border: 1px solid #d8dee9;
                border-left: 4px solid #cbd5e1;
                border-radius: 8px;
                padding: 0.55rem 0.65rem;
                margin: 0.35rem 0;
                background: #ffffff;
                color: #172033;
            }
            .prediction-match-card.prediction-hit-exact {
                border-color: #86efac;
                border-left-color: #16a34a;
                background: #f0fdf4;
            }
            .prediction-match-card.prediction-hit-tendency {
                border-color: #fbbf24;
                border-left-color: #d97706;
                background: #fffbeb;
            }
            .prediction-team-left {
                text-align: right;
                font-weight: 700;
                color: #111827;
                overflow-wrap: anywhere;
            }
            .prediction-team-right {
                text-align: left;
                font-weight: 700;
                color: #111827;
                overflow-wrap: anywhere;
            }
            .prediction-score {
                min-width: 1.7rem;
                border-radius: 6px;
                background: #ffffff;
                border: 1px solid #94a3b8;
                color: #0f172a;
                padding: 0.18rem 0.35rem;
                text-align: center;
                font-weight: 800;
            }
            .prediction-vs {
                color: #64748b;
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
            }
            @media (max-width: 700px) {
                .prediction-match-card {
                    grid-template-columns: minmax(0, 1fr) auto auto auto minmax(0, 1fr);
                }
                .prediction-match-card .hit-badge {
                    grid-column: 1 / -1;
                    justify-self: center;
                }
            }
        </style>
        <div style="display:flex; gap:0.45rem; flex-wrap:wrap; margin:0.25rem 0 0.7rem;">
            <span class="hit-badge hit-exact">Marcador exacto</span>
            <span class="hit-badge hit-tendency">Tendencia correcta</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_prediction_hit_badge(container, hit_type, real_result, has_prediction=True):
    if not real_result:
        container.caption("Pendiente")
        return
    if not has_prediction:
        container.markdown("<span class='hit-badge hit-none'>Sin predicción</span>", unsafe_allow_html=True)
        return
    container.markdown(prediction_hit_badge_html(hit_type), unsafe_allow_html=True)

def render_readonly_group_prediction_row(local, visitante, prediction, real_result):
    hit_type = classify_prediction_hit(prediction, real_result)
    row_class = f" prediction-hit-{hit_type}" if hit_type else ""
    score_l = prediction["l"] if prediction else "-"
    score_v = prediction["v"] if prediction else "-"
    if not real_result:
        badge = "<span class='hit-badge hit-none'>Pendiente</span>"
    elif not prediction:
        badge = "<span class='hit-badge hit-none'>Sin predicción</span>"
    else:
        badge = prediction_hit_badge_html(hit_type)
    st.markdown(
        f"""
        <div class="prediction-match-card{row_class}">
            <div class="prediction-team-left">{escape(local)}</div>
            <div class="prediction-score">{score_l}</div>
            <div class="prediction-vs">vs</div>
            <div class="prediction-score">{score_v}</div>
            <div class="prediction-team-right">{escape(visitante)}</div>
            {badge}
        </div>
        """,
        unsafe_allow_html=True,
    )

def UI_prediccion_jugador(player_name, player_data, key_prefix):
    st.header(f"Predicción de {player_name}")
    st_p1, st_p2, st_p3 = st.tabs(["Fase de Grupos", "Fase Eliminatoria (Bracket)", "Bracket Oficial"])
    
    group_predictions = player_data.get("group_predictions", {})
    ko_predictions = player_data.get("ko_predictions", {})
    
    with st_p1:
        g_sel = st.selectbox("Selecciona un grupo:", list(PARTIDOS_GRUPOS.keys()), key=f"{key_prefix}_g_sel")
        render_prediction_hit_legend()
        for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_sel]):
            m_id = f"{g_sel}_{i}"
            prediction = group_predictions.get(m_id)
            real_result = data["real_results"]["group_results"].get(m_id)
            render_readonly_group_prediction_row(l, v, prediction, real_result)

        player_tables, _, player_thirds = get_all_group_tables(group_predictions)
        st.subheader("📋 Tablas según esta predicción:")
        cx = st.columns(3)
        for idx, g in enumerate(PARTIDOS_GRUPOS.keys()):
            with cx[idx % 3]:
                st.write(f"**{g}**")
                st.dataframe(player_tables[g][["Equipo", "Pts", "PJ", "GD", "GF"]], hide_index=True)
                
        st.divider()
        st.subheader("🥉 Mejores Terceros")
        st.dataframe(player_thirds[["Grupo", "Equipo", "Pts", "GD", "GF", "Avanza"]], hide_index=True)

    with st_p2:
        player_tables, _, player_thirds = get_all_group_tables(group_predictions)
        player_bracket = resolve_full_bracket(player_tables, player_thirds, ko_predictions)
        st.metric(label="🏆 CAMPEÓN PREDICHO", value=player_bracket["Campeon"])
        UI_fase_eliminatoria(player_bracket, ko_predictions, f"{key_prefix}_ko", read_only=True)

    with st_p3:
        UI_prediccion_bracket_oficial(player_data, f"{key_prefix}_official_ko", read_only=True)

# ================= TAB 1: MI PREDICCIÓN =================
with t_pred:
    st.header(f"Simulación Completa de {user}")
    if predictions_locked:
        st.warning(f"Predicción 1 bloqueada: {prediction_lock_message()}")
    st_p1, st_p2, st_p3 = st.tabs(["Fase de Grupos", "Fase Eliminatoria (Bracket)", "Bracket Oficial"])
    
    with st_p1:
        g_sel = st.selectbox("Selecciona un grupo para predecir:", list(PARTIDOS_GRUPOS.keys()), key="p_g_sel")
        render_prediction_hit_legend()
        with st.form(f"form_user_{g_sel}"):
            for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_sel]):
                m_id = f"{g_sel}_{i}"
                saved_prediction = data["users"][user]["group_predictions"].get(m_id)
                cur = saved_prediction or {"l": 0, "v": 0}
                real_result = data["real_results"]["group_results"].get(m_id)
                hit_type = classify_prediction_hit(saved_prediction, real_result)
                c1, c2, c3, c4, c5, c6 = st.columns([3,1,1,1,3,2])
                c1.write(l); l_in = c2.number_input("", 0, 20, cur["l"], key=f"u_l_{m_id}", disabled=predictions_locked, label_visibility="collapsed")
                c3.write("vs"); v_in = c4.number_input("", 0, 20, cur["v"], key=f"u_v_{m_id}", disabled=predictions_locked, label_visibility="collapsed")
                c5.write(v)
                render_prediction_hit_badge(c6, hit_type, real_result, has_prediction=saved_prediction is not None)
            if st.form_submit_button("Guardar Resultados del Grupo", disabled=predictions_locked):
                if predictions_are_locked():
                    st.error(prediction_lock_message())
                    st.stop()
                for i, _ in enumerate(PARTIDOS_GRUPOS[g_sel]):
                    m_id = f"{g_sel}_{i}"
                    data["users"][user]["group_predictions"][m_id] = {"l": st.session_state[f"u_l_{m_id}"], "v": st.session_state[f"u_v_{m_id}"]}
                data["users"][user]["ko_predictions"] = {}
                save_data(data)
                st.success("Grupo simulado. La llave se reinició para usar los cruces actualizados.")
                st.rerun()
        
        u_tables, _, df_u_thirds = get_all_group_tables(data["users"][user]["group_predictions"])
        st.subheader("📋 Así lucen tus grupos según tus predicciones:")
        cx = st.columns(3)
        for idx, g in enumerate(PARTIDOS_GRUPOS.keys()):
            with cx[idx % 3]:
                st.write(f"**{g}**")
                st.dataframe(u_tables[g][["Equipo", "Pts", "PJ", "GD", "GF"]], hide_index=True)
                
        st.divider()
        st.subheader("🥉 Tus Mejores Terceros")
        st.dataframe(df_u_thirds[["Grupo", "Equipo", "Pts", "GD", "GF", "Avanza"]], hide_index=True)

    with st_p2:
        st.subheader("🎯 Tu Camino Hacia El Campeón")
        u_tables, _, df_u_thirds = get_all_group_tables(data["users"][user]["group_predictions"])
        user_bracket = resolve_full_bracket(u_tables, df_u_thirds, data["users"][user]["ko_predictions"])
        
        st.metric(label="🏆 TU CAMPEÓN PREDICHO", value=user_bracket["Campeon"])
        UI_fase_eliminatoria(user_bracket, data["users"][user]["ko_predictions"], "u_ko", read_only=predictions_locked)

    with st_p3:
        st.subheader("🎯 Tu Predicción Desde El Bracket Oficial")
        if official_bracket_predictions_locked:
            st.warning(f"Predicción 2 bloqueada: {official_bracket_prediction_lock_message()}")
        UI_prediccion_bracket_oficial(
            data["users"][user],
            "u_official_ko",
            read_only=official_bracket_predictions_locked,
        )

# ================= TAB 2: OTROS JUGADORES =================
with t_otros:
    player_options = [u_name for u_name in data["users"].keys() if u_name and u_name != user]
    
    if not player_options:
        st.info("Todavía no hay otros jugadores con predicciones guardadas.")
    else:
        selected_player = st.selectbox("Elige un jugador para ver su predicción:", sorted(player_options))
        selected_data = data["users"].get(selected_player, {})
        UI_prediccion_jugador(selected_player, selected_data, f"otros_{selected_player}")

# ================= TAB 3: REALIDAD =================
with t_real:
    st.header("🌍 Estado Real del Mundial")
    
    if admin_mode:
        st.subheader("🛠️ Panel Administrador")
        adm_mode_sel = st.radio(
            "¿Qué deseas actualizar?",
            ["Resultados de Grupos", "Bracket Oficial R32", "Fase Eliminatoria", "Participantes"],
            key="admin_real_update_mode",
        )
        
        if adm_mode_sel == "Resultados de Grupos":
            UI_admin_group_results()
        elif adm_mode_sel == "Bracket Oficial R32":
            UI_admin_official_r32()
        elif adm_mode_sel == "Fase Eliminatoria":
            if not official_bracket_is_ready(data["real_results"].get("official_r32", {})):
                st.warning("Carga el bracket oficial R32 antes de publicar resultados de fase eliminatoria.")
            real_bracket = resolve_real_bracket(data["real_results"])
            UI_admin_ko_results(real_bracket, data["real_results"]["ko_results"])
        else:
            UI_admin_participants(user)

    st.divider()

    real_view = st.radio(
        "Visualizar datos reales:",
        ["Partidos de Grupos", "Tablas de Posiciones", "Llave Eliminatoria", "Simulador"],
        horizontal=True,
        key="real_public_view",
    )
    r_tables, _, df_r_thirds = get_all_group_tables(data["real_results"]["group_results"], use_fifa_tiebreakers=True)
    real_team_statuses = qualification_statuses_from_real_results(data["real_results"]["group_results"])

    if real_view == "Partidos de Grupos":
        UI_real_group_results_view(data["real_results"]["group_results"])
    elif real_view == "Tablas de Posiciones":
        st.subheader("📊 Tablas de Posiciones Reales de la FIFA")
        UI_real_status_summary(real_team_statuses)
        cx2 = st.columns(3)
        for idx, g in enumerate(PARTIDOS_GRUPOS.keys()):
            with cx2[idx % 3]:
                st.write(f"**{g}**")
                real_group_table = add_real_status_columns(r_tables[g], real_team_statuses)
                st.dataframe(style_real_status_table(real_group_table), hide_index=True)

        st.subheader("🥉 Tabla de Terceros por Marcadores")
        st.caption("La clasificación oficial de terceros puede depender de fair play y ranking FIFA; usa el bracket oficial R32 cargado por el administrador para la llave real.")
        third_columns = ["Grupo", "Equipo", "Pts", "GD", "GF", "Avanza"]
        if {"FairPlay", "Ranking FIFA"}.issubset(df_r_thirds.columns):
            third_columns = ["Grupo", "Equipo", "Pts", "GD", "GF", "FairPlay", "Ranking FIFA", "Avanza"]
        st.dataframe(df_r_thirds[third_columns], hide_index=True)
    elif real_view == "Llave Eliminatoria":
        st.subheader("🌳 Llave de Eliminación Oficial Actualizada")
        UI_real_status_summary(real_team_statuses)
        if official_bracket_is_ready(data["real_results"].get("official_r32", {})):
            real_bracket = resolve_real_bracket_for_display(data["real_results"])
            st.caption("Usando el bracket oficial R32 cargado por el administrador.")
        else:
            real_bracket = resolve_real_bracket_for_display(data["real_results"])
            st.caption("Bracket oficial provisional calculado con las posiciones actuales de grupos. Solo usa grupos que ya tienen al menos un resultado; los cruces de terceros siguen la tabla Annex C cuando hay ocho terceros provisionales.")
        st.success(f"🏆 CAMPEÓN REAL ACTUAL: {real_bracket['Campeon']}")
        UI_fase_eliminatoria(
            real_bracket,
            data["real_results"].get("ko_results", {}),
            "view_real_ko",
            read_only=True,
            team_statuses=real_team_statuses,
        )
    else:
        UI_real_group_simulator(data["real_results"]["group_results"])

# ================= TAB 4: POSICIONES Y REGLAS =================
with t_puntos:
    st.header("🏆 Tabla de Clasificación de la Quiniela")
    real_results_for_scoring = load_persisted_real_results()

    def extraer_equipos(round_matches):
        eqs = set()
        for m in round_matches:
            for k in ["L_team", "V_team"]:
                if not any(f in m[k] for f in ["Por definir", "Mejor", "Esperando"]):
                    eqs.add(m[k])
        return eqs

    def calcular_puntos_bracket(user_bracket, real_bracket):
        pts = 0
        pts += len(extraer_equipos(user_bracket["R16"]).intersection(extraer_equipos(real_bracket["R16"]))) * 2
        pts += len(extraer_equipos(user_bracket["QF"]).intersection(extraer_equipos(real_bracket["QF"]))) * 4
        pts += len(extraer_equipos(user_bracket["SF"]).intersection(extraer_equipos(real_bracket["SF"]))) * 8
        pts += len(extraer_equipos(user_bracket["Third"]).intersection(extraer_equipos(real_bracket["Third"]))) * 8
        pts += len(extraer_equipos(user_bracket["Final"]).intersection(extraer_equipos(real_bracket["Final"]))) * 16
        if user_bracket["Campeon"] == real_bracket["Campeon"] and real_bracket["Campeon"] != "Por definir":
            pts += 32
        return pts

    def calcular_aciertos_etapas_bracket(user_bracket, real_bracket):
        real_champion = real_bracket.get("Campeon", "Por definir")
        champion_hit = (
            real_champion != "Por definir"
            and user_bracket.get("Campeon") == real_champion
        )
        return {
            "Equipos R16": len(extraer_equipos(user_bracket["R16"]).intersection(extraer_equipos(real_bracket["R16"]))),
            "Equipos R8": len(extraer_equipos(user_bracket["QF"]).intersection(extraer_equipos(real_bracket["QF"]))),
            "Equipos Semifinal": len(extraer_equipos(user_bracket["SF"]).intersection(extraer_equipos(real_bracket["SF"]))),
            "Equipos Final": len(extraer_equipos(user_bracket["Final"]).intersection(extraer_equipos(real_bracket["Final"]))),
            "Campeón": "Sí" if champion_hit else "No",
        }

    def resolve_user_full_bracket(user_obj):
        u_grp = user_obj.get("group_predictions", {})
        u_tables, _, df_u_thirds = get_all_group_tables(u_grp)
        return resolve_full_bracket(u_tables, df_u_thirds, user_obj.get("ko_predictions", {}))

    def resolve_user_official_bracket(user_obj, real_obj):
        return resolve_official_bracket(
            real_obj.get("official_r32", {}),
            user_obj.get("official_bracket_predictions", {}),
        )
	    
    def calcular_aciertos_grupos(user_obj, real_obj):
        stats = {"tendencias": 0, "exactos": 0, "puntos": 0}
        u_grp = user_obj.get("group_predictions", {})
        r_grp = real_obj.get("group_results", {})
        for m_id, r_res in r_grp.items():
            if m_id in u_grp:
                hit_type = classify_prediction_hit(u_grp[m_id], r_res)
                if hit_type == "exact":
                    stats["exactos"] += 1
                    stats["puntos"] += 3
                elif hit_type == "tendency":
                    stats["tendencias"] += 1
                    stats["puntos"] += 1
        return stats

    def sum_goal_totals(predictions, real_results):
        predicted_goals = 0
        real_goals = 0
        for m_id, r_res in real_results.items():
            real_goals += r_res["l"] + r_res["v"]
            if m_id in predictions:
                u_res = predictions[m_id]
                predicted_goals += u_res["l"] + u_res["v"]
        return predicted_goals, real_goals

    def build_goal_total_stats(predicted_goals, real_goals):
        return {
            "display": f"{predicted_goals} / {real_goals}",
            "difference": abs(predicted_goals - real_goals),
        }

    def calcular_goles_torneo_completo(user_obj, real_obj):
        group_predicted_goals, group_real_goals = sum_goal_totals(
            user_obj.get("group_predictions", {}),
            real_obj.get("group_results", {}),
        )
        ko_predicted_goals, ko_real_goals = sum_goal_totals(
            user_obj.get("ko_predictions", {}),
            real_obj.get("ko_results", {}),
        )

        return build_goal_total_stats(
            group_predicted_goals + ko_predicted_goals,
            group_real_goals + ko_real_goals,
        )

    def calcular_goles_bracket_oficial(user_obj, real_obj):
        predicted_goals, real_goals = sum_goal_totals(
            user_obj.get("official_bracket_predictions", {}),
            real_obj.get("ko_results", {}),
        )
        return build_goal_total_stats(predicted_goals, real_goals)

    def calcular_aciertos_r32_bracket_oficial(user_obj, real_obj):
        stats = {"tendencias": 0, "exactos": 0, "puntos": 0}
        u_ko = user_obj.get("official_bracket_predictions", {})
        r_ko = real_obj.get("ko_results", {})
        for i in range(16):
            m_id = f"R32_{i}"
            if m_id not in u_ko or m_id not in r_ko:
                continue

            hit_type = classify_prediction_hit(u_ko[m_id], r_ko[m_id])
            if hit_type == "exact":
                stats["exactos"] += 1
                stats["puntos"] += 3
            elif hit_type == "tendency":
                stats["tendencias"] += 1
                stats["puntos"] += 1
        return stats

    def calcular_puntos_totales(user_obj, real_obj, group_stats=None):
        pts = (group_stats or calcular_aciertos_grupos(user_obj, real_obj))["puntos"]
        rb = resolve_real_bracket(real_obj)
        ub = resolve_user_full_bracket(user_obj)
        pts += calcular_puntos_bracket(ub, rb)
        return pts

    def calcular_puntos_bracket_oficial(user_obj, real_obj):
        official_r32 = real_obj.get("official_r32", {})
        if not official_bracket_is_ready(official_r32):
            return 0

        rb = resolve_official_bracket(official_r32, real_obj.get("ko_results", {}))
        ub = resolve_user_official_bracket(user_obj, real_obj)
        return calcular_aciertos_r32_bracket_oficial(user_obj, real_obj)["puntos"] + calcular_puntos_bracket(ub, rb)
	
    ranking_full = []
    ranking_official = []
    real_full_bracket = resolve_real_bracket(real_results_for_scoring)
    official_ready = official_bracket_is_ready(real_results_for_scoring.get("official_r32", {}))
    real_official_bracket = (
        resolve_official_bracket(real_results_for_scoring.get("official_r32", {}), real_results_for_scoring.get("ko_results", {}))
        if official_ready
        else None
    )
    for u_name, u_data in data["users"].items():
        group_stats = calcular_aciertos_grupos(u_data, real_results_for_scoring)
        full_goal_stats = calcular_goles_torneo_completo(u_data, real_results_for_scoring)
        user_full_bracket = resolve_user_full_bracket(u_data)
        full_stage_stats = calcular_aciertos_etapas_bracket(user_full_bracket, real_full_bracket)
        ranking_full.append({
            "Jugador": u_name,
            "Tendencias Correctas": group_stats["tendencias"],
            "Marcadores Exactos": group_stats["exactos"],
            **full_stage_stats,
            "Goles Predichos/Reales": full_goal_stats["display"],
            "Diferencia Goles": full_goal_stats["difference"],
            "Puntos Totales": calcular_puntos_totales(u_data, real_results_for_scoring, group_stats),
        })
        r32_stats = calcular_aciertos_r32_bracket_oficial(u_data, real_results_for_scoring)
        official_goal_stats = calcular_goles_bracket_oficial(u_data, real_results_for_scoring)
        official_stage_stats = {}
        if official_ready:
            user_official_bracket = resolve_user_official_bracket(u_data, real_results_for_scoring)
            official_stage_stats = calcular_aciertos_etapas_bracket(user_official_bracket, real_official_bracket)
        ranking_official.append({
            "Jugador": u_name,
            "Tendencias R32": r32_stats["tendencias"],
            "Marcadores Exactos R32": r32_stats["exactos"],
            **official_stage_stats,
            "Goles Predichos/Reales": official_goal_stats["display"],
            "Diferencia Goles": official_goal_stats["difference"],
            "Puntos Bracket Oficial": calcular_puntos_bracket_oficial(u_data, real_results_for_scoring),
        })
	        
    st.subheader("Predicción 1: Torneo Completo")
    if ranking_full:
        df_rank = pd.DataFrame(ranking_full).sort_values(
            ["Puntos Totales", "Diferencia Goles"],
            ascending=[False, True],
        ).reset_index(drop=True)
        df_rank.index += 1
        st.table(df_rank)
    else:
        st.info("No hay datos de jugadores aún.")

    st.subheader("Predicción 2: Bracket Oficial")
    if not official_ready:
        st.info("El ranking del bracket oficial se activará cuando el administrador cargue el R32 oficial completo.")
    elif ranking_official:
        df_rank_official = pd.DataFrame(ranking_official).sort_values(
            ["Puntos Bracket Oficial", "Diferencia Goles"],
            ascending=[False, True],
        ).reset_index(drop=True)
        df_rank_official.index += 1
        st.table(df_rank_official)
    else:
        st.info("No hay predicciones de bracket oficial aún.")
        
    st.divider()
    
    st.subheader("📖 Explicación del Criterio de Puntos")
    st.markdown("""
    Para evaluar un torneo completo con fase eliminatoria (*Bracket Challenge*), aplicar puntos por goles en llaves avanzadas castiga al jugador si su equipo fue eliminado antes. Por ello, se utiliza el **Criterio de Progresión Exponencial**:
    
    1. **Predicción 1 - Torneo Completo**
       * Incluye fase de grupos y una llave proyectada desde tus propios resultados de grupos.
       * Esta predicción se evalúa contra los resultados reales de grupos y la llave real/official del torneo.

    2. **Predicción 2 - Bracket Oficial**
       * Se activa cuando el administrador carga el bracket oficial de dieciseisavos.
       * Empieza desde ese bracket oficial y se puntúa en una tabla paralela.
       * Las predicciones se bloquean el **28/06/2026 a las 20:00 CET**.

    3. **En Fase de Grupos (Por Partido):**
       * **3 Puntos:** Resultado Exacto (Le acertaste al marcador idéntico).
       * **1 Punto:** Tendencia Correcta (Acertaste al ganador o al empate, pero con otro marcador).
    
    4. **En Predicción 2 - Dieciseisavos/R32 (Por Partido):**
       * **3 Puntos:** Marcador exacto del partido.
       * **1 Punto:** Tendencia correcta (ganador o empate), pero con otro marcador.
       
    5. **En Fase Eliminatoria (Por Equipo Clasificado):**
       * **2 Puntos** por cada equipo que metas correctamente en **Octavos de Final** (R16).
       * **4 Puntos** por cada equipo que metas correctamente en **Cuartos de Final** (QF).
       * **8 Puntos** por cada equipo que metas correctamente en **Semifinales** (SF) y al **Tercer Puesto**.
       * **16 Puntos** por cada equipo que metas correctamente en la **Gran Final**.
       * **32 Puntos** adicionales si aciertas exactamente al **Campeón del Mundo**.

    6. **Criterio de Desempate: Total de Goles**
       * La tabla se ordena primero por puntos.
       * Si dos o más jugadores tienen los mismos puntos, queda arriba quien tenga menor **Diferencia Goles**.
       * **Diferencia Goles** es la distancia absoluta entre los goles totales predichos y los goles reales de los partidos ya jugados.
       * Este criterio no suma puntos: solo desempata jugadores con el mismo puntaje.
    """)
