from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
    make_response,
)
from . import profile


def login_required():
    if "username" in session:
        return None

    flash("Please log in to open your profile.", "danger")
    return redirect(url_for("auth.login"))


def visible_cookies() -> list[dict[str, str]]:
    return [{"key": key, "value": value} for key, value in request.cookies.items()]


@profile.get("/profile")
def profile_func():
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    return render_template(
        "profile.html",
        title="Profile",
        username=session["username"],
        cookies=visible_cookies(),
        theme=request.cookies.get("color_scheme", "light"),
    )


@profile.post("/profile/cookies/add")
def add_cookie():
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    key = request.form.get("cookie_key", "").strip()
    value = request.form.get("cookie_value", "").strip()
    expiry_minutes_raw = request.form.get("expiry_minutes", "").strip()

    if not key:
        flash("Cookie key is required.", "danger")
        return redirect(url_for("profile.profile_func"))

    if key == current_app.config["SESSION_COOKIE_NAME"]:
        flash("This cookie key is reserved by Flask sessions.", "danger")
        return redirect(url_for("profile.profile_func"))

    try:
        expiry_minutes = int(expiry_minutes_raw)
        if expiry_minutes <= 0:
            raise ValueError
    except ValueError:
        flash("Expiry time must be a positive number of minutes.", "danger")
        return redirect(url_for("profile.profile_func"))

    response = make_response(redirect(url_for("profile.profile_func")))
    response.set_cookie(
        key,
        value,
        max_age=expiry_minutes * 60,
        httponly=False,
        samesite="Lax",
    )
    flash(f'Cookie "{key}" was added.', "success")
    return response


@profile.post("/profile/cookies/delete")
def delete_cookie():
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    key = request.form.get("cookie_key", "").strip()
    if not key:
        flash("Enter a cookie key to delete.", "danger")
        return redirect(url_for("profile.profile_func"))

    if key not in request.cookies:
        flash(f'Cookie "{key}" was not found.', "warning")
        return redirect(url_for("profile.profile_func"))

    response = make_response(redirect(url_for("profile.profile_func")))
    response.delete_cookie(key)
    flash(f'Cookie "{key}" was removed.', "success")
    return response


@profile.post("/profile/cookies/clear")
def clear_cookies():
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    response = make_response(redirect(url_for("profile.profile_func")))
    removed_any = False
    session_cookie = current_app.config["SESSION_COOKIE_NAME"]
    for key in request.cookies.keys():
        if key == session_cookie:
            continue
        response.delete_cookie(key)
        removed_any = True

    if removed_any:
        flash("All custom cookies were removed.", "success")
    else:
        flash("There are no custom cookies to remove.", "info")
    return response


@profile.get("/theme/<scheme>")
def set_theme(scheme: str):
    redirect_response = login_required()
    if redirect_response is not None:
        return redirect_response

    if scheme not in current_app.config["SUPPORTED_THEMES"]:
        flash("Unknown color scheme.", "danger")
        return redirect(url_for("profile.profile_func"))

    response = make_response(redirect(url_for("profile.profile_func")))
    response.set_cookie(
        "color_scheme", scheme, max_age=30 * 24 * 60 * 60, samesite="Lax"
    )
    flash(f"{scheme.title()} theme enabled.", "success")
    return response
