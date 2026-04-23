# Lab 6

to init db use this command:
```
python -c "from app import app, db; ctx = app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
```