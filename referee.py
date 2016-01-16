# referee.py, gives referee status to a player with the password and enables the following console commands:
#########################################################################
# ref help             - Lists all referee commands
# ref allready         - Force all players to be 'ready' and start the match.
# ref abort            - Abandon the current game and return to warmup.
# ref pause            - Pause the current match indefinitely.
# ref unpause          - Unpause the current match.
# ref lock <r/b>       - Stop players from joining the team.
# ref unlock <r/b>     - Allow players to join the team.
# ref speclock         - Disable freecam spectator mode for dead players.
# ref specunlock       - Enable freecam spectator mode for dead players.
# ref alltalk <0/1>    - Disable/enable communication between teams.
# ref put <id> [r/b/s] - Move a player to red/blue/spectators.
# ref mute <id>        - Mute a player.
# ref unmute <id>      - Unmute a player.
#########################################################################
# The commands can be input via the console, for example: /ref allready, or through the chat: !ref allready
# The only exceptions being "/ref pass" and "/ref help", which are console-only.
# To get referee status, type /ref pass "password" (without quotation marks).
# The initial password is set on line 34 of this file ("CHANGE_ME"), change it to something unique.
# You can change the password in-game/between matches with !refpass "password" (without quotation marks), which will also reset all current referees.
# To show the currently set password, type !getrefpass.

import minqlx
import re

