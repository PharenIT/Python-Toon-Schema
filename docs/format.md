# Encoding Rules (Compact TOON)

## Objects

Objects are encoded with a key list and value list:

Input:
```json
{"name": "Alice", "age": 30}
```
Output:
```
{name,age|Alice|30}
```

## Arrays

Arrays are pipe-delimited:

Input:
```json
[1, 2, 3]
```
Output:
```
[1|2|3]
```

## Tabular Arrays (uniform dicts)

Input:
```json
[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
```
Output:
```
^csv[id,name|1,A|2,B]
```

## Mixed Arrays

Input:
```json
[{"x": 1}, 42, "hi"]
```
Output:
```
[{x|1}|42|hi]
```

## Primitive Values

Primitives are emitted as-is with minimal quoting.
Quotes are used only when necessary: whitespace, empty strings, reserved tokens,
numeric ambiguity, or delimiter characters.
