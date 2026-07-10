# SMART-TRAFFIC Weekly Route Calendar
=====================================

Đây là lịch trình chi tiết cho cấu hình chạy chuẩn của dự án: **Strict Time Windows** (Quy ước chặt - xe phải hoàn thành dỡ hàng trước hạn). Giải thuật Greedy kết hợp Local Search và Repair Operator (Ejection Chain) đã thành công lập lịch cho toàn bộ 300/300 khách hàng.

---

## 1. Shipper Shift Times
- **Monday:** 08:00 AM – 09:42 PM (Return time: 1302.6 mins)
- **Tuesday:** 08:00 AM – 09:41 PM (Return time: 1301.2 mins)
- **Wednesday:** 08:00 AM – 09:31 PM (Return time: 1291.8 mins)
- **Thursday:** 08:00 AM – 09:42 PM (Return time: 1302.1 mins)
- **Friday:** 08:00 AM – 09:43 PM (Return time: 1303.0 mins)
- **Saturday:** 08:00 AM – 05:58 PM (Return time: 1078.9 mins)
- **Sunday:** 08:00 AM – 02:38 PM (Return time: 878.5 mins)

## 2. Route Calendar
| Day | Served Count | Route (Sequence of Visits) |
| --- | --- | --- |
| **Monday** | 48 | DEPOT -> C048 -> C175 -> C228 -> C247 -> C110 -> C174 -> C206 -> C107 -> C179 -> C005 -> C143 -> C119 -> C144 -> C150 -> C135 -> C216 -> C152 -> C243 -> C291 -> C265 -> C158 -> C166 -> C178 -> C063 -> C154 -> C167 -> C187 -> C129 -> C236 -> C059 -> C081 -> C268 -> C197 -> C180 -> C261 -> C139 -> C299 -> C120 -> C142 -> C014 -> C049 -> C062 -> C234 -> C270 -> C188 -> C108 -> C125 -> C210 -> DEPOT |
| **Tuesday** | 60 | DEPOT -> C030 -> C269 -> C231 -> C162 -> C229 -> C274 -> C176 -> C203 -> C198 -> C008 -> C148 -> C245 -> C294 -> C122 -> C276 -> C141 -> C284 -> C015 -> C033 -> C017 -> C003 -> C112 -> C013 -> C102 -> C073 -> C255 -> C025 -> C161 -> C006 -> C021 -> C183 -> C215 -> C256 -> C260 -> C160 -> C151 -> C032 -> C126 -> C271 -> C075 -> C300 -> C039 -> C238 -> C295 -> C165 -> C136 -> C123 -> C097 -> C253 -> C028 -> C278 -> C169 -> C051 -> C181 -> C211 -> C040 -> C170 -> C114 -> C085 -> C280 -> DEPOT |
| **Wednesday** | 50 | DEPOT -> C115 -> C288 -> C056 -> C061 -> C086 -> C224 -> C218 -> C053 -> C182 -> C134 -> C034 -> C297 -> C041 -> C186 -> C258 -> C252 -> C106 -> C184 -> C201 -> C264 -> C044 -> C060 -> C084 -> C068 -> C192 -> C217 -> C069 -> C100 -> C078 -> C171 -> C071 -> C204 -> C205 -> C194 -> C146 -> C237 -> C023 -> C287 -> C257 -> C031 -> C250 -> C009 -> C011 -> C116 -> C027 -> C262 -> C263 -> C200 -> C036 -> C189 -> DEPOT |
| **Thursday** | 43 | DEPOT -> C140 -> C057 -> C055 -> C214 -> C251 -> C072 -> C016 -> C227 -> C242 -> C052 -> C241 -> C232 -> C285 -> C124 -> C046 -> C275 -> C223 -> C283 -> C096 -> C054 -> C246 -> C077 -> C022 -> C010 -> C221 -> C092 -> C101 -> C239 -> C038 -> C067 -> C111 -> C149 -> C289 -> C298 -> C095 -> C235 -> C248 -> C007 -> C091 -> C089 -> C168 -> C099 -> C281 -> DEPOT |
| **Friday** | 23 | DEPOT -> C230 -> C130 -> C296 -> C117 -> C156 -> C147 -> C002 -> C249 -> C024 -> C070 -> C098 -> C163 -> C001 -> C202 -> C190 -> C131 -> C137 -> C173 -> C128 -> C083 -> C076 -> C233 -> C272 -> DEPOT |
| **Saturday** | 48 | DEPOT -> C209 -> C132 -> C145 -> C207 -> C018 -> C199 -> C254 -> C225 -> C004 -> C164 -> C282 -> C093 -> C172 -> C191 -> C080 -> C259 -> C066 -> C138 -> C177 -> C050 -> C195 -> C103 -> C090 -> C153 -> C208 -> C037 -> C127 -> C157 -> C109 -> C266 -> C220 -> C121 -> C074 -> C213 -> C222 -> C159 -> C185 -> C047 -> C087 -> C226 -> C065 -> C043 -> C026 -> C155 -> C094 -> C035 -> C290 -> C105 -> DEPOT |
| **Sunday** | 28 | DEPOT -> C267 -> C113 -> C082 -> C244 -> C273 -> C277 -> C042 -> C104 -> C219 -> C118 -> C292 -> C020 -> C279 -> C240 -> C196 -> C079 -> C193 -> C012 -> C293 -> C064 -> C029 -> C212 -> C133 -> C088 -> C058 -> C045 -> C019 -> C286 -> DEPOT |

## 3. Missing/Unserved Customers
Out of 300 total customers, **0** could not be served. All deliveries successfully completed!
