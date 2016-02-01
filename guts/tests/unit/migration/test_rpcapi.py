# Copyright (c) 2015 Aptira Pty Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Unit Tests for guts.migration.rpcapi
"""

import copy

import mock
from oslo_config import cfg

from guts import context
from guts.migration import rpcapi as migration_rpcapi
from guts import test


CONF = cfg.CONF


class MigrationRpcAPITestCase(test.TestCase):

    def setUp(self):
        super(MigrationRpcAPITestCase, self).setUp()

    def tearDown(self):
        super(MigrationRpcAPITestCase, self).tearDown()

    def _test_migration_api(self, method, rpc_method,
                            fanout=False, **kwargs):
        ctxt = context.RequestContext('fake_user', 'fake_project')
        rpcapi = migration_rpcapi.MigrationAPI()
        expected_retval = 'foo' if rpc_method == 'call' else None

        target = {
            "fanout": fanout,
            "version": kwargs.pop('version', rpcapi.RPC_API_VERSION)
        }

        expected_msg = copy.deepcopy(kwargs)

        self.fake_args = None
        self.fake_kwargs = None

        def _fake_prepare_method(*args, **kwds):
            for kwd in kwds:
                self.assertEqual(target[kwd], kwds[kwd])
            return rpcapi.client

        def _fake_rpc_method(*args, **kwargs):
            self.fake_args = args
            self.fake_kwargs = kwargs
            if expected_retval:
                return expected_retval

        with mock.patch.object(rpcapi.client, "prepare") as mock_prepared:
            mock_prepared.side_effect = _fake_prepare_method

            with mock.patch.object(rpcapi.client, rpc_method) as mock_method:
                mock_method.side_effect = _fake_rpc_method
                retval = getattr(rpcapi, method)(ctxt, **kwargs)
                self.assertEqual(expected_retval, retval)
                expected_args = [ctxt, method, expected_msg]
                for arg, expected_arg in zip(self.fake_args, expected_args):
                    self.assertEqual(expected_arg, arg)

                for kwarg, value in self.fake_kwargs.items():
                    self.assertEqual(expected_msg[kwarg], value)



    @mock.patch('oslo_messaging.RPCClient.can_send_version',
                return_value=True)
    def test_create_migration(self, can_send_version):
        self._test_migration_api('create_migration',
                                 rpc_method='call',
                                 migration_ref='fake_migration_ref',
                                 vm_uuid='fake_uuid',
                                 version='1.8')
        can_send_version.assert_called_once_with('1.8')


    @mock.patch('oslo_messaging.RPCClient.can_send_version',
                return_value=True)
    def test_fetch_vms(self, can_send_version):
        self._test_migration_api('fetch_vms',
                                 rpc_method='call',
                                 source_hypervisor_id='fake_source_hypervisor_id',
		                 version='1.8')
        can_send_version.assert_called_once_with('1.8')
