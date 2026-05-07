## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask db upgrade
python run.py
```

## Add genres in `flask shell`

```python
from app import db
from app.books.models import Genre

db.session.add_all(
    [
        Genre(name="Fantasy", shelf_code="FAN-1", description="Fantasy books and adventures"),
        Genre(name="Science Fiction", shelf_code="SCI-2", description="Science fiction and futuristic stories"),
        Genre(name="Detective", shelf_code="DET-3", description="Mystery, crime, and detective fiction"),
    ]
)
db.session.commit()
```
