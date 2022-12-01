#coding:utf-8
import imp
from pickle import FALSE
from tkinter import CENTER
from py2neo import Graph
# import jieba, eventlet, time
import py2neo, json, flask
from flask import request, Flask, jsonify, make_response
from flask_cors import CORS
import json

def connectNeo4j():
    # return Graph("http://localhost:7474/", auth=("neo4j", "123"))
    return 0


def showDataType(graph):
    print(graph.schema.node_labels)
    print(graph.schema.relationship_types)


def getName(graph, text):
    g_TimeLine = 1.5
    # eventlet.monkey_patch()
    # with eventlet.Timeout(g_TimeLine, False):
    #     gql = "match (p:vertices) where p.name contains '{}' return p.name, id(p) limit 1".format(text)
    #     res = graph.run(gql).data()
    #     print(res[0]['p.name'])
    #     return res[0]['id(p)']
    return False


def getNameByID(graph, id):
    gql = "match (p:vertices) where ID(p) in [{}] return p.name".format(id)
    return graph.run(gql).data()[0]['p.name']


def getNodeByID(graph, id):
    gql = "match (p:vertices) where ID(p) in [{}] return p".format(id)
    return graph.run(gql).data()[0]['p']


def alignment(graph, text):
    name = getName(graph, text)
    if name is not False:
        return name
    new_text = jieba.lcut(text)
    for text in new_text:
        name = getName(graph, text)
        if name is not False:
            return name
    return False


class Association():
    def __init__(self, graph):
        self.graph = graph

    def priority1(self, source, target):
        # 任意有关系的两个公司
        # # gql = "match p=(source:vertices)-[r*1..10]-(target:vertices) where ID(source) in [{}] and ID(target) in [{}] return source,r,target,nodes(p)".format(source, target)
        gql = "match p=(source:vertices)-[r*1..10]-(target:vertices) return source,r,target,nodes(p) limit 1"
        res = self.graph.run(gql).data()
        # TODO: deal with the res
        return res

    def priority2(self, source, target):
        # 单向股权关系
        # gql = "match p=(source:vertices)-[r1:HOLDER*1..5]->(target:vertices) where ID(source) in [{}] and ID(target) in [{}] return source,r1,target,nodes(p)".format(source, target)
        gql = "match p=(source:vertices)-[r1:HOLDER*1..5]->(target:vertices) return source,r1,target,nodes(p) limit 1"
        res = self.graph.run(gql).data()
        print(res)
        # TODO: deal with the res
        return res

    def priority3(self, source, target):
        # 单中心汇总关系
        # gql = "match p=(source:vertices)-[r1:HOLDER|:MANAGER*1..2]->(center1:vertices)<-[r2:HOLDER|:MANAGER*1..2]-(target:vertices) where ID(source) in [{}] and ID(target) in [{}] return source,r1,r2,target,nodes(p)".format(source, target)
        gql = "match p=(source:vertices)-[r1:HOLDER|:MANAGER*1..2]->(center1:vertices)<-[r2:HOLDER|:MANAGER*1..2]-(target:vertices) return source,r1,r2,target,nodes(p) limit 1"
        res = self.graph.run(gql).data()
        # TODO: deal with the res
        return res

    def priority4(self, source, target):
        # 其他任意两级关系
        # gql = "match p=(source:vertices)-[r1*1]->(center1:vertices)<-[r2*1]-(target:vertices) where ID(source) in [{}] and ID(target) in [{}] return source,r1,r2,target,nodes(p)".format(source, target)
        gql = "match p=(source:vertices)-[r1*1]->(center1:vertices)<-[r2*1]-(target:vertices) return source,r1,r2,target,nodes(p) limit 1"
        res = self.graph.run(gql).data()
        # TODO: deal with the res
        return res

    def priority5(self, source, target):
        # 单方向客户供应商关系
        # source = alignment(self.graph, source)
        # target = alignment(self.graph, target)
        # gql = "match p=(source:vertices)-[r:SUPPLIER*1..5]->(target:vertices) where ID(source) in [{}] and ID(target) in [{}] return source,r,target,nodes(p) limit 1".format(source, target)
        gql = "match p=(source:vertices)-[r:SUPPLIER*1..5]->(target:vertices) return source,r,target,nodes(p) limit 1"
        res = self.graph.run(gql).data()
        nodes = res[0]['nodes(p)']
        ret = []
        for i in range(len(nodes) - 1):
            e = {
                'source': nodes[i]['name'],
                'target': nodes[i + 1]['name'],
                'description': 'SUPPLIER'
            }
            ret.append(e)
        # TODO: deal with the res
        print(ret)
        return ret

    def priority6(self, source, target, mid):
        # 两中心汇总关系
        # gql = "match p=(source:vertices)-[r1:HOLDER|:MANAGER*1..2]->(center1:vertices)<-[r2:HOLDER|:MANAGER*1..2]-(mid:vertices)-[r3:HOLDER|:MANAGER*1..2]->(center2:vertices)<-[r4:HOLDER|:MANAGER*1..2]-(target:vertices) where ID(source) in [{}] and ID(mid) in [{}] and ID(target) in [{}] return source,r1,r2,r3,r4,target,mid,nodes(p) limit 1".format(source, mid, target)
        gql = "match p=(source:vertices)-[r1:HOLDER|:MANAGER*1..2]->(center1:vertices)<-[r2:HOLDER|:MANAGER*1..2]-(mid:vertices)-[r3:HOLDER|:MANAGER*1..2]->(center2:vertices)<-[r4:HOLDER|:MANAGER*1..2]-(target:vertices) return source,r1,r2,r3,r4,target,mid,nodes(p) limit 1"
        res = self.graph.run(gql).data()
        # TODO: deal with the res
        return res


