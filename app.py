from flask import Flask, jsonify, Response

from services import (
    service_get_geral, service_get_geral_resumo,
    service_get_platform, service_get_platform_resumo
)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Fernando Júlio da Silva Martins, fernandojmartinsprofissional@gmail.com, https://www.linkedin.com/in/fernando-j%C3%BAlio-06338721b/'


@app.route('/<platform>', methods=['GET'])
def get_platform(platform):
    return service_get_platform(platform)


@app.route('/<platform>/resumo', methods=['GET'])
def get_platform_resumo(platform):
    return service_get_platform_resumo(platform)


@app.route('/geral', methods=['GET'])
def get_geral():
    return service_get_geral()
        

@app.route('/geral/resumo', methods=['GET'])
def get_geral_resumo():
    return service_get_geral_resumo()


app.run()