import os.path
import inspect
import urllib3
from DBModule.database import mysql_database
from Site24Module.Site24x7 import Site24x7
from Site24Module.site24configuration import Configuration as site24config
from NagiosModule.agios import Agios
from NagiosModule.nagiosconfiguration import Configuration

# add team contacts manually for:
# Tier-2
# Tier-3
# Server-APAC
# Server-EMEA
# Telecom
# Network

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def update_DB():

    ################################### Site24 ###################################
    db = mysql_database('crcdb.yaml')
    basedir = os.path.dirname(inspect.getfile(site24config))
    config = site24config(os.path.join(basedir, 'Site24config.yaml'))

    #Site24 board
    Site24 = Site24x7()

    business_units = config.get_bu_configs()

    site24_monitor_list = {}
    site24_group_list = {}
    site24_user_list = {}
    site24_monitors = []
    # build a list of all site24x7 monitors to reduce api requests to site24... we'll search for ids from this list
    for unit in business_units:
        BU = db.get_records_by_value("board", "board_bu_id", unit["BUID"])
        # Add records for the business units if they don't exist
        if len(BU) == 0:
            params = {}
            params['board_name'] = unit["BUName"]
            params['board_type'] = "Site24"
            params['board_bu_id'] = unit["BUID"]
            db.new_record("board", params)
        site24_monitor_list[unit["BUID"]] = Site24.get_all_monitors(unit["BUID"])
        site24_group_list[unit["BUID"]] = Site24.get_all_user_groups(unit["BUID"])
        site24_user_list[unit["BUID"]] = Site24.get_all_users(unit["BUID"])



    ########################### New Monitor Records ###############################
    allowed_types = ["URL", "DNS", "PORT-POP", "PORT-SMTP", "PORT_FTP", "SERVER", 
                     "VCENTER", "VMWAREESX", "VMWAREVM", "NETWORKDEVICE", "IISSERVER",
                     "SQLSERVER", "ADSERVER", "AGENTLESSSERVER", "AMAZON", "HYPERV",
                     "AZURE", "AZURE-MANAGEINSTANCE", "AZURE-MANAGEDCLUSTERS", "EC2INSTANCE"]
    for BUID in site24_monitor_list: # O(n) but there are 11... fairly static
        #print(len(site24_monitor_list[BUID]))
        for entry in site24_monitor_list[BUID]: # O(n2)
            if entry['type'] in allowed_types:
                params = {}
                try:
                    params['monitor_ip'] = entry['ipaddress']
                except:
                    pass
                if entry['type'] == 'URL':
                    params['monitor_url'] = entry['website']
                params['monitor_name'] = entry['display_name']
                params['monitor_type'] = entry['type']
                params['board_id'] = db.get_record_ids("board", "board_bu_id", BUID)[0]
                params['monitor_site24_id'] = entry['monitor_id']
                params['monitor_state'] = 'Active' if entry['state'] == 0 else 'Suspended'
                #print(type(entry['state']))
                # params['contact_group_id'] = idlookup(entry['user_group_ids'])
                record = db.get_records_by_value("monitor", "monitor_site24_id", entry['monitor_id'])
                if len(record) == 0:
                    db.new_record("monitor", params)
                    print("new record added:", params)
                if 'user_group_ids' in entry:
                    for group in entry['user_group_ids']:
                        params = {}
                        try: #It's possible there is a missing record for a monitor or group... so skip it and pop an alert...
                            params["contact_group_id"] = db.get_records_by_value("contact_group", "contact_group_site24_id", group)[0]["contact_group_id"]
                        except:
                            print("couldn't find contact group", group)
                        try:    
                            params["monitor_id"] = db.get_records_by_value("monitor", "monitor_site24_id", entry["monitor_id"])[0]["monitor_id"]
                            if len(db.match_record("monitor_link_group", params)) == 0:
                                db.new_record("monitor_link_group", params)
                        except:
                            print("Records could not be located for this monitor: ", entry['display_name'], entry['monitor_id'])
            temp = [item['display_name'] for item in site24_monitor_list[BUID]]
            site24_monitors.extend(temp)


########################### New Contact Records ###############################

        for entry in site24_user_list[BUID]:
            params = {}
            params['contact_name'] = entry['display_name']
            params['contact_type'] = "Individual"
            params['contact_email'] = entry['email_address']
            try:
                params['contact_phone'] = entry['mobile_settings']['mobile_number']
            except:
                # print("No Phone found for", entry['display_name'])
                pass
            params['contact_site24_id'] = entry['user_id']
            record = db.get_records_by_value("contact", "contact_site24_id", entry['user_id'])
            if len(record) == 0:
                db.new_record("contact", params)
                print("new record added:", params)

