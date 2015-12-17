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

"""Built-in sources VM properties."""


from oslo_config import cfg
from oslo_log import log as logging

from guts import context
from guts import db
from guts import exception
from guts.i18n import _, _LE


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def get_all_vms(ctxt, inactive=0):
    """Get all non-deleted source vms.

    Pass true as argument if you want deleted sources returned also.

    """
    return db.vm_get_all(ctxt, inactive)


def get_vm(ctxt, id):
    """Retrieves single source by ID."""
    if id is None:
        msg = _("ID cannot be None")
        raise exception.InvalidSource(reason=msg)

    if ctxt is None:
        ctxt = context.get_admin_context()

    return db.vm_get(ctxt, id)


def get_vm_by_name(context, name):
    """Retrieves single source by name."""
    if name is None:
        msg = _("VM name cannot be None")
        raise exception.InvalidSource(reason=msg)

    return db.vm_get_by_name(context, name)


def vm_delete(context, id):
    """Deletes specified source VM."""

    return db.vm_delete(context, id)


def _create(ctxt, name, source_id, description=None):
    """Creates source types."""
    try:
        type_ref = db.vm_create(ctxt,
                                dict(name=name,
                                     source_id=source_id,
                                     description=description))
    except Exception:
        LOG.exception(_LE('DB error:'))
        raise exception.SourceTypeCreateFailed(name=name)

    return type_ref


def fetch_vms(context, source_id):
    """Fetch VMs from the source hypervisor."""
    # TODO(Alok): Fetch vms list and assign variable 'vms'
    # Example: vms = [{"id": "1234"}, {"id": "5678"}]

    vms = []
    for vm in vms:
        _create(context, vm['id'], source_id)
