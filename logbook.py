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

jump_type_profiles = {'RW': FREEFALL_PROFILE_HORIZONTAL,
                      'CRW': FREEFALL_PROFILE_HORIZONTAL,
                      'Static Line': FREEFALL_PROFILE_HORIZONTAL,
                      'Hop and Pop': FREEFALL_PROFILE_HORIZONTAL,
                      'JM': FREEFALL_PROFILE_HORIZONTAL,
                      'Tandem': FREEFALL_PROFILE_HORIZONTAL,
                      'Sit-Fly': FREEFALL_PROFILE_HORIZONTAL,
                      'Hybrid': FREEFALL_PROFILE_HORIZONTAL,
                      'Freestyle': FREEFALL_PROFILE_HORIZONTAL,
                      'Tracking': FREEFALL_PROFILE_TRACKING}

normal_exit_altitudes = {'Mile-Hi': (11000, 13999),
                         'Spaceland Dallas': (11000, 14999)}

freefall_time_table_109mph = ((500, 6),
                              (1000, 10),
                              (1500, 13),
                              (2000, 16),
                              (2500, 20),
                              (3000, 23),
                              (3500, 26),
                              (4000, 29),
                              (4500, 32),
                              (5000, 35),
                              (5500, 39),
                              (6000, 42),
                              (6500, 45),
                              (7000, 48),
                              (7500, 51),
                              (8000, 54),
                              (8500, 57),
                              (9000, 61),
                              (9500, 64),
                              (10000, 67),
                              (10500, 70),
                              (11000, 73),
                              (11500, 76),
                              (12000, 80),
                              (12500, 83))

def exit_alt_average(i):
    dropzone = jumps[i][1]
    if dropzone in normal_exit_altitudes:
        minimum = normal_exit_altitudes[dropzone][0]
        maximum = normal_exit_altitudes[dropzone][1]

        alt_total = 0.0
        num_alts = 0
        for j in sorted(jumps):
            if j >= i:
                break

            if jumps[j][5] != '' and jumps[j][1] == dropzone:
                exit_alt = int(jumps[j][5])
                if exit_alt >= minimum and exit_alt <= maximum:
                    alt_total += exit_alt
                    num_alts += 1

        return round(alt_total / num_alts)
    else:
        return None

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
        t = round(math.sqrt(2.0 * d / a))
    else:
        #t = round(((i - dt) / 1000.0) * tpt + tt)
        t = round((d - dt) / vt + tt)

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
        d = round(0.5 * a * (t * t))
    else:
        d = round(dt + (t - tt) * vt)

    return(ealt - d)

def alt_from_time_109mph(ealt, t):
    if t < 10.0:
        p = 1.4
        d = round((1000 / 10**p) * t**p)
    else:
        m = (12500 - 1000) / (82.834 - 10)
        b = -10 * m + 1000
        d = round(m * t + b)

    return(ealt - d)

def gear_used(jump_num):
    gear = ''
    for i in sorted(gear_log):
        if i > jump_num:
            break
        gear = gear_log[i][0]

    return gear

def had_reserve_ride(jump_num):
    if jump_num in reserve_ride_log:
        return 'Yes'

    return 'No'

def had_cutaway(jump_num):
    if jump_num in reserve_ride_log:
        return reserve_ride_log[jump_num][0]

    return 'No'


if '--diag' in sys.argv:
    print('Old freefall time table function test with just values in table')
    print('(table time, table distance, distance, distance difference)')
    print('---------------------------------------------------------------')
    average = 0.0
    num = 0
    for table_entry in freefall_time_table_109mph:
        table_dist = table_entry[0]
        table_time = table_entry[1]
        dist = -alt_from_time_109mph(0, table_time)
        dist_diff = dist - table_dist
        print(table_time, table_dist, dist, dist_diff)
        if table_time >= 10.0:
            average += dist_diff
            num += 1
    print("Average distance difference (in linear range): " + str(average / num))
    print()

    print('Old freefall time table function test for every second')
    print('(time, distance)')
    print('------------------------------------------------------')
    for time in range(0, 100):
        dist = -alt_from_time_109mph(0, time)
        print(time, dist)

    sys.exit()

list_jumps = False
header = False
csv = False
full = False
export = False
stats = False
show_types = False
show_aircraft = False
show_dropzones = False
show_gear = False

one_jump_only = None
latest_jumps_only = None
range_of_jumps_only = None

fix_files = False

