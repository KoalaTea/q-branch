import threading
import time
from slack import SlackBot
from arsenal_pyclient.arsenal import target
from arsenal_pyclient.arsenal import action

#TODO config

class QBot(SlackBot):
    watch_timeout = 3

    def commands(self, command, channel):
        if command.startswith('arsenal '):
            # remove arsenal from the command and strip out extra spaces
            command = ' '.join(command.split()[1:]).strip()
            self._logger.info('running arsenal command: {}'.format(command))
            return self.handle_arsenal_command(command, channel)

    def handle_arsenal_command(self, command, channel):
        command_lower = command.lower()

        if command_lower.startswith('listtargets'):
            self._logger.debug('running list targets')
            answers = []
            targets = target.ListTargets()
            for t in targets['targets']:
                sessions = [s for s in t['sessions'] if s['status'] == 'active']
                answers.append('*{}* has *{}* active sessions'.format(t['name'], len(sessions)))
                for interface in t['interfaces'].keys():
                    answers.append('{}'.format(t['interfaces'][interface]))
            return '{}'.format('\n'.join(answers))

        elif command_lower.startswith('createaction'):
            command_list = command.split()
            if len(command_list) > 2:
                target_name = command_list[1]
                return self.create_action(target_name)
            return 'bad command for CreateAction {}'.format(command) #TODO log how to make command?

        elif command_lower.startswith('getaction'):
            command_list = command.split()
            if len(command_list) == 2:
                return self.get_action(command_list[1])
            return 'bad command for GetAction {}'.format(command)

        elif command_lower.startswith('renametarget'):
            command_list = command.split()
            if len(command_list) == 3:
                data = target.UpdateTargetByName(command_list[1], {'new_name': command_list[2]})
                if data['status'] != 200:
                    return 'rename *{} errored* with *{}*'.format(command_list[1], data['message'])
                return 'renamed *{}* to *{}*'.format(command_list[1], command_list[2])

        elif command_lower.startswith('help'):
            lines = []
            lines.append('ListTargets')
            lines.append('CreateAction <target_name> exec <command>')
            lines.append('GetAction <action_id>')
            lines.append('RenameTarger <old_name> <new_name>')
            return '\n'.join(lines)

    def create_action(self):
        self._logger.debug('getting target {}'.format(target_name))
        try:
            t = target.GetTargetByName(target_name)
            self._logger.debug('found target {}'.format(t))
        except:
            self._logger.debug('target {} does not exist'.format(target_name))
            return 'target {} does not exist'.format(target_name)
        if t['target']['name'] is not None:
            cmd = ' '.join(command_list[2:])
            data = action.CreateAction(t['target']['name'], cmd)
            action_id = data['action']['action_id']
            msg = '*{}* created on target *{}* for command *{}*'.format(action_id,
                                                                        target_name, cmd)
            threading.Thread(target=self.watch_for_action,
                             args=(t, action_id, channel,)).start()
            return msg
            #self.send_message(channel, msg)


    def get_action(self, action_id):
        try:
            data = action.GetAction(action_id)
        except:
            return 'action {} does not exist'.format(action_id)
        a = data['action']
        response = a['response']
        if response:
            if response['error']:
                return '{} *{}* on *{}*\n*errored* with *{}*'.format(a['action_id'],
                                                                     a['actionString'],
                                                                     a['target_name'],
                                                                     response['stderr'])
            else:
                lines = []
                lines.append('{} *{}* on *{}* has output on'.format(a['action_id'],
                                                                    a['actionString'],
                                                                    a['target_name']))
                lines.append('```{}```'.format(response['stdout']))
                return '\n'.join(lines)
        return 'command on *{}* has status *{}*'.format(a['target_name'], a['status'])


    def rename_target(self, old_name, new_name):
        pass

    def watch_for_action(self, target_json, action_id, channel):
        trys = 0
        interval = target_json['interval']
        while trys <= watch_timeout:
            a = action.GetAction(action_id)
            if a is not None:
                if a['status'] != 'sent':
                    pass
