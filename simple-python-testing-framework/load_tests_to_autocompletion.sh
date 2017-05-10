#! /bin/bash

FILES="`ls /<full-path>/tests/*.py`"
TESTS="`grep -o -P '(?<=class ).*(?=\(TestBase\):)' ${FILES} | cut -d':' -f2`"

function tests {
	python /<full-path>/tests_runner.py -t $*
}

complete -W "${TESTS}" tests
