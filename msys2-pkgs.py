from bs4 import BeautifulSoup
import requests
import subprocess
import os

index_url = 'https://repo.msys2.org/msys/x86_64/'

to_process = set(["git", "automake-wrapper", "make", "sed", "libtool", "autoconf",
    "findutils", "m4", "bash", "texinfo", "p7zip", "curl", "base", "tar", "zip",
    "unzip", "diffutils", "patch", "patchutils"])

provides = {"sh": "bash", "libuuid": "libutil-linux", "awk": "gawk",
        "perl-IO-stringy": "perl-IO-Stringy"}

seen = {}

def get_pkgs():
    directory_listing = requests.get(index_url).text
    s = BeautifulSoup(directory_listing, 'html.parser')
    full_names = [node.get('href') for node in s.find_all('a') if node.get('href').endswith((".tar.zst", "tar.xz"))]
    # format: msy2-w32api-headers-10.0.0.r16.g49a56d453-1-x86_64.pkg.tar.zst
    return list(sorted([("-".join(pkg.split('-')[:-3]), "-".join(pkg.split('-')[-3:])) for pkg in full_names]))

pkg_latest_ver = dict(get_pkgs())
# for pkg, info in pkg_latest_ver.items():
#    print(pkg, info)

def get_depends(pkg):
    info = pkg_latest_ver[pkg]
    basename = f"cache/{pkg}-{info}"
    url = f"{index_url}/{pkg}-{info}"
    if not os.path.exists(basename):
        subprocess.check_call(["wget", url, "-O", basename])
    subprocess.check_call(["mkdir", "-p", "cache/tmp"])
    subprocess.check_call(["tar", "-xf", basename, "--directory=cache/tmp"])
    with open("cache/tmp/.PKGINFO") as f:
        depends = [line[len("depend = "):].strip() for line in f.readlines() if line.startswith("depend = ")]
    depends = [dep for dep in depends if not dep.startswith("pacman")]
    return depends

while to_process:
    pkg = to_process.pop()
    depends = get_depends(pkg)
    for full_dep in depends:
        dep = full_dep.split(">")[0].split("=")[0].split("<")[0]
        dep = provides.get(dep, dep)
        if dep not in seen:
            to_process.add(dep)
    seen[pkg] = depends

for pkg, depends in seen.items():
    print(f"{pkg} {pkg_latest_ver[pkg]} {' '.join(depends)}")
