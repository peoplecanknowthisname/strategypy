#!/bin/sh

while [ 1 ]; do
	git add gen*
	git commit -m "updating dna history"
	git push
	git pull
	sleep 60
done
