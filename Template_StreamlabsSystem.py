#---------------------------
#   Import Libraries
#---------------------------
import ConfigParser
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

# import clr
# clr.AddReference("IronPython.SQLite.dll")
# clr.AddReference("IronPython.Modules.dll")

#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Rocksmith playtime"
Website = "https://www.streamlabs.com"
Description = "!rsplaytime will display your current playtime in Rocksmith"
Creator = "Bairei"
Version = "0.0.0.1"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()

#---------------------------
#   Define File Variables
#---------------------------

ROCKSMITH_APP_ID = 221680

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    ScriptSettings = MySettings(SettingsFile)
    ScriptSettings.Response = "Overwritten pong! ^_^"
    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Command and Parent.IsOnUserCooldown(ScriptName,ScriptSettings.Command,data.User):
        Parent.SendStreamMessage("This command is on cooldown for {0} more seconds.".format(str(Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Command, data.User))))

    #   Check if the propper command is used, the command is not on cooldown and the user has permission to use the command
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Command and not Parent.IsOnUserCooldown(ScriptName,ScriptSettings.Command,data.User) and Parent.HasPermission(data.User,ScriptSettings.Permission,ScriptSettings.Info):
        Parent.BroadcastWsEvent("EVENT_MINE","{'show':false}")

        # get SteamAPI key
        config_path = os.path.join(os.path.dirname(__file__), "api.properties")
        Parent.Log(ScriptName, config_path)
        if os.path.isfile(config_path):
            config = ConfigParser.RawConfigParser()
            config.read(config_path)
            if config.get("global", "steam.apikey") is None:
                Parent.Log(ScriptName, "No SteamAPI key found in properties")
                Parent.SendStreamMessage("Error while preparing data for request. O.o")
                # Put the command on cooldown
                Parent.AddUserCooldown(ScriptName, ScriptSettings.Command, data.User, ScriptSettings.Cooldown)
                return
        else:
            Parent.Log(ScriptName, "No api.properties file was found")
            Parent.SendStreamMessage("Error while preparing data for request. O.o")
            # Put the command on cooldown
            Parent.AddUserCooldown(ScriptName, ScriptSettings.Command, data.User, ScriptSettings.Cooldown)
            return

        # get response from SteamAPI
        api_key = "key={0}".format(config.get("global", "steam.apikey"))
        steam_id = "steamid=" + ScriptSettings.UserId
        app_ids_filter = 'appids_filter[0]=' + str(ROCKSMITH_APP_ID)
        response_format = "format=json"
        include_appinfo = "include_appinfo=1"
        params = '?' + '&'.join([api_key, steam_id, response_format, app_ids_filter, include_appinfo])
        url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/{0}".format(params)
        response = Parent.GetRequest(url, {})
        Parent.Log(ScriptName, "GET: {0}".format(url))
        json_obj = json.loads(response)

        if json_obj['status'] == 200:
            Parent.Log(ScriptName, json_obj['response'])
            content = json.loads(json_obj['response'])
            Parent.Log(ScriptName, str(content))
            api_response = content['response']
            try:
                if api_response['game_count'] == 1 and api_response['games'][0]['appid'] == ROCKSMITH_APP_ID:
                    rocksmith_data = api_response['games'][0]
                    name = rocksmith_data['name']
                    hours = '{:02d} hours and {:02d} minutes'.format(*divmod(rocksmith_data['playtime_forever'], 60))
                    Parent.Log(ScriptName, 'Total playtime in {0}: {1}'.format(name, hours))
                    Parent.SendStreamMessage('Total playtime in {0}: {1}'.format(name, hours))
                elif api_response['game_count'] == 0:
                    Parent.Log(ScriptName, 'Response from SteamAPI includes no games for given id! {0}'.format(ROCKSMITH_APP_ID))
                    Parent.SendStreamMessage("This user doesn't own Rocksmith :(")
                elif api_response['game_count'] > 0:
                    Parent.Log(ScriptName, 'Response from SteamAPI includes no games for given id! {0}'.format(ROCKSMITH_APP_ID))
                    Parent.SendStreamMessage("Unexpected error while fetching user data. O.o")
            except KeyError:
                Parent.Log(ScriptName, 'Unable to found Rocksmith in response, check if {0} is a correct id.'.format(ScriptSettings.UserId))
                Parent.SendStreamMessage("Unexpected error while fetching user data. O.o")
        else:
            Parent.Log(ScriptName, str(json_obj))
            Parent.SendStreamMessage("Response received with status {0}.".format(json_obj['status']))

        # Parent.SendStreamMessage(ScriptSettings.Response)    # Send your message to chat
        Parent.AddUserCooldown(ScriptName,ScriptSettings.Command,data.User,ScriptSettings.Cooldown)  # Put the command on cooldown

    
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    
    if "$myparameter" in parseString:
        return parseString.replace("$myparameter","I am a cat!")
    
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.__dict__ = json.loads(jsonData)
    ScriptSettings.Save(SettingsFile)
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return
