# Connecting to the DB from jupyter

```python
import pandas as pd
```

Don't run this cell twice or you change the path again:

```python
import os
os.chdir("../")
from models.base import get_session
```

```python
session = get_session()
```

### Executing a SQL query

```python
query = "SELECT * FROM PAPER"
```

```python
df = pd.read_sql(query, session.bind)
```

```python
df
```
