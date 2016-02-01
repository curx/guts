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

import mock

from guts.api.v1 import types
from guts import test
from guts.migration import types as m_types


class TypesControllerTest(test.TestCase):
    def setUp(self):
        super(TypesControllerTest, self).setUp()

    def test_types_index(self):
        controller = types.TypesController(mock.MagicMock)
        stypes = {'type_1': {'id': 1, 'name': 'type1',
                             'driver_class_path': 'type_driver1',
                             'description': 'description1'},
                  'type_2': {'id': 2, 'name': 'type2',
                             'driver_class_path': 'type_driver2',
                             'description': 'description2'}}
        with mock.patch.object(m_types, 'get_all_types',
                               return_value=stypes) as mock_get_all_types:
            req = mock.MagicMock()
            expected = {'source_types': [{'description': 'description2',
                                          'driver': 'type_driver2',
                                          'id': 2,
                                          'name': 'type2'},
                                         {'description': 'description1',
                                          'driver': 'type_driver1',
                                          'id': 1,
                                          'name': 'type1'}]}
            result = controller.index(req)
            self.assertEqual(expected, result)

    def test_types_index_no_data(self):
        controller = types.TypesController(mock.MagicMock)
        stypes = {}
        with mock.patch.object(m_types, 'get_all_types',
                               return_value = stypes) as mock_get_all_types:
            req = mock.MagicMock()
            expected = {'source_types': []}
            result = controller.index(req)
            self.assertEqual(expected, result)

    def test_types_show(self):
        controller = types.TypesController(mock.MagicMock)
        stypes = {'description': 'description1',
                  'driver_class_path': 'type_driver1',
                  'id': '1', 'name': 'type1'}
        with mock.patch.object(m_types, 'get_source_type',
                               return_value=stypes) as mock_get_source_type:
            req = mock.MagicMock()
            expected = {'source_type': {'description': 'description1',
                                        'driver': 'type_driver1', 'id': '1',
                                        'name': 'type1'}}
            result = controller.show(req, stypes.get('id'))
            self.assertEqual(expected, result)

    def test_types_create(self):
        controller = types.TypesController(mock.MagicMock)
        body = {'source_type': {'driver': 'type_driver1', 'name': 'type1',
                'description': 'description1'}}
        with mock.patch.object(m_types, 'create',
                               return_value=body) as mock_create:
            get_source_type_return = {'driver_class_path': 'type_driver1',
                                      'name': 'type1',
                                      'description': 'description1',
                                      'id': '1'}
            with mock.patch.object(m_types, 'get_source_type_by_name',
                                   return_value=get_source_type_return) as \
                    mock_get_source_type_by_name:
                types.validate_type_driver = mock.MagicMock()
                req = mock.MagicMock()
                expected = {'source_type': {'description': 'description1',
                                            'driver': 'type_driver1',
                                            'id': '1',
                                            'name': 'type1'}}
                result = controller.create(req, body)
                self.assertEqual(expected, result)

    def test_types_delete(self):
        controller = types.TypesController(mock.MagicMock)
        with mock.patch.object(m_types, 'source_type_delete',
                               return_value=None) as mock_source_type_delete:
            req = mock.MagicMock()
            result = controller.delete(req, 1)
            self.assertEqual(202, result.status_int)
