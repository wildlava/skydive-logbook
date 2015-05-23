import sys
import math
import time
import calendar
import datetime

a = 32.174
vt_horizontal = 176.0
vt_tracking = 144.0

FREEFALL_PROFILE_HORIZONTAL = 0
FREEFALL_PROFILE_TRACKING = 1

def time_from_alt(ealt, dalt, jump_type):
    if jump_type == FREEFALL_PROFILE_TRACKING:
        vt = vt_tracking
    else:
        vt = vt_horizontal

    tt = vt / a
    dt = 0.5 * a * (tt * tt)
    #tpt = 1000.0 / vt

    d = ealt - dalt
    if d < dt:
        t = int(round(math.sqrt(2.0 * d / a), 0))
    else:
        #t = int(round(((i - dt) / 1000.0) * tpt + tt, 0))
        t = int(round((d - dt) / vt + tt, 0))

    return(t)


def alt_from_time(ealt, t, jump_type):
    if jump_type == FREEFALL_PROFILE_TRACKING:
        vt = vt_tracking
    else:
        vt = vt_horizontal

    tt = vt / a
    dt = 0.5 * a * (tt * tt)
    #tpt = 1000.0 / vt

    if t < tt:
        d = int(round(0.5 * a * (t * t)))
    else:
        d = int(round(dt + (t - tt) * vt))

    return(ealt - d)


def gear_used(jump_num):
    gear = ''
    for gear_log_entry in gear_log:
        if int(gear_log_entry[0]) > jump_num:
            break
        gear = gear_log_entry[1]

    return gear


if '--list' in sys.argv:
    list_jumps = True
else:
    list_jumps = False

if '--old-only' in sys.argv:
    old_jumps_only = True
else:
    old_jumps_only = False

if '--new-only' in sys.argv:
    new_jumps_only = True
else:
    new_jumps_only = False

if '--fix-files' in sys.argv:
    fix_files = True
else:
    fix_files = False

if '--header' in sys.argv:
    header = True
else:
    header = False

if '--csv' in sys.argv:
    csv = True
else:
    csv = False

if '--export' in sys.argv:
    export = True
else:
    export = False

if '--stats' in sys.argv:
    stats = True
else:
    stats = False

#
# Ingest gear log data
#
fp = open('gear.csv', 'r')

gear_log = []
for line in fp:
    line = line.strip()
    if line == '' or not line[0].isdigit():
        continue

    gear_log.append(line.strip().split(','))

fp.close()

jumps = {}

#
# Ingest data from old logbooks
#
fp = open('first_logbooks.csv', 'r')
if fix_files:
    fp_new = open('first_logbooks_new.csv', 'w')

first_jumps = {}
for line in fp:
    line = line.strip()
    if line == '':
        if fix_files:
            print(line, file=fp_new)
        continue

    items = line.split(',', 5)

    if not items[0].isdigit():
        #if len(items) == 9:
        #    items.insert(4, 'Gear')
        #if len(items) == 10:
        #    items.insert(8, 'Altitude Unit')
        #    items.insert(10, 'Cutaway')
        #
        #print(','.join(items))
        if fix_files:
            print(line, file=fp_new)
        continue

    jump_num = int(items[0])
    if jump_num in first_jumps:
        sys.exit('Duplicate jump number at jump ' + str(jump_num) + ' in first_logbooks')

    if len(items) != 6:
        sys.exit('Wrong number of columns at jump ' + str(jump_num))

    if (items[4] == 'RW' or
        items[4] == 'CRW' or
        items[4] == 'Static Line' or
        items[4] == 'Hop and Pop' or
        items[4] == 'Sit-Fly' or
        items[4] == 'Hybrid' or
        items[4] == 'Freestyle'):
        freefall_profile = FREEFALL_PROFILE_HORIZONTAL
    elif items[4] == 'Tracking':
        freefall_profile = FREEFALL_PROFILE_TRACKING
    else:
        sys.exit('Invalid jump type at jump ' + str(jump_num) + ' in first_logbooks')

    # Undo quoting of notes field
    notes = items[-1]
    if notes.startswith('"') and notes.endswith('"'):
        notes = notes[1:-1]
        notes = notes.replace('""', '"')
        items[-1] = notes

    if fix_files:
        if ',' in notes or '"' in notes:
            notes = '"' + notes.replace('"', '""') + '"'
        print(str(jump_num) + ',' + ','.join(tuple(items[1:5]) + (notes,)), file=fp_new)

    first_jumps[jump_num] = tuple(items[1:])

fp.close()
if fix_files:
    fp_new.close()

fp = open('logbook.dat', 'r')

jump_num = 1

