# SMART-TRAFFIC Weekly Route Calendars (Both Configurations)
=============================================================

Đây là lịch trình chi tiết cho cả hai cấu hình chạy: **Lenient Time Windows** (Quy ước lỏng - xe chỉ cần đến trước hạn) và **Strict Time Windows** (Quy ước chặt - xe phải hoàn thành dỡ hàng trước hạn).

---

## 1. CONFIGURATION A: LENIENT TIME WINDOWS (Cấu hình lỏng)

### Shipper Shift Times (Lenient)
- **Monday:** 08:00 AM – 09:51 PM (Return time: 1311.0 mins)
- **Tuesday:** 08:00 AM – 09:48 PM (Return time: 1308.6 mins)
- **Wednesday:** 08:00 AM – 09:30 PM (Return time: 1290.6 mins)
- **Thursday:** 08:00 AM – 09:55 PM (Return time: 1315.7 mins)
- **Friday:** 08:00 AM – 09:48 PM (Return time: 1308.0 mins)
- **Saturday:** 08:00 AM – 04:57 PM (Return time: 1017.3 mins)
- **Sunday:** 08:00 AM – 02:27 PM (Return time: 867.0 mins)

### Route Calendar (Lenient)
| Day | Served Count | Route (Sequence of Visits) |
| --- | --- | --- |
| **Monday** | 53 | C228 -> C175 -> C252 -> C106 -> C184 -> C288 -> C057 -> C056 -> C171 -> C072 -> C251 -> C071 -> C112 -> C214 -> C061 -> C017 -> C055 -> C224 -> C033 -> C148 -> C284 -> C249 -> C218 -> C294 -> C053 -> C182 -> C134 -> C276 -> C122 -> C194 -> C205 -> C204 -> C297 -> C088 -> C233 -> C064 -> C012 -> C058 -> C065 -> C045 -> C040 -> C237 -> C019 -> C286 -> C290 -> C051 -> C031 -> C257 -> C114 -> C085 -> C155 -> C280 -> C009 |
| **Tuesday** | 61 | C008 -> C110 -> C054 -> C179 -> C107 -> C068 -> C005 -> C152 -> C216 -> C135 -> C231 -> C059 -> C030 -> C217 -> C229 -> C291 -> C069 -> C274 -> C161 -> C300 -> C176 -> C100 -> C203 -> C187 -> C269 -> C198 -> C073 -> C075 -> C271 -> C126 -> C032 -> C256 -> C238 -> C260 -> C160 -> C151 -> C039 -> C006 -> C025 -> C255 -> C063 -> C236 -> C001 -> C197 -> C120 -> C163 -> C127 -> C157 -> C168 -> C062 -> C090 -> C108 -> C131 -> C103 -> C132 -> C278 -> C050 -> C195 -> C177 -> C097 -> C028 |
| **Wednesday** | 38 | C201 -> C258 -> C186 -> C015 -> C245 -> C141 -> C041 -> C034 -> C003 -> C086 -> C013 -> C102 -> C078 -> C239 -> C038 -> C154 -> C167 -> C192 -> C129 -> C247 -> C264 -> C162 -> C060 -> C084 -> C115 -> C265 -> C139 -> C299 -> C208 -> C125 -> C014 -> C082 -> C244 -> C273 -> C099 -> C281 -> C211 -> C036 |
| **Thursday** | 50 | C140 -> C016 -> C227 -> C242 -> C215 -> C241 -> C052 -> C101 -> C092 -> C232 -> C285 -> C124 -> C046 -> C275 -> C223 -> C283 -> C166 -> C158 -> C081 -> C243 -> C150 -> C144 -> C044 -> C246 -> C266 -> C143 -> C206 -> C174 -> C096 -> C221 -> C010 -> C022 -> C089 -> C259 -> C191 -> C091 -> C007 -> C248 -> C235 -> C095 -> C298 -> C136 -> C165 -> C289 -> C149 -> C067 -> C111 -> C267 -> C210 -> C270 |
| **Friday** | 27 | C024 -> C002 -> C147 -> C156 -> C117 -> C296 -> C130 -> C230 -> C077 -> C119 -> C098 -> C183 -> C070 -> C268 -> C295 -> C180 -> C202 -> C137 -> C128 -> C076 -> C250 -> C287 -> C023 -> C170 -> C146 -> C181 -> C105 |
| **Saturday** | 42 | C169 -> C145 -> C209 -> C188 -> C049 -> C109 -> C037 -> C153 -> C138 -> C178 -> C066 -> C253 -> C207 -> C018 -> C123 -> C080 -> C172 -> C282 -> C093 -> C199 -> C254 -> C225 -> C004 -> C164 -> C047 -> C263 -> C185 -> C159 -> C087 -> C027 -> C116 -> C035 -> C094 -> C272 -> C026 -> C043 -> C226 -> C213 -> C222 -> C074 -> C220 -> C121 |
| **Sunday** | 27 | C011 -> C133 -> C212 -> C029 -> C293 -> C193 -> C262 -> C200 -> C079 -> C196 -> C240 -> C279 -> C020 -> C021 -> C292 -> C118 -> C261 -> C219 -> C104 -> C142 -> C042 -> C277 -> C113 -> C234 -> C190 -> C173 -> C189 |

