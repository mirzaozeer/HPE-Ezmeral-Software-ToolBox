import { endpoint_action_2_url } from './page_specific_urls.js';
import { get_ssh_credentials } from './ssh_credentials.js';
import { get_ip_host_addresses } from './ip_hostname_table.js';
import { flex_Element_Add_Device, flex_Element_Update_Device, flex_Element_Clear_Devices } from './flex_container.js';
import { showNotification } from './notification.js';
import { button_disable_by_element, checkResponses_restore } from './tools.js';



function restore_control(button = null) {
    button_disable_by_element(button, true);
    
    flex_Element_Clear_Devices();
    let device_ip_addresses = get_ip_host_addresses(true);
    let device_elements = flex_Element_Add_Device(device_ip_addresses.map(device => device.ip));
    
    let ipAddressesJson = JSON.stringify(
        device_ip_addresses.map(device => {
            return { "ip": device.ip }
        })
    );

    let credentials = get_ssh_credentials();
    let ssh_usernameJson = credentials[0];
    let ssh_passwordJson = credentials[1];


    // Append the IP addresses as a query parameter
    let url = endpoint_action_2_url;
    url = url + '?ssh_username=' + encodeURIComponent(ssh_usernameJson);
    url = url + '&ssh_password=' + encodeURIComponent(ssh_passwordJson);
    url = url + '&ip_addresses_hostnames=' + encodeURIComponent(ipAddressesJson);

    // Call Endpoint
    fetch(url).then(response => response.json()).then(data => {
        if (typeof data.message === "string") {
            showNotification(data.message, "error");
        }
        else{
            for (const [key, value] of Object.entries(data.message)) {
                // data.message = "IP: " + item.ip_address + " | " + "Response: " + item.response + " | " + "Message: " + item.message;

                // flex_Element_Update_Device:
                // element: str,
                // ip: str,
                // connection_status: str,
                // cron_job_status: str,
                // backup_script_status: str,
                // background_class: str

                let backups = value["responses_backups"]["message"].split("\n");
                let index = backups.indexOf("");
                if (index > -1) { // only splice array when item is found
                    backups.splice(index, 1); // 2nd parameter means remove one item only
                }

                let backup_number = backups.length;

                let connection_check_status = checkResponses_restore(value, "connection");
                let response_check_status = checkResponses_restore(value, "response");
                let connection_status = connection_check_status[0];
                let connection = connection_check_status[1];

                let backup_id = value["responses_backup_id"]["response"] === false ? "🔴" : value["responses_backup_id"]["message"] + " 🟢";
                let backup_cron = value["responses_backup_cron"]["response"] === false ? "🔴" : "🟢";
                let backup_script = value["responses_backup_script"]["response"] === false ? "🔴" : "🟢";
                let restore_script = value["responses_restore_script"]["response"] === false ? "🔴" : "🟢";
                let backups_status = backup_number > 0 ? backup_number - 1 + " 🟢" : " 🔴";

                let background_class = "";
                if (connection_status && response_check_status){
                    background_class = "bg-gif-alert-green-1";
                }
                else if (connection_status && !response_check_status) {
                    background_class = "bg-gif-alert-yellow-1";
                }
                else if (!connection_status) {
                    background_class = "bg-gif-noise-1";
                }
                else {
                    background_class = "bg-gif-simpsons-hide-1";
                }

                flex_Element_Update_Device(
                    device_elements[key],
                    key,
                    connection,
                    backup_id,
                    backup_cron,
                    backup_script,
                    restore_script,
                    backups_status,
                    background_class
                );
            }
        }
        // showNotification(notification, "info");

        if (button !== null || button !== undefined) {
            button.disabled = false;
        }
    }).catch(error => {
        console.error(error);
        showNotification(error, "error");
        button_disable_by_element(button, false);
    });
};
window.restore_control = restore_control;

export function get_Backup_Type(){
    let selectedRadio = document.querySelector('input[name="backup_type"]:checked');
    if (selectedRadio) {
        let selectedBackupType = selectedRadio.id;
        return selectedBackupType;
    } else {
        console.error("Backup type should be selected!");
    }
}