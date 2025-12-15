from rest_framework import serializers


class EnumCharField(serializers.CharField):
    def __init__(self, enum_class, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if value is not None:
            return str(value)
        return None

    def to_internal_value(self, data):
        if data is not None:
            try:
                return getattr(self.enum_class, data)
            except AttributeError:
                raise serializers.ValidationError(f"Invalid enum value: {data}")
        return None


class EmptySerializer(serializers.Serializer):
    pass


class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
