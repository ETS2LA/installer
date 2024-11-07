import os
try:
    import requests
except:
    import os
    os.system("pip install requests")
    import requests

NODE_URL = "https://nodejs.org/dist/v20.15.0/node-v20.15.0-x64.msi"

def show_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    if iteration == total:
        print()

# Download Node.js
print("Downloading Node.js...")
data = requests.get(NODE_URL, stream=True)
total_length = int(data.headers.get('content-length'))
with open("node-v20.15.0-x64.msi", "wb") as file:
    chunk_size = 1024
    chunk_count = 0
    for data_chunk in data.iter_content(chunk_size=chunk_size):
        chunk_count += 1
        file.write(data_chunk)
        show_progress_bar(chunk_count, total_length / chunk_size, length=50)

print("Node.js downloaded!")

# Run the installer
print("Running the installer...")
os.system("node-v20.15.0-x64.msi")
# Remove the installer
os.remove("node-v20.15.0-x64.msi")
print("Node.js installed and installer removed!")