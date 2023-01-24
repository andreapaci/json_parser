# Class used to store the tuple (key, accepted_values). Used in json_parse library to check whether a json contains certain key, value pairs
class Json_Key:

    def __init__(self, _key: str, _is_pattern: bool):
        self.key = _key  # Key can be an exact path (key1$key2$3#key4$) or just a pattern (3#key4)
        self.is_pattern = _is_pattern


class Json_Key_Val:

    def __init__(self, _key: str, _is_pattern: bool, _val):
        self.key = _key  # Key can be an exact path (key1$key2$3#key4$) or just a pattern (3#key4)
        self.is_pattern = _is_pattern
        self.val = _val

class Json_Write:
    # Assuming path is always a pattern
    def __init__(self, path=None, index=None, new_val=None):
        self.path = path
        self.index = index
        self.use_path = True
        self.new_val = new_val

        if self.path is not None:
            self.use_path = True
        elif self.index is not None:
            self.use_path = False
