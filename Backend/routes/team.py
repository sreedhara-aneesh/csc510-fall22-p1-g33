from flask import Blueprint
from flask import request
from ..extensions import db
from ..models.all import Team, Teamabout, Project, User
from flask import jsonify

team = Blueprint('team', __name__)

@team.route('/', methods=['POST'])
def post_team():
    args = request.get_json()
    creator = args['creator']
    project = args['project']

    u = User.query.filter_by(id=creator).first()
    if u is None:
        return 'Not Found', 404
    p = Project.query.filter_by(id=project).first()
    if p is None:
        return 'Not Found', 404
    
    t = Team(project_id=p.id, filled=False)
    db.session.add(t)
    db.session.commit()

    ta = Teamabout(team_id=t.id, name='Unnamed Team', description='No description.')
    db.session.add(ta)
    db.session.commit()

    t = Team.query.filter_by(id=t.id).first()
    t.users.append(u)
    db.session.add(t)
    db.session.commit()

    return jsonify({ "id": t.id }), 201
@team.route('/<id>', methods=['GET'])
def get_team_id(id):
    t = Team.query.filter_by(id=id).first()
    if t is None:
        return 'Not Found', 404

    ta = Teamabout.query.filter_by(team_id=t.id).first()
    ret = {
        "team": {
            "id": str(t.id),
            "users": list(map(lambda u: str(u.id), t.users)),
            "project": str(t.project.id),
            "about": {
                "name": str(ta.name),
                "description": str(ta.description)
            }
        }
    }
    return jsonify(ret), 200

@team.route('/<id>', methods=['DELETE'])
def delete_team_id(id):
    # TODO: Remove this route and move deletion logic to user removal
    # ALERT: YOU SHOULD NOT BE CALLING THIS IN NORMAL USE
    # DELETION OCCURS WHEN LAST USER IS REMOVED, AUTOMATICALLY
    t = Team.query.filter_by(id=id).first()
    if t is None:
        return f'Not Found', 404
    db.session.delete(t)
    db.session.commit()
    return 'OK', 200

# @team.route('/<id>/users/add', methods=['PATCH'])
# def patch_project_id_users_add(id):
#     p = Project.query.filter_by(id=id).first()
#     if p is None:
#         return f'Not Found', 404
#     args = request.get_json()
#     uid = args['user_id']
#     u = User.query.filter_by(id=uid).first()
#     if u is None:
#         return f'Not Found', 404
#     p.users.append(u)
#     db.session.add(p)
#     db.session.commit()
#     return 'OK', 200

@team.route('/<id>/users/remove', methods=['PATCH'])
def patch_team_id_users_remove(id):
    # ALERT: THIS DELETES THE PROJECT IF NO USERS ARE LEFT.
    t = Team.query.filter_by(id=id).first()
    if t is None:
        return f'Not Found', 404
    args = request.get_json()
    uid = args['user_id']
    u = User.query.filter_by(id=uid).first()
    if u is None or u not in t.users:
        return f'Not Found', 404
    t.users.remove(u)
    db.session.add(t)
    db.session.commit()
    # TODO: redo deletion thing, looks sketchy
    t = Team.query.filter_by(id=id).first()
    if len(t.users) == 0:
        delete_team_id(id)
    return 'OK', 200

@team.route('/<id>/about', methods=['PATCH'])
def patch_team_id_about(id):
    t = Team.query.filter_by(id=id).first()
    if t is None:
        return f'Not Found', 404
    args = request.get_json()
    ta = t.about
    ta.name = args['name']
    ta.description = args['description']
    db.session.add(ta)
    db.session.commit()
    return 'OK', 200

@team.route('/<id>/filled', methods=['PATCH'])
def patch_team_id_filled(id):
    return 'Not Implemented', 501