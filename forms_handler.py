import logging

class _Input:
    def __init__(self, value, errors=None):
        self.value = value
        self.errors = errors


class FormHandler:
    '''Abstract class defining methods neccessary to validate forms. \
        form input represented by the Input class. where Input.value is the input value returned from form, errors messages must be set by input validators.
        subclasses mut call super constructor
    '''
    def __init__(self):
        self.is_valid = False
    
    @property
    def input_args(self):
        ''' this method return valid (modified if there ) from input as a dict object.\
            eg. 
            retutn { 'input-name': Input.value.upper() }
            note: subclass might check is_valid attribute before returning from this method.
        '''
        # TODO  
        # 
        pass
    

    def validate(self):
        '''This method should check all inputs validators, Return True if all inputss are valid , False other wise, note: invalid failds should be reseted to empty\
           update self.valid then return 
        '''
        return False    



class RestaurantFormHandler(FormHandler):
    def __init__(self, name=None):
        super().__init__()
        self.name = _Input(name)

    @property
    def input_arg(self):
        return {
            'name': self.name.value
        }

    def _validate_name(self):
        if self.name.value and len(self.name.value) > 2:
            logging.info('restaurant name is valid')
            return True
        else:
            self.name.value = ""
            self.name.errors = 'Enter a restaurant name. ( 3 letters minimum )'
            logging.info('invalid restaurant name. value:{}'.format(self.name.value))
            return False
    
    def validate(self):
        self.is_valid = self._validate_name()
        return self.is_valid

class ItemFormHandler(FormHandler):
    '''Handle Menu Item form data, provid validation with appropiate error message for invalid fields.\
        pass menu item argument then call validate.
        '''
    def __init__(self, name='', description='', course='', price='', **kwargs):
        super().__init__()
        # attributes represents input fields
        # Input object hold value and errors of an input field form
        # the first part of the tupel is the field value 
        # the second is field error messages if any
        self.name = _Input(name)
        self.description = _Input(description)
        self.course = _Input(course)
        self.price = _Input(price)

    @property
    def input_args(self):
        ''' this method return modified inputs arguments if any as a dict object'''
        
        return {
            'name': self.name.value,
            'description': self.description.value,
            'course': self.course.value,
            'price': self.price.value
        }

    # helper methods
    # invalid inputs are re-seted
    def _validate_name(self):
        if self.name.value and len(self.name.value) > 2:
            logging.info('name input is valid')
            return True
        else:
            self.name.errors = "Enter an item name. ( 3 letters is minimum )"
            logging.info('name input is invalid less than 3 letters or None: value ={}'
                            .format(self.name.value))
            self.name.value = ""
            
            return False
    
    def _validate_course(self):
        if self.course.value and len(self.course.value) > 2:   
            logging.info('course input is valid')
            return True
        else: 
            self.course.errors = "Enter a valid course. ( 3 letters miimum )" 
            logging.info('course input is invalid None or less than 3 letters Value:{}'.format(self.course.value))
            self.course.value = ""
            return False

    def _validate_description(self):
        if self.description.value and len(self.description.value) > 10:
            logging.info('description input is valid')
            return True  
        else:
            self.description.errors = "Enter a valid description. ( 15 letters minimum )" 
            logging.info('descrition input is invalid, None or less than 15 letters, value:{}'.format(self.description.value))
            self.description.value = ""
            return False

    def _validate_price(self):
        if self.price.value and self.price.value.isdigit():
            # bad idea
            # if '$' not in self.price.value:
                # self.price.value = "$" + self.price.value
            return True
        else:
            self.price.errors = "Enter a valid price ( eg. 15 )"
            logging.info('price input is invalid, None or not digits, value:{}'.format(self.price.value))
            self.price.value = ""
            return False
    

    def validate(self):
        "Return True if all fields are valid , False other wise, note: invalid failds are reseted to empty"
        # using and will prvent callling all methods when one fail
        self.is_valid= self._validate_name() & self._validate_description() \
                    & self._validate_course() & self._validate_price()
        return self.is_valid     