import json
import json_struct as js

jsonString = '{"id": "file","value": "File","popup":{"menuitem": { "ADDRESS":[{"value": "New", "onclick": "CreateNewDoc()"}, {"value": [{"value": "New", "onclick": "CreateNewDoc()"}, {"value": "Open", "onclick": "OpenDoc()"},{"value": {"id": "file","value": "File","popup":{"menuitem": { "ADDRESS":[{"value": "New", "onclick": "CreateNewDoc()"}, {"value": [{"value": "New", "onclick": "CreateNewDoc()"}, {"value": "Open", "onclick": "OpenDoc()"},{"value": "Close", "onclick": "CloseDoc()"}], "onclick": "OpenDoc()"},{"value": "Close", "onclick": [1,"2",3,4,{"value": "New", "onclick": "CreateNewDoc()"}]}]}}}}]}]}}}'
jsonString2 = '{"glossary": {"title": "example glossary","GlossDiv": {"title": "S","GlossList": {"GlossEntry": {"ID": "SGML","SortAs": "SGML","GlossTerm": "Standard Generalized Markup Language","Acronym": "SGML","Abbrev": "ISO 8879:1986","GlossDef": {"para": "A meta-markup language, used to create markup languages such as DocBook.","GlossSeeAlso": ["GML", "XML"]},"GlossSee": "markup"}}}}}'
indent_char = '  '
container_char_dict = '$'
container_char_list = '#'


def eval_expression(old_val, new_val):
    val = old_val
    loc_ = {"val": val}
    exec("val = " + str(new_val), globals(), loc_)
    val = loc_["val"]
    return val


def json_modify_by_index(data, index: int, new_val, lst: list[int] = None):
    """
    json_modify_by_index access the json key with index and modifies the value with new_val .
    :param data: json data struct
    :param index: index to be accessed
    :param new_val: new value to be written
    :return: True if the index has been accessed and written, False otherwise
    """
    if lst is None:
        lst = [0]
    if isinstance(data, dict):
        for (k, v) in data.items():
            if isinstance(v, dict) or isinstance(v, list):
                if json_modify_by_index(v, index, new_val, lst=lst):
                    return True
            else:
                if index == lst[0]:
                    data[k] = eval_expression(data[k], new_val)
                    return True
                lst[0] = lst[0] + 1
    elif isinstance(data, list):
        for i in range(0, len(data)):
            if isinstance(data[i], dict) or isinstance(data[i], list):
                if json_modify_by_index(data[i], index, new_val, lst=lst):
                    return True
            else:
                if index == lst[0]:
                    data[i] = eval_expression(data[i], new_val)
                    return True
                lst[0] = lst[0] + 1
    else:
        raise Exception("Json decoding went wrong!")
    return False


def json_access_by_index(data, index: int, lst: list[int] = None):
    """
    json_access_by_index access the json key with index and returns its value.

    :param data: json data struct
    :param index: index to be accessed
    :return: the element read if found, None otherwise
    """
    if lst is None:
        lst = [0]
    if isinstance(data, dict):
        for (k, v) in data.items():
            if isinstance(v, dict) or isinstance(v, list):
                ret = json_access_by_index(v, index, lst=lst)
                if ret is not None:
                    return ret
            else:
                if index == lst[0]:
                    return data[k]
                lst[0] = lst[0] + 1
    elif isinstance(data, list):
        for i in range(0, len(data)):
            if isinstance(data[i], dict) or isinstance(data[i], list):
                ret = json_access_by_index(data[i], index, lst=lst)
                if ret is not None:
                    return ret
            else:
                if index == lst[0]:
                    return data[i]
                lst[0] = lst[0] + 1
    else:
        raise Exception("Json decoding went wrong!")
    return None