date = ''
gear = ''
for line in fp:
    location = ''
    aircraft = ''
    jump_type = ''
    notes = ''

    if jump_num < 1208:
        items = line.strip().split()
        exit_alt = int(items[0])
        freefall_time = int(items[1])
        if freefall_time < 0:
            deploy_alt = 2500
            freefall_time = time_from_alt(exit_alt, deploy_alt, FREEFALL_PROFILE_HORIZONTAL)
        else:
            deploy_alt = alt_from_time(exit_alt, freefall_time, FREEFALL_PROFILE_HORIZONTAL)
            if jump_num < 100 and deploy_alt < 2500 and exit_alt >= 3000:
                deploy_alt = 2500
                freefall_time = time_from_alt(exit_alt, deploy_alt, FREEFALL_PROFILE_HORIZONTAL)
            elif deploy_alt < 2200 and exit_alt >= 3000:
                deploy_alt = 2200
                freefall_time = time_from_alt(exit_alt, deploy_alt, FREEFALL_PROFILE_HORIZONTAL)
            #if deploy_alt < 2500:
            #    print('*************************************************************')

        if jump_num in first_jumps:
            date = first_jumps[jump_num][0]
            location = first_jumps[jump_num][1]
            aircraft = first_jumps[jump_num][2]
            jump_type = first_jumps[jump_num][3]
            notes = first_jumps[jump_num][4]

        gear = gear_used(jump_num)

        jumps[jump_num] = (date, location, aircraft, gear, jump_type, str(exit_alt), str(deploy_alt), 'Feet', '0', str(freefall_time), 'No', notes)

        jump_num += 1

fp.close()

#
# Ingest data manually entered from last paper logbook
#
fp = open('last_logbook.csv', 'r')
if fix_files:
    fp_new = open('last_logbook_new.csv', 'w')

for line in fp:
    line = line.strip()
    if line == '':
        if fix_files:
            print(line, file=fp_new)
        continue

    items = line.split(',', 8)

    if not items[0].isdigit():
        #if len(items) == 9:
        #    items.insert(4, 'Gear')
        #if len(items) == 10:
        #    items.insert(8, 'Altitude Unit')
        #    items.insert(10, 'Cutaway')
        #
        #print(','.join(items))
        if fix_files:
            print(line, file=fp_new)
        continue

    jump_num = int(items[0])
    if jump_num in jumps:
        sys.exit('Duplicate jump number at jump ' + str(jump_num) + ' in last_logbook')

    if len(items) != 9:
        sys.exit('Wrong number of columns at jump ' + str(jump_num) + ' in last_logbook')

    #if len(items) != 13:
    #    sys.exit('Wrong number of columns at jump ' + str(jump_num))

    # Undo quoting of notes field
    notes = items[-1]
    if notes.startswith('"') and notes.endswith('"'):
        notes = notes[1:-1]
        notes = notes.replace('""', '"')
        items[-1] = notes

    if fix_files:
        if ',' in notes or '"' in notes:
            notes = '"' + notes.replace('"', '""') + '"'
        print(str(jump_num) + ',' + ','.join(tuple(items[1:8]) + (notes,)), file=fp_new)

    items.insert(4, gear_used(jump_num))

    if (items[5] == 'RW' or
        items[5] == 'CRW' or
        items[5] == 'Hop and Pop' or
        items[5] == 'Sit-Fly' or
        items[5] == 'Hybrid' or
        items[5] == 'Freestyle'):
        freefall_profile = FREEFALL_PROFILE_HORIZONTAL
    elif items[5] == 'Tracking':
        freefall_profile = FREEFALL_PROFILE_TRACKING
    else:
        sys.exit('Invalid jump type at jump ' + str(jump_num) + ' in last_logbook')

    items.insert(8, 'Feet')
    items.insert(9, '0')
    items.insert(11, 'No')

    if items[10] == '':
        if items[7] == '':
            items[7] = '2500'
        items[10] = str(time_from_alt(int(items[6]), int(items[7]), freefall_profile))
    elif items[7] == '':
        items[7] = str(alt_from_time(int(items[6]), int(items[10]), freefall_profile))

    jumps[jump_num] = tuple(items[1:])

fp.close()
if fix_files:
    fp_new.close()
last_old_jump = jump_num

#
# Ingest data from Skydiving Logbook app
#
fp = open('skydiving_logbook.csv', 'r')
if fix_files:
    fp_new = open('skydiving_logbook_new.csv', 'w')