class referee(minqlx.Plugin):
    def __init__(self):
        self.add_hook("client_command", self.handle_client_command)
        self.add_command("refpass", self.cmd_refpass, 5, usage="<password> (no spaces)")
        self.add_command("getrefpass", self.cmd_getrefpass, 5)
        self.add_command("ref", self.cmd_ref)

        self.password = "CHANGE_ME"
        self.referees = []

    def handle_client_command(self, caller, cmd):
        if cmd == "ref pass " + self.password:
            self.referees.append(caller.steam_id)
            caller.tell("^5Password correct, referee status granted. /ref help to list all commands.")

        elif cmd.lower() == "ref help" and caller.steam_id in self.referees:
            caller.tell("^3Use /ref or !ref cmd <arg>:\n"
                        "^5ref allready               ^3- ^7Force all players to be 'ready' and start the match.\n"
                        "^5ref abort                  ^3- ^7Abandon the current game and return to warmup.\n"
                        "^5ref pause                  ^3- ^7Pause the current match indefinitely.\n"
                        "^5ref unpause                ^3- ^7Unpause the current match.\n"
                        "^5ref lock <r/b>             ^3- ^7Stop players from joining the team. (both if no arg given)\n"
                        "^5ref unlock <r/b>           ^3- ^7Allow players to join the team. (both if no arg given)\n"
                        "^5ref speclock               ^3- ^7Disable freecam spectator mode for dead players.\n"
                        "^5ref specunlock             ^3- ^7Enable freecam spectator mode for dead players.\n"
                        "^5ref alltalk <0/1>          ^3- ^7Disable/enable communication between teams.\n"
                        "^5ref put <id> [r/b/s]       ^3- ^7Move a player to red/blue/spectators.\n"
                        "^5ref mute <id>              ^3- ^7Mute a player.\n"
                        "^5ref unmute <id>            ^3- ^7Unmute a player.")

        elif cmd.lower() == "ref allready" and caller.steam_id in self.referees:
            if self.game.state == "warmup":
                self.msg("^6Referee ^7" + str(caller) + " readied the teams.")
                self.allready()
            else:
                caller.tell("The game is already in progress.")

        elif cmd.lower() == "ref abort" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(caller) + " aborted the match.")
                self.abort()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref pause" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(caller) + " paused the match.")
                self.pause()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref unpause" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(caller) + " unpaused the match.")
                self.unpause()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref lock" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " locked the teams.")
            self.lock()

        elif (cmd.lower() == "ref lock r" or cmd.lower() == "ref lock red") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " locked the ^1red ^7team.")
            self.lock("red")

        elif (cmd.lower() == "ref lock b" or cmd.lower() == "ref lock blue") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " locked the ^4blue ^7team.")
            self.lock("blue")

        elif cmd.lower() == "ref unlock" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " unlocked the teams.")
            self.unlock()

        elif (cmd.lower() == "ref unlock r" or cmd.lower() == "ref unlock red") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " unlocked the ^1red ^7team.")
            self.unlock("red")

        elif (cmd.lower() == "ref unlock b" or cmd.lower() == "ref unlock blue") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " unlocked the ^4blue ^7team.")
            self.unlock("blue")

        elif cmd.lower() == "ref speclock" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " disabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "0")

        elif cmd.lower() == "ref specunlock" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " enabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "1")

        elif cmd.lower() == "ref alltalk 0" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " disabled communication between teams.")
            self.set_cvar("g_allTalk", "0")

        elif cmd.lower() == "ref alltalk 1" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " enabled communication between teams.")
            self.set_cvar("g_allTalk", "1")

        elif re.search(r"ref put \d+ s", cmd.lower()) and caller.steam_id in self.referees:
            id = re.search(r"\d+", cmd.lower()).group()
            if self.player(int(id)):
                self.msg("^6Referee ^7" + str(caller) + " moved " + self.player(int(id)).name + " to the spectators.")
                self.player(int(id)).put("spectator")
            else:
                caller.tell("No player with ID: ^2" + id + "^7.")

        elif re.search(r"ref mute \d+", cmd.lower()) and caller.steam_id in self.referees:
            id = re.search(r"\d+", cmd.lower()).group()
            if self.player(int(id)):
                self.msg("^6Referee ^7" + str(caller) + " muted " + self.player(int(id)).name + ".")
                self.player(int(id)).mute()
            else:
                caller.tell("No player with ID: ^2" + id + "^7.")

        elif re.search(r"ref unmute \d+", cmd.lower()) and caller.steam_id in self.referees:
            id = re.search(r"\d+", cmd.lower()).group()
            if self.player(int(id)):
                self.msg("^6Referee ^7" + str(caller) + " unmuted " + self.player(int(id)).name + ".")
                self.player(int(id)).unmute()
            else:
                caller.tell("No player with ID: ^2" + id + "^7.")

    def cmd_ref(self, player, msg, channel):
        if msg[1].lower() == "allready" and player.steam_id in self.referees:
            if self.game.state == "warmup":
                self.msg("^6Referee ^7" + str(player) + " readied the teams.")
                self.allready()
            else:
                player.tell("The game is already in progress.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "abort" and player.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(player) + " aborted the match.")
                self.abort()
            else:
                player.tell("The match hasn't started yet.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "pause" and player.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(player) + " paused the match.")
                self.pause()
            else:
                player.tell("The match hasn't started yet.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unpause" and player.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(player) + " unpaused the match.")
                self.unpause()
            else:
                player.tell("The match hasn't started yet.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "lock" and len(msg) < 3 and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " locked the teams.")
            self.lock()
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "lock" and (msg[2].lower() == "r" or msg[2].lower() == "red") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " locked the ^1red ^7team.")
            self.lock("red")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "lock" and (msg[2].lower() == "b" or msg[2].lower() == "blue") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " locked the ^4blue ^7teams")
            self.lock("blue")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unlock" and len(msg) < 3 and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " unlocked the teams.")
            self.unlock()
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unlock" and (msg[2].lower() == "r" or msg[2].lower() == "red") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " unlocked the ^1red ^7team.")
            self.unlock("red")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unlock" and (msg[2].lower() == "b" or msg[2].lower() == "blue") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " unlocked the ^4blue ^7team.")
            self.unlock("blue")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "speclock" and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " disabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "0")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "specunlock" and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " enabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "0")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "alltalk" and (msg[2] == "0" or msg[2].lower() == "off") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " disabled communication between teams.")
            self.set_cvar("g_allTalk", "0")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "alltalk" and (msg[2] == "1" or msg[2].lower() == "on") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " enabled communication between teams.")
            self.set_cvar("g_allTalk", "1")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "put" and (0 <= int(msg[2]) < 64) and (msg[3] == "s" or msg[3] == "spec" or msg[3] == "spectator") and player.steam_id in self.referees:
            if self.player(int(msg[2])):
                self.msg("^6Referee ^7" + str(player) + " moved " + self.player(int(msg[2])).name + " to the spectators.")
                self.player(int(msg[2])).put("spectator")
            else:
                player.tell("No player with ID: ^2" + msg[2] + "^7.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "mute" and (0 <= int(msg[2]) < 64) and player.steam_id in self.referees:
            if self.player(int(msg[2])):
                self.msg("^6Referee ^7" + str(player) + " muted " + self.player(int(msg[2])).name + ".")
                self.player(int(msg[2])).mute()
            else:
                player.tell("No player with ID: ^2" + msg[2] + "^7.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unmute" and (0 <= int(msg[2]) < 64) and player.steam_id in self.referees:
            if self.player(int(msg[2])):
                self.msg("^6Referee ^7" + str(player) + " unmuted " + self.player(int(msg[2])).name + ".")
                self.player(int(msg[2])).unmute()
            else:
                player.tell("No player with ID: ^2" + msg[2] + "^7.")
            return minqlx.RET_STOP_ALL

        else:
            return minqlx.RET_STOP_ALL

    def cmd_refpass(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        self.password = str(msg[1])
        self.referees = []
        player.tell("Referee password changed to: ^2" + str(msg[1]) +"^7; referee list reset.")
        return minqlx.RET_STOP_ALL

    def cmd_getrefpass(self, player, msg, channel):
        player.tell("Referee password is: ^2" + self.password +"^7.")
        return minqlx.RET_STOP_ALL