########################### New Contact Group Records ###############################

        for entry in site24_group_list[BUID]:
            params = {}
            group_name = db.get_records_by_value("board", "board_bu_id", BUID)[0]["board_name"] + "-" + entry['display_name']
            params['contact_group_name'] = group_name
            params['contact_group_site24_id'] = entry['user_group_id']
            record = db.get_records_by_value("contact_group", "contact_group_name", group_name)
            if len(record) == 0:
                db.new_record("contact_group", params)
            for user in entry['users']:
                params = {}
                try: #It's possible there is a missing record for a contact or group... so skip it and pop an alert...
                    params["contact_group_id"] = db.get_records_by_value("contact_group", "contact_group_name", group_name)[0]["contact_group_id"]
                except:
                    print("couldn't find contact group", group_name)
                try:    
                    params["contact_id"] = db.get_records_by_value("contact", "contact_site24_id", user)[0]["contact_id"]
                    if len(db.match_record("contact_link_group", params)) == 0:
                        db.new_record("contact_link_group", params)
                except:
                    print("Records could not be located for this userid: ", user)
                 


    ################################ Update to add monitor status #####################################
    # for BUID in site24_monitor_list:
    #     for entry in site24_monitor_list[BUID]:
    #         params = {}
    #         record = db.get_record("monitor", "monitor_name", entry['display_name'])
    #         params['monitor_state'] = 'Active' if entry['state']==0 else 'Suspended'
    #         try: 
    #             db.update_record("monitor", record[0], params)
    #         except:
    #             print("record not found ", entry['display_name'], record)


    ################################# End Site24 #################################



    ################################### Nagios ###################################

    basedir = os.path.dirname(inspect.getfile(Configuration))
    config = Configuration(os.path.join(basedir, 'nagiosconfig.yaml'))

    nagios_board_configs = config.get_board_configs()

    # This is where we'll store our boards (agios instances)
    boards = []

    # This is where we'll store monitors for comparing to db records
    nagios_monitors = []

    # Take information we got from the config file (config.yaml) and create board instances, adding each to the "boards" array
    for board_config in nagios_board_configs:
        boards.append(Agios(board_config["api_key"], board_config["hostname"], board_config["timezone"],
                            should_verify_https_cert=board_config["should_verify_https_cert"]))

    #### Build a dict with all existing monitors in a board to reduce API calls ####
    nagios_monitor_list = {}
    # build a list of all Nagios monitors to reduce api requests to Nagios...
    for board in boards:
        record = db.get_records_by_value("board", "board_name", board.api_host)
        if len(record) == 0:
            params = {}
            params['board_name'] = board.api_host
            params['board_type'] = "Nagios"
            db.new_record("board", params)
        try:
            nagios_monitor_list[board.api_host] = board.api_get("host")["host"]
        except: ### this will need to be added to message?
            print("No data was received from ", board.api_host, " through API. Please check API parameters or request help from CRC.")

########################### New Monitor Records ###############################

    for board in nagios_monitor_list:
        #print(board)
        for entry in nagios_monitor_list[board]:
            #print(entry)
            #break
            params = {}
            params['monitor_ip'] = entry['address']
            params['monitor_name'] = entry['host_name']
            params['monitor_type'] = "SERVER"
            #print(entry['host_name'])
            params['board_id'] = db.get_record_ids("board", "board_name", board)[0]
            if entry['is_active'] == '0':
                params['monitor_state'] = "Suspended"
            else:
                params['monitor_state'] = "Active"
            #print("entry_active", type(entry['is_active']))
            record = db.match_record("monitor", params)
            if len(record) == 0:
                db.new_record("monitor", params)
                print("new record added:", params)
        temp = [item['host_name'] for item in nagios_monitor_list[board]]
        nagios_monitors.extend(temp) #make new list not including board info to go compare for marking inactive monitors

################################# End Nagios #################################

################################# Mark removed monitors #################################

    db_monitors = db.get_all_records("monitor")

    for monitor in db_monitors:
        if monitor['monitor_name'] not in nagios_monitors and monitor['monitor_name'] not in site24_monitors:
            record = db.get_records_by_value("monitor", "monitor_name", monitor["monitor_name"])
            #print(record)
            if len(record) == 1:
                if record[0]["monitor_state"] != "decommed":
                    params = {
                        "monitor_state":"decommed"
                    }
                    db.update_record("monitor", record[0]["monitor_id"], params)
                else:
                    pass
            else:
                print("Multiple records match", monitor["monitor_name"], "please match record and mark decomm")

    

update_DB()