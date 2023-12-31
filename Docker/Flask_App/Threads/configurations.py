import logging

from Flask_App.Classes.FQDN_Class import FQDN_Class
from Flask_App.Classes.Cleanup_Class import Cleanup_Class
from Flask_App.Classes.Backup_Restore_Class import Backup_Restore_Class
from Flask_App.Classes.Log_Collection_Class import Log_Collection_Class
from Flask_App.Classes.File_Handler import File_Content_Streamer_Thread
from Flask_App.Classes.Notification_Handler import Notification_Handler_Thread, Notification_Status

from Flask_App.paths import root_path_log_collection_logs, root_log_collection_folder, root_fqdn_folder, root_path_cleanup_logs, root_path_fqdn_logs, root_path_backup_logs


maxBytes = 64*1024


notification_thread = Notification_Handler_Thread()
# notification_thread.start()


# Log Collection Thread
log_collection_thread = Log_Collection_Class(
    name="Log Collection Thread",
    download_path=root_log_collection_folder,
    logger=None,
    logger_level_stdo=logging.DEBUG,
    logger_level_file=logging.DEBUG,
    logger_file_path=root_path_log_collection_logs,
    mode="a", 
    maxBytes=maxBytes, 
    backupCount=2
)
log_collection_thread.before_task_call = lambda: notification_thread.queue_add("Log Collection started", Notification_Status.INFO)
log_collection_thread.after_task_call = lambda: notification_thread.queue_add("Log Collection Finished", Notification_Status.INFO)
# log_collection_thread.set_Parameters(
#     ssh_username="mapr",
#     ssh_password="mapr",
#     ip_addresses=[]
# )
log_collection_thread.start_Thread()

log_collection_logger_streamer = File_Content_Streamer_Thread(
    path=root_path_log_collection_logs,
    # wait_thread=log_collection_thread,
    is_yield=True
)
# log_collection_logger_thread.start()


# Cleanup Thread
cleanup_thread = Cleanup_Class(
    name="Cleanup Thread",
    logger=None,
    logger_level_stdo=logging.DEBUG,
    logger_level_file=logging.DEBUG,
    logger_file_path=root_path_cleanup_logs,
    mode="a", 
    maxBytes=maxBytes, 
    backupCount=2
)
cleanup_thread.before_task_call = lambda: notification_thread.queue_add("Cleanup started", Notification_Status.INFO)
cleanup_thread.after_task_call = lambda: notification_thread.queue_add("Cleanup finished", Notification_Status.INFO)
cleanup_thread.start_Thread()

cleanup_logger_streamer = File_Content_Streamer_Thread(
    path=root_path_cleanup_logs,
    # wait_thread=log_collection_thread,
    is_yield=True
)



# FQDN Thread
fqdn_thread = FQDN_Class(
    name="FQDN Thread",
    hosts_folder=root_fqdn_folder,
    logger=None,
    logger_level_stdo=logging.DEBUG,
    logger_level_file=logging.DEBUG,
    logger_file_path=root_path_fqdn_logs,
    mode="a", 
    maxBytes=maxBytes, 
    backupCount=2
)
fqdn_thread.before_task_call = lambda: notification_thread.queue_add("FQDN Setup started", Notification_Status.INFO)
fqdn_thread.after_task_call = lambda: notification_thread.queue_add("FQDN Setup finished", Notification_Status.INFO)
fqdn_thread.start_Thread()

fqdn_logger_streamer = File_Content_Streamer_Thread(
    path=root_path_fqdn_logs,
    # wait_thread=log_collection_thread,
    is_yield=True
)



# Backup Thread
backup_restore_thread = Backup_Restore_Class(
    name="Backup Thread",
    logger=None,
    logger_level_stdo=logging.DEBUG,
    logger_level_file=logging.DEBUG,
    logger_file_path=root_path_backup_logs,
    mode="a", 
    maxBytes=maxBytes, 
    backupCount=2
)
backup_restore_thread.before_task_call = lambda: notification_thread.queue_add("Backup / Restore started", Notification_Status.INFO)
backup_restore_thread.after_task_call = lambda: notification_thread.queue_add("Backup / Restore finished", Notification_Status.INFO)
backup_restore_thread.start_Thread()

backup_restore_logger_streamer = File_Content_Streamer_Thread(
    path=root_path_backup_logs,
    # wait_thread=log_collection_thread,
    is_yield=True
)

