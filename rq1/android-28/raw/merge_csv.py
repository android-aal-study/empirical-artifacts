

is_member = lambda m: '->' in m
black = set(filter(is_member, open('hiddenapi-blacklist.txt')))
darkgrey = set(filter(is_member, open('hiddenapi-dark-greylist.txt')))
lightgrey = set(filter(is_member, open('hiddenapi-light-greylist.txt')))

print('black list: ' + str(len(black)))
print('dark-grey list: ' + str(len(darkgrey)))
print('light-grey list: ' + str(len(lightgrey)))

print(len(black)+len(darkgrey)+len(lightgrey))

merged = black.union(darkgrey).union(lightgrey)

print(len(merged))



import csv



with open('../hiddenapi-flags.csv', 'w', newline='') as w:
    writer = csv.writer(w)
    for b in black:
        writer.writerow((b.strip(), 'black'))
    for d in darkgrey:
        writer.writerow((d.strip(), 'darkgrey'))
    for l in lightgrey:
        writer.writerow((l.strip(), 'lightgrey'))



