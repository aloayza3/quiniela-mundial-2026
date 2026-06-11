import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone

# --- CONFIGURACIÓN DE DATOS ---
DATA_FILE = "quiniela_2026_auto.json"
APP_SCHEMA_VERSION = 3
PREDICTION_LOCK_DEADLINE = datetime(2026, 6, 10, 12, 0, tzinfo=timezone(timedelta(hours=1), "CET"))

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

def predictions_are_locked():
    return datetime.now(timezone.utc) >= PREDICTION_LOCK_DEADLINE.astimezone(timezone.utc)

def prediction_lock_message():
    return f"Las predicciones quedaron bloqueadas el {PREDICTION_LOCK_DEADLINE:%d/%m/%Y a las %H:%M} CET."

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

def rank_equal_points_teams(teams, group_name, resultados_dict, overall_stats, team_order):
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
            ranked.extend(rank_equal_points_teams(tied_teams, group_name, resultados_dict, overall_stats, team_order))
        if len(ranked) == len(teams):
            return ranked

    overall_sorted = sorted(
        teams,
        key=lambda team: (overall_stats[team]["GD"], overall_stats[team]["GF"], -team_order[team]),
        reverse=True,
    )
    return overall_sorted

def rank_group_table(group_name, equipos, resultados_dict):
    team_order = {team: idx for idx, team in enumerate(GRUPOS_EQUIPOS[group_name])}
    teams = GRUPOS_EQUIPOS[group_name]
    teams_by_points = sorted(teams, key=lambda team: (equipos[team]["Pts"], -team_order[team]), reverse=True)

    ranked = []
    for _, tied_teams in split_by_equal_keys(teams_by_points, lambda team: equipos[team]["Pts"]):
        ranked.extend(rank_equal_points_teams(tied_teams, group_name, resultados_dict, equipos, team_order))

    rows = [{"Equipo": team, **equipos[team]} for team in ranked]
    return pd.DataFrame(rows, columns=["Equipo", "Pts", "PJ", "GF", "GC", "GD"])

# --- PROCESAMIENTO DE MATRICES ---
def get_all_group_tables(resultados_dict):
    tables = {}
    thirds = []
    for g in GRUPOS_EQUIPOS.keys():
        completed = group_is_complete(resultados_dict, g)
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
        df = rank_group_table(g, equipos, resultados_dict).reset_index(drop=True)
        tables[g] = df
        if len(df) >= 3:
            tercero = df.iloc[2].to_dict()
            tercero["Grupo"] = g
            tercero["Completo"] = completed
            thirds.append(tercero)
	            
    df_thirds = pd.DataFrame(thirds).sort_values(by=["Pts", "GD", "GF"], ascending=False, kind="mergesort").reset_index(drop=True)
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

def resolve_bracket_from_r32(r32, ko_data):
    # --- R16: OCTAVOS (M89 al M96) ---
    r16_slots = [(1, 4), (0, 2), (3, 5), (6, 7), (10, 11), (8, 9), (13, 15), (12, 14)]
    r16 = [{"id": i, "L_team": get_winner(ko_data.get(f"R32_{l}"), r32[l]["L_team"], r32[l]["V_team"]), "V_team": get_winner(ko_data.get(f"R32_{v}"), r32[v]["L_team"], r32[v]["V_team"])} for i, (l, v) in enumerate(r16_slots)]
    
    # --- QF: CUARTOS (M97 al M100) ---
    qf_slots = [(0, 1), (4, 5), (2, 3), (6, 7)]
    qf = [{"id": i, "L_team": get_winner(ko_data.get(f"R16_{l}"), r16[l]["L_team"], r16[l]["V_team"]), "V_team": get_winner(ko_data.get(f"R16_{v}"), r16[v]["L_team"], r16[v]["V_team"])} for i, (l, v) in enumerate(qf_slots)]
    
    # --- SF: SEMIFINALES (M101 y M102) ---
    sf_slots = [(0, 1), (2, 3)]
    sf = [{"id": i, "L_team": get_winner(ko_data.get(f"QF_{l}"), qf[l]["L_team"], qf[l]["V_team"]), "V_team": get_winner(ko_data.get(f"QF_{v}"), qf[v]["L_team"], qf[v]["V_team"])} for i, (l, v) in enumerate(sf_slots)]
    
    # --- TERCER PUESTO (M103) ---
    third = [{"id": 0, "L_team": get_loser(ko_data.get(f"SF_0"), sf[0]["L_team"], sf[0]["V_team"]), "V_team": get_loser(ko_data.get(f"SF_1"), sf[1]["L_team"], sf[1]["V_team"])}]
    
    # --- FINAL (M104) ---
    final = [{"id": 0, "L_team": get_winner(ko_data.get(f"SF_0"), sf[0]["L_team"], sf[0]["V_team"]), "V_team": get_winner(ko_data.get(f"SF_1"), sf[1]["L_team"], sf[1]["V_team"])}]
    
    campeon = get_winner(ko_data.get("Final_0"), final[0]["L_team"], final[0]["V_team"])
    
    return {"R32": r32, "R16": r16, "QF": qf, "SF": sf, "Third": third, "Final": final, "Campeon": campeon}

