import os
import subprocess
import shutil
import time

import psutil

def remove_files(files_to_remove):
    ind = 1
    print("The following files can be removed:")
    for file in files_to_remove:
        print(f'{ind}. {file}')
        ind += 1
    user_input = input("What files should be deleted? Print 0, you want to remove all files, -1 if nothing should be deleted."
                       "In other case list indexes of files to be deleted and put commas between them.")
    user_input = user_input.replace(" ", "")
    files = user_input.split(',')
    if files[0] == '-1':
        return
    elif files[0] == '0':
        for index in range(len(files_to_remove)):
            try:
                if user_input.lower() == "y":
                    if os.path.isfile(files_to_remove[index]):
                        os.remove(files_to_remove[index])
                    elif os.path.isdir(files_to_remove[index]):
                        shutil.rmtree(files_to_remove[int(index)])
            except:
                print(f"Couldn't remove file {files_to_remove[index]}")
    else:
        for file in files:
           try:
               index = int(file) - 1
               if user_input.lower() == "y":
                  if os.path.isfile(files_to_remove[index]):
                      os.remove(files_to_remove[index])
                  elif os.path.isdir(files_to_remove[index]):
                      shutil.rmtree(files_to_remove[index])
           except:
               print(f"Couldn't remove file {files_to_remove[int(file) - 1]}")


def remove_junk():
    # Create a list of files to be removed
    files_to_remove = []
    # Add old kernels to the list
    output = subprocess.check_output(["sudo", "apt-get", "autoremove", "--dry-run", "-y"])
    for line in output.decode().split("\n"):
        if line.startswith("Removing") and "/boot" in line:
            files_to_remove.append(line.split()[-1])
    # Add unused packages to the list
    output = subprocess.check_output(["sudo", "apt-get", "clean", "--dry-run", "-y"])
    for line in output.decode().split("\n"):
        if line.startswith("Cleaning") and "/var/cache/apt/archives" in line:
            files_to_remove.append(line.split()[-1])
    # Add temporary files to the list
    files_to_remove.append("/tmp")
    remove_files(files_to_remove)


file_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".jpg", ".jpeg", ".png",
                       ".gif", ".mp3", ".mp4", ".avi", ".mov", ".zip", ".tar", ".gz"]


def is_old_file(path):
    """
            Returns True if the file at `path` has not been accessed within the
            threshold time, False otherwise.
            """
    try:
        access_time = os.path.getatime(path)
        file_info = os.stat(path)
        now = time.time()
        return (now - access_time) > 2592000 and path.endswith(tuple(file_extensions))
    except:
        return False

def remove_old_files(path):
    exclude_list = ['/var', '/usr', '/etc/passwd', '/etc/shadow', '/snap']

    deletable_files = []
    for root, dirs, files in os.walk(path):
        # Exclude directories or files in the exclude list
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_list]
        files[:] = [f for f in files if os.path.join(root, f) not in exclude_list]

        for name in files:
            file_path = os.path.join(root, name)
            if is_old_file(file_path):
                    deletable_files.append(file_path)
    remove_files(deletable_files)


def remove_malware():
    # Scan for malware
    output = subprocess.check_output(["sudo", "clamscan", "-r", "/", "--infected"], stderr=subprocess.DEVNULL)
    infected_files = output.decode().strip().split("\n")
    if infected_files:
        # Create a list of infected files to be removed
        files_to_remove = []
        for file in infected_files:
            files_to_remove.append(file.split()[-1])
        # Prompt the user to confirm the removal of each file
        for file in files_to_remove:
            print("The following infected file will be removed:", file)
            user_input = input("Do you want to remove it? (y/n) ")
            if user_input.lower() == "y":
                if os.path.isfile(file):
                    os.remove(file)
                elif os.path.isdir(file):
                    shutil.rmtree(file)
            else:
                print("File not removed.")

def tune_system():
    # Adjust CPU frequency
    subprocess.run(["sudo", "cpupower", "frequency-set", "-g", "performance"])

    # Optimize startup
    subprocess.run(["sudo", "systemctl", "disable", "app.service"])

    # Benchmark the system
    # ...

def monitor_system():
    # Monitor CPU usage
    print("CPU usage:", psutil.cpu_percent())

    # Monitor memory usage
    print("Memory usage:", psutil.virtual_memory().percent)

    # Monitor disk usage
    print("Disk usage:", psutil.disk_usage('/').percent)

    # Analyze system logs
    # ...

if __name__ == "__main__":
    remove_junk()
    remove_old_files('/')
    remove_malware()
    tune_system()
    monitor_system()