

###########  Daten vom Aufruf des Scripts abholen in Array getdata  ###########
getdata = data.get("on_off_bool_time",[])

###########  Erstes Element des Array in ontime_inp  ON-ZEIT  ###########
ontime_inp = str(getdata['inputdt_on'])
switch_onstate = hass.states.get(ontime_inp).state
switch_ontmstp = hass.states.get(ontime_inp).attributes.get('timestamp')
[hours_on, minutes_on, seconds_on] = [int(x) for x in switch_onstate.split(':')]

###########  Zweites Element des Array in offtime_inp  OFF-ZEIT  ###########
offtime_inp = str(getdata['inputdt_off'])
switch_offstate = hass.states.get(offtime_inp).state
switch_offtmstp = hass.states.get(offtime_inp).attributes.get('timestamp')
[hours_off, minutes_off, seconds_off] = [int(x) for x in switch_offstate.split(':')]

###########  Drittes Element des Array in laufz_shw  SENSOR BINÄR   AN AUS  ###########
laufz_shw = str(getdata['binsens_bool'])
sens_laufz = hass.states.get(laufz_shw)

###########  Viertes Element des Array in laufz_shwt  SENSOR TEMPLATE LAUFZEIT ###########
laufz_shwt = str(getdata['senstpl_ontime'])
sens_laufzt = hass.states.get(laufz_shwt)

###########  Zeit mit Korrektur 2h  ###########
current_time = datetime.datetime.now() + datetime.timedelta(hours=2)
# logger.warning(current_time)

###########  on off Zeit in Binary Sensor  ###########
sens_tpl_text = ""

###########  zeit on ist höher als zeit off d.h. es läuft über Mitternacht  ###########
# on: 21 off: 3 geht
# on:  1 off: 2 geht nicht
error = False

if switch_ontmstp > switch_offtmstp:
    
    ###########  nächster tag als integer  (von jetziger zeit)###########
    dayplus = current_time +  datetime.timedelta(hours=24)
    dayplus = int(dayplus.day)

    ###########  vorheriger tag als integer (von jetziger zeit) ###########
    dayminus = current_time -  datetime.timedelta(hours=24)
    dayminus = int(dayminus.day)    

    #  Ab Mitternach bis Schaltzeit Off    ODER Jetzt in OFF Stunde   
    #  Ein 21:00  Aus 03:00      jetzt 00:00 < OFF 03:00 geht     jetzt 23:59 < OFF 03:00  geht nicht
    #  jetzt: 0 <= off: 3   on: 21 geht
    #  jetzt:23 <= off: 3   on: 21 geht nicht aber sollte ON  nächste if    
    #  jetzt: 4 <= off: 3   on: 21 geht nicht
    #  jetzt: 4 <= off: 3   on: 21 geht nicht
    #  jetzt: 3 <= off: 3   on:    geht wird mit nächster if gespalten
    if current_time.hour <= hours_off :
 
        #  ab mitternacht und selbe stunde
        #  off: 3 on: 3  geht
        #  off: 2 on: 3  geht nicht       
        if hours_on == hours_off:

            # wenn off minuten grösser als jetzt 
            #  off: 3:30 >= jetzt: 3:20  geht      
            #  off: 3:30 >= jetzt: 3:30  geht
            #  off: 3:30 >= jetzt: 3:31  geht nicht
            #  Zusammenfassung: 
            #  wenn off zeit grösser als on zeit? läuft über mitternacht + Ausschaltstunde erreicht? + aus ein Ausschaltstunde gleich? + aus minuten noch nicht erreicht? von input
            if minutes_off >= current_time.minute:
                
                # on zeit von gestern generieren da wir mitternacht überschritten haben          dayminus  
                neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % dayminus + ' ' + str(switch_onstate)
                # datetime datum erstellen mit input:on zeit + datum von gestern  dayminus
                dateon = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")

                sens_tpl_text = sens_tpl_text + "1 : On:" + neui[:-3]
                
                # off zeit mit auschaltdatum von heute  input:off + aktuelles datum
                neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % current_time.day + ' ' + str(switch_offstate)
                dateoff = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
                # Binary sensor Off Zeit Text mit datum von gestern angehängt an on zeit          
                sens_tpl_text = sens_tpl_text + " | Off:" + neui[:-3]
                
            # off minuten kleiner als jetzt     OFF Status  neues einschalt datum erstellen
            # Ausschaltzeit erreicht wenn off_on Stunden gleich + aus_ein schaltsunde gleich
            else:    
                # inpu:on mit datum von heute = neue ein-schaltzeit 
                neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % current_time.day + ' ' + str(switch_onstate)
                dateon = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
                # Binary sensor input:on  mit datum von heute            
                sens_tpl_text = sens_tpl_text + "2 : On:" + neui

                # inpu:off mit datum von morgen = neue aus-schaltzeit  (alles noch in selber stunde)
                neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % dayplus + ' ' + str(switch_offstate)
                dateoff = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
                # Binary sensor input:off  mit datum von morgen                
                sens_tpl_text = sens_tpl_text + " | Off:" + neui    
        
        # ein und auschaltzeit nicht in selber stunde  +  ab mitternacht bis Ausschaltzeit  
        else:
            # Einschaltzeit + Datum jetzt
            neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % dayminus + ' ' + str(switch_onstate)
            dateon = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
            # Binary sensor input:on  mit datum von gestern            
            sens_tpl_text = sens_tpl_text + "3 : On:" + neui
            
            # Ausschaltzeit + Datum jetzt
            neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % current_time.day + ' ' + str(switch_offstate)
            dateoff = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
            # Binary sensor input:off  mit datum von heute                
            sens_tpl_text = sens_tpl_text + " | Off:" + neui  
            
            
    #  Schaltzeit On bis mitternacht        
    #  Ein 21:00  Aus 03:00      jetzt 00:00 >= ON 21:00 geht nicht    jetzt 23:59 > ON 21:00  geht 
    #  jetzt: 20 >= on: 21   off:  3 False
    #  jetzt: 21 >= on: 21   off:  3 True
    #  jetzt: 22 >= on: 21   off:  3 True
    #  jetzt:  0 >= on: 21   off:  3 False  vorheriger if
    #  jetzt: 3 >=  on: 21   off:  3 False  vorheriger if + selbe stunde
    #  jetzt: 4 >=  on: 21   off:  3 False   
    elif current_time.hour >= hours_on:
        # Einschaltzeit + Datum jetzt        
        neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % current_time.day + ' ' + str(switch_onstate)
        dateon = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
        # Binary sensor input:on  mit datum von heute  
        sens_tpl_text = sens_tpl_text + "4 : On:" + neui
        
        neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % dayplus + ' ' + str(switch_offstate)
        dateoff = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
        # Binary sensor input:off  mit datum von morgen      
        sens_tpl_text = sens_tpl_text + " | Off:" + neui    
        
        # laufzeit = str(dateoff - dateon)
        # # laufzeit = laufzeit[:-3] 
        # # logger.warning(laufzeit[:-3] )
        
        # hass.states.set( laufz_shwt, laufzeit, {
        # 'friendly_name': 'Lampe Laufzeit' 
        # })    

        
        # if dateon < current_time < dateoff:
        #     hass.states.set( laufz_shw, "on", { 'friendly_name': sens_tpl_text }) 
        #     logger.warning("lampe an")
        # else:
        #     hass.states.set( laufz_shw, "off", { 'friendly_name': sens_tpl_text }) 
        #     logger.warning("lampe aus")

    else:       
        # Einschaltzeit + Datum jetzt
        neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % current_time.day + ' ' + str(switch_onstate)
        dateon = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
        # Binary sensor input:on  mit datum von heute  
        sens_tpl_text = sens_tpl_text + "5 : On:" + neui
        
        # Einschaltzeit + Datum morgen        
        neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % dayplus + ' ' + str(switch_offstate)
        dateoff = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
        # Binary sensor input:off  mit datum von heute      
        sens_tpl_text = sens_tpl_text + " | Off:" + neui    


    
