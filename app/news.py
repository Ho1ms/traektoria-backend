from . import app

import os
from json import dumps
from hashlib import sha256
from os.path import join, exists
from flask_cors import cross_origin
from flask import Blueprint, request, send_file

from .modules.database import create_connect
from .modules.validator import validate_data
from .modules.access_handler import access_handler, get_user