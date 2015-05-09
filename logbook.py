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

if '--export' in sys.argv:
    export = True
else:
    export = False

if '--stats' in sys.argv:
    stats = True
else:
    stats = False


jumps = {}

#
# Ingest data from old logbook
#
fp = open('old_jumps_andy.csv', 'r')

ignore_next_line = False
for line in fp:
    if ignore_next_line:
        ignore_next_line = False
        continue

    line = line.strip()
    if line == '':
        continue

    items = line.split(',', 12)

    if items[0] == 'Jump #':
        #if len(items) == 9:
        #    items.insert(4, 'Gear')
        #if len(items) == 10:
        #    items.insert(8, 'Altitude Unit')
        #    items.insert(10, 'Cutaway')
        #
        #print(','.join(items))
        continue

    jump_num = int(items[0])

    if len(items) == 12:
        # No Notes field - add a blank one
        items.append('')

    if len(items) != 13:
        print(items)
        sys.exit('Wrong number of columns at jump ' + str(jump_num) + ' in app data')

    if items[10] == '':
        # Should not happen for this file
        sys.exit('odd: missing freefall time at jump ' + str(jump_num) + ' in app data')
    elif items[7] == '':
        # Should not happen for this file
        sys.exit('odd: missing pull altitude at jump ' + str(jump_num) + ' in app data')

    # Reformat date if needed
    if items[1].find('/') != -1:
        m, d, y = tuple(int(e) for e in items[1].split('/'))
        items[1] = "%04d-%02d-%02d" % (y, m, d)

    # Fix quoting on notes field
    notes = items[-1]
    if notes.startswith('"'):
        if notes.endswith('"'):
            notes = notes[1:-1]
        else:
            notes = notes[1:]
            ignore_next_line = True
    notes = notes.replace('""', '"')
    items[-1] = notes

    if jump_num in jumps:
        if jumps[jump_num] != tuple(items[1:]):
            sys.exit('Jump info does not match old info at jump ' + str(jump_num) + ' in old data')
    else:
        jumps[jump_num] = tuple(items[1:])

fp.close()
last_old_jump = jump_num

#
# Ingest data from new/app logbook file
#
# (note that code is dupicated largely from above so behavior
#  can be slightly tweaked)
#
fp = open('skydiving_logbook_andy.csv', 'r')

ignore_next_line = False
for line in fp:
    if ignore_next_line:
        ignore_next_line = False
        continue

    line = line.strip()
    if line == '':
        continue

    items = line.split(',', 12)

    if items[0] == 'Jump #':
        #if len(items) == 9:
        #    items.insert(4, 'Gear')
        #if len(items) == 10:
        #    items.insert(8, 'Altitude Unit')
        #    items.insert(10, 'Cutaway')
        #
        #print(','.join(items))
        continue

    jump_num = int(items[0])

    if len(items) == 12:
        # No Notes field - add a blank one
        items.append('')

    if len(items) != 13:
        print(items)
        sys.exit('Wrong number of columns at jump ' + str(jump_num) + ' in app data')

    if items[10] == '':
        # Should not happen for this file
        sys.exit('odd: missing freefall time at jump ' + str(jump_num) + ' in app data')
    elif items[7] == '':
        # Should not happen for this file
        sys.exit('odd: missing pull altitude at jump ' + str(jump_num) + ' in app data')

    # Reformat date if needed
    if items[1].find('/') != -1:
        m, d, y = tuple(int(e) for e in items[1].split('/'))
        items[1] = "%04d-%02d-%02d" % (y, m, d)

    # Fix quoting on notes field
    notes = items[-1]
    if notes.startswith('"'):
        if notes.endswith('"'):
            notes = notes[1:-1]
        else:
            notes = notes[1:]
            ignore_next_line = True
    notes = notes.replace('""', '"')
    items[-1] = notes

    jumps[jump_num] = tuple(items[1:])

fp.close()

# Not processing new jumps (yet)
first_new_jump = None


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
        #sys.exit('Jump date goes back in time at jump ' + str(i))
        print('Warning: Jump date goes back in time at jump ' + str(i))

    last_jump_num = i
    last_timestamp = timestamp

if list_jumps:
    for i in sorted(jumps):
        if ((not old_jumps_only and not new_jumps_only) or
            (old_jumps_only and i <= last_old_jump) or
            (new_jumps_only and first_new_jump != None and i >= first_new_jump)):
            print(str(i) + ',' + ','.join(jumps[i]))

if export:
    print('Jump #,Date,Drop Zone,Aircraft,Gear,Jump Type,Exit Alt,Depl Alt,Altitude Unit,Delay (s),Cutaway,Notes')
    #print('Jump #,Date,Drop Zone,Aircraft,Gear,Jump Type,Exit Alt,Depl Alt,Altitude Unit,Dist to Target,Delay (s),Cutaway,Notes')

    for i in sorted(jumps):
        if ((not old_jumps_only and not new_jumps_only) or
            (old_jumps_only and i <= last_old_jump) or
            (new_jumps_only and first_new_jump != None and i >= first_new_jump)):
            print(str(i) + ',' + ','.join(jumps[i][:7] + ('ft',) + jumps[i][9:11] + ('"' + jumps[i][11] + '"',)))
            #print(str(i) + ',' + ','.join(jumps[i]))

if stats:
    if export:
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
