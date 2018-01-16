#!/usr/bin/python
#
# Reads and writes to contactlist in Motorola Tetra terminals
#
# 2016 Jon-Harald Brathen
#
import time
import csv
import argparse
import sys
import serial


parser = argparse.ArgumentParser(description='Reads and writes to contactlist in Motorola Tetra terminals')

parser.add_argument('operation', help="read, write, delete")

parser.add_argument('--file', help='Filename with contacts in CSV format')
parser.add_argument('--port', help='serialport e.g. /dev/cu.usbserial')

args = parser.parse_args()


def comment_stripper(iterator):
    """Rremoving blank lines and lines starting with # for comment"""
    for line in iterator:
        if line[:1] == '#':
            continue
        if not line.strip():
            continue
        yield line


def read_contacts(filename):
    """Reading contact using GSM AT command"""
    if not isinstance(filename, basestring):
        print "Error: filename missing\n"
        parser.print_help()

    try:
        file_pointer = open(filename, 'w')
    
    except:
        print("Error: Could not open file " + filename + " for writing")
        sys.exit(1)


    trimmed = ""

    with serial.Serial(args.port, 38400, timeout=4) as ser:
        ser.write('at+cscs=8859-1\n\r')
        time.sleep(0.2)
        ser.write(b'at+cpbr=1,100\n\r')
        result = ser.read(2000000)
        trimmed = result[result.find('+CPBR:')+7:-8]
        ser.close()

    for line in trimmed.splitlines():
        file_pointer.write(line + '\n')

    print "Contacts imported til file"

def write_contacts(filename):
    if not isinstance(filename, basestring):
        print("Error: filename missing\n")
        parser.print_help()
        sys.exit(1)

    try:
        fp = open(filename, 'r')
    except:
        print("Error: Could not open file " + filename + " for reading")
        sys.exit(1)
 
    lines = comment_stripper(fp.readlines())
   
    with serial.Serial(args.port, 38400, timeout=1) as ser:
        ser.write('at+cscs=8859-1\n\r')
        time.sleep(0.2)
        for line in lines:
            contact = line[:-1].split(',')
            print "Transfering to terminal: " + line
            ser.write('at+cpbw=' + contact[0] + ',' + contact[1] + ',' + contact[2] + ',' + contact[3] + '\n\r')
            time.sleep(0.1)
            #ser.write(b'at+cpbw=1,100\n\r')
        result = ser.read(1000000)

        if result.count('ERROR') != 0:
            print str(result.count('ERROR')) + " contacts failed"
        print str(result.count('OK')) + " contacts successfully transferred"
        ser.close()

    
def delete_contacts():
    with serial.Serial(args.port, 38400, timeout=1) as ser:
        for num in range(1,300):
            ser.write('at+cpbw=' + str(num) + '\n\r')
            time.sleep(0.1)
            print "Deleting contact " + str(num)
            #print ser.readline()

        ser.close()
    
if args.operation == "read":
    read_contacts(args.file)

elif args.operation == "write":
    write_contacts(args.file)

elif args.operation == "delete":
    delete_contacts()

else:
    parser.print_help()

