import streamlit as st
# import string
import copy
import os, re
import time
import requests
import json, yaml
import subprocess
import shutil
from io import StringIO
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import streamlit_authenticator as stauth
from streamlit_ace import st_ace
from streamlit_authenticator.utilities.hasher import Hasher
# from streamlit_tree_select import tree_select #pip install streamlit-tree-select
st.set_page_config(layout= 'wide', page_title= 'BNGBlaster', page_icon= ':b:')
font_css = """
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 17px;
}
# </style>
# """
st.markdown(font_css, unsafe_allow_html=True)

if 'p1' not in st.session_state:
    st.session_state.p1= True
    st.session_state.p2= False
    st.session_state.p3= False
    st.session_state.p4= False
    st.session_state.p5= False
    st.session_state.user = ''
def write_dict_to_yaml(data_dict, file_path):
    """
    Write a dictionary to a YAML file.
    Parameters:
    data_dict (dict): The dictionary to write to the YAML file.
    file_path (str): The path to the YAML file where the data will be written.
    """
    with open(file_path, 'w') as file:
        yaml.dump(data_dict, file, default_flow_style=False)
def copy_and_rename_file(source_path, destination_path, new_name):
    """Copies a file and renames the copy.

    Args:
        source_path: Path to the source file.
        destination_path: Path to the destination directory.
        new_name: The new name for the copied file.
    """
    # Copy the file
    shutil.copy(source_path, destination_path)

    # Construct the full path to the copied file
    copied_file_path = os.path.join(destination_path, os.path.basename(source_path))

    # Construct the full path to the renamed file
    renamed_file_path = os.path.join(destination_path, new_name)

    # Rename the copied file
    os.rename(copied_file_path, renamed_file_path)
def is_valid_name_instance(s):
    # Regular expression to match only letters, numbers, and underscores,
    # and not start with a number
    pattern = r'^[A-Za-z_][A-Za-z0-9_]*$'
    return bool(re.match(pattern, s))
# Function for log action
def log_authorize(user, server , action):
    from datetime import datetime, timezone, timedelta # Datetime
    timestamp = datetime.now(timezone(timedelta(hours=+7), 'ICT')).strftime("%d/%m/%Y_%H:%M:%S")
    with open('auth.log', 'a') as session:
        session.write('\n')
        session.write(f"{timestamp}_{user}_{server} : {action}")

# hashed_passwords = Hasher(['xxx']).generate()
# print(hashed_passwords)
import yaml
from yaml.loader import SafeLoader
with open('authen/config.yaml') as file:
    config_authen = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config_authen['credentials'],
    config_authen['cookie']['name'],
    config_authen['cookie']['key'],
    config_authen['cookie']['expiry_days'],
    config_authen['preauthorized']
)
colx, coly, colz = st.columns([1,1.8,1])
with coly:
    st.image('./images/home.png', output_format= 'JPEG')
    st.logo('./images/svtech-logo.png', size= 'large', link = 'https://www.svtech.com/')
    name, authentication_status, username = authenticator.login('main', fields = {'Form name': ':pushpin: :orange[LOGIN]'})
if authentication_status:
    st.session_state.user= username
    # authenticator.logout('Logout', 'main')
elif authentication_status == False:
    with coly:
        st.error('Username/password is incorrect')
        st.stop()
elif authentication_status == None:
    with coly:
        st.warning('Please enter your username and password')
        st.stop()

# from streamlit_google_auth import Authenticate

# st.title('Streamlit Google Auth Example')

# authenticator = Authenticate(
#     secret_credentials_path = 'google_credentials.json',
#     cookie_name='my_cookie_name',
#     cookie_key='this_is_secret',
#     redirect_uri = 'http://10.98.12.70:8501',
# )

# # Catch the login event
# authenticator.check_authentification()

# # Create the login button
# authenticator.login()

# if st.session_state['connected']:
#     st.image(st.session_state['user_info'].get('picture'))
#     st.write('Hello, '+ st.session_state['user_info'].get('name'))
#     st.write('Your email is '+ st.session_state['user_info'].get('email'))
#     if st.button('Log out'):
#         authenticator.logout()
########################### Functions SQLite ########################
import sys
sys.path.append('../')
from lib import *

# def create_table(conn, table_name, columns):
#     cursor = conn.cursor()
#     # Construct the CREATE TABLE SQL statement
#     columns_with_types = ', '.join(f"{col_name} {data_type}" for col_name, data_type in columns.items())
#     create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"
#     cursor.execute(create_table_sql)
#     conn.commit()
#     print(f"Table '{table_name}' created successfully.")
# table_name = 'blasters'
# columns = {
#     'ip': 'TEXT PRIMARY KEY NOT NULL',
#     'port': 'INTEGER NOT NULL',
#     'user': 'TEXT NOT NULL',
#     'passwd': 'TEXT NOT NULL'
# }
# db_name = 'blaster.db'
# conn = sqlite_connect_to_db(db_name)
# # Create table
# create_table(conn, table_name, columns)

############# Collect to DB and save to varriable ###################################
user_privilege = ['admin', 'admin1', 'operator']
db = DatabaseConnection()
# db_name = 'blaster.db'
# conn_db = sqlite_connect_to_db(db_name)
conn_db=db.connection
# dict_user_db = dict(sqlite_fetch_table(conn_db, 'users'))
dict_user_db= dict(db.execute_query("SELECT * FROM users"))
# dict_blaster_db = pd.DataFrame(sqlite_fetch_table(conn_db, 'blasters')).to_dict('index')
dict_blaster_db = pd.DataFrame(db.execute_query("SELECT * FROM blasters")).to_dict('index')
dict_blaster_db_format ={}
for i in range(len(dict_blaster_db.keys())):
    element = {'port': dict_blaster_db[i][1], 'user': dict_blaster_db[i][2], 'passwd': dict_blaster_db[i][3]}
    dict_blaster_db_format[dict_blaster_db[i][0]] = element
conn_db.close()

# sqlite_create_table_user(conn)
# sqlite_insert_user(conn, 'hoanguyen', 'admin1')
# sqlite_insert_user(conn, 'linhnt', 'admin')
# users = sqlite_fetch_users(conn)
# st.write(users)
# sqlite_delete_user(conn, 'linhnt')
# users = sqlite_fetch_users(conn)
# st.write(users)
# conn.close()

#############################################################################
import ipaddress
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
#############################################################################
def check_key_value_is_list(dictionary, key):
    if key in dictionary:
        return isinstance(dictionary[key], list)
    else:
        return False
