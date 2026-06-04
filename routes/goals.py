from flask import Blueprint, request, redirect

from core.storage import load_data, save_data

goals_bp = Blueprint("goals", __name__)

@goals_bp.route("/add_goal", methods=["POST"])
def add_goal():

    data = load_data()

    name = request.form.get("name")
    target = float(request.form.get("target", 0))

    if target <= 0:
        return redirect("/")

    data["goals"].append({
        "name": name,
        "target": target,
        "saved": 0
    })

    save_data(data)

    return redirect("/")
