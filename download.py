import file_names as files
import paramiko
import time
import socket
import getpass
import os

failed_downloads = []
fail = open('failed_downloads_LOG.txt','a')
success = open('successful_downloads_LOG.txt','w')

# Starting time
start_time = time.time()
# Local directory
local_dir = os.getcwd()

# Connect to the server
# host, port, user, password = ('host', 22, 'user', 'pass')
host, port = ('host', 22)

#Log file
paramiko.util.log_to_file('download_log.txt')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()

try:
	user = input("Username: ")
	# password = input("Password:")
	password = getpass.getpass("Password: ")
	
	ssh.connect(host, port=port, username=user, password=password)
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls')
	sftp = ssh.open_sftp()
except paramiko.BadHostKeyException as badHostKeyException:
	print("Unable to verify server's host key: %s" % badHostKeyException)
except paramiko.AuthenticationException as auth:
	print("Authentication failed, please verify your credentials: %s" % auth)
except paramiko.SSHException as sshException:
	print("Unable to establish SSH connection: %s" % sshException)
except Exception as e:
	print("Operation error: %s" % e)


report_number = int(input("Which csv's you want to download? MAKRO or Suppliers? Enter: (1) for MAKRO, (2) for Suppliers, (3) Quarterly \n"))
if report_number == 1:
	report_kind = files.MAKRO
elif report_number == 2:
	report_kind = files.SUPPLIERS
elif report_number == 3:
	report_kind = files.QUARTERLY

def download(kind_of_reports):
	for x in range(0,len(kind_of_reports)):
		try:
			ensure_dir(kind_of_reports[x][2])
			sftp.get(kind_of_reports[x][0], kind_of_reports[x][1])	# Downloading files
			print('Downloaded: ' + str(kind_of_reports[x][1])),		# Print downloaded file name
			success.write('[' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) + '] ' + kind_of_reports[x][1] + '\n') # Write succeeded download LOG
		except:
			# print(str(kind_of_reports[x][1]) + " can't be downloaded"),
			failed_downloads.append(kind_of_reports[x][1])
			fail.write('[' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) + '] ' + kind_of_reports[x][1] + '\n') # Write failed download LOG
	end_time = time.time()

def ensure_dir(file_path):
    # folder_name = os.path.dirname(file_path)
    directory = os.path.join(local_dir, file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

download(report_kind)
fail.write('-------------------------------------------------------------------------------------- \n')

success.close()
fail.close()
sftp.close()
ssh.close()

# Overal time
overal_time = end_time - start_time
minutes = int(overal_time / 60)
seconds = overal_time - (minutes*60)
# print("\n --- %.2f seconds ---" % (time.time() - start_time))
print("--- " + minutes + " min " + seconds + " seconds ---")

if len(failed_downloads) > 0:
	print(str(len(failed_downloads))  + ' files were not downloaded:')
	for x in range(0,len(failed_downloads)):
		print(failed_downloads[x]),