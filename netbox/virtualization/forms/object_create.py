from utilities.forms import ExpandableNameField
from .models import VMInterfaceForm

__all__ = (
    'VMInterfaceCreateForm',
)


class VMInterfaceCreateForm(VMInterfaceForm):
    name = ExpandableNameField()
    replication_fields = ('name',)
