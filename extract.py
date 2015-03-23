# Your task is to read the input DATAFILE line by line, and for the first 10 lines (not including the header)
# split each line on "," and then for each line, create a dictionary
# where the key is the header title of the field, and the value is the value of that field in the row.
# The function parse_file should return a list of dictionaries,
# each data line in the file being a single list entry.
# Field names and values should not contain extra whitespace, like spaces or newline characters.
# You can use the Python string method strip() to remove the extra whitespace.
# You have to parse only the first 10 data lines in this exercise,
# so the returned list should have 10 entries!
import os, re

DATADIR = ""
DATAFILE = "mir.txt"

def parse_file(datafile):
    data = []
    page = 1
    count = 0
    ews_pages = {}
    ews_sq = 0
    pages_to_be_extracted = []
    flag = False
    with open(datafile, "r") as f:
        for line in f:
            if flag == True:
                match = re.search('^\d{8}', line)
                if match:
                    print line.strip()

            match = re.search('Page\s\d+\sof\s\d+$', line)
            if match:
                #print match.group(0)
                page += 1
                if flag == True:
                    flag = False
            
            match = re.search('^~(.*\([A-Z][A-Z]\))$', line)
            if match:
                #print match.group(0)
                data.append(match.group(1).strip())
            
            match = re.search('^.*\d\d-[A-Z][a-z][a-z]-\d\d\d\d$', line)
            if match:
                flag = True
                pages_to_be_extracted.append(page)
                if (ews_sq % 2) == 0:
                    print line.strip()
                    ews_pages[data[ews_sq/2]] = page
                #print str(page) + match.group(0)
                ews_sq += 1

    print pages_to_be_extracted
    print data
    print ews_pages
    return data

#EWS_DATA = '27303054 BUKHARI TRAVEL SERVICES (PVT) LTD HO W 968,156.00 Insurance Bond 205.25% 38,726.24 122.28%'

#EWS_DATA = '91209311 HAYS TRANSPORT LTD HO W 3,499,769.95 N/A 83,327.81 201.74%'

EWS_DATA = '35308431 EXPEDIA (THAILAND) LIMITED HO W 1,382,034.99 * * 115,169.58 105.61%'

def parse_security_info(EWS_DATA):
    info = {}
    m = re.search('^(\d{8})\s(.*)\s(HO|AO)\s([WTFSDM])\s(.*)',EWS_DATA)
    temp = ''
    if m:
        info['iata_no'] = m.group(1)
        info['agt_name'] = m.group(2)
        info['location_type'] = m.group(3)
        info['frequency']  = m.group(4)
        temp = m.group(5).split(' ')
        cnt = len(temp)
        info['amt_to_be_remitted'] = temp[0]
        if cnt > 4:
            info['security_type'] = " ".join(temp[1:cnt-3])
        else:
            info['security_type'] = ""

        info['security_utilized'] = temp[cnt-3]
        info['daily_cash_avg'] = temp[cnt-2]
        info['sales_variation'] = temp[cnt-1]
    
    return info            



def main():
    #datafile = os.path.join(DATADIR, DATAFILE)
    #d = parse_file(datafile)
    info = parse_security_info(EWS_DATA)
    print info

if __name__ == '__main__':
    main()

######
# '91209311 HAYS TRANSPORT LTD HO W 3,499,769.95 N/A 83,327.81 201.74%'
# '27303054 BUKHARI TRAVEL SERVICES (PVT) LTD HO W 968,156.00 Insurance Bond 205.25% 38,726.24 122.28%'
# '35308431 EXPEDIA (THAILAND) LIMITED HO W 1,382,034.99 * * 115,169.58 105.61%'

# m = re.search('^(\d{8})\s(.*)\s(HO)\s(W)\s(.*)',d)

# iata_no = m.group(1)
# agt_name = m.group(2)
# HO = m.group(3)
# W  = m.group(4)
# temp = m.group(5)
# m = re.search('^([\d,\.]+)\s([A-Za-z\s]+)\s(.*)',temp)

