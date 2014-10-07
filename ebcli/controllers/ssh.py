# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings
from ebcli.core import fileoperations, operations, io
from ebcli.lib import utils


class SSHController(AbstractBaseController):
    class Meta:
        label = 'ssh'
        description = strings['ssh.info']
        usage = AbstractBaseController.Meta.usage.replace('{cmd}', label)
        arguments = AbstractBaseController.Meta.arguments + [
            (['-n', '--number'], dict(help='Number of instance in list',
                                      type=int)),
            (['-i', '--instance'], dict(help='Instance id')),
        ]

    def do_command(self):
        app_name = self.get_app_name()
        region = self.get_region()
        number = self.app.pargs.number
        env_name = self.get_env_name()
        instance = self.app.pargs.instance

        if instance and number:
            io.log_error('Please provide either instance or number, not both')
            return

        if instance:
            operations.ssh_into_instance(instance, region)
        else:
            instances = operations.get_instance_ids(app_name, env_name, region)
            if number is not None:
                if number > len(instances) or number < 1:
                    io.log_error('Invalid index number (' + str(number) +
                                 ') for environment with ' +
                                 str(len(instances)) + ' instances')
                    return
                else:
                    instance = instances[number - 1]

            elif len(instances) == 1:
                instance = instances[0]
            else:
                io.echo()
                io.echo('Select an instance to ssh into')
                instance = utils.prompt_for_item_in_list(instances)

            operations.ssh_into_instance(instance, region)

    def complete_command(self, commands):
        if not self.complete_region(commands):
            # Environment names are the second positional argument in this
            ## controller, so we only complete if its the second
            if len(commands) == 2 and commands[-1].startswith('-'):
                region = fileoperations.get_default_region()
                app_name = fileoperations.get_application_name()
                io.echo(*operations.get_env_names(app_name, region))