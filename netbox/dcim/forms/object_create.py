from django import forms

from dcim.models import *
from netbox.forms import NetBoxModelForm
from utilities.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableNameField
from . import models as model_forms

__all__ = (
    'ComponentCreateForm',
    'ConsolePortCreateForm',
    'ConsolePortTemplateCreateForm',
    'ConsoleServerPortCreateForm',
    'ConsoleServerPortTemplateCreateForm',
    'DeviceBayCreateForm',
    'DeviceBayTemplateCreateForm',
    'FrontPortCreateForm',
    'FrontPortTemplateCreateForm',
    'InterfaceCreateForm',
    'InterfaceTemplateCreateForm',
    'InventoryItemCreateForm',
    'InventoryItemTemplateCreateForm',
    'ModuleBayCreateForm',
    'ModuleBayTemplateCreateForm',
    'PowerOutletCreateForm',
    'PowerOutletTemplateCreateForm',
    'PowerPortCreateForm',
    'PowerPortTemplateCreateForm',
    'RearPortCreateForm',
    'RearPortTemplateCreateForm',
    'VirtualChassisCreateForm',
)


class ComponentCreateForm(forms.Form):
    """
    Subclass this form when facilitating the creation of one or more device component or component templates based on
    a name pattern.
    """
    name = ExpandableNameField()
    label = ExpandableNameField(
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )

    # TODO: Incorporate this validation
    # def clean(self):
    #     super().clean()
    #
    #     # Validate that all patterned fields generate an equal number of values
    #     patterned_fields = [
    #         field_name for field_name in self.fields if field_name.endswith('_pattern')
    #     ]
    #     pattern_count = len(self.cleaned_data['name_pattern'])
    #     for field_name in patterned_fields:
    #         value_count = len(self.cleaned_data[field_name])
    #         if self.cleaned_data[field_name] and value_count != pattern_count:
    #             raise forms.ValidationError({
    #                 field_name: f'The provided pattern specifies {value_count} values, but {pattern_count} are '
    #                             f'expected.'
    #             }, code='label_pattern_mismatch')


# class ModularComponentTemplateCreateForm(ComponentCreateForm):
#     """
#     Creation form for component templates that can be assigned to either a DeviceType *or* a ModuleType.
#     """
#     name = ExpandableNameField(
#         label='Name',
#         help_text="""
#                 Alphanumeric ranges are supported for bulk creation. Mixed cases and types within a single range
#                 are not supported. Example: <code>[ge,xe]-0/0/[0-9]</code>. {module} is accepted as a substitution for
#                 the module bay position.
#                 """
#     )


#
# Device component templates
#

class ConsolePortTemplateCreateForm(ComponentCreateForm, model_forms.ConsolePortTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.ConsolePortTemplateForm.Meta):
        exclude = ('name', 'label')


class ConsoleServerPortTemplateCreateForm(ComponentCreateForm, model_forms.ConsoleServerPortTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.ConsoleServerPortTemplateForm.Meta):
        exclude = ('name', 'label')


class PowerPortTemplateCreateForm(ComponentCreateForm, model_forms.PowerPortTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.PowerPortTemplateForm.Meta):
        exclude = ('name', 'label')


class PowerOutletTemplateCreateForm(ComponentCreateForm, model_forms.PowerOutletTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.PowerOutletTemplateForm.Meta):
        exclude = ('name', 'label')


class InterfaceTemplateCreateForm(ComponentCreateForm, model_forms.InterfaceTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.InterfaceTemplateForm.Meta):
        exclude = ('name', 'label')


