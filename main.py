import json
import re

jsonString = '{"id": "file","value": "File","popup":{"menuitem": { "ADDRESS":[{"value": "New", "onclick": "CreateNewDoc()"}, {"value": [{"value": "New", "onclick": "CreateNewDoc()"}, {"value": "Open", "onclick": "OpenDoc()"},{"value": {"id": "file","value": "File","popup":{"menuitem": { "ADDRESS":[{"value": "New", "onclick": "CreateNewDoc()"}, {"value": [{"value": "New", "onclick": "CreateNewDoc()"}, {"value": "Open", "onclick": "OpenDoc()"},{"value": "Close", "onclick": "CloseDoc()"}], "onclick": "OpenDoc()"},{"value": "Close", "onclick": [1,"2",3,4,{"value": "New", "onclick": "CreateNewDoc()"}]}]}}}}]}]}}}'
indent_char = '  '
container_char_dict = '$'
container_char_list = '#'


# Recursive function: This function modify a value of a json field accessing with an index
# Returns True are set in order to prematurely exit the function once it has modified what it has to.
# If the function returns True, it means it has found what he had to, otherwise it hasn't found it.
def json_modify_by_index(data, index, new_val, lst=None):
    if lst is None:
        lst = [0]
    if isinstance(data, dict):
        for (k, v) in data.items():
            if isinstance(v, dict) or isinstance(v, list):
                if json_modify_by_index(v, index, new_val, lst=lst):
                    return True
            else:
                if index == lst[0]:
                    data[k] = new_val
                    return True
                lst[0] = lst[0] + 1
    elif isinstance(data, list):
        for i in range(0, len(data)):
            if isinstance(data[i], dict) or isinstance(data[i], list):
                if json_modify_by_index(data[i], index, new_val, lst=lst):
                    return True
            else:
                if index == lst[0]:
                    data[i] = new_val
                    return True
                lst[0] = lst[0] + 1
    else:
        raise Exception("Json decoding went wrong!")
    return False


# Recursive function. Return the value of a json field accessed by index
def json_access_by_index(data, index, lst=None):
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


def json_modify_by_path(data, path, new_val, index=None):
    if path == "":
        data[index] = new_val
        return
    dict_pos = path.find(container_char_dict)
    list_pos = path.find(container_char_list)
    if (0 < dict_pos < list_pos and list_pos > 0) or (list_pos < 0 and dict_pos > 0):
        tokens = path.split(container_char_dict, 1)
        if index is None:
            return json_modify_by_path(data, tokens[1], new_val, index=tokens[0])
        else:
            return json_modify_by_path(data[index], tokens[1], new_val, index=tokens[0])
    if (0 < list_pos < dict_pos and dict_pos > 0) or (dict_pos < 0 and list_pos > 0):
        tokens = path.split(container_char_list, 1)
        if index is None:
            return json_modify_by_path(data, tokens[1], new_val, index=int(tokens[0]))
        else:
            return json_modify_by_path(data[index], tokens[1], new_val, index=int(tokens[0]))
    raise Exception("Path accessing went wrong")


def json_access_by_path(data, path):
    if path == "":
        return data
    dict_pos = path.find(container_char_dict)
    list_pos = path.find(container_char_list)
    if (0 < dict_pos < list_pos and list_pos > 0) or (list_pos < 0 and dict_pos > 0):
        tokens = path.split(container_char_dict, 1)
        return json_access_by_path(data[tokens[0]], tokens[1])
    if (0 < list_pos < dict_pos and dict_pos > 0) or (dict_pos < 0 and list_pos > 0):
        tokens = path.split(container_char_list, 1)
        return json_access_by_path(data[int(tokens[0])], tokens[1])
    raise Exception("Path accessing went wrong")


def json_find_by_pattern(data, pattern, path=""):
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


def search_elem_in_keys(e, keys, lst):
    for i in range(0, len(keys)):
        if keys[i] == e.lower():
            lst[i] = True
    res = True
    for v in lst:
        res = res and v
    return res

# Recursive function: This function returns True if all the keys specified in "keys" are found in data, False otherwise
def json_key_find(data, keys, lst=None):
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



def json_parse(data, indent=0, lst=None, path=""):
    if lst is None:
        lst = [0]
    if isinstance(data, dict):
        for (k, v) in data.items():
            new_path = path + k + container_char_dict
            print(indent_char * indent, "\"" + str(k) + "\"", ":", end='', sep='')
            if isinstance(v, dict):
                print("{")
                json_parse(v, indent=indent + 1, lst=lst, path=new_path)
                print(indent_char * indent, "},", sep='')
            elif isinstance(v, list):
                print("[")
                json_parse(v, indent=indent + 1, lst=lst, path=new_path)
                print(indent_char * indent, "],", sep='')
            else:
                if isinstance(v, str):
                    print("\"" + str(v) + "\",", "(" + str(lst[0]) + ")", new_path)
                    # print("\"" + str(v) + "\",")
                else:
                    print(str(v) + ",", "(" + str(lst[0]) + ")", new_path)
                    # print(str(v) + ",")
                lst[0] = lst[0] + 1
    elif isinstance(data, list):
        for i in range(0, len(data)):
            new_path = path + str(i) + container_char_list
            if isinstance(data[i], dict):
                print(indent_char * indent, "{", sep='')
                json_parse(data[i], indent=indent + 1, lst=lst, path=new_path)
                print(indent_char * indent, "},", sep='')
            elif isinstance(data[i], list):
                print(indent_char * indent, "[", sep='')
                json_parse(data[i], indent=indent + 1, lst=lst, path=new_path)
                print(indent_char * indent, "],", sep='')
            else:
                if isinstance(data[i], str):
                    print(indent_char * indent + "\"" + str(data[i]) + "\",", "(" + str(lst[0]) + ")", new_path)
                    # print(indent_char * indent + "\"" + str(data[i]) + "\",")
                else:
                    print(indent_char * indent + str(data[i]) + ",", "(" + str(lst[0]) + ")", new_path)
                    # print(indent_char * indent + str(data[i]) + ",")
                lst[0] = lst[0] + 1
    else:
        raise Exception("Json decoding went wrong!")


if __name__ == '__main__':
    data = json.loads(jsonString)

    print("------------------------------------------------------------")
    json_parse(data)
    print("------------------------------------------------------------")


    for i in range(0, 18, 2):
        assert json_modify_by_index(data, i, i)
        assert i == json_access_by_index(data, i)
        print(i, ":", json_access_by_index(data, i))

    assert not json_modify_by_index(data, 120, 120)
    assert json_access_by_index(data, 120) is None

    pattern_val = [["addreSS$2#oncliCk$1", "A"], ["address$1#onclick$", "B"], ["id", 1], ["$menuitem$address$2#onclick$0#", 1337]]
    for e in pattern_val:
        json_modify_by_path(data, json_find_by_pattern(data, e[0]), e[1])
        print(json_access_by_path(data, json_find_by_pattern(data, e[0])))
        assert e[1] == json_access_by_path(data, json_find_by_pattern(data, e[0]))

    assert json_find_by_pattern(data, "xxxxxxxxxxxxxxx") is None

    assert json_key_find(data, ["address", "id"])
    assert json_key_find(data, ["adDress", "MENUITEM"])
    assert not json_key_find(data, ["address", "caccapupu"])

    print("------------------------------------------------------------")
    json_parse(data)
    print("------------------------------------------------------------")
