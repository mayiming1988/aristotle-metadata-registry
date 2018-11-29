class CurrentProfileDefault:
    def set_context(self, serializer_field):
        self.profile = serializer_field.context['request'].user.profile

    def __call__(self):
        return self.profile

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)