class EquityPenetration():

    def __init__(self, graph):
        self.graph = graph

    def priority1(self, center):
        # TODO:暂时只做一层的股权穿透分析
        center = alignment(self.graph, center)
        gql = "match (source:vertices)-[rs1:HOLDER*0..1]->(center) where id(center) in [{}] with distinct source as source_distinct \
            match (center)-[rs2:HOLDER*0..1]->(target:vertices) where id(center) in [{}] \
            with distinct target as target_distinct, source_distinct, center \
            with [i in collect(target_distinct) + source_distinct + center | id(i)] as target_id_collect \
            match (source_ret)-[r_ret:HOLDER]->(target_ret) \
            where id(source_ret) in target_id_collect and id(target_ret) in target_id_collect \
            return collect(distinct [source_ret,r_ret,target_ret,type(r_ret)]) as all_edges".format(center, center)
        res = self.graph.run(gql).data()
        print(res[0]['all_edges'])
        all_edges = res[0]['all_edges']
        ret = []
        for edge in all_edges:
            e = {
                'source': edge[2]['name'],
                'target': edge[0]['name'],
                'description': edge[1]['f1']
            }
            ret.append(e)
        return ret


def nodes_distinct(nodes):
    """
    节点去重
    """
    node_set = {}
    for n in nodes:
        node_set[n.identity] = n
    return [i[1] for i in node_set.items()]


