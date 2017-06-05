from flask import jsonify
import os
from flask import Flask
from flask import send_file,make_response, redirect, url_for
import json



if os.path.isfile('config.py'):
    path_config = 'config.py'
elif os.path.isfile('default_config.py'):
    path_config = 'default_config.py'


try:
    from api.config import configure_app

except:
    from api.default_config import configure_app


app = Flask(__name__)

@app.route('/threads', methods=['GET'])
def get_threads():
    d=[{'prova1':'provando1', 'prova2':'provando2'}]
    json_d = json.dumps(d)

    return jsonify(threads=json_d), 200

@app.route('/viewer/zipvv/fromuser/<string:user>')
def download_vvs_fom_user(user):
    return redirect('/viewer/zipvv/fromuser/{}/vv.zip'.format(user))

@app.route('/viewer/zipvv/fromuser/<string:user>/vv.zip')
def download_vvs_fom_user_with_zip_name(user):
    domains = app.db.get_domains_from_user(user,status='Started')
    output_file = app.f.create_zip_vv(domains)
    return send_file(output_file,
                     as_attachment=True,
                     attachment_filename='vv_{}.zip'.format(user),
                     mimetype='application/zip')
    # return Response(r.content,
    #                 mimetype='application/zip',
    #                 headers={'Content-Disposition': 'attachment;filename=zones.zip'})
    pass




@app.route('/create_domain/bulk_to_user/<string:username>/<string:template_id>/<int:quantity>/<string:prefix>', methods=['GET'])
def create_domain_bulk(username, template_id, quantity, prefix):
    print(template_id)
    for n in range(quantity):
        suffix = str(n).zfill(2)
        app.db.create_domain_from_template(template_id, '{}_{}'.format(prefix,suffix), username,
                                       batch_create_id=prefix)
    return 'ok'

@app.route('/user/<string:user>/domains-batch/<string:batch_create_id>/start')
def start_domains_from_user(user,batch_create_id):
    for id in app.db.get_domains_from_user(user,status='Stopped',batch_create_id=batch_create_id):
        app.db.update_domain_status('Starting',id)

@app.route('/user/<string:user>/domains-batch/<string:batch_create_id>/stop')
def stop_domains_from_user(user,batch_create_id):
    for id in app.db.get_domains_from_user(user,status='Started',batch_create_id=batch_create_id):
        app.db.update_domain_status('Stopping',id)

@app.route('/create_domain/bulk_random_to_user/<string:username>/<int:quantity>/<string:prefix>', methods=['POST'])
def create_domain_bulk_random_to_user():
    pass


@app.route('/create_domain/to_user/<string:username>/<string:template_id>/<string:domain_id>', methods=['POST'])
def create_domain_bulk_to_user():
    pass

@app.route('/create_domain/to_group/<string:group>/<string:template_id>/<int:quantity>/<string:prefix>', methods=['POST'])
def create_domain_to_group():
    pass


@app.route('/action_with_domain/<string:action>/<string:domain_id>', methods=['PUT'])
def start_domain():
    pass


@app.route('/action_with_domains_group_by/<string:groupby>/<string:action>/with_prefix/<string:prefix>', methods=['PUT'])
def action_with_domains_group_by():
    pass


@app.route('/action_with_domains/<string:action>/from_user/<string:username>', methods=['PUT'])
def start_domain_with_prefix():
    pass


@app.route('/action_with_domains/<string:action>/from_template/<string:template>', methods=['PUT'])
def start_domain_with_prefix_from_template():
    pass

@app.route('/viewer/vv/<string:domain_id>')
def download_vv(domain_id):
    pass






@app.route('/engine_info', methods=['GET'])
def engine_info():
    d_engine = {}
    if app.m.t_background.is_alive():
        d_engine['is_alive'] = True
        d_engine['event_thread_is_alive'] = app.m.t_events.is_alive()
        d_engine['broom_thread_is_alive'] = app.m.t_broom.is_alive()
        d_engine['changes_hyps_thread_is_alive'] = app.m.t_changes_hyps.is_alive()
        d_engine['changes_domains_thread_is_alive'] = app.m.t_changes_domains.is_alive()
        d_engine['working_threads'] = list(app.m.t_workers.keys())
        d_engine['status_threads'] = list(app.m.t_status.keys())
        d_engine['disk_operations_threads'] = list(app.m.t_disk_operations.keys())
        d_engine['queue_size_working_threads'] = {k:q.qsize() for k,q in app.m.q.workers.items()}
        d_engine['queue_disk_operations_threads'] = {k:q.qsize() for k,q in app.m.q_disk_operations.items()}
    else:
        d_engine['is_alive'] = False

    return jsonify(d_engine), 200

@app.route('/domains/user/<string:username>', methods=['GET'])
def get_domains(username):
    domains = app.db.get_domains_from_user(username)
    json_domains = json.dumps(domains,sort_keys=True, indent=4)

    return jsonify(domains = json_domains)