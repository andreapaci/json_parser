import json
import re

jsonString = '{"id": "file","value": "File","popup":{"menuitem": { "address":[{"value": "New", "onclick": "CreateNewDoc()"}, {"value": [{"value": "New", "onclick": "CreateNewDoc()"}, {"value": "Open", "onclick": "OpenDoc()"},{"value": {"id": "file","value": "File","popup":{"menuitem": { "address":[{"value": "New", "onclick": "CreateNewDoc()"}, {"value": [{"value": "New", "onclick": "CreateNewDoc()"}, {"value": "Open", "onclick": "OpenDoc()"},{"value": "Close", "onclick": "CloseDoc()"}], "onclick": "OpenDoc()"},{"value": "Close", "onclick": [1,"2",3,4,{"value": "New", "onclick": "CreateNewDoc()"}]}]}}}}]}]}}}'
indent_char = '  '
container_char_dict = '$'
container_char_list = '#'


# Recursive function
# Returns True are set in order to prematurely exit the function once it has modified what it has to.
# If the function returns True, it means it has found what he had to, otherwise it hasn't found it.
def json_modify_by_index(data, index, new_val=None, lst=None):
    if lst is None:
        lst = [0]
    if isinstance(data, dict):
        for (k, v) in data.items():
            if isinstance(v, dict):
                if json_modify_by_index(v, index, new_val=new_val , lst=lst):
                    return True
            elif isinstance(v, list):
                if json_modify_by_index(v, index, new_val=new_val , lst=lst):
                    return True
            else:
                if index == lst[0]:
                    data[k] = new_val
                    return True
                lst[0] = lst[0] + 1
    elif isinstance(data, list):
        for i in range(0, len(data)):
            if isinstance(data[i], dict):
                if json_modify_by_index(data[i], index, new_val=new_val , lst=lst):
                    return True
            elif isinstance(data[i], list):
                if json_modify_by_index(data[i], index, new_val=new_val , lst=lst):
                    return True
            else:
                if index == lst[0]:
                    data[i] = new_val
                    return True
                lst[0] = lst[0] + 1
    else:
        raise Exception("Json decoding went wrong!")
    return False

def json_modify_by_path(data, path):
    if path == "":
        return data
    dict_pos = path.find(container_char_dict)
    list_pos = path.find(container_char_list)
    print(dict_pos, list_pos)
    if list_pos < 0 or dict_pos < list_pos:
        tokens = path.split(container_char_dict, 1)
        return json_modify_by_path(data[tokens[0]], tokens[1])
    if dict_pos < 0 or list_pos < dict_pos:
        tokens = path.split(container_char_list, 1)
        return json_modify_by_path(data[int(tokens[0])], tokens[1])
    print("Bella")
    raise Exception("Path accessing went wrong")

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
                    #print("\"" + str(v) + "\",", "(" + str(lst[0]) + ")", new_path)
                    print("\"" + str(v) + "\",")
                else:
                    #print(str(v) + ",", "(" + str(lst[0]) + ")", new_path)
                    print(str(v) + ",")
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
                    #print(indent_char * indent + "\"" + str(data[i]) + "\",", "(" + str(lst[0]) + ")", new_path)
                    print(indent_char * indent + "\"" + str(data[i]) + "\",")
                else:
                    #print(indent_char * indent + str(data[i]) + ",", "(" + str(lst[0]) + ")", new_path)
                    print(indent_char * indent + str(data[i]) + ",")
                lst[0] = lst[0] + 1
    else:
        raise Exception("Json decoding went wrong!")



if __name__ == '__main__':
    data = json.loads(jsonString)
    json_parse(data)

    #print(json_modify_by_path(data, "popup$menuitem$0#onclick$"))
    #print(json_modify_by_path(data, "popup$menuitem$1#value$2#onclick$"))
    #print(json_modify_by_path(data, "id$"))
    #print(json_modify_by_path(data, "popup$menuitem$0#value$"))

    #for i in range(0,12):
        #print("----------------------")
        #json_modify_by_index(data, i, new_val=1)
        #json_parse(data)
