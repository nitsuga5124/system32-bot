from glob import glob
from os import name
from socket import socket
from socket import AF_INET, SOCK_DGRAM


def on_vps():
	sock = socket(AF_INET, SOCK_DGRAM)
	sock.connect(("8.8.8.8", 1))

	return sock.getsockname()[0] == "66.42.94.105"


def on_nt():
    return name == "nt"


def match_files(path):
    return [file.split("\\" if on_nt() else "/")[-1].split(".")[0] for file in glob(path)]