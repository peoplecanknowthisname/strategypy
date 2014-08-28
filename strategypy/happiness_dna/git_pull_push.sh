#!/bin/sh

while [ 1 ]; do
	git add gen*
	git commit -m "updating dna history"
	git fetch
	git rebase origin/happiness_evo
	git push
	sleep 60
done
