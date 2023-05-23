# Batch-Shutterstock-Download-Utility
Python script to batch download images from Shutterstock from a list using browser automation.

Dependencies:

csv, time, datetime, argparse, logging, pathlib, playwright

To Run at Command Line:

python Bulk-Download-Images-from-Shutterstock.py <SHUTTERSTOCK_UID> <SHUTTERSTOCK_PASSWORD> <PATH_TO_INPUT_CSV> <PATH_TO_DOWLOAD_FOLDER>

To See Help:

python Bulk-Download-Images-from-Shutterstock.py -h

The input should be a CSV file, one column, with the header "description" and each phrase to search on Shutterstock.com listed below that. Example:

description

Acer freemanii

Acer palmatum var. atropurpureum

Acer palmatum var. dissectum

Agapanthus africanus

Agapanthus hybrid

Agapanthus orientalis

Agave stricta

Aglaonema nitidum

Apocynum lancifolium

Apocynum pictum

Apocynum venetum