# Ein und Ausschaltzeit im gleichen Tag
# 
elif switch_ontmstp < switch_offtmstp:
    
    # Einschaltzeit + Datum jetzt
    neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % current_time.day + ' ' + str(switch_onstate)
    dateon = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
    # Binary sensor input:on  mit datum von heute  
    sens_tpl_text = sens_tpl_text + "5 : On:" + neui
    
    neui = str(current_time.year) + '-' + '%02d' % current_time.month + '-' + '%02d' % current_time.day + ' ' + str(switch_offstate)
    dateoff = datetime.datetime.strptime(neui , "%Y-%m-%d %H:%M:%S")
    # Binary sensor input:off  mit datum von heute      
    sens_tpl_text = sens_tpl_text + " | Off:" + neui    
    
else:
    logger.warning("error lampe aus")
    # Binary sensor input:on  mit datum von heute  
    sens_tpl_text = sens_tpl_text + "6 : Error Off" 
    error = True

# logger.warning(dateon)
# logger.warning(current_time)
# logger.warning(dateoff)
 
            




if error == True:
    
    hass.states.set( laufz_shw, "off", { 'friendly_name': sens_tpl_text }) 
    logger.warning("error dateon = None   lampe off")
    hass.states.set( laufz_shwt, "error", { 'friendly_name': "Error: No Date" }) 

else:
    
    laufzeit = str(dateoff - dateon)
    hass.states.set( laufz_shwt, laufzeit, { 'friendly_name': 'Lampe Laufzeit' })
    
    if dateon < current_time < dateoff:
        hass.states.set( laufz_shw, "on", { 'friendly_name': sens_tpl_text }) 
        logger.warning("lampe an")
        
        sending = hass.states.get('switch.mystrom_1').state
        logger.warning(sending)
        if sending == "off":
            
            hass.services.call( "switch", "turn_on", service_data={ 'entity_id': 'switch.mystrom_1' })
            # hass.services.call('light', 'turn_on', service_data={ 'entity_id': 'light.dining_table_lights', 'brightness': '255', 'kelvin': '2700' })
        
            
        
    else:
        hass.states.set( laufz_shw, "off", { 'friendly_name': sens_tpl_text }) 
        logger.warning("lampe aus")
        
        sending = hass.states.get('switch.mystrom_1').state
        logger.warning(sending)
        if sending == "on":
            hass.services.call( "switch", "turn_off", service_data={ 'entity_id': 'switch.mystrom_1' })
            # hass.services.call( "switch", "switch.turn_off", "off", { "entity_id": "switch.mystrom_1"})
            # hass.states.set( 'switch.mystrom_1', "off")        
