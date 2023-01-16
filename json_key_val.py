# Class used to store the tuple (key, accepted_values). Used in json_parse library to check whether a json contains certain key, value pairs
class Json_Key_Val:

    def __init__(self, _key, _is_pattern, _val):
        self.key = _key #Key can be an exact path (key1$key2$3#key4$) or just a pattern (3#key4)
        self.is_pattern = _is_pattern
        self.val = _val