for option in sys.argv:
    if option[0].isnumeric():
        if option.find('-') != -1:
            range_of_jumps_only = [ int(x) for x in option.split('-', 1) ]
        else:
            one_jump_only = int(option)
    elif not option.startswith('--') and option.startswith('-'):
        option_string = option[1:]
        if option_string.isnumeric():
            latest_jumps_only = int(option_string)
        else:
            for option_char in option[1:]:
                if option_char == 'l':
                    list_jumps = True
                elif option_char == 'h':
                    header = True
                elif option_char == 'c':
                    csv = True
                elif option_char == 'f':
                    full = True
                elif option_char == 'e':
                    export = True
                elif option_char == 's':
                    stats = True
                elif option_char == 't':
                    show_types = True
                elif option_char == 'a':
                    show_aircraft = True
                elif option_char == 'd':
                    show_dropzones = True
                elif option_char == 'g':
                    show_gear = True

if '--list' in sys.argv:
    list_jumps = True

if '--fix-files' in sys.argv:
    fix_files = True

if '--header' in sys.argv:
    header = True

if '--csv' in sys.argv:
    csv = True

if '--full' in sys.argv:
    full = True

if '--export' in sys.argv:
    export = True

if '--stats' in sys.argv:
    stats = True

if '--types' in sys.argv:
    show_types = True

if '--aircraft' in sys.argv:
    show_aircraft = True

if '--dropzones' in sys.argv:
    show_dropzones = True

if '--gear' in sys.argv:
    show_gear = True

#
# Ingest gear log data
#
fp = open('gear.csv', 'r')

gear_log = {}
for line in fp:
    line = line.strip()
    if line == '':
        continue

    items = line.strip().split(',', 1)

    if not items[0].isdigit():
        continue

    gear_log[int(items[0])] = items[1:]

fp.close()

#
# Ingest reserve ride data
#
fp = open('reserve_rides.csv', 'r')

reserve_ride_log = {}
for line in fp:
    line = line.strip()
    if line == '':
        continue

    items = line.strip().split(',', 2)

    if not items[0].isdigit():
        continue

    reserve_ride_log[int(items[0])] = items[1:]

fp.close()

jumps = {}
jump_num_offset = 0
gaps = []

#
# Ingest data from old logbooks
#
fp = open('first_logbooks.csv', 'r')
if fix_files:
    fp_new = open('first_logbooks_new.csv', 'w')

first_jumps = {}
last_jump_num = 0
add_gap = False
for line in fp:
    line = line.strip()
    if line == '':
        if fix_files:
            print(line, file=fp_new)
        continue

    items = line.split(',', 5)

    if items[0] == 'gap':
        add_gap = True
        continue
    elif items[0] == 'offset':
        jump_num_offset += int(items[1])
        continue

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

    jump_num = int(items[0]) + jump_num_offset

    if jump_num < 1 or jump_num > 1207:
        sys.exit('Jump number out of range at jump ' + str(jump_num - jump_num_offset) + ' in first_logbooks')
    if jump_num in first_jumps:
        sys.exit('Duplicate jump number at jump ' + str(jump_num - jump_num_offset) + ' in first_logbooks')
    if jump_num <= last_jump_num:
        sys.exit('Jump number not increasing at jump ' + str(jump_num - jump_num_offset) + ' in first_logbooks')

    if add_gap:
        gaps.append(jump_num)
        add_gap = False

    if len(items) != 6:
        sys.exit('Wrong number of columns at jump ' + str(jump_num - jump_num_offset) + ' in first_logbooks')

    # Undo quoting of notes field
    notes = items[-1]
    if notes.startswith('"') and notes.endswith('"'):
        notes = notes[1:-1]
        notes = notes.replace('""', '"')
        items[-1] = notes

    if fix_files:
        if ',' in notes or '"' in notes:
            notes = '"' + notes.replace('"', '""') + '"'
        print(str(jump_num) + ',' + ','.join(items[1:5] + [notes]), file=fp_new)

    first_jumps[jump_num] = items[1:]

    last_jump_num = jump_num

fp.close()
if fix_files:
    fp_new.close()

fp = open('logbook.dat', 'r')

