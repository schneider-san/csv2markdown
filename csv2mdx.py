#! /usr/bin/env python3
# coding:utf-8

"""
DISCLAIMER
  This script is an extract from a proprietary software [redacted]. With permission, I am 
  making it publicly available. 

DESCRIPTION
  Given a table in a csv file with numerous entries, a user wishes to populate each row into
  a markdown file .mdx, using a predefined template with keywords that match columns in the
  csv table.

PROBLEM STATEMENT
  Write a program or script that can achieve the above description. If any, submit
  observations, improvement suggestions or limitations of this program or script.

REQUIREMENTS
  - The script is expected to iterate through the csv file and create markdown files using
    the predefined template file.
  - The file name of each markdown file must be the value of its primary key in the csv file.
  - Retain previous copy (single or multiple) of generated markdown files in the case of
    file exist conflicts.

CONSTRAINTS
  - Use python inbuilt modules only !

SAMPLES
  - csvsample.csv (contains little data, but can be used to show working implementation of
                  the program or script).
  - template.mdx

"""

from csv import reader as creader
from sys import argv
from os import sep, getcwd, makedirs
from os.path import abspath, isfile, isdir
from time import sleep, time, ctime
from shutil import copyfile

# a dictionary of all process statuses
alerts = {
    "error":"An error occurred. See more => {}",
    "inputError":"\n[!] Input parameters not satisfied.\n[~] See usage:\n\tpython3 csv2md.py -c \"[filename | fullpath_to_csvFile]\" -t \"[filename | fullpath_to_templateFile]\"\n[!] Double quote \"\" input parameters containing spaces.",
    "warning":"[!] Existing file {} will before overwritten. CTRL+C to terminate all processes.",
    "info":"[+] Saving new file {} ...",
    "info2":"[+] Saved new file {} to disk.",
    "info3":"[+] Creating backup of existing file {}. CTRL+C to terminate all processes.",
    "success":"[+] Process Completed Successfully.\n[ Finished in {}s ]\n"
}

# lambda process time function
ptime = lambda: ctime(time()).split(" ")[3]

# construct log filename
logname = ctime(time()).split(" ")
logname = f"{logname[1]}_{logname[2]}_{logname[-1]}"

# create existing file backups folder
BACKUP = getcwd()+sep+'$backups'+sep+logname+sep
if not isdir(BACKUP):
    makedirs(BACKUP)

def log(ptime, text):
    """ process logger function """
    with open(logname+'_csv2mdx.log', 'a+') as logf:
        logf.write(f"[ {ptime} ] | {text}\n")
    print(f"[ {ptime} ] | {text}")

def mdx_writer(filename, contents):
    try:
        # construct filename and path to file on disk
        filename = filename+".mdx"
        fullfilepath = getcwd()+sep+filename

        # create backup of file if it exists
        if isfile(fullfilepath):
            # notify on existing file backup give time to cancel
            log(ptime(),alerts['info3'].format(filename))
            sleep(2.5)
            copyfile(fullfilepath, BACKUP+filename+".bak")
            
            # warn on existing file overwrite and give time to cancel
            log(ptime(),alerts['warning'].format(filename))
            sleep(2.5)

        # write new file to disk
        log(ptime(),alerts['info'].format(filename))

        with open(filename, "wb") as writer:
            writer.write(contents.encode('utf-8'))
        writer.close()
        
        log(ptime(),alerts['info2'].format(abspath(filename)))
        
        return True
    except Exception as e: return e

def create_mdx(table):
    # Create fallback copy of structured csv and template File
    table_copy, mdx_copy = table

    # Create File Writer Error container
    ERROR = ""

    # Map table to template for each key in table
    for key in table_copy:
        mapper = table_copy[key]
        # Create copy of template container
        tmp = mdx_copy
        for item in mapper:
            tmpItem = "csv-column-"+item
            if ("pci-321" in item):
                tmpItem = "pci-321"
            if ("analyst-followup" in item):
                tmpItem = "csv-column-cis-anal"
            tmp = tmp.replace(tmpItem, mapper[item].strip())

        # Write new file to disk
        done = mdx_writer(key, tmp)
        if done:
            continue
        else:
            ERROR = f"Template Writer ERRORS\n\nError with Key => {key}\n{done}\n\n"

def get_csv(csvFile, templateFile):
    # Get required files
    csvFile = csvFile

    # Get contents of CSV file
    with open(csvFile, newline="", encoding='utf-8') as readF:
        csv = creader(readF, delimiter=',', quotechar='"')
        csv = [i for i in csv]

    # Get contents of Template file
    with open(templateFile, "r") as readF:
        mdx = readF.read()
        readF.close()

    # Create dictionary from csv
    CSV_DICT = {}
    columns = csv[0]
    rows = csv[1:]
    for row in range(len(rows)):
        row = rows[row]
        tm = {}
        for col in range(len(columns)):
            tm[columns[col]] = row[col]
        CSV_DICT[tm['key']] = tm
    return CSV_DICT, mdx


if __name__ == '__main__':
    st = time()
    try:
        csvFile = argv[argv.index('-c')+1]
        templateFile = argv[argv.index('-t')+1]
        try:
            log(ptime(),f"[+] Program Starting In Directory: {getcwd()}")
            for i in (csvFile, templateFile):
                assert(i)
            done = create_mdx(get_csv(csvFile, templateFile))
            try:
                if 'ERRORS' in done:
                    log(ptime(),"Errors during template writer process saved to ./writerLogs.log\n")
            except TypeError: log(ptime(),alerts['success'].format(round((time()-st), 2)))
        except AssertionError: log(ptime(),alerts["inputError"])
    except ValueError:
        print(alerts["inputError"])
    except IndexError:
        print(alerts["inputError"])
    except KeyboardInterrupt: log(ptime(),"[!] Terminating Program"); sleep(1); log(ptime(),"[~] Program terminated\n");print("[ + Finished in {}s + ]".format(round((time()-st), 2)))

