# SMART-TRAFFIC Weekly Route Calendar
=====================================

## Shipper Shift Times
The shipper departs from the central `DEPOT` at **08:00 AM** (minute 480.0 when windows open). The shift end time represents the vehicle's return to the central depot after completing all daily deliveries:
- **Monday:** 08:00 AM – 09:51 PM (Return time: 1311.0 mins)
- **Tuesday:** 08:00 AM – 09:48 PM (Return time: 1308.6 mins)
- **Wednesday:** 08:00 AM – 09:30 PM (Return time: 1290.6 mins)
- **Thursday:** 08:00 AM – 09:55 PM (Return time: 1315.7 mins)
- **Friday:** 08:00 AM – 09:48 PM (Return time: 1308.0 mins)
- **Saturday:** 08:00 AM – 04:57 PM (Return time: 1017.3 mins)
- **Sunday:** 08:00 AM – 02:27 PM (Return time: 867.0 mins)


## Route Calendar
| Day | Served Customers Count | Route (Sequence of Visits) |
| --- | --- | --- |
| **Monday** | 53 | C228 -> C175 -> C252 -> C106 -> C184 -> C288 -> C057 -> C056 -> C171 -> C072 -> C251 -> C071 -> C112 -> C214 -> C061 -> C017 -> C055 -> C224 -> C033 -> C148 -> C284 -> C249 -> C218 -> C294 -> C053 -> C182 -> C134 -> C276 -> C122 -> C194 -> C205 -> C204 -> C297 -> C088 -> C233 -> C064 -> C012 -> C058 -> C065 -> C045 -> C040 -> C237 -> C019 -> C286 -> C290 -> C051 -> C031 -> C257 -> C114 -> C085 -> C155 -> C280 -> C009 |
| **Tuesday** | 61 | C008 -> C110 -> C054 -> C179 -> C107 -> C068 -> C005 -> C152 -> C216 -> C135 -> C231 -> C059 -> C030 -> C217 -> C229 -> C291 -> C069 -> C274 -> C161 -> C300 -> C176 -> C100 -> C203 -> C187 -> C269 -> C198 -> C073 -> C075 -> C271 -> C126 -> C032 -> C256 -> C238 -> C260 -> C160 -> C151 -> C039 -> C006 -> C025 -> C255 -> C063 -> C236 -> C001 -> C197 -> C120 -> C163 -> C127 -> C157 -> C168 -> C062 -> C090 -> C108 -> C131 -> C103 -> C132 -> C278 -> C050 -> C195 -> C177 -> C097 -> C028 |
| **Wednesday** | 38 | C201 -> C258 -> C186 -> C015 -> C245 -> C141 -> C041 -> C034 -> C003 -> C086 -> C013 -> C102 -> C078 -> C239 -> C038 -> C154 -> C167 -> C192 -> C129 -> C247 -> C264 -> C162 -> C060 -> C084 -> C115 -> C265 -> C139 -> C299 -> C208 -> C125 -> C014 -> C082 -> C244 -> C273 -> C099 -> C281 -> C211 -> C036 |
| **Thursday** | 50 | C140 -> C016 -> C227 -> C242 -> C215 -> C241 -> C052 -> C101 -> C092 -> C232 -> C285 -> C124 -> C046 -> C275 -> C223 -> C283 -> C166 -> C158 -> C081 -> C243 -> C150 -> C144 -> C044 -> C246 -> C266 -> C143 -> C206 -> C174 -> C096 -> C221 -> C010 -> C022 -> C089 -> C259 -> C191 -> C091 -> C007 -> C248 -> C235 -> C095 -> C298 -> C136 -> C165 -> C289 -> C149 -> C067 -> C111 -> C267 -> C210 -> C270 |
| **Friday** | 27 | C024 -> C002 -> C147 -> C156 -> C117 -> C296 -> C130 -> C230 -> C077 -> C119 -> C098 -> C183 -> C070 -> C268 -> C295 -> C180 -> C202 -> C137 -> C128 -> C076 -> C250 -> C287 -> C023 -> C170 -> C146 -> C181 -> C105 |
| **Saturday** | 42 | C169 -> C145 -> C209 -> C188 -> C049 -> C109 -> C037 -> C153 -> C138 -> C178 -> C066 -> C253 -> C207 -> C018 -> C123 -> C080 -> C172 -> C282 -> C093 -> C199 -> C254 -> C225 -> C004 -> C164 -> C047 -> C263 -> C185 -> C159 -> C087 -> C027 -> C116 -> C035 -> C094 -> C272 -> C026 -> C043 -> C226 -> C213 -> C222 -> C074 -> C220 -> C121 |
| **Sunday** | 27 | C011 -> C133 -> C212 -> C029 -> C293 -> C193 -> C262 -> C200 -> C079 -> C196 -> C240 -> C279 -> C020 -> C021 -> C292 -> C118 -> C261 -> C219 -> C104 -> C142 -> C042 -> C277 -> C113 -> C234 -> C190 -> C173 -> C189 |

## Missing/Unserved Customers
-----------------------------
Out of 300 total customers, **2** could not be served within the physical constraints and planning period.

The following customers are missing from the traffic routes:
- **C048** (Coordinates: 14.4918, 18.9853 | Demand: 1.2)
  - *Time Windows:* Monday (08:30–11:30, 13:30–17:00), Thursday (08:30–11:30, 13:30–17:00)
  - *Reason for Omission:* C048 is located far from the depot (~24 km, requiring a 28-min one-way trip) and its only available delivery days (Monday and Thursday) are the two busiest days of the week (53 and 50 scheduled stops respectively). Detouring to serve C048 would cause subsequent time-window violations for multiple other customers.
- **C083** (Coordinates: 19.5498, -17.1281 | Demand: 1.3)
  - *Time Windows:* Thursday (18:30–21:30), Friday (18:30–21:30)
  - *Reason for Omission:* C083 only permits evening deliveries starting at 06:30 PM. However, the shipper completes all other deliveries and returns to the central depot much earlier (05:10 PM on Thursday and 01:40 PM on Friday). Serving C083 would force the shipper to remain idle for hours, violating the waiting time optimization limits.