jump_num = 1
date = ''
for line in fp:
    if jump_num > 1207:
        break

    items = line.strip().split()
    exit_alt = int(items[0])
    deploy_alt = None
    freefall_time = int(items[1])
    if freefall_time < 0:
        if freefall_time < -1:
            deploy_alt = -freefall_time
        freefall_time = None

    if jump_num in first_jumps:
        date = first_jumps[jump_num][0]
        location = first_jumps[jump_num][1]
        aircraft = first_jumps[jump_num][2]
        jump_type = first_jumps[jump_num][3]
        notes = first_jumps[jump_num][4]
    else:
        date = ''
        location = ''
        aircraft = ''
        # Use RW for jump type if details not yet entered.
        # Note: This whole "else" can be changed to an error
        #       when all data has been entered.
        jump_type = 'RW'
        notes = ''

    jumps[jump_num] = [date, location, aircraft, gear_used(jump_num), jump_type, str(exit_alt), '' if deploy_alt == None else str(deploy_alt), 'Feet', '0', '' if freefall_time == None else str(freefall_time), had_reserve_ride(jump_num), had_cutaway(jump_num), notes]

    jump_num += 1

fp.close()

#
# Ingest data manually entered from last paper logbook
#
fp = open('last_logbook.csv', 'r')
if fix_files:
    fp_new = open('last_logbook_new.csv', 'w')

last_jump_num = 0
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
    if jump_num <= last_jump_num:
        sys.exit('Jump number not increasing at jump ' + str(jump_num) + ' in last_logbook')

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
        print(str(jump_num) + ',' + ','.join(items[1:8] + [notes]), file=fp_new)

    items.insert(4, gear_used(jump_num))

    items.insert(8, 'Feet')
    items.insert(9, '0')
    items.insert(11, had_reserve_ride(jump_num))
    items.insert(12, had_cutaway(jump_num))

    jumps[jump_num] = items[1:]

    last_jump_num = jump_num

fp.close()
if fix_files:
    fp_new.close()

#
# Ingest data from current jumps
#
fp = open('jumps.csv', 'r')
if fix_files:
    fp_new = open('jumps_new.csv', 'w')

last_jump_num = 0
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
        sys.exit('Duplicate jump number at jump ' + str(jump_num) + ' in current jumps')
    if jump_num <= last_jump_num:
        sys.exit('Jump number not increasing at jump ' + str(jump_num) + ' in current jumps')

    if len(items) != 9:
        sys.exit('Wrong number of columns at jump ' + str(jump_num) + ' in current jumps')

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
        print(str(jump_num) + ',' + ','.join(items[1:8] + [notes]), file=fp_new)

    items.insert(4, gear_used(jump_num))

    items.insert(8, 'Feet')
    items.insert(9, '0')
    items.insert(11, had_reserve_ride(jump_num))
    items.insert(12, had_cutaway(jump_num))

    jumps[jump_num] = items[1:]

    last_jump_num = jump_num

fp.close()
if fix_files:
    fp_new.close()

#
# Ingest data from Skydiving Logbook app
#
try:
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
        # Note: The app does not obey the rule that requires quoting of
        #       strings containing double quotes, so we always have to
        #       convert double quote pairs to double quotes.
        notes = notes.replace('""', '"')
        items[-1] = notes

        if fix_files:
            if ',' in notes or '"' in notes:
                notes = '"' + notes.replace('"', '""') + '"'
            print(str(jump_num) + ',' + ','.join(items[1:12] + [notes]), file=fp_new)

        items.insert(11, had_reserve_ride(jump_num))

        if items[10] == '':
            # Should not happen for this file
            sys.exit('odd: missing freefall time at jump ' + str(jump_num) + ' in app data')
        elif items[7] == '':
            # Should not happen for this file
            sys.exit('odd: missing pull altitude at jump ' + str(jump_num) + ' in app data')

        if jump_num in jumps:
            if jumps[jump_num] != items[1:]:
                sys.exit('Jump info does not match old info at jump ' + str(jump_num) + ' in app data')
        else:
            jumps[jump_num] = items[1:]

    fp.close()
    if fix_files:
        fp_new.close()
except FileNotFoundError:
    pass

# Check for errors in log data
last_jump_num = 0
last_timestamp = None

for i in sorted(jumps):
    if len(jumps[i]) != 13:
        sys.exit('Wrong number of columns at jump ' + str(i))

    jump_time_string = jumps[i][0]
    if jump_time_string:
        if i not in gaps and i != last_jump_num + 1:
            sys.exit('Jump number not in sequence at jump ' + str(i))

        timestamp = calendar.timegm(time.strptime(jump_time_string, '%Y-%m-%d'))
        if last_timestamp != None and timestamp < last_timestamp:
            sys.exit('Jump date goes back in time at jump ' + str(i))

        if jumps[i][4] not in jump_type_profiles:
            sys.exit('Invalid jump type at jump ' + str(i))

        last_jump_num = i
        last_timestamp = timestamp

