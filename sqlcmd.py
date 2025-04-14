# import subprocess
#
# def is_sqlcmd_installed():
#     try:
#         result = subprocess.run(["sqlcmd", "-?"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         return result.returncode == 0 or b"usage" in result.stdout.lower()
#     except FileNotFoundError:
#         return False
#
# if is_sqlcmd_installed():
#     print("sqlcmd is installed.")
# else:
#     print("sqlcmd is NOT installed.")


import os

def is_c_sht_tools_in_path():
    target = os.path.normcase(r"C:\SHT\Tools")
    path_env = os.environ.get("PATH", "")
    paths = [os.path.normcase(p.strip('"')) for p in path_env.split(os.pathsep)]
    return target in paths

if is_c_sht_tools_in_path():
    print(r'"C:\SHT\Tools" is in the PATH.')
else:
    print(r'"C:\SHT\Tools" is NOT in the PATH.')
