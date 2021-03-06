import os
import json
import re
import types
import sys


class Config:
    """
    설정 파일에 대한 처리를 하는 클래스.
    json 형식을 지원하고 set_param을 통해 등록한 변수들은
    인스턴스에서 참조하듯이(a = abc()/a.set_param("a", 1)/a.a)
    사용할 수 있다.
    """

    def __init__(self, default=None, json_file=None):
        """
        인자로 dict나 json 형식의 파일이름을 받아 데이터를 설정한다.
        먼저 dict 형식의 인자를 추가하고, 그 다음에 json 형식의 파일을 읽어
        내용을 추가하거나 갱신한다.

        Args:
            default (dict or None) : json type dict data.
            json_file (str or None) : json file path.
        """

        # default값 먼저 설정
        if default is not None and type(default) == dict:
            self.update_from_dict(default)

        if json_file is not None and type(json_file) == str:
            self.load_json(json_file)

        self.log = '[Config] '

    def _clean_name(self, name):
        """
        받은 문자열을 변수로 사용할 수 있는 문자열로 바꾼다.

        Args:
            name (str) : 변수로 사용할 문자열.

        Returns:
            str : 변경된 문자열. 실패한 경우에는 ""가 반환된다.
        """
        result = name
        # 앞에 붙은 '-'를 제거한다.
        while result.startswith("-"):
            result = result[1:]

        # '_', '.', ":" 를 제외한 특수문자가 남아있는지 확인한다.
        if len(re.findall("[^a-zA-Z0-9_.:/\\\]+", result)) > 0:
            return ""

        return result

    def update_from_dict(self, dict_data):
        """
        dict에 있는 데이터를 변수로 추가한다.
        기존에 있는 데이터는 새로운 값으로 갱신한다.

        Args:
            dict_data (dict) : json 형식의 dict 데이터
        Returns:
            boolean : 성공하면 True를 실패하면 False를 반환한다.
        """
        if type(dict_data) != dict:
            return False

        for key in dict_data:
            # 값의 이름을 쓸수 있는 형태로 바꾼다.
            name = self._clean_name(str(key).strip())
            if name == "":
                continue

            # 기존에 함수형태로 가진것과 동일한 것은 반영하지 않음
            # if hasattr(self, name):
            #     attr = getattr(self, name)
            # else:
            #     attr = None
            #
            # if type(attr) == types.MethodType \
            #         or type(attr) == types.FunctionType:
            #     continue

            # 값을 설정한다
            value = dict_data[key]
            setattr(self, name, value)

        return True

    def load_json(self, filename):
        """
        json 파일을 읽어 설정을 갱신한다.

        Args:
            filename (str) : json filename.

        Returns:
            bool : True or False
        """
        if not (type(filename) == str and filename != "" and os.path.isfile(filename)):
            print('filename is abnormal or path is abnormal')
            return False
        try:
            with open(filename, "r", encoding="utf-8") as rf:
                data = json.load(rf)

        except Exception as e:
            print(self.log, 'load_json error occured..', e)
            return False

        self.update_from_dict(data)

        return True

    def set_param(self, name, val):
        """
                변수를 설정한다.

                Args:
                    name (str) : 변수명
                    val : 변수값
        """
        try:
            setattr(self, name, val)
        except Exception as e:
            print(self.log, 'set_param error occured..', e)

    def get_param(self, name, default=None):
        """
        변수값을 반환한다.
        없는 경우에는 default를 설정값으로 한 뒤 반환한다.

        Args:
            name (str) : 변수명
            default : 변수가 없을시 반환되는 값
        Returns:
            various : 해당 변수의 값
        """
        try:
            if not hasattr(self, name):
                setattr(self, name, default)
        except Exception as e:
            print(self.log, 'get_param error occured..', e)
            return default

        return getattr(self, name)

    def has_param(self, name):
        """
        변수값이 있는지 확인한다.

        Args:
            name (str) : 변수명
        Returns:
            boolean : 해당 변수가 있으면 True, 없으면 False를 반환한다.
        """
        return hasattr(self, name)

    def get_all_params(self):
        """
        가진 모든 변수를 dict형태로 반환한다.
        가져간 dict 데이터를 수정해도 Config에는 반영되지 않는다.

        Returns:
            dict : 가진 모든 변수의 dict 데이터
        """
        return self.__dict__.copy()