def build_official_r32(official_r32):
    r32 = []
    for i in range(16):
        m_id = f"R32_{i}"
        match = official_r32.get(m_id, {})
        r32.append({
            "id": i,
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

    r_tables, _, df_r_thirds = get_all_group_tables(real_obj.get("group_results", {}))
    return resolve_full_bracket(r_tables, df_r_thirds, real_obj.get("ko_results", {}))
	
def resolve_full_bracket_from_slots(clasificados, df_thirds, ko_data):
    if not df_thirds.empty and "Qualified" in df_thirds.columns:
        mejores_8_terceros = df_thirds[df_thirds["Qualified"]].head(8).to_dict('records')
    else:
        mejores_8_terceros = df_thirds.head(8).to_dict('records') if not df_thirds.empty else []

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
    slots_r32 = [
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
    r32 = [{"id": i, "L_team": get_team(l), "V_team": get_team(v)} for i, (l, v) in enumerate(slots_r32)]
    return resolve_bracket_from_r32(r32, ko_data)

def resolve_full_bracket(group_tables, df_thirds, ko_data):
    clasificados = {}
    for g, tabla in group_tables.items():
        complete = "PJ" in tabla.columns and int(tabla["PJ"].sum()) == len(PARTIDOS_GRUPOS[g]) * 2
        if len(tabla) >= 2 and complete:
            clasificados[f"1{g[-1]}"] = tabla.iloc[0]["Equipo"]
            clasificados[f"2{g[-1]}"] = tabla.iloc[1]["Equipo"]

    return resolve_full_bracket_from_slots(clasificados, df_thirds, ko_data)
    
# --- INTERFAZ ---
st.set_page_config(page_title="Quiniela Pro Mundial 2026", layout="wide")
data = load_data()
predictions_locked = predictions_are_locked()

st.sidebar.title("🏆 Configuración")
user = st.sidebar.text_input("Tu Nombre de Jugador:")
admin_mode = st.sidebar.toggle("Modo Administrador (Resultados Oficiales)")

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
def UI_fase_eliminatoria(bracket_dict, storage_path, key_prefix, read_only=False):
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
                
                bloqueado = (
                    any(f in match["L_team"] for f in ["Por definir", "Mejor", "Esperando"])
                    or any(f in match["V_team"] for f in ["Por definir", "Mejor", "Esperando"])
                    or read_only
                )
                
                c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 1, 1, 3, 2])
                c1.write(f"**{match['L_team']}**")
                l_in = c2.number_input("", 0, 15, cur["l"], key=f"{key_prefix}_l_{m_id}", disabled=bloqueado, label_visibility="collapsed")
                c3.write("vs")
                v_in = c4.number_input("", 0, 15, cur["v"], key=f"{key_prefix}_v_{m_id}", disabled=bloqueado, label_visibility="collapsed")
                c5.write(f"**{match['V_team']}**")
                
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

def build_group_match_rows(group_name, group_results):
    rows = []
    for i, (local, visitante) in enumerate(PARTIDOS_GRUPOS[group_name]):
        m_id = f"{group_name}_{i}"
        result = group_results.get(m_id)
        if result:
            rows.append({
                "Grupo": group_name,
                "Partido": f"{local} vs {visitante}",
                "Resultado": f"{result['l']} - {result['v']}",
                "Estado": "Finalizado",
            })
        else:
            rows.append({
                "Grupo": group_name,
                "Partido": f"{local} vs {visitante}",
                "Resultado": "Pendiente",
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
                st.dataframe(pd.DataFrame(rows)[["Partido", "Resultado", "Estado"]], hide_index=True)
    else:
        rows = build_group_match_rows(selected_group, group_results)
        st.dataframe(pd.DataFrame(rows)[["Partido", "Resultado", "Estado"]], hide_index=True)

def UI_admin_group_results():
    st.subheader("Resultados Reales de Grupos")
    group_results = data["real_results"]["group_results"]
    g_adm = st.selectbox("Grupo Real:", list(PARTIDOS_GRUPOS.keys()), key="admin_group_results_group")

    with st.form("f_real_grp"):
        for i, (local, visitante) in enumerate(PARTIDOS_GRUPOS[g_adm]):
            m_id = f"{g_adm}_{i}"
            cur = group_results.get(m_id, {"l": 0, "v": 0})
            c0, c1, c2, c3, c4, c5 = st.columns([1.3, 3, 1, 0.7, 1, 3])
            c0.checkbox("Finalizado", value=m_id in group_results, key=f"r_played_{m_id}")
            c1.write(local)
            c2.number_input("", 0, 20, cur["l"], key=f"r_l_{m_id}", label_visibility="collapsed")
            c3.write("vs")
            c4.number_input("", 0, 20, cur["v"], key=f"r_v_{m_id}", label_visibility="collapsed")
            c5.write(visitante)

        if st.form_submit_button("Publicar Resultados Reales de Grupo"):
            for i, _ in enumerate(PARTIDOS_GRUPOS[g_adm]):
                m_id = f"{g_adm}_{i}"
                if st.session_state[f"r_played_{m_id}"]:
                    group_results[m_id] = {
                        "l": st.session_state[f"r_l_{m_id}"],
                        "v": st.session_state[f"r_v_{m_id}"],
                    }
                else:
                    group_results.pop(m_id, None)
            save_data(data)
            st.success("Datos oficiales guardados.")
            st.rerun()

def UI_prediccion_jugador(player_name, player_data, key_prefix):
    st.header(f"Predicción de {player_name}")
    st_p1, st_p2, st_p3 = st.tabs(["Fase de Grupos", "Fase Eliminatoria (Bracket)", "Bracket Oficial"])
    
    group_predictions = player_data.get("group_predictions", {})
    ko_predictions = player_data.get("ko_predictions", {})
    
    with st_p1:
        g_sel = st.selectbox("Selecciona un grupo:", list(PARTIDOS_GRUPOS.keys()), key=f"{key_prefix}_g_sel")
        for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_sel]):
            m_id = f"{g_sel}_{i}"
            cur = group_predictions.get(m_id, {"l": 0, "v": 0})
            c1, c2, c3, c4, c5 = st.columns([3,1,1,1,3])
            c1.write(l)
            c2.number_input("", 0, 20, cur["l"], key=f"{key_prefix}_l_{m_id}", disabled=True, label_visibility="collapsed")
            c3.write("vs")
            c4.number_input("", 0, 20, cur["v"], key=f"{key_prefix}_v_{m_id}", disabled=True, label_visibility="collapsed")
            c5.write(v)

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
        with st.form(f"form_user_{g_sel}"):
            for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_sel]):
                m_id = f"{g_sel}_{i}"
                cur = data["users"][user]["group_predictions"].get(m_id, {"l": 0, "v": 0})
                c1, c2, c3, c4, c5 = st.columns([3,1,1,1,3])
                c1.write(l); l_in = c2.number_input("", 0, 20, cur["l"], key=f"u_l_{m_id}", disabled=predictions_locked, label_visibility="collapsed")
                c3.write("vs"); v_in = c4.number_input("", 0, 20, cur["v"], key=f"u_v_{m_id}", disabled=predictions_locked, label_visibility="collapsed")
                c5.write(v)
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
        UI_prediccion_bracket_oficial(data["users"][user], "u_official_ko")

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
        st.subheader("🛠️ Panel de Carga de Datos Oficiales (Admin)")
        adm_mode_sel = st.radio("¿Qué deseas actualizar?", ["Resultados de Grupos", "Bracket Oficial R32", "Fase Eliminatoria"], key="admin_real_update_mode")
        
        if adm_mode_sel == "Resultados de Grupos":
            UI_admin_group_results()
        elif adm_mode_sel == "Bracket Oficial R32":
            UI_admin_official_r32()
        else:
            if not official_bracket_is_ready(data["real_results"].get("official_r32", {})):
                st.warning("Carga el bracket oficial R32 antes de publicar resultados de fase eliminatoria.")
            real_bracket = resolve_real_bracket(data["real_results"])
            UI_fase_eliminatoria(real_bracket, data["real_results"]["ko_results"], "r_ko")

    st.divider()

    real_view = st.radio(
        "Visualizar datos reales:",
        ["Partidos de Grupos", "Tablas de Posiciones", "Llave Eliminatoria"],
        horizontal=True,
        key="real_public_view",
    )
    r_tables, _, df_r_thirds = get_all_group_tables(data["real_results"]["group_results"])

    if real_view == "Partidos de Grupos":
        UI_real_group_results_view(data["real_results"]["group_results"])
    elif real_view == "Tablas de Posiciones":
        st.subheader("📊 Tablas de Posiciones Reales de la FIFA")
        cx2 = st.columns(3)
        for idx, g in enumerate(PARTIDOS_GRUPOS.keys()):
            with cx2[idx % 3]:
                st.write(f"**{g}**")
                st.dataframe(r_tables[g], hide_index=True)

        st.subheader("🥉 Tabla de Terceros por Marcadores")
        st.caption("La clasificación oficial de terceros puede depender de fair play y ranking FIFA; usa el bracket oficial R32 cargado por el administrador para la llave real.")
        st.dataframe(df_r_thirds[["Grupo", "Equipo", "Pts", "GD", "GF", "Avanza"]], hide_index=True)
    else:
        st.subheader("🌳 Llave de Eliminación Oficial Actualizada")
        real_bracket = resolve_real_bracket(data["real_results"])
        if official_bracket_is_ready(data["real_results"].get("official_r32", {})):
            st.caption("Usando el bracket oficial R32 cargado por el administrador.")
        else:
            st.caption("Bracket provisional calculado desde resultados de grupos hasta que el administrador cargue el bracket oficial R32.")
        st.success(f"🏆 CAMPEÓN REAL ACTUAL: {real_bracket['Campeon']}")
        UI_fase_eliminatoria(real_bracket, {}, "view_real_ko", read_only=True)