def json_modify_by_path(data, path: str, new_val, index=None):
    """
    json_modify_by_path modify a json value using a path.

    :param data: json data struct
    :param path: the path specified as: key1$key2$list_index1#key3$list_index2#
    :param new_val: value to be written
    :return: True if the value has been accessed and written, False otherwise
    """
    if path is None:
        return False
    if path == "":
        data[index] = eval_expression(data[index], new_val)
        return True
    dict_pos = path.find(container_char_dict)
    list_pos = path.find(container_char_list)
    if (0 < dict_pos < list_pos and list_pos > 0) or (list_pos < 0 < dict_pos):
        tokens = path.split(container_char_dict, 1)
        if index is None:
            if tokens[0] not in data:
                return False
            return json_modify_by_path(data, tokens[1], new_val, index=tokens[0])
        else:
            if tokens[0] not in data[index]:
                return False
            return json_modify_by_path(data[index], tokens[1], new_val, index=tokens[0])
    if (0 < list_pos < dict_pos and dict_pos > 0) or (dict_pos < 0 < list_pos):
        tokens = path.split(container_char_list, 1)
        if index is None:
            if int(tokens[0]) >= len(data):
                return False
            return json_modify_by_path(data, tokens[1], new_val, index=int(tokens[0]))
        else:
            if int(tokens[0]) >= len(data[index]):
                return False
            return json_modify_by_path(data[index], tokens[1], new_val, index=int(tokens[0]))
    return False


def json_access_by_path(data, path: str):
    """
    json_access_by_path return a json value using a path.

    :param data: json data struct
    :param path: the path specified as: key1$key2$list_index1#key3$list_index2#
    :return: the value accessed if found, None otherwise
    """
    if path is None:
        return None
    if path == "":
        return data
    dict_pos = path.find(container_char_dict)
    list_pos = path.find(container_char_list)
    if (0 < dict_pos < list_pos and list_pos > 0) or (list_pos < 0 < dict_pos):
        tokens = path.split(container_char_dict, 1)
        if tokens[0] not in data:
            return None
        return json_access_by_path(data[tokens[0]], tokens[1])
    if (0 < list_pos < dict_pos and dict_pos > 0) or (dict_pos < 0 < list_pos):
        tokens = path.split(container_char_list, 1)
        if int(tokens[0]) >= len(data):
            return None
        return json_access_by_path(data[int(tokens[0])], tokens[1])
    return None


def json_find_by_pattern(data, pattern: str, path: str = ""):
    """
    json_find_by_pattern find the path from a given pattern. Case-insensitive.

    :param data: json data struct
    :param pattern: the pattern to be found/completed
    :return: the pattern if it can be found, None otherwise
    """
    if isinstance(data, dict):
        for (k, v) in data.items():
            new_path = path + k + container_char_dict
            if isinstance(v, dict) or isinstance(v, list):
                ret = json_find_by_pattern(v, pattern, path=new_path)
                if ret is not None:
                    return ret
            else:
                if pattern.lower() in new_path.lower():
                    return new_path
    elif isinstance(data, list):
        for i in range(0, len(data)):
            new_path = path + str(i) + container_char_list
            if isinstance(data[i], dict) or isinstance(data[i], list):
                ret = json_find_by_pattern(data[i], pattern, path=new_path)
                if ret is not None:
                    return ret
            else:
                if pattern.lower() in new_path.lower():
                    return new_path
    else:
        raise Exception("Json decoding went wrong!")
    return None

def json_find_all_by_patterns(data, patterns: list[str], path: str = "", lst: list[str] = None):
    """
    json_access_all_by_patterns returns all the paths contains one of the patter specified in "patterns". Case-insensitive.

    :param data: json data struct
    :param patterns: list of patterns to be found/completed
    :return: list all the paths
    """
    if lst is None:
        lst = []
    if isinstance(data, dict):
        for (k, v) in data.items():
            new_path = path + k + container_char_dict
            if isinstance(v, dict) or isinstance(v, list):
                lst = json_find_all_by_patterns(v, patterns, lst=lst, path=new_path)
            else:
                for p in patterns:
                    if p.lower() in new_path.lower():
                        if new_path not in lst:
                            lst.append(new_path)
    elif isinstance(data, list):
        for i in range(0, len(data)):
            new_path = path + str(i) + container_char_list
            if isinstance(data[i], dict) or isinstance(data[i], list):
                lst = json_find_all_by_patterns(data[i], patterns, lst=lst, path=new_path)
            else:
                for p in patterns:
                    if p.lower() in new_path.lower():
                        if new_path not in lst:
                            lst.append(new_path)
    else:
        raise Exception("Json decoding went wrong!")
    return lst


