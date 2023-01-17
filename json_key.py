# Class used to store the tuple (key, accepted_values). Used in json_parse library to check whether a json contains certain key, value pairs
class Json_Key:

    def __init__(self, _key: str, _is_pattern: bool):
        self.key = _key #Key can be an exact path (key1$key2$3#key4$) or just a pattern (3#key4)
        self.is_pattern = _is_pattern