class FrontPortTemplateCreateForm(ComponentCreateForm, model_forms.FrontPortTemplateForm):
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.FrontPortTemplateForm.Meta):
        exclude = ('name', 'label')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: This needs better validation
        if 'device_type' in self.initial or self.data.get('device_type'):
            parent = DeviceType.objects.get(
                pk=self.initial.get('device_type') or self.data.get('device_type')
            )
        elif 'module_type' in self.initial or self.data.get('module_type'):
            parent = ModuleType.objects.get(
                pk=self.initial.get('module_type') or self.data.get('module_type')
            )
        else:
            return

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in parent.frontporttemplates.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = parent.rearporttemplates.all()
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port_set'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class RearPortTemplateCreateForm(ComponentCreateForm, model_forms.RearPortTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.RearPortTemplateForm.Meta):
        exclude = ('name', 'label')


class DeviceBayTemplateCreateForm(ComponentCreateForm, model_forms.DeviceBayTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.DeviceBayTemplateForm.Meta):
        exclude = ('name', 'label')


class ModuleBayTemplateCreateForm(ComponentCreateForm, model_forms.ModuleBayTemplateForm):
    position = ExpandableNameField(
        label='Position',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.ModuleBayTemplateForm.Meta):
        exclude = ('name', 'label')


class InventoryItemTemplateCreateForm(ComponentCreateForm, model_forms.InventoryItemTemplateForm):
    field_order = ('device_type', 'name', 'label')

    class Meta(model_forms.InventoryItemTemplateForm.Meta):
        exclude = ('name', 'label')


#
# Device components
#

class ConsolePortCreateForm(ComponentCreateForm, model_forms.ConsolePortForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.ConsolePortForm.Meta):
        exclude = ('name', 'label')


class ConsoleServerPortCreateForm(ComponentCreateForm, model_forms.ConsoleServerPortForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.ConsoleServerPortForm.Meta):
        exclude = ('name', 'label')


class PowerPortCreateForm(ComponentCreateForm, model_forms.PowerPortForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.PowerPortForm.Meta):
        exclude = ('name', 'label')


class PowerOutletCreateForm(ComponentCreateForm, model_forms.PowerOutletForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.PowerOutletForm.Meta):
        exclude = ('name', 'label')


class InterfaceCreateForm(ComponentCreateForm, model_forms.InterfaceForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.InterfaceForm.Meta):
        exclude = ('name', 'label')


class FrontPortCreateForm(ComponentCreateForm, model_forms.FrontPortForm):
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.FrontPortForm.Meta):
        exclude = ('name', 'label')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )

        # Determine which rear port positions are occupied. These will be excluded from the list of available
        # mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in device.frontports.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = RearPort.objects.filter(device=device)
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port_set'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class RearPortCreateForm(ComponentCreateForm, model_forms.RearPortForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.RearPortForm.Meta):
        exclude = ('name', 'label')


class DeviceBayCreateForm(ComponentCreateForm, model_forms.DeviceBayForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.DeviceBayForm.Meta):
        exclude = ('name', 'label')


class ModuleBayCreateForm(ComponentCreateForm, model_forms.ModuleBayForm):
    position = ExpandableNameField(
        label='Position',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.ModuleBayForm.Meta):
        exclude = ('name', 'label')


class InventoryItemCreateForm(ComponentCreateForm, model_forms.InventoryItemForm):
    field_order = ('device', 'name', 'label')

    class Meta(model_forms.InventoryItemForm.Meta):
        exclude = ('name', 'label')


#
# Virtual chassis
#

class VirtualChassisCreateForm(NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    members = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
        }
    )
    initial_position = forms.IntegerField(
        initial=1,
        required=False,
        help_text='Position of the first member device. Increases by one for each additional member.'
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'region', 'site_group', 'site', 'rack', 'members', 'initial_position', 'tags',
        ]

    def clean(self):
        super().clean()

        if self.cleaned_data['members'] and self.cleaned_data['initial_position'] is None:
            raise forms.ValidationError({
                'initial_position': "A position must be specified for the first VC member."
            })

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Assign VC members
        if instance.pk and self.cleaned_data['members']:
            initial_position = self.cleaned_data.get('initial_position', 1)
            for i, member in enumerate(self.cleaned_data['members'], start=initial_position):
                member.virtual_chassis = instance
                member.vc_position = i
                member.save()

        return instance
