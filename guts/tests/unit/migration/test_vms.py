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
Unit Tests for guts.migration.vms
"""

from guts import context
from guts import db
from guts import exception
from guts import test
from guts.migration import vms

class VMsTestCase(test.TestCase):
    def setUp(self):
        super(VMsTestCase, self).setUp()
        self.user_id = 'fake_user'
        self.project_id = 'fake_project'
        self.context = context.RequestContext(self.user_id,
                                              self.project_id,
                                              is_admin=True)
        self.calls = []

    def _stub_vms(self):
        def fake_vm_get_all(context, inactive):
            self.calls.append('vm_get_all')
            if not inactive:
                return dict(
                    fake_vm_active={'id': 1,
                                    'name': 'fake_vm_active',
                                    'description': 'non-deleted vm',
                                    },
                    )
            else:
                return dict(
                    fake_vm_inactive={'id': 1,
                                      'name': 'fake_vm_inactive',
                                      'description': 'non-deleted vm',
                                      },
                    )

        def fake_vm_get(context, id):
            self.calls.append('vm_get')
            self.assertEqual(id, 'test_project')
            return dict(
                to_be_finished='',
                )

        def fake_vm_get_by_name(context, name):
            self.calls.append('vm_get_by_name')
            self.assertEqual(name, 'test_project')
            return dict(
                to_be_finished='',
                )

        def fake_vm_delete(context, id):
            self.calls.append('vm_delete')
            self.assertEqual(id, 'test_project')
            return dict(
                to_be_finished='',
                )

        self.stubs.Set(db, 'vm_get_all', fake_vm_get_all)
        self.stubs.Set(db, 'vm_get', fake_vm_get)
        #self.stubs.Set(db, 'vm_get_by_name', fake_vm_get_by_name)
        self.stubs.Set(db, 'vm_delete', fake_vm_delete)

    def test_get_all_vms_active(self):
        self._stub_vms()
        result = db.vm_get_all(self.context, inactive=False)
        self.assertEqual(self.calls, ['vm_get_all',])
        self.assertEqual(result, {
                'fake_vm_active': {
                    'id': 1,
                    'name': 'fake_vm_active',
                    'description': 'non-deleted vm',
                    },
                })

    def test_get_all_vms_inactive(self):
        self._stub_vms()
        result = db.vm_get_all(self.context, inactive=True)
        self.assertEqual(self.calls, ['vm_get_all',])
        self.assertEqual(result, {
                'fake_vm_inactive': {
                    'id': 1,
                    'name': 'fake_vm_inactive',
                    'description': 'non-deleted vm',
                    },
                })

    def test_get_vm_no_id(self):
        self.assertRaises(exception.InvalidSource,
                          vms.get_vm,
                          self.context)

    def test_get_vm_not_found(self):
        self._stub_vms()
        result = db.vm_get_all(self.context, id=1)

    """

    def test_get_vm_by_name(self):


    def test_vm_delete(self):


    def test_fetch_vms(self):

   """