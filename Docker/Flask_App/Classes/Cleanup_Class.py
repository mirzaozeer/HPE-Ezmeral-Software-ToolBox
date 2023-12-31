

 
import time

from Flask_App.Classes.Task_Handler import Task_Handler_Class
from Flask_App.Libraries.network_tools import ssh_execute_command, ssh_send_file



class Cleanup_Class(Task_Handler_Class):
    def __init__(self, *args, **kwargs):
        super(Cleanup_Class, self).__init__(*args, **kwargs)
        
        self.__parameters_template = {
            "ssh_username": "",
            "ssh_password": "",
            "ip_addresses": [],
            "script_path": ""
        }
        self.parameters = self.__parameters_template.copy()


    def set_Parameters(self, script_path: str, ssh_username: str, ssh_password: str, ip_addresses: list[str]) -> int:
        self.parameters = self.__parameters_template.copy()
        
        self.parameters["ssh_username"] = ssh_username
        self.parameters["ssh_password"] = ssh_password
        self.parameters["ip_addresses"] = ip_addresses
        self.parameters["script_path"] = script_path
        return 0
   

    def task(self, script_path, ssh_username, ssh_password, ip_addresses):
        self.logger.info(f"Cleaning {ip_addresses} ...")
        
        failed_ip_addresses:list[str] = list()

        try:
            # Check Thread State
            time.sleep(1)
            if self.stop_Action_Control():
                self.logger.warn("Thread Task Forced to Stop. Some actions may have done before stop, be carefully continue.")
                return -1
            
            # Execute cleanup.py over SSH
            for ip_address in ip_addresses:
                self.logger.info("Connecting to " + ip_address + " ...")
                
                remote_file_path = ssh_send_file(
                    ssh_client=ip_address, 
                    username=ssh_username, 
                    password=ssh_password, 
                    timeout=3,
                    local_file_path=script_path,
                    # remote_file_path="/tmp/", 
                    overwrite=True,
                    logger_hook=self.logger
                )

                # Check Thread State
                time.sleep(1)
                if self.stop_Action_Control():
                    self.logger.warn("Thread Task Forced to Stop. Some actions may have done before stop, be carefully continue.")
                    return -1
                
                if remote_file_path != "":
                    ssh_execute_command(
                        ssh_client=ip_address, 
                        username=ssh_username, 
                        password=ssh_password, 
                        command=f"python3 {remote_file_path} {ssh_password}",
                        reboot=False,
                        logger_hook=self.logger
                    )
                else:
                    self.logger.info("File transfer failed!")
                    failed_ip_addresses.append(ip_address)
                
                # Check Thread State
                time.sleep(1)
                if self.stop_Action_Control():
                    self.logger.warn("Thread Task Forced to Stop. Some actions may have done before stop, be carefully continue.")
                    return -1
                    
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        
        if len(failed_ip_addresses) > 0:
            self.logger.info(f"Cleanup Failed for IP Addresses: {failed_ip_addresses}")
        self.logger.info(f"Cleanup Finished for IP Addresses: {[ip for ip in ip_addresses if ip not in failed_ip_addresses]}")
        
        return 0