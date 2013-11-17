#!/usr/bin/env python2.7
from tasks import add

def main():
    add.delay(4, 3)

if __name__ == "__main__":
	main()
	exit (0)