def search_elem_in_keys(e: str, keys: list[str], lst: list[bool]):
    """
    search_elem_in_keys search if the key "e" is found in keys and updates lst. Case-insensitive.

    :param e: the key to be found
    :param keys: all the keys
    :param lst: bool list that checks if the #n entry of keys has been found
    :return: True all the keys have been found, False otherwise
    """
    for i in range(0, len(keys)):
        if keys[i] == e.lower():
            lst[i] = True
    res = True
    for v in lst:
        res = res and v
    return res


def json_key_find(data, keys: list[str], lst: list[bool] = None):
    """
    json_key_find checks if all the keys exists in data. Case-insensitive.

    :param data: json data struct
    :param keys: all the keys to be found
    :return: True if all the keys are found, false otherwise
    """
    if lst is None:
        lst = [False] * len(keys)
        keys = [e.lower() for e in keys]

    if isinstance(data, dict):
        for (k, v) in data.items():
            if search_elem_in_keys(k, keys, lst):
                return True
            if isinstance(v, dict) or isinstance(v, list):
                if json_key_find(v, keys, lst=lst):
                    return True
    elif isinstance(data, list):
        for i in range(0, len(data)):
            if isinstance(data[i], dict) or isinstance(data[i], list):
                if json_key_find(data[i], keys, lst=lst):
                    return True
    else:
        raise Exception("Json decoding went wrong!")
    return False


def json_key_value_exists(data, key_value: list[js.Json_Key_Val]):
    """
    json_key_value_exists check if all the key-values pair in key_value are present in data.

    :param data: json data struct
    :param key_value: List made by Json_Key_Value entries.
    :return: True if all key-value pairs are present, False otherwise
    """
    # For each element of the key values...
    for kv in key_value:
        # If the keys doesn't exist, return false
        key = kv.key
        if kv.is_pattern:
            key = json_find_by_pattern(data, kv.key)
            if key is None:
                return False
        val = json_access_by_path(data, key)
        res = False
        for v in kv.val:
            res = res or val == v
        if not res:
            return False
    return True


def json_key_value_exists_delete(data, key_value: list[js.Json_Key_Val]):
    """
    json_key_value_exists_delete it is like json_key_value_exists, bit it deletes keys when are found.

    :param data: json data struct
    :param key_value: List made by Json_Key_Value entries.
    """
    # For each element of the key values...
    dump = list[js.Json_Key_Val]()
    for kv in key_value:
        key = kv.key
        if kv.is_pattern:
            key = json_find_by_pattern(data, kv.key)
            if key is None:
                continue
        val = json_access_by_path(data, key)
        res = False

        for v in kv.val:
            res = res or val == v
        if res:
            dump.append(kv)

    for d in dump:
        key_value.remove(d)


def json_key_exists(data, keys: list[js.Json_Key]):
    """
    json_key_exists checks if keys specified in "keys" exits.

    :param data: json data struct
    :param keys: list of Json_Keys
    :return: True if all keys are found, False otherwise
    """
    full_keys = list[str]()
    for k in keys:
        if k.is_pattern:
            ret = json_find_by_pattern(data, k.key)
            if ret is None:
                return False
            # TODO: Questo si potrebbe levare (se find_pattern ha restituito una chiave,
            #  questa è sicuramente accessibile)
            full_keys.append(ret)
        else:
            full_keys.append(k.key)
    for e in full_keys:
        if not json_access_by_path(data, e):
            return False
    return True


def json_key_exists_delete(data, keys: list[js.Json_Key]):
    """
    json_key_exists_delete is the same as json_key_exists, but it deletes entry in keys when are found

    :param data: json data struct
    :param keys: list of Json_Keys
    """
    dump = list[js.Json_Key]()
    for k in keys:
        if k.is_pattern:
            ret = json_find_by_pattern(data, k.key)
            if ret is None:
                continue
            if json_access_by_path(data, ret):
                dump.append(k)
        else:
            if json_access_by_path(data, k.key):
                dump.append(k)

    for d in dump:
        keys.remove(d)

#                                                   #
#   External functions - Use this functions only    #
#                                                   #


def json_key_keyval_exists(data, keys_val: list[js.Json_Key_Val] = None, keys: list[js.Json_Key] = None):
    """
    json_key_keyval_exists is a function that searches in a json data if key-value pair are found and keys
    (without specifying its value) are present

    :param data: json data struct
    :param keys_val: list of key-value pairs
    :param keys: list of keys
    :return: True if all key-value pairs and keys are found, False otherwise
    """
    if keys_val is not None:
        if not json_key_value_exists(data, keys_val):
            return False
    if keys is not None:
        if not json_key_exists(data, keys):
            return False
    return True


