# Test Auto-Linting

This is a test file with deliberate markdown violations:

## Bad heading without proper spacing

Missing language in code block:

```python
def test():

```
return "hello world"

```

```yaml

Bad table formatting:

| column1 | column2 | column3 |
| --- | --- | --- |
| data | more data | final data |

Bare URL: <https://github.com/user/repo>

```text
Indented code block instead of fenced

```

## Emphasized text used as heading
