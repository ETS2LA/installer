import os
try:
    import requests
except:
    import os
    os.system("pip install requests")
    import requests


GIT_URL = "https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe"

def show_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    if iteration == total:
        print()

# Download Node.js
print("Downloading Git...")
data = requests.get(GIT_URL, stream=True)
total_length = int(data.headers.get('content-length'))
with open("Git-2.45.2-64-bit.exe", "wb") as file:
    chunk_size = 1024
    chunk_count = 0
    for data_chunk in data.iter_content(chunk_size=chunk_size):
        chunk_count += 1
        file.write(data_chunk)
        show_progress_bar(chunk_count, total_length / chunk_size, length=50)

print("Git downloaded!")

# Run the installer
print("Running the installer...")
os.system("Git-2.45.2-64-bit.exe /SILENT")
# Remove the installer
os.remove("Git-2.45.2-64-bit.exe")
print("Git installed and installer removed!")