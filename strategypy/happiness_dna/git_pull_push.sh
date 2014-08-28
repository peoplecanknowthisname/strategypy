#!/bin/sh

while [ 1 ]; do
	git add gen*
	git commit -m "updating dna history"
	git pull --ff-only
	git push
	sleep 60
done