# Predict missing exit altitudes
predicted_exit_alts = {}
for i in jumps:
    if jumps[i][5] == '':
        predicted_exit_alt = exit_alt_average(i)
        if predicted_exit_alt == None:
            sys.exit('Exit altitude calculation not supported at jump ' + str(i))
        else:
            predicted_exit_alts[i] = predicted_exit_alt

# Insert calculated values for missing altitudes and/or freefall times
for i in jumps:
    if i in predicted_exit_alts:
        jumps[i][5] = str(predicted_exit_alts[i])

    if jumps[i][9] == '':
        if jumps[i][6] == '':
            if i < 1569:
                jumps[i][6] = '2500'
            else:
                jumps[i][6] = '2700'

        jumps[i][9] = str(time_from_alt(int(jumps[i][5]), int(jumps[i][6]), jump_type_profiles[jumps[i][4]]))
    elif jumps[i][6] == '':
        if i <= 1207:
            # For the "first jumps", a freefall time table for 109mph
            # was incorrectly used to log freefall time, so here we
            # use the reverse calculation to obtain the correct
            # deployment altitude and then fix the freefall time.
            jumps[i][6] = str(alt_from_time_109mph(int(jumps[i][5]), int(jumps[i][9])))
            jumps[i][9] = str(time_from_alt(int(jumps[i][5]), int(jumps[i][6]), jump_type_profiles[jumps[i][4]]))
        else:
            jumps[i][6] = str(alt_from_time(int(jumps[i][5]), int(jumps[i][9]), jump_type_profiles[jumps[i][4]]))

if list_jumps:
    if header:
        if csv:
            print('Jump #,Date,Drop Zone,Aircraft,Gear,Jump Type,Exit Alt,Deploy Alt,Altitude Unit,Dist to Target,Delay,Reserve Ride,Cutaway,Notes')
        elif export:
            print('Jump Number,Date,Location,Aircraft,Gear,Jump Type,Exit Alt,Deployment Alt,Altitude Unit,Distance to Target,Freefall Time (sec),Cutaway,Notes')
        elif full:
            print('Jump #: Date|Drop Zone|Aircraft|Gear|Jump Type|Exit Alt|Deploy Alt|Delay|Reserve Ride|Cutaway|Notes')
        else:
            print('Jump #: Date|Drop Zone|Notes')

    if latest_jumps_only != None:
        jump_list = sorted(jumps)[-latest_jumps_only:]
    elif range_of_jumps_only != None:
        jump_list = sorted(set(range(range_of_jumps_only[0], range_of_jumps_only[1] + 1)) & set(jumps))
    elif one_jump_only != None:
        jump_list = list({one_jump_only} & set(jumps))
    else:
        jump_list = sorted(jumps)

    if csv:
        for i in jump_list:
            notes = jumps[i][12]
            if ',' in notes or '"' in notes:
                notes = '"' + notes.replace('"', '""') + '"'
            print(str(i) + ',' + ','.join(jumps[i][:12] + [notes]))
    elif export:
        alt_unit_translations = {'Feet': 'ft', 'Meters': 'm'}
        for i in jump_list:
            notes = jumps[i][12]
            if ',' in notes or '"' in notes:
                notes = '"' + notes.replace('"', '""') + '"'
            print(str(i) + ',' + ','.join(jumps[i][:7] + [alt_unit_translations[jumps[i][7]]] + jumps[i][8:10] + jumps[i][11:12] + [notes]))
    elif full:
        for i in jump_list:
            print(str(i) + ': ' + '|'.join(jumps[i][:7] + jumps[i][9:13]))
    else:
        for i in jump_list:
            print(str(i) + ': ' + '|'.join(jumps[i][:2] + jumps[i][12:13]))

