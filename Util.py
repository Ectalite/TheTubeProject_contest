import os
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import datetime, threading, time
import serial
import Util

def LoadDataFile(fileName):
    # Création du chemin du fichier des données joint
    rep_base = ''
    filePath = os.path.join(os.getcwd(), rep_base, fileName)

    # Récupération des données joint
    series = pd.read_csv(filePath, header=0, sep=";")
    # Départ de l'index à 0ms
    series.index = series.index.values.astype(float) - float(series.index[0])

    return series


def formatFinalBufferintoDataFrame(_readingBuffer):
    _df = pd.DataFrame.from_records(_readingBuffer, columns=['time', 'setpoint', 'position'])
    _df['time'] = pd.to_datetime(_df['time'], format='%H:%M:%S.%f')
    _df = _df.set_index('time')
    _df['position'] = _df['position'].astype(float)
    _df['setpoint'] = _df['setpoint'].astype(float)

    return _df


def trajectory_generation(arduino, _traj_index, _traj_len, _traj_data, _stop_event,_traj_period = 0.1):

    while not _stop_event.is_set():
        next_call = time.time()

        write(arduino,f"traj={datetime.datetime.now().time()};{_traj_data.Setpoint[_traj_index]}\r\n")

        next_call = next_call + _traj_period
        if _traj_index < _traj_len:
            _traj_index = _traj_index + 10 * _traj_period
        else:
            _traj_index = 0
        time_sleep = next_call - time.time()
        if time_sleep > 0 :
            time.sleep(time_sleep)
        else:
            print("!! Warning, time frame missed !!")


def write(arduino,x):
    arduino.write(bytes(x, 'utf-8'))


def readToBuffer(arduino, readingBuffer):
    print("Start read thread")
    # Réinitialisation des tampons d'entrée et de sortie
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    while True:
        if arduino.inWaiting() > 0:
            try:
                line = arduino.readline().strip()
                values = line.decode('ascii').split(';')
                readingBuffer.append(tuple(values))
                print(line)
            except ValueError:  # this deals will the error
                print("!! Warning, Unable to put data in read buffer !!")
