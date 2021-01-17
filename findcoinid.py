import csv
'''
bigfile = open("coinids.txt", "r")
bigstring = bigfile.read()
test = bigstring.split("</option>")

coin_id_dict = {

}
for i in range(len(test)):
    test[i] = test[i].lower()
    string_no_option = test[i][8:]
    data_subtext_index_start = string_no_option.find("data-subtext")
    data_subtext_index_end = string_no_option.find(">")

    #print(string_no_option)
    #print(string_no_option[data_subtext_index_start:data_subtext_index_end+1])
    almost_clean = string_no_option[:data_subtext_index_start] + string_no_option[data_subtext_index_end+1:]
    almost_clean = almost_clean[7:]
    quote_index = almost_clean.find("\"")
    very_clean = almost_clean[:quote_index] + almost_clean[quote_index+1:]
    space_index = very_clean.find(" ")
    very_clean_id = very_clean[:space_index]
    very_clean_token = very_clean[space_index+1:]
    very_clean_token = very_clean_token.replace(" ", "-")
    #print(very_clean_token, very_clean_id)
    coin_id_dict[very_clean_token]=very_clean_id



del coin_id_dict['--------</selec---------</select']
print(coin_id_dict)


w = csv.writer(open("output.csv", "w"))
for key, val in coin_id_dict.items():
    w.writerow([key, val])

f = open("coin_id_dict.txt","w")
f.write( str(coin_id_dict) )
f.close()
'''

def find_coin_id(coin_name):
    with open('output.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if row[0] == coin_name:
                print(row[1])

find_coin_id("ethereum")