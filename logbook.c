#include <stdio.h>
#include <string.h>
#ifdef mac
#include <StdLib.h>
#endif

#define MAX_JUMPS 5000
/*#define TIME_FROM_ALT(a) (((a) - 3000.0) / 1000.0 * 6.3 + 10.5)*/
int time_chart[] = { 6, 10, 13, 16, 20,
                    23, 26, 29, 32, 35,
                    39, 42, 45, 48, 51,
                    54, 57, 61, 64, 67,
                    70, 73, 76, 80, 83,
                    86, 89, 92, 95, 98}; // This line is extrapolated.

int		jump_chart[21][5], total[5];

int time_from_alt(int altitude)
{
    int time;

    if (altitude < 3000)
        time = 0;
    else
    {
        int idx = (altitude - 3000) / 500;

        if (idx > (sizeof(time_chart) / sizeof(int) - 1))
        {
            printf("Time chart not big enough!\n");
            exit(1);
        }
        
        time = time_chart[idx];
    }
    
    return time;
}

main(argc, argv)
    int		argc;
    char	*argv[];
{
    FILE	*in, *out;
    int		jumps, freefalls, hours, mins, secs;
    int		calc_hours, calc_mins, calc_secs;
    int		inp_alt, inp_time, altitude[MAX_JUMPS], time[MAX_JUMPS];
    int		i, group, num_groups;
    char        line[256], *pos;
    int         twelve_reached = 0;
    int         running_totals = 0;
    int         excel_format = 0;
    
    if (argc != 1 && argc != 2)
    {
	printf("Usage: logbook [-a][-r]\n");
	exit(1);
    }
	
    in= fopen("logbook.dat", "r");
	
    jumps= 0;
    while (1)
    {
	fscanf(in, "%d %d", &altitude[jumps], &time[jumps]);
	if (altitude[jumps] == 0)
	    break;
	++jumps;
    }

    fclose(in);
	
    if (argc == 2 && !strcmp(argv[1], "-r"))
    {
        running_totals = 1;
    }
    else if (argc == 2 && !strcmp(argv[1], "-e"))
    {
        excel_format = 1;
    }
/*
    else if (argc == 2 && !strcmp(argv[1], "-c"))
    {
        int i;
        
        for (i=0; i<jumps; ++i)
        {
            int match = 0;
            
            if (time[i] == time_from_alt(altitude[i]))
            {
                time[i] = -1;
            }
        }

	out= fopen("logbook.dat", "w");
	    
	for (i=0; i<jumps; ++i)
        {
            printf("jump %d\n", i);
	    fprintf(out, "%d %d\n", altitude[i], time[i]);
        }
        
	fprintf(out, "0 0\n");
	    
	fclose(out);

        exit(0);
    }
*/
    else if (argc == 2 && !strcmp(argv[1], "-a"))
    {
	while (1)
	{
	    printf("Jump %d: ", jumps + 1);
	    fgets(line, 256, stdin);
	    while (line[0] != '\0' && line[0] < '!')
		strcpy(line, line + 1);
	    while (line[0] != '\0' && line[strlen(line) - 1] < '!')
		line[strlen(line) - 1] = '\0';
	    
	    inp_alt = atoi(line);
	    if (line[0] == '\0' || inp_alt == 0)
		break;
	    
	    if (inp_alt < 20)
		inp_alt *= 1000;
	    else if (inp_alt < 1000)
		inp_alt *= 100;
	    
	    pos = strchr(line, ' ');
	    if (pos)
		inp_time = atoi(pos + 1);
	    else
	    {
                inp_time = -1;
	    }
	    
	    altitude[jumps]= inp_alt;
	    time[jumps]= inp_time;
	    ++jumps;
	}
	    
	out= fopen("logbook.dat", "w");
	    
	for (i=0; i<jumps; ++i)
	    fprintf(out, "%d %d\n", altitude[i], time[i]);
	    
	fprintf(out, "0 0\n");
	    
	fclose(out);

        exit(0);
    }
	
    for (group=0; group<21; ++group)
	for (i=0; i<5; ++i)
	    jump_chart[group][i]= 0;
    for (i=0; i<5; ++i)
	total[i]= 0;
		
    hours= mins= secs= 0;
    calc_hours= calc_mins= calc_secs= 0;
    freefalls= 0;

    if (running_totals)
    {
        printf("Jump\tAlt\tTime\tAltTime\tTotalTime\tComments\n");
        printf("-------------------------------------------------------------\n");
    }
    else if (excel_format)
    {
        printf("Jump,Alt,Time,AltTime,TotalTime\n");
    }
    
    for (i=0; i<jumps; ++i)
    {
        int t, ta;

        group= i / 10;
	if (group > 20)
	    group= 20;
		
        t = time[i];
        ta = time_from_alt(altitude[i]);
        
        if (t < 0)
        {
            t = ta;
        }

        if (t == 0)
	{
	    ++jump_chart[group][0];
	    ++total[0];
	}
	else if (t <= 39)
        {
            ++jump_chart[group][1];
            ++total[1];
            ++freefalls;
        }
        else if (t <= 44)
        {
            ++jump_chart[group][2];
            ++total[2];
            ++freefalls;
        }
        else if (t <= 59)
        {
            ++jump_chart[group][3];
            ++total[3];
            ++freefalls;
        }
        else
        {
            ++jump_chart[group][4];
            ++total[4];
            ++freefalls;
        }

	secs += t;
	while (secs >= 60)
	{
	    ++mins;
	    if (mins == 60)
	    {
		++hours;
		mins= 0;
	    }
			
	    secs -= 60;
	}

	if ((!twelve_reached && hours >= 12) && !excel_format)
	{
	    printf("*** 12-hours of freefall reached on jump %d\n", i + 1);
	    twelve_reached = 1;
	}
	
	calc_secs += ta;
	while (calc_secs >= 60)
	{
	    ++calc_mins;
	    if (calc_mins == 60)
	    {
		++calc_hours;
		calc_mins= 0;
	    }
			
	    calc_secs -= 60;
	}		

        if (running_totals)
        {
            printf("%d\t%d\t", i+1, altitude[i]);
            
            if (time[i] < 0)
            {
                printf("---\t");
            }
            else
            {
                printf("%d\t", time[i]);
            }
            
            printf("%d\t%02d:%02d:%02d\t",
                   ta,
                   hours, mins, secs);

            if (t > (ta + 4))
            {
                printf("Low pull??\n");
            }
            else if (t < (ta - 4))
            {
                if ((t < 4) && (altitude[i] > 4000))
                {
                    printf("Crew jump?\n");
                }
                else
                {
                    printf("High pull?\n");
                }
            }
            else
            {
                printf("\n");
            }
        }
        else if (excel_format)
        {
            printf("%d,%d,", i+1, altitude[i]);
            
            if (time[i] < 0)
            {
                printf("---,");
            }
            else
            {
                printf("%d,", time[i]);
            }
            
            printf("%d,%02d:%02d:%02d\n",
                   ta,
                   hours, mins, secs);
        }
    }

    if (!excel_format)
    {
        printf("\n");
        
        num_groups= (jumps - 1) / 10 + 1;
        if (num_groups > 21)
            num_groups= 21;
        
        printf("                 ");
        for (group=0; group<num_groups; ++group)
            printf("%2d ", group + 1);
        printf(" Total\n");
	
        printf("                -");
        for (group=0; group<num_groups; ++group)
            printf("---");
        printf("------\n");
	
        printf("Static lines:    ");
        for (group=0; group<num_groups; ++group)
            printf("%2d ", jump_chart[group][0]);
        printf(" %4d\n", total[0]);
	
        printf("1 to 39 secs:    ");
        for (group=0; group<num_groups; ++group)
            printf("%2d ", jump_chart[group][1]);
        printf(" %4d\n", total[1]);
	
        printf("40 to 44 secs:   ");
        for (group=0; group<num_groups; ++group)
            printf("%2d ", jump_chart[group][2]);
        printf(" %4d\n", total[2]);
	
        printf("45 to 59 secs:   ");
        for (group=0; group<num_groups; ++group)
            printf("%2d ", jump_chart[group][3]);
        printf(" %4d\n", total[3]);
	
        printf("60 or more secs: ");
        for (group=0; group<num_groups; ++group)
            printf("%2d ", jump_chart[group][4]);
        printf(" %4d\n\n", total[4]);
	
        printf("Total jumps:         %d\n", jumps);
        printf("Total freefalls:     %d\n", freefalls);
        printf("Total freefall time: %d:%02d:%02d\n\n", hours, mins, secs);
        printf("Total freefall time calculated from altitudes: %d:%02d:%02d\n",
               calc_hours, calc_mins, calc_secs);
    }
}
