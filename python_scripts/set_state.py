    
#===================================================================================================================
#  python_scripts/set_state.py 
# Set the state or other attributes for the entity specified in the Automation Action
#===================================================================================================================
#Credits:---https://github.com/rodpayne/home-assistant/blob/master/.homeassistant/python_scripts/set_state.py-------
#-------------------------------------------------------------------------------------------------------------------

inputEntity = data.get('entity_id')
if inputEntity is None:
    logger.warning("===== entity_id is required if you want to set something.")
else:    
    inputStateObject = hass.states.get(inputEntity)
    inputState = inputStateObject.state
    inputAttributesObject = inputStateObject.attributes.copy()

    for item in data:
        newAttribute = data.get(item)
        logger.debug("===== item = {0}; value = {1}".format(item,newAttribute))
        if item == 'entity_id':
            continue            # already handled
        elif item == 'state':
            inputState = newAttribute
        else:
            inputAttributesObject[item] = newAttribute
        
    hass.states.set(inputEntity, inputState, inputAttributesObject)




#Example Use:

# - alias: Garage Door Open
#   hide_entity: True
#   trigger:
#     platform: state
#     entity_id: sensor.garage_door
#     to: 'Open'
#   action:
#     - service: python_script.set_state
#       data_template:
#         entity_id: sensor.garage_door
#         icon: mdi:garage-open

# - alias: Garage Door Closed
#   hide_entity: True
#   trigger:
#     platform: state
#     entity_id: sensor.garage_door
#     to: 'Closed'
#   action:
#     - service: python_script.set_state
#       data_template:
#         entity_id: sensor.garage_door
#         icon: mdi:garage
