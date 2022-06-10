from modules.core.time import tictoc as stopwatch, convert as converter
from modules.core.constants import initialise_constants

from constants import *
from modules.core.system import input as inpt
from modules.collisions.loadsave import loadsave as rw
from modules.collisions.features import scrub as scrub, lat_lon as lat_lon, \
    scalar_generate as sc_gen
from modules.core.variables import num_man as nm
from modules.core.features import graph as graph
from modules.collisions.model import theta_ap as theta_ap

stopwatch.start_time()
initialise_constants()

t = 'time'
p = 'proton'
a = 'alpha'

particle_list = [p, a]
valid_enc = [4, 6, 7]
print('Currently loaded encounters:', valid_enc, '\n')

valid_full = ['f', 'F', 'full', 'Full', 'ful', 'Ful', 'ff', 'FF', 'fF', 'Ff']
valid_single = ['s', 'S', 'single', 'Single', 'ss', 'SS', 'sS', 'Ss']

h = 1
while h > 0:
    data_set_input = input('Full data set or singular? (F/S)')
    if data_set_input in valid_full:
        encount = 0
        h = 0
    elif data_set_input in valid_single:
        h = 0
        g = 1
        while g > 0:
            enc_input = input('Please enter an encounter:')
            if inpt.validate_input_number(enc_input):
                if int(enc_input) in valid_enc:
                    encount = int(enc_input)
                    g = 0
                elif enc_input == '':
                    print('Error: No input provided.')
                else:
                    print('Error: No corresponding encounter available.')
            else:
                print('Error: Argument provided is not valid,'
                      f' argument {enc_input}, is of type {type(enc_input)}.')
    else:
        print('Error: Please make a valid selection.')

# Generate directory strings for encounters
enc(encount, valid_enc, False)
print('\n')
error_files = enc.error_files_loaded
mm_data = rw.encounter_import(encount, valid_enc, error_files)
if error_files:
    error_data = rw.error_import()
sc_data = rw.sc_import()
print('\nData import sucessful.\n')

# Generate equal sized arays for all data

mm_len_max = 0
error_len_max = 0
sc_len_max = 0

for x in enc.encounter:
    for y in mm_data[x].keys():
        if len(mm_data[x][y][t]) > mm_len_max:
            mm_len_max = len(mm_data[x][y][t])
            arg_encount_ = x
            arg_mm_file = y

    if error_files:
        for y in error_data[x].keys():
            if len(error_data[x][y][t]) > error_len_max:
                error_len_max = len(error_data[x][y][t])
                arg_encount_ = x
                arg_error_file = y
    else:
        pass

    for y in sc_data[x].keys():
        if len(sc_data[x][y][t]) > sc_len_max:
            sc_len_max = len(sc_data[x][y][t])  # here
            arg_encount_ = x
            arg_sc_file = y

lengths = [mm_len_max, error_len_max, sc_len_max]
max_len = max(lengths)

if max_len == lengths[0]:
    t_ = mm_data[arg_encount_][arg_mm_file][t]
elif max_len == lengths[1]:
    t_ = error_data[arg_encount_][arg_error_file][t]
elif max_len == lengths[2]:
    t_ = sc_data[arg_encount_][arg_sc_file][t]

for x in enc.encounter:
    for y in mm_data[x].keys():
        xp = mm_data[x][y][t]
        for z in mm_data[x][y].keys():
            fp = mm_data[x][y][z]
            mm_data[x][y][z] = np.interp(t_, xp, fp)

    if error_files:
        for y in error_data[x].keys():
            xp = error_data[x][y][t]
            for z in error_data[x][y].keys():
                fp = error_data[x][y][z]
                error_data[x][y][z] = np.interp(t_, xp, fp)

    for y in sc_data[x].keys():
        xp = sc_data[x][y][t]
        for z in sc_data[x][y].keys():
            fp = sc_data[x][y][z]
            sc_data[x][y][z] = np.interp(t_, xp, fp)

# Generate file and/or combine files
print('Generating data file... \n')
solar_data = {}
errors = {}
spc_data = {}

for particle in particle_list:
    solar_data[particle] = {}
    errors[particle] = {}

for x in range(1):
    encount = enc.encounter[x]
    for y in range(1):
        for particle in particle_list:
            indx = particle_list.index(particle)
            if nm.is_even(indx):
                arg_x_ = 0
            elif nm.is_odd(indx):
                arg_x_ = 1
            for z in mm_data[encount][enc.encounter_names[2 * x + arg_x_]].keys():
                solar_data[particle][z] = []

    if error_files:
        for y in range(1):
            for particle in particle_list:
                indx = particle_list.index(particle)
                if nm.is_even((indx)):
                    arg_x_ = 0
                else:
                    arg_x_ = 1
                for z in error_data[encount][enc.encounter_errors[2 * x + arg_x_]].keys():
                    errors[particle][z] = []

    for y in range(len(enc.sc_names)):
        spc_data[enc.sc_names[y]] = {}
        for z in sc_data[encount][enc.sc_names[y]].keys():
            spc_data[enc.sc_names[y]][z] = []

for x in range(enc.num_of_encs):
    encount = enc.encounter[x]
    for particle in particle_list:
        indx = particle_list.index(particle)
        if nm.is_even(indx):
            arg_x_ = 0
        elif nm.is_odd(indx):
            arg_x_ = 1
        for z in solar_data[particle].keys():
            for w in range(len(mm_data[encount][enc.encounter_names[2 * x + arg_x_]][z])):
                solar_data[particle][z].append(
                    mm_data[encount][enc.encounter_names[2 * x + arg_x_]][z][w])
        if error_files:
            for z in errors[particle].keys():
                for w in range(len(error_data[encount][enc.encounter_names[2*x + arg_x_]][z])):
                    errors[particle][z].append(error_data[encount][enc.encounter_names[2 * x + arg_x_]][z][w])

    for y in enc.sc_names:
        for z in spc_data[y].keys():
            for w in range(len(sc_data[encount][y][z])):
                spc_data[y][z].append(sc_data[encount][y][z][w])

print('Scrubbing data...')
# solar_data, errors, spc_data = scrub.scrub_data(solar_data, errors, spc_data)

spc_data[enc.sc_names[0]] = lat_lon.latlong_psp(spc_data[enc.sc_names[0]])
spc_data[enc.sc_names[1]] = lat_lon.latlong_wind(spc_data[enc.sc_names[1]])

# Generate single time set for the whole data set in appropriate unit
solar_data[t] = []
for i in range(len(solar_data[p][t])):
    solar_data[t].append(converter.epoch_time(solar_data[p][t][i]))

# Generate temperatures and velocity magnitudes
print('Generating velocity magnitudes and temperature file... \n')
scalar_velocity = sc_gen.scalar_velocity(solar_data)
psp_scalar_temps, wind_scalar_temps = sc_gen.scalar_temps(solar_data, spc_data)
theta_ap_0 = psp_scalar_temps['theta_ap']
print('Note: Files have been generated and loaded in.', '\n')
theta_ap_final = theta_ap.make_theta_vals(solar_data, spc_data, psp_scalar_temps, 1.0)

theta = {'i': theta_ap_0, 'f': theta_ap_final}

X = np.linspace(0, 15, 1000)
Y = theta
color = ['red', 'blue']
line_style = ['solid', 'dashed']

graph.histogram(X, Y,  style=line_style, colours=color)

stopwatch.end_time()