class affiliated_match:
    """
    关联方查询
    """

    def __init__(self, graph):
        self.graph = graph

    def direct_holders(self, company, holder, limit=5):
        """
        控股关联方
        :param company: 主体公司
        :param holder: 主体公司的(某个)实际控制人
        :param limit: 中间股东最大数量,包括实际控制人 (None为无限制,但是会很慢)
        :return: 控股关联方
        e.g.:
        match p=(n)-[r:HOLDER*1..2]->(m) where id(n)=72646205 and id(m)=91910043
        with n,NODES(p) as x
        unwind x as y
        with n,[i in collect(distinct y) where id(i) <> id(n)] as res
        return res
        """
        result = self.graph.run(f"MATCH p=(n)-[r:HOLDER*1..{limit if limit is not None else ''}]->(m) "
                                f"WHERE ID(n)={company.identity} and ID(m)={holder.identity} "
                                f"WITH n,NODES(p) as x "
                                f"UNWIND x as y "
                                f"WITH n,[i IN COLLECT(DISTINCT y) WHERE ID(i) <> ID(n)] as result "
                                f"RETURN result").data()
        return result[0]['result']

    def cor_holder(self, company, holder, limit=5):
        """
        同一控制关联方
        :param company: 主体公司
        :param holder: 主体公司的(某个)实际控制人
        :param limit: 中间股东最大数量,包括实际控制人 (None为无限制,但是会很慢)
        :return: 同一控制关联方
        e.g.:
        match p=(n)<-[r:HOLDER*1..2]-(m)
        where id(n)=91910043 and id(m)<>72646205
        return m
        """
        result = self.graph.run(f"MATCH p=(n)<-[r:HOLDER*1..{limit if limit is not None else ''}]-(m) "
                                f"WHERE ID(n)={holder.identity} and ID(m)<>{company.identity} "
                                f"RETURN m").data()
        return [i['m'] for i in result]

    def natural_holder(self, company, holder, limit=5, threshold=0.05):
        """
        非控股自然人关联方
        :param company: 主体公司
        :param holder: 主体公司的(某个)实际控制人
        :param limit: 中间股东最大数量,包括实际控制人 (None为无限制,但是会很慢)
        :param threshold: 股份阈值
        :return: 非控股自然人关联方
        :return:
        e.g.:
        match p=(n)-[r:HOLDER*1..2]->(m) where id(n)=83679750 and id(m)=91910043
        with n,NODES(p) as x
        unwind x as y
        with n,[i in collect(distinct y) where id(i) <> id(n) | id(i)] as a
        with a
        match p=(n)-[r:HOLDER]->(m{type:"1"}) where id(n)=83679750 and toFloat(r.f1)>=0.05 and none(i in a where i=id(m)) return p
        """
        result = self.graph.run(f"MATCH p=(n)-[r:HOLDER*1..{limit if limit is not None else ''}]->(m) "
                                f"WHERE ID(n)={company.identity} and ID(m)={holder.identity} "
                                f"WITH n,NODES(p) as x "
                                f"UNWIND x as y "
                                f"WITH n,[i IN COLLECT(DISTINCT y) WHERE ID(i) <> ID(n) | ID(i)] as a "
                                f"WITH a "
                                f"MATCH p=(n)-[r:HOLDER]->(m{{type:\"1\"}}) "
                                f"WHERE ID(n)={company.identity} and toFloat(r.f1)>={threshold} and none(i in a where i=ID(m)) "
                                f"RETURN m").data()
        return [i['m'] for i in result]

    def manager(self, company):
        """
        董监高关联方
        :param company: 主体公司
        :return: 董监高关联方
        e.g.:
        match (n)-[:MANAGER]->(m) where id(n)=83679750 return m
        """
        result = self.graph.run(f"MATCH p=(n)-[:MANAGER]->(m) "
                                f"WHERE ID(n)={company.identity} "
                                f"RETURN DISTINCT m").data()
        return [i['m'] for i in result]

    def manager_holder(self, company, holder, limit=5):
        """
        控股单位董监高关联方
        :param company: 主体公司
        :param holder: 主体公司的(某个)实际控制人
        :param limit: 中间股东最大数量,包括实际控制人 (None为无限制,但是会很慢)
        :return: 控股单位董监高关联方
        e.g.:
        match p=(n)-[r:HOLDER*1..2]->(m) where id(n)=83679750 and id(m)=112651112
        with n,NODES(p) as x
        unwind x as y
        with n,[i in collect(distinct y) where id(i) <> id(n) | id(i)] as a
        with a
        match p=(n)-[:MANAGER]->(m) where id(n)=83679750 and id(m) in a return p
        """
        result = self.graph.run(f"MATCH p=(n)-[r:HOLDER*1..{limit if limit is not None else ''}]->(m) "
                                f"WHERE ID(n)={company.identity} and ID(m)={holder.identity} "
                                f"WITH n,NODES(p) as x "
                                f"UNWIND x as y "
                                f"WITH n,[i IN COLLECT(DISTINCT y) WHERE ID(i) <> ID(n) | id(i)] as a "
                                f"WITH a "
                                f"MATCH p=(n)-[:MANAGER]->(m) "
                                f"WHERE ID(n)={company.identity} and ID(m) IN a "
                                f"RETURN m").data()
        return [i['m'] for i in result]

    def friendly_company(self, company, holder, limit=5):
        """
        :param company: 主体公司
        :param holder: 主体公司的(某个)实际控制人
        :param limit: 中间股东最大数量,包括实际控制人 (None为无限制,但是会很慢)
        :return: 友方公司
        e.g.:
        match p=(n)-[r:HOLDER*1..5]->(m) where id(n)=35580442 and  id(m)=91910043
        with n,nodes(p) as x
        unwind x as y
        with n,[i in collect(distinct y) where id(i) <> id(n) and i.type <> "1" | id(i)] as a
        match p=(nn)-[r:MANAGER]->(mm) where id(mm) in [91910043,4973358,121641908,121539184] and none(i in a where i=id(nn))
        return p
        """
        friendly_holders = self.direct_holders(company, holder, limit) + self.manager(company)
        friendly_holders = nodes_distinct(friendly_holders)
        friendly_holders_id = [i.identity for i in friendly_holders]
        result = self.graph.run(f"MATCH p=(n)-[r:HOLDER*1..{limit if limit is not None else ''}]->(m) "
                                f"WHERE id(n)={company.identity} and  id(m)={holder.identity} "
                                f"WITH n,NODES(p) AS x "
                                f"UNWIND x AS y "
                                f"WITH n,[i IN COLLECT(DISTINCT y) WHERE ID(i) <> ID(n) AND i.type <> \"1\" | ID(i)] as a "
                                f"MATCH p=(nn)-[r:MANAGER]->(mm) "
                                f"WHERE ID(mm) in {str(friendly_holders_id)} AND NONE(i IN a WHERE i=ID(nn)) "
                                f"RETURN nn").data()
        return [i['nn'] for i in result]

    def match(self, order, company, holder):
        if order == 'direct':
            nodes = self.direct_holders(company,holder)
        elif order == 'cor':
            nodes = self.cor_holder(company,holder)
        elif order == 'natural':
            nodes = self.natural_holder(company,holder)
        elif order == 'manager':
            nodes = self.manager(company)
        elif order == 'manager_holder':
            nodes = self.manager_holder(company,holder)
        else:
            nodes = self.friendly_company(company,holder)

        nodes_id = [n.identity for n in nodes]
        nodes_id += [company.identity,holder.identity]
        nodes_id = list(set(nodes_id))
        links = self.graph.run(f"MATCH p=(n)-->(m) WHERE ID(n) IN {str(nodes_id)} AND ID(m) IN {str(nodes_id)} RETURN p").data()
        links = [l['p'] for l in links]
        result = {'nodes':[],'links':[]}
        nodes_set = set()
        for link in links:
            source = link.start_node
            target = link.end_node
            if source.identity not in nodes_set:
                result['nodes'].append({'index':source.identity,'label':source['name'],'type':source['type']})
                nodes_set.add(source.identity)
            if target.identity not in nodes_set:
                result['nodes'].append({'index': target.identity, 'label': target['name'], 'type': target['type']})
                nodes_set.add(target.identity)
            result['links'].append({'source':source.identity,'target':target.identity,'describe':type(link.relationships[0]).__name__})

        return result


