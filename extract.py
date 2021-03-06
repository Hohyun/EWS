
import sys, getopt, os, re, subprocess, csv
import pymongo

DATADIR = ""
# DATAFILE = "mir.txt"
DATAFILE = 'Management_Information_Report_Agent_Sales_2015-03-23-13.txt'
OUTFILE = "mir_extracted.txt"
CSVFILE = "mir_extracted.csv"
#EWS_DATA = '27303054 BUKHARI TRAVEL SERVICES (PVT) LTD HO W 968,156.00 Insurance Bond 205.25% 38,726.24 122.28%'
#EWS_DATA = '91209311 HAYS TRANSPORT LTD HO W 3,499,769.95 N/A 83,327.81 201.74%'
#EWS_DATA = '35308431 EXPEDIA (THAILAND) LIMITED HO W 1,382,034.99 * * 115,169.58 105.61%'

# 06200950 KNEISSL TOURISTIK GMBH HO W 746,409.31
# Statement Of
# Assignment
# 101.00% 37,320.47 116.83%

# 14341294 AADESH TRAVELS PVT. LTD. HO F 868,473.06
# Bank Guarantee,
# Insurance Bond
# 181.77% 62,033.79 106.59%


class Mir():
    '''
    This class is for the extraction information from IATA BSP Management Information Report
    '''

    def __init__(self, src_file, dst_file):
        self.src = src_file
        self.dst = dst_file
        self.parsed_data = []
        self.extracted_data = ''

    def parse_file (self):
        page = 1
        ews_sq = 0
        flag = False

        with open(self.src, "r") as f:
            data = ''
            dataFound = False

            for line in f:
                if flag == True:
                    match = re.search('^\d{8}', line)
                    if match:
                        # multi_flag = True
                        dataFound = True
                        data += line.strip()
                        if data[-1] == '%' or data[-3:] == 'N/A':
                            self.parsed_data.append(data)
                            dataFound = False
                            data = ''
                    elif dataFound == True:
                        data += ' {0}'.format(line.strip())
                        if data[-1] == '%' or data[-3:] == 'N/A':
                            self.parsed_data.append(data)
                            dataFound = False
                            data = ''

                match = re.search('Page\s\d+\sof\s\d+$', line)
                if match:
                    #print match.group(0)
                    page += 1
                    if flag == True:
                        flag = False

                match = re.search('^.*\d\d-[A-Z][a-z][a-z]-\d\d\d\d$', line)
                if match:
                    flag = True
                    if (ews_sq % 2) == 0:
                        self.parsed_data.append(line.strip())
                    ews_sq += 1

    def parse_bsps(self):
        filtered_bsp = []
        with open(self.src, "r") as f:
            for line in f:
                match = re.search('^~(.*\([A-Z][A-Z]\))$', line)
                if match:
                    #print match.group(0)
                    filtered_bsp.append(match.group(1).strip())
        return filtered_bsp

    def parse_pages(self):
        page = 1
        pages_to_be_extracted = []

        with open(self.src, "r") as f:
            for line in f:

                match = re.search('Page\s\d+\sof\s\d+$', line)
                if match:
                    page += 1

                match = re.search('^.*\d\d-[A-Z][a-z][a-z]-\d\d\d\d$', line)
                if match:
                    pages_to_be_extracted.append(page)

        print pages_to_be_extracted
        return pages_to_be_extracted

    def parse_security_info(self, EWS_DATA):
        info = {}
        m = re.search('^(\d{8})\s(.*)\s(HO|AO)\s([WTFSDMR])\s(.*)',EWS_DATA)
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

    def format_ews_info(self):
        filtered_bsp = self.parse_bsps()
        for bsp in filtered_bsp:
            self.extracted_data += "- %s\n" % bsp

        header =    "%-8s %-39s %-4s %-4s %14s %-19s %12s %14s %10s" % \
                 ('Head', '', 'Loc', '', 'Sales to be', 'Security', 'Security', 'Daily', 'Sales')
        header += "\n%-8s %-39s %-4s %-4s %14s %-19s %12s %14s %10s" % \
                 ('Office', 'Legal Name', 'Type', 'Frq.', 'Remitted', 'Type', 'Utilized(%)', 'Cash Avg', 'Variation')
        uline = "-------- --------------------------------------- ---- ---- -------------- "
        uline += "------------------- ------------ -------------- ----------"

        for line in self.parsed_data:
            match = re.search('^\d{8}', line)
            if match:
                print line
                info = self.parse_security_info(line)

                data = "%-8s %-39s %-4s %-4s %14s %-19s %12s %14s %10s" % \
                       (info['iata_no'], info['agt_name'][0:39], info['location_type'], \
                        info['frequency'], info['amt_to_be_remitted'], info['security_type'][0:19], \
                        info['security_utilized'], info['daily_cash_avg'], info['sales_variation'])
                #print data
                self.extracted_data += "%s\n" % data
            else:
                s = line.split('Period:')
                self.extracted_data += "\n\n%s\n%s\n%s\n%s\n" % (s[0].strip(), s[1].strip(), header, uline)

        # print self.extracted_data

    def export_to_csv(self):
        conn = pymongo.MongoClient("mongodb://localhost")
        db = conn.ews
        coll = db.mdm

        bsp = ''
        with open(CSVFILE, 'wb') as csv_file:
            w = csv.writer(csv_file)
            # header
            w.writerow(['Branch', 'BSP', 'IATA No', 'AGT Name', 'LOC Type', 'Freq.', 'AMT to be Remitted',
                        'Security Type', 'Security Utilized(%)', 'Daily Cash Avg', 'Sales Variation'])
            for line in self.parsed_data:
                match = re.search('^\d{8}', line)
                if match:
                    info = self.parse_security_info(line)
                    doc = coll.find_one({'iata_no' : info['iata_no']})
                    if doc:
                        branch = doc['branch'.encode('utf-8')]
                    else:
                        branch = ""

                    w.writerow([branch, bsp, info['iata_no'], info['agt_name'], info['location_type'], \
                        info['frequency'], info['amt_to_be_remitted'], info['security_type'], \
                        info['security_utilized'], info['daily_cash_avg'], info['sales_variation']])
                else:
                    s = line.split('Period:')
                    bsp = s[0].strip()
        
        print "Extraction completed ... {0} is created.".format(CSVFILE)


    def save_file(self):
        f = open(self.dst, 'w')
        report_header = """
[ IATA BSP Management Information Report ]

Reporting Criteria
* Agents with an average monthly sales for the last 12 months of 500,000.00 USD and above; that 100% or more sales variation.
* All amounts in this Report have been converted to USD using IATA 5 days exchange rate.

Definitions
* Head Office: Agent IATA code
* Legal Name: Agent Legal Name
* Loc Type: Agent Location Type (HO-Head Office, AO-Administrative Office)
* Frq: Remittance Frequency (W-Weekly, T-Twice a Week, S-Super Weekly, F-Fortnightly, D-Every 10 days, M-Monthly)
* Sales to be Remitted: Total Reported Sales(NET) in the report period that are not yet due for remittance.
* Security Utilized(%): The percentage of Financial Security used compared to sales to be remitted.
* Daily Cash Avg: The ratio between Daily Net Cash Sales(cumulated) until the date of this report and the number of days in the reported period.
* Sales Variation: The Daily Cash Average in the current period as compared to the Average Daily Cash sales in the last 12 months.

List of BSP Countries for which Agents meet the filtering criteria
"""
        f.write(report_header)
        f.write(self.extracted_data)
        f.close()
        print "Extraction completed ... {0} is created.".format(OUTFILE)

    def make_pdf(self, src_pdf):
        page_list = self.parse_pages()
        pages = ''
        for p in page_list:
            pages += str(p) + ','
        pages = pages[0:-1]  # remove last comma

        tex_src = """\documentclass[landscape]{article}
\usepackage[pdftex]{graphicx}
\usepackage{pdfpages}
\\begin{document}
\includepdf[pages={%s}]{%s}
\end{document}
""" % (pages, src_pdf)

        fn = os.path.join(DATADIR, "mir_extracted.tex")
        f = open(fn , 'w')
        f.write(tex_src)
        f.close()
        subprocess.call(["pdflatex", "--interaction=batchmode", fn])
        #subprocess.call(["rm", "*.aux"])
        #subprocess.call(["rm", "*.log"])

def check_args():
    usage = 'Usage: python extract.py source_file.txt'
    opts, args = getopt.getopt(sys.argv[1:], "h", "help")
    for o, a in opts:
        if o == '-h' or o == '--help':
            print usage
            sys.exit(0)

    if len(sys.argv) == 1:
        print usage
        sys.exit(0)


def main():
    check_args()
    # inputFile = os.path.join(DATADIR, DATAFILE)
    outputFile = os.path.join(DATADIR, OUTFILE)
    # mir = Mir(inputFile, outputFile)
    mir = Mir(sys.argv[1], outputFile)   
    mir.parse_file()
    mir.format_ews_info()
    # export to csv file
    mir.export_to_csv()
    # txt file save
    mir.save_file()
    # mir.make_pdf("mir.pdf")

if __name__ == '__main__':
    main()

