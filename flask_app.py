import json

from flask import Flask, jsonify, request, send_file, render_template, Response

from Libraries.tools import delete_folder, archive_files, archive_directory, list_dir
from paths import root_log_collection_folder, root_path_log, root_path_archives
from Threads.configurations import log_collection_logger_streamer, log_collection_thread
from threading import Lock

app = Flask(__name__, template_folder='frontend/pages', static_folder='frontend/static')


__log_collection_endpoint_lock = Lock()
__log_collection_stop_endpoint_lock = Lock()


@app.route('/',methods = ['POST', 'GET'])
def index():
    return render_template('index.html')


###################
### CLEANUP API ###
###################


@app.route('/cleanup',methods = ['POST', 'GET'])
def cleanup_page():
    return render_template('cleanup.html')

###################
###################
###################

######################
### FQDN SETUP API ###
######################

@app.route('/fqdn',methods = ['POST', 'GET'])
def fqdn_page():
    return render_template('fqdn.html')

######################
######################
######################

##########################
### LOG COLLECTION API ###
##########################

@app.route('/log_collection',methods = ['POST', 'GET'])
def log_collection_page():
    return render_template(
        'log_collection.html'
    )
    

@app.route('/log_collection_endpoint',methods = ['POST', 'GET'])
def log_collection_endpoint():
    
    global __log_collection_endpoint_lock
    if not __log_collection_endpoint_lock.locked():
        with __log_collection_endpoint_lock:
            ssh_username_json = request.args.get('ssh_username')
            ssh_password_json = request.args.get('ssh_password')
            ip_addresses_json = request.args.get('ip_addresses')
            
            
            if ssh_username_json is not None:
                ssh_username = json.loads(ssh_username_json)
            else:
                ssh_username = ""
                
            if ssh_password_json is not None:
                ssh_password = json.loads(ssh_password_json)
            else:
                ssh_password = ""
            
            if ip_addresses_json is not None:
                ip_addresses = json.loads(ip_addresses_json)
            else:
                ip_addresses = []
            
            
            log_collection_thread.set_Parameters(
                ssh_username=ssh_username,
                ssh_password=ssh_password,
                ip_addresses=ip_addresses
            )
            
            if not log_collection_thread.is_Running():
                log_collection_thread.start_Task()
            else:
                log_collection_thread.stop_Task()
                log_collection_thread.wait_To_Stop_Once_Task()
                log_collection_thread.start_Task()
    else:
        return jsonify(
            message="Log collection task already running"
        )
    
    return jsonify(
        message="Log collection task queued"
    )


@app.route('/log_collection_log_endpoint',methods = ['POST', 'GET'])
def log_collection_log_endpoint():
    return Response(
        log_collection_logger_streamer.read_file_continues(
            is_yield=True,
            sleep_time=0.05, # 0.3
            new_sleep_time=0.07,
            content_control=False
        ), 
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no' # Disable buffering
        }
    )


@app.route('/log_collection_list_collected_endpoint',methods = ['POST', 'GET'])
def log_collection_list_collected_endpoint():
    return jsonify(
        message=log_collection_thread.get_Collected_Log_Folder()
    )

@app.route('/log_collection_download_collected_endpoint')
def log_collection_download_collected_endpoint():
    archive_name = "collected_logs"
    archive_path = root_path_archives + archive_name + ".zip"
    
    print("log_collection_thread.get_Collected_Log_Folder()", log_collection_thread.get_Collected_Log_Folder())
    archive_directory(
        archive_name=archive_name,
        directory_to_compress=log_collection_thread.get_Collected_Log_Folder(),
        output_directory=root_path_archives,
    )
    return send_file(
        path_or_file=archive_path, 
        as_attachment=True, 
        download_name="collected_logs.zip"
    )

@app.route('/log_collection_download_terminal_log_endpoint')
def log_collection_download_terminal_log_endpoint():
    archive_path = root_path_archives + "log_collection_terminal_logs.zip"
    archive_files(
        log_collection_thread.get_Logs(), 
        archive_path
    )
    return send_file(
        path_or_file=archive_path, 
        as_attachment=False, 
        download_name="log_collection_terminal_logs.zip"
    )

    
@app.route('/clear_Collected_Log_Files',methods = ['POST', 'GET'])
def clear_Collected_Log_Files():
    response = delete_folder(root_log_collection_folder)
    
    return jsonify(
        message=f"Collected Log Files Response: {response}"
    )

@app.route('/clear_Log_Collection_Log_Files',methods = ['POST', 'GET'])
def clear_Log_Collection_Log_Files():
    log_collection_logger_streamer.clear_File_Content()
    
    return jsonify(
        message="Log contents are cleared"
    )
    

@app.route('/clear_Log_Buffer',methods = ['POST', 'GET'])
def clear_Log_Buffer():
    log_collection_logger_streamer.clear_Buffer()
    
    return jsonify(
        message="Log buffer cleared"
    )
    

@app.route('/log_collection_log_stop_endpoint',methods = ['POST', 'GET'])
def log_collection_stop_endpoint():
    global __log_collection_stop_endpoint_lock
    
    if not __log_collection_stop_endpoint_lock.locked():
        with __log_collection_stop_endpoint_lock:
            log_collection_thread.stop_Task()
            log_collection_thread.wait_To_Stop_Task()
    else:
        return jsonify(
            message="Log collection task stop already running"
        )
    
    return jsonify(
        message="Log collection tasks stopped"
    )
    
    
##########################
##########################
##########################


@app.route('/about',methods = ['POST', 'GET'])
def about():
    return render_template('about.html')


@app.route('/404',methods = ['POST', 'GET'])
def not_found():
    return render_template('404.html')



if __name__ == '__main__':
   app.run(debug = True)