################### Function for set background ############################
import base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .main {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-attachment: local;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
# set_background('background.jpg')

##################### Function for gif file #################################
@st.cache_resource
def gif(gif_path):
    import base64
    file_ = open(gif_path, "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/gif;base64,{data_url}" alt="cat gif" style="max-width: 100%; height: 250px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    # st.markdown(
    #     f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    #     unsafe_allow_html=True,
    # )
#############################################################################

# path_bgp_update="/home/juniper/bngblaster/bgp_update"
# path_configs="/home/juniper/bngblaster/configs"
# path_templates="/home/juniper/bngblaster/templates"
# path_templates_part="/home/juniper/bngblaster/templates_part"
# path_templates_streams="/home/juniper/bngblaster/templates_streams"
# path_templates_interfaces="/home/juniper/bngblaster/templates_interfaces"

## Read VAR_PATH from env 
if "BNGBLASTER_CONFIG" in os.environ:
    file_path= os.environ['BNGBLASTER_CONFIG']
else:
    file_path = "./default_variable.yml"
print(f"BNGBLASTER_CONFIG IS {file_path}")
## read file yaml config
def read_config_yaml(file_path):
    with open(file_path, 'r') as yaml_file:
        config_data = yaml.safe_load(yaml_file)
        return config_data
config= read_config_yaml(file_path)
path_bgp_update= config.get('path').get('path_bgp_update')
path_configs=config.get('path').get('path_configs')
path_templates=config.get('path').get('path_templates')
path_templates_part=config.get('path').get('path_templates_part')
path_templates_streams=config.get('path').get('path_templates_streams')
path_templates_interfaces=config.get('path').get('path_templates_interfaces')

## Payload for REST API 
payload_command_session_counters="""
{
    "command": "session-counters"
}
"""
payload_command_network_interface="""
{
    "command": "network-interfaces"
}
"""
payload_command_access_interface="""
{
    "command": "access-interfaces"
}
"""
payload_command_stream_summary="""
{
    "command": "stream-summary"
}
"""
payload_start="""
{
    "logging": true,
    "logging_flags": [
        "session",
        "stream",
        "debug",
        "pppoe",
        "ip"
    ],
    "report": true,
    "report_flags": [
        "sessions",
        "streams"
    ]
}
"""
payload_stop="""
{
    "logging": true,
    "logging_flags": [
        "session",
        "stream",
        "debug",
        "pppoe",
        "ip"
    ],
    "report": true
    "report_flags": [
        "sessions",
        "streams"
   ]
}
"""
def push_file_to_server_by_ftp(hostname, username, password, local_path, remote_path):
    import paramiko
    # Define the SFTP connection parameters
    # hostname = ''
    port = 22
    # username = ''
    # password = ''

    # Define the local file path and the remote destination path
    # local_path = '/path/to/local/file.txt'
    # remote_path = '/path/to/remote/destination/file.txt'

    # Establish an SSH transport and SFTP session
    transport = paramiko.Transport((hostname, port))
    try:
        transport.connect(username=username, password=password)
    except Exception as e:
        print(f'Error connect to server, Error: {e}')
    sftp = paramiko.SFTPClient.from_transport(transport)
    # Upload the file
    sftp.put(local_path, remote_path)
    # Close the SFTP session and the SSH transport
    sftp.close()
    transport.close()

def push_file_to_server_rest_api(server, port, file_path):
    import requests
    # Replace 'http://your-server-url.com/upload' with the actual URL of your server endpoint
    url = f'http://{server}:{port}/upload'

    # Path to the file you want to send
    # file_path = '/home/juniper/python/data.csv'

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Send a POST request with the file attached
        response = requests.post(url, files={'file': file})

    # Check the response
    if response.status_code == 200:
        print("File uploaded successfully.")
        return 200
    else:
        print("Error occurred while uploading file:", response.status_code)
def delete_file_on_server(server, port, file_path):
    import requests

    url = f'http://{server}:{port}/delete'

    # Make a POST request to the server to delete the file
    response = requests.post(url, data={'filename': file_path})

    # Check the response
    if response.status_code == 200:
        print("File deleted successfully.")
    elif response.status_code == 404:
        print("File not found on the server.")
    else:
        print("Error occurred while deleting file:", response.status_code)

def get_variables_jinja_file(file_path):
    from jinja2 import Environment, meta
    # linhnt : 24.04.2024
    # file_path : directory to folder have file
    import re
    with open(file_path, 'r') as file:
        template_content = file.read()
        # Use a regular expression to find Jinja variable syntax
        # variable_pattern = r'{{\s*(\w+)\s*}}'
        # variables = re.findall(variable_pattern, template_content)
        env = Environment() 
        parsed_content = env.parse(template_content) # Parse the template into an AST
        undeclared_variables = meta.find_undeclared_variables(parsed_content) # Find all undeclared variables
        # return list(dict.fromkeys(variables))
        return list(undeclared_variables)

def get_list_file(file_path, file_type):
  file_list=[]
  list_file_result=[]
  for files in os.walk(file_path):
      file_list = files[2] #Get file_list
  
  for i in range(len(file_list)):
    str = "^.*\." + file_type + "$"
    x= re.search(str,file_list[i])
    if x:
        list_file_result.append(file_list[i])
  #list_file_result_str = [str(x) for x in list_file_result]     # Change string format
  return list_file_result
########################## Get list config ############################################
list_json= get_list_file(path_configs, 'json') # Get list file json from folder
list_instance=[]
for i in list_json:
    list_instance.append(i.split('.')[0])
################# Get list part_template ##########################################
list_part_file= get_list_file(path_templates_part, "j2")
list_part=[]
for i in list_part_file:
    list_part.append(i[:-3])
dict_element_config={}
for i in list_part:
    # data = yaml.load(open(f"{path_templates_part}/{i}.j2", 'r'), Loader=yaml.FullLoader)
    with open(f"{path_templates_part}/{i}.j2", 'r') as part:
        data=part.read()
    dict_element_config[i] = data
# st.write(dict_element_config)
################# Get list templates_streams ##########################################
list_streams_file= get_list_file(path_templates_streams, "j2")
list_streams=[]
for i in list_streams_file:
    list_streams.append(i[:-3])
dict_streams_templates={}
for i in list_streams:
    with open(f"{path_templates_streams}/{i}.j2", 'r') as part:
        data=part.read()
    dict_streams_templates[i] = data
# st.write(dict_streams_templates)
################# Get list templates_interfaces ##########################################
list_interfaces_file= get_list_file(path_templates_interfaces, "j2")
list_interfaces=[]
for i in list_interfaces_file:
    list_interfaces.append(i[:-3])
dict_interfaces_templates={}
for i in list_interfaces:
    with open(f"{path_templates_interfaces}/{i}.j2", 'r') as part:
        data=part.read()
    dict_interfaces_templates[i] = data
# st.write(dict_interfaces_templates)
###################################################################################
list_templates= get_list_file(path_templates, 'j2') # Get list file j2 from folder
###################################################################################
list_bgp_update= get_list_file(path_bgp_update, 'bgp') # Get list file bgp from folder

def execute_remote_command(host, username, command):
    ssh_command = ['ssh', f'{username}@{host}', command]
    result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return result.stdout.strip()  # Return the output of the command
    else:
        print(f"Error executing command: {result.stderr.strip()}")
        return None
def execute_remote_command_use_passwd(host, username, passwd , command):
    import paramiko
    import time
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the remote server
        client.connect(host, username=username, password=passwd)
        # Execute the command to check network interfaces
        print('Command: %s send to %s'%(command, host))
        stdin, stdout, stderr = client.exec_command(f'{command}')
        time.sleep(0.01)
        stdin.write(passwd + "\n")
        time.sleep(0.01)
        stdin.flush()
        # Read the command output
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print("execute_remote_command_use_passwd() output %s"%output)
            return output
        if error:
            print("execute_remote_command_use_passwd() error %s"%error)
            return 0
    finally:
        # Close the connection
        client.close()
def execute_remote_command_use_passwd_get_time(host, username, passwd , command):
    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the remote server
        client.connect(host, username=username, password=passwd)
        # Execute the command to check network interfaces
        stdin, stdout, stderr = client.exec_command(f'{command}')
        # Read the command output
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            line = output.split('\n')
            for time in line:
                if time != '':
                    return time
                else: continue
        if error:
            print(error)
            return 0
    finally:
        # Close the connection
        client.close()
def find_sub_interface(host, username, password, interface):
    sub=''
    host = '10.99.94.2'
    username = 'root'
    command = 'netstat -i | grep %s'%interface  # Command to execute remotely
    output = execute_remote_command(host, username, command)
    if output is not None:
        print("Output of the remote command:")
        line= output.split('\n')
        sub= line[-1].split(' ')[0]
        # print(sub.split('.'))
        if sub.split('.') == interface:
            return sub.split('.')[1]
        else:
            return 0
    else:
        print('Do not have already sub-interface')
        return 0
def find_unused_vlans(hostname, username, password, interface): # Function find unsued vlan of one interface (range vlan from 1-4094)
    import paramiko
    # Create an SSH client
    client = paramiko.SSHClient()
    # Automatically add untrusted hosts (not recommended for production)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the remote server
        client.connect(hostname, username=username, password=password)
        # Execute the command to check network interfaces
        # stdin, stdout, stderr = client.exec_command("sudo -S netstat -i | grep -e ens -e eth")
        stdin, stdout, stderr = client.exec_command("ip link show | grep '@%s' | awk -F '@' '{print $1}' | awk -F '.' '{print $2}'"%interface)
        stdin.write(password + "\n")
        stdin.flush()
        # Read the command output
        output = stdout.read().decode()
        error = stderr.read().decode()
        # Assuming VLANs are numbered from 2 to 4094
        all_vlans = set(map(str, range(1, 4095)))
        # unused_vlans = all_vlans - used_vlans
        if output:
            line = output.split('\n')
            list_vlan_temp = []
            for i in line:
                list_vlan_temp.append(i)
            return sorted(all_vlans - set(list_vlan_temp))   #Return list vlan unused
        else:
            return sorted(all_vlans) # Return list vlan unused
        if error:
            print(error)
    finally:
        # Close the connection
        client.close()
def find_used_vlans(hostname, username, password, interface): # Function find unsued vlan of one interface (range vlan from 1-4094)
    import paramiko
    # Create an SSH client
    client = paramiko.SSHClient()
    # Automatically add untrusted hosts (not recommended for production)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the remote server
        client.connect(hostname, username=username, password=password)
        # Execute the command to check network interfaces
        # stdin, stdout, stderr = client.exec_command("sudo -S netstat -i | grep -e ens -e eth")
        stdin, stdout, stderr = client.exec_command("ip link show | grep '@%s' | awk -F '@' '{print $1}' | awk -F '.' '{print $2}'"%interface)
        stdin.write(password + "\n")
        stdin.flush()
        # Read the command output
        output = stdout.read().decode()
        error = stderr.read().decode()
        # used_vlans
        if output:
            line = output.split('\n')
            list_vlan_temp = []
            for i in line:
                if i == "":
                    continue
                else:
                    list_vlan_temp.append(i)
            return sorted(set(list_vlan_temp))   #Return list vlan used
        else:
            return ['null']
        if error:
            print(error)
    finally:
        # Close the connection
        client.close()
def find_and_split_line_from_file(file_path, search_string):
    try:
        last_matching_line = None
        with open(file_path, 'r') as file:
            for line in file:
                if search_string in line:
                    last_matching_line = line.strip()  # Store the last matching line

        if last_matching_line is not None:
            # Split the last matching line into components
            components = last_matching_line.split()  # You can specify a delimiter if needed
            return components
        else:
            return None  # Return None if the string is not found
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def find_interface(hostname, username, password):
    import paramiko
    # Create an SSH client
    client = paramiko.SSHClient()
    # Automatically add untrusted hosts (not recommended for production)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the remote server
        client.connect(hostname, username=username, password=password)
        # Execute the command to check network interfaces
        # stdin, stdout, stderr = client.exec_command("sudo -S netstat -i | grep -e ens -e eth")
        stdin, stdout, stderr = client.exec_command("sudo -S netstat -i | grep -e ens")
        stdin.write(password + "\n")
        stdin.flush()
        # Read the command output
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            # st.code(output)  
            line = output.split('\n')
            list_int_temp = []
            for i in line:
                sub= i.split(' ')[0]
                if ("." not in sub) and (sub != ""):
                    list_int_temp.append(sub) 
            return set(list_int_temp)   
        else:
            return ['null']         
        if error:
            print(error)
    finally:
        # Close the connection
        client.close()
def filter_dict(data: dict, extract):
    try:
        if isinstance(extract, list):
            list_result=[]
            while extract:
                if result := filter_dict(data, extract.pop(0)):
                    list_result.append(result)
            return list_result
        shadow_data = data.copy()
        for key in extract.split('.'):
            if str(key).isnumeric():
                key = int(key)
            shadow_data = shadow_data[key]
        return shadow_data
    except (IndexError, KeyError, AttributeError, TypeError):
        return None
@st.dialog("Confirmation")
def delete_config(path_configs, instance):
    st.write(f":orange[Are you sure for deleting?]")
    col1, col2 = st.columns([1,6])
    with col1:
        if st.button(":red[**YES**]"):
            os.remove(f"{path_configs}/{instance}.json")
            if os.path.exists('%s/%s.yml'%(path_configs,instance)):
                os.remove(f"{path_configs}/{instance}.yml")
            if os.path.exists('%s/%s_streams.yml'%(path_configs,instance)):
                os.remove(f"{path_configs}/{instance}_streams.yml")
            if os.path.exists('%s/%s_interfaces.yml'%(path_configs,instance)):
                os.remove(f"{path_configs}/{instance}_interfaces.yml")
            st.toast(':blue[Delete test profile %s successfully]'%instance, icon="🔥")
            log_authorize(st.session_state.user,blaster_server['ip'], f'DELETE test profile {instance}')
            time.sleep(1)
            st.rerun()
    with col2:
        if st.button("**CANCEL**", type= 'primary'):
            st.rerun()

# @st.cache_data
def CALL_API_BLASTER(server,port,instance, method, body, action=''):
    try:
        # print(f'http://{server}:{port}/api/v1/instances/{instance}{action}')
        response = requests.request(method, f'http://{server}:{port}/api/v1/instances/{instance}{action}', headers={'Content-Type': 'application/json'},data=body)
        # print(response.headers["Date"])
        return response.status_code, response.content
    except Exception as e:
        print(f'Can not request API blaster server. Error {e}')
def VERSION_BLASTER(server,port):
    try:
        # print(f'http://{server}:{port}/api/v1/instances/{instance}{action}')
        response = requests.request('GET', f'http://{server}:{port}/api/v1/version')
        # print(response.headers["Date"])
        return response.status_code, response.content
    except Exception as e:
        print(f'Can not request API blaster server. Error {e}')        
def UPLOAD_FILE_BLASTER(server, port, instance, file_path):
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(
                f'http://{server}:{port}/api/v1/instances/{instance}/_upload',
                files={'file': file}  # Use 'files' instead of 'form'
            )
        return response.status_code, response.content
    except Exception as e:
        print(f'Cannot request API blaster server. Error: {e}')
def GET_ALL_INTANCES_BLASTER(server,port):
    try:
        # print(f'http://{server}:{port}/api/v1/instances/{instance}{action}')
        response = requests.request("GET", f'http://{server}:{port}/api/v1/instances', headers={'Content-Type': 'application/json'},data="")
        # print(response.headers["Date"])
        return response.status_code, response.content
    except Exception as e:
        print(f'Can not request API blaster server. Error {e}')
################## Function for blaster-status ############################################
def blaster_status(ip, port, list_instance_running_from_blaster, list_instance_avail_from_blaster):
    with st.container(border=True):
        bscol1, bscol2 = st.columns([1,2], border=True)
        with bscol1:
            st.subheader(f':sunny: :green[BNG-BLASTER [{ip}] STATUS]')
            version_sc, version_ct = VERSION_BLASTER(blaster_server['ip'], blaster_server['port'])
            if version_sc==200:
                version = json.loads(version_ct)
                st.write(":green[*:material/sunny_snowing: [BNGBlaster: V%s] [BNGBlasterCtrl: V%s] [%s]*]"%(version['bngblaster-version'], version['bngblasterctrl-version'], version['bngblaster-compiler']))
        with bscol2:
            # Note: dict_blaster_db_format is var global
            list_int_server = find_interface(ip, dict_blaster_db_format[ip]['user'], dict_blaster_db_format[ip]['passwd'])
            for i in list_int_server:
                st.write(':green[ :material/share: *Interface %s existed sub: %s*]'%(i, find_used_vlans(ip, dict_blaster_db_format[ip]['user'], dict_blaster_db_format[ip]['passwd'], i)))
        col_select, col_display= st.columns([1,2])
        with col_select:
            with st.container(border=True):
                st.write(":fire: :violet[**TEST PROFILE RUNNING**]")
            with st.container(border=True, height= 400):   
                select_running_instance={}
                for i in list_instance_running_from_blaster:
                    col111, col112= st.columns([4,1], border= True)
                    with col111:
                        exec(f"""select_running_instance['{i}'] = st.checkbox(f":orange[*{i}*]")""") 
                    with col112:
                        with st.popover(':orange[:material/access_time:]', use_container_width=True):
                        # with st.container(border=True):
                            time_start = find_and_split_line_from_file('auth.log', 'RUN START test profile %s'%i)
                            st.info(":blue[**:material/sound_sampler: LAST START**]")
                            try:
                                st.write(":orange[ :material/sound_sampler: *%s*]"%time_start[0].split('_')[0:3])
                                st.write(":orange[ :material/dns: *%s*]"%time_start[0].split('_')[3])
                            except:
                                st.write(":orange[ :material/sound_sampler: *None*]")
                                st.write(":orange[ :material/dns: *None*]")
                            time_stop = find_and_split_line_from_file('auth.log', 'RUN STOP test profile %s'%i)
                            st.info(":blue[**:material/stop_circle: LAST STOP**]")
                            try:
                                st.write(":orange[ :material/stop_circle:*%s*]"%time_stop[0].split('_')[0:3])
                                st.write(":orange[ :material/dns: *%s*]"%time_stop[0].split('_')[3])
                            except:
                                st.write(":orange[ :material/stop_circle: *None*]")
                                st.write(":orange[ :material/dns: *None*]")
                select_running_instance_cb = [] # List select checkbox
                for i in select_running_instance.keys():
                    if select_running_instance[i]:
                        select_running_instance_cb.append(i)    
        with  st.expander(":material/graphic_eq: :violet[**TEST PROFILE EXISTED CONFIG**]"):
            for i in list_instance_avail_from_blaster:
                with st.container(border=True):
                    col1, col2= st.columns([1,1])
                    with col1:
                        st.write(f":orange[**Profile :**] *{i}*")
                    with col2:
                        with st.popover(f":blue[:material/visibility: **CONFIG**]", use_container_width=True):
                            view_config_avail_sc,  view_config_avail_ct = CALL_API_BLASTER(ip, port, i, 'GET', payload_start, '/config.json')
                            if view_config_avail_sc==200:
                                try:
                                    config_avail = json.loads(view_config_avail_ct)
                                    st.code(json.dumps(config_avail, indent=2), language='json')
                                except Exception as e:
                                    st.error(':blue[Test profile %s have json syntax error %s]'%(i,e), icon="🔥")
                                    continue
                # st.dataframe(list_instance_avail_from_blaster, use_container_width= True)
                # st.dataframe(list_instance_avail_from_blaster, use_container_width= True, column_config={"value": "instance-name"})
        with col_display:
            with st.container(border=True):
                st.write(":fire: :violet[**GRAPH**]")
            with st.container(border=True, height= 400):
                for i in select_running_instance_cb:
                    st.markdown("""
                        <style>
                        /* This targets the actual popover container */
                        div[data-testid="stPopoverBody"] {
                            width: 1680px;  /* Change as needed */
                            max-width: 10000px;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    with st.popover(f":orange[:material/timeline: *{i}*]", use_container_width=True):
                        col_realtime, col_graph= st.columns([1,1])
                        with col_realtime:
                            with st.container(border= True, height=600):
                                with st.container(border= True):
                                    st.write("##### :green[**:material/bolt: INTERFACES STATISTICS**]")
                                with st.container(border= True):
                                    st.write(':violet[**:material/share: NETWORK INTERFACES**]')
                                    exec("display_nw_interface_%s = st.empty()"%i)
                                with st.container(border= True):
                                    st.write(':violet[**:material/share: ACCESS INTERFACES**]')
                                    exec("display_acc_interface_%s = st.empty()"%i)
                        with st.container(border= True):
                            with st.container(border= True):
                                col_stream1, col_stream2,col_stream3,col_stream4,col_stream5= st.columns([1,0.2,3,0.2,1])
                                with col_stream1:
                                    with st.container(border= True):
                                        st.write('##### :green[:material/bolt: **STREAMS STATISTICS**]')
                                with col_stream3:
                                    payload_command_stream_stats="""
                                    {
                                        "command": "stream-stats"
                                    }
                                    """
                                    run_command_streams_stats_sc, run_command_streams_stats_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_stream_stats, '/_command')
                                    if run_command_streams_stats_sc == 200:
                                        data_streams_stats = json.loads(run_command_streams_stats_ct)
                                        total_flows = data_streams_stats['stream-stats']['total-flows']
                                    if total_flows > 0:
                                        with st.container(border= True):
                                            exec("flow_selection_%s = st.multiselect(':green[:material/add: Select flow-id]', options=range(1,%s), default=[1])"%(i,total_flows))
                                with col_stream5:
                                    if st.button(':orange[:material/bolt: **RESET**]', use_container_width=True, key='%s'%i):
                                        payload_command_stream_reset="""
                                        {
                                            "command": "stream-reset"
                                        }
                                        """
                                        run_command_streams_reset_sc, run_command_streams_reset_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_stream_reset, '/_command')
                                        if run_command_streams_reset_sc == 200:
                                            st.toast(':blue[Reset stream statistic test profile %s successfully]'%i, icon="🔥")
                            with st.container(border= True):
                                exec("display_streams_%s = st.empty()"%i)
                        # df_nw_tx_rx = pd.DataFrame([[0, 0]], columns=(["network_tx_packets", "network_rx_packets"]))
                        # df_acc_tx_rx = pd.DataFrame([[0, 0]], columns=(["access_tx_packets", "access_rx_packets"]))
                        with col_graph:
                            with st.container(border= True, height=600):
                                with st.container(border= True):
                                    st.write("##### :green[**:material/diagonal_line: GRAPH**]")
                                with st.expander(":violet[:material/arrow_drop_down_circle: **NETWORK-INTERFACES**]"):
                                    df_nw_tx_rx_pps = pd.DataFrame([[0, 0]], columns=(["network_tx_pps", "network_rx_pps"]))
                                    run_command_nw_int_sc, run_command_nw_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_network_interface, '/_command')
                                    if run_command_nw_int_sc == 200:
                                        data_nw_int = json.loads(run_command_nw_int_ct)
                                        num_nw_int =len(data_nw_int['network-interfaces']) # Number network interfaces in json
                                        for j in range(num_nw_int):
                                            st.write(':orange[**Network Interface  [%s]**]'%filter_dict(data_nw_int, 'network-interfaces.%s.name'%j))
                                            # with st.container(border= True):
                                            #     exec(f'nw_int_chart_{i} = st.line_chart(df_nw_tx_rx, color = ["#FF0000", "#0000FF"], use_container_width= True)')
                                            with st.container(border= True):
                                                exec(f'nw_int_chart_{i}_{j}_pps = st.line_chart(df_nw_tx_rx_pps, color = ["#FF0000", "#0000FF"], use_container_width= True)')
                                        # with st.container(border= True):
                                        #     st.write(':orange[**PACKET LOSS %s **]'%filter_dict(data_nw_int, 'network-interfaces.%s.name'%j))
                                        #     exec(f'nw_pktloss_chart_{i}_{j} = st.line_chart(df_nw_rx_pktloss, color = ["#FF0000"],use_container_width= True)')
                                with st.expander(":violet[:material/arrow_drop_down_circle: **ACCESS-INTERFACES**]"):
                                    df_acc_tx_rx_pps = pd.DataFrame([[0, 0]], columns=(["access_tx_pps", "access_rx_pps"]))
                                    run_command_acc_int_sc, run_command_acc_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_access_interface, '/_command')
                                    if run_command_acc_int_sc == 200:
                                        data_acc_int = json.loads(run_command_acc_int_ct)
                                        num_acc_int =len(data_acc_int['access-interfaces']) # Number access interfaces in json
                                        for j in range(num_acc_int):
                                            st.write(':orange[**Access Interface [%s]**]'%filter_dict(data_acc_int, 'access-interfaces.%s.name'%j))
                                            # with st.container(border= True):
                                            #     exec(f'acc_int_chart_{i} = st.line_chart(df_acc_tx_rx, color = ["#FF0000", "#0000FF"], use_container_width= True)')
                                            with st.container(border= True):
                                                exec(f'acc_int_chart_{i}_{j}_pps = st.line_chart(df_acc_tx_rx_pps, color = ["#FF0000", "#0000FF"], use_container_width= True)')
                if len(select_running_instance_cb) !=0:
                    while True:
                        for i in select_running_instance_cb:
                            with st.container(border= True):
                                # Call API for network interface value====================
                                run_command_nw_int_sc, run_command_nw_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_network_interface, '/_command')
                                if run_command_nw_int_sc == 200:
                                    data_nw_int = json.loads(run_command_nw_int_ct)
                                    num_nw_int =len(data_nw_int['network-interfaces']) # Number network interfaces in json
                                    list_nw_name,list_nw_tx_pps, list_nw_rx_pps, list_nw_pkt_loss, list_nw_pkt_loss_graph=[],[],[],[],[]
                                    # Loop for multiple network interfaces
                                    for j in range(num_nw_int):
                                        list_nw_name.append(filter_dict(data_nw_int, 'network-interfaces.%s.name'%j))
                                        list_nw_tx_pps.append(filter_dict(data_nw_int, 'network-interfaces.%s.tx-pps'%j))
                                        list_nw_rx_pps.append(filter_dict(data_nw_int, 'network-interfaces.%s.rx-pps'%j))
                                        list_nw_pkt_loss.append(filter_dict(data_nw_int, 'network-interfaces.%s.rx-loss-packets-streams'%j))
                                        temp_list=[]
                                        for o in range(10): # this loop  for linechart column
                                            temp_nw_int_sc, temp_nw_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_network_interface, '/_command')
                                            temp_data_nw_int = json.loads(temp_nw_int_ct)
                                            temp_list.append(filter_dict(temp_data_nw_int, 'network-interfaces.%s.rx-loss-packets-streams'%j))
                                            time.sleep(0.001)
                                        list_nw_pkt_loss_graph.append(temp_list)
                                    # Create table for network interfaces and access interfaces
                                    table_nw_int = {
                                        "NAME": list_nw_name,
                                        "NW-TX(pps)": list_nw_tx_pps,
                                        "NW-RX(pps)": list_nw_tx_pps,
                                        "NW-LOSS(pkt)": list_nw_pkt_loss,
                                        "NW-LOSS-GRAPH": list_nw_pkt_loss_graph,
                                    }
                                    # Display table for network interfaces
                                    exec("display_nw_interface_%s.dataframe(table_nw_int, column_config={\"NW-LOSS-GRAPH\": st.column_config.AreaChartColumn(\"PKT-LOSS-GRAPH\")},use_container_width=True)"%i) # Edit configure by st.column_config.AreaChartColumn
                                    
                                # Call API for access interface value =================
                                run_command_acc_int_sc, run_command_acc_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_access_interface, '/_command')
                                if run_command_acc_int_sc == 200:
                                    data_acc_int = json.loads(run_command_acc_int_ct)
                                    num_acc_int =len(data_acc_int['access-interfaces']) # Number network interfaces in json
                                    list_acc_name,list_acc_tx_pps, list_acc_rx_pps, list_acc_pkt_loss, list_acc_pkt_loss_graph=[],[],[],[],[]

                                    # Loop for multiple access interfaces
                                    for k in range(num_acc_int):
                                        list_acc_name.append(filter_dict(data_acc_int, 'access-interfaces.%s.name'%k))
                                        list_acc_tx_pps.append(filter_dict(data_acc_int, 'access-interfaces.%s.tx-pps'%k))
                                        list_acc_rx_pps.append(filter_dict(data_acc_int, 'access-interfaces.%s.rx-pps'%k))
                                        list_acc_pkt_loss.append(filter_dict(data_acc_int, 'access-interfaces.%s.rx-loss-packets-streams'%k))
                                        temp_list=[]
                                        for o in range(10): # this loop  for linechart column
                                            temp_acc_int_sc, temp_acc_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_access_interface, '/_command')
                                            temp_data_acc_int = json.loads(temp_acc_int_ct)
                                            temp_list.append(filter_dict(temp_data_acc_int, 'access-interfaces.%s.rx-loss-packets-streams'%k))
                                            time.sleep(0.001)
                                        
                                        list_acc_pkt_loss_graph.append(temp_list)
                                    
                                    # df_nw_int= pd.DataFrame.from_dict(table_nw_int)
                                    table_acc_int = {
                                        "NAME": list_acc_name,
                                        "AC-TX(pps)": list_acc_tx_pps,
                                        "AC-RX(pps)": list_acc_tx_pps,
                                        "AC-LOSS(pkt)": list_acc_pkt_loss,
                                        "AC-LOSS-GRAPH": list_acc_pkt_loss_graph,
                                    }
                                    # Display table for access interfaces
                                    exec("display_acc_interface_%s.dataframe(table_acc_int, column_config={\"AC-LOSS-GRAPH\": st.column_config.AreaChartColumn(\"PKT-LOSS-GRAPH\")},use_container_width=True)"%i) # Edit configure by st.column_config.AreaChartColumn
                                    
                                # ====================== Call API for stream summary ======================
                                payload_command_stream_stats="""
                                {
                                    "command": "stream-stats"
                                }
                                """
                                run_command_streams_stats_sc, run_command_streams_stats_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_stream_stats, '/_command')
                                if run_command_streams_stats_sc == 200:
                                    data_streams_stats = json.loads(run_command_streams_stats_ct)
                                    total_flows = data_streams_stats['stream-stats']['total-flows']
                                if total_flows > 0:
                                    list_streams_name, list_streams_flowid, list_streams_direction, list_streams_sessionid, list_streams_tx_pps, list_streams_tx_bps, list_streams_rx_pps, list_streams_rx_bps, list_streams_loss=[],[],[],[],[],[],[],[],[]
                                    for n in eval("flow_selection_%s"%i): # Loop for make table of flow-ids
                                        payload_command_stream_info="""
                                        {
                                            "command": "stream-info",
                                            "arguments": {"flow-id": %s}
                                        }
                                        """%n
                                        run_command_streams_info_sc, run_command_streams_info_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_stream_info, '/_command')
                                        if run_command_streams_info_sc == 200:
                                            data_streams_info = json.loads(run_command_streams_info_ct)

                                            list_streams_name.append(filter_dict(data_streams_info, 'stream-info.name'))
                                            list_streams_flowid.append(filter_dict(data_streams_info, 'stream-info.flow-id'))
                                            list_streams_tx_pps.append(filter_dict(data_streams_info, 'stream-info.tx-pps'))
                                            list_streams_tx_bps.append(filter_dict(data_streams_info, 'stream-info.tx-bps-l2'))
                                            list_streams_rx_pps.append(filter_dict(data_streams_info, 'stream-info.rx-pps'))
                                            list_streams_rx_bps.append(filter_dict(data_streams_info, 'stream-info.rx-bps-l2'))
                                            list_streams_loss.append(filter_dict(data_streams_info, 'stream-info.rx-loss'))
                                            list_streams_direction.append(filter_dict(data_streams_info, 'stream-info.direction'))
                                            list_streams_sessionid.append(filter_dict(data_streams_info, 'stream-info.session-id'))
                                    # Create table for streams dataframe    
                                    table_streams = {
                                        "NAME": list_streams_name,
                                        "FLOW-ID": list_streams_flowid,
                                        "DIRECTION": list_streams_direction,
                                        "SESSION-ID": list_streams_sessionid, 
                                        "TX(pps)": list_streams_tx_pps,
                                        "TX(bps)": list_streams_tx_bps,
                                        "RX(pps)": list_streams_rx_pps,
                                        "RX(bps)": list_streams_rx_bps,
                                        "PKT-LOSS(pkts)": list_streams_loss,
                                    }
                                    exec("display_streams_%s.dataframe(table_streams, column_config={ },use_container_width=True)"%i)
                            if run_command_nw_int_sc == 200:
                                # add_nw_df = pd.DataFrame([[filter_dict(data_nw_int, 'network-interfaces.0.tx-packets'), filter_dict(data_nw_int, 'network-interfaces.0.rx-packets')]], columns=(["network_tx_packets", "network_rx_packets"]))
                                # eval(f'nw_int_chart_{i}.add_rows(add_nw_df)')
                                # num_nw_int=len(data_nw_int['network-interfaces'])
                                for j in range(num_nw_int):
                                    add_nw_pps_df = pd.DataFrame([[filter_dict(data_nw_int, 'network-interfaces.%s.tx-pps'%j), filter_dict(data_nw_int, 'network-interfaces.%s.rx-pps'%j)]], columns=(["network_tx_pps", "network_rx_pps"]))
                                    eval(f'nw_int_chart_{i}_{j}_pps.add_rows(add_nw_pps_df)')
                            if run_command_acc_int_sc == 200:
                                for j in range(num_acc_int):
                                    add_acc_pps_df = pd.DataFrame([[filter_dict(data_acc_int, 'access-interfaces.%s.tx-pps'%j), filter_dict(data_acc_int, 'access-interfaces.%s.rx-pps'%j)]], columns=(["access_tx_pps", "access_rx_pps"]))
                                    eval(f'acc_int_chart_{i}_{j}_pps.add_rows(add_acc_pps_df)')
                        # time.sleep(0.5)
#################### Function for copy dict by path ####################################
def get_value_by_path(root, path):
    current = root
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and key < len(current):
            current = current[key]
        else:
            # Path does not exist
            return None
    return current
def pick_elements_by_multipath(data, paths):
    """
    Recursively keep only elements at exact specified multiple paths in a nested dict or list of dicts,
    removing all other elements.
    """

    def merge_values(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            merged = a.copy()
            for k in b:
                if k in merged:
                    merged[k] = merge_values(merged[k], b[k])
                else:
                    merged[k] = b[k]
            return merged
        return b  # Overwrite otherwise

    if not paths or data is None:
        return {} if isinstance(data, dict) else []

    if isinstance(data, dict):
        result = {}
        grouped_paths = {}
        for path in paths:
            if not path:
                continue
            key = path[0]
            grouped_paths.setdefault(key, []).append(path[1:])
        for key, subpaths in grouped_paths.items():
            if key in data:
                if any(subpaths):  # not all empty
                    value = pick_elements_by_multipath(data[key], subpaths)
                else:
                    value = data[key]
                if key in result:
                    result[key] = merge_values(result[key], value)
                else:
                    result[key] = value
        return result

    elif isinstance(data, list):
        index_paths = {}
        for path in paths:
            if not path:
                continue
            try:
                index = int(path[0])
            except (ValueError, TypeError):
                continue
            index_paths.setdefault(index, []).append(path[1:])
        
        result = []
        for i in sorted(index_paths):
            if 0 <= i < len(data):
                if any(index_paths[i]):
                    value = pick_elements_by_multipath(data[i], index_paths[i])
                else:
                    value = data[i]
                result.append(value)
        return result

    return data
def list_all_paths(nested_structure, current_path=None):
    """
    Lists all paths in a nested structure of dictionaries and lists.

    :param nested_structure: The nested structure (dict or list) to search through.
    :param current_path: The current path being constructed (used for recursion).
    :return: A list of paths, where each path is represented as a list of keys/indices.
    """
    if current_path is None:
        current_path = []

    paths = []

    if isinstance(nested_structure, dict):
        for key, value in nested_structure.items():
            new_path = current_path + [key]  # Extend the current path with the new key
            if isinstance(value, (dict, list)):
                paths.extend(list_all_paths(value, new_path))  # Recur for nested structures
            else:
                paths.append(new_path)  # Add the path to the list if it's a leaf node
    elif isinstance(nested_structure, list):
        for index, item in enumerate(nested_structure):
            new_path = current_path + [index]  # Extend the current path with the new index
            if isinstance(item, (dict, list)):
                paths.extend(list_all_paths(item, new_path))  # Recur for nested structures
            else:
                paths.append(new_path)  # Add the path to the list if it's a leaf node

    return paths
def find_list_paths(data, current_path=None):
    if current_path is None:
        current_path = []

    paths = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = current_path + [key]
            if isinstance(value, list):
                paths.append(new_path)
                for i, item in enumerate(value):
                    paths.extend(find_list_paths(item, new_path + [i]))
            elif isinstance(value, dict):
                paths.extend(find_list_paths(value, new_path))

    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = current_path + [i]
            paths.extend(find_list_paths(item, new_path))

    return paths
def pop_empty_structures(nested_structure):
    """
    Removes keys with empty string values, empty dictionaries, and empty lists
    from a nested structure of dictionaries and lists.
    Also removes empty strings, empty dicts, and empty lists from lists.
    :param nested_structure: The nested structure (dict or list) to modify in place.
    """
    if isinstance(nested_structure, dict):
        # Identify keys to pop where value is empty string, empty dict, or empty list
        keys_to_pop = [key for key, value in nested_structure.items() if value == "" or value == {} or value == []]
        for key in keys_to_pop:
            nested_structure.pop(key)
        # Recurse for remaining values
        for key, value in list(nested_structure.items()):  # Use list() to avoid RuntimeError
            pop_empty_structures(value)
    elif isinstance(nested_structure, list):
        # Remove empty string, empty dict, empty list from list in place
        nested_structure[:] = [item for item in nested_structure if not (item == "" or item == {} or item == [])]
        # Recurse over remaining items
        for item in nested_structure:
            pop_empty_structures(item)
def copy_dict_with_empty_values(nested_structure):
    """
    Creates a copy of a nested dictionary with all values set to empty strings.

    :param nested_structure: The nested structure (dict or list) to copy.
    :return: A new nested structure with the same keys but empty string values.
    """
    if isinstance(nested_structure, dict):
        # Create a new dictionary with the same keys and empty string values
        new_dict = {key: copy_dict_with_empty_values(value) for key, value in nested_structure.items()}
        return new_dict
    elif isinstance(nested_structure, list):
        # Create a new list with the same length, filled with empty strings
        return [copy_dict_with_empty_values(item) for item in nested_structure]
    else:
        # For non-dict and non-list values, return an empty string
        return ""
def find_all_paths_by_key(d, target_key, path=None):
    if path is None:
        path = []
    paths = []
    if isinstance(d, dict):
        for key, value in d.items():
            current_path = path + [key]
            if key == target_key:
                paths.append(current_path)
            # Recur into the dictionary or list
            paths.extend(find_all_paths_by_key(value, target_key, current_path))

    elif isinstance(d, list):
        for index, item in enumerate(d):
            current_path = path + [index]
            paths.extend(find_all_paths_by_key(item, target_key, current_path))

    return paths
def find_deepest_element(d, path=None, depth=0, max_depth=0, deepest_element=None):
    if path is None:
        path = []

    if isinstance(d, dict):
        for key, value in d.items():
            current_path = path + [key]
            current_depth = depth + 1
            
            if isinstance(value, (dict, list)):
                # Recur into the dictionary or list
                deepest_element, max_depth = find_deepest_element(value, current_path, current_depth, max_depth, deepest_element)
            else:
                # Check if this is the deepest element found so far
                if current_depth > max_depth:
                    max_depth = current_depth
                    deepest_element = (current_path, value)

    elif isinstance(d, list):
        for index, item in enumerate(d):
            current_path = path + [index]
            deepest_element, max_depth = find_deepest_element(item, current_path, depth, max_depth, deepest_element)

    return deepest_element, max_depth
# deepest_element, max_depth = find_deepest_element(data)
########################################################################################
def list_to_string(list, connector):
    string = ''
    for x in list:
        if isinstance(x,str):
            if x.find('-') == -1:
                string += x+'%s'%connector
            else:
                string += x.replace('-', '_') +'%s'%connector
        else:
            string += str(x) +'%s'%connector
    return string
def convert_str_to_int(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value.isdigit():
                data[key] = int(value)
            else:
                convert_str_to_int(value)
    elif isinstance(data, list):
        for item in data:
            convert_str_to_int(item)
def convert_str_to_float(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and isinstance(value, float):
                data[key] = float(value)
            else:
                convert_str_to_float(value)
    elif isinstance(data, list):
        for item in data:
            convert_str_to_float(item)
def convert_str_to_bool(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and (value == 'False' or value == 'false'):
                data[key] = False
            elif isinstance(value, str) and (value == 'True' or value == 'true'):
                data[key] = True
            else:
                convert_str_to_bool(value)
    elif isinstance(data, list):
        for item in data:
            convert_str_to_bool(item)
def check_stub_dict(data):
    # Check if the input is a dictionary
    if not isinstance(data, dict):
        return False
    
    # Iterate through the dictionary items
    for key, value in data.items():
        # Check if the value is a dictionary
        if isinstance(value, dict):
            return False  # Found a nested dictionary
        # Check if the value is a list
        elif isinstance(value, list):
            return False  # Found a list, which is not allowed
    return True  # No nested dictionaries or lists
def dict_selection_part_UI(data, key_up_level, number_column, number_key=0, indices=[]):
    with eval("col%s"%number_column):
        with st.container(border=True):
            selection= st.multiselect(
                ":green[:material/add: Level %s]"%number_column,
                data.keys(),
                key="%s_%s_%s_%s"%(num_col,number_key,key_up_level, list_to_string(indices,'_'))
            )
            for i in selection:
                indices.append(i)
                with st.container(border=True):
                    if isinstance(data[i], dict):
                        with eval("col%s"%(number_column+1)):
                            # st.write(":violet[:material/add: OPTIONS OF **%s/%s**]"%(key_up_level.upper(),i.upper()))
                            st.write(":violet[:material/account_tree: **%s**]"%(indices))
                            dict_selection_part_UI(data[i], i, (number_column+1), "%s_%s"%(number_key,i), indices)
                    elif isinstance(data[i], list):
                        with eval("col%s"%(number_column+1)):
                            with st.container(border=True):
                                varload = list_to_string(indices, '___') # for using in command below
                                # st.write(':violet[:material/add: LIST OF **%s/%s**]'%(key_up_level.upper(),i.upper()))
                                st.write(':violet[:material/account_tree: **%s**]'%(indices))
                                exec("num_%s = st.number_input(':blue[:material/add: Number **%s/%s**]', min_value=1, max_value=100, step=1, key= '%s_%s_%s')"%(varload,key_up_level,i, key_up_level,number_key,i))
                                access_var=""
                                for ind in indices:
                                    access_var += "['%s']"%ind
                            for p in eval("range(num_%s)"%varload):
                                indices.append(p)
                                st.write(":orange[:material/add: **%s/%s** number **%s** :]"%(key_up_level,i,p))
                                dict_selection_part_UI(data[i][0], "%s_%s"%(i,p), number_column+1, "%s_%s"%(i,p), indices)
                                indices.pop(indices.index(p))
                    elif isinstance(data[i], str):
                        with eval("col%s"%(number_column)):
                            if data[i].find(':') != -1 and (data[i].split(':')[0]).find(',') != -1: # Condition for recognize "1, 1:10"
                                with st.container(border=True):
                                    varload = list_to_string(indices, '___') # for using in command below
                                    start= int(data[i].split(',')[1].split(':')[0])
                                    end= int(data[i].split(',')[1].split(':')[1])
                                    list_input= list(range(start, end))
                                    exec("%s=st.selectbox(':orange[:material/add: Choose **%s** (default=%s)]', range(%s,%s), index=%s, key= 'sb1_%s_%s_%s')"%(varload,i, data[i].split(',')[0], start, end, list_input.index(int(data[i].split(',')[0])) ,i,number_key,i ))
                            else:
                                with st.container(border=True):
                                    if data[i] == "": # Condition for recognize empty ""
                                        varload = list_to_string(indices, '___') # for using in command below
                                        exec("%s=st.text_input(':orange[:material/add: Typing **%s**]', key='%s_%s')"%(varload, i,number_key,i ))
                                    elif data[i].find(',') != -1 and (data[i].split(',')[0]).find(':') != -1 and (data[i].split(',')[1]).find(':') != -1: # Condition for recognize empty "1:1 , N:1"
                                        varload = list_to_string(indices, '___') # for using in command below
                                        exec("%s=st.selectbox(':orange[:material/add: Choose **%s**]', data[i].split(','), key='%s_%s')"%(varload, i,number_key,i))
                                    elif data[i] == 'interface_auto':
                                        st.write(':orange[:material/add: Select **interface**]')
                                        varload = list_to_string(indices, '___') # for using in command below
                                        intf,vlan =st.columns([1,1])
                                        with intf:
                                            with st.container(border=True):
                                                interface = st.selectbox(f":green[:material/share: interface]", find_interface(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd']), key = 'intf_%s_%s'%(indices,number_key) )
                                        with vlan:
                                            with st.container(border=True):
                                                vlan = st.selectbox(f":green[:material/link: vlan]", find_unused_vlans(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'], interface),key = 'vlan_%s_%s'%(indices,number_key))
                                        exec("%s= '%s.%s' "%(varload,interface,vlan))
                                    elif data[i] == 'ipv4_mask':
                                        st.write(':orange[:material/add: Select **%s**]'%i, key= 'txt'+list_to_string(indices, '/'))
                                        varload = list_to_string(indices, '___') # for using in command below
                                        with st.popover(':green[:material/open_in_full: ipv4 with mask]', use_container_width=True):
                                            with st.container(border=True):
                                                o1 = st.selectbox(f":green[Octet1]", range(0,256), key='o1'+list_to_string(indices, '_'))
                                            with st.container(border=True):
                                                o2 = st.selectbox(f":green[Octet2]", range(0,256), key='o2'+list_to_string(indices, '_'))
                                            with st.container(border=True):
                                                o3 = st.selectbox(f":green[Octet3]", range(0,256), key='o3'+list_to_string(indices, '_'))
                                            with st.container(border=True):
                                                o4 = st.selectbox(f":green[Octet4]", range(0,256), key='o4'+list_to_string(indices, '_'))
                                            with st.container(border=True):
                                                mask = st.selectbox(f":green[SubnetMask]", range(0,33), index= 32, key='mask'+list_to_string(indices, '_'))
                                        exec("%s= '%s.%s.%s.%s/%s' "%(varload,o1,o2,o3,o4,mask))
                                    elif data[i] == 'ipv4':
                                        st.write(':orange[:material/add: Select **%s**]'%i, key= 'txt'+list_to_string(indices, '/'))
                                        varload = list_to_string(indices, '___') # for using in command below
                                        with st.popover(':green[:material/open_in_full: ipv4]', use_container_width=True):
                                            with st.container(border=True):
                                                o1 = st.selectbox(f":green[Octet1]", range(0,256), key='o1'+list_to_string(indices, '_'))
                                            with st.container(border=True):
                                                o2 = st.selectbox(f":green[Octet2]", range(0,256), key='o2'+list_to_string(indices, '_'))
                                            with st.container(border=True):
                                                o3 = st.selectbox(f":green[Octet3]", range(0,256), key='o3'+list_to_string(indices, '_'))
                                            with st.container(border=True):
                                                o4 = st.selectbox(f":green[Octet4]", range(0,256), key='o4'+list_to_string(indices, '_'))
                                        exec("%s= '%s.%s.%s.%s' "%(varload,o1,o2,o3,o4))
                                    elif data[i] == 'ipv6':
                                        st.write(':orange[:material/add: Select **%s**]'%i, key= 'txt'+list_to_string(indices, '/'))
                                        varload = list_to_string(indices, '___') # for using in command below
                                        with st.popover(':green[:material/open_in_full: ipv6]', use_container_width=True):
                                            ipv6_selection= list(range(0,10)) + ['a','b','c','d','e','f']
                                            exec("%s = '' "%varload)
                                            for octet in range(1,9):
                                                st.write('**:orange[:material/add: Select octet %s]**'%octet)
                                                ipv61,ipv62,ipv63,ipv64=st.columns([1,1,1,1])
                                                with ipv61:
                                                    exec("o%s_1 = st.selectbox(f':green[Fist]', ipv6_selection, index=0, key='o%s_1_' + list_to_string(indices, '_'))"%(octet, octet))
                                                with ipv62:
                                                    exec("o%s_2 = st.selectbox(f':green[Second]', ipv6_selection, index=0,key='o%s_2_' +list_to_string(indices, '_'))"%(octet, octet))
                                                with ipv63:
                                                    exec("o%s_3 = st.selectbox(f':green[Third]', ipv6_selection, index=0,key='o%s_3_' +list_to_string(indices, '_'))"%(octet, octet))
                                                with ipv64:
                                                    exec("o%s_4 = st.selectbox(f':green[Fourth]', ipv6_selection, index=0,key='o%s_4_' +list_to_string(indices, '_'))"%(octet, octet))
                                                exec("temp = str(o%s_1) + str(o%s_2) + str(o%s_3) + str(o%s_4)"%(octet,octet,octet,octet))
                                                if octet != 8:
                                                    exec("%s += str(temp)+ ':' "%varload)
                                                else:
                                                    exec("%s += str(temp) "%varload)
                                    elif data[i] == 'ipv6_mask':
                                        st.write(':orange[:material/add: Select **%s**]'%i, key= 'txt'+list_to_string(indices, '/'))
                                        varload = list_to_string(indices, '___') # for using in command below
                                        with st.popover(':green[:material/open_in_full: ipv6 with mask]', use_container_width=True):
                                            ipv6_selection= list(range(0,10)) + ['a','b','c','d','e','f']
                                            exec("%s = '' "%varload)
                                            for octet in range(1,9):
                                                st.write('**:orange[:material/add: Select octet %s]**'%octet)
                                                ipv61,ipv62,ipv63,ipv64=st.columns([1,1,1,1])
                                                with ipv61:
                                                    exec("o%s_1 = st.selectbox(f':green[Fist]', ipv6_selection, index=0, key='o%s_1_' + list_to_string(indices, '_'))"%(octet, octet))
                                                with ipv62:
                                                    exec("o%s_2 = st.selectbox(f':green[Second]', ipv6_selection, index=0,key='o%s_2_' +list_to_string(indices, '_'))"%(octet, octet))
                                                with ipv63:
                                                    exec("o%s_3 = st.selectbox(f':green[Third]', ipv6_selection, index=0,key='o%s_3_' +list_to_string(indices, '_'))"%(octet, octet))
                                                with ipv64:
                                                    exec("o%s_4 = st.selectbox(f':green[Fourth]', ipv6_selection, index=0,key='o%s_4_' +list_to_string(indices, '_'))"%(octet, octet))
                                                exec("temp = str(o%s_1) + str(o%s_2) + str(o%s_3) + str(o%s_4)"%(octet,octet,octet,octet))
                                                if octet != 8:
                                                    exec("%s += str(temp)+ ':' "%varload)
                                                else:
                                                    exec("%s += str(temp) "%varload)
                                            st.write('**:orange[:material/add: Mask]**')
                                            ipv6_mask= st.selectbox(f':green[Choose ipv6 mask]', range(0,129), index=128 , key='ipv6_mask' +list_to_string(indices, '_'))
                                            exec("%s += '/'+ str(ipv6_mask) "%varload)
                                    else:
                                        varload = list_to_string(indices, '___') # for using in command below
                                        exec("%s=st.selectbox(':orange[:material/add: Choose **%s**]', data[i].split(','), key='%s_%s')"%(varload, i,number_key,i))
                    else:
                        st.write(data[i])   
                indices.pop(indices.index(i))  
    dict_var_locals=locals() # Get list vars local functions
    for i in dict_var_locals.keys():
        if '___' in i:
            dict_var[i] = dict_var_locals[i]
def dict_selection_part_UI_new(data, key_up_level, number_column, number_key=0, indices=[]):
    with eval("col%s"%number_column):
        with st.container(border=True):
            #### Pop element is attribute
            list_options=[]
            for e in data.keys():
                if '__' not in e:
                    list_options.append(e)
            selection= st.multiselect(
                ":green[:material/add: Level %s]"%number_column,
                list_options,
                key="%s_%s_%s_%s"%(num_col,number_key,key_up_level, list_to_string(indices,'_'))
            )
            for i in selection:
                indices.append(i)
                with st.container(border=True):
                    if isinstance(data[i], dict):
                        if '__value' not in data[i].keys():
                            with eval("col%s"%(number_column+1)):
                                # st.write(":violet[:material/add: OPTIONS OF **%s/%s**]"%(key_up_level.upper(),i.upper()))
                                st.write(":violet[:material/account_tree: **%s**]"%(indices))
                                dict_selection_part_UI_new(data= data[i], key_up_level= i, number_column=(number_column+1), number_key="%s_%s"%(number_key,i), indices=indices)
                        else:
                            widget_type = data[i]["__widget"]
                            label = data[i]["__label"]
                            value = data[i]["__value"]
                            options = data[i]["__options"]
                            data_type= data[i]["__datatype"]
                            full_key = f"{list_to_string(indices, '_')}_{i}"
                            if widget_type == "text_input":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.text_input(':orange[:material/add: **%s**]', value=value, key=full_key)"%(varload, label))
                                if data_type == 'int' or data_type == 'float': 
                                    exec("%s = %s(%s)"%(varload, data_type, varload))
                            elif widget_type == "selectbox":
                                varload = list_to_string(indices, '___') # for using in command below
                                index = options.index(value) if value in options else 0
                                exec("%s = st.selectbox(':orange[:material/add: **%s**]', options=options, index=index, key=full_key)"%(varload, label))
                            elif widget_type == "multiselect":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.multiselect(':orange[:material/add: **%s**]', options=options, default=value or [], key=full_key)"%(varload,label))
                            elif widget_type == "checkbox":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.checkbox(':orange[:material/add: **%s**]', value=bool(value), key=full_key)"%(varload,label))
                            elif widget_type == "number_input":
                                varload = list_to_string(indices, '___') # for using in command below
                                min_value = options['__min']
                                max_value = options['__max']
                                step = options['__step']
                                exec("%s = st.number_input(':orange[:material/add: **%s**]', min_value=min_value, max_value=max_value, value=value or 0, step=step, key=full_key)"%(varload, label))
                            elif widget_type == "text_area":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s=st.text_area(':orange[:material/add: **%s**]', value=value or '', key=full_key)"%(varload,label))
                            elif widget_type == "file_uploader":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.file_uploader(':orange[:material/add: **%s**]', key=full_key).name"%(varload,label))
                            elif widget_type == "slider":
                                varload = list_to_string(indices, '___') # for using in command below
                                min_value = options['__min']
                                max_value = options['__max']
                                exec("%s = st.slider(':orange[:material/add: **%s**]', min_value=min_value, max_value=max_value, value=value or 0, key=full_key)"%(varload,label))
                            elif widget_type == "customize":
                                if data[i]['__datatype'] == 'interface_auto':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'])
                                    varload = list_to_string(indices, '___') # for using in command below
                                    intf,vlan =st.columns([1,1])
                                    with intf:
                                        interface = st.selectbox(f":green[:material/share: interface]", find_interface(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd']), key = 'intf_%s_%s'%(indices,number_key) )
                                    with vlan:
                                        vlan = st.selectbox(f":green[:material/link: vlan]", find_unused_vlans(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'], interface),key = 'vlan_%s_%s'%(indices,number_key))
                                    exec("%s= '%s.%s' "%(varload,interface,vlan))
                                elif data[i]['__datatype'] == 'ipv4_mask':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv4 with mask]', use_container_width=True):
                                        with st.container(border=True):
                                            o1 = st.selectbox(f":green[Octet1]", range(0,256), key='o1'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o2 = st.selectbox(f":green[Octet2]", range(0,256), key='o2'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o3 = st.selectbox(f":green[Octet3]", range(0,256), key='o3'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o4 = st.selectbox(f":green[Octet4]", range(0,256), key='o4'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            mask = st.selectbox(f":green[SubnetMask]", range(0,33), index= 32, key='mask'+list_to_string(indices, '_'))
                                    exec("%s= '%s.%s.%s.%s/%s' "%(varload,o1,o2,o3,o4,mask))
                                elif data[i]['__datatype'] == 'ipv4':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv4]', use_container_width=True):
                                        with st.container(border=True):
                                            o1 = st.selectbox(f":green[Octet1]", range(0,256), key='o1'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o2 = st.selectbox(f":green[Octet2]", range(0,256), key='o2'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o3 = st.selectbox(f":green[Octet3]", range(0,256), key='o3'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o4 = st.selectbox(f":green[Octet4]", range(0,256), key='o4'+list_to_string(indices, '_'))
                                    exec("%s= '%s.%s.%s.%s' "%(varload,o1,o2,o3,o4))
                                elif data[i]['__datatype'] == 'ipv6':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv6]', use_container_width=True):
                                        ipv6_selection= list(range(0,10)) + ['a','b','c','d','e','f']
                                        exec("%s = '' "%varload)
                                        for octet in range(1,9):
                                            st.write('**:orange[:material/add: Select octet %s]**'%octet)
                                            ipv61,ipv62,ipv63,ipv64=st.columns([1,1,1,1])
                                            with ipv61:
                                                exec("o%s_1 = st.selectbox(f':green[Fist]', ipv6_selection, index=0, key='o%s_1_' + list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv62:
                                                exec("o%s_2 = st.selectbox(f':green[Second]', ipv6_selection, index=0,key='o%s_2_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv63:
                                                exec("o%s_3 = st.selectbox(f':green[Third]', ipv6_selection, index=0,key='o%s_3_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv64:
                                                exec("o%s_4 = st.selectbox(f':green[Fourth]', ipv6_selection, index=0,key='o%s_4_' +list_to_string(indices, '_'))"%(octet, octet))
                                            exec("temp = str(o%s_1) + str(o%s_2) + str(o%s_3) + str(o%s_4)"%(octet,octet,octet,octet))
                                            if octet != 8:
                                                exec("%s += str(temp)+ ':' "%varload)
                                            else:
                                                exec("%s += str(temp) "%varload)
                                elif data[i]['__datatype'] == 'ipv6_mask':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv6 with mask]', use_container_width=True):
                                        ipv6_selection= list(range(0,10)) + ['a','b','c','d','e','f']
                                        exec("%s = '' "%varload)
                                        for octet in range(1,9):
                                            st.write('**:orange[:material/add: Select octet %s]**'%octet)
                                            ipv61,ipv62,ipv63,ipv64=st.columns([1,1,1,1])
                                            with ipv61:
                                                exec("o%s_1 = st.selectbox(f':green[Fist]', ipv6_selection, index=0, key='o%s_1_' + list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv62:
                                                exec("o%s_2 = st.selectbox(f':green[Second]', ipv6_selection, index=0,key='o%s_2_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv63:
                                                exec("o%s_3 = st.selectbox(f':green[Third]', ipv6_selection, index=0,key='o%s_3_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv64:
                                                exec("o%s_4 = st.selectbox(f':green[Fourth]', ipv6_selection, index=0,key='o%s_4_' +list_to_string(indices, '_'))"%(octet, octet))
                                            exec("temp = str(o%s_1) + str(o%s_2) + str(o%s_3) + str(o%s_4)"%(octet,octet,octet,octet))
                                            if octet != 8:
                                                exec("%s += str(temp)+ ':' "%varload)
                                            else:
                                                exec("%s += str(temp) "%varload)
                                        st.write('**:orange[:material/add: Mask]**')
                                        ipv6_mask= st.selectbox(f':green[Choose ipv6 mask]', range(0,129), index=128 , key='ipv6_mask' +list_to_string(indices, '_'))
                                        exec("%s += '/'+ str(ipv6_mask) "%varload)
                                else:
                                    varload = list_to_string(indices, '___') # for using in command below
                                    exec("%s=st.selectbox(':orange[:material/add: Choose **%s**]', data[i].split(','), key='%s_%s')"%(varload, i,number_key,i))
                            else:
                                st.warning(f"Unsupported widget type: {widget_type} (field: {key})")
                    elif isinstance(data[i], list):
                        with eval("col%s"%(number_column+1)):
                            with st.container(border=True):
                                varload = list_to_string(indices, '___') # for using in command below
                                st.write(':violet[:material/account_tree: **%s**]'%(indices))
                                exec("num_%s = st.number_input(':blue[:material/add: Number **%s/%s**]', min_value=1, max_value=100, step=1, key= '%s_%s_%s')"%(varload,key_up_level,i, key_up_level,number_key,i))
                                access_var=""
                                for ind in indices:
                                    access_var += "['%s']"%ind
                            for p in eval("range(num_%s)"%varload):
                                indices.append(p)
                                st.write(":orange[:material/add: **%s/%s** number **%s** :]"%(key_up_level,i,p))
                                dict_selection_part_UI_new(data[i][0], "%s_%s"%(i,p), number_column+1, "%s_%s"%(i,p), indices)
                                indices.pop(indices.index(p))
                    else:
                        st.write(data[i])   
                indices.pop(indices.index(i))  
    dict_var_locals=locals() # Get list vars local functions
    for i in dict_var_locals.keys():
        if '___' in i:
            dict_var[i] = dict_var_locals[i]
def dict_selection_part_UI_edit(data, key_up_level, number_column, number_key=0, indices=[]):
    with eval("col%s"%number_column):
        with st.container(border=True):
            #### Pop element is attribute
            list_options=[]
            for e in data.keys():
                if '__' not in e:
                    list_options.append(e)
            selection= st.multiselect(
                ":green[:material/add: Level %s]"%number_column,
                list_options,
                list(data.keys()),
                key="%s_%s_%s_%s"%(num_col,number_key,key_up_level, list_to_string(indices,'_'))
            )
            for i in selection:
                indices.append(i)
                with st.container(border=True):
                    if isinstance(data[i], dict):
                        if '__value' not in data[i].keys():
                            with eval("col%s"%(number_column+1)):
                                # st.write(":violet[:material/add: OPTIONS OF **%s/%s**]"%(key_up_level.upper(),i.upper()))
                                st.write(":violet[:material/account_tree: **%s**]"%(indices))
                                dict_selection_part_UI_edit(data= data[i], key_up_level= i, number_column=(number_column+1), number_key="%s_%s"%(number_key,i), indices=indices)
                        else:
                            widget_type = data[i]["__widget"]
                            label = data[i]["__label"]
                            value = data[i]["__value"]
                            options = data[i]["__options"]
                            data_type = data[i]["__datatype"]
                            full_key = f"{list_to_string(indices, '_')}_{i}"
                            if widget_type == "text_input":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.text_input(':orange[:material/add: **%s**]', value=value, key=full_key)"%(varload, label))
                                if data_type == 'int' or data_type == 'float':
                                    exec("%s = %s(%s)"%(varload, data_type, varload))
                            elif widget_type == "selectbox":
                                varload = list_to_string(indices, '___') # for using in command below
                                index = options.index(value) if value in options else 0
                                exec("%s = st.selectbox(':orange[:material/add: **%s**]', options=options, index=index, key=full_key)"%(varload, label))
                            elif widget_type == "multiselect":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.multiselect(':orange[:material/add: **%s**]', options=options, default=value or [], key=full_key)"%(varload,label))
                            elif widget_type == "checkbox":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.checkbox(':orange[:material/add: **%s**]', value=bool(value), key=full_key)"%(varload,label))
                            elif widget_type == "number_input":
                                varload = list_to_string(indices, '___') # for using in command below
                                min_value = options['__min']
                                max_value = options['__max']
                                step = options['__step']
                                exec("%s = st.number_input(':orange[:material/add: **%s**]', min_value=min_value, max_value=max_value, value=value or 0, step=step, key=full_key)"%(varload, label))
                            elif widget_type == "text_area":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s=st.text_area(':orange[:material/add: **%s**]', value=value or '', key=full_key)"%(varload,label))
                            elif widget_type == "file_uploader":
                                varload = list_to_string(indices, '___') # for using in command below
                                exec("%s = st.file_uploader(':orange[:material/add: **%s**]', key=full_key).name"%(varload,label))
                            elif widget_type == "slider":
                                varload = list_to_string(indices, '___') # for using in command below
                                min_value = options['__min']
                                max_value = options['__max']
                                exec("%s = st.slider(':orange[:material/add: **%s**]', min_value=min_value, max_value=max_value, value=value or 0, key=full_key)"%(varload,label))
                            elif widget_type == "customize":
                                if data[i]['__datatype'] == 'interface_auto':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'])
                                    varload = list_to_string(indices, '___') # for using in command below
                                    intf,vlan =st.columns([1,1])
                                    with intf:
                                        interface = st.selectbox(f":green[:material/share: interface]", find_interface(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd']), key = 'intf_%s_%s'%(indices,number_key) )
                                    with vlan:
                                        vlan = st.selectbox(f":green[:material/link: vlan]", find_unused_vlans(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'], interface),key = 'vlan_%s_%s'%(indices,number_key))
                                    exec("%s= '%s.%s' "%(varload,interface,vlan))
                                elif data[i]['__datatype'] == 'ipv4_mask':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv4 with mask]', use_container_width=True):
                                        with st.container(border=True):
                                            o1 = st.selectbox(f":green[Octet1]", range(0,256), key='o1'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o2 = st.selectbox(f":green[Octet2]", range(0,256), key='o2'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o3 = st.selectbox(f":green[Octet3]", range(0,256), key='o3'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o4 = st.selectbox(f":green[Octet4]", range(0,256), key='o4'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            mask = st.selectbox(f":green[SubnetMask]", range(0,33), index= 32, key='mask'+list_to_string(indices, '_'))
                                    exec("%s= '%s.%s.%s.%s/%s' "%(varload,o1,o2,o3,o4,mask))
                                elif data[i]['__datatype'] == 'ipv4':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv4]', use_container_width=True):
                                        with st.container(border=True):
                                            o1 = st.selectbox(f":green[Octet1]", range(0,256), key='o1'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o2 = st.selectbox(f":green[Octet2]", range(0,256), key='o2'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o3 = st.selectbox(f":green[Octet3]", range(0,256), key='o3'+list_to_string(indices, '_'))
                                        with st.container(border=True):
                                            o4 = st.selectbox(f":green[Octet4]", range(0,256), key='o4'+list_to_string(indices, '_'))
                                    exec("%s= '%s.%s.%s.%s' "%(varload,o1,o2,o3,o4))
                                elif data[i]['__datatype'] == 'ipv6':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv6]', use_container_width=True):
                                        ipv6_selection= list(range(0,10)) + ['a','b','c','d','e','f']
                                        exec("%s = '' "%varload)
                                        for octet in range(1,9):
                                            st.write('**:orange[:material/add: Select octet %s]**'%octet)
                                            ipv61,ipv62,ipv63,ipv64=st.columns([1,1,1,1])
                                            with ipv61:
                                                exec("o%s_1 = st.selectbox(f':green[Fist]', ipv6_selection, index=0, key='o%s_1_' + list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv62:
                                                exec("o%s_2 = st.selectbox(f':green[Second]', ipv6_selection, index=0,key='o%s_2_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv63:
                                                exec("o%s_3 = st.selectbox(f':green[Third]', ipv6_selection, index=0,key='o%s_3_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv64:
                                                exec("o%s_4 = st.selectbox(f':green[Fourth]', ipv6_selection, index=0,key='o%s_4_' +list_to_string(indices, '_'))"%(octet, octet))
                                            exec("temp = str(o%s_1) + str(o%s_2) + str(o%s_3) + str(o%s_4)"%(octet,octet,octet,octet))
                                            if octet != 8:
                                                exec("%s += str(temp)+ ':' "%varload)
                                            else:
                                                exec("%s += str(temp) "%varload)
                                elif data[i]['__datatype'] == 'ipv6_mask':
                                    st.write(':orange[:material/add: **%s**]'%data[i]['__label'], key= 'txt'+list_to_string(indices, '/'))
                                    varload = list_to_string(indices, '___') # for using in command below
                                    with st.popover(':green[:material/open_in_full: ipv6 with mask]', use_container_width=True):
                                        ipv6_selection= list(range(0,10)) + ['a','b','c','d','e','f']
                                        exec("%s = '' "%varload)
                                        for octet in range(1,9):
                                            st.write('**:orange[:material/add: Select octet %s]**'%octet)
                                            ipv61,ipv62,ipv63,ipv64=st.columns([1,1,1,1])
                                            with ipv61:
                                                exec("o%s_1 = st.selectbox(f':green[Fist]', ipv6_selection, index=0, key='o%s_1_' + list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv62:
                                                exec("o%s_2 = st.selectbox(f':green[Second]', ipv6_selection, index=0,key='o%s_2_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv63:
                                                exec("o%s_3 = st.selectbox(f':green[Third]', ipv6_selection, index=0,key='o%s_3_' +list_to_string(indices, '_'))"%(octet, octet))
                                            with ipv64:
                                                exec("o%s_4 = st.selectbox(f':green[Fourth]', ipv6_selection, index=0,key='o%s_4_' +list_to_string(indices, '_'))"%(octet, octet))
                                            exec("temp = str(o%s_1) + str(o%s_2) + str(o%s_3) + str(o%s_4)"%(octet,octet,octet,octet))
                                            if octet != 8:
                                                exec("%s += str(temp)+ ':' "%varload)
                                            else:
                                                exec("%s += str(temp) "%varload)
                                        st.write('**:orange[:material/add: Mask]**')
                                        ipv6_mask= st.selectbox(f':green[Choose ipv6 mask]', range(0,129), index=128 , key='ipv6_mask' +list_to_string(indices, '_'))
                                        exec("%s += '/'+ str(ipv6_mask) "%varload)
                                else:
                                    varload = list_to_string(indices, '___') # for using in command below
                                    exec("%s=st.selectbox(':orange[:material/add: Choose **%s**]', data[i].split(','), key='%s_%s')"%(varload, i,number_key,i))
                            else:
                                st.warning(f"Unsupported widget type: {widget_type} (field: {key})")
                    elif isinstance(data[i], list):
                        with eval("col%s"%(number_column+1)):
                            for num_list in range(len(data[i])):
                                with st.container(border=True):
                                    # st.write(':violet[:material/add: LIST OF **%s/%s**]'%(key_up_level.upper(),i.upper()))
                                    st.write(':violet[:material/account_tree: **%s**]'%(indices))
                                    indices.append(num_list)
                                    st.write(":orange[:material/add: **%s/%s** number **%s** :]"%(key_up_level,i,num_list))
                                    dict_selection_part_UI_edit(data=data[i][num_list], key_up_level="%s_%s"%(i,num_list), number_column=number_column+1, number_key="%s_%s"%(i,num_list), indices=indices)
                                    indices.pop(indices.index(num_list))
                    else:
                        st.write(':orange[:material/check: **%s** =] :green[%s]'%(i, data[i]))  
                indices.pop(indices.index(i))  
    dict_var_locals=locals() # Get list vars local functions
    for i in dict_var_locals.keys():
        if '___' in i:
            dict_var[i] = dict_var_locals[i]
################################ Start PAGE #############################################
if st.session_state.p1:
    col30,col31,col33= st.columns([2,3,2])
    with st.container(border= True):
        with col31:
            with st.container(border= True):
                st.write(f":material/storage: :orange[*PROVIDE YOUR BNG-BLASTER INFO*]")
                st.session_state.ip_blaster = st.selectbox(':green[IP_BLASTER] ',dict_blaster_db_format.keys(), placeholder = 'Typing your IP')
                st.session_state.port_blaster = st.text_input(':green[PORT_BLASTER] ',8001, placeholder = 'Typing your PORT')
                if dict_user_db[st.session_state.user] == 'admin1' or dict_user_db[st.session_state.user] == 'admin':
                    with st.expander(':blue[ADD NEW BNG-BLASTER CONTROLLER]'):
                        blaster_new_ip = st.text_input(':green[NEW BLASTER IP] ', placeholder = 'Typing your IP')
                        blaster_new_port = st.text_input(':green[NEW BLASTER PORT] ',8001, placeholder = 'Typing your PORT')
                        blaster_new_user = st.text_input(':green[NEW BLASTER USERNAME] ', placeholder = 'Typing your USERNAME')
                        blaster_new_passwd = st.text_input(':green[NEW BLASTER PASSWORD] ', placeholder = 'Typing your PASSWORD', type='password')
                        if st.button(":orange[:material/add: **ADD NEW BLASTER**]"):
                            # conn = sqlite_connect_to_db(db_name)
                            # sqlite_insert_user(conn, user, user_class)
                            db = DatabaseConnection()
                            conn=db.connection
                            # sqlite_insert_blaster(conn, blaster_new_ip, blaster_new_port, blaster_new_user, blaster_new_passwd)
                            temp_blaster_insert = {'ip': blaster_new_ip, 'port': blaster_new_port, 'user': blaster_new_user, 'passwd': blaster_new_passwd}
                            db.insert('blasters', temp_blaster_insert)
                            conn.close()
                            st.info(":green[Add successfully]")
                            time.sleep(2)
                            st.rerun()
            log_authorize(st.session_state.user, st.session_state.ip_blaster , f'Select BNG-Blaster {st.session_state.ip_blaster}')
################################ LIST ALL INSTANCES (RUNNING +STOP) SERVER #############
blaster_server = {
    'ip': st.session_state.ip_blaster,
    'port': st.session_state.port_blaster,
}
list_instance_running_from_blaster=[]
list_instance_avail_from_blaster=[]
error = False
try:
    list_all_instances_sc, list_all_instances_ct = GET_ALL_INTANCES_BLASTER(blaster_server['ip'], blaster_server['port'])
    list_all_instances =list(json.loads(list_all_instances_ct))
    if list_all_instances_sc == 200:
        for i in list_all_instances:
            instance_exist_st, instance_exist_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'GET', payload_start)
            if "started" in str(instance_exist_ct):
                list_instance_running_from_blaster.append(i)
            else:
                list_instance_avail_from_blaster.append(i)
        for j in list_instance_avail_from_blaster:
            if j == "uploads":
                list_instance_avail_from_blaster.pop(list_instance_avail_from_blaster.index("uploads"))
        log_authorize(st.session_state.user,blaster_server['ip'], f'Success get BNG-Blaster_{st.session_state.ip_blaster} info')
    else:
        st.error('Can not get list-profile from server', icon="🚨")
except Exception as e:
    e1,e2,e3= st.columns([1,2,1])
    with e2:
        st.error(f"Can't get info from your BNG-Blaster server. Choose other Server available", icon="🚨")
        log_authorize(st.session_state.user,blaster_server['ip'], f'Fail get BNG-Blaster_{st.session_state.ip_blaster} info')
        print(f"Check your bng-blaster server.Error **{e}**")
        error = True
if st.session_state.p1:
    with col31:
        if st.button(":material/login: **SELECT**", type= 'primary'):
            if error:
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= True, False, False, False, False
                st.rerun()
            else: 
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
                st.rerun()
#########################################################################################
if st.session_state.p2:
    gif1, gif2, gif3, gif4, gif5, gif6, gif7 = st.columns([0.1,2.1,0.1,1.5,0.1,2.1,0.1])
    with gif2:
        with st.container(border= True):
            gif('./images/one.gif')
            if st.button(':material/first_page: **PRE-RUN**', use_container_width=True):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                log_authorize(st.session_state.user,blaster_server['ip'], 'Select PRE-RUN page')
                st.rerun()
    with gif4:
        with st.container(border= True):
            gif('./images/two.gif')
            if st.button(':material/all_inclusive:  **RUN**', use_container_width=True):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
                log_authorize(st.session_state.user,blaster_server['ip'], 'Select RUN page')
                st.rerun()
    with gif6:
        with st.container(border= True):
            gif('./images/three.gif')
            # if st.button(':chart_with_upwards_trend:  **REPORT**', disabled= True, use_container_width=True):
            if st.button(':material/insights:  **REPORT**', use_container_width=True):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, False, True
                log_authorize(st.session_state.user,blaster_server['ip'], 'Select REPORT page')
                st.rerun()
if st.session_state.p3:
    st.session_state.create_instance = True
    st.title(':material/first_page: :rainbow[ DEFINE FILE CONFIG.JSON]')
    col51, col52 ,col53 =st.columns([19,0.9,0.9])
    with col52:
        if st.button(':material/widgets:', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
            log_authorize(st.session_state.user,blaster_server['ip'], 'Return HOME')
            st.rerun()
    with col53:
        if st.button(':material/all_inclusive: ', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
            log_authorize(st.session_state.user,blaster_server['ip'], 'Change RUN page')
            st.rerun()
    # tab1, tab2, tab3, tab4, tab5= st.tabs([":material/edit_note: CREATE/EDIT BY SELECTION", ":material/note_add: CREATE BY TEMPLATE", ":material/edit_note: MODIFY", ":material/publish: JSON_IMPORT", ":material/note_alt: TEMPLATE"])
    tab1, tab2= st.tabs([":material/edit_note: CREATE/EDIT BY SELECTION",":material/publish: IMPORT/CLONE JSON CONFIG"])
    with tab2: # Tab for import json
        with st.container(border= True):
            col1,col2,col3=st.columns([1,1,1])
            with col2:
                choice_import = st.radio(
                    ":violet[:material/call_split: **SELECT FOR CLONE EXISTED PROFILE OR IMPORT FILE**]",
                    [":green[:material/note_add: **CLONE EXISTED PROFILE**]", ":green[:material/edit_note: **IMPORT FILE**]"],
                    index=None,
                    horizontal=True
                )
        if choice_import == ":green[:material/edit_note: **IMPORT FILE**]":
            col1, col2 = st.columns([1,2])
            with col1:
                with st.container(border=True):
                    name_json_config= st.text_input("**:violet[1. INPUT NAME OF TEST PROFILE]**")
                    data_json_import = st.file_uploader("**:violet[2. CHOOSE YOUR JSON FILE]**", accept_multiple_files=False)
                    if data_json_import:
                        stringio = StringIO(data_json_import.getvalue().decode("utf-8"))
                        string_data = stringio.read()
                        try:
                            input_json = json.loads(string_data)
                            if is_valid_name_instance(name_json_config):
                                # st.write(name_json_config)
                                if (name_json_config+'.json') not in list_json:
                                    # try:
                                    # export_yaml= yaml.dump(input_json)
                                    with col2:
                                        with st.container(border=True):
                                            st.write("**:violet[3. EDIT TEST PROFILE]**")
                                            with st.container(border=True):
                                                convert_json= st_ace(
                                                value= json.dumps(input_json, indent=2),
                                                language= 'json', 
                                                theme= '', 
                                                show_gutter= True, 
                                                keybinding='vscode', 
                                                auto_update= True, 
                                                placeholder= '*Edit your config*')
                                            if st.button("SAVE CONFIG", type= 'primary', use_container_width= True):
                                                # This code for convert json to template yaml
                                                import_paths=list_all_paths(json.loads(convert_json))
                                                with open('all_conf.yml', 'r') as file_template:
                                                    try:
                                                        data=yaml.safe_load(file_template) # This dict is library of bngblaster
                                                    except yaml.YAMLError as exc:
                                                        st.error(exc)
                                                new_dict_import=copy_dict_with_empty_values(json.loads(convert_json))
                                                for i in import_paths:
                                                    if isinstance(i[-1],int):
                                                        i.pop(-1)
                                                    var_access=''
                                                    var_access_data=''
                                                    for e in i:
                                                        if isinstance(e,int):
                                                            var_access+= "[%s]"%e
                                                            if int(e) == 0:
                                                                var_access_data+= "[%s]"%e
                                                            else:
                                                                var_access_data+= "[0]"
                                                        else:
                                                            var_access+= "['%s']"%e
                                                            var_access_data+= "['%s']"%e
                                                    exec("new_dict_import%s=copy.deepcopy(data%s)"%(var_access,var_access_data))
                                                    exec("data_type= new_dict_import%s['__datatype']"%(var_access))
                                                    if data_type == 'int' or data_type == 'float': # This code for case user input integer auto cast into float and divert
                                                        exec("new_dict_import%s['__value']=%s(json.loads(convert_json)%s)"%(var_access,data_type,var_access))
                                                    else:
                                                        exec("new_dict_import%s['__value']=json.loads(convert_json)%s"%(var_access,var_access))
                                                    # For change wdget customize to input text with edit mode
                                                    if eval("new_dict_import%s['__widget'] == 'customize'"%(var_access)):
                                                        exec("new_dict_import%s['__widget']='text_input'"%(var_access))
                                                # Write to template file
                                                write_dict_to_yaml(new_dict_import,'%s/%s.yml'%(path_configs,name_json_config))
                                                # This code for save json config
                                                with open('%s/%s.json'%(path_configs,name_json_config), mode= 'w', encoding= 'utf-8') as json_config:
                                                    json.dump(json.loads(convert_json), json_config, indent=2)
                                                st.success("Config save successfully", icon="🔥")
                                                log_authorize(st.session_state.user,blaster_server['ip'], f'Create new json {name_json_config}')
                                    # except Exception as e:
                                    #     with col2:
                                    #         st.error(f"Can not yaml dump content, check error {e}", icon="🚨")
                                else:
                                    st.error('Name existed', icon="🚨")
                            else:
                                st.error('Name empty or wrong syntax', icon="🚨")
                        except Exception as e:
                            with col2:
                                st.error(f"Can not read json content, check error {e}", icon="🚨")
                        # st.write(list_json)
                    else:
                        st.error('Import file please', icon="🚨")
        if choice_import == ":green[:material/note_add: **CLONE EXISTED PROFILE**]":
            col1, col2 = st.columns([1,2])
            with col1:
                with st.container(border=True):
                    import_clone_new= st.text_input("**:violet[1. NAME OF NEW TEST PROFILE]**")
                    import_clone_instance= st.selectbox("**:violet[2. CHOOSE TEST PROFILE EXISTED]**", list_instance,placeholder = 'Select one test profile')
                    with open("%s/%s.json"%(path_configs,import_clone_instance) , 'r') as edit_config_data:
                        import_clone_json= edit_config_data.read()
                    if import_clone_new:
                        try:
                            input_json = json.loads(import_clone_json)
                            if is_valid_name_instance(import_clone_new):
                                # st.write(name_json_config)
                                if (import_clone_new+'.json') not in list_json:
                                    # try:
                                    # export_yaml= yaml.dump(input_json)
                                    with col2:
                                        with st.container(border=True):
                                            st.write("**:violet[3. EDIT TEST PROFILE]**")
                                            with st.container(border=True):
                                                convert_json= st_ace(
                                                value= json.dumps(input_json, indent=2),
                                                language= 'json', 
                                                theme= '', 
                                                show_gutter= True, 
                                                keybinding='vscode', 
                                                auto_update= True, 
                                                placeholder= '*Edit your config*')
                                            if st.button("SAVE CONFIG", type= 'primary', use_container_width= True):
                                                # This code for convert json to template yaml
                                                import_paths=list_all_paths(json.loads(convert_json))
                                                with open('all_conf.yml', 'r') as file_template:
                                                    try:
                                                        data=yaml.safe_load(file_template) # This dict is library of bngblaster
                                                    except yaml.YAMLError as exc:
                                                        st.error(exc)
                                                new_dict_import=copy_dict_with_empty_values(json.loads(convert_json))
                                                for i in import_paths:
                                                    if isinstance(i[-1],int):
                                                        i.pop(-1)
                                                    var_access=''
                                                    var_access_data=''
                                                    for e in i:
                                                        if isinstance(e,int):
                                                            var_access+= "[%s]"%e
                                                            if int(e) == 0:
                                                                var_access_data+= "[%s]"%e
                                                            else:
                                                                var_access_data+= "[0]"
                                                        else:
                                                            var_access+= "['%s']"%e
                                                            var_access_data+= "['%s']"%e
                                                    exec("new_dict_import%s=copy.deepcopy(data%s)"%(var_access,var_access_data))
                                                    exec("data_type= new_dict_import%s['__datatype']"%(var_access))
                                                    if data_type == 'int' or data_type == 'float': # This code for case user input integer auto cast into float and divert
                                                        exec("new_dict_import%s['__value']=%s(json.loads(convert_json)%s)"%(var_access,data_type,var_access))
                                                    else:
                                                        exec("new_dict_import%s['__value']=json.loads(convert_json)%s"%(var_access,var_access))
                                                    # For change wdget customize to input text with edit mode
                                                    if eval("new_dict_import%s['__widget'] == 'customize'"%(var_access)):
                                                        exec("new_dict_import%s['__widget']='text_input'"%(var_access))
                                                # Write to template file
                                                write_dict_to_yaml(new_dict_import,'%s/%s.yml'%(path_configs,import_clone_new))
                                                # This code for save json config
                                                with open('%s/%s.json'%(path_configs,import_clone_new), mode= 'w', encoding= 'utf-8') as json_config:
                                                    json.dump(json.loads(convert_json), json_config, indent=2)
                                                st.success("Config save successfully", icon="🔥")
                                                log_authorize(st.session_state.user,blaster_server['ip'], f'Create new json {import_clone_new}')
                                    # except Exception as e:
                                    #     with col2:
                                    #         st.error(f"Can not yaml dump content, check error {e}", icon="🚨")
                                else:
                                    st.error('Name existed', icon="🚨")
                            else:
                                st.error('Name wrong syntax', icon="🚨")
                        except Exception as e:
                            with col2:
                                st.error(f"Can not read json content, check error {e}", icon="🚨")
                        # st.write(list_json)
                    else:
                        st.error('Test profile name empty', icon="🚨")
    with tab1:
        with st.container(border= True):
            col1,col2,col3=st.columns([1.5,1,1])
            with col2:
                choice = st.radio(
                    ":violet[:material/call_split: **SELECT FOR CREATE OR EDIT**]",
                    [":green[:material/note_add: **CREATE**]", ":green[:material/edit_note: **EDIT**]"],
                    index=None,
                    horizontal=True
                )
        if choice== ":green[:material/note_add: **CREATE**]": 
            log_authorize(st.session_state.user,blaster_server['ip'], 'Select CREATE')
            with st.container(border= True):
                enable= False
                st.subheader(':sunny: :green[**CREATE YOUR CONFIG**]')
                with st.container(border= True):
                    st.write(':violet[**:material/account_circle: YOUR TEST PROFILE NAME**]')
                    with st.container(border=True):
                        select_instance_name = st.text_input(':orange[Name of your test profile] ', placeholder = 'Typing your test profile name', key='create_by_selection')
                        if is_valid_name_instance(select_instance_name):
                            if select_instance_name + '.json' not in list_json:
                                st.info(':blue[Your test profile\'s name can be use]', icon="🔥")
                                st.session_state.create_instance= False
                                enable= True # Var for display when name instance valid
                            else:
                                st.error('Your test profile was duplicate, choose other name', icon="🚨")
                        else:
                            st.error('Test profile name is null or wrong syntax', icon="🔥")
                if enable:
                    with open('all_conf.yml', 'r') as file_template:
                        try:
                            data=yaml.safe_load(file_template) # This dict is library of bngblaster
                        except yaml.YAMLError as exc:
                            st.error(exc)
                    load_data=copy_dict_with_empty_values(data) # This dict to export json config
                    dict_var={} # Var for save value from UI (define before dict_selection_part_UI_new())
                    ##################### Value of columns dynamic to deep elements of dict ######################
                    _, num_col= find_deepest_element(data)
                    num_col = num_col - 2 # Adjust number column for display UI
                    var_col=""
                    for i in range(num_col):
                        if i == (num_col-1):
                            var_col += "col%s"%i
                        else:
                            var_col += "col%s"%i + ','
                    x=''
                    for i in range(num_col):
                        if i == 0:
                            x += "0.8"
                        else:
                            x += ",1"
                    x='[%s]'%x # This var for modify scale column
                    exec("%s =st.columns(%s, border=True)"%(var_col,x))
                    with col0:
                        st.write(":violet[:material/account_tree: **[BNGBlaster Configs]**]")
                        dict_selection_part_UI_new(data=data, key_up_level="", number_column=0)
                    # st.write(dict_var)
                    if dict_var:
                        #For process len(list of dict)
                        for i,v in dict_var.items(): 
                            if "num_" in i:
                                path_ext= i.split("num_")[1]
                                path= path_ext.split('___')
                                path.remove("")
                                for k in path:
                                    if k.find('_') != -1 and k != '_comment':
                                        path[path.index(k)]=k.replace('_','-')
                                str_path=""
                                for o in path:
                                    if isinstance(o, int):
                                        str_path += "[%s]"%o
                                    else:
                                        str_path += "['%s']"%o
                                for u in range(v-1):
                                    exec("copy%s = data%s"%(u, str_path))
                                    exec("temp_data = copy.deepcopy(copy%s)"%(u))
                                    exec("copy_empty= copy_dict_with_empty_values(copy%s)"%u)
                                    exec("load_data%s.extend(copy_empty)"%(str_path)) # Extend number element list of dict
                                    exec("data%s.extend(temp_data)"%(str_path))
                        #For process input of elements UI
                        path_save=[]
                        for i,v in dict_var.items(): 
                            if "num_" not in i:
                                path= i.split('___')
                                path.remove("")
                                path_save.append(path)
                                for k in path:
                                    if k.find('_') != -1 and k != '_comment':
                                        path[path.index(k)]=k.replace('_','-')
                                    try:
                                        path[path.index(k)]=int(k)
                                    except Exception as e:
                                        # print(e)
                                        continue
                                str_path=""
                                for o in path:
                                    if isinstance(o, int):
                                        str_path += "[%s]"%o
                                    else:
                                        str_path += "['%s']"%o
                                if isinstance(v, int) or isinstance(v, list) or isinstance(v, float):
                                    exec("load_data%s= %s"%(str_path, v))
                                else:
                                    exec("load_data%s= '%s'"%(str_path, v))
                                    
                                if isinstance(v, int) or isinstance(v, list) or isinstance(v, float):
                                    exec("data%s['__value']= %s"%(str_path, v))
                                else:
                                    exec("data%s['__value']= '%s'"%(str_path, v))
                                # st.write("load_data%s= '%s'"%(str_path, v))
                    for i in range(num_col+10): # For remove emptry dict, list, str
                        pop_empty_structures(load_data)
                    with st.popover(':green[**:material/visibility: REVIEW**]', use_container_width=True):
                        convert_str_to_int(load_data)
                        convert_str_to_float(load_data)
                        convert_str_to_bool(load_data)
                        st.code(json.dumps(load_data, indent=2))
                    if st.button(':material/add: **CREATE PROFILE**', type= 'primary', disabled = st.session_state.create_instance, key= 'btn_create_by_selection'):
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4,st.session_state.p5= False,False, True, False, False
                        # if "" not in dict_input.values():
                        with open('%s/%s.json'%(path_configs,select_instance_name), mode= 'w', encoding= 'utf-8') as config:
                            json.dump(load_data, config, indent=2)
                        
                        # Code save value to template for edit
                        dict_save_for_edit=pick_elements_by_multipath(data, path_save)
                        # Change __widget= customize to input_text
                        # st.write(path_save)
                        for path_widget in path_save:
                            str_path=""
                            for o in path_widget:
                                if isinstance(o, int):
                                    str_path += "[%s]"%o
                                else:
                                    str_path += "['%s']"%o
                            if eval("dict_save_for_edit%s['__widget'] == 'customize'"%(str_path)):
                                exec("dict_save_for_edit%s['__widget']= 'text_input'"%(str_path))
                        # st.write(dict_save_for_edit)
                        temp_dict_save_for_edit= json.dumps(dict_save_for_edit)
                        write_dict_to_yaml(yaml.safe_load(temp_dict_save_for_edit),'%s/%s.yml'%(path_configs,select_instance_name))
                        st.info(':blue[Create successfully]', icon="🔥")
                        log_authorize(st.session_state.user,blaster_server['ip'], f'CREATE test profile {select_instance_name}')
                        time.sleep(3)
                        st.rerun()
        elif choice== ":green[:material/edit_note: **EDIT**]":
            log_authorize(st.session_state.user,blaster_server['ip'], 'Select EDIT')
            with st.container(border= True):
                st.subheader(':sunny: :green[**MODIFY YOUR CONFIG**]')
                st.write(':violet[**YOUR TEST PROFILE NAME**]')
                st.session_state.edit_instance= False
                edit_list_var=[]
                with st.container(border=True):
                    edit_instance= st.selectbox(':orange[Select your test profile for modifing]?', list_instance, placeholder = 'Select one test profile')
                    log_authorize(st.session_state.user,blaster_server['ip'], f'Edit config {edit_instance}')
                if os.path.exists('%s/%s.yml'%(path_configs,edit_instance)):
                    with open('%s/%s.yml'%(path_configs,edit_instance), 'r') as file_template:
                        try:
                            data=yaml.safe_load(file_template) # This dict is library of bngblaster
                        except yaml.YAMLError as exc:
                            st.error(exc)
                    load_data=copy_dict_with_empty_values(data) # This dict is library of bngblaster
                    dict_var={} # Var for save value from UI
                    ##################### Value of columns dynamic to deep elements of dict ######################
                    _, num_col= find_deepest_element(load_data)
                    var_col=""
                    for i in range(num_col):
                        if i == (num_col-1):
                            var_col += "col%s"%i
                        else:
                            var_col += "col%s"%i + ','
                    x=''
                    for i in range(num_col):
                        if i == 0:
                            x += "0.8"
                        else:
                            x += ",1"
                    x='[%s]'%x # This var for modify scale column
                    exec("%s =st.columns(%s, border=True)"%(var_col,x))
                    with col0:
                        st.write(":violet[:material/account_tree: **[BNGBlaster Configs]**]")
                        dict_selection_part_UI_edit(data=data,key_up_level="",number_column=0)
                    # st.write(dict_var)
                    if dict_var:
                        #For process input of elements UI
                        for i,v in dict_var.items(): 
                            if "num_" not in i:
                                path= i.split('___')
                                path.remove("")
                                # st.write(path)
                                for k in path:
                                    if k.find('_') != -1 and k != '_comment':
                                        path[path.index(k)]=k.replace('_','-')
                                    try:
                                        path[path.index(k)]=int(k)
                                    except Exception as e:
                                        # print(e)
                                        continue
                                str_path=""
                                for o in path:
                                    if isinstance(o, int):
                                        str_path += "[%s]"%o
                                    else:
                                        str_path += "['%s']"%o
                                if isinstance(v, int) or isinstance(v, list) or isinstance(v, float):
                                    exec("load_data%s= %s"%(str_path, v))
                                else:
                                    exec("load_data%s= '%s'"%(str_path, v))
                                    
                                if isinstance(v, int) or isinstance(v, list) or isinstance(v, float):
                                    exec("data%s['__value']= %s"%(str_path, v))
                                else:
                                    exec("data%s['__value']= '%s'"%(str_path, v))
                                # st.write("load_data%s= '%s'"%(str_path, v))
                    for i in range(num_col+10): # For remove emptry dict, list, str
                        pop_empty_structures(load_data)
                    with st.popover(':green[**:material/visibility: REVIEW**]', use_container_width=True):
                        convert_str_to_int(load_data)
                        convert_str_to_float(load_data)
                        convert_str_to_bool(load_data)
                        st.code(json.dumps(load_data, indent=2))
                    st.divider()
                    col14, col15, col16,col17 = st.columns([1,1,2,1])
                    with col14:
                        if st.button(':material/save: **SAVE**', type= 'primary', disabled = st.session_state.edit_instance, use_container_width=True):
                            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False,False, True, False, False
                            ### Save new config
                            with open('%s/%s.json'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as config:
                                json.dump(load_data, config, indent=2)
                            ### Save data instance to yaml
                            write_dict_to_yaml(data,'%s/%s.yml'%(path_configs,edit_instance))

                            st.toast(':blue[Save test profile %s successfully]'%edit_instance, icon="🔥")
                            log_authorize(st.session_state.user,blaster_server['ip'], f'Edit and save test profile {edit_instance}')
                    with col15:
                        with st.popover(':material/content_copy: **CLONE**', use_container_width=True):
                            new_name= st.text_input(f":orange[:material/add: Your test profile name for cloning config: ]","", placeholder = "Fill your name")
                            if is_valid_name_instance(new_name):
                                if new_name + '.json' not in list_json:
                                    # st.info(':blue[Your instance\'s name can be use.]', icon="🔥")
                                    st.info(':blue[Use button below for saving.]', icon="🔥")
                                    if st.button('**:material/done_outline:**', use_container_width=True):
                                        # Clone json config
                                        with open('%s/%s.json'%(path_configs,new_name), mode= 'w', encoding= 'utf-8') as config:
                                            json.dump(load_data, config, indent=2)
                                        # Clone template
                                        write_dict_to_yaml(data,'%s/%s.yml'%(path_configs,new_name))
                                        st.toast(':blue[Clone test profile %s successfully]'%new_name, icon="🔥")
                                        log_authorize(st.session_state.user,blaster_server['ip'], "Clone %s to %s"%(edit_instance,new_name))
                                        time.sleep(2)
                                        st.rerun()
                                else:
                                    st.error('Your test profile was duplicate, choose other name', icon="🚨")
                            else:
                                st.error('Test profile name is null or wrong syntax', icon="🔥")
                    with col17:
                        if st.button(':material/delete: **DELETE**', use_container_width=True):
                            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                            delete_config(path_configs, edit_instance)
                else:
                    with open("%s/%s.json"%(path_configs,edit_instance) , 'r') as edit_config_data:
                        edit_json_raw= edit_config_data.read()
                    with st.container(border=True):
                        edit_json= st_ace(
                            value= edit_json_raw,
                            language= 'json', 
                            theme= '', 
                            show_gutter= True, 
                            keybinding='vscode', 
                            auto_update= True, 
                            placeholder= '*Edit your config*')
                    col141, col151, col161,col171 = st.columns([1,1,2,1])
                    with col141:
                        if st.button(':material/save: **SAVE**', type= 'primary', use_container_width=True):
                            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False,False, True, False, False
                            try: 
                                json.loads(edit_json)
                                with open("%s/%s.json"%(path_configs,edit_instance) , 'w') as after_edit_json:
                                    json.dump(json.loads(edit_json), after_edit_json, indent=2)
                                    st.toast(':blue[Save test profile **%s** successfully]'%edit_instance, icon="🔥")
                                    log_authorize(st.session_state.user,blaster_server['ip'], "Save test profile %s"%(edit_instance))
                            except Exception as e:
                                st.error('Error json %s'%e, icon="🚨")
                    with col151:
                        if st.button(':material/change_circle: **CONVERT**', use_container_width=True):
                            dict_edit= json.loads(edit_json)
                            convert_paths=list_all_paths(dict_edit)
                            with open('all_conf.yml', 'r') as file_template:
                                try:
                                    data=yaml.safe_load(file_template) # This dict is library of bngblaster
                                except yaml.YAMLError as exc:
                                    st.error(exc)
                            new_dict_template=copy_dict_with_empty_values(dict_edit)
                            for i in convert_paths:
                                # Pop index of list inside dict
                                if isinstance(i[-1],int):
                                    i.pop(-1)
                                var_access=''
                                var_access_data=''
                                for e in i:
                                    if isinstance(e,int):
                                        var_access+= "[%s]"%e
                                        if int(e) == 0:
                                            var_access_data+= "[%s]"%e
                                        else:
                                            var_access_data+= "[0]"
                                    else:
                                        var_access+= "['%s']"%e
                                        var_access_data+= "['%s']"%e
                                exec("new_dict_template%s=copy.deepcopy(data%s)"%(var_access,var_access_data))
                                # exec("new_dict_template%s['__value']=dict_edit%s"%(var_access,var_access))
                                exec("data_type= new_dict_template%s['__datatype']"%(var_access))
                                if data_type == 'int' or data_type == 'float': # This code for case user input integer auto cast into float and divert
                                    exec("new_dict_template%s['__value']=%s(dict_edit%s)"%(var_access,data_type,var_access))
                                else:
                                    exec("new_dict_template%s['__value']=dict_edit%s"%(var_access,var_access))
                                # For change wdget customize to input text with edit mode
                                if eval("new_dict_template%s['__widget'] == 'customize'"%(var_access)):
                                    exec("new_dict_template%s['__widget']='text_input'"%(var_access))
                            # Write to template file
                            write_dict_to_yaml(new_dict_template,'%s/%s.yml'%(path_configs,edit_instance))
                            st.toast(':blue[Convert config of **%s** successfully]'%edit_instance, icon="🔥")
                            log_authorize(st.session_state.user,blaster_server['ip'], "Convert config test profile %s to yaml"%(edit_instance))
                            time.sleep(2)
                            st.rerun()
                    with col171:
                        if st.button(':material/delete: **DELETE**', use_container_width=True):
                            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                            delete_config(path_configs, edit_instance)
                    if edit_json != "":
                        with st.popover(":green[**:material/preview: REVIEW JSON**]", use_container_width=True):
                            # st.json(yaml.safe_load(edit_content))
                            st.code(json.dumps(json.loads(edit_json), indent=2))
if st.session_state.p4:
    st.title(':material/all_inclusive: :rainbow[RUN BLASTER]')
    col41, col42 ,col43 =st.columns([19,0.9,0.9])
    with col42:
        if st.button(':material/widgets:', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
            st.rerun()
    with col43:
        if st.button(":material/insights: ", use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, False, True
            st.rerun()
    blaster_status(blaster_server['ip'],blaster_server['port'],list_instance_running_from_blaster, list_instance_avail_from_blaster) # call function display status of blaster server
    col4, col5=st.columns([1.5,1])
    with col4:
        with st.container(border= True):
            st.subheader(':sunny: :green[CONFIG MANAGEMENT [%s JSONs]]'%len(list_json))
            col19, col20 =st.columns([1.3,1])
            with col19:
                with st.container(border= True):
                    instance= st.selectbox(':orange[:material/done: Select your test profile]?', list_instance, placeholder = 'Select one test profile')
                    instance_exist_st, instance_exist_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start)
            with col20:
                with st.popover(":blue[:material/visibility: **CONFIG**]", use_container_width=True):
                    st.info(":violet[Content of **%s.json**]"%instance, icon="🔥")
                    with open('%s/%s.json'%(path_configs, instance), 'r') as file_show:
                        data= file_show.read()
                    data_json=json.loads(data)    
                    st.code(data)
                    if st.button(':material/edit: **EDIT**', use_container_width=True):
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                        log_authorize(st.session_state.user,blaster_server['ip'], 'Change RUN to PRE-RUN for EDIT')
                        st.rerun()
                with st.container(border= True):
                    try:
                        temp_list_nw=[]
                        for i in range(len(data_json['interfaces']['network'])):
                            temp_list_nw.append(data_json['interfaces']['network'][i]['interface'])
                        st.info(':material/info: Test profile **%s** use network interface *%s*'%(instance, temp_list_nw))
                        temp_list_acc=[]
                        for i in range(len(data_json['interfaces']['access'])):
                            temp_list_acc.append(data_json['interfaces']['access'][i]['interface'])
                        st.info(':material/info: Test profile **%s** use access interface *%s*'%(instance, temp_list_acc))
                    except Exception as e:
                        print('[RUN] Json config dont have network or access interface, error %s'%e)
                    if "started" not in str(instance_exist_ct):
                        if 'bgp' in data_json.keys():
                            if 'raw-update-file' in data_json['bgp'].keys():
                                with st.container(border= True):
                                    st.warning(':material/warning: Define absolute path when your define \'raw-update-file\' .Example: **/var/bngblaster/<profile>/test.bgp**')
                                    st.warning(':material/warning: Should have file **%s** before start test profile **%s**'%(data_json['bgp']['raw-update-file'], instance))
                                    with st.popover(":green[:material/data_saver_on: Create **raw-update-file**]", use_container_width=True):
                                        with st.form("CREATE_FILE"):
                                            asnumber= st.text_input(f":orange[:material/add: Your AS (-a) :]",f"{data_json['bgp']['local-as']}", placeholder = "Fill AS Number")
                                            nexthop= st.text_input(f":orange[:material/add: Your next-hop (-n) :]",data_json['bgp']['local-address'], placeholder = "Fill next-hop IP")
                                            nexthop_count= st.text_input(f":orange[:material/add: Your next-hop count (-N) :]",'', placeholder = "Fill next-hop count")
                                            lp= st.text_input(f":orange[:material/add: Your local_pref (-l) :]",'', placeholder = "Fill LP")
                                            prefix= st.text_input(f":orange[:material/add: Your prefix (-p):]","", placeholder = "Fill IP prefix")
                                            num_prefix= st.text_input(f":orange[:material/add: Your number of prefixs (-P): ]","", placeholder = "Fill number")
                                            submitted = st.form_submit_button(label= ":green[:material/send: **CREATE**]", use_container_width=True)
                                            if submitted:
                                                if "/" in prefix and prefix:
                                                    name_bgp_update = data_json['bgp']['raw-update-file'].split('/')[-1]
                                                    if prefix and num_prefix:
                                                        list_bgpupdate=["bgpupdate","-f", "./bgp_update/%s"%name_bgp_update, "-p", prefix, "-P",num_prefix]
                                                        if asnumber:
                                                            list_bgpupdate.append("-a")
                                                            list_bgpupdate.append(asnumber)
                                                        if nexthop:
                                                            list_bgpupdate.append("-n")
                                                            list_bgpupdate.append(nexthop)
                                                        if nexthop_count:
                                                            list_bgpupdate.append("-N")
                                                            list_bgpupdate.append(nexthop_count)
                                                        if lp:
                                                            list_bgpupdate.append("-l")
                                                            list_bgpupdate.append(lp)
                                                        # st.write(list_bgpupdate)
                                                        result = subprocess.run(list_bgpupdate, capture_output=True, text=True)
                                                        if 'error' not in str(result):
                                                            execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), "sudo -S mkdir /var/bngblaster/%s"%instance)
                                                            time.sleep(0.1)
                                                            # push_file_to_server_by_ftp(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'],f"{path_bgp_update}/{name_bgp_update}.bgp", f"{data_json['bgp']['raw-update-file']}")
                                                            upload_sc, upload_st = UPLOAD_FILE_BLASTER(blaster_server['ip'], blaster_server['port'], instance, f"{path_bgp_update}/{name_bgp_update}")
                                                            # st.write(upload_sc, upload_st)
                                                            if upload_sc == 200:
                                                                st.info(':blue[Upload sucessfully]', icon="🔥")
                                                            else:
                                                                st.warning("Upload not sucessfully, Error %s"%upload_st, icon="🔥")
                                                            log_authorize(st.session_state.user,blaster_server['ip'], f'Create file bgpupdate {prefix} num {num_prefix} test profile {instance}')
                                                        else:
                                                            st.error(":violet[Wrong prefix]", icon="🔥")
                                                    else:
                                                        st.error(":violet[Fill prefix advertise above first]", icon="🔥")
                                                else:
                                                    st.error('Type your prefix with subnet mask, please', icon="🚨")
            if "started" in str(instance_exist_ct):
                st.session_state.button_start= True
                st.session_state.button_stop= False
                with col19:
                    st.warning("This test profile already running", icon="🔥")
                if os.path.exists('%s/%s.yml'%(path_configs,instance)):
                    with open('%s/%s.yml'%(path_configs,instance), 'r') as file_temp:
                        run_template = yaml.load(file_temp, Loader=yaml.FullLoader)
                    if 'bgp' in run_template.keys():
                        if 'raw-update-file' in run_template['bgp'].keys():
                            st.info(":green[**:material/route: BGP ROUTE UPDATE :material/expand_more:**]")
                            col17, col18 =st.columns([1,1])
                            with col17:
                                with st.form("ADVERTISE"):
                                    asnumber= st.text_input(f":orange[:material/add: Your AS (-a) :]",f"{data_json['bgp']['local-as']}", placeholder = "Fill AS Number")
                                    nexthop= st.text_input(f":orange[:material/add: Your next-hop (-n) :]",data_json['bgp']['local-address'], placeholder = "Fill next-hop IP")
                                    nexthop_count= st.text_input(f":orange[:material/add: Your next-hop count (-N) :]",'', placeholder = "Fill next-hop count")
                                    lp= st.text_input(f":orange[:material/add: Your local_pref (-l) :]",'', placeholder = "Fill LP")
                                    prefix= st.text_input(f":orange[:material/add: Your prefix (-p):]","", placeholder = "Fill IP prefix")
                                    num_prefix= st.text_input(f":orange[:material/add: Your number of prefixs (-P): ]","", placeholder = "Fill number")
                                    submitted = st.form_submit_button(label= ":green[:material/send: **ADVERTISE**]", use_container_width=True)
                                    if submitted:
                                        if "/" in prefix and prefix:
                                            name_bgp_update = instance + "_"+ prefix.split('/')[0]+"_"+num_prefix
                                            payload_command_bgp_raw_update= """
                                            {
                                                "command": "bgp-raw-update",
                                                "arguments": {
                                                    "file": "/var/bngblaster/%s/%s.bgp"
                                                }
                                            }
                                            """%(instance, name_bgp_update)
                                            if prefix and num_prefix:
                                                list_bgpupdate=["bgpupdate","-f", "./bgp_update/%s.bgp"%name_bgp_update, "-p", prefix, "-P",num_prefix]
                                                if asnumber:
                                                    list_bgpupdate.append("-a")
                                                    list_bgpupdate.append(asnumber)
                                                if nexthop:
                                                    list_bgpupdate.append("-n")
                                                    list_bgpupdate.append(nexthop)
                                                if nexthop_count:
                                                    list_bgpupdate.append("-N")
                                                    list_bgpupdate.append(nexthop_count)
                                                if lp:
                                                    list_bgpupdate.append("-l")
                                                    list_bgpupdate.append(lp)
                                                # st.write(list_bgpupdate)
                                                result= subprocess.run(list_bgpupdate, capture_output=True, text=True)
                                                if 'error' not in str(result):
                                                    upload_sc, upload_st = UPLOAD_FILE_BLASTER(blaster_server['ip'], blaster_server['port'], instance, f"{path_bgp_update}/{name_bgp_update}.bgp")
                                                    if upload_sc == 200:
                                                        st.info(':blue[Upload file sucessfully]', icon="🔥")
                                                    else:
                                                        st.warning("Upload file not sucessfully, Error %s"%upload_st, icon="🔥")
                                                    adv_sc, adv_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_command_bgp_raw_update, '/_command')
                                                    if adv_sc==200:
                                                        st.info(':blue[Advertise route sucessfully]', icon="🔥")
                                                        log_authorize(st.session_state.user,blaster_server['ip'], f'Advertise BGP route {prefix} num {num_prefix}')
                                                    else:
                                                        st.warning("Advertise route not sucessfully, Error %s"%adv_ct, icon="🔥")
                                                else:
                                                    st.error(":violet[Wrong prefix]", icon="🔥")
                                            else:
                                                st.error(":violet[Fill prefix advertise above first]", icon="🔥")
                                        else:
                                            st.error('Type your prefix with subnet mask, plz', icon="🚨")
                            with col18:
                                with st.form('WITHDRAW'):
                                    asnumber_wd= st.text_input(f":orange[:material/add: Your AS (-a) :]",f"{data_json['bgp']['local-as']}", placeholder = "Fill AS Number")
                                    nexthop_wd= st.text_input(f":orange[:material/add: Your next-hop (-n) :]",data_json['bgp']['local-address'], placeholder = "Fill next-hop IP")
                                    nexthop_count_wd= st.text_input(f":orange[:material/add: Your next-hop count (-N) :]",'', placeholder = "Fill next-hop count")
                                    lp_wd= st.text_input(f":orange[:material/add: Your local_pref (-l) :]",'', placeholder = "Fill LP")
                                    prefix_wd= st.text_input(f":orange[:material/add: Your prefix (-p):]","", placeholder = "Fill IP prefix")
                                    num_prefix_wd= st.text_input(f":orange[:material/add: Your number of prefixs (-P): ]","", placeholder = "Fill number")

                                    # prefix_wd= st.text_input(f":orange[:material/add: Your prefix you want withdraw: ]","", placeholder = "Fill your IP prefix")
                                    # num_prefix_wd= st.text_input(f":orange[:material/add: Your number of prefixs you want withdraw: ]","", placeholder = "Fill number")
                                    submitted = st.form_submit_button(label= ":green[:material/dangerous: **WITHDRAW**]", use_container_width=True)
                                    if submitted:
                                        if "/" in prefix_wd and prefix_wd:
                                            name_bgp_update_wd = instance+"_withdraw_"+ prefix_wd.split('/')[0]+"_"+num_prefix_wd
                                            payload_command_bgp_raw_update_wd= """
                                            {
                                                "command": "bgp-raw-update",
                                                "arguments": {
                                                    "file": "/var/bngblaster/%s/%s.bgp"
                                                }
                                            }
                                            """%(instance, name_bgp_update_wd)
                                            if prefix_wd and num_prefix_wd:
                                                list_bgpupdate_wd=["bgpupdate","-f", "./bgp_update/%s.bgp"%name_bgp_update_wd, "-p", prefix, "-P",num_prefix]
                                                if asnumber_wd:
                                                    list_bgpupdate_wd.append("-a")
                                                    list_bgpupdate_wd.append(asnumber_wd)
                                                if nexthop_wd:
                                                    list_bgpupdate_wd.append("-n")
                                                    list_bgpupdate_wd.append(nexthop_wd)
                                                if nexthop_count_wd:
                                                    list_bgpupdate_wd.append("-N")
                                                    list_bgpupdate_wd.append(nexthop_count_wd)
                                                if lp_wd:
                                                    list_bgpupdate_wd.append("-l")
                                                    list_bgpupdate_wd.append(lp_wd)
                                                list_bgpupdate_wd.append("--withdraw")
                                                # result_wd= subprocess.run(["bgpupdate","-a", run_template[instance]['bgp_local_as'], "-n",run_template[instance]['bgp_local_address'], "-p", prefix_wd, "-P",num_prefix_wd,"-f", "./bgp_update/%s.bgp"%name_bgp_update_wd,"--withdraw"], capture_output=True, text=True)
                                                result_wd= subprocess.run(list_bgpupdate_wd, capture_output=True, text=True)
                                                if "error" not in str(result_wd):
                                                    upload_sc, upload_st = UPLOAD_FILE_BLASTER(blaster_server['ip'], blaster_server['port'], instance, f"{path_bgp_update}/{name_bgp_update_wd}.bgp")
                                                    if upload_sc == 200:
                                                        st.info(':blue[Upload file sucessfully]', icon="🔥")
                                                    else:
                                                        st.warning("Upload file not sucessfully, Error %s"%upload_st, icon="🔥")
                                                    wd_sc, wd_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_command_bgp_raw_update_wd, '/_command')
                                                    if wd_sc==200:
                                                        st.info(':blue[Withdraw sucessfully]', icon="🔥")
                                                        log_authorize(st.session_state.user,blaster_server['ip'], f'Withdraw BGP route {prefix_wd} num {num_prefix_wd}')
                                                    else:
                                                        st.warning("Advertise route not sucessfully, Error %s"%wd_ct, icon="🔥")
                                                else:
                                                    st.error(":violet[Wrong prefix]", icon="🔥")
                                            else:
                                                st.error(":violet[Fill prefix withdraw above first]", icon="🔥")
                                        else:
                                            st.error('Type your prefix with subnet mask, plz', icon="🚨")
            else:
                with col19:
                    st.session_state.button_start= False
                    st.session_state.button_stop= True
                    st.session_state.button_kill= True
                    with st.container(border= True):
                        if instance in list_instance_avail_from_blaster:
                            st.warning(f'Test profile **{instance}** can start but its config will be overrided', icon="🔥")
                        else:
                            st.info("You can start this test profile", icon="🔥")
            with col19:
                if st.button(':material/sound_sampler: **START**', type = 'primary',use_container_width=True, disabled= st.session_state.button_start):
                    list_inf = []
                    with open(f"{path_configs}/{instance}.json", "r") as json_run:
                        val_json=json.load(json_run)
                    try:
                        for i in range(len(val_json['interfaces']['access'])):
                            list_inf.append(val_json['interfaces']['access'][i]['interface'])
                    except:
                        pass
                    try:
                        for i in range(len(val_json['interfaces']['network'])):
                            list_inf.append(val_json['interfaces']['network'][i]['interface'])
                    except:
                        pass
                    for i in list_inf:
                        if '.' in i:
                            # st.toast(i)
                            execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), "sudo -S modprobe 8021q")
                            time.sleep(0.02)
                            execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), f"sudo -S ip link add link {i.split('.')[0]} name {i} type vlan id {i.split('.')[1]}")
                            time.sleep(0.02)
                            execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), f"sudo -S ip link set dev {i} up")
                    try:
                        exist_sc, exist_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start)
                        # st.write(exist_sc, exist_ct)
                    except Exception as e:
                        st.info(f'Error {e}')
                    if exist_sc == 200:
                        st.write(':orange[:material/done: Start traffic generating ...]')
                        with open(f'{path_configs}/{instance}.json') as file:
                            exist_put_body= json.load(file)
                        CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'PUT', json.dumps(exist_put_body, indent=2))
                        start_exist_sc, start_exist_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_start, '/_start')
                        #st.write(start_exist_sc, start_exist_ct)
                        run_pg1 = st.progress(0)
                        for percent_complete3 in range(100):
                            time.sleep(0.01)
                            run_pg1.progress(percent_complete3 + 1, text= f':violet[{percent_complete3+1}%]')
                    else:
                        ######## Push config.json ##############################
                        with open(f'{path_configs}/{instance}.json') as file:
                            put_body= json.load(file)
                        st.write(':orange[:material/upload: Put config.json ...]')
                        put_sc, put_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'PUT', json.dumps(put_body, indent=2))
                        put_pg = st.progress(0)
                        for percent_complete1 in range(100):
                            time.sleep(0.01)
                            put_pg.progress(percent_complete1 + 1, text= f':violet[{percent_complete1+1}%]')
                        ######## Start trafffic ##############################
                        st.write(':orange[:material/done: Start traffic generating ...]')
                        start_sc, start_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_start, '/_start')
                        # st.write(start_sc, start_ct)
                        run_pg = st.progress(0)
                        for percent_complete2 in range(100):
                            time.sleep(0.01)
                            run_pg.progress(percent_complete2 + 1, text= f':violet[{percent_complete2+1}%]')
                        if put_sc == 201:
                            print('Create test profile on blaster sucessfully')
                        else: 
                            print('Create test profile on blaster didnt sucessfully')
                    st.session_state.button_stop= False
                    log_authorize(st.session_state.user,blaster_server['ip'], f'RUN START test profile {instance}')
                    time.sleep(1)
                    st.rerun()
                # with st.container(border= True):
                if st.button(':material/stop_circle: **STOP**', type= 'primary', use_container_width=True, disabled= st.session_state.button_stop):
                    stop_sc, stop_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_stop, '/_stop')
                    # st.write(stop_sc, stop_ct)
                    log_authorize(st.session_state.user,blaster_server['ip'], f'RUN STOP test profile {instance}')
                    if stop_sc == 202:
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
                        log_authorize(st.session_state.user,blaster_server['ip'], f'STOP test profile {instance} successfully')
                        
                        stop_pg = st.progress(0)
                        # for percent_complete3 in range(100):
                        #     time.sleep(0.004)
                        #     stop_pg.progress(percent_complete3 + 1, text= f':violet[{percent_complete3+1}%]')
                        m = False # this var for display warning if for below out of range, user need wait more and refresh page
                        for i in range(10):
                            check_instance_st, check_instance_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start)
                            # st.write(check_instance_st,check_instance_ct)
                            if "stopped" in str(check_instance_ct):
                                list_inf = []
                                with open(f"{path_configs}/{instance}.json", "r") as json_run:
                                    val_json=json.load(json_run)
                                try:
                                    for i in range(len(val_json['interfaces']['access'])):
                                        list_inf.append(val_json['interfaces']['access'][i]['interface'])
                                except:
                                    pass
                                try:
                                    for i in range(len(val_json['interfaces']['network'])):
                                        list_inf.append(val_json['interfaces']['network'][i]['interface'])
                                except:
                                    pass
                                for i in list_inf:
                                    if '.' in i:
                                        # st.toast(i)
                                        execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), f"sudo -S ip link delete link {i.split('.')[0]} name {i} type vlan id {i.split('.')[1]}")
                                        time.sleep(0.02)
                                stop_pg.progress(100, text= f':violet[100%]')
                                st.info(":green[Stop successfully]", icon="🔥")
                                time.sleep(1)
                                break
                            if i == 9:
                                m = True
                            stop_pg.progress(i*10, text= f':violet[{i*10}%]')
                            time.sleep(2)
                        if m:
                            st.warning("Your profile can still running, wait and refresh again or use kill below", icon="🔥")
                            st.session_state.button_kill= False
                        else:
                            time.sleep(1)
                            st.rerun()
                if st.button(':material/offline_bolt: **KILL**', type= 'primary', use_container_width=True, disabled= st.session_state.button_kill):
                    kill_sc, kill_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_stop, '/_kill')
                    if kill_sc == 202:
                        st.warning("You used KILL button, report after testing which couldn't be generated", icon="🔥")
                        time.sleep(1)
                        st.rerun()
    with col5:
        with st.container(border= True):
            st.subheader(':sunny: :green[OUTPUT LOGGING]')
            if ("started" in str(instance_exist_ct)) or ("stopped" in str(instance_exist_ct)):
                run_out=''
                run_log= ''
                run_err= ''
                if instance:
                    run_log_sc, run_log = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start, '/run.log')
                    run_out_sc, run_out = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start, '/run.stdout')
                    run_err_sc, run_err = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start, '/run.stderr')
                if run_log != '':
                    with st.status(':violet[ALL_RUNNING_LOG]', expanded=False):
                        for i in str(run_log).split('\\n')[-50:-1]:
                            # time.sleep(0.01)
                            st.text('%s'%i)
                if run_out != '':
                    with st.status(':violet[RUNNING_LOG]', expanded=False):
                        for i in str(run_out).split('\\n')[-30:-1]:
                            # time.sleep(0.01)
                            st.text('%s'%i)            
                if run_err != '':
                    with st.status(':violet[ERROR_LOG]', expanded=False):
                        for i in str(run_err).split('\\n')[-30:-1]:
                            # time.sleep(0.01)
                            st.text('%s'%i)
if st.session_state.p5:
    st.title(':material/insights: :rainbow[DASHBOARD]')
    col61, col62 ,col63 =st.columns([19,0.9,0.9])
    with col62:
        # if st.button('◀️'):
        if st.button(':material/widgets: ', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
            log_authorize(st.session_state.user,blaster_server['ip'], 'REPORT return HOME')
            st.rerun()
    with col63:
        if st.button(':material/all_inclusive:', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
            log_authorize(st.session_state.user,blaster_server['ip'], 'REPORT return RUN')
            st.rerun()
    blaster_status(blaster_server['ip'],blaster_server['port'],list_instance_running_from_blaster, list_instance_avail_from_blaster) # call function display status of blaster server
    # instance_running= ['bgp_linhnt','bras_pppoe_linhnt','bras_pppoe_hoand']
    with st.container(border=True):
        st.subheader(':sunny: :green[REPORTING]')
    col29, col30 = st.columns([1,1])
    with col29:
        with st.container(border=True):
            instance_report = st.selectbox(':orange[Select your test profile for reporting]', list_instance_avail_from_blaster)
    # run_report_sc, run_report = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], f'{st.session_state.report}', 'GET', payload_start, '/run_report.json')
    run_report_sc, run_report = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance_report, 'GET', payload_start, '/run_report.json')
    if run_report_sc == 200:
        report_timestamp = execute_remote_command_use_passwd_get_time(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), f"stat --printf=%y /var/bngblaster/{instance_report}/config.json | cut -d. -f1")
        st.info(f"*Last run: :orange[{report_timestamp}]*")
        report= json.loads(run_report)
        df= pd.DataFrame.from_dict(report, orient="index") # convert report to dataframe
        with col30:
            with st.container(border=True):
                key_select = st.multiselect(':orange[Select your fields]',df.columns, default=['interfaces', 'sessions', 'streams'], placeholder = 'Select your filed for reporting')
        # st.write(key_select)
        # st.write(list(df.columns))
        col27, col28 = st.columns([1,3])
        with col27:
            with st.container(border=True):
                st.subheader(":label: :green[METRICS]")
        with col28:
            with st.container(border=True):
                st.subheader(":newspaper: :green[TABLES]")
        if key_select:
            for i in key_select:
                x= json.loads(df[i].to_json(orient= 'index'))
                # st.write(x['report'])
                with col27:
                    with st.container(border=True):
                        if isinstance(x['report'], int) or isinstance(x['report'], float) or i == 'version':
                            label= f":orange[**{i}**]"
                            value= "%s"%x['report']
                            delta= f"{i}"
                            st.metric(label= label, value= value, delta=delta)
                with col28:
                    with st.container(border=True):
                        if not (isinstance(x['report'], int) or isinstance(x['report'], float) or i == 'version'):
                            st.write(f":orange[**{i} statistics**]")
                            st.dataframe(x['report'], use_container_width= True)
    else:
        with col30:
            with st.container(border=True):
                st.warning('Report not existed', icon="🚨")
        print('[404] File report.json does not exist')
st.divider()
col25,col27,col26 = st.columns([10,1,1])
if authentication_status:
    if st.session_state.p1 or st.session_state.p2 :
        with col26:
            authenticator.logout(':x:', 'main')
with col27:
    if st.session_state.p2:
        if st.button(":material/storage:", use_container_width= True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= True, False, False, False, False
            st.rerun()
################################# For ADMIN ##########################################
if dict_user_db[st.session_state.user] == 'admin' and st.session_state.p2:
    st.divider()
    with col25:
        with st.expander(':green[RESET PASSWORD]'):
            try:
                username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
                st.write(username_of_forgotten_password, '\n', email_of_forgotten_password, '\n' ,new_random_password)
                if username_of_forgotten_password:
                    with open('authen/config.yaml', 'w') as file:
                        yaml.dump(config_authen, file, default_flow_style=False)
                    st.success('New password to be sent securely', icon="🔥")
                    # The developer should securely transfer the new password to the user.
                elif username_of_forgotten_password == False:
                    st.error('Username not found')
            except Exception as e:
                st.error(e)
        with st.expander(':green[CREATE USER LOGIN]'):
            try:
                email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
                if email_of_registered_user:
                    with open('authen/config.yaml', 'w') as file:
                        yaml.dump(config_authen, file, default_flow_style=False)
                    # conn = sqlite_connect_to_db(db_name)
                    db = DatabaseConnection()
                    conn= db.connection
                    # sqlite_insert_user(conn, username_of_registered_user, 'operator')
                    temp_user_insert = {'name': username_of_registered_user, 'class': 'operator'}
                    db.insert('users', temp_user_insert)
                    conn.close()
                    st.success('User registered successfully', icon="🔥")
            except Exception as e:
                st.error(e)
        with st.expander(':green[EDIT USER PRIVILEGES]'):
            col1, col2= st.columns([1,1])
            with col1:
                with st.container(border=True):
                    st.write(":orange[:material/delete: **DELETE**]")
                    # conn = sqlite_connect_to_db(db_name)
                    db = DatabaseConnection()
                    conn= db.connection
                    # users= sqlite_fetch_users(conn)
                    users=db.execute_query('SELECT * from users')
                    st.write(":orange[List users]")
                    st.table(users)
                    list_user=[]
                    for i in users:
                        list_user.append(i[0])
                    user_select= st.selectbox(":orange[User]", list_user)
                    if st.button(":blue[**DELETE_USER**]"):
                        # sqlite_delete_user(conn, user_select)
                        db.delete('users',"name='%s'"%user_select)
                        st.info(":green[Delete successfully]")
                    conn.close()
            with col2:
                with st.container(border=True):
                    st.write(":orange[**UPDATE**]")
                    # conn = sqlite_connect_to_db(db_name)
                    db = DatabaseConnection()
                    conn= db.connection
                    # users= sqlite_fetch_users(conn)
                    users=db.execute_query('SELECT * from users')
                    list_user=[]
                    for i in users:
                        list_user.append(i[0])
                    user_update= st.selectbox(":orange[User update]", list_user)
                    user_class_update= st.selectbox(":orange[User]", user_privilege)
                    if st.button(":blue[**UPDATE**]"):
                        # sqlite_update_user_class(conn, user_update, user_class_update)
                        db.update('users', {'class': '%s'%user_class_update}, "name='%s'"%user_update)
                        st.info(":green[Update successfully]")
                    conn.close() 
        with st.expander(':green[EDIT BLASTERs]'):
            col1, col2= st.columns([1,1])
            with col1:
                with st.container(border=True):
                    st.write(":orange[**INSERT NEW BLASTER**]")
                    ip = st.text_input(":orange[Blaster IP]")
                    port= st.text_input(":orange[Blaster PORT]", '8001')
                    user_ssh= st.text_input(":orange[User SSH]")
                    passwd_ssh= st.text_input(":orange[Password SSH]", type= 'password')
                    if st.button(":blue[**INSERT_BLASTER**]"):
                        # conn = sqlite_connect_to_db(db_name)
                        # sqlite_insert_user(conn, user, user_class)
                        db = DatabaseConnection()
                        conn= db.connection
                        # sqlite_insert_blaster(conn, ip, port, user_ssh, passwd_ssh)
                        db.insert('blasters', {'ip': ip,'port':port,'user':user_ssh,'passwd':passwd_ssh})
                        conn.close()
                        st.info(":green[Insert successfully]")
            with col2:
                with st.container(border=True):
                    st.write(":orange[**DELETE BLASTER**]")
                    delete_blaster = st.selectbox(":orange[Select Delete Blaster IP]", dict_blaster_db_format.keys())
                    if st.button(":blue[**DELETE BLASTER**]"):
                        # conn = sqlite_connect_to_db(db_name)
                        db = DatabaseConnection()
                        conn= db.connection
                        # sqlite_delete_blaster(conn, delete_blaster)
                        db.delete('blasters',"ip='%s'"%delete_blaster)
                        conn.close()
                        st.info(":green[Delete blaster successfully]")
        with st.expander(':green[LOG USERS ACTIONS]'):
            with open('auth.log', 'r') as log:
                logging= log.read()
                st.text_area(':orange[Logging]',logging, height = 400)
        with st.expander(':green[DATABASES]'):
            col1, col2= st.columns([1,1])
            with col1:
                with st.container(border=True):
                    st.write(":orange[**ALL TABLEs**]")
                    # conn = sqlite_connect_to_db(db_name)
                    db = DatabaseConnection()
                    conn= db.connection
                    # list_table= sqlite_get_all_tables(conn)
                    list_table= db.get_all_tables()
                    select_table= st.selectbox(":orange[Get Table]", list_table)
                    # table_detail= sqlite_fetch_table(conn, select_table)
                    exec("table_detail= db.execute_query(\"SELECT * FROM %s\")"%select_table)
                    st.table(table_detail)
                    if st.button(":blue[**DELETE_TABLE**]"):
                        # sqlite_delete_table(conn, select_table)
                        db.delete_table(select_table)
                        st.info(":green[Delete successfully]")
                    # conn.close()
                    db.close_connection()
################################# For user ##########################################
if st.session_state.p2:
    with col25:
        with st.expander(':green[CHANGE YOUR PASSWORD]'):
            try:
                if authenticator.reset_password(st.session_state["username"], fields= {'Form name': ':herb: :orange[CHANGE YOUR PASSWORD]', 'Reset':':herb: :blue[**CHANGE**]'}):
                    with open('authen/config.yaml', 'w') as file:
                        yaml.dump(config_authen, file, default_flow_style=False)
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(f'Your password incorrect. Error: {e}', icon="🚨")