if stats:
    if list_jumps:
        print()

    today = datetime.date.today()
    year_ago = datetime.date(today.year - 1, today.month, today.day)
    month_ago_year = today.year - (today.month == 1)
    month_ago_month = 12 if today.month == 1 else (today.month - 1)
    month_ago_day = min(today.day, calendar.monthrange(month_ago_year,
                                                       month_ago_month)[1])
    month_ago = datetime.date(month_ago_year,
                              month_ago_month,
                              month_ago_day)

    total_freefall_seconds = 0
    total_freefall_feet = 0
    num_reserve_rides = 0
    num_cutaways = 0
    highest_jump = 0
    lowest_pull = -1
    longest_freefall_time = 0
    last_jump_date = None
    jumps_in_year = {}
    jumps_past_year = 0
    jumps_past_month = 0
    for i in sorted(jumps):
        freefall_seconds = int(jumps[i][9])
        total_freefall_seconds += freefall_seconds
        total_freefall_feet += int(jumps[i][5]) - int(jumps[i][6])
        num_reserve_rides += jumps[i][10] != 'No'
        num_cutaways += jumps[i][11] != 'No'
        exit_alt = int(jumps[i][5])
        if exit_alt > highest_jump:
            highest_jump = exit_alt
        deploy_alt = int(jumps[i][6])
        if lowest_pull == -1 or deploy_alt < lowest_pull:
            lowest_pull = deploy_alt
        if freefall_seconds > longest_freefall_time:
            longest_freefall_time = freefall_seconds

        jump_time_string = jumps[i][0]
        if jump_time_string:
            jump_time = time.strptime(jump_time_string, '%Y-%m-%d')
            jump_date = datetime.date(jump_time.tm_year,
                                      jump_time.tm_mon,
                                      jump_time.tm_mday)

            if jump_date > year_ago:
                jumps_past_year += 1
            if jump_date > month_ago:
                jumps_past_month += 1

            if not jump_date.year in jumps_in_year:
                jumps_in_year[jump_date.year] = 1
            else:
                jumps_in_year[jump_date.year] += 1

            last_jump_date = jump_date

    days_since_last_jump = (today - last_jump_date).days

    left_width = 40
    #right_width = 32

    for i in sorted(jumps_in_year):
        print(('Jumps in %s' % i).ljust(left_width) + str(jumps_in_year[i]))

    print()

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

    print('Total reserve rides: '.ljust(left_width) + str(num_reserve_rides))

    print('Total cutaways: '.ljust(left_width) + str(num_cutaways))

    print('Longest freefall time: '.ljust(left_width) + str(longest_freefall_time) + ' sec')

    print('Highest jump: '.ljust(left_width) + str(highest_jump) + ' feet')

    print('Lowest pull: '.ljust(left_width) + str(lowest_pull) + ' feet')

    print()

    if last_jump_date:
        print('Date of last jump: '.ljust(left_width) + last_jump_date.strftime('%A, %b %d, %Y').replace(' 0', ' ') + '  (' + str(days_since_last_jump) + ' ' + ('day' if days_since_last_jump == 1 else 'days') + ' ago)')
    else:
        print('Date of last jump: '.ljust(left_width) + 'Never')

    print('Jumps in the past year: '.ljust(left_width) + str(jumps_past_year))

    print('Jumps in the past month: '.ljust(left_width) + str(jumps_past_month))

if show_types:
    jump_types_done = []
    for i in sorted(jumps):
        jump_type = jumps[i][4]
        if jump_type and (jump_type not in jump_types_done):
            jump_types_done.append(jump_type)

    print('Jump types done:')
    for jump_type in jump_types_done:
        print('    ' + jump_type)

if show_aircraft:
    aircraft_jumped = []
    for i in sorted(jumps):
        aircraft = jumps[i][2]
        if aircraft and (aircraft not in aircraft_jumped):
            aircraft_jumped.append(aircraft)

    print('Aircraft jumped:')
    for aircraft in aircraft_jumped:
        print('    ' + aircraft)

if show_dropzones:
    dropzones_jumped = []
    for i in sorted(jumps):
        dropzone = jumps[i][1]
        if dropzone and (dropzone not in dropzones_jumped):
            dropzones_jumped.append(dropzone)

    print('Dropzones jumped:')
    for dropzone in dropzones_jumped:
        print('    ' + dropzone)

if show_gear:
    rigs_jumped = []
    canopies_jumped = []
    for i in sorted(jumps):
        gear = jumps[i][3]
        if gear:
            if ' / ' in gear:
                rig, canopy = gear.split(' / ', 1)
                if canopy == '[unknown]':
                    canopy = None
            else:
                canopy = gear
                rig = None

            if rig and (rig not in rigs_jumped):
                rigs_jumped.append(rig)
            if canopy and (canopy not in canopies_jumped):
                canopies_jumped.append(canopy)

    print('Rigs jumped:')
    for rig in rigs_jumped:
        print('    ' + rig)
    print('Canopies jumped:')
    for canopy in canopies_jumped:
        print('    ' + canopy)
