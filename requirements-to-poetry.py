import subprocess

with open('requirements.txt', 'r') as f:
    packages = f.read().splitlines()

for package in packages:
    subprocess.check_call(['poetry', 'add', package])