def json_multiple_key_keyval_exists(data: list, keys_val: list[js.Json_Key_Val] = None, keys: list[js.Json_Key] = None):
    """
    json_multiple_key_keyval_exists is a function that searches in multiple json data if key-value pair are found and keys
    (without specifying its value) are present for multiple data

    :param data: list of json data struct
    :param keys_val: list of key-value pairs
    :param keys: list of keys
    :return: True if all key-value pairs and keys are found, False otherwise
    """
    if keys_val is not None:
        cp_keys_val = keys_val.copy()
        for d in data:
            json_key_value_exists_delete(d, cp_keys_val)
        if len(cp_keys_val) > 0:
            return False

    if keys is not None:
        cp_keys = keys.copy()
        for d in data:
            json_key_exists_delete(d, cp_keys)
        if len(cp_keys) > 0:
            return False
    return True


def json_inject_value(data, inject: js.Json_Write):
    """
    json_inject_value write the values specified in js.Json_Write in data

    :param data: json data struct
    :param inject: new value to be written
    :return: True if value has been written, False otherwise
    """
    if inject.use_path:
        path = json_find_by_pattern(data, inject.path)
        if path is None:
            return False
        return json_modify_by_path(data, path, inject.new_val)
    else:
        return json_modify_by_index(data, inject.index, inject.new_val)


def json_parse(data, print_index: bool = False, print_path: bool = False, indent: int = 0, lst: list[int] = None, path: str = ""):
    """
    json_parse parses a json struct and returns it as json string. Can print extra info

    :param data: json data struct
    :param print_index: Default False. Prints the index of each element
    :param print_path: Default False. Prints the path
    :return the string of the parsing
    """
    output = ""
    if lst is None:
        lst = [0]
    if isinstance(data, dict):
        for (k, v) in data.items():
            new_path = path + k + container_char_dict
            output += indent_char * indent + "\"" + str(k) + "\"" + ":"
            if isinstance(v, dict):
                output += "{\n"
                output += json_parse(v, print_index=print_index, print_path=print_path, indent=indent + 1, lst=lst, path=new_path)
                output += indent_char * indent + "},\n"
            elif isinstance(v, list):
                output += "[\n"
                output += json_parse(v, print_index=print_index, print_path=print_path, indent=indent + 1, lst=lst, path=new_path)
                output += indent_char * indent + "],\n"
            else:
                if isinstance(v, str):
                    output += "\"" + str(v) + "\", "
                else:
                    output += str(v) + ", "
                if print_index:
                    output += "(" + str(lst[0]) + ") "
                if print_path:
                    output += new_path
                output += "\n"
                lst[0] = lst[0] + 1
    elif isinstance(data, list):
        for i in range(0, len(data)):
            new_path = path + str(i) + container_char_list
            if isinstance(data[i], dict):
                output += indent_char * indent + "{\n"
                output += json_parse(data[i], print_index=print_index, print_path=print_path, indent=indent + 1, lst=lst,
                           path=new_path)
                output += indent_char * indent + "},\n"
            elif isinstance(data[i], list):
                output += indent_char * indent + "[\n"
                output += json_parse(data[i], print_index=print_index, print_path=print_path, indent=indent + 1, lst=lst,
                           path=new_path)
                output += indent_char * indent + "],\n"
            else:
                if isinstance(data[i], str):
                    output += indent_char * indent + "\"" + str(data[i]) + "\", "
                else:
                    output += indent_char * indent + str(data[i]) + ", "
                if print_index:
                    output += "(" + str(lst[0]) + ") "
                if print_path:
                    output += new_path
                output += "\n"
                lst[0] = lst[0] + 1
    else:
        raise Exception("Json decoding went wrong!")
    return output


