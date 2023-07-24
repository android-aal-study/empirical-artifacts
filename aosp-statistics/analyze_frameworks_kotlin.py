
category = {
    'test': 0,
    'system-app': 0,
    'sdk-tool': 0,
    'others': 0,
}

with open('ls-kt-framework.txt') as r:
    for line in map(str.strip, r):
        if 'test' in line:
            category['test'] += 1
        elif 'packages' in line:
            category['system-app'] += 1
        elif 'tools' in line:
            category['sdk-tool'] += 1
        else:
            category['others'] += 1
            print(line)

print('-----')
print(category)
