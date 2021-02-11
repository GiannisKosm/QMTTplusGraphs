import paho.mqtt.client as mqtt
import ssl
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from threading import Timer
from datetime import datetime

class IoT:
    def __init__(self):
        self.ax = None
        self._establish_mqtt_connection()
        self._prepare_graph_window()
        
    def start(self):
        if self.ax:
            self.client.loop_start()
            plt.show()
        else:
            self.client.loop_forever()

    def disconnect(self, args=None):
        self.client.disconnect()

    def _establish_mqtt_connection(self):
        self.client = mqtt.Client()
        self.client.tls_set_context(ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_log = self._on_log
        self.client.username_pw_set('','')
        self.client.connect("",)


    def _on_connect(self,client,userdata,flags,rc):
        print("Connected with result code "+str(rc))

        self.client.subscribe('hscnl/hscnl02/state/ZWaveNode005_ElectricMeterWatts/state')
        self.client.subscribe('hscnl/hscnl02/command/ZWaveNode005_Switch/command')
        self.client.subscribe('hscnl/hscnl02/state/ZWaveNode005_Switch/state')

    def _on_message(self,client,userdata,msg):
        if msg.topic == 'hscnl/hscnl02/state/ZWaveNode005_ElectricMeterWatts/state':
            self._add_value_to_plot(float(msg.payload))

        print('Message: '+msg.topic+' '+str(msg.payload))
    
    def _on_log(self,client,userdata,level,buf):
        print('Log: ',buf)

    def _prepare_graph_window(self):
        plt.rcParams['toolbar'] = 'None'
        self.ax = plt.subplot(111)
        self.dataX = []
        self.dataY = []
        self.first_ts = datetime.now()
        self.lineplot, = self.ax.plot(
        self.dataX, self.dataY, linestyle='--', marker='o', color='b')
        self.ax.figure.canvas.mpl_connect('close_event', self.disconnect)
        self.finishing = False
        self._my_timer()
        axcut = plt.axes([0.0, 0.0, 0.1, 0.06])
        self.bcut = Button(axcut, 'ON')
        axcut2 = plt.axes([0.1, 0.0, 0.1, 0.06])
        self.bcut2 = Button(axcut2, 'OFF')
        self.state_field = plt.text(1.5, 0.3, 'STATE: -')
        self.bcut.on_clicked(self._button_on_clicked)
        self.bcut2.on_clicked(self._button_off_clicked)
    
    def _refresh_plot(self): 
        if len(self.dataX) > 0:
            self.ax.set_xlim(min(self.first_ts, min(self.dataX)), max(max(self.dataX), datetime.now()))
            self.ax.set_ylim(min(self.dataY) * 0.8, max(self.dataY) * 1.2)
            self.ax.relim() 
        else:
            self.ax.set_xlim(self.first_ts, datetime.now())
            self.ax.relim() 
        plt.draw()
    
    def _add_value_to_plot(self, value): 
        self.dataX.append(datetime.now()) 
        self.dataY.append(value) 
        self.lineplot.set_data(self.dataX, self.dataY) 
        self._refresh_plot()
    
    def _my_timer(self): 
        self._refresh_plot() 
        if not self.finishing:
            Timer(1.0, self._my_timer).start()

    
    def _button_on_clicked(self, event): 
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode005_Switch', 'ON')

    def _button_off_clicked(self, event): 
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode005_Switch', 'OFF')

    
try:
    iotexam = IoT()
    iotexam.start()

except KeyboardInterrupt:
    print('interrupted')
    try:
        iotexam.disconnect()
        sys.exit(0)
    except SystemExit:
        os._exit(0)