def test():
    """
    test runs some tests regarding json_parser implementation.
    """

    data = json.loads(jsonString)
    data2 = json.loads(jsonString2)

    # ---------------------------------------------------------------------
    # Test json_parse with index and path enabled/disabled

    print("------------------------------------------------------------")
    print(json_parse(data))
    print(json_parse(data, print_index=True))
    print(json_parse(data, print_path=True))
    print(json_parse(data, print_index=True, print_path=True))

    print(json_parse(data2))
    print(json_parse(data2, print_index=True))
    print(json_parse(data2, print_path=True))
    print(json_parse(data2, print_index=True, print_path=True))
    print("------------------------------------------------------------")

    # ---------------------------------------------------------------------
    # Test json_modify/access_by_index

    for i in range(0, 18, 2):
        assert json_modify_by_index(data, i, i)
        assert i == json_access_by_index(data, i)

    assert not json_modify_by_index(data, 120, 120)
    assert json_access_by_index(data, 120) is None

    for i in range(0, 12, 2):
        assert json_modify_by_index(data2, i, i)
        assert i == json_access_by_index(data2, i)

    assert not json_modify_by_index(data2, 120, 120)
    assert json_access_by_index(data2, 120) is None

    # ---------------------------------------------------------------------
    # Test josn_modify/access_by_path and json_find_pattern

    pattern_val = [["addreSS$2#oncliCk$1", "'A'", "A"], ["address$1#onclick$", "'B'", 'B'], ["id", "1", 1],
                   ["$menuitem$address$2#onclick$0#", 1337, 1337]]
    for e in pattern_val:
        json_modify_by_path(data, json_find_by_pattern(data, e[0]), e[1])
        assert e[2] == json_access_by_path(data, json_find_by_pattern(data, e[0]))

    pattern_val = [["title", "'A'", "A"], ["ENTRY$glosss", "'B'", 'B'], ["$SORTAS", 1, 1],
                   ["also$1#", 1337, 1337]]
    for e in pattern_val:
        json_modify_by_path(data2, json_find_by_pattern(data2, e[0]), e[1])
        assert e[2] == json_access_by_path(data2, json_find_by_pattern(data2, e[0]))

    assert json_access_by_path(data, "xxxxxxxxx") is None
    assert not json_modify_by_path(data, "xxxxxxxxx", "1")

    assert json_find_by_pattern(data, "xxxxxxxxxxxxxxx") is None

    assert json_access_by_path(data2, "xxxxxxxxx") is None
    assert not json_modify_by_path(data2, "xxxxxxxxx", "1")

    assert json_find_by_pattern(data2, "xxxxxxxxxxxxxxx") is None

    assert isinstance(json_access_by_path(data, "popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$"), list)


    # ---------------------------------------------------------------------
    # Test json_key_find

    assert json_key_find(data, ["address", "id"])
    assert json_key_find(data, ["adDress", "MENUITEM"])
    assert json_key_find(data, ["id", "ID"])
    assert not json_key_find(data, ["address", "notexisting"])
    assert not json_key_find(data, ["notexisting"])
    assert json_key_find(data, [])

    assert json_key_find(data2, ["ABBREV", "id"])
    assert json_key_find(data2, ["aCROnYM", "abbrev"])
    assert json_key_find(data2, ["id", "ID"])
    assert not json_key_find(data2, ["para", "notexisting"])
    assert not json_key_find(data2, ["notexisting"])
    assert json_key_find(data2, [])

    # ---------------------------------------------------------------------
    # Test json_key_value_compare

    key_val = [js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                ["A", "12", 1337]),
               js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$3#", True,
                                ["A", 4, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", "12", 1])]

    assert json_key_value_exists(data, key_val)

    key_val = [js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                ["A", 1337, "12"]),
               js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$2#", True,
                                ["A", 87878, 3, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", "12", "file"])]

    assert not json_key_value_exists(data, key_val)

    key_val = [js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    assert json_key_value_exists(data, key_val)

    key_val = [js.Json_Key_Val("address$0#value$", True, [2, "12", "New"]),
               js.Json_Key_Val("dsadasdsdsa#dsadsadsa#", True, ["A", 87878]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    assert not json_key_value_exists(data, key_val)

    key_val = [js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 1337]),
               js.Json_Key_Val("id", False, ["cane", "example", 1, "file"])]

    assert not json_key_value_exists(data, key_val)

    # ---------------------------------------------------------------------
    # Test json_key_exists

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", True)]

    assert json_key_exists(data, key)

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", True)]

    assert json_key_exists(data, key)

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", False)]

    assert not json_key_exists(data, key)

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("popup$menuitem$ADDRESS$0#", False)]

    assert json_key_exists(data, key)

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("adadadada", False)]

    assert not json_key_exists(data, key)

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("adadadada", True)]

    assert not json_key_exists(data, key)

    # ---------------------------------------------------------------------
    # Test json_key_keyval_exists

    assert json_key_keyval_exists(data)

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", False)]

    assert not json_key_keyval_exists(data, keys=key)

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", True)]

    assert json_key_keyval_exists(data, keys=key)

    key_val = [js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    assert json_key_keyval_exists(data, keys_val=key_val)

    key_val = [js.Json_Key_Val("address$0#value$", True, [2, "12", "New"]),
               js.Json_Key_Val("dsadasdsdsa#dsadsadsa#", True, ["A", 87878]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    assert not json_key_keyval_exists(data, keys_val=key_val)

    key_val = [js.Json_Key_Val("address$0#value$", True, [2, "12", "New"]),
               js.Json_Key_Val("dsadasdsdsa#dsadsadsa#", True, ["A", 87878]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", True)]

    assert not json_key_keyval_exists(data, keys_val=key_val, keys=key)

    key_val = [js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", False)]

    assert not json_key_keyval_exists(data, keys_val=key_val, keys=key)

    key_val = [js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    key = [js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
           js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
           js.Json_Key("id", True)]

    assert json_key_keyval_exists(data, keys_val=key_val, keys=key)

    # ---------------------------------------------------------------------
    # Test json_key_value_exists_delete

    key_val = [js.Json_Key_Val("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False,
                                [1, "lol", "no", "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 77]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2])]

    json_key_value_exists_delete(data2, key_val)

    assert len(key_val) == 1

    key_val = [js.Json_Key_Val("notexisting", True,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", False, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("notexisting", True, [1, "lol", "no", 1337, 2])]

    json_key_value_exists_delete(data2, key_val)

    assert len(key_val) == 3

    key_val = [js.Json_Key_Val("aaaaaaaaaaa", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2])]

    json_key_value_exists_delete(data2, key_val)

    assert len(key_val) == 1

    # ---------------------------------------------------------------------
    # Test json_key_exists_delete

    keys = [js.Json_Key("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False), js.Json_Key("id", True),
            js.Json_Key("also$1#", True)]

    json_key_exists_delete(data2, keys)

    assert len(keys) == 0

    keys = [js.Json_Key("notexisting", True), js.Json_Key("id", False), js.Json_Key("notexisting", True)]

    json_key_exists_delete(data2, keys)

    assert len(keys) == 3

    keys = [js.Json_Key("aaaaaaaaaaa", False), js.Json_Key("id", True), js.Json_Key("also$1#", True)]

    json_key_exists_delete(data2, keys)

    assert len(keys) == 1


    # ---------------------------------------------------------------------
    # Test json_multiple_key_keyval_exists

    key_val = [js.Json_Key_Val("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2])]

    assert json_multiple_key_keyval_exists([data2], keys_val=key_val)


    key_val = [js.Json_Key_Val("notexisting", True,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", False, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("notexisting", True, [1, "lol", "no", 1337, 2])]

    assert not json_multiple_key_keyval_exists([data2], keys_val=key_val)



    key_val = [js.Json_Key_Val("aaaaaaaaaaa", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2])]

    assert not json_multiple_key_keyval_exists([data2], keys_val=key_val)


    keys = [js.Json_Key("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False), js.Json_Key("id", True),
            js.Json_Key("also$1#", True)]

    assert json_multiple_key_keyval_exists([data2], keys=keys)

    keys = [js.Json_Key("notexisting", True), js.Json_Key("id", False), js.Json_Key("notexisting", True)]

    assert not json_multiple_key_keyval_exists([data2], keys=keys)

    keys = [js.Json_Key("aaaaaaaaaaa", False), js.Json_Key("id", True), js.Json_Key("also$1#", True)]

    assert not json_multiple_key_keyval_exists([data2], keys=keys)


    keys = [js.Json_Key("aaaaaaaaaaa", False), js.Json_Key("id", True), js.Json_Key("also$1#", True)]

    key_val = [js.Json_Key_Val("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2])]

    assert not json_multiple_key_keyval_exists([data2], keys=keys, keys_val=key_val)

    keys = [js.Json_Key("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False), js.Json_Key("id", True),
            js.Json_Key("also$1#", True)]

    key_val = [js.Json_Key_Val("aaaaaaaaaaa", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2])]

    assert not json_multiple_key_keyval_exists([data2], keys=keys, keys_val=key_val)

    keys = [js.Json_Key("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False), js.Json_Key("id", True),
            js.Json_Key("also$1#", True)]

    key_val = [js.Json_Key_Val("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2])]

    assert json_multiple_key_keyval_exists([data2], keys=keys, keys_val=key_val)


    keys = [js.Json_Key("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False), js.Json_Key("id", True),
            js.Json_Key("also$1#", True),

            js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
            js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
            js.Json_Key("popup$menuitem$ADDRESS$0#", False)]

    key_val = [js.Json_Key_Val("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2]),

               js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    assert json_multiple_key_keyval_exists([data, data2], keys=keys, keys_val=key_val)
    assert len(keys) > 0 and len(key_val) > 0

    keys = [js.Json_Key("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False), js.Json_Key("id", True),
            js.Json_Key("also$1#", True),

            js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
            js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
            js.Json_Key("popup$meaaaaaa", False)]

    key_val = [js.Json_Key_Val("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [1, "lol", "no", "id", 2]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2]),

               js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 1337]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    assert not json_multiple_key_keyval_exists([data, data2], keys=keys, keys_val=key_val)

    keys = [js.Json_Key("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False), js.Json_Key("id", True),
            js.Json_Key("also$1#", True),

            js.Json_Key("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False),
            js.Json_Key("menuitem$ADDRESS$2#onclick$0#", True),
            js.Json_Key("popup$menuitem$ADDRESS$0#", False)]

    key_val = [js.Json_Key_Val("glossary$GlossDiv$GlossList$GlossEntry$GlossDef$para$", False,
                                [1, "lol", "no",
                                 "A meta-markup language, used to create markup languages such as DocBook."]),
               js.Json_Key_Val("id", True, [2, "lol", "no", "id", 3333]),
               js.Json_Key_Val("also$1#", True, [1, "lol", "no", 1337, 2]),

               js.Json_Key_Val("popup$menuitem$ADDRESS$1#value$2#value$popup$menuitem$ADDRESS$2#onclick$0#", False,
                                [1, 1, "A", 1337]),
               js.Json_Key_Val("menuitem$ADDRESS$2#onclick$0#", True, ["A", 87878, 66666]),
               js.Json_Key_Val("id", True, ["cane", "example", 1, "file"])]

    assert not json_multiple_key_keyval_exists([data, data2], keys=keys, keys_val=key_val)


    # ---------------------------------------------------------------------
    # Test json_inject_value

    inject = js.Json_Write(path="ADDRESS$0#VALUE", new_val="'NUOVO_VALORE'")
    assert json_inject_value(data, inject)
    assert "NUOVO_VALORE" == json_access_by_path(data, json_find_by_pattern(data, "ADDRESS$0#VALUE"))

    inject = js.Json_Write(path="non_existing", new_val="'val123'")
    assert not json_inject_value(data, inject)
    assert not "val123" == json_access_by_path(data, json_find_by_pattern(data, "non_existing"))

    inject = js.Json_Write(index=25, new_val="'iliade'")
    assert json_inject_value(data, inject)
    assert "iliade" == json_access_by_index(data, 25)

    inject = js.Json_Write(index=256, new_val="'odissea'")
    assert not json_inject_value(data, inject)
    assert not "odissea" == json_access_by_index(data, 256)

    inject = js.Json_Write(index=0, new_val="val + 12000")
    assert json_inject_value(data, inject)
    assert 12001 == json_access_by_index(data, 0)

    inject = js.Json_Write(index=1, new_val=True)
    assert json_inject_value(data, inject)
    assert json_access_by_index(data, 1)

    # ---------------------------------------------------------------------
    # Test json_find_all_by_patterns

    print(json_find_all_by_patterns(data, ["d", "I"]))

    print("------------------------------------------------------------")
    print(json_parse(data))
    print(json_parse(data2))
    print("------------------------------------------------------------")

    # To export as json
    print(json.dumps(data))
    print(json.dumps(data2))


if __name__ == '__main__':
    test()