class controller_match:
    class case_graph:
        """
        储存本次计算需要考虑的节点
        """

        class case_node:
            """
            节点的结构体
            """

            def __init__(self, graph, nid):
                self.graph = graph
                self.node = self.graph.run(f"MATCH (n) WHERE ID(n)={nid} RETURN n").data()[0]['n']
                self.father = None
                self.absolute_flag = False  # father是否为绝对控制
                self.absolute_hold = []  # 其绝对控制的节点
                self.relative_hold = []  # 其相对控制的节点
                self.holders = []
                self.shares = []

        def __init__(self, graph, nodes_ids: list):
            """
            初始化节点,
            完成absolute_hold和relative_hold的填充,
            完成初始father和absolute_flag的判断
            """
            self.graph = graph
            self.nodes = {}
            self.top_nodes = []

            for nid in nodes_ids:
                self.nodes[nid] = self.case_node(graph, nid)

            for nid in nodes_ids:
                holders = self.graph.run(f"MATCH (n)-[r:HOLDER]->(m) "
                                         f"WHERE ID(n)={nid} "
                                         f"RETURN ID(m) as id, TOFLOAT(r.f1) as f1").data()

                if len(holders) == 0:
                    self.top_nodes.append(nid)
                    continue

                max_idx = 0
                for x, h in enumerate(holders):
                    if h['f1'] >= holders[max_idx]['f1']: max_idx = x
                    self.nodes[nid].holders.append(h['id'])
                    self.nodes[nid].shares.append(h['f1'])

                if holders[max_idx]['f1'] >= 0.5:
                    self.nodes[holders[max_idx]['id']].absolute_hold.append(nid)
                    self.nodes[holders[max_idx]['id']].relative_hold.append(nid)
                elif holders[max_idx]['f1'] >= 0.3:
                    self.nodes[holders[max_idx]['id']].relative_hold.append(nid)

            print('case init done')

            self.find_absolute()

            print('absolute done')

            self.find_relative()

            print('relative done')

        def find_absolute(self):
            queue = []
            for i in self.top_nodes:
                for j in self.nodes[i].absolute_hold:
                    self.nodes[j].father = i
                    self.nodes[j].absolute_flag = True
                    assert j not in queue
                    queue.append(j)

            head = 0
            while head != len(queue):
                h = queue[head]
                for i in self.nodes[h].absolute_hold:
                    assert i not in queue
                    queue.append(i)
                    self.nodes[i].father = self.nodes[h].father
                    self.nodes[i].absolute_flag = True
                head += 1

            # init done

            change = True
            while change:
                change = False
                for nid, n in self.nodes.items():
                    if n.father is not None or len(n.holders) == 0: continue
                    group = {}
                    max_group_id = None
                    max_group_f1 = 0
                    for i in range(len(n.holders)):
                        hn = self.nodes[n.holders[i]]
                        hf1 = n.shares[i]
                        if hn.father is None: continue
                        if hn.father not in group:
                            group[hn.father] = hf1
                        else:
                            group[hn.father] += hf1
                        if group[hn.father] > max_group_f1:
                            max_group_f1 = group[hn.father]
                            max_group_id = hn.father
                    if max_group_f1 >= 0.5:
                        n.father = max_group_id
                        n.absolute_flag = True
                        change = True

        def find_relative(self):
            queue = []
            for i in self.top_nodes:
                for j in self.nodes[i].relative_hold:
                    if self.nodes[j].father is None:
                        self.nodes[j].father = i
                    assert j not in queue
                    queue.append(j)

            head = 0
            while head != len(queue):
                h = queue[head]
                for i in self.nodes[h].relative_hold:
                    assert i not in queue
                    queue.append(i)
                    if self.nodes[i].father is None:
                        self.nodes[i].father = self.nodes[h].father
                head += 1

            # init done

            change = True
            while change:
                change = False
                for nid, n in self.nodes.items():
                    if n.father is not None or len(n.holders) == 0: continue
                    group = {}
                    max_group_id = None
                    max_group_f1 = 0
                    max_single_f1 = 0
                    for i in range(len(n.holders)):
                        hn = self.nodes[n.holders[i]]
                        hf1 = n.shares[i]
                        max_single_f1 = max(max_single_f1, hf1)
                        if hn.father is None: continue
                        if hn.father not in group:
                            group[hn.father] = hf1
                        else:
                            group[hn.father] += hf1
                        if group[hn.father] > max_group_f1:
                            max_group_f1 = group[hn.father]
                            max_group_id = hn.father
                    if max_group_f1 >= 0.3 and max_group_f1 > max_single_f1:
                        n.father = max_group_id
                        change = True

        def node_match(self, nid):
            if self.nodes[nid].father is None:
                return 0, None
            elif self.nodes[nid].absolute_flag:
                return 2, self.nodes[self.nodes[nid].father].node
            else:
                return 1, self.nodes[self.nodes[nid].father].node

    def __init__(self, graph):
        self.graph = graph

    def single_controler_match(self, company, limit=6):
        raw_nodes = self.graph.run(f"MATCH p=(n)-[r:HOLDER*1..{limit if limit is not None else ''}]->(m) "
                                   f"WHERE ID(n)={company.identity} "
                                   f"WITH NODES(p) as np "
                                   f"UNWIND np as unp "
                                   f"RETURN DISTINCT ID(unp)").data()
        nodes = [i['ID(unp)'] for i in raw_nodes]
        case = self.case_graph(self.graph, nodes)
        return case.node_match(company.identity)


