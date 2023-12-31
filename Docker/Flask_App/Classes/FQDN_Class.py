

 
from datetime import datetime
import os
import time

from Flask_App.Classes.Task_Handler import Task_Handler_Class
from Flask_App.Libraries.network_tools import create_hosts_file, send_hostfile_to_device_ssh, update_hostname_ssh



class FQDN_Class(Task_Handler_Class):
    def __init__(self, hosts_folder, *args, **kwargs):
        super(FQDN_Class, self).__init__(*args, **kwargs)
        
        self.hosts_folder = hosts_folder
        
        self.__parameters_template:dict[str, str | list[dict[str, str]]] = {
            "ssh_username": "",
            "ssh_password": "",
            "ip_address_hostnames_list": [],
        }
        self.parameters = self.__parameters_template.copy()


    def set_Parameters(self, ssh_username: str, ssh_password: str, ip_address_hostnames_list: list[dict[str, str]]) -> int:
        self.parameters = self.__parameters_template.copy()
        
        self.parameters["ssh_username"] = ssh_username
        self.parameters["ssh_password"] = ssh_password
        self.parameters["ip_address_hostnames_list"] = ip_address_hostnames_list
        return 0
   

    def task(self, ssh_username, ssh_password, ip_address_hostnames_list):
        self.logger.info(f"FQDN setting up to {ip_address_hostnames_list} ...")
        
        failed_ip_addresses:list[dict[str, str]] = list()

        try:
            # Check Thread State
            time.sleep(1)
            if self.stop_Action_Control():
                self.logger.warn("Thread Task Forced to Stop. Some actions may have done before stop, be carefully continue.")
                return -1
            
            log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            timestamp_folder_logs = self.hosts_folder + log_timestamp + "/"
            
            # Create Hosts File
            if not os.path.exists(timestamp_folder_logs):
                os.makedirs(timestamp_folder_logs)
                
            ip_address_hostnames_list = create_hosts_file(
                ip_address_hostnames_list=ip_address_hostnames_list,
                folder=timestamp_folder_logs,
                logger_hook=self.logger
            )
            
            # Check Thread State
            time.sleep(1)
            if self.stop_Action_Control():
                self.logger.warn("Thread Task Forced to Stop. Some actions may have done before stop, be carefully continue.")
                return -1
            
            # Execute cleanup.py over SSH
            for i, ip_address_hostname_hosts in enumerate(ip_address_hostnames_list):
                self.logger.info(f"Connecting to {ip_address_hostname_hosts} ...")
                filepath_for_ip_address =  f"hosts_{ip_address_hostname_hosts['ip']}"
                
                response = send_hostfile_to_device_ssh(
                    ssh_client=ip_address_hostname_hosts["ip"], 
                    username=ssh_username, 
                    password=ssh_password, 
                    local_file_path=ip_address_hostname_hosts["hosts_file_path"],
                    remote_file_path="/etc/hosts", 
                    logger_hook=self.logger
                )
                if response != True:
                    failed_ip_addresses.append(ip_address_hostname_hosts)
                    continue
            
                # Check Thread State
                time.sleep(1)
                if self.stop_Action_Control():
                    self.logger.warn("Thread Task Forced to Stop. Some actions may have done before stop, be carefully continue.")
                    return -1
                
                response = update_hostname_ssh(
                    ssh_client=ip_address_hostname_hosts["ip"], 
                    # port=int(input("Please enter a Port: ")), 
                    username=ssh_username, 
                    password=ssh_password, 
                    new_hostname=ip_address_hostnames_list[i]["hostname"],
                    reboot="y", 
                    logger_hook=self.logger
                )
                if response != 0:
                    failed_ip_addresses.append(ip_address_hostname_hosts)
                
                # Check Thread State
                time.sleep(1)
                if self.stop_Action_Control():
                    self.logger.warn("Thread Task Forced to Stop. Some actions may have done before stop, be carefully continue.")
                    return -1
                    
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        
        if len(failed_ip_addresses) > 0:
            self.logger.info(f"FQDN Setup Failed for IP Addresses: {failed_ip_addresses}")
        self.logger.info(f"FQDN Setup Finished for IP Addresses: {[ip_hostname for ip_hostname in ip_address_hostnames_list if ip_hostname not in failed_ip_addresses]}")
        
        return 0


    def get_hosts_folder(self):
        return self.hosts_folder