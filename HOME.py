import streamlit as st
# import string
import os, re
import time
import requests
import json, yaml
import subprocess
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
            st.toast(':blue[Delete instance %s successfully]'%instance, icon="🔥")
            log_authorize(st.session_state.user,blaster_server['ip'], f'DELETE instance {instance}')
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
        with bscol2:
            # Note: dict_blaster_db_format is var global
            list_int_server = find_interface(ip, dict_blaster_db_format[ip]['user'], dict_blaster_db_format[ip]['passwd'])
            for i in list_int_server:
                st.write(':green[ :material/share: *Interface %s used vlan: %s*]'%(i, find_used_vlans(ip, dict_blaster_db_format[ip]['user'], dict_blaster_db_format[ip]['passwd'], i)))
        col_select, col_display= st.columns([1,2])
        with col_select:
            with st.container(border=True):
                st.write(":fire: :violet[**INSTANCE RUNNING**]")
            with st.container(border=True, height= 400):   
                select_running_instance={}
                for i in list_instance_running_from_blaster:
                    col111, col112= st.columns([4,1], border= True)
                    with col111:
                        exec(f"""select_running_instance['{i}'] = st.checkbox(f":orange[*{i}*]")""") 
                    with col112:
                        with st.popover(':orange[:material/access_time:]', use_container_width=True):
                        # with st.container(border=True):
                            time_start = find_and_split_line_from_file('auth.log', 'RUN START instance %s'%i)
                            st.info(":blue[**:material/sound_sampler: LAST START**]")
                            try:
                                st.write(":orange[ :material/sound_sampler: *%s*]"%time_start[0].split('_')[0:3])
                                st.write(":orange[ :material/dns: *%s*]"%time_start[0].split('_')[3])
                            except:
                                st.write(":orange[ :material/sound_sampler: *None*]")
                                st.write(":orange[ :material/dns: *None*]")
                            time_stop = find_and_split_line_from_file('auth.log', 'RUN STOP instance %s'%i)
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
        with  st.expander(":material/graphic_eq: :violet[**INSTANCE EXISTED CONFIG**]"):
            for i in list_instance_avail_from_blaster:
                with st.container(border=True):
                    col1, col2= st.columns([1,1])
                    with col1:
                        st.write(f":orange[**Instance :**] *{i}*")
                    with col2:
                        with st.popover(f":blue[:material/visibility: **CONFIG**]", use_container_width=True):
                            view_config_avail_sc,  view_config_avail_ct = CALL_API_BLASTER(ip, port, i, 'GET', payload_start, '/config.json')
                            if view_config_avail_sc==200:
                                try:
                                    config_avail = json.loads(view_config_avail_ct)
                                    st.code(json.dumps(config_avail, indent=2), language='json')
                                except Exception as e:
                                    st.error(':blue[Instance %s have json syntax error %s]'%(i,e), icon="🔥")
                                    continue
                # st.dataframe(list_instance_avail_from_blaster, use_container_width= True)
                # st.dataframe(list_instance_avail_from_blaster, use_container_width= True, column_config={"value": "instance-name"})
        with col_display:
            with st.container(border=True):
                st.write(":fire: :violet[**GRAPH**]")
            with st.container(border=True, height= 400):
                for i in select_running_instance_cb:
                    with st.popover(f":orange[:material/timeline: *{i}*]", use_container_width=True):
                        col_realtime, col_graph= st.columns([1,1])
                        with col_realtime:
                            with st.container(border= True, height=600):
                                st.write("##### :green[**:material/bolt: INTERFACES STATISTICS**]")
                                st.write(':violet[**:material/share: NETWORK INTERFACES**]')
                                exec("display_nw_interface_%s = st.empty()"%i)
                                st.write(':violet[**:material/share: ACCESS INTERFACES**]')
                                exec("display_acc_interface_%s = st.empty()"%i)
                        with st.container(border= True):
                            st.write('##### :green[:material/bolt: **STREAMS STATISTICS**]')
                            exec("display_streams_%s = st.empty()"%i)
                        # df_nw_tx_rx = pd.DataFrame([[0, 0]], columns=(["network_tx_packets", "network_rx_packets"]))
                        # df_acc_tx_rx = pd.DataFrame([[0, 0]], columns=(["access_tx_packets", "access_rx_packets"]))
                        with col_graph:
                            with st.container(border= True, height=600):
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
                                # Call API for network interface value
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
                                            time.sleep(0.01)
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
                                    
                                # Call API for access interface value
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
                                run_command_streams_sum_sc, run_command_streams_sum_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_stream_summary, '/_command')
                                if run_command_streams_sum_sc == 200:
                                    data_streams_summary = json.loads(run_command_streams_sum_ct)
                                    num_flows =len(data_streams_summary['stream-summary']) # Number network interfaces in json
                                    list_streams_name,list_streams_flowid, list_streams_direction, list_streams_sessionid, list_streams_tx_pps, list_streams_tx_bps, list_streams_rx_pps, list_streams_rx_bps, list_streams_loss=[],[],[],[],[],[],[],[],[]
                                    
                                    for n in range(num_flows): # Loop for make table of flow-ids
                                        list_streams_name.append(filter_dict(data_streams_summary, 'stream-summary.%s.name'%n))
                                        list_streams_flowid.append(filter_dict(data_streams_summary, 'stream-summary.%s.flow-id'%n))
                                        
                                        # Block for get stream-info
                                        flowid= filter_dict(data_streams_summary, 'stream-summary.%s.flow-id'%n)
                                        payload_command_stream_info="""
                                        {
                                            "command": "stream-info",
                                            "arguments": {"flow-id": %s}
                                        }
                                        """%flowid
                                        run_command_streams_info_sc, run_command_streams_info_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_stream_info, '/_command')
                                        if run_command_streams_info_sc == 200:
                                            data_streams_info = json.loads(run_command_streams_info_ct)

                                            list_streams_tx_pps.append(filter_dict(data_streams_info, 'stream-info.tx-pps'))
                                            list_streams_tx_bps.append(filter_dict(data_streams_info, 'stream-info.tx-bps-l2'))
                                            list_streams_rx_pps.append(filter_dict(data_streams_info, 'stream-info.rx-pps'))
                                            list_streams_rx_bps.append(filter_dict(data_streams_info, 'stream-info.rx-bps-l2'))
                                            # temp_list=[]
                                            # for o in range(10):
                                            #     temp_streams_info_sc, temp_streams_info_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_stream_info, '/_command')
                                            #     temp_data_streams_info = json.loads(temp_streams_info_ct)
                                            #     temp_list.append(filter_dict(temp_data_streams_info, 'stream-info.rx-loss'))
                                            #     time.sleep(0.001)
                                            # list_streams_loss.append(temp_list)
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
                                # exec("display_streams_%s.write(data_streams_info)"%i)
                            # run_command_counter_sc, run_command_counter_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_session_counters, '/_command')
                            # run_command_nw_int_sc, run_command_nw_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_network_interface, '/_command')
                            # run_command_acc_int_sc, run_command_acc_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_access_interface, '/_command')
                            # data_counter = json.loads(run_command_counter_ct)
                            # data_nw_int = json.loads(run_command_nw_int_ct)
                            # st.code(data_nw_int)
                            # data_acc_int = json.loads(run_command_acc_int_ct)
                            if run_command_nw_int_sc == 200:
                                # add_nw_df = pd.DataFrame([[filter_dict(data_nw_int, 'network-interfaces.0.tx-packets'), filter_dict(data_nw_int, 'network-interfaces.0.rx-packets')]], columns=(["network_tx_packets", "network_rx_packets"]))
                                # eval(f'nw_int_chart_{i}.add_rows(add_nw_df)')
                                # num_nw_int=len(data_nw_int['network-interfaces'])
                                for j in range(num_nw_int):
                                    add_nw_pps_df = pd.DataFrame([[filter_dict(data_nw_int, 'network-interfaces.%s.tx-pps'%j), filter_dict(data_nw_int, 'network-interfaces.%s.rx-pps'%j)]], columns=(["network_tx_pps", "network_rx_pps"]))
                                    eval(f'nw_int_chart_{i}_{j}_pps.add_rows(add_nw_pps_df)')
                                # add_acc_df = pd.DataFrame([[filter_dict(data_acc_int, 'access-interfaces.0.tx-packets'), filter_dict(data_acc_int, 'access-interfaces.0.rx-packets')]], columns=(["access_tx_packets", "access_rx_packets"]))
                                # eval(f'acc_int_chart_{i}.add_rows(add_acc_df)')
                                # num_acc_int = len(data_acc_int['access-interfaces'])
                            if run_command_acc_int_sc == 200:
                                for j in range(num_acc_int):
                                    add_acc_pps_df = pd.DataFrame([[filter_dict(data_acc_int, 'access-interfaces.%s.tx-pps'%j), filter_dict(data_acc_int, 'access-interfaces.%s.rx-pps'%j)]], columns=(["access_tx_pps", "access_rx_pps"]))
                                    eval(f'acc_int_chart_{i}_{j}_pps.add_rows(add_acc_pps_df)')
                                # add_acc_pps_df = pd.DataFrame([[filter_dict(data_acc_int, 'access-interfaces.%s.tx-pps'%j), filter_dict(data_acc_int, 'access-interfaces.0.rx-pps')]], columns=(["access_tx_pps", "access_rx_pps"]))
                                # eval(f'acc_int_chart_{i}_pps.add_rows(add_acc_pps_df)')
                        # time.sleep(0.5)
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
def convert_str_to_bool(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and (value == 'True' or value == 'False' or value == 'true' or value == 'false'):
                data[key] = bool(value)
            else:
                convert_str_to_bool(value)
    elif isinstance(data, list):
        for item in data:
            convert_str_to_bool(item)
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
        st.error('Can not get list-instance from server', icon="🚨")
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([":material/note_add: CREATE BY SELECTION",":material/note_add: CREATE BY TEMPLATE", ":material/edit_note: MODIFY", ":material/publish: JSON_IMPORT", ":material/note_alt: TEMPLATE"])
    with tab2:
        with st.container(border= True):
            st.subheader(':sunny: :green[**CREATE YOUR CONFIG**]')
            st.write(':violet[**YOUR INSTANCE NAME**]')
            with st.container(border=True):
                instance_name = st.text_input(':orange[Name of your instance] ', placeholder = 'Typing your instance name')
                if is_valid_name_instance(instance_name):
                    if instance_name + '.json' not in list_json:
                        st.info(':blue[Your instance\'s name can be use]', icon="🔥")
                        st.session_state.create_instance= False
                    else:
                        st.error('Your instance was duplicate, choose other name', icon="🚨")
                else:
                    st.error('Instance name is null or wrong syntax', icon="🔥")
            st.write(':violet[**SELECT YOUR PROTOCOLS TEMPLATES**]')
            col21, col22 = st.columns([4.2,1])
            with col21:
                with st.container(border= True):
                    select_template= st.selectbox(':orange[Select your template]?', list_templates, placeholder = 'Select one template')
                    log_authorize(st.session_state.user,blaster_server['ip'], f'Select template {select_template}')
            with col22:
                with st.popover(":material/visibility: :green[**VIEW**]", use_container_width=True):
                    st.info(":violet[Content of **%s template**]"%select_template, icon="🔥")
                    with open('%s/%s'%(path_templates,select_template), 'r') as file_template:
                        data= file_template.read()
                    st.code(data)
            col23, col24 = st.columns([2,1])
            with col23:
                with st.container(border= True):
                    st.write(':violet[**FILL YOUR VARIABLES BELOW**]')
                    list_var = get_variables_jinja_file(f'{path_templates}/{select_template}')
                    list_var.sort()
                    dict_input={}
                    index=int(len(list_var)/3)
                    col1, col2, col3 = st.columns([1,1,1])
                    with col1:
                        with st.container(border= True):
                            for i in list_var[0:index+1]:
                                exec(f"""dict_input['{i}'] = st.text_input(f':orange[**{i}**] ', placeholder = f'Typing {i}')""")
                                # st.warning('%s is null, fill it'%i, icon="🚨")
                    with col2:
                        with st.container(border= True):
                            for i in list_var[index+1:2*index+1]:
                                exec(f"""dict_input['{i}'] = st.text_input(f':orange[**{i}**] ', placeholder = f'Typing {i}')""")
                                # st.warning('%s is null, fill it'%i, icon="🚨")
                    with col3:
                        with st.container(border= True):
                            for i in list_var[2*index+1:len(list_var)]:
                                exec(f"""dict_input['{i}'] = st.text_input(f':orange[**{i}**] ', placeholder = f'Typing {i}')""")
                                # st.warning('%s is null, fill it'%i, icon="🚨")
                    # st.divider()
                    dict_check = {}
                    for d in list_var:
                        if d.endswith("address") or d.endswith("gateway") or d.endswith("gate"):
                            if is_valid_ip(dict_input[d]):
                                continue
                            else:
                                dict_check[d]= False
            with st.container(border= True):
                st.write(':violet[**INTERFACES ENABLE**]')
                str_interfaces_pre=""
                list_interfaces_templates = list(dict_interfaces_templates.keys())
                index_list_interfaces_templates = int(len(list_interfaces_templates)/2)
                col1, col2 = st.columns([1,1])
                with col1:
                    for s in list_interfaces_templates[0:index_list_interfaces_templates+1]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_interfaces}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            if var.endswith('interface'):
                                                with st.container(border= True):
                                                    st.write(f":orange[{s}/{i}/**{var}**]")
                                                    with st.container(border= True):
                                                        col_int1, col_int2 = st.columns([1.2,1])
                                                        with col_int1:
                                                            interface = st.selectbox(f":green[interface]", find_interface(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd']), key = f"{s}/{var}/{i}/interface" )
                                                        with col_int2:
                                                            # vlan = st.text_input(f":green[vlan]", key=f"{s}/{var}/{i}/vlan")
                                                            vlan = st.selectbox(f":green[vlan]", find_unused_vlans(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'], interface),key=f"{s}/{var}/{i}/vlan")
                                                if vlan == "":
                                                    exec(f"""{s}_content['{var}']= interface """)
                                                else:
                                                    exec(f"""{s}_content['{var}']= interface +'.'+ vlan""")
                                            else:
                                                with st.container(border= True):
                                                    exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_interfaces}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        if i==0:
                                            str_interfaces_pre += "\n" + content
                                        else:
                                            content1 = "\n".join(content.split("\n")[1:])
                                            str_interfaces_pre += "\n" + content1
                with col2:
                    for s in list_interfaces_templates[index_list_interfaces_templates+1:len(list_interfaces_templates)]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_interfaces}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            if var.endswith('interface'):
                                                with st.container(border= True):
                                                    st.write(f":orange[{s}/{i}/**{var}**]")
                                                    with st.container(border= True):
                                                        col_int1, col_int2 = st.columns([1.2,1])
                                                        with col_int1:
                                                            interface = st.selectbox(f":green[interface]", find_interface(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd']), key =f"{s}/{var}/{i}/interface" )
                                                        with col_int2:
                                                            # vlan = st.text_input(f":green[vlan]", key=f"{s}/{var}/{i}/vlan")
                                                            vlan = st.selectbox(f":green[vlan]", find_unused_vlans(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'], interface),key=f"{s}/{var}/{i}/vlan")
                                                if vlan == "":
                                                    exec(f"""{s}_content['{var}']= interface """)
                                                else:
                                                    exec(f"""{s}_content['{var}']= interface +'.'+ vlan""")
                                            else:
                                                with st.container(border= True):
                                                    exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_interfaces}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        if i==0:
                                            str_interfaces_pre += "\n" + content
                                        else:
                                            content1 = "\n".join(content.split("\n")[1:])
                                            str_interfaces_pre += "\n" + content1
            str_interfaces_pre1 = "\n  ".join(str_interfaces_pre.split("\n")[0:])
            str_interfaces = "interfaces:"+ str_interfaces_pre1
            # st.code(str_interfaces)
            with st.container(border= True):
                st.write(':violet[**STREAMS ENABLE**]')
                str_streams_pre=""
                list_streams_templates = list(dict_streams_templates.keys())
                index_list_streams_templates = int(len(list_streams_templates)/2)
                col1, col2 = st.columns([1,1])
                with col1:
                    for s in list_streams_templates[0:index_list_streams_templates+1]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_streams}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/stream_{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_streams}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        str_streams_pre += "\n" + content
                with col2:
                    for s in list_streams_templates[index_list_streams_templates+1:len(list_streams_templates)]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_streams}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/stream_{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_streams}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        str_streams_pre += "\n" + content
            str_streams = "streams:"+ str_streams_pre     
            with col24:
                with st.container(border= True):
                    st.write(':violet[**OR IMPORT YOUR VARIABLES WITH YAML FORMAT**]')
                    dict_export_file={}
                    with st.container(border= True):
                        data_import = st.file_uploader(":orange[CHOOSE YOUR YAML FILE]", accept_multiple_files=False, disabled= st.session_state.create_instance)
                        if data_import:
                            # if data_import.name[-4:] == '.yml' or data_import.name[-5:] == '.yaml':
                            stringio = StringIO(data_import.getvalue().decode("utf-8"))
                            string_data = stringio.read()
                            try:
                                convert_yaml = yaml.load(string_data, Loader=yaml.FullLoader)
                            except Exception as e:
                                st.error(f"Can not read yaml content, check error {e}")
                            # st.write(list(convert_yaml.keys())[0])
                            if list(convert_yaml.keys())[0] == instance_name: 
                                dict_input = convert_yaml.get(instance_name)
                                # st.write(import_dict_input)
                                if '' not in dict_input.values():
                                    if set(list_var).issubset(set(list(dict_input.keys()))):
                                        # Pop items no need
                                        pop=[]
                                        for e in list(dict_input.keys()):
                                            if e not in list_var:
                                                pop.append(e)
                                        for i in range(len(pop)):
                                            dict_input.pop(pop[i])
                                        dict_input['template']= select_template # Save mapping config: template
                                        st.info(':blue[Import variables successfully]', icon="🔥")
                                        log_authorize(st.session_state.user,blaster_server['ip'], 'IMPORT yaml file')
                                    else:
                                        list_var_lack= set(list_var).difference(set(list(dict_input.keys())))
                                        st.error(f'Data lack of vars **{list_var_lack}**', icon="🚨")
                                else:
                                    st.error('Have values empty', icon="🚨")
                            else:
                                st.error('Could not change intance-name', icon="🚨")
                            # else:
                            #     st.error('Upload file with .yaml or .yml , please. No accept other types ', icon="🚨")
                    if instance_name:
                        dict_export_file[instance_name] = dict_input
                        st.download_button(':material/schema: DATA_FORMAT', '---\n'+yaml.dump(dict_export_file, indent = 2, encoding= None), disabled= st.session_state.create_instance)
            with st.popover(":material/visibility: :green[**REVIEW**]", use_container_width=True):
                environment = Environment(loader=FileSystemLoader(f"{path_templates}"))
                template = environment.get_template(f"{select_template}")
                if str_streams== "streams:":
                    if str_interfaces =="interfaces:":
                        review_content= template.render(dict_input)
                    else:
                        review_content= template.render(dict_input) + '\n' + str_interfaces
                else:
                    if str_interfaces =="interfaces:":
                        review_content= template.render(dict_input) + '\n' + str_streams
                    else:
                        review_content= template.render(dict_input) + '\n' + str_interfaces + '\n' + str_streams
                    # review_content= template.render(dict_input) + '\n' + str_streams
                st.code(review_content)
            if st.button(':material/add: **CREATE INSTANCE**', type= 'primary', disabled = st.session_state.create_instance):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4,st.session_state.p5= False,False, True, False, False
                # if "" not in dict_input.values():
                if len(list(dict_check.keys())) == 0:
                    environment = Environment(loader=FileSystemLoader(f"{path_templates}"))
                    template = environment.get_template(f"{select_template}")
                    if str_streams== "streams:":
                        if str_interfaces =="interfaces:":
                            content= template.render(dict_input)
                        else:
                            content= template.render(dict_input) + '\n' + str_interfaces
                    else:
                        if str_interfaces =="interfaces:":
                            content= template.render(dict_input) + '\n' + str_streams
                        else:
                            content= template.render(dict_input) + '\n' + str_interfaces + '\n' + str_streams
                    with open('%s/%s.json'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as config:
                        # config.write(content)
                        json.dump(yaml.safe_load(content), config, indent=2)
                    dict_data, dict_data_input={}, {} # Build dict of data
                    for i in dict_input.keys():
                        dict_data_input.update({i: dict_input[i]})
                    dict_data_input['template']= select_template # Save mapping config: template
                    dict_data[instance_name]= dict_data_input
                    with open('%s/%s.yml'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as file_data:
                        file_data.write('---\n')
                        file_data.write(yaml.dump(dict_data))
                        file_data.write('\n')
                    if str_streams != "streams:":
                        with open('%s/%s_streams.yml'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as file_data_streams:
                            file_data_streams.write('---\n')
                            file_data_streams.write(str_streams)
                    if str_interfaces != "interfaces:":
                        with open('%s/%s_interfaces.yml'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as file_data_interfaces:
                            file_data_interfaces.write('---\n')
                            file_data_interfaces.write(str_interfaces)
                    st.info(':blue[Create successfully]', icon="🔥")
                    log_authorize(st.session_state.user,blaster_server['ip'], f'CREATE intance {instance_name}')
                    time.sleep(3)
                    st.rerun()
                else:
                    for i in dict_check.keys():
                        st.error(f'Input **{i}** wrong, check IP format before create, please', icon="🚨")    
    with tab3:
        with st.container(border= True):
            st.subheader(':sunny: :green[**MODIFY YOUR CONFIG**]')
            st.write(':violet[**YOUR INSTANCE NAME**]')
            st.session_state.edit_instance= False
            edit_list_var=[]
            with st.container(border=True):
                edit_instance= st.selectbox(':orange[Select your instance for modifing]?', list_instance, placeholder = 'Select one instance')
                log_authorize(st.session_state.user,blaster_server['ip'], f'Edit config {edit_instance}')
            if os.path.exists('%s/%s.yml'%(path_configs,edit_instance)):
                try:
                    with open("%s/%s.yml"%(path_configs,edit_instance) , 'r') as file_data:
                        config_data = yaml.load(file_data, Loader=yaml.FullLoader)
                        edit_template= config_data[edit_instance]['template']
                        edit_list_var = get_variables_jinja_file(f'{path_templates}/{edit_template}')
                        edit_list_var.sort()
                except Exception as ex:
                    st.error(f"Can not load data file {ex}")
                edit_dict_input={}
                if edit_list_var:
                    st.write(':violet[**EDIT YOUR PROTOCOLS VARIABLE BELOW**]')
                    index=int(len(edit_list_var)/3)
                    with st.container(border= True):
                        col1, col2, col3 = st.columns([1,1,1])
                        with col1:
                            with st.container(border= True):
                                for i in edit_list_var[0:index+1]:
                                    exec(f"""edit_dict_input['{i}'] = st.text_input(f':orange[Modify **{i}**] ',config_data['{edit_instance}']['{i}'], placeholder = f'Typing {i}')""")
                        with col2:
                            with st.container(border= True):
                                for i in edit_list_var[index+1:2*index+1]:
                                    exec(f"""edit_dict_input['{i}'] = st.text_input(f':orange[Modify **{i}**] ',config_data['{edit_instance}']['{i}'], placeholder = f'Typing {i}')""")
                        with col3:
                            with st.container(border= True):
                                for i in edit_list_var[2*index+1:len(edit_list_var)]:
                                    exec(f"""edit_dict_input['{i}'] = st.text_input(f':orange[Modify **{i}**] ',config_data['{edit_instance}']['{i}'], placeholder = f'Typing {i}')""") 
                else:
                    print('Can not load jinja template')
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
                col141, col151, col161 = st.columns([1,4,1])
                with col141:
                    if st.button(':material/save: **SAVE**', type= 'primary', use_container_width=True):
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False,False, True, False, False
                        try: 
                            json.loads(edit_json)
                            with open("%s/%s.json"%(path_configs,edit_instance) , 'w') as after_edit_json:
                                json.dump(json.loads(edit_json), after_edit_json, indent=2)
                                st.toast(':blue[Save instance **%s** successfully]'%edit_instance, icon="🔥")
                        except Exception as e:
                            st.error('Error json %s'%e, icon="🚨")
                with col161:
                    if st.button(':material/delete: **DELETE**', use_container_width=True):
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                        delete_config(path_configs, edit_instance)
                if edit_json != "":
                    with st.popover(":green[**:material/preview: REVIEW JSON**]", use_container_width=True):
                        # st.json(yaml.safe_load(edit_content))
                        st.code(json.dumps(json.loads(edit_json), indent=2))
            if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                with open('%s/%s_interfaces.yml'%(path_configs,edit_instance), mode= 'r') as interfaces:
                    edit_interfaces_input= yaml.safe_load(interfaces.read())
                edit_list_key_interfaces = list(edit_interfaces_input['interfaces'].keys())
                if len(edit_interfaces_input['interfaces']) == 0 :
                    st.write("interfaces null")
                else:
                    dict_edit_interfaces ={}
                    st.write(f':violet[**EDIT INTERFACES VARIABLE BELOW**]')
                    with st.container(border= True):
                        index_int = int(len(edit_list_key_interfaces)/2)
                        # st.write(edit_list_key_interfaces)
                        col1, col2= st.columns([1,1])
                        with col1:
                            for key in edit_list_key_interfaces[0:index_int+1]:
                                if check_key_value_is_list(edit_interfaces_input['interfaces'], key):
                                    exec(f"edit_interfaces_{key} = []")
                                    with st.container(border= True):
                                        st.write(f':green[**interfaces/{key}**]')
                                        for i in range(len(edit_interfaces_input['interfaces'][key])):
                                            temp_edit_interfaces ={}
                                            with st.popover(f":orange[interfaces_{key}_{i}]", use_container_width=True):
                                                list_input= edit_interfaces_input['interfaces'][key][i].keys()
                                                for j in list_input:
                                                    exec(f"""temp_edit_interfaces['{j}'] = st.text_input(f":orange[interaces_{key}_{i}]/:orange[**{j}**]", edit_interfaces_input['interfaces'][key][i]['{j}'])""")
                                            eval(f"edit_interfaces_{key}.append(temp_edit_interfaces)")
                                            if i == (len(edit_interfaces_input['interfaces'][key])-1):
                                                ###### Convert value of interface value to int #############################
                                                for k in eval(f"edit_interfaces_{key}"):
                                                    list_keys = list(k.keys())
                                                    for n in list_keys:
                                                        try:
                                                            temp=int(k[n])
                                                            k[n] = temp
                                                        except:
                                                            pass
                                                        if (k[n]== 'True') or (k[n]== 'true'):
                                                            k[n] = True
                                                        if (k[n]== 'False') or (k[n]== 'false'):
                                                            k[n] = False
                                                exec(f"dict_edit_interfaces[key] = edit_interfaces_{key}")
                                else:
                                    # key_convert= key.replace('-','_')
                                    with st.container(border= True):
                                        st.write(f':green[**interfaces/{key}**]')
                                        with st.popover(f":orange[interfaces_{key}]", use_container_width=True):
                                            temp_edit_interfaces = st.text_input(f":orange[interfaces_{key}]", edit_interfaces_input['interfaces'][key])
                                        try:
                                            temp_edit_interfaces= int(temp_edit_interfaces)
                                        except:
                                            pass
                                        if isinstance(edit_interfaces_input['interfaces'][key], float):
                                            try:
                                                temp_edit_interfaces= float(temp_edit_interfaces)
                                            except:
                                                pass
                                        dict_edit_interfaces[key] = temp_edit_interfaces
                        with col2:
                            for key in edit_list_key_interfaces[index_int+1:len(edit_list_key_interfaces)]:
                                if check_key_value_is_list(edit_interfaces_input['interfaces'],key):
                                    exec(f"edit_interfaces_{key} = []")
                                    with st.container(border= True):
                                        st.write(f':green[**interfaces/{key}**]')
                                        for i in range(len(edit_interfaces_input['interfaces'][key])):
                                            temp_edit_interfaces ={}
                                            with st.popover(f":orange[interfaces_{key}_{i}]", use_container_width=True):
                                                list_input= edit_interfaces_input['interfaces'][key][i].keys()
                                                for j in list_input:
                                                    exec(f"""temp_edit_interfaces['{j}'] = st.text_input(f":orange[interaces_{key}_{i}]/:orange[**{j}**]", edit_interfaces_input['interfaces'][key][i]['{j}'])""")
                                            eval(f"edit_interfaces_{key}.append(temp_edit_interfaces)")
                                            if i == (len(edit_interfaces_input['interfaces'][key])-1):
                                                ###### Convert value of interface value to int #############################
                                                for k in eval(f"edit_interfaces_{key}"):
                                                    list_keys = list(k.keys())
                                                    for n in list_keys:
                                                        try:
                                                            temp=int(k[n])
                                                            k[n] = temp
                                                        except:
                                                            pass
                                                        if (k[n]== 'True') or (k[n]== 'true'):
                                                            k[n] = True
                                                        if (k[n]== 'False') or (k[n]== 'false'):
                                                            k[n] = False
                                                exec(f"dict_edit_interfaces[key] = edit_interfaces_{key}")
                                else:
                                    # key_convert= key.replace('-','_')
                                    with st.container(border= True):
                                        st.write(f':green[**interfaces/{key}**]')
                                        with st.popover(f":orange[interfaces_{key}]", use_container_width=True):
                                            temp_edit_interfaces = st.text_input(f":orange[interfaces_{key}]", edit_interfaces_input['interfaces'][key])
                                        try:
                                            temp_edit_interfaces= int(temp_edit_interfaces)
                                        except:
                                            pass
                                        if isinstance(edit_interfaces_input['interfaces'][key], float):
                                            try:
                                                temp_edit_interfaces= float(temp_edit_interfaces)
                                            except:
                                                pass
                                        dict_edit_interfaces[key] = temp_edit_interfaces
                        # st.write(dict_edit_interfaces)
            if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                # st.divider()
                with open('%s/%s_streams.yml'%(path_configs,edit_instance), mode= 'r') as streams:
                    edit_streams_input= yaml.safe_load(streams.read())
                # st.write(edit_streams_input['streams'])
                if len(edit_streams_input['streams']) == 0 :
                    st.write("streams null")
                else:
                    edit_streams = []
                    st.write(':violet[**EDIT STREAMS VARIABLE BELOW**]')
                    with st.container(border= True):
                        index_col = int(len(edit_streams_input['streams'])/2)
                        col1, col2= st.columns([1,1])
                        with col1:
                            for i in range(0,index_col+1):
                                temp_edit_streams ={}
                                with st.popover(f":orange[stream_{i}]", use_container_width=True):
                                    list_input= edit_streams_input['streams'][i].keys()
                                    for j in list_input:
                                        exec(f"""temp_edit_streams['{j}'] = st.text_input(f":orange[streams_{i}]/:orange[**{j}**]", edit_streams_input['streams'][i]['{j}'])""")
                                edit_streams.append(temp_edit_streams)
                        with col2:
                            for i in range(index_col+1,len(edit_streams_input['streams'])):
                                temp_edit_streams ={}
                                with st.popover(f":orange[stream_{i}]", use_container_width=True):
                                    list_input= edit_streams_input['streams'][i].keys()
                                    for j in list_input:
                                        exec(f"""temp_edit_streams['{j}'] = st.text_input(f":orange[streams_{i}]/:orange[**{j}**]", edit_streams_input['streams'][i]['{j}'])""")
                                edit_streams.append(temp_edit_streams)
                ###### Convert value of streams to int #############################
                for i in edit_streams:
                    list_keys = list(i.keys())
                    for j in list_keys:
                        try:
                            temp=int(i[j])
                            i[j] = temp
                        except:
                            continue
                # st.write(edit_streams)
            st.divider()
            edit_content=""
            col14, col15, col16 = st.columns([1,4,1])
            if os.path.exists('%s/%s.yml'%(path_configs,edit_instance)):
                with col14:
                    if st.button(':material/save: **SAVE**', type= 'primary', disabled = st.session_state.edit_instance, use_container_width=True):
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False,False, True, False, False
                        if "" not in edit_dict_input.values():
                            streams_save={}
                            interfaces_save={}
                            if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                                streams_save['streams']= edit_streams
                            if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                                interfaces_save['interfaces']= dict_edit_interfaces
                            # Render config from Jinja file
                            environment = Environment(loader=FileSystemLoader(f"{path_templates}"))
                            template = environment.get_template(f"{config_data[edit_instance]['template']}")
                            edit_content = template.render(edit_dict_input)
                            ### Save new config
                            with open('%s/%s.json'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as edit_config:
                                if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                                    if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                                        edit_content += "\n" + yaml.dump(streams_save) + "\n" +yaml.dump(interfaces_save)
                                    else:
                                        edit_content += "\n" + yaml.dump(streams_save)
                                else:
                                    if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                                        edit_content += "\n" +yaml.dump(interfaces_save)
                                json.dump(yaml.safe_load(edit_content), edit_config, indent=2)
                            save_dict_data, save_dict_data_input={}, {} # Build dict of data
                            for i in edit_dict_input.keys():
                                save_dict_data_input.update({i: edit_dict_input[i]})
                            save_dict_data_input['template']= config_data[edit_instance]['template'] # Save mapping config: template
                            save_dict_data[edit_instance]= save_dict_data_input
                            ### Save data instance to yaml
                            with open('%s/%s.yml'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as data:
                                data.write('---\n')
                                data.write(yaml.dump(save_dict_data))
                                data.write('\n')
                            ### Save interfaces to yaml
                            if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                                with open('%s/%s_interfaces.yml'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as interfaces_data:
                                    interfaces_data.write('---\n')
                                    interfaces_data.write(yaml.dump(interfaces_save))
                            ### Save streams to yaml
                            if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                                with open('%s/%s_streams.yml'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as streams_data:
                                    streams_data.write('---\n')
                                    streams_data.write(yaml.dump(streams_save))
                            st.toast(':blue[Save instance %s successfully]'%edit_instance, icon="🔥")
                            log_authorize(st.session_state.user,blaster_server['ip'], f'Edit and save instance {edit_instance}')
                        else:
                            st.toast(':red[Have parameters empty, fill us before save, please]', icon="🚨")
                with col16:
                    if st.button(':material/delete: **DELETE**', use_container_width=True):
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                        delete_config(path_configs, edit_instance)
                if edit_content != "":
                    with st.popover(":green[**REVIEW**]", use_container_width=True):
                        # st.json(yaml.safe_load(edit_content))
                        st.code(edit_content)
    if dict_user_db[st.session_state.user] == 'admin' or dict_user_db[st.session_state.user] == 'admin1':
        with tab5:
            with st.container(border= True):
                st.subheader(':sunny: :green[YOUR SELECTION]')
                import_radio = st.radio(
                    ":violet[SELECT KIND OF TEMPLATES BELOW]",
                    [":orange[PROTOCOLS]", ":orange[INTERFACES]", ":orange[STREAMS]"],
                    index=None,
                )
            if import_radio == ":orange[PROTOCOLS]":
                col1_template, col2_template = st.columns([1.25,1])
                with col2_template:
                    with st.container(border=True, height=630):
                        st.subheader(':desktop_computer: :green[IMPORT PROTOCOLS TEMPLATE]')
                        st.write(':violet[Upload protocols template]')
                        protocols_file_import = st.file_uploader("Choose a Template file", accept_multiple_files=False)
                        if protocols_file_import:
                            if protocols_file_import.name[-3:] == '.j2':
                                stringio = StringIO(protocols_file_import.getvalue().decode("utf-8"))
                                string_data = stringio.read() 
                                if protocols_file_import.name not in list_templates:
                                    with open(f"{path_templates}/{protocols_file_import.name}", 'w') as jinja:
                                        jinja.write(string_data)
                                        st.info(':blue[Upload template %s successfully]'%protocols_file_import.name, icon="🔥")
                                        log_authorize(st.session_state.user,blaster_server['ip'], f'Import protocols template file {protocols_file_import.name}')
                                else:
                                    st.error('Duplicate name file, change your file name and try again', icon="🚨")
                            else:
                                st.error('Upload file with .j2 , please. No accept other types ', icon="🚨")
                        else:
                            st.info(':blue[Select file upload]', icon="🔥")
                with col1_template:
                    with st.container(border=True):
                        st.subheader(':memo: :green[EDIT PROTOCOLS TEMPLATE]')
                        template_edit = st.selectbox(':orange[Select your template for editing]?', list_templates, placeholder = 'Select one template')
                        with open(f"{path_templates}/{template_edit}", "r") as view:
                            cont1= view.read()
                        with st.container(border=True):
                            edit_template_text = st_ace(
                            value= cont1,
                            language= 'yaml', 
                            theme= '', 
                            show_gutter= True, 
                            keybinding='vscode', 
                            auto_update= False, 
                            placeholder= '*Edit your template*',
                            height=350)
                        col100, col101, col102 =st.columns([1,2,1])
                        with col100:
                            if st.button(":material/save: SAVE", type = 'primary', use_container_width= True):
                                with open(f"{path_templates}/{template_edit}", "w") as write:
                                    write.write(edit_template_text)
                                st.toast(f':blue[Save your template **{template_edit}** successfully]', icon="🔥")
                        with col102:
                            if st.button(":material/delete: DELETE", use_container_width= True):
                                os.remove(f"{path_templates}/{template_edit}")
                                st.info(':blue[Delete successfully]', icon="🔥")
                                st.rerun()
            if import_radio == ":orange[INTERFACES]":
                col1_template, col2_template = st.columns([1.25,1])
                with col2_template:
                    with st.container(border=True, height=630):
                        st.subheader(':desktop_computer: :green[IMPORT INTERFACES TEMPLATE]')
                        st.write(':violet[Upload interfaces template]')
                        protocols_file_import = st.file_uploader("Choose a Template file", accept_multiple_files=False)
                        if protocols_file_import:
                            if protocols_file_import.name[-3:] == '.j2':
                                stringio = StringIO(protocols_file_import.getvalue().decode("utf-8"))
                                string_data = stringio.read() 
                                if protocols_file_import.name not in list_templates:
                                    with open(f"{path_templates_interfaces}/{protocols_file_import.name}", 'w') as jinja:
                                        jinja.write(string_data)
                                        st.info(':blue[Upload template %s successfully]'%protocols_file_import.name, icon="🔥")
                                        log_authorize(st.session_state.user,blaster_server['ip'], f'Import interfaces template file {protocols_file_import.name}')
                                else:
                                    st.error('Duplicate name file, change your file name and try again', icon="🚨")
                            else:
                                st.error('Upload file with .j2 , please. No accept other types ', icon="🚨")
                        else:
                            st.info(':blue[Select file upload]', icon="🔥")
                with col1_template:
                    with st.container(border=True):
                        st.subheader(':memo: :green[EDIT INTERFACES TEMPLATE]')
                        template_edit = st.selectbox(':orange[Select your template for editing]?', list_interfaces, placeholder = 'Select one template')
                        with open(f"{path_templates_interfaces}/{template_edit}.j2", "r") as view:
                            cont1= view.read()
                        with st.container(border=True):
                            edit_template_text = st_ace(
                            value= cont1,
                            language= 'yaml', 
                            theme= '', 
                            show_gutter= True, 
                            keybinding='vscode', 
                            auto_update= False, 
                            placeholder= '*Edit your template*',
                            height=350)
                        col100, col101, col102 =st.columns([1,2,1])
                        with col100:
                            if st.button("SAVE", type = 'primary', use_container_width= True):
                                with open(f"{path_templates_interfaces}/{template_edit}.j2", "w") as write:
                                    write.write(edit_template_text)
                                st.toast(f':blue[Save your template **{template_edit}** successfully]', icon="🔥")
                        with col102:
                            if st.button(":material/delete: DELETE", use_container_width= True):
                                os.remove(f"{path_templates_interfaces}/{template_edit}.j2")
                                st.info(':blue[Delete successfully]', icon="🔥")
                                st.rerun()
            if import_radio == ":orange[STREAMS]":
                col1_template, col2_template = st.columns([1.25,1])
                with col2_template:
                    with st.container(border=True, height=630):
                        st.subheader(':desktop_computer: :green[IMPORT STREAMS TEMPLATE]')
                        st.write(':violet[Upload streams template]')
                        streams_file_import = st.file_uploader("Choose a Template file", accept_multiple_files=False)
                        if streams_file_import:
                            if streams_file_import.name[-3:] == '.j2':
                                stringio = StringIO(streams_file_import.getvalue().decode("utf-8"))
                                string_data = stringio.read() 
                                if streams_file_import.name not in list_templates:
                                    with open(f"{path_templates_streams}/{streams_file_import.name}", 'w') as jinja:
                                        jinja.write(string_data)
                                        st.info(':blue[Upload template %s successfully]'%streams_file_import.name, icon="🔥")
                                        log_authorize(st.session_state.user,blaster_server['ip'], f'Import template file {streams_file_import.name}')
                                else:
                                    st.error('Duplicate name file, change your file name and try again', icon="🚨")
                            else:
                                st.error('Upload file with .j2 , please. No accept other types ', icon="🚨")
                        else:
                            st.info(':blue[Select file upload]', icon="🔥")
                with col1_template:
                    with st.container(border=True):
                        st.subheader(':memo: :green[EDIT STREAMS TEMPLATE]')
                        template_edit = st.selectbox(':orange[Select your template for editing]?', list_streams_templates, placeholder = 'Select one template')
                        with open(f"{path_templates_streams}/{template_edit}.j2", "r") as view:
                            cont1= view.read()
                        with st.container(border=True):
                            edit_template_text = st_ace(
                            value= cont1,
                            language= 'yaml', 
                            theme= '', 
                            show_gutter= True, 
                            keybinding='vscode', 
                            auto_update= False, 
                            placeholder= '*Edit your template*',
                            height=350)
                        col100, col101, col102 =st.columns([1,2,1])
                        with col100:
                            if st.button(":material/save: SAVE", use_container_width=True, type = 'primary'):
                                with open(f"{path_templates_streams}/{template_edit}.j2", "w") as write:
                                    write.write(edit_template_text)
                                st.toast(f':blue[Save your template **{template_edit}** successfully]', icon="🔥")
                        with col102:
                            if st.button(":material/delete: DELETE", use_container_width= True):
                                os.remove(f"{path_templates_streams}/{template_edit}.j2")
                                st.info(':blue[Delete successfully]', icon="🔥")
                                st.rerun()
            if import_radio == ":orange[PROTOCOLS]":
                with st.container(border= True):
                    st.subheader(':package: :green[BUILD YOUR PROTOCOLS TEMPLATE]')
                    # st.write(list_part)
                    output_str=""
                    st.write(":violet[Select your pieces of your template]")
                    with st.container(border=True):
                        col1_temp, col2_temp = st.columns([1,1])
                        index_temp = int(len(list_part)/2)
                        with col1_temp:
                            for i in list_part[0:index_temp+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_element_config[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= False, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_part.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        with col2_temp:
                            for i in list_part[index_temp+1:len(list_part)+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_element_config[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= False, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_part.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        name_template = st.text_input(':violet[Input your name of new template]')
                        if (f"{name_template}.j2") in list_templates:
                            st.error('Name existed, try other name', icon="🚨")
                            st.session_state.save_template= True
                        else:
                            if name_template == "":
                                st.warning("Name can not null", icon="🔥")
                                st.session_state.save_template= True
                            else:
                                if is_valid_name_instance(name_template):
                                    st.info("You can use this name", icon="🔥")
                                    st.session_state.save_template= False
                                else:
                                    st.warning("Name wrong syntax", icon="🔥")
                                    st.session_state.save_template= True
                    if st.button(":material/save: **SAVE**", type= 'primary', disabled= st.session_state.save_template):
                        if output_str != "":
                            with open(f"{path_templates}/{name_template}.j2", 'w') as file:
                                file.write(output_str)
                            st.code(output_str)
                        else:
                            st.error("Select above first", icon="🚨")
            if import_radio == ":orange[INTERFACES]":
                with st.container(border= True):
                    st.subheader(':package: :green[BUILD YOUR INTERFACES TEMPLATE]')
                    # st.write(list_interfaces)
                    output_str=""
                    st.write(":violet[Select your pieces of your template]")
                    with st.container(border=True):
                        col1_temp, col2_temp = st.columns([1,1])
                        index_temp = int(len(list_interfaces)/2)
                        with col1_temp:
                            for i in list_interfaces[0:index_temp+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]', key='{i}')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_interfaces_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= False, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_interfaces.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        with col2_temp:
                            for i in list_interfaces[index_temp+1:len(list_interfaces)+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]', key='{i}')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_interfaces_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= False, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_interfaces.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        name_template = st.text_input(':violet[Input your name of new template]')
                        if (f"{name_template}") in list_interfaces:
                            st.error('Name existed, try other name', icon="🚨")
                            st.session_state.save_template= True
                        else:
                            if name_template == "":
                                st.warning("Name can not null", icon="🔥")
                                st.session_state.save_template= True
                            else:
                                if is_valid_name_instance(name_template):
                                    st.info("You can use this name", icon="🔥")
                                    st.session_state.save_template= False
                                else:
                                    st.warning("Name wrong syntax", icon="🔥")
                                    st.session_state.save_template= True
                    if st.button(":material/save: **SAVE**", type= 'primary', disabled= st.session_state.save_template):
                        if output_str != "":
                            with open(f"{path_templates_interfaces}/{name_template}.j2", 'w') as file:
                                file.write(output_str)
                            st.code(output_str)
                        else:
                            st.error("Select above first", icon="🚨")
            if import_radio == ":orange[STREAMS]":
                with st.container(border= True):
                    st.subheader(':package: :green[BUILD YOUR STREAMS TEMPLATE]')
                    # st.write(list_part)
                    streams_output_str=""
                    st.write(":violet[Select your pieces of your template]")
                    with st.container(border=True):
                        col1_temp, col2_temp = st.columns([1,1])
                        index_temp = int(len(list_streams)/2)
                        with col1_temp:
                            for i in list_streams[0:index_temp+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[.**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_streams_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= False, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_streams.index(i))
                                            #########################################
                                            streams_output_str += '\n' + add_part
                        with col2_temp:
                            for i in list_streams[index_temp+1:len(list_streams)+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[.**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_streams_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= False, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_streams.index(i))
                                            #########################################
                                            streams_output_str += '\n' + add_part
                        name_template = st.text_input(':violet[Input your name of new template]',"streams_")
                        if (f"{name_template}.j2") in list_streams:
                            st.error('Name existed, try other name', icon="🚨")
                            st.session_state.save_template= True
                        else:
                            if name_template == "streams_":
                                st.warning("Typing your name", icon="🔥")
                                st.session_state.save_template= True
                            else:
                                if is_valid_name_instance(name_template):
                                    st.info("You can use this name", icon="🔥")
                                    st.session_state.save_template= False
                                else:
                                    st.warning("Name wrong syntax", icon="🔥")
                                    st.session_state.save_template= True
                    if st.button(":material/save: **SAVE**", type= 'primary', disabled= st.session_state.save_template):
                        if streams_output_str != "":
                            with open(f"{path_templates_streams}/{name_template}.j2", 'w') as file:
                                file.write(streams_output_str)
                            st.code(streams_output_str)
                        else:
                            st.error("Select above first", icon="🚨")
    with tab4:
        col1, col2 = st.columns([2,2])
        with col1:
            with st.container(border=True):
                name_json_config= st.text_input("**:violet[1. INPUT NAME OF CONFIG]**")
                data_json_import = st.file_uploader("**:violet[2. CHOOSE YOUR JSON FILE]**", accept_multiple_files=False)
                if data_json_import:
                    stringio = StringIO(data_json_import.getvalue().decode("utf-8"))
                    string_data = stringio.read()
                    try:
                        input_json = json.loads(string_data)
                        if is_valid_name_instance(name_json_config):
                            # st.write(name_json_config)
                            if (name_json_config+'.json') not in list_json:
                                try:
                                    export_yaml= yaml.dump(input_json)
                                    with col2:
                                        with st.container(border=True):
                                            st.write("**:violet[3. EDIT CONFIG]**")
                                            with st.container(border=True):
                                                convert_json= st_ace(
                                                value= export_yaml,
                                                language= 'yaml', 
                                                theme= '', 
                                                show_gutter= True, 
                                                keybinding='vscode', 
                                                auto_update= True, 
                                                placeholder= '*Edit your config*')
                                            if st.button("SAVE CONFIG", type= 'primary', use_container_width= True):
                                                with open('%s/%s.json'%(path_configs,name_json_config), mode= 'w', encoding= 'utf-8') as json_config:
                                                    json.dump(yaml.safe_load(convert_json), json_config, indent=2)
                                                st.success("Config save successfully", icon="🔥")
                                                log_authorize(st.session_state.user,blaster_server['ip'], f'Create new json {name_json_config}')
                                except Exception as e:
                                    with col2:
                                        st.error(f"Can not yaml dump content, check error {e}", icon="🚨")
                            else:
                                st.error('Name existed', icon="🚨")
                        else:
                            st.error('Name empty or wrong syntax', icon="🚨")
                    except Exception as e:
                        st.error(f"Can not read json content, check error {e}", icon="🚨")
                    # st.write(list_json)
                else:
                    st.error('Import File', icon="🚨")
    with tab1:
        with st.container(border= True):
            st.subheader(':sunny: :green[**CREATE YOUR CONFIG**]')
            with st.container(border= True):
                st.write(':violet[**:material/account_circle: YOUR INSTANCE NAME**]')
                with st.container(border=True):
                    select_instance_name = st.text_input(':orange[Name of your instance] ', placeholder = 'Typing your instance name', key='create_by_selection')
                    if is_valid_name_instance(select_instance_name):
                        if select_instance_name + '.json' not in list_json:
                            st.info(':blue[Your instance\'s name can be use]', icon="🔥")
                            st.session_state.create_instance= False
                        else:
                            st.error('Your instance was duplicate, choose other name', icon="🚨")
                    else:
                        st.error('Instance name is null or wrong syntax', icon="🔥")
            with open('all_conf.yaml', 'r') as file_template:
                try:
                    data=yaml.safe_load(file_template) # This dict is library of bngblaster
                except yaml.YAMLError as exc:
                    st.error(exc)
            load_data=copy_dict_with_empty_values(data) # This dict is library of bngblaster
            dict_var={} # Var for save value from UI
            ##################### Value of columns dynamic to deep elements of dict ######################
            _, num_col= find_deepest_element(data)
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
                dict_selection_part_UI(data,"", 0)
            # st.write(dict_var)
            if dict_var:
                #For process len(list of dict)
                for i,v in dict_var.items(): 
                    if "num_" in i:
                        path_ext= i.split("num_")[1]
                        path= path_ext.split('___')
                        path.remove("")
                        for k in path:
                            if k.find('_') != -1:
                                path[path.index(k)]=k.replace('_','-')
                        str_path=""
                        for o in path:
                            if isinstance(o, int):
                                str_path += "[%s]"%o
                            else:
                                str_path += "['%s']"%o
                        for u in range(v-1):
                            exec("copy%s = data%s"%(u, str_path))
                            exec("copy_empty= copy_dict_with_empty_values(copy%s)"%u)
                            exec("load_data%s.extend(copy_empty)"%(str_path)) # Extend number element list of dict
                #For process input of elements UI
                for i,v in dict_var.items(): 
                    if "num_" not in i:
                        path= i.split('___')
                        path.remove("")
                        # st.write(path)
                        for k in path:
                            if k.find('_') != -1:
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
                        exec("load_data%s= '%s'"%(str_path, v))
                        # st.write("load_data%s= '%s'"%(str_path, v))
            for i in range(num_col+1): # For remove emptry dict, list, str
                pop_empty_structures(load_data)
            with st.popover(':green[**:material/visibility: REVIEW**]', use_container_width=True):
                convert_str_to_int(load_data)
                convert_str_to_bool(load_data)
                st.code(json.dumps(load_data, indent=2))
            if st.button(':material/add: **CREATE INSTANCE**', type= 'primary', disabled = st.session_state.create_instance, key= 'btn_create_by_selection'):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4,st.session_state.p5= False,False, True, False, False
                # if "" not in dict_input.values():
                with open('%s/%s.json'%(path_configs,select_instance_name), mode= 'w', encoding= 'utf-8') as config:
                    json.dump(load_data, config, indent=2)
                st.info(':blue[Create successfully]', icon="🔥")
                log_authorize(st.session_state.user,blaster_server['ip'], f'CREATE intance {instance_name}')
                time.sleep(3)
                st.rerun()
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
                    instance= st.selectbox(':orange[:material/done: Select your instance]?', list_instance, placeholder = 'Select one instance')
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
                        st.info(':material/info: Instance **%s** use network interface *%s*'%(instance, temp_list_nw))
                        temp_list_acc=[]
                        for i in range(len(data_json['interfaces']['access'])):
                            temp_list_acc.append(data_json['interfaces']['access'][i]['interface'])
                        st.info(':material/info: Instance **%s** use access interface *%s*'%(instance, temp_list_acc))
                    except Exception as e:
                        print('[RUN] Json config dont have network or access interface, error %s'%e)
            instance_exist_st, instance_exist_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start)
            if "started" in str(instance_exist_ct):
                st.session_state.button_start= True
                st.session_state.button_stop= False
                with col19:
                    st.warning("This instance already running", icon="🔥")
                if os.path.exists('%s/%s.yml'%(path_configs,instance)):
                    with open('%s/%s.yml'%(path_configs,instance), 'r') as file_temp:
                        run_template = yaml.load(file_temp, Loader=yaml.FullLoader)
                    col17, col18 =st.columns([1,1])
                    if run_template[instance]['template'] == "bgp.j2":
                        with col17:
                            with st.form('ADVERTISE'):
                                prefix= st.text_input(f":orange[Your prefix you want advertise: ]","", placeholder = "Fill your IP prefix")
                                num_prefix= st.text_input(f":orange[Your number of prefixs you want advertise: ]","", placeholder = "Fill number")
                                submitted = st.form_submit_button(label= "ADVERTISE")
                                if submitted:
                                    if "/" in prefix and prefix:
                                        name_bgp_update = instance + "_"+ prefix.split('/')[0]+"_"+num_prefix
                                        payload_command_bgp_raw_update= """
                                        {
                                            "command": "bgp-raw-update",
                                            "arguments": {
                                                "file": "/var/bngblaster/uploads/%s.bgp"
                                            }
                                        }
                                        """%name_bgp_update
                                        if prefix and num_prefix:
                                            # subprocess.run(["bgpupdate","-f", "%s.bgp"%instance,"-a", run_template[instance]['local_as'], "-n",run_template[instance]['bgp_local_address'], "-p", prefix, "-P",num_prefix,"-f", "withdraw.bgp","--withdraw"], capture_output=True, text=True)
                                            result = subprocess.run(["bgpupdate","-f", "./bgp_update/%s.bgp"%name_bgp_update,"-a", run_template[instance]['bgp_local_as'], "-n",run_template[instance]['bgp_local_address'], "-p", prefix, "-P",num_prefix], capture_output=True, text=True)
                                            if 'error' not in str(result):
                                                # send_file = push_file_to_server_rest_api(blaster_server['ip'], '5000', './bgp_update/%s.bgp'%name_bgp_update)
                                                push_file_to_server_by_ftp(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'],f"{path_bgp_update}/{name_bgp_update}.bgp", f'/var/bngblaster/uploads/{name_bgp_update}.bgp')
                                                adv_sc, adv_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_command_bgp_raw_update, '/_command')
                                                st.info(':blue[Advertise sucessfully]', icon="🔥")
                                                log_authorize(st.session_state.user,blaster_server['ip'], f'Advertise BGP route {prefix} num {num_prefix}')
                                            else:
                                                st.error(":violet[Wrong prefix]", icon="🔥")
                                        else:
                                            st.error(":violet[Fill prefix advertise above first]", icon="🔥")
                                    else:
                                        st.error('Type your prefix with subnet mask, plz', icon="🚨")
                        with col18:
                            with st.form('WITHDRAW'):
                                prefix_wd= st.text_input(f":orange[Your prefix you want withdraw: ]","", placeholder = "Fill your IP prefix")
                                num_prefix_wd= st.text_input(f":orange[Your number of prefixs you want withdraw: ]","", placeholder = "Fill number")
                                submitted = st.form_submit_button(label= "WITHDRAW")
                                if submitted:
                                    if "/" in prefix_wd and prefix_wd:
                                        name_bgp_update_wd = instance+"_withdraw_"+ prefix_wd.split('/')[0]+"_"+num_prefix_wd
                                        payload_command_bgp_raw_update_wd= """
                                        {
                                            "command": "bgp-raw-update",
                                            "arguments": {
                                                "file": "/var/bngblaster/uploads/%s.bgp"
                                            }
                                        }
                                        """%name_bgp_update_wd
                                        if prefix_wd and num_prefix_wd:
                                            result_wd= subprocess.run(["bgpupdate","-a", run_template[instance]['bgp_local_as'], "-n",run_template[instance]['bgp_local_address'], "-p", prefix_wd, "-P",num_prefix_wd,"-f", "./bgp_update/%s.bgp"%name_bgp_update_wd,"--withdraw"], capture_output=True, text=True)
                                            if "error" not in str(result_wd):
                                                # send_file_wd = push_file_to_server_rest_api(blaster_server['ip'], '5000', './bgp_update/%s.bgp'%name_bgp_update_wd)
                                                push_file_to_server_by_ftp(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']]['user'],dict_blaster_db_format[blaster_server['ip']]['passwd'] ,f"{path_bgp_update}/{name_bgp_update_wd}.bgp", f'/var/bngblaster/uploads/{name_bgp_update_wd}.bgp')
                                                wd_sc, wd_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_command_bgp_raw_update_wd, '/_command')
                                                st.info(':blue[Withdraw sucessfully]', icon="🔥")
                                                log_authorize(st.session_state.user,blaster_server['ip'], f'Withdraw BGP route {prefix_wd} num {num_prefix_wd}')
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
                    with st.container(border= True):
                        if instance in list_instance_avail_from_blaster:
                            st.warning(f'Instance **{instance}** can start but its config will be overrided', icon="🔥")
                        else:
                            st.info("You can start this instance", icon="🔥")
            with col19:
                if st.button('**START** :material/sound_sampler: ', type = 'primary',use_container_width=True, disabled= st.session_state.button_start):
                    # Get list interface "ens" from config and send remote set bng-blaster server
                    if os.path.exists('%s/%s_interfaces.yml'%(path_configs,instance)):
                        with open(f"{path_configs}/{instance}_interfaces.yml", "r") as interfaces_set:
                            data_set = yaml.safe_load(interfaces_set.read())
                        list_int_key = list(data_set['interfaces'].keys())
                        int_list =[]
                        if len(list_int_key) == 1:
                            for i in data_set['interfaces'][list_int_key[0]]:
                                try:
                                    int_list.append(i['interface'])
                                except:
                                    continue
                        else:
                            for type_int in list_int_key:
                                if isinstance(data_set['interfaces'][type_int], list):
                                    for i in data_set['interfaces'][type_int]:
                                        try:
                                            int_list.append(i['interface'])
                                        except:
                                            continue
                                else:
                                    continue
                        for y in int_list:
                            if "." in y:
                                execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), "sudo modprobe 8021q")
                                time.sleep(0.02)
                                execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), f"sudo ip link add link {y.split('.')[0]} name {y} type vlan id {y.split('.')[1]}")
                                time.sleep(0.02)
                                execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), f"sudo ip link set dev {y} up")
                    else:
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
                        st.write(':orange[Start traffic generating ...]')
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
                        st.write(':orange[Put config.json ...]')
                        put_sc, put_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'PUT', json.dumps(put_body, indent=2))
                        put_pg = st.progress(0)
                        for percent_complete1 in range(100):
                            time.sleep(0.01)
                            put_pg.progress(percent_complete1 + 1, text= f':violet[{percent_complete1+1}%]')
                        ######## Start trafffic ##############################
                        st.write(':orange[Start traffic generating ...]')
                        start_sc, start_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_start, '/_start')
                        # st.write(start_sc, start_ct)
                        run_pg = st.progress(0)
                        for percent_complete2 in range(100):
                            time.sleep(0.01)
                            run_pg.progress(percent_complete2 + 1, text= f':violet[{percent_complete2+1}%]')
                        if put_sc == 201:
                            print('Create instance on blaster sucessfully')
                        else: 
                            print('Create instance on blaster didnt sucessfully')
                    st.session_state.button_stop= False
                    log_authorize(st.session_state.user,blaster_server['ip'], f'RUN START instance {instance}')
                    time.sleep(1)
                    st.rerun()
                # with st.container(border= True):
                if st.button('**STOP** :material/stop_circle:', type= 'primary', use_container_width=True, disabled= st.session_state.button_stop):
                    stop_sc, stop_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_stop, '/_stop')
                    # st.write(stop_sc, stop_ct)
                    st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
                    log_authorize(st.session_state.user,blaster_server['ip'], f'RUN STOP instance {instance}')
                    
                    stop_pg = st.progress(0)
                    for percent_complete3 in range(100):
                        time.sleep(0.04)
                        stop_pg.progress(percent_complete3 + 1, text= f':violet[{percent_complete3+1}%]')
                    st.info(":green[Stop successfully]", icon="🔥")
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
            instance_report = st.selectbox(':orange[Select your instance for reporting]', list_instance_avail_from_blaster)
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
