
"""
FILE: myParser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 10/16/2016 by Rao Zhang (zhangrao@stanford.edu)

Skeleton parser for CS145 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        tableSell = ""
        tableCategory = ""
        tableUser = ""
        tableCatItem = ""
        tableBid = ""
        tableItem = ""
        for item in items:

            ItemID = item[ "ItemID" ]

            sellUserID = item[ "Seller" ][ "UserID" ]
            sellUserID = "\"" + sellUserID.replace( "\"", "\"\"" ) + "\""

            sellUserRating = item[ "Seller" ][ "Rating" ]

            sellUserLocation = item[ "Location" ]
            sellUserLocation = "\"" + sellUserLocation.replace( "\"", "\"\"" ) + "\""

            sellUserCountry = item[ "Country" ]
            sellUserCountry = "\"" + sellUserCountry.replace( "\"", "\"\"" ) + "\""

            Name = item[ "Name" ]
            Name = "\"" + Name.replace( "\"", "\"\"" ) + "\""

            Started = transformDttm( item[ "Started" ] )
            Started = "\"" + Started.replace( "\"", "\"\"" ) + "\""

            Ends = transformDttm( item[ "Ends" ] )
            Ends = "\"" + Ends.replace( "\"", "\"\"" ) + "\""

            First_Bid = transformDollar( item[ "First_Bid" ] )
            Currently = transformDollar( item[ "Currently" ] )
            Number_of_Bids = item[ "Number_of_Bids" ]

            if "Buy_Price" in item:
                Buy_Price = transformDollar( item[ "Buy_Price" ] )
            else:
                Buy_Price = 'NULL'

            if None != item[ "Description" ]:
                Description = item[ "Description" ]
                Description = "\"" + Description.replace( "\"", "\"\"" ) + "\""
            else:
                Description = 'NULL'

            tableItem = tableItem + ItemID + columnSeparator + Name + columnSeparator + Started + columnSeparator + Ends + columnSeparator + Number_of_Bids + columnSeparator + First_Bid + columnSeparator + Currently + columnSeparator + Buy_Price + columnSeparator + Description + "\n"
            tableUser = tableUser + sellUserID + columnSeparator + sellUserRating + columnSeparator + sellUserLocation + columnSeparator + sellUserCountry +"\n"
            tableSell = tableSell + ItemID + columnSeparator + sellUserID + "\n"

            for category in item[ "Category" ]:
                tableCategory = tableCategory + category + "\n"
                tableCatItem = tableCatItem + category + columnSeparator + ItemID + "\n"

            if None != item[ "Bids" ]:
                for bid in item[ "Bids" ]:

                    bidUserID = bid[ "Bid" ][ "Bidder" ][ "UserID" ]
                    bidUserID = "\"" + bidUserID.replace( "\"", "\"\"" ) + "\""
                    bidTime = transformDttm( bid[ "Bid" ][ "Time" ] )
                    bidAmount = transformDollar( bid[ "Bid" ][ "Amount" ] )
                    bidRating = bid[ "Bid" ][ "Bidder" ][ "Rating" ]

                    if "Location" in bid[ "Bid" ][ "Bidder" ]:
                        bidLocation = bid[ "Bid" ][ "Bidder" ][ "Location" ]
                        bidLocation = "\"" + bidLocation.replace( "\"", "\"\"" ) + "\""
                    else:
                        bidLocation = 'NULL'

                    if "Country" in bid[ "Bid" ][ "Bidder" ]:
                        bidCountry = bid[ "Bid" ][ "Bidder" ][ "Country" ]
                        bidCountry = "\"" + bidCountry.replace( "\"", "\"\"" ) + "\""
                    else:
                        bidCountry = 'NULL'
                    tableUser = tableUser + bidUserID + columnSeparator + bidRating + columnSeparator + bidLocation + columnSeparator + bidCountry + "\n"
                    tableBid = tableBid + ItemID + columnSeparator + bidUserID + columnSeparator + bidTime + columnSeparator + bidAmount + "\n"

        f_sell = open( "tableSell.dat", "a" )
        f_sell.write( tableSell +'\n' )
        f_sell.close()

        f_category = open( "tableCategory.dat", "a" )
        f_category.write( tableCategory +'\n' )
        f_category.close()

        f_user = open( "tableUser.dat", "a" )
        f_user.write( tableUser + '\n' )
        f_user.close()

        f_catItem = open( "tableCatItem.dat", "a" )
        f_catItem.write( tableCatItem + '\n' )
        f_catItem.close()

        f_bid = open( "tableBid.dat", "a" )
        f_bid.write( tableBid +'\n' )
        f_bid.close()

        f_item = open( "tableItem.dat", "a" )
        f_item.write( tableItem +'\n' )
        f_item.close()

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print "Success parsing " + f

if __name__ == '__main__':
    main(sys.argv)
