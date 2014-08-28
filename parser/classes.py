

class Document(object):
    '''Composite for data storage. Stores real data as content and other container as parts.

    @content    real data
    @parts      other containers
    '''
    def __init__(self):
        self.content = []
        self.parts = []

    def recent_doc(self):
        '''Returns lastly added part.'''
        if self.parts:
            return self.parts[-1]

    def recent_estate(self):
        '''Returns last part's lastly added part.'''
        if self.recent_doc() and isinstance(self.recent_doc(), Document):
            return self.recent_doc().recent_doc()

    def recent_obj(self):
        '''Return last part's last part's lastly added part.'''
        if self.recent_estate() and isinstance(self.recent_estate(), Document):
            return self.recent_estate().recent_doc()

    def line_split(self, sep, max = 1):
        '''Splits every line of the document by sep and acts recursively for any further Document objects.'''
        if isinstance(self.content, basestring):
            self.content = [part.strip() for part in self.content.split(sep, max)]
        else:
            for i in xrange(len(self.content)):
                self.content[i] = [part.strip() for part in self.content[i].split(sep, max)]

        if self.parts:
            if isinstance(self.parts[0], Document):
                for i in xrange(len(self.parts)):
                    self.parts[i] = self.parts[i].line_split(sep, max)
            else:
                for i in xrange(len(self.parts)):
                    self.parts[i] = [part.strip() for part in self.parts[i].split(sep, max)]

        return self

    def low_level_count(self):
        '''Find documents at the lowest level possible and sum their len(parts).'''
        count = 0
        if self.parts and len(self.parts):
            if isinstance(self.parts[0], Document):
                for document in self.parts:
                    count += document.low_level_count()
            else:
                count += len(self.parts)
        return count




class EntityExtractor(object):
    '''Extracts objects from a list of key-value pairs. It assumes that an object can have only one value for a
    distinct key. It either accepts a predefined key_set or computes a new one on invokation of the extract method.
    '''
    def __init__(self, key_set = set()):
        '''Initializes the extractor.

        @key_set    set    predefined key_set
        '''
        self.key_set = key_set

    def extract_keys(self, entries):
        '''Extracts keys from entries. Assumes that entry[0] in entries is a key.

        @entries    list    a list of key-value pairs
        '''
        key_set = set()
        for key, value in entries:
            key_set.add(key)
        return key_set

    def extract(self, entries, find_key_set = False):
        '''Extracts entities. Computes a key_set if it wasn't available or find_key_set == True.

        @entries    list    a list of key-value pairs
        '''
        if not entries or len(entries) == 1 and not isinstance(entries[0], (tuple, list)):
            return None

        if not self.key_set or find_key_set:
            self.key_set = self.extract_keys(entries)

        objects = []
        obj = dict()
        for key, value in entries:
            if not key or isinstance(key, basestring) and not key.strip():
                raise KeyError('Key evaluates to None (value is: %s)' %value)

            if key in self.key_set:
                if key in obj:
                    objects.append(obj)
                    obj = dict()
                obj[key] = value


        objects.append(obj)
        return objects

    def clear_key_set(self):
        '''Resets key_set.'''
        self.key_set = set()