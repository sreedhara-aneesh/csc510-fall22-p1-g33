from flask import Blueprint
from flask import request
from ..extensions import db
from ..models.all import Project, Projectabout, User
from flask import jsonify

project = Blueprint('project', __name__)

@project.route('/query', methods=['GET'])
def get_project_query():
    ps = list(map(lambda p: str(p.id), Project.query.all()))
    return jsonify({'projects': [] + ps}), 200

@project.route('/dashboard', methods=['GET'])
def get_dashboard():
    ps = list(map(lambda p: (p.id, p.about.name, p.users), Project.query.all()))
    # print (ps[0][1][0].id)
    entries = []
    for p in ps:
        print(p)
        uname_list = []
        for u in p[2]:
            print (u.id)
            user_ = User.query.filter_by(id=u.id).first()
            uname_list.append ((user_.id, user_.username))
        print (uname_list)
        obj = {
            'pid': p[0],
            'pname': p[1],
            'user_list': uname_list
        }
        entries.append (obj)


   
    return jsonify(entries), 200

@project.route('/', methods=['POST'])
def post_project():
    print (request)
    args = request.get_json()
    creator = args['creator']
    project_name = args['name']
    project_desc = args['description']

    print ("POST Project:", creator, project_name, project_desc)

    u = User.query.filter_by(id=creator).first()
    if u is None:
        return 'Not Found', 404

    p = Project()
    db.session.add(p)
    db.session.commit()
    
    pa = Projectabout(project_id=p.id, name=project_name, description=project_desc)
    db.session.add(pa)
    db.session.commit()

    p = Project.query.filter_by(id=p.id).first()
    p.users.append(u)
    db.session.add(p)
    db.session.commit()

    return jsonify({ "id": p.id }), 201

@project.route('/<id>', methods=['GET'])
def get_project_id(id):
    p = Project.query.filter_by(id=id).first()
    if p is None:
        return f'Not Found', 404
    pa = Projectabout.query.filter_by(project_id=p.id).first()
    ret = {
        "project": {
            "id": str(p.id),
            "users": list(map(lambda u: str(u.id), p.users)),
            "teams": list(map(lambda t: str(t.id), p.teams)),
            "about": {
                "name": str(pa.name),
                "description": str(pa.description)
            }
        }
    }
    return jsonify(ret), 200

@project.route('/<id>', methods=['DELETE'])
def delete_project_id(id):
    # TODO: Remove this route and move deletion logic to user removal
    # ALERT: YOU SHOULD NOT BE CALLING THIS IN NORMAL USE
    # DELETION OCCURS WHEN LAST USER IS REMOVED, AUTOMATICALLY
    p = Project.query.filter_by(id=id).first()
    if p is None:
        return f'Not Found', 404
    db.session.delete(p)
    db.session.commit()
    return 'OK', 200

@project.route('/<id>/users/add', methods=['PATCH'])
def patch_project_id_users_add(id):
    p = Project.query.filter_by(id=id).first()
    if p is None:
        return f'Not Found', 404
    args = request.get_json()
    uid = args['user_id']
    u = User.query.filter_by(id=uid).first()
    if u is None:
        return f'Not Found', 404
    p.users.append(u)
    db.session.add(p)
    db.session.commit()
    return 'OK', 200

@project.route('/<id>/users/remove', methods=['PATCH'])
def patch_project_id_users_remove(id):
    # ALERT: THIS DELETES THE PROJECT IF NO USERS ARE LEFT.
    p = Project.query.filter_by(id=id).first()
    if p is None:
        return f'Not Found', 404
    args = request.get_json()
    uid = args['user_id']
    u = User.query.filter_by(id=uid).first()
    if u is None or u not in p.users:
        return f'Not Found', 404
    p.users.remove(u)
    db.session.add(p)
    db.session.commit()
    # TODO: redo deletion thing, looks sketchy
    p = Project.query.filter_by(id=id).first()
    if len(p.users) == 0:
        delete_project_id(id)
    return 'OK', 200

@project.route('/<id>/about', methods=['PATCH'])
def patch_project_id_about(id):
    p = Project.query.filter_by(id=id).first()
    if p is None:
        return f'Not Found', 404
    args = request.get_json()
    pa = p.about
    pa.name = args['name']
    pa.description = args['description']
    db.session.add(pa)
    db.session.commit()
    return 'OK', 200