### Missing/Unserved Customers (Lenient)
Out of 300 total customers, **2** could not be served:
- **C048** (遠 - Far from depot ~24 km; available on busy days Mon/Thu)
- **C083** (Time window late evening 18:30–21:30 overlaps with Thursday/Friday tight schedules)

---

## 2. CONFIGURATION B: STRICT TIME WINDOWS (Cấu hình chặt)

### Shipper Shift Times (Strict)
- **Monday:** 08:00 AM – 09:21 PM (Return time: 1281.0 mins)
- **Tuesday:** 08:00 AM – 09:12 PM (Return time: 1272.2 mins)
- **Wednesday:** 08:00 AM – 09:21 PM (Return time: 1281.3 mins)
- **Thursday:** 08:00 AM – 08:44 PM (Return time: 1243.6 mins)
- **Friday:** 08:00 AM – 08:52 PM (Return time: 1251.5 mins)
- **Saturday:** 08:00 AM – 09:15 PM (Return time: 1275.2 mins)
- **Sunday:** 08:00 AM – 09:11 PM (Return time: 1271.3 mins)

### Route Calendar (Strict)
| Day | Served Count | Route (Sequence of Visits) |
| --- | --- | --- |
| **Monday** | 52 | C175 -> C228 -> C247 -> C110 -> C174 -> C206 -> C107 -> C179 -> C005 -> C143 -> C119 -> C144 -> C150 -> C135 -> C216 -> C152 -> C243 -> C291 -> C265 -> C158 -> C166 -> C178 -> C063 -> C154 -> C167 -> C187 -> C129 -> C236 -> C059 -> C081 -> C030 -> C115 -> C197 -> C180 -> C261 -> C139 -> C299 -> C120 -> C142 -> C014 -> C049 -> C062 -> C234 -> C270 -> C188 -> C108 -> C125 -> C210 -> C202 -> C132 -> C209 -> C267 |
| **Tuesday** | 59 | C269 -> C231 -> C162 -> C229 -> C274 -> C176 -> C203 -> C198 -> C008 -> C148 -> C245 -> C294 -> C122 -> C276 -> C141 -> C284 -> C015 -> C033 -> C017 -> C003 -> C112 -> C013 -> C102 -> C073 -> C255 -> C025 -> C161 -> C006 -> C021 -> C183 -> C215 -> C256 -> C260 -> C160 -> C151 -> C032 -> C126 -> C271 -> C075 -> C300 -> C039 -> C238 -> C295 -> C165 -> C136 -> C123 -> C097 -> C253 -> C028 -> C278 -> C169 -> C051 -> C181 -> C211 -> C040 -> C170 -> C114 -> C085 -> C280 |
| **Wednesday** | 49 | C288 -> C056 -> C061 -> C086 -> C224 -> C218 -> C053 -> C182 -> C134 -> C034 -> C297 -> C041 -> C186 -> C258 -> C252 -> C106 -> C184 -> C201 -> C264 -> C044 -> C060 -> C084 -> C068 -> C192 -> C217 -> C069 -> C100 -> C078 -> C171 -> C071 -> C204 -> C205 -> C194 -> C146 -> C237 -> C023 -> C287 -> C257 -> C031 -> C250 -> C009 -> C011 -> C116 -> C027 -> C262 -> C263 -> C200 -> C036 -> C189 |
| **Thursday** | 43 | C140 -> C057 -> C055 -> C214 -> C251 -> C072 -> C016 -> C227 -> C242 -> C052 -> C241 -> C232 -> C285 -> C124 -> C046 -> C275 -> C223 -> C283 -> C096 -> C054 -> C246 -> C077 -> C022 -> C010 -> C221 -> C092 -> C101 -> C239 -> C038 -> C067 -> C111 -> C149 -> C289 -> C298 -> C095 -> C235 -> C248 -> C007 -> C091 -> C089 -> C168 -> C099 -> C281 |
| **Friday** | 22 | C230 -> C130 -> C296 -> C117 -> C156 -> C147 -> C002 -> C249 -> C024 -> C070 -> C098 -> C163 -> C001 -> C190 -> C131 -> C137 -> C173 -> C128 -> C083 -> C076 -> C233 -> C272 |
| **Saturday** | 46 | C145 -> C207 -> C018 -> C199 -> C254 -> C225 -> C004 -> C164 -> C282 -> C093 -> C172 -> C191 -> C080 -> C259 -> C066 -> C138 -> C177 -> C050 -> C195 -> C103 -> C090 -> C153 -> C208 -> C037 -> C127 -> C157 -> C109 -> C266 -> C220 -> C121 -> C074 -> C213 -> C222 -> C159 -> C185 -> C047 -> C087 -> C226 -> C065 -> C043 -> C026 -> C155 -> C094 -> C035 -> C290 -> C105 |
| **Sunday** | 27 | C113 -> C082 -> C244 -> C273 -> C277 -> C042 -> C104 -> C219 -> C118 -> C292 -> C020 -> C279 -> C240 -> C196 -> C079 -> C193 -> C012 -> C293 -> C064 -> C029 -> C212 -> C133 -> C088 -> C058 -> C045 -> C019 -> C286 |

### Missing/Unserved Customers (Strict)
Out of 300 total customers, **2** could not be served:
- **C048**
- **C083**
