#!/bin/sh
#
# Run 'mkdocs serve' on port 8000 (default)

# Make sure that this is being run from the build-util folder
pwd=`pwd`
dirname=`basename ${pwd}`
if [ ! ${dirname} = "build-util" ]
	then
	echo "Must run from build-util folder"
	exit 1
fi

cd ..

echo "View the website using http://localhost:8000"
echo "Kill the server with CTRL-C"
#mkdocs serve -a 0.0.0.0:8000
mkdocs serve