for line in fp:
    line = line.strip()
    if line == '':
        if fix_files:
            print(line, file=fp_new)
        continue

    items = line.split(',', 12)

    if not items[0].isdigit():
        #if len(items) == 9:
        #    items.insert(4, 'Gear')
        #if len(items) == 10:
        #    items.insert(8, 'Altitude Unit')
        #    items.insert(10, 'Cutaway')
        #
        #print(','.join(items))
        if fix_files:
            print(line, file=fp_new)
        continue

    jump_num = int(items[0])

    if len(items) != 13:
        print(items)
        sys.exit('Wrong number of columns at jump ' + str(jump_num) + ' in app data')

    # Undo quoting of notes field
    notes = items[-1]
    if notes.startswith('"') and notes.endswith('"'):
        notes = notes[1:-1]
        notes = notes.replace('""', '"')
        items[-1] = notes

    if fix_files:
        if ',' in notes or '"' in notes:
            notes = '"' + notes.replace('"', '""') + '"'
        print(str(jump_num) + ',' + ','.join(tuple(items[1:12]) + (notes,)), file=fp_new)

    if items[10] == '':
        # Should not happen for this file
        sys.exit('odd: missing freefall time at jump ' + str(jump_num) + ' in app data')
    elif items[7] == '':
        # Should not happen for this file
        sys.exit('odd: missing pull altitude at jump ' + str(jump_num) + ' in app data')

    if jump_num in jumps:
        if jumps[jump_num] != tuple(items[1:]):
            sys.exit('Jump info does not match old info at jump ' + str(jump_num) + ' in app data')
    else:
        jumps[jump_num] = tuple(items[1:])

fp.close()
if fix_files:
    fp_new.close()

#
# Ingest new jumps
#
first_new_jump = None
try:
    fp = open('new_jumps.csv', 'r')

    for line in fp:
        line = line.strip()
        if line == '':
            continue

        items = line.split(',', 8)

        if not items[0].isdigit():
            continue

        jump_num = int(items[0])
        if jump_num in jumps:
            sys.exit('Duplicate jump number at jump ' + str(jump_num) + ' in new_jumps')

        if len(items) != 9:
            sys.exit('Wrong number of columns at jump ' + str(jump_num) + ' in new_jumps')

        # Undo quoting of notes field
        notes = items[-1]
        if notes.startswith('"') and notes.endswith('"'):
            notes = notes[1:-1]
            notes = notes.replace('""', '"')
            items[-1] = notes
        else:
            if ',' in notes or '"' in notes:
                sys.exit('Notes field needs proper quoting at jump ' + str(jump_num) + ' in new_jumps')

        items.insert(4, gear_used(jump_num))

        if (items[5] == 'RW' or
            items[5] == 'CRW' or
            items[5] == 'Hop and Pop' or
            items[5] == 'Sit-Fly' or
            items[5] == 'Hybrid' or
            items[5] == 'Freestyle'):
            freefall_profile = FREEFALL_PROFILE_HORIZONTAL
        elif items[5] == 'Tracking':
            freefall_profile = FREEFALL_PROFILE_TRACKING
        else:
            sys.exit('Invalid jump type at jump ' + str(jump_num) + ' in new_jumps')

        items.insert(8, 'Feet')
        items.insert(9, '0')
        items.insert(11, 'No')

        if items[10] == '':
            if items[7] == '':
                items[7] = '2700'
            items[10] = str(time_from_alt(int(items[6]), int(items[7]), freefall_profile))
        elif items[7] == '':
            items[7] = str(alt_from_time(int(items[6]), int(items[10]), freefall_profile))

        jumps[jump_num] = tuple(items[1:])
        if first_new_jump == None:
            first_new_jump = jump_num

    fp.close()
except FileNotFoundError:
    pass

# Check for errors in log data
last_jump_num = -1
last_timestamp = -1

for i in sorted(jumps):
    if len(jumps[i]) != 12:
        sys.exit('Wrong number of columns at jump ' + str(i))

    if last_jump_num != -1 and i != (last_jump_num + 1):
        sys.exit('Jump numbers not monatomically increasing at jump ' + str(i))

    timestamp = calendar.timegm(time.strptime(jumps[i][0], '%Y-%m-%d'))
    if last_timestamp != -1 and timestamp < last_timestamp:
        sys.exit('Jump date goes back in time at jump ' + str(i))

    last_jump_num = i
    last_timestamp = timestamp

