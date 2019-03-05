fp = open('logbook.dat', 'r')

logbook_dat_entries = {}
jump_num = 1
for line in fp:
    items = line.strip().split()
    exit_alt = int(items[0])
    freefall_time = int(items[1])

    if exit_alt == 0 and freefall_time == 0:
        break

    if jump_num > 1207:
        logbook_dat_entries[jump_num] = [exit_alt, freefall_time]

    jump_num += 1

fp.close()

fp = open('last_logbook.csv', 'r')

for line in fp:
    line = line.strip()
    if line == '':
        continue

    items = line.split(',', 8)

    if not items[0].isdigit():
        continue

    jump_num = int(items[0])
    last_logbook_entry = items[1:]

    if jump_num in logbook_dat_entries:
        if last_logbook_entry[4] != str(logbook_dat_entries[jump_num][0]):
            print("Mismatch (exit altitude) on jump " + str(jump_num))
            print("  from logbook.dat: " + str(logbook_dat_entries[jump_num][0]))
            print("  from last_logbook.csv: '" + last_logbook_entry[4] + "'")
        if ((logbook_dat_entries[jump_num][1] == -1 and last_logbook_entry[6] != '') or
            (logbook_dat_entries[jump_num][1] != -1 and last_logbook_entry[6] != str(logbook_dat_entries[jump_num][1]))):
            print("Mismatch (delay) on jump " + str(jump_num))
            print("  from logbook.dat: " + str(logbook_dat_entries[jump_num][1]))
            print("  from last_logbook.csv: '" + last_logbook_entry[6] + "'")
