import uuid

from django.db import models


class ModelBase(models.Model):

    CUSTOM_INITIAL_FIELDS = None

    class Meta:
        abstract = True

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._initial_values = dict(zip(field_names, values))
        if cls.CUSTOM_INITIAL_FIELDS:
            for field in cls.CUSTOM_INITIAL_FIELDS:
                instance._initial_values[field] = getattr(instance, field)
        return instance

    def refresh_initial_values(self, field_names=None):
        """Reset the "_initial_values" dict using current attributes
        """
        if not field_names:
            field_names = self._meta.fields
            if self.CUSTOM_INITIAL_FIELDS:
                field_names = field_names + tuple(self.CUSTOM_INITIAL_FIELDS)
        for field in self.CUSTOM_INITIAL_FIELDS:
            self._initial_values = {field: getattr(self, field)}

    def get_initial(self, field):
        """Return the initial value for a given field
        """
        return self._initial_values.get(field)

    def update(self, **kwargs) -> None:
        """Easily update and save a block of fields
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save(update_fields=list(kwargs.keys()))

    @classmethod
    def add_perm_lookup(cls) -> str:
        return f'{cls._meta.app_label}.add_{cls._meta.model_name}'

    @classmethod
    def change_perm_lookup(cls) -> str:
        return f'{cls._meta.app_label}.change_{cls._meta.model_name}'

    @classmethod
    def delete_perm_lookup(cls) -> str:
        return f'{cls._meta.app_label}.delete_{cls._meta.model_name}'

    @classmethod
    def view_perm_lookup(cls) -> str:
        return f'{cls._meta.app_label}.view_{cls._meta.model_name}'


class UUIDPrimaryKeyMixin(ModelBase):
    """Provides a primary key as a UUID field instead of auto-incrementing integer
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
