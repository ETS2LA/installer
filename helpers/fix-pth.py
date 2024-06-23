lines = []
with open("python/python311._pth") as f:
    lines = f.readlines()
    lines = [l for l in lines if not l.startswith("import")]

with open("python/python311._pth", "w") as f:
    for line in lines:
        if line == "#import site\n" or line == "#import site":
            f.write("import site\n")
        else:
            f.write(line)