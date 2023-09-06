import { endpoint_action_2_url } from './page_specific_urls.js';
import { get_ip_addresses, get_ssh_credentials } from './ssh_credentials.js';


function backup_cron_control() {

    // Encode the IP addresses array into a JSON string
    var ipAddressesJson = get_ip_addresses(true);
    var ssh_usernameJson, ssh_passwordJson = get_ssh_credentials();

    // Append the IP addresses as a query parameter
    var url = endpoint_action_2_url
    url = url + '?ssh_username=' + encodeURIComponent(ssh_usernameJson);
    url = url + '&ssh_password=' + encodeURIComponent(ssh_passwordJson);
    url = url + '&ip_addresses=' + encodeURIComponent(ipAddressesJson);

    if (!terminal_source || terminal_source.readyState === 2) {
        terminal_EventSource_Start();
    }

    // Call Endpoint
    fetch(url).then(response => response.json()).then(data => {
        // console.log(data.message);
        showNotification(data.message, "info");
    }).catch(error => {
        console.error(error);
        showNotification(error, "error");
    });
};