if list_jumps:
    if header:
        if csv:
            print('Jump #,Date,Drop Zone,Aircraft,Gear,Jump Type,Exit Alt,Deploy Alt,Altitude Unit,Dist to Target,Delay,Cutaway,Notes')
        elif export:
            print('Jump #,Date,Drop Zone,Aircraft,Gear,Jump Type,Exit Alt,Depl Alt,Altitude Unit,Delay (s),Cutaway,Notes')
        else:
            print('Jump #: Date|Drop Zone|Aircraft|Gear|Jump Type|Exit Alt|Deploy Alt|Delay|Notes')

    if csv:
        for i in sorted(jumps):
            if ((not old_jumps_only and not new_jumps_only) or
                (old_jumps_only and i <= last_old_jump) or
                (new_jumps_only and first_new_jump != None and i >= first_new_jump)):
                notes = jumps[i][11]
                if ',' in notes or '"' in notes:
                    notes = '"' + notes.replace('"', '""') + '"'
                print(str(i) + ',' + ','.join(jumps[i][:11] + (notes,)))
    elif export:
        for i in sorted(jumps):
            if ((not old_jumps_only and not new_jumps_only) or
                (old_jumps_only and i <= last_old_jump) or
                (new_jumps_only and first_new_jump != None and i >= first_new_jump)):
                notes = jumps[i][11]
                if ',' in notes or '"' in notes:
                    notes = '"' + notes.replace('"', '""') + '"'
                print(str(i) + ',' + ','.join(jumps[i][:7] + ('ft',) + jumps[i][9:11] + (notes,)))
    else:
        for i in sorted(jumps):
            if ((not old_jumps_only and not new_jumps_only) or
                (old_jumps_only and i <= last_old_jump) or
                (new_jumps_only and first_new_jump != None and i >= first_new_jump)):
                print(str(i) + ': ' + '|'.join(jumps[i][:7] + jumps[i][9:10] + jumps[i][11:12]))


if stats:
    if list_jumps:
        print('')

    today = datetime.date.today()
    year_ago = datetime.date(today.year - 1, today.month, today.day)
    #month_ago = datetime.date((today.year - 1) if today.month == 1 else today.year,
    #                          12 if today.month == 1 else (today.month - 1),
    #                          today.day)
    month_ago = datetime.date(today.year - (today.month == 1),
                              12 if today.month == 1 else (today.month - 1),
                              today.day)

    total_freefall_seconds = 0
    total_freefall_feet = 0
    jump_types_done = []
    num_cutaways = 0
    highest_jump = 0
    lowest_pull = -1
    longest_freefall_time = 0
    jumps_past_year = 0
    jumps_past_month = 0
    for i in sorted(jumps):
        jump_type = jumps[i][4]
        if jump_type != '' and (jump_type not in jump_types_done):
            jump_types_done.append(jump_type)

        freefall_seconds = int(jumps[i][9])
        total_freefall_seconds += freefall_seconds
        total_freefall_feet += int(jumps[i][5]) - int(jumps[i][6])
        num_cutaways += jumps[i][10] != 'No'
        exit_alt = int(jumps[i][5])
        if exit_alt > highest_jump:
            highest_jump = exit_alt
        deploy_alt = int(jumps[i][6])
        if lowest_pull == -1 or deploy_alt < lowest_pull:
            lowest_pull = deploy_alt
        if freefall_seconds > longest_freefall_time:
            longest_freefall_time = freefall_seconds

        jump_time = time.strptime(jumps[i][0], '%Y-%m-%d')
        jump_date = datetime.date(jump_time.tm_year,
                                  jump_time.tm_mon,
                                  jump_time.tm_mday)
        if jump_date >= year_ago:
            jumps_past_year += 1
        if jump_date >= month_ago:
            jumps_past_month += 1

    left_width = 32
    #right_width = 32

    print('Total jumps: '.ljust(left_width) + str(len(jumps)))

    total_freefall_minutes = total_freefall_seconds // 60
    total_freefall_hours = total_freefall_minutes // 60
    print('Total freefall time: '.ljust(left_width) +
          ('%d:%02d:%02d' % (total_freefall_hours,
                             total_freefall_minutes % 60,
                             total_freefall_seconds % 60)))

    total_freefall_miles = total_freefall_feet // 5280
    print('Total freefall distance: '.ljust(left_width) +
          ('%d miles, %d feet' % (total_freefall_miles,
                                  total_freefall_feet % 5280)))

    print('Total cutaways: '.ljust(left_width) + str(num_cutaways))

    print('Longest freefall time: '.ljust(left_width) + str(longest_freefall_time) + ' sec')

    print('Highest jump: '.ljust(left_width) + str(highest_jump) + ' feet')

    print('Lowest pull: '.ljust(left_width) + str(lowest_pull) + ' feet')

    print('Jumps in the past year: '.ljust(left_width) + str(jumps_past_year))

    print('Jumps in the past month: '.ljust(left_width) + str(jumps_past_month))

    print('')

    print('Jump types done:')
    print('    ' + ', '.join(jump_types_done))
