# TOON Prompt Header (Short)

Rules:
- Objects: `{k1,k2|v1|v2}` (keys list, then values list)
- Arrays: `[v1|v2|v3]`
- Tables (uniform dicts): `^csv[k1,k2|r1c1,r1c2|r2c1,r2c2]`
- Strings are quoted only when needed

Examples:
- `{"name":"Alice","age":30}` -> `{name,age|Alice|30}`
- `[1,2,3]` -> `[1|2|3]`
- `[{"id":1,"name":"A"},{"id":2,"name":"B"}]` -> `^csv[id,name|1,A|2,B]`