# ================= TAB 4: POSICIONES Y REGLAS =================
with t_puntos:
    st.header("🏆 Tabla de Clasificación de la Quiniela")

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
	    
    def calcular_puntos_totales(user_obj, real_obj):
        pts = 0
        u_grp = user_obj.get("group_predictions", {})
        r_grp = real_obj.get("group_results", {})
        for m_id, r_res in r_grp.items():
            if m_id in u_grp:
                pl, pv = u_grp[m_id]["l"], u_grp[m_id]["v"]
                rl, rv = r_res["l"], r_res["v"]
                if pl == rl and pv == rv: pts += 3
                elif (pl > pv and rl > rv) or (pl < pv and rl < rv) or (pl == pv and rl == rv): pts += 1

        u_tables, _, df_u_thirds = get_all_group_tables(u_grp)
        
        rb = resolve_real_bracket(real_obj)
        ub = resolve_full_bracket(u_tables, df_u_thirds, user_obj.get("ko_predictions", {}))
        pts += calcular_puntos_bracket(ub, rb)
        return pts

    def calcular_puntos_bracket_oficial(user_obj, real_obj):
        official_r32 = real_obj.get("official_r32", {})
        if not official_bracket_is_ready(official_r32):
            return 0

        rb = resolve_official_bracket(official_r32, real_obj.get("ko_results", {}))
        ub = resolve_official_bracket(official_r32, user_obj.get("official_bracket_predictions", {}))
        return calcular_puntos_bracket(ub, rb)
	
    ranking_full = []
    ranking_official = []
    for u_name, u_data in data["users"].items():
        ranking_full.append({"Jugador": u_name, "Puntos Totales": calcular_puntos_totales(u_data, data["real_results"])})
        ranking_official.append({"Jugador": u_name, "Puntos Bracket Oficial": calcular_puntos_bracket_oficial(u_data, data["real_results"])})
	        
    st.subheader("Predicción 1: Torneo Completo")
    if ranking_full:
        df_rank = pd.DataFrame(ranking_full).sort_values("Puntos Totales", ascending=False).reset_index(drop=True)
        df_rank.index += 1
        st.table(df_rank)
    else:
        st.info("No hay datos de jugadores aún.")

    st.subheader("Predicción 2: Bracket Oficial")
    if not official_bracket_is_ready(data["real_results"].get("official_r32", {})):
        st.info("El ranking del bracket oficial se activará cuando el administrador cargue el R32 oficial completo.")
    elif ranking_official:
        df_rank_official = pd.DataFrame(ranking_official).sort_values("Puntos Bracket Oficial", ascending=False).reset_index(drop=True)
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

    3. **En Fase de Grupos (Por Partido):**
       * **3 Puntos:** Resultado Exacto (Le acertaste al marcador idéntico).
       * **1 Punto:** Tendencia Correcta (Acertaste al ganador o al empate, pero con otro marcador).
       
    4. **En Fase Eliminatoria (Por Equipo Clasificado):**
       * **2 Puntos** por cada equipo que metas correctamente en **Octavos de Final** (R16).
       * **4 Puntos** por cada equipo que metas correctamente en **Cuartos de Final** (QF).
       * **8 Puntos** por cada equipo que metas correctamente en **Semifinales** (SF) y al **Tercer Puesto**.
       * **16 Puntos** por cada equipo que metas correctamente en la **Gran Final**.
       * **32 Puntos** adicionales si aciertas exactamente al **Campeón del Mundo**.
    """)
