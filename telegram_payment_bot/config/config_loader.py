# Copyright (c) 2021 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#
# Imports
#
import configparser
from typing import Any, Dict, List

from telegram_payment_bot.config.config_object import ConfigObject


#
# Types
#
FieldCfgType = Dict[str, Any]
FieldsCfgType = List[FieldCfgType]
ConfigCfgType = Dict[str, FieldsCfgType]


#
# Classes
#

# Configuration load not existent error class
class ConfigLoadNotExistentError(Exception):
    pass


# Configuration load value error class
class ConfigLoadValueError(Exception):
    pass


# Configuration loader class
class ConfigLoader:

    config_cfg: ConfigCfgType
    config_obj: ConfigObject

    # Constructor
    def __init__(self,
                 config_obj: ConfigObject,
                 config_cfg: ConfigCfgType) -> None:
        self.config_cfg = config_cfg
        self.config_obj = config_obj

    # Load configuration
    def Load(self,
             config_file: str) -> None:
        # Read file
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)

        print(f"\nLoading configuration file {config_file}...\n")
        # Load sections
        self.__LoadSections(config_parser)
        # New line

    # Get object
    def GetLoadedObject(self) -> ConfigObject:
        return self.config_obj

    # Load sections
    def __LoadSections(self,
                       config_parser: configparser.ConfigParser) -> None:
        # For each section
        for section, fields in self.config_cfg.items():
            # Print section
            print(f"Section [{section}]")
            # Load fields
            self.__LoadFields(section, fields, config_parser)

    # Load fields
    def __LoadFields(self,
                     section: str,
                     fields: FieldsCfgType,
                     config_parser: configparser.ConfigParser) -> None:
        # For each field
        for field in fields:
            # Load if needed
            if self.__FieldShallBeLoaded(field):
                # Set field value and print it
                self.__SetFieldValue(section, field, config_parser)
                self.__PrintFieldValue(field)
            else:
                if "def_val" in field:
                    self.config_obj.SetValue(field["type"], field["def_val"])

    # Get if field shall be loaded
    def __FieldShallBeLoaded(self,
                             field: FieldCfgType) -> bool:
        return field["load_if"](self.config_obj) if "load_if" in field else True

    # Set field value
    def __SetFieldValue(self,
                        section: str,
                        field: FieldCfgType,
                        config_parser: configparser.ConfigParser) -> None:
        try:
            field_val = config_parser[section][field["name"]]
        # Field not present, set default value if specified
        except KeyError as ex:
            if "def_val" not in field:
                raise ConfigLoadNotExistentError(f"Configuration field \"{field['name']}\" not found") from ex
            field_val = field["def_val"]
        else:
            # Convert value if needed
            if "conv_fct" in field:
                field_val = field["conv_fct"](field_val)

        # Validate value if needed
        if "valid_if" in field and not field["valid_if"](self.config_obj, field_val):
            raise ConfigLoadValueError(f"Value '{field_val}' is not valid for field \"{field['name']}\"")

        # Set value
        self.config_obj.SetValue(field["type"], field_val)

    # Print field value
    def __PrintFieldValue(self,
                          field: FieldCfgType) -> None:
        if "print_fct" in field:
            print(f"- {field['name']}: {field['print_fct'](self.config_obj.GetValue(field['type']))}")
        else:
            print(f"- {field['name']}: {self.config_obj.GetValue(field['type'])}")
