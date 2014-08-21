
# coding: utf-8

# In[3]:

##
## Create HathiTrust Annual Reports of Physical Titles
## J Ammmerman
## August, 2014
## v. 1.0
##
## 

## Import required libraries
import time
from datetime import datetime
tstart = datetime.now()
from pymarc import Field, Record, MARCWriter, MARCReader
import marcx
import sys  
reload(sys)  
import glob

## define some functions:
##
def tsv_row(self):
    row = ''
    for col in self.itervalues():
        if type(col) != 'str':
            row += ''
        else:
            row += col
        row += '\t'
    row = row[:-1] + '\n'
    return row

## set variables
sys.setdefaultencoding('utf8')
error_loc = []
oclc_dict = {}
oclc_dict['digit'] = 0
oclc_dict['(OCoLC)'] = 0
oclc_dict['ocm'] = 0
oclc_dict['ocn'] = 0
oclc_dict['other'] = 0
cleanup_dict = {}
errorcount = 0
rec_count = 0
ser_count = 0
mpm_count = 0
spm_count = 0
is_serial = False
is_mpm = False
##
## open files for output
##
spm_file = open('spm.tsv', 'wb') 
mpm_file = open('mpm.tsv', 'wb')
ser_file = open('serials.tsv', 'wb')
digit_file = open('digit.tsv', 'wb')
##
## create a list of files with *.mrc endings
##
flist = glob.glob('*.mrc')
for f in flist:
    print f
    print 'Record Count: ', str(rec_count)
    print 'Error Count: ', str(errorcount)
    print 'Serials Count: ', str(ser_count)
    print 'MPM Count: ', str(mpm_count)
    print 'SPM Count: ', str(spm_count)
    print 'Not OCLC: ', str(oclc_dict['other'])
    marc_records = []
    with open(f) as marc_file:

        #print marc_file
        marc_reader = MARCReader(marc_file)
        try:
            for rec in marc_reader:
                rec_count += 1
                marc_records.append(rec)
        except:
            error_loc.append(f + ' - ' + str(rec_count))
            errorcount += 1
    rec_dict = {}   
    for i, rec in enumerate(marc_records[0:len(marc_records) ]):
        
        ## 
        ## exclude Microforms for HathiTrust
        ##
        try: 
            micro = rec['007'].data
            match = (micro[0] == 'h')
            if match:
                continue
        except (TypeError, AttributeError, ValueError) as e :
            pass
        
        ##
        ## reset values for rec_dict 
        ##
        x = 0
        while x < 7:
            rec_dict[x] = ''
            x += 1
        ##
        ## grab the value of 035
        #
        _035 = ''
        try:
            _035 = rec['035']['a']

        except (TypeError, AttributeError, ValueError) as e :
            pass
        

        ##
        ## We have a value in _035. Check to see if it is an OCLC system number
        try:
            att_test = _035.isdigit()
        except (TypeError, AttributeError, ValueError) as e :
            continue
           
        if _035.isdigit():
            rec_dict[0] = '(OCoLC)' + _035
            oclc_dict['digit'] += 1
            digit_file.write(rec['001'].data + '\n')
        elif _035[0:7] == '(OCoLC)':
            rec_dict[0] = _035
            oclc_dict['(OCoLC)'] += 1
        else:
            # it isn't, so increment counters and loop
            oclc_dict['other'] += 1
            cleanup_dict[rec['001'].value()] = _035
            continue
        ## MMS ID from Alma
        rec_dict[1] = rec['001'].data
        ## Current Holding
        rec_dict[2] = 'CH'
        ## No value for condition
        rec_dict[3] = ''
        ##
        ## check to see if the record is for a multi part monograph
        ##
        try:
            pos = rec['300']['a'].index('v.')
            if pos > 0:
                rec_dict[4] = rec['300']['a'][0:pos+2]
            else:
                rec_dict[4] = 'v.'
            mpm_count += 1
            is_mpm = True
        except (TypeError, AttributeError, ValueError) as e :
            is_mpm = False
        ##
        ## Check to see if this is a serial
        ##
        try:
            leader = rec.leader
            if leader[7] == 's' or leader[7] == 'i':
                is_serial = True
                #rec_dict[4] = ser_holdings(rec)
                ser_count += 1
            else:
                is_serial = False
        except (TypeError, AttributeError, ValueError) as e :
            is_serial = False
        ##
        ## we have a single part monograph
        ##
        if (is_mpm is False and is_serial is False):
            spm_count += 1
            is_spm = True
        else:
            is_spm = False
            
        ##
        ## if is_serial, check for an ISSN and add to red_dict[5]
        ##
        if is_serial:
            ## serial holdings
            rec_dict[5] = '         '
            try:
                if (type(rec['866']['a']) == 'str') :
                    rec_dict[4] = rec['866']['a']
            except (TypeError, AttributeError, ValueError) as e :
                rec_dict[4] = ''
                pass
            ## issn
            try: 
                rec_dict[5] = rec['022']['a'] 
            except (TypeError, AttributeError, ValueError) as e :
                rec_dict[5] = ''
                pass
        ##
        ## check to see if this is a government document
        ##
        try: 
            govdoc = rec['008'].data
            if len(govdoc) > 29:
                match = (govdoc[28] == 'f')
            else:
                match = False
                
            if match:
                rec_dict[6] = '1'
            else:
                rec_dict[6] = '0'   
        except (TypeError, AttributeError, ValueError) as e :
            rec_dict[6] = '0'
            
        ## prepare to output the record
        #print rec_dict
        ##print tsv_row(rec_dict)
        row = ''
        for col in rec_dict.itervalues():
            #if type(col) == 'str':
            try:
                row += col
            except (TypeError, AttributeError, ValueError) as e :
                row += ''
            row += '\t'
        row = row[:-1] + '\n'
        #print row
        if is_serial:
            ser_file.write(row)
        if is_mpm:
            mpm_file.write(row)
        if is_spm:
            spm_file.write(row)


ser_file.close()
mpm_file.close()
spm_file.close()
digit_file.close()

tend = datetime.now()
duration = tend - tstart
##
## final report of counts
print ' '
print '+++++++++++++++++++++++'
print ' '
print ' Final Counts'
print 'Record Count: ', str(rec_count)
print 'Error Count: ', str(errorcount)
print 'Serials Count: ', str(ser_count)
print 'MPM Count: ', str(mpm_count)
print 'SPM Count: ', str(spm_count)
print 'Not OCLC: ', str(oclc_dict['other'])
print ' '
print 'Time: ' , str(duration.seconds) , 'seconds'

            

            
        


# In[4]:

oclc_dict


# In[ ]:



