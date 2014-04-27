class ProductType(type):
    def __new__(cls, name, bases, attrs):
        # Dict to store allowed attributes and their class
        attrs['_allowed_attrs'] = {}

        # Dict to store defined business rules
        attrs['_rules'] = {}

        # Add necessary methods
        def add_attribute(cls, attr_class):
            cls._allowed_attrs[attr_class.name] = attr_class
        attrs['add_attribute'] = classmethod(add_attribute)

        def remove_attribute(cls, attr_name):
            cls._allowed_attrs.pop(attr_name, None)
        attrs['remove_attribute'] = classmethod(remove_attribute)

        def get_attribute(self, attr_name):
            if attr_name not in self._allowed_attrs.keys():
                raise TypeError('`%s` is not an allowed attribute '
                                 'on `%s` class' % (attr_name, self.__name__))
            attr_instance = getattr(self, attr_name, None)
            if not attr_instance:
                raise ValueError('`%s` was not set on `%s` '
                                 'class' % (attr_name, self.__name__))
            return attr_instance.value
        attrs['get_attribute'] = get_attribute

        def set_attribute(self, attr_name, value):
            if attr_name not in self._allowed_attrs.keys():
                raise TypeError('`%s` is not an allowed attribute '
                                 'on `%s` class' % (attr_name, self.__name__))
            attr_class = self._allowed_attrs[attr_name]
            setattr(self, attr_name, attr_class(value))
        attrs['set_attribute'] = set_attribute

        def add_rule(cls, name, rule):
            if not rule.validate(cls):
                raise TypeError('Unavailable attributes used when defining '
                                'rule `%s`' % name)
            cls._rules[name] = rule
        attrs['add_rule'] = classmethod(add_rule)

        def apply_rule(self, name):
            if name not in self._rules:
                raise TypeError('`%s` is not a rule defined on `%s` class' % (
                                name, self.__name__))
            return self._rules[name].do(self)
        attrs['apply_rule'] = apply_rule

        return super(ProductType, cls).__new__(cls, name, bases, attrs)


class AttributeType(type):
    def __new__(cls, name, bases, attrs):
        # Add necessary methods
        def __init__(self, value):
            if not isinstance(value, self.type):
                raise ValueError('Value `%s` supplied for attribute `%s` must'
                                 ' be of type `%s`' % (value, self.name,
                                 self.type))
            self.value = value
        attrs['__init__'] = __init__

        return super(AttributeType, cls).__new__(cls, name, bases, attrs)


class Rule(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def validate(self, cls):
        """
        Checks whether rule can be applied on given class
        """

        def validate_a():
            if isinstance(self.a, Rule):
                return self.a.validate(cls)
            elif type(self.a) == AttributeType:
                return self.a in cls._allowed_attrs.values()
            return True

        def validate_b():
            if isinstance(self.b, Rule):
                return self.b.validate(cls)
            elif type(self.b) == AttributeType:
                return self.b in cls._allowed_attrs.values()
            return True

        return validate_a() and validate_b()

    def _get_values(self, instance):
        """
        Retrieves values of rule, computed upon given instance
        """

        def get_a():
            if isinstance(self.a, Rule):
                return self.a.do(instance)
            elif type(self.a) == AttributeType:
                return instance.get_attribute(self.a.name)
            return self.a

        def get_b():
            if isinstance(self.b, Rule):
                return self.b.do(instance)
            elif type(self.b) == AttributeType:
                return instance.get_attribute(self.b.name)
            return self.b

        return get_a(), get_b()

    def do(self, instance):
        """
        Apply the rule on the given instance
        """

        raise NotImplemented('`do()` method must be implemented on all'
                             'subclasses of `Rule`')


class Add(Rule):
    def do(self, instance):
        a, b = self._get_values(instance)
        return a+b


class Subtract(Rule):
    def do(self, instance):
        a, b = self._get_values(instance)
        return a-b


class Multiply(Rule):
    def do(self, instance):
        a, b = self._get_values(instance)
        return a*b


def create_product(cls_name, cls_base=object):
    """
    Return a product class
    """

    return ProductType(cls_name, (cls_base,), {})


def create_attribute(cls_name, attr_name, attr_type):
    """
    Return an attribute class
    """

    return AttributeType(cls_name, (), {'name': attr_name, 'type': attr_type})


if __name__ == '__main__':
    # Dynamically create Product classes
    Insurance = create_product('Insurance')
    HouseInsurance = create_product('HouseInsurance')
    CarInsurance = create_product('CarInsurance')

    # Dynamically create Attribute classes
    ConstructionYear = create_attribute(
        'ConstructionYear', 'construction_year', int)
    Age = create_attribute('Age', 'age', int)
    Zone = create_attribute('Zone', 'zone', str)
    Manufacturer = create_attribute('Manufacturer', 'manufacturer', str)
    EnginePower = create_attribute('EnginePower', 'engine_power', float)

    # Add attributes to created product classes
    HouseInsurance.add_attribute(ConstructionYear)
    HouseInsurance.add_attribute(Age)
    HouseInsurance.add_attribute(Zone)
    CarInsurance.add_attribute(Manufacturer)
    CarInsurance.add_attribute(Age)
    CarInsurance.add_attribute(EnginePower)

    # Add rules to created product classes
    CarInsurance.add_rule('price',
        Add(Subtract(Multiply(1000, Age), Multiply(10, Age)), Multiply(5, EnginePower)))

    # Create some products and play with attributes and rules
    johns_house_insurance = HouseInsurance()
    johns_house_insurance.set_attribute('construction_year', 1990)

    janes_car_insurance = CarInsurance()
    janes_car_insurance.set_attribute('age', 20)
    janes_car_insurance.set_attribute('manufacturer', 'BMW')
    janes_car_insurance.set_attribute('engine_power', 100.5)

