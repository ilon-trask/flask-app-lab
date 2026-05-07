from flask import session


def _session_key(form_name: str) -> str:
    return f"_form_state_{form_name}"


def stash_form_state(
    form_name: str,
    form,
    *,
    exclude_fields: set[str] | None = None,
) -> None:
    excluded = set(exclude_fields or set())
    excluded.add("csrf_token")

    session[_session_key(form_name)] = {
        "data": {
            field_name: field.data
            for field_name, field in form._fields.items()
            if field_name not in excluded
        },
        "errors": {
            field_name: list(field.errors)
            for field_name, field in form._fields.items()
            if field_name not in excluded and field.errors
        },
    }


def restore_form_state(form_name: str, form):
    state = session.pop(_session_key(form_name), None)
    if not state:
        return form

    form.process(data=state.get("data", {}))

    for field_name, errors in state.get("errors", {}).items():
        if field_name in form._fields:
            form._fields[field_name].errors = list(errors)

    return form