graph = connectNeo4j()
ass = Association(graph)
eq = EquityPenetration(graph)
aff = affiliated_match(graph)
con = controller_match(graph)

app = Flask(__name__)
CORS(app)

@app.route('/fun1', methods=['get'])
#关联关系
def fun1():
    source = request.args['source']
    target = request.args['target']
    print(source, target)
    if source == '11' and target == '111':
        ret = {'nodes': [{'id': 4221017, 'label': '上海能辉科技股份有限公司', 'type': '2'}, {'id': 1589544, 'label': '江苏中信博新能源科技股份有限公司', 'type': '2'}, {'id': 24388799, 'label': '张家港保税区登月国际贸易有限公司', 'type': '3'}], 'links': [{'source': 4221017, 'target': 1589544, 'description': 'SUPPLIER'}, {'source': 1589544, 'target': 24388799, 'description': 'SUPPLIER'}]}
    else:
        ret = {'nodes': [], 'links': []}
    return jsonify(ret)


@app.route('/fun2', methods=['get'])
#股权穿透
def fun2():
    # center = json.loads(request.data)['center']
    # ret = eq.priority1(center)
    center = request.args['center']
    print(center)
    ret = {'nodes': [{'id': 1500570990, 'label': '刘建明', 'type': '1'}, {'id': 6999967, 'label': '淘宝众筹(北京)投资管理有限公司', 'type': '3'}, {'id': 1500570989, 'label': '余玉喜', 'type': '1'}, {'id': 1500570992, 'label': '李玲', 'type': '1'}, {'id': 1500570991, 'label': '张雷', 'type': '1'}], 'links': [{'source': 1500570990, 'target': 6999967, 'description': '0.10000'}, {'source': 1500570989, 'target': 6999967, 'description': '0.40000'}, {'source': 1500570992, 'target': 6999967, 'description': '0.10000'}, {'source': 1500570991, 'target': 6999967, 'description': '0.40000'}]}
    return jsonify(ret)


@app.route('/fun3', methods=['get'])
#实际控股人
def fun3():
    company = request.args['source']
    order = request.args['order']
    company = "广州钿菲配资科技有限公司"
    order = "manager_holder"
    company_id = 44846867
    if not company_id:
        ret = {'node': [], 'links': []}
        return jsonify(ret)
    _, holder = con.single_controler_match(company)
    print(holder['name'])
    if holder is None: return json.dumps({})
    ret = aff.match(order, company, holder)
    print(ret)
    return jsonify(ret)

@app.route('/ping', methods=['get'])
def ping():
    response = make_response('Ping success!')
    response.mimetype = 'text/plain'
    return response

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=7478, debug=True)
    app.run()