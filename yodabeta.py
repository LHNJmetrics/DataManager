from core.findata import todayint, corredges
import sqlite3
import warnings
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def getcorr(allcode, term='M', before=1, name='name', content=0, addr="D:\\yodadb\\anal.db"):
    # allcode는 setDB에서 allcodelist()로 얻는 DataFrame
    # before는 최소연수. before보다 어린 증권 제외
    # addr은 각 증권별 수익률 데이터가 저장된 주소
    # content = {0: 수익률, 1: 거래량변동률}
    # name은 'name'이면 종목명, 'code'면 종목코드
    content = {0: 'rates', 1: 'vol_fluc'}[content]
    anal = sqlite3.connect(addr)
    cordic = {}
    print("\nLoading Data...\n")
    for i in allcode.index:
        if allcode.ix[i].start > todayint() - 10000 * before:
            continue
        else:
            code = allcode.code[i]
            if name == 'name':
                col = allcode.name[i]
            else:
                col = code
            codeinfo = pd.read_sql("SELECT * From '{}{}'".format(code, term), anal, index_col='index')
            cordic[col] = codeinfo[content]
    return corredges(cordic)


class Relationship:
    # 클래스 변수 리스트
    # 인스턴스 변수 리스트
    term = 'M'
    vol_min = 10000
    size_min = 100000000
    years_min = 2
    node_name = 'code'
    
    def __init__(self, content=0, addr="D:\\yodadb\\anal.db"):
        anal = sqlite3.connect(addr)
        cordic = {}
        self.content = {0: 'rates', 1: 'vol_fluc'}[content]
        self.acl = pd.read_sql("SELECT * From 'allcode'", anal, index_col='index')
        for i in self.acl.index:
            if self.acl.ix[i].start > todayint() - 10000 * Relationship.years_min:
                continue
            elif self.acl.ix[i].recentV < Relationship.vol_min:
                continue
            elif self.acl.ix[i].recentV * self.acl.ix[i].recentP < Relationship.size_min:
                continue
            else:
                code = self.acl.code[i]
                if Relationship.node_name == 'name':
                    col = self.acl.name[i]
                else:
                    col = code
                codeinfo = pd.read_sql("SELECT * From '{}{}'".format(code, Relationship.term),
                                       anal, index_col='index')
                cordic[col] = codeinfo[self.content]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.edgelist = corredges(cordic)

    def show_setting(self):
        print("""CURRENT SETTING
        term = {}
        vol_min = {}
        size_min = {}
        years_min = {}
        name = {}
        content = {}""".format(Relationship.term, Relationship.vol_min, Relationship.size_min,
                               Relationship.years_min, Relationship.node_name, self.content))


class Network:
    # 클래스 변수 리스트
    # 인스턴스 변수 리스트
    def __init__(self, r, depth=0.7):
        # r : Relationship class의 인스턴스
        print("\nMaking Network...\n")
        n1, n2, sign = [], [], []
        (self.acl, self.term, self.content, self.node_name, self.edgelist
         ) = (r.acl, r.term, r.content, r.node_name, r.edgelist)
        self.depth = depth
        self.edge_color = []
        for i in self.edgelist.index:
            if abs(self.edgelist['corr'][i]) >= depth:
                n1.append(self.edgelist['a'][i])
                n2.append(self.edgelist['b'][i])
                if self.edgelist['corr'][i] > 0:
                    sign.append('+')
                    self.edge_color.append('r')
                else:
                    sign.append('-')
                    self.edge_color.append('b')
        df = pd.DataFrame({'n1': n1, 'n2': n2, 'sign': sign})
        self.G = nx.from_pandas_edgelist(df, 'n1', 'n2', edge_attr='sign')
        (self.degree, self.nodes, self.edges, self.adj
         ) = (self.G.degree, self.G.nodes, self.G.edges, self.G.adj)

    def show(self, node_size=1, font_size=8):
        nx.draw_networkx(self.G, node_size=node_size, edge_color=self.edge_color, font_size=font_size)
        plt.show()

    def degreerank(self):
        a = self.degree


if __name__ == '__main__':
    from matplotlib import font_manager, rc
    font_name = font_manager.FontProperties(fname="C:\\Windows\\Fonts\\malgun.ttf").get_name()
    rc('font', family=font_name)
    rs = Relationship()
    nw = Network(rs)
