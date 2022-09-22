from app.api import bp
from flask import request, jsonify, url_for
import json, copy
from app import databaseMode
from model import *

if databaseMode:
    from app import graph

data = {}


@bp.route('/get_data', methods=['GET'])
def get_data():
    global data
    if databaseMode:
        data = loadDataFromNeo4j(graph)
    else:
        # print(request.json)
        # data = loadDataFromJson('./templates/data.json')
        data = loadDataFromJson('./templates/test.json')
    print(data)
    inniAdjMatrix(data)

    return jsonify(data)


indexNew2Old = {}
mainGraphData = {}
subGraphData = {}


@bp.route('/get_subGraphData', methods=['GET'])
def get_subGraphData():
    global indexNew2Old
    global mainGraphData
    # print(indexNew2Old)
    # print(request.args['baseNodeIndex'])
    # try:
    #     print(indexNew2Old[int(request.args['baseNodeIndex'])])
    # except:
    #     pass

    if mainGraphData != data:
        mainGraphData = copy.deepcopy(data)
        updateAdjMatrix = True
    else:
        updateAdjMatrix = False
    try:
        subGraphData = adjSubgraph(mainGraphData, indexNew2Old[int(request.args['baseNodeIndex'])],
                                   int(request.args['numLayer']), updateAdjMatrix=updateAdjMatrix)
    except KeyError:
        subGraphData = adjSubgraph(mainGraphData, int(request.args['baseNodeIndex']), int(request.args['numLayer']),
                                   updateAdjMatrix=updateAdjMatrix)
    subGraphData, indexNew2Old = refreshIndex(subGraphData)
    res = {'subgraph': subGraphData, 'new2old': list(indexNew2Old.values())}
    return jsonify(res)


@bp.route('/get_mainGraphData', methods=['GET'])
def get_mainGraphData():
    return jsonify(data)


@bp.route('/get_search', methods=['GET'])
def get_search():
    print(request.args['search'])
    global indexNew2Old
    global mainGraphData
    global subGraphData

    # if mainGraphData != data:
    #     mainGraphData = copy.deepcopy(data)
    #     updateAdjMatrix = True
    # else:
    #     updateAdjMatrix = False
    if databaseMode:
        subGraphData = searchSubGraph(request.args['search'])

    if subGraphData:
        subGraphData, indexNew2Old = refreshIndex(subGraphData)
    # res = {'graph': subGraphData, 'new2old': list(indexNew2Old.values())}
    res = {'graph': data, 'new2old': list(indexNew2Old.values())}
    return jsonify(res)


@bp.route('/get_autoComplete', methods=['GET'])
def get_autoComplete():
    return jsonify(autoComplete(graph, request.args